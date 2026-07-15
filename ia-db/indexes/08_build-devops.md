# Índice 08 — Build & DevOps (MotorDsl)

> **Propósito:** índice temático de build, scripts, CI/CD, versionado y empaquetado NuGet del
> proyecto MotorDsl (repo `PrintThermal_Motor_Maui`).
> **Fuentes primarias:** `scripts/local/`, `scripts/mobile/`, `scripts/nuget/`,
> `.github/workflows/` (6 yml), `NuGet.config`, `CHANGELOG.md`, `README.md`, `vs.bat`,
> `.github/copilot-instructions.md`, `docs/09_devops/`, `nupkg/Readme.md`.
> **Referencia de versión:** `v1.0.13 @83677eb` (HEAD de `main`; tags `v1.0.0`…`v1.0.13`
> verificados con `git tag`).
> Todas las rutas son relativas a la raíz del repo origen
> `f:\repos\ng-sa\Workspace-GDA\Librerias\PrintThermal_Motor_Maui\`. Lo no verificable en
> fuente se marca «No verificado».

---

## 1. Scripts

### 1.1 `scripts/local/` — build + run de samples en Android (dispositivo conectado)

Documentados en `scripts/local/Readme.md`. Patrón común de los `run-*.bat`: agregan
`C:\Program Files (x86)\Android\android-sdk\platform-tools` al PATH, verifican con
`adb devices` que haya un dispositivo en estado `device`, y ejecutan
`dotnet build "<sample>.csproj" -t:Run -f net10.0-android`.

| Script | Qué hace | Prerequisitos |
|---|---|---|
| `scripts/local/run-MotorDsl.SampleApp.bat` | Compila y lanza `samples/MotorDsl.SampleApp` en Android | .NET 10 SDK, workload `maui-android`, Android SDK, dispositivo/emulador con depuración USB |
| `scripts/local/run-MotorDsl.MultaApp.bat` | Ídem para `samples/MotorDsl.MultaApp` | Ídem |
| `scripts/local/run-MotorDsl.Integrated.MultaApp.bat` | Ídem para `samples/MotorDsl.Integrated.MultaApp` | Ídem |
| `scripts/local/run-MotorDsl.Nuget.MultaApp.bat` | Ídem para `samples/MotorDsl.Nuget.MultaApp` (consume paquetes NuGet) | Ídem + paquetes `MotorDsl.*` resolubles (nuget.org o `./nupkg`) |
| `scripts/local/run-MotorDsl.Nuget.Integrated.MultaApp.bat` | Ídem para `samples/MotorDsl.Nuget.Integrated.MultaApp` | Ídem |
| `scripts/local/run-All.bat` | Encadena `update-packages.bat` + los 5 `run-*` anteriores | Ídem |
| `scripts/local/update-packages.bat` | Actualiza `<PackageReference>` `MotorDsl.*` de los 2 samples Nuget a la última versión estable vía `dotnet outdated --upgrade --include MotorDsl` (instala `dotnet-outdated-tool` si falta) | .NET SDK, internet (nuget.org) |
| `scripts/local/Readme.md` | Catálogo, uso típico y troubleshooting (workloads, libQuestPdfSkia, adb) | — |

Limitación documentada (`scripts/local/Readme.md`): `update-packages.bat` upgradea solo los 4
paquetes originales (`Core`, `Parser`, `Rendering`, `Extensions`); los 3 nuevos (`Maui`,
`Bluetooth`, `Printing.Abstractions`) se consumían por `<ProjectReference>` en «Fase 1».

### 1.2 `scripts/mobile/` — publicación de APK firmado (Release, android-arm64)

Documentados en `scripts/mobile/Readme.md`. Patrón común de los `publish-*-apk.bat`:
(0) patcheo opcional de `backendBaseUrl` en `Resources/Raw/motordsl-config.json` si se pasa
una URL por argumento; (1) `dotnet clean`; (2) `dotnet publish -f net10.0-android -c Release
-p:RuntimeIdentifier=android-arm64 -p:AndroidPackageFormat=apk -p:EmbedAssembliesIntoApk=true`;
(3) localiza el `*-Signed.apk`; (4) lo copia a `out/mobile/<NombreSample>.apk`.
`EmbedAssembliesIntoApk=true` es obligatorio para poder instalar con `adb install`.

| Script | Qué hace | Prerequisitos |
|---|---|---|
| `scripts/mobile/publish-MotorDsl.SampleApp-apk.bat` | APK firmado de `MotorDsl.SampleApp` → `out/mobile/MotorDsl.SampleApp.apk` | .NET 10 SDK, workload MAUI Android, Android SDK en `C:\Program Files (x86)\Android\android-sdk` |
| `scripts/mobile/publish-MotorDsl.MultaApp-apk.bat` | APK de `MotorDsl.MultaApp` | Ídem |
| `scripts/mobile/publish-MotorDsl.Integrated.MultaApp-apk.bat` | APK de `MotorDsl.Integrated.MultaApp` | Ídem |
| `scripts/mobile/publish-MotorDsl.Nuget.MultaApp-apk.bat` | APK de `MotorDsl.Nuget.MultaApp` (nota: el destino tiene typo `MotorDsl.Nuget.MultaAppt.apk`) | Ídem |
| `scripts/mobile/publish-MotorDsl.Nuget.Integrated.MultaApp-apk.bat` | APK de `MotorDsl.Nuget.Integrated.MultaApp` | Ídem |
| `scripts/mobile/publish-all.bat` | Encadena los 5 publish (el call a `update-packages.bat` está comentado por default) | Ídem |
| `scripts/mobile/update-packages.bat` | Copia idéntica del helper de `scripts/local/update-packages.bat` | Ídem |
| `scripts/mobile/Readme.md` | Catálogo, uso, troubleshooting (16 KB pages, tamaño APK, QuestPDF) | — |

### 1.3 `scripts/nuget/` — build y publicación de los 7 paquetes en nuget.org

| Script | Qué hace | Prerequisitos |
|---|---|---|
| `scripts/nuget/build-motordsl-nuget.bat` | Restore + Build Release de las 7 librerías de `src/` (Printing.Abstractions, Core, Parser, Rendering, Extensions, Bluetooth, Maui). NO empaqueta ni publica | .NET 10 SDK |
| `scripts/nuget/get-next-version.ps1` | `param($PackageName, $Fallback="1.0.0")` — consulta `https://api.nuget.org/v3-flatcontainer/<id>/index.json`, toma la última versión estable `X.Y.Z` y devuelve `X.Y.(Z+1)` por stdout (diagnóstico a stderr). 404 = paquete inexistente → fallback `1.0.0` | PowerShell, internet; no requiere API key (solo lectura) |
| `scripts/nuget/publish-motordsl-nuget.bat` | Pipeline local completo en 7 pasos: [0] resuelve API key (`MOTORDSL_NUGET_API_KEY` o prompt); calcula versión unificada = `max(next(patch))` de los 7 paquetes; [1] restore; [2] build Release con `/p:Version` + `/p:MotorDslVersion`; [3] `dotnet test` de `src/MotorDsl.Tests` (aborta si fallan); [4] `dotnet pack` con `-p:PackageVersion` + `-p:MotorDslVersion` → `./nupkg/`; [5] `dotnet nuget push` a nuget.org con `--skip-duplicate` en orden topológico; [6] tag git `v<version>` + push a origin (dispara `cd-nuget.yml`); [7] limpia cache HTTP de NuGet | .NET 10 SDK, API key de nuget.org con scope push, git con acceso a origin, internet |
| `scripts/nuget/notas.md` | Documentación del script: los 7 paquetes, versión unificada anti-`NU1605`, variable `MotorDslVersion`, orden de push, estrategias alternativas de versionado (manual, prerelease, MinVer) | — |

