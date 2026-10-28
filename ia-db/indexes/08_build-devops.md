# 08 — Build, CI/CD y versionado

> **Propósito**: cómo se compila, se prueba, se versiona y se publica el proyecto, y qué se puede
> hacer en cada sistema operativo.
> **Fuentes primarias**: `.github/workflows/` (6), `scripts/`, `.devcontainer/`,
> `docs/09_devops/`, `PrintThermalDriver.slnx`.

---

## 1. La restricción que ordena todo el pipeline

Seis paquetes son `net10.0` puro y compilan **en cualquier lado**. Dos —`MotorDsl.Bluetooth` y
`MotorDsl.Maui`— son multi-TFM (`net10.0-android;net10.0-ios`), y `dotnet pack` de un proyecto
multi-TFM **exige compilar todos sus TFM**. El workload `ios` no existe para Linux
(«Workload ID ios isn't supported on this platform», luego `NETSDK1178`), así que esos dos
paquetes solo se pueden empaquetar en macOS.

De ahí sale el reparto:

| Dónde | Qué se puede hacer |
|---|---|
| Devcontainer / Linux | Compilar y testear los 6 proyectos `net10.0` |
| Runner self-hosted `<etiqueta del runner>` | Todo lo anterior + `net10.0-android` (APKs) |
| Runner `macos-15` | Único lugar donde conviven los workloads `ios` y `android` → empaqueta los 2 multi-TFM |

No es una preferencia: es estructural, y está declarado como tal en `cd-nuget.yml`, en el
`Dockerfile` del devcontainer y en `scripts/nuget/tag-next-version.sh`.

---

## 2. Los seis workflows

| Workflow | Dispara | Runner | Qué hace |
|---|---|---|---|
| `ci.yml` | push a `main` (ignora `**.md` y `docs/**`), PR a `main` | self-hosted | Restore + build + `dotnet test`, sube `.trx`, comenta el PR si falla |
| `cd-nuget.yml` | tags `v*`, push a `main`, `workflow_dispatch` | mixto | Publica los 8 paquetes (ver §3) |
| `cd-android.yml` | push a `main`, tags `v*`, manual | self-hosted | APK Release de `SampleApp` y `MultaApp` por matriz |
| `cd-ios-sampleapp.yml` | push a `main` bajo `samples/MotorDsl.SampleApp/**`, `workflow_call` | `macos-15` | Build iOS del SampleApp |
| `cd-ios-multaapp.yml` | push a `main` bajo `samples/MotorDsl.MultaApp/**`, `workflow_call` | `macos-15` | Build iOS del MultaApp |
| `cd-ios-multaapp.nuget.yml` | push bajo `samples/MotorDsl.MultaApp.Nuget/**` (ver aviso), `workflow_call` | `macos-15` | Build iOS del MultaApp consumiendo NuGet |

> **Filtro de ruta muerto**: `cd-ios-multaapp.nuget.yml` filtra por
> `samples/MotorDsl.MultaApp.Nuget/**`, y esa carpeta no existe — el sample se llama
> `samples/MotorDsl.Nuget.MultaApp/`. El workflow nunca se dispara por push; solo por
> `workflow_call`. Verificable comparando el `on:` del YAML con `ls samples/`.

`DOTNET_VERSION` es `10.0.102` (GA) en todos. `cd-android.yml` fija además Java 17 e instala el
workload `maui-android` en `10.0.100`, y publica con `-p:RuntimeIdentifier=android-arm64`,
`-p:AndroidPackageFormat=apk`, `-p:AndroidKeyStore=false`.

---

## 3. `cd-nuget.yml` — tres jobs encadenados

```text
version ──┬── pack-managed  (self-hosted): restore+build+TEST+pack de los 6 net10.0
          └── pack-platform (macos-15):    restore+build+pack de Bluetooth y Maui
                    ↓
                 publish  (self-hosted): baja ambos artefactos, VERIFICA que sean 8, publica
```

**Resolución de versión** (job `version`): un tag `v1.0.14` da `1.0.14`; un `workflow_dispatch` usa
el input; cualquier otro disparo genera `0.0.0-preview.<run_number>`, que **no** se publica.

**La compuerta de los 8**: antes de publicar, el job cuenta los `.nupkg` y aborta con
`::error::Se esperaban 8 paquetes y hay N. No se publica un conjunto incompleto.` Es lo que impide
un release parcial si uno de los dos runners falló.

**Orden de publicación**: `Printing.Abstractions` primero y los consumidores después
(`Core, Parser, Rendering, Extensions, Network, Bluetooth, Maui`), con `--skip-duplicate`.

**Tests como precondición**: `pack-managed` corre `dotnet test` antes del `pack`. Ningún paquete
sale con la suite en rojo.

---

## 4. Versionado

Fuente: `docs/09_devops/estrategia-versionado_v1.0.md`.

- **SemVer** `MAJOR.MINOR.PATCH`, con `0.0.0-preview.<n>` para builds de `main`.
- **Versión unificada**: los 8 paquetes comparten siempre el mismo número.
- **La versión NO vive en los `.csproj`**: ninguno declara `<Version>`. Se inyecta en build/pack con
  `/p:Version`, `-p:PackageVersion` y `-p:MotorDslVersion`. Verificable leyendo cualquier
  `src/MotorDsl.*/*.csproj`.
- **El tag manda**: `cd-nuget.yml` toma el número del tag `v*`.

### `scripts/nuget/tag-next-version.sh`

Cubre exactamente el hueco que el workflow no resuelve: **elegir el número**. Consulta nuget.org por
HTTPS, calcula la siguiente versión y crea el tag que dispara la publicación. No necesita el SDK de
.NET, así que corre en cualquier Linux, dentro o fuera del devcontainer.

```bash
./scripts/nuget/tag-next-version.sh            # calcula, muestra y pide confirmación
./scripts/nuget/tag-next-version.sh --dry-run  # solo calcula
./scripts/nuget/tag-next-version.sh 1.0.14     # fuerza una versión
```

Existe porque un port a `.sh` del `.bat` de Windows solo podría empaquetar 6 de 8 paquetes.

---

## 5. Scripts

| Carpeta | Contenido | Plataforma |
|---|---|---|
| `scripts/local/` | `run-<Sample>.bat` (×5), `run-All.bat`, `update-packages.bat` | Windows |
| `scripts/mobile/` | `publish-<Sample>-apk.bat` (×5), `publish-all.bat`, `update-packages.bat` | Windows |
| `scripts/nuget/` | `build-motordsl-nuget.bat`, `publish-motordsl-nuget.bat`, `get-next-version.ps1`, `tag-next-version.sh`, `notas.md` | Windows + el `.sh` multiplataforma |

El `.bat` de publicación funciona porque corre en Windows, donde el workload `ios` sí existe.

---

## 6. Devcontainer

`.devcontainer/Dockerfile` + `devcontainer.json`.

- Base `mcr.microsoft.com/dotnet/sdk:10.0` (GA), **no** `devcontainers/dotnet:1-10.0`, que hoy
  entrega `10.0.100-rc.2` mientras el CI trabaja sobre GA.
- Crea un usuario `vscode` no privilegiado con UID/GID 1000 de forma idempotente, para que los
  archivos generados no queden como root en el árbol del host.
- `postCreateCommand`: `dotnet restore src/MotorDsl.Tests/MotorDsl.Tests.csproj` — restaurar los
  tests arrastra por `ProjectReference` los seis proyectos `net10.0`, que es todo lo compilable
  ahí.
- Extensiones: `ms-dotnettools.csdevkit`, `ms-dotnettools.csharp`; solución por defecto
  `PrintThermalDriver.slnx`.

Alcance declarado explícitamente en los comentarios del `json`: **solo** los TFM `net10.0`.

---

## 7. Solución y estructura de build

`PrintThermalDriver.slnx` (formato slnx, no `.sln`) declara tres carpetas: `/github.workflow/` con
los seis YAML como archivos sueltos, `/samples/` con los cinco proyectos —cuatro marcados
`<Deploy Solution="Debug|*" />`, y `MotorDsl.Nuget.Integrated.MultaApp` con `<Deploy />` sin
condición— y `/src/` con los nueve proyectos.

Propiedades comunes en todos los `src/`: `ImplicitUsings` y `Nullable` habilitados. Los dos
paquetes de plataforma llevan `AndroidLdFlags = -Wl,-z,max-page-size=16384` y
`SupportedOSPlatformVersion` iOS 15.0 / Android 24 (Bluetooth) y 25 (Maui). Cada `.csproj`
empaquetable incluye el `README.md` de la raíz como `PackageReadmeFile`.

Comando de build local mínimo:

```bash
dotnet build src/MotorDsl.Maui/MotorDsl.Maui.csproj -c Debug   # requiere workload maui
```

---

## 8. Documentación DevOps

`docs/09_devops/`: `entornos-deploy_v1.0.md`, `estrategia-versionado_v1.0.md`,
`guia-publicacion-nuget_v1.0.md`, `pipeline-ci-cd_v1.0.md`.

Nota de vigencia: esa documentación describe el estado previo a `MotorDsl.Network`. El CHANGELOG
registra que `cd-nuget.yml` pasó de publicar 4 paquetes —con otros 3 dependiendo de un script local
de Windows— a publicar los 8 desde CI. Ante discrepancia, **manda el YAML**.
