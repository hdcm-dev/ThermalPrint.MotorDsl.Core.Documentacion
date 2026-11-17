# 08 — Build, CI/CD y versionado

> **Propósito**: cómo se compila, se prueba, se versiona y se publica el proyecto, y qué se puede
> hacer en cada sistema operativo.
> **Fuentes primarias**: `.github/workflows/` (6), `scripts/` (incl. `scripts/local-devcontainer/`), `.devcontainer/`,
> `docs/09_devops/`, `PrintThermalDriver.slnx`. Verificado contra `main` @ `0f8413d` (2026-09-24).
> Sin SDK .NET en el host de indexado: nada de lo aquí escrito afirma que compile o que los tests pasen.

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
| Linux + Docker (`scripts/local-devcontainer/`) | APK `net10.0-android` de los 5 samples en contenedor efímero (ver §6) |
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
| `cd-ios-multaapp.nuget.yml` | **todo** push a `main` (filtro `paths:` comentado), `workflow_call` | `macos-15` | Build iOS del MultaApp consumiendo NuGet |

> **Cambio desde `e688f3c`**: el filtro `paths: samples/MotorDsl.MultaApp.Nuget/**` (carpeta
> inexistente; el sample es `samples/MotorDsl.Nuget.MultaApp/`) se **comentó** en vez de
> corregirse. Antes el workflow nunca se disparaba por push; ahora se dispara en **cada** push a
> `main`, incluidos los que solo tocan `**.md`/`docs/**`. Fuente: `git diff e688f3c..HEAD --
> .github/workflows/cd-ios-multaapp.nuget.yml`.

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
| `scripts/local/` | `run-<Sample>.bat` (×5), `run-All.bat`, `update-packages.bat`, `Readme.md` | Windows |
| `scripts/local-devcontainer/` | `run-<Sample>.sh` (×5), `run-All.sh`, `update-packages.sh`, `limpiar.sh`, `run-sample.sh`, `lib.sh`, `Dockerfile`, `interno/` (3), `Readme.md` | Linux + Docker (nuevo, `347ebfb`) |
| `scripts/mobile/` | `publish-<Sample>-apk.bat` (×5), `publish-all.bat`, `update-packages.bat`, `Readme.md` | Windows |
| `scripts/nuget/` | `build-motordsl-nuget.bat`, `publish-motordsl-nuget.bat`, `get-next-version.ps1`, `tag-next-version.sh`, `notas.md` | Windows + el `.sh` multiplataforma |

El `.bat` de publicación funciona porque corre en Windows, donde el workload `ios` sí existe.
Qué demuestra cada sample: ver `06_samples.md`.

---

## 6. `scripts/local-devcontainer/` — APK Android desde Linux

Fuente: `scripts/local-devcontainer/Readme.md` y los scripts citados. Versión Linux de
`scripts/local/`: el host solo necesita Docker.

```text
run-<Sample>.sh ─exec─> run-sample.sh <Sample> [--sin-instalar] [--rid R] [--url U]
   asegurar_imagen (lib.sh)        → docker build motordsl-android-build:net10 si falta
   contenedor "build" (--rm, repo :ro) → interno/compilar.sh → OUTPUTs/<Sample>.apk (chown al UID host)
   instalar (salvo --sin-instalar):
     ├─ contenedor ajeno con `adb fork-server` → docker cp + interno/instalar.sh ahí
     └─ si no: contenedor "adb" --privileged + /dev/bus/usb → interno/instalar.sh
```