Orden de push por dependencias (`scripts/nuget/notas.md` y `publish-motordsl-nuget.bat`):
`Printing.Abstractions → Core → Parser → Rendering → Extensions → Bluetooth → Maui`.

### 1.4 Raíz

| Script | Qué hace | Prerequisitos |
|---|---|---|
| `vs.bat` | Una sola línea: `code .` — abre el repo en VS Code | VS Code en PATH |

---

## 2. Workflows GitHub Actions (`.github/workflows/`, 6 yml)

| Workflow | Nombre | Trigger | Runner / Jobs | Qué publica |
|---|---|---|---|---|
| `ci.yml` | CI - Tests | push a `main` (ignora `**.md` y `docs/**`) y PR a `main` | `ubuntu-latest`, job `test` («185 tests — MotorDsl.Tests»): restore/build/test de `src/MotorDsl.Tests` en Release, .NET `10.0.102` | Artifact `test-results-<run>` (`.trx`, 7 días). Si falla en PR, comenta el PR vía `github-script` |
| `cd-nuget.yml` | CD NuGet - Publish MotorDsl | push de tags `v*`, push a `main`, `workflow_dispatch` (input `version`) | `ubuntu-latest`, job `publish-nuget`: determina versión (tag sin `v` / input / `0.0.0-preview.<run_number>` en main), restore+build+test, `dotnet pack` de **4 proyectos** (Core, Parser, Rendering, Extensions) con `-p:PackageVersion` | Push a `https://api.nuget.org/v3/index.json` con `secrets.NUGET_API_KEY` + `--skip-duplicate` **solo** en tag `v*` o dispatch; siempre sube artifact `nuget-packages-<version>` (30 días) |
| `cd-android.yml` | CD Android - APK Release | push a `main`, tags `v*`, `workflow_dispatch` | `ubuntu-latest`, job `build-android` con matrix (SampleApp, MultaApp): Java 17 (microsoft), .NET `10.0.102`, workload `maui-android 10.0.100`, `dotnet publish -p:AndroidPackageFormat=apk -p:AndroidKeyStore=false` | Artifacts `SampleApp-APK-<run>` y `MultaApp-APK-<run>` (`com.motordsl.*-Signed.apk`) |
| `cd-ios-sampleapp.yml` | CD iOS - SampleApp - MotorDsl | push a `main` con paths `samples/MotorDsl.SampleApp/**`; `workflow_call` | `macos-15`, job `publish-ios`: descarga Xcode 26.0 desde Google Drive (`gdown`), instala .NET `10.0.102` + workloads `ios maui maui-ios 10.0.100`, build para simulador `iossimulator-arm64` sin firma real, zip del `.app` | Artifact `<fecha>_<version>_com.motordsl.sampleapp.app.zip` (1 día) |
| `cd-ios-multaapp.yml` | CD iOS - MultaApp - MotorDsl | push a `main` con paths `samples/MotorDsl.MultaApp/**`; `workflow_call` | Ídem SampleApp pero proyecto `MotorDsl.MultaApp` | Artifact `<fecha>_<version>_com.motordsl.multaapp.app.zip` (1 día) |
| `cd-ios-multaapp.nuget.yml` | CD iOS - MultaApp - MotorDsl (nombre duplicado con el anterior) | push a `main` con paths `samples/MotorDsl.MultaApp.Nuget/**`; `workflow_call` | Ídem, proyecto `MotorDsl.MultaApp.Nuget` | Artifact `.app.zip` del sample Nuget (1 día). Ver hallazgo H4: la ruta que dispara y el proyecto no existen en `samples/` |

