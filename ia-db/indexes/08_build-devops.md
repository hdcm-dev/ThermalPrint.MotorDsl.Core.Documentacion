# 08 — Build, versionado y DevOps

> **Propósito**: cómo se compila, versiona, empaqueta y publica el proyecto; qué hace cada
> workflow de CI/CD y cada script; y cómo correr los samples en un dispositivo.
> **Fuentes primarias**: `PrintThermalDriver.slnx`, `src/*/*.csproj`, `.github/workflows/`,
> `scripts/{local,mobile,nuget}/`, `docs/09_devops/`, `CHANGELOG.md`, `NuGet.config`.

---

## 1. Prerrequisitos

| Requisito | Para qué |
|---|---|
| .NET 10 SDK (CI usa `10.0.102`) | Todo |
| `dotnet workload install maui` | `MotorDsl.Maui`, `MotorDsl.Bluetooth` y los samples |
| Android SDK | Compilar y correr samples en Android |
| JDK 17 | Build de Android en CI |

Los 5 proyectos `net10.0` (`Core`, `Parser`, `Rendering`, `Extensions`, `Printing.Abstractions`)
y `MotorDsl.Tests` compilan **sin** workload MAUI. `MotorDsl.Maui` y `MotorDsl.Bluetooth`
(`net10.0-android;net10.0-ios`) no.

La solución está en formato **`.slnx`** (`PrintThermalDriver.slnx`), con carpetas
`/src`, `/samples` y `/github.workflow`.

---

## 2. Comandos habituales

```bash
dotnet restore
dotnet build                                                   # solución completa
dotnet build src/MotorDsl.Maui/MotorDsl.Maui.csproj -c Debug   # un proyecto
dotnet test  src/MotorDsl.Tests/MotorDsl.Tests.csproj          # suite (net10.0 puro)

# correr un sample en Android
dotnet build -t:Run -f net10.0-android \
  samples/MotorDsl.Nuget.Integrated.MultaApp/MotorDsl.Nuget.Integrated.MultaApp.csproj
```

---

## 3. Versionado

Esquema **SemVer**. Regla central: **la versión no vive en los `.csproj`** — se inyecta en
build/pack vía `-p:PackageVersion` y `-p:MotorDslVersion`.

**Versión unificada**: los 8 paquetes comparten siempre el mismo número. El script de publicación
calcula `versión unificada = max(next(patch) de cada paquete)` consultando el *flat container* de
nuget.org. El motivo es evitar `NU1605` (downgrade de dependencia) en apps que mezclen varios.

`scripts/nuget/get-next-version.ps1` hace el auto-bump: consulta
`https://api.nuget.org/v3-flatcontainer/<paquete>/index.json` (lectura sin API key), filtra
versiones estables `X.Y.Z` y devuelve la siguiente **solo por stdout**; los diagnósticos van a
stderr para no romper el `FOR /F` del `.bat` que lo invoca.

`MotorDslVersion` se pasa además de `Version` y `PackageVersion` para que los `.csproj` puedan
referenciar esa versión internamente sin parsear `Version` en MSBuild.

Las versiones publicadas son **inmutables**: no se re-publica un número ya subido
(`docs/09_devops/estrategia-versionado_v1.0.md` §8). Los tags git tienen forma `v<versión>`.

Historial de cambios en `CHANGELOG.md`, formato *Keep a Changelog*; la entrada vigente es
**1.0.13 (2026-07-13)**.

---

## 4. Publicación NuGet — `scripts/nuget/publish-motordsl-nuget.bat`

Es la ruta **completa** de publicación. Secuencia:

1. Resuelve la API key desde `MOTORDSL_NUGET_API_KEY` o la pide por prompt.
2. Calcula la versión unificada de los 8 paquetes.
3. `restore` + `build -c Release` de las 7 librerías con la versión inyectada.
4. `restore` + `dotnet test` de `MotorDsl.Tests` — **si fallan, aborta antes de publicar**.
5. `dotnet pack` de las 7 a `./nupkg/`.
6. `dotnet nuget push` con `--skip-duplicate`, **en orden de dependencias**:
   `Printing.Abstractions` → `Core` → `Parser` → `Rendering` → `Extensions` → `Bluetooth` → `Maui`.
7. Tag git `v<versión>` y push a origin (lo que dispara `cd-nuget.yml`).
8. Limpia el caché HTTP de NuGet.

```bat
set MOTORDSL_NUGET_API_KEY=oy2x...
scripts\nuget\publish-motordsl-nuget.bat
```

`scripts/nuget/build-motordsl-nuget.bat` empaqueta sin publicar. Detalle completo en
`scripts/nuget/notas.md`.

---

## 5. Workflows de CI/CD

| Workflow | Disparadores | Qué hace |
|---|---|---|
| `ci.yml` | push y PR sobre `main` | `restore` → `build -c Release` → `dotnet test` de `MotorDsl.Tests` en `ubuntu-latest`; sube resultados como artefacto y comenta el PR si falla |
| `cd-nuget.yml` | tags `v*`, push a `main`, `workflow_dispatch` (con input `version`) | Determina versión → build → tests → pack → push a nuget.org |
| `cd-android.yml` | push a `main`, tags `v*`, `workflow_dispatch` | Matriz de 2 apps (`SampleApp`, `MultaApp`): instala workload `maui-android`, publica el APK, lo verifica y lo sube como artefacto |
| `cd-ios-sampleapp.yml`, `cd-ios-multaapp.yml`, `cd-ios-multaapp.nuget.yml` | push a ramas indicadas | Publicación iOS en `macos-15`, con instalación manual de Xcode (descarga desde Google Drive) y del SDK .NET |