| Pieza | Dato verificado | Fuente |
|---|---|---|
| Imagen | `FROM mcr.microsoft.com/dotnet/sdk:10.0` + JDK 17 + Android SDK (platforms 36 y 35, build-tools 36.0.0 y 35.0.0) + workload `maui-android` + `dotnet-outdated-tool`; corre como root (adb necesita el USB) | `scripts/local-devcontainer/Dockerfile` |
| Distinta del devcontainer | El devcontainer deja `net10.0-android` fuera a propósito; esta imagen no se usa como devcontainer de VS Code | ídem, cabecera |
| Persistencia | Imagen (override `MOTORDSL_IMAGEN`) y volumen `motordsl-android-cache` (override `MOTORDSL_VOLUMEN`) con `/cache/nuget` y `/cache/keystore/debug.keystore` | `lib.sh`, `interno/compilar.sh` |
| Árbol limpio | Repo montado `:ro`, copiado con `tar` excluyendo `.git`, `.vs`, `bin`, `obj`, `out`, `OUTPUTs`; `--url` reescribe `backendBaseUrl` solo en la copia | `interno/compilar.sh` |
| Build | `dotnet build -f net10.0-android -c Release -p:AndroidPackageFormat=apk -p:EmbedAssembliesIntoApk=true`, firmado con el keystore persistente (alias `androiddebugkey`); sin `--rid` lleva todas las ABIs de `<RuntimeIdentifiers>`; toma el primer `*-Signed.apk` | `interno/compilar.sh` |
| Instalación | `adb install -r`; ante `INSTALL_FAILED_UPDATE_INCOMPATIBLE`/firma distinta desinstala y reinstala (pierde datos); lanza con `monkey`; sin dispositivo sale con 1 y deja el APK | `interno/instalar.sh` |
| Selección de adb | `ADB_CONTENEDOR=<nombre>` fuerza uno; `ADB_CONTENEDOR=ninguno` fuerza el propio; auto-detección ignora contenedores `motordsl-*` | `run-sample.sh`, `lib.sh` |
| Limpieza | `trap` EXIT borra los contenedores; `limpiar.sh` borra `motordsl-(build\|adb\|update)-*`; `--todo` también volumen e imagen | `lib.sh`, `limpiar.sh` |
| `update-packages.sh` | `dotnet outdated --upgrade --include MotorDsl` sobre copia; devuelve solo los `.csproj` de `MotorDsl.Nuget.MultaApp` y `MotorDsl.Nuget.Integrated.MultaApp` si cambiaron | `interno/actualizar-paquetes.sh` |
| `run-All.sh` | `update-packages.sh` + los 5 samples; sigue ante fallos y sale 1 listando los fallidos | `run-All.sh` |
| APKs fuera de git | `OUTPUTs/*` ignorado salvo `.gitkeep` | `scripts/local-devcontainer/.gitignore` |

Soporte en los samples: los 5 `.csproj` declaran `net10.0-android` y añaden `net10.0-ios` solo con
`IsOSPlatform('windows') or IsOSPlatform('osx')` (`samples/*/*.csproj`, línea 16), lo que permite
restaurar/compilar en Linux.

> **Observación**: desde `e688f3c`, `samples/MotorDsl.Integrated.MultaApp/` también pasó de
> `ProjectReference` a `PackageReference` `MotorDsl.*` `1.0.17` (`git diff e688f3c..HEAD --
> samples/`), pero `update-packages.sh`/`.bat` solo actualizan los dos samples `Nuget`: ese
> tercer consumidor de paquetes queda fuera del refresco automático. El sample
> `MotorDsl.Nuget.Integrated.MultaApp` volvió a NuGet (comentario del `.csproj`: «Vuelto a
> PackageReference en 1.0.16»). Detalle en `06_samples.md`.

---

## 7. Devcontainer

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

Alcance declarado explícitamente en los comentarios del `json`: **solo** los TFM `net10.0`. Para
APKs en Linux, ver §6.

---

## 8. Solución y estructura de build

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

## 9. Documentación DevOps

`docs/09_devops/`: `entornos-deploy_v1.0.md`, `estrategia-versionado_v1.0.md`,
`guia-publicacion-nuget_v1.0.md`, `pipeline-ci-cd_v1.0.md`.

Nota de vigencia: esa documentación describe el estado previo a `MotorDsl.Network`. El CHANGELOG
registra que `cd-nuget.yml` pasó de publicar 4 paquetes —con otros 3 dependiendo de un script local
de Windows— a publicar los 8 desde CI. Ante discrepancia, **manda el YAML**. Tampoco mencionan
`scripts/local-devcontainer/` (su único documento es su `Readme.md`). Inventario documental: `09_docs-existentes.md`.