Notas transversales de los 3 workflows iOS: Xcode `26.0` se baja de Google Drive
(`XCODE_GOOGLE_FILE_INSTALLER_ID`), simulador `iPhone 17 Pro Max`, versión de bundle leída de
`Platforms/iOS/Info.plist` (`CFBundleVersion` / `CFBundleShortVersionString`), firma ad-hoc
(`codesign --sign "-"`) con `Entitlements.Development.plist`.

---

## 3. Estrategia de versionado

Fuente normativa: `docs/09_devops/estrategia-versionado_v1.0.md` (v1.0, Aprobado, 2026-03-28).
Confirmada operativamente por `scripts/nuget/publish-motordsl-nuget.bat`, `scripts/nuget/notas.md`,
`.github/workflows/cd-nuget.yml` y `CHANGELOG.md`.

| Aspecto | Regla | Fuente |
|---|---|---|
| Esquema | SemVer `MAJOR.MINOR.PATCH`; preview `0.0.0-preview.<run_number>` en builds de `main` | `docs/09_devops/estrategia-versionado_v1.0.md` §2 |
| La versión NO vive en los `.csproj` | Ningún proyecto empaquetable declara `<Version>`; se inyecta en build/pack vía `/p:Version`, `-p:PackageVersion`, `-p:MotorDslVersion` | Ídem §3; `CHANGELOG.md` (encabezado); `publish-motordsl-nuget.bat` pasos [2] y [4] |
| Auto-bump de patch | `scripts/nuget/get-next-version.ps1` consulta el flat container de nuget.org y devuelve `X.Y.(Z+1)`; fallback `1.0.0` | Ídem §4; el propio script |
| Versión unificada | Los 7 paquetes salen siempre con la misma versión = `max(next(patch))`, para evitar downgrade `NU1605` | Ídem §5; `notas.md`; `publish-motordsl-nuget.bat` |
| Variable `MotorDslVersion` | Propiedad MSBuild extra para que los `.csproj` referencien esa versión en `PackageReference` internos futuros | `scripts/nuget/notas.md` §«Variable MotorDslVersion» |
| Publicación desde CI | `cd-nuget.yml` publica a nuget.org solo en tags `v*` o `workflow_dispatch`; push a `main` produce solo artifact preview | Ídem §6; `.github/workflows/cd-nuget.yml` |
| Tag git | Cada release lleva tag `v<version>` creado y pusheado por `publish-motordsl-nuget.bat` tras el push exitoso; el tag dispara `cd-nuget.yml` | Ídem §7 |
| Inmutabilidad | Versiones publicadas no se sobrescriben; `--skip-duplicate`; error → nueva versión PATCH | Ídem §8 |
| Última versión | `1.0.13` (2026-07-13), tag `v1.0.13` existente; HEAD `main` = `83677eb` | `CHANGELOG.md`; `git tag` / `git log` |