Variables de entorno de CI: `DOTNET_VERSION = 10.0.102`, `DOTNET_VERSION_WORKLOAD = 10.0.100`,
`JAVA_VERSION = 17`. La API key de publicación viene del secret `NUGET_API_KEY`.

Resolución de versión en `cd-nuget.yml`: tag `v*` → el tag sin la `v`; `workflow_dispatch` → el
input; cualquier otro push → `0.0.0-preview.<run_number>`. El `push` a nuget.org **solo** ocurre
para tags `v*` o `workflow_dispatch`.

> **Discrepancia resuelta**: `cd-nuget.yml` empaquetaba **solo 4** proyectos. La causa era
> estructural y no un descuido: el job corría en Linux, y `dotnet pack` de un proyecto multi-TFM
> exige compilar todos sus TFM, pero el workload `ios` **no existe para Linux**
> (`Workload ID ios isn't supported on this platform`; el build corta con `NETSDK1178`). Por eso
> `Bluetooth` y `Maui` eran imposibles ahí. `Printing.Abstractions`, en cambio, sí era un descuido:
> es `net10.0` puro.
>
> El workflow se reestructuró en cuatro jobs — `version`, `pack-managed` (6 paquetes `net10.0` en
> el runner self-hosted), `pack-platform` (`Bluetooth` y `Maui` en `macos-15`) y `publish`, que
> junta ambos artefactos, verifica que estén los 8 y hace push en orden de dependencias. La
> publicación completa ya no depende del script local de Windows.

---

## 6. Scripts locales

| Carpeta | Scripts | Para qué |
|---|---|---|
| `scripts/local/` | `run-<Sample>.bat` (5), `run-All.bat`, `update-packages.bat` | Compilar y lanzar samples en un Android conectado por ADB. Equivale a `dotnet build -t:Run -f net10.0-android` con chequeo previo de dispositivo. `update-packages.bat` actualiza los `PackageReference` de los samples NuGet a la última versión estable publicada (usa `dotnet-outdated`) |
| `scripts/mobile/` | `publish-<Sample>-apk.bat` (5), `publish-all.bat`, `update-packages.bat` | APK firmado `Release` `arm64` para instalación manual: `clean` → `publish -c Release -p:RuntimeIdentifier=android-arm64 -p:AndroidPackageFormat=apk -p:EmbedAssembliesIntoApk=true` → copia a `out/mobile/<Sample>.apk` |
| `scripts/nuget/` | `build-…`, `publish-…`, `get-next-version.ps1`, `notas.md` | Empaquetado y publicación (§4) |

> `EmbedAssembliesIntoApk=true` es **obligatorio** para los APK: sin eso el paquete no se instala
> manualmente vía ADB, solo funciona con `dotnet build -t:Run`
> (fuente: `scripts/mobile/Readme.md`).

Los scripts son `.bat` / `.ps1`: están pensados para Windows.

---

## 7. Metadatos de paquete

Comunes a los 8 `.csproj`: `Authors` (Fernando Rafael Filipuzzi; `MotorDsl.Bluetooth` declara
«UTN FRP TUP Aplicada 2025»), `PackageLicenseExpression = MIT`,
`RepositoryUrl = https://github.com/Aplicada-Streaming/PrintThermal_Motor_Maui`,
`PackageReadmeFile = README.md` (se incluye el README de la raíz),
`PackageTags` con `maui;thermal;escpos;dsl;printing`.

`ImplicitUsings` y `Nullable` habilitados en todos. `NuGet.config` en la raíz define las fuentes
de restore.

---

## 8. Flujo de desarrollo y Definition of Done

Flujo (`docs/README.md`): branch `feature/*` → cambios + tests → validaciones → PR → CI en verde →
merge a `main` → generación de versión.

Se considera terminado cuando: compila, los tests pasan, la cobertura es ≥ 70 %, las validaciones
del DSL son exitosas, la documentación está actualizada y el PR fue aprobado.

`nupkg/` está en `.gitignore`.

---

## 9. Fuentes

| Tema | Archivo |
|---|---|
| Solución y proyectos | `PrintThermalDriver.slnx`, `src/*/*.csproj` |
| Workflows | `.github/workflows/{ci,cd-nuget,cd-android,cd-ios-*}.yml` |
| Scripts | `scripts/local/Readme.md`, `scripts/mobile/Readme.md`, `scripts/nuget/notas.md`, `scripts/nuget/get-next-version.ps1` |
| Versionado | `docs/09_devops/estrategia-versionado_v1.0.md` |
| Pipeline y entornos | `docs/09_devops/{pipeline-ci-cd_v1.0,entornos-deploy_v1.0,guia-publicacion-nuget_v1.0}.md` |
| Historial | `CHANGELOG.md` |