`CHANGELOG.md` (formato Keep a Changelog + SemVer) documenta únicamente `[1.0.13]`:
fix de rasterizado SkiaSharp (`SKImage.FromEncodedData`), propagación de `bold` en
`LayoutEngine`, manejo por severidad en `BitmapEscPosRenderer`, y limpieza de
`Console.WriteLine`. Historia previa a 1.0.13: No verificado (no hay entradas anteriores).

---

## 4. Empaquetado NuGet

### 4.1 Los 7 paquetes

Fuente: `README.md` §«Paquetes NuGet» (tabla con TFM/rol/dependencias),
`scripts/nuget/notas.md`, `docs/09_devops/estrategia-versionado_v1.0.md` §5.

| Paquete | TFM | Rol (resumen del README) |
|---|---|---|
| `MotorDsl.Core` | net10.0 | Núcleo: contratos, modelos, evaluador, layout |
| `MotorDsl.Parser` | net10.0 | Parser DSL JSON → AST (dep: Core) |
| `MotorDsl.Rendering` | net10.0 | Renderers Text + EscPos básicos (dep: Core) |
| `MotorDsl.Extensions` | net10.0 | Fluent DI: `AddMotorDslEngine`, `AddTemplates`, `AddProfiles`, `AddRenderer` (dep: Core, Parser, Rendering) |
| `MotorDsl.Printing.Abstractions` | net10.0 | Contratos transport-agnostic (`IThermalPrinterTransport`, `IThermalPrinterService`, `PrinterDevice`) + orquestador con retry/eventos (dep: Core) |
| `MotorDsl.Bluetooth` | net10.0-android;net10.0-ios | Transport BT Classic SPP (Android); iOS lanza `PlatformNotSupportedException` (dep: Printing.Abstractions) |
| `MotorDsl.Maui` | net10.0-android;net10.0-ios | Controles MAUI, renderers (PDF, ESC/POS bitmap, raster preview), error handler y diagnóstico (dep: Core, Rendering, Extensions, Printing.Abstractions) |

Instalación mínima para apps MAUI: `MotorDsl.Maui` + `MotorDsl.Bluetooth` (el resto llega
transitivo) — `README.md` §TL;DR.

### 4.2 `NuGet.config` (raíz)

`<clear />` + dos fuentes en orden: `local-nupkg` → `./nupkg` (relativa al config) y
`nuget.org` → `https://api.nuget.org/v3/index.json` (protocolVersion 3). Permite probar
samples `Nuget.*` contra paquetes recién empacados antes del push (racional completo en
`nupkg/Readme.md`, incl. advertencia sobre el caché global `%userprofile%\.nuget\packages`).

### 4.3 Carpeta `nupkg/`

Destino de `dotnet pack` del script local (paso [4/7]) y fuente NuGet local. Gitignored según
`README.md` §Estructura; hoy solo contiene `nupkg/Readme.md` (cómo referenciar `.nupkg`
locales desde `samples/`: opción recomendada = `NuGet.config` raíz; alternativas
`dotnet nuget add source` y `<RestoreSources>`).

### 4.4 Documentación devops relacionada

| Documento | Contenido |
|---|---|
| `docs/09_devops/estrategia-versionado_v1.0.md` | SemVer, inyección de versión, versión unificada, tags, inmutabilidad (Aprobado) |
| `docs/09_devops/guia-publicacion-nuget_v1.0.md` | Empaquetado/publicación/consumo; dependencias transitivas; enfoque granular vs monolítico (Aprobado, 2026-04-02) |
| `docs/09_devops/pipeline-ci-cd_v1.0.md` | Pipeline CI/CD completo: triggers, build, tests, pack, publish, APK Android, iOS simulador (Aprobado, 2026-03-29) |
| `docs/09_devops/entornos-deploy_v1.0.md` | Entornos DEV → QA → STAGING (opcional) → PROD y reglas de promoción (Aprobado) |

---

## 5. `.github/copilot-instructions.md` (contexto para agentes)

Contiene: stack (.NET 10, MAUI, xUnit), estructura del repo, las 2 modalidades de entrada del
motor (`format: "template"` clásico con pipeline Parse→Evaluate→Layout→Render vs
`format: "integrated"` sin Evaluate), guías de diagnóstico cuando falla un workflow
(Android/iOS/tests/NuGet), tabla de workflows y notas de implementación iOS.
Varias secciones están desactualizadas respecto del repo actual — ver hallazgos H5–H7.

---

## 6. Hallazgos / divergencias (con fuente)

| # | Hallazgo | Fuentes |
|---|---|---|
| H1 | `cd-nuget.yml` empaqueta y publica solo **4** paquetes (Core, Parser, Rendering, Extensions), mientras el script local y la estrategia de versionado publican **7**. `scripts/nuget/notas.md` afirma que el workflow «hace lo equivalente desde CI» — hoy no es equivalente | `.github/workflows/cd-nuget.yml` step «Pack los 4 proyectos»; `scripts/nuget/publish-motordsl-nuget.bat`; `scripts/nuget/notas.md` |
| H2 | Conteo de tests inconsistente: `ci.yml` dice «185 tests — MotorDsl.Tests»; `copilot-instructions.md` dice «212 tests (185 originales + 27 del formato integrado)» | `.github/workflows/ci.yml` (job name); `.github/copilot-instructions.md` §Stack |
| H3 | `cd-ios-multaapp.yml` y `cd-ios-multaapp.nuget.yml` tienen el mismo `name:` («CD iOS - MultaApp - MotorDsl»), lo que confunde la UI de Actions | Ambos yml, línea 1 |
| H4 | `cd-ios-multaapp.nuget.yml` apunta a `samples/MotorDsl.MultaApp.Nuget/**` y proyecto `MotorDsl.MultaApp.Nuget.csproj`, pero la carpeta real es `samples/MotorDsl.Nuget.MultaApp/`; además su step «Verificar net10.0-ios» chequea `MotorDsl.MultaApp.csproj` (nombre de archivo equivocado). El trigger por paths nunca coincidiría | `.github/workflows/cd-ios-multaapp.nuget.yml` líneas 8, 24-26, 198; listado real de `samples/` |
| H5 | `copilot-instructions.md` dice que el destino NuGet es GitHub Packages (`nuget.pkg.github.com`, `GITHUB_TOKEN`); el workflow real publica en nuget.org con `NUGET_API_KEY` | `.github/copilot-instructions.md` §«Error de NuGet»; `.github/workflows/cd-nuget.yml` |
| H6 | `copilot-instructions.md` lista un sample `MotorDsl.MultaApp.Nuget/` (inexistente; los reales son `MotorDsl.Nuget.MultaApp` y `MotorDsl.Nuget.Integrated.MultaApp`) y omite `src/MotorDsl.Printing.Abstractions`, `src/MotorDsl.Bluetooth` y `src/MotorDsl.Maui`; su tabla de workflows lista 5 de los 6 (falta `cd-ios-multaapp.nuget.yml`) | `.github/copilot-instructions.md` §Estructura y §Workflows; `ls samples/`, `ls .github/workflows/` |
| H7 | `copilot-instructions.md` y `ci.yml` citan `PrintThermalDriver.sln`; la solución real en la raíz es `PrintThermalDriver.slnx` | `.github/copilot-instructions.md`; `.github/workflows/ci.yml` step «Comentar PR»; listado raíz del repo |
| H8 | Typo en salida de `publish-MotorDsl.Nuget.MultaApp-apk.bat`: genera `out/mobile/MotorDsl.Nuget.MultaAppt.apk` (una `t` extra). Otros publish-*.bat tienen mensajes de error internos que nombran al proyecto equivocado (copy-paste), sin efecto funcional | `scripts/mobile/publish-MotorDsl.Nuget.MultaApp-apk.bat` (`OUT_APK`) |
| H9 | `docs/README.md` §Estructura menciona `scripts/ (local | mobile | nuget | docker)`; la carpeta `scripts/docker/` no existe | `docs/README.md`; `ls scripts/` |
| H10 | `cd-nuget.yml` también corre en cada push a `main` (versión `0.0.0-preview.<run_number>`, sin publish) — costo de CI por push; coherente con la estrategia §6 pero fácil de confundir con una publicación | `.github/workflows/cd-nuget.yml` on.push.branches |
| H11 | Los workflows iOS descargan el instalador de Xcode 26.0 desde un Google Drive personal vía `gdown` (ID hardcodeado) — dependencia externa no reproducible si el archivo desaparece | `cd-ios-*.yml` env `XCODE_GOOGLE_FILE_INSTALLER_ID` |

---

## 7. Trazabilidad rápida (cheat-sheet)

- ¿Cómo se publica una release? → `scripts/nuget/publish-motordsl-nuget.bat` (local, 7 paquetes,
  tag `v*`) → el tag dispara `.github/workflows/cd-nuget.yml` (CI, hoy 4 paquetes).
- ¿Dónde está definida la versión? → En ningún `.csproj`; se calcula con
  `scripts/nuget/get-next-version.ps1` y se inyecta con `-p:PackageVersion` /
  `-p:MotorDslVersion` (norma: `docs/09_devops/estrategia-versionado_v1.0.md`).
- ¿Cómo pruebo paquetes sin publicarlos? → `dotnet pack` a `./nupkg` + fuente `local-nupkg`
  de `NuGet.config` (detalle: `nupkg/Readme.md`).
- ¿Cómo corro un sample en un teléfono? → `scripts/local/run-*.bat`; ¿APK distribuible? →
  `scripts/mobile/publish-*-apk.bat` (`EmbedAssembliesIntoApk=true`).
- ¿Qué corre en cada PR? → `ci.yml` (tests de `src/MotorDsl.Tests` en ubuntu, .NET 10.0.102).
