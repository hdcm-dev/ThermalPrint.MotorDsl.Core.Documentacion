# Verificación 1: la evidencia del plan, los núcleos y los conocimientos

Fecha: 2026-11-17. Verificador escéptico, con la lente de evidencia. Fase de sólo lectura: no se tocó código, git ni infraestructura. Las correcciones se hicieron únicamente en `OUTPUTs/Nucleos/`. Para revisar el SDK, los zip se extrajeron en el scratchpad de la sesión y no en el repositorio.

## Afirmaciones comprobadas (se sostienen)

| Afirmación | Evidencia |
|---|---|
| `WriteBytesAsync` existe en el contrato | `IThermalPrinterTransport.cs:17` |
| `raster-preview` emite PNG | `RasterPreviewRenderer.cs:19,144-146` |
| Los tests enlazan fuentes de Bluetooth | `MotorDsl.Tests.csproj:31-32` |
| El registro usa `AddSingleton` y los transportes coexisten | `MotorDslNetworkServiceCollectionExtensions.cs:11-26` |
| `AddProfiles` | `MotorDslBuilder.cs:28-34` (está en `src/MotorDsl.Extensions/`) |
| ESC/POS emite texto ASCII y QR | `BitmapEscPosRenderer.cs:90,108` |
| Hoy se publican 8 paquetes desde `macos-15` | `cd-nuget.yml:3,106,108,124,183-186,193`; `ls src` da 9 directorios, uno de ellos Tests |
| Versión y preview | `CHANGELOG.md:5-9,11`; `cd-nuget.yml:38-45`; `NuGet.config:5` |
| Imagen del devcontainer | `scripts/local-devcontainer/Dockerfile:4-8` |
| La base de tests es 315 | 315 casos ejecutados según R1:83. El conteo estático de `[Fact]`/`[Theory]` da 292, lo que coincide con R1:84 |
| `main` está en 0f8413d (librería) y la app en `origin/main` d6b63f3 | `git log` |
| El perfil 58HB6 está fijo | `PrintCoordinator.cs:90-93` |
| Patrón `Refresco` | `WhiteLabel.props:101` |
| `TRIO_PROPS` | `cd-main-android-build.yml:294` |
| `RuntimeIdentifiers` incluye x86 y x64 | `<app>.csproj:54` |
| La app consume paquetes NuGet 1.0.17 | `<app>.csproj:212-220` |
| Ningún manifiesto declara Bluetooth | `grep -rli bluetooth Recursos <app>/Platforms Utils` no devuelve nada |
| Rama de la impresora única y textos «por Bluetooth» | `PrinterOverlayViewModel.cs:120,149-150,180` |
| El catálogo de errores compara texto | `PrinterErrorCatalog.cs:136-147` |
| Build en el devcontainer de la app | `.devcontainer/dev.sh:103-104` |
| Homologacion | `origin/Homologacion` = c89f8588 y la rama local = 49a1427e |
| 6970c6b3 sólo está en `origin/fix08-blazor-web-compat-webview-postnet` | `git branch -r --contains` |
| `PrintService.cs` arma la URL de `ImpresoraTunnel` | `PrintService.cs:30,41` en `origin/Homologacion` |
| No existe un clon `Issue699-<app-web>` | `ls <app-web>/` sólo muestra `<app-web>`, `<app-web>.Documentacion` y `<app-web>-<equipo-1>-devcontainer`. La tarea computada decía que existía, y eso es falso |
| Líneas de `IPrinter.java` (src-html del zip NeptuneLiteApi 4.15.00) | 220: menos de 30.000 puntos; 299: `getStatus`; 438-445: «Cannot mix»; 447: `print(Bitmap, IPinterListener)`; 601: recorte por ancho |
| `NeptuneLiteUser` | :71 tiene el chequeo comentado; :134-136 lanza `LOAD DAL ERR` |
| `.so` | Sólo vienen para `arm64-v8a` y `armeabi`, ninguna para x86. `libpaxcanvas` sólo está en arm64 |
| `com.pax.ipp.neptune` | No aparece en el SDK: queda bien marcado como **Inferido** |
| udev y adb | `/etc/udev/rules.d/` sólo tiene `51-android-motorola.rules` (y vboxdrv); adb es la 29.0.6 |
| `windows-<equipo-1>` | Sus `devices` son sólo `/dev/kvm` y `/dev/net/tun` (`docker-compose.yml:18-20`) |
| SCN-PAY | :212-213: la WebView 155 no instala; :264-265: `static{}`; :269: GMS; :315: WebView real desconocida |
| Recursos | :354: acceso por adb remoto; `KIT/comun.sh:37-50`, citado en App-Android:282-283 |

## Hallazgos confirmados

| # | Hallazgo | Evidencia | Acción |
|---|---|---|---|
| H1 | El Núcleo 03 atribuye «Ya cargué papel — Reintentar» a `(:286-313)` justo después de `PrinterErrorCatalog`, lo que lleva a leer `PrinterErrorCatalog.cs`. En realidad el texto está en el ViewModel | `grep -rn "Ya cargu"` → `PrinterOverlayViewModel.cs:283,293` | **Corregido** en `Nucleos/03` |
| H2 | El Núcleo 04 dice «fix08 ya ensayado 2026-11-12, `SCN-PAY:264-265`». Esas líneas describen el error, no el ensayo. Además, lo que se ensayó fue un script bajado a la sintaxis de Chrome 91 servido por el proxy (un control del mecanismo), no el equipo real | `SCN-PAY:318-320` | **Corregido** en `Nucleos/04` |
| H3 | El Núcleo 06 cita `SCN-PAY:264-265,315` para el umbral de 119, pero esas líneas sólo respaldan el de 94 | `Promise.withResolvers` y 119 están en `SCN-PAY:319,342` | **Corregido** en `Nucleos/06` (se completó la cita) |
| H4 | El commit 5e468dc inserta 5 líneas en `Knowledge-Test-…-App-Android.md` (hunk `@@ -338,0 +339,5 @@`). Con eso, la fila de trazabilidad que estaba en la línea 471 pasa a la 476. `SCN-PAY:349` (1.0.3) cita `App-Android.md:471`, así que la cita queda corrida | `git show HEAD~1:… \| sed -n 471p` contra `sed -n 476p` en el worktree | **No corregido**: queda fuera de `OUTPUTs`, y la escena Pay-Android no se toca. Hay que decidirlo en el worktree: mover el párrafo o anotar el corrimiento |

## Queda dudoso

- **D1:** «el A910S llega en Debug» sale del prompt del PO (`Agregar-PAX-A910s.md:28,34`). En cambio, `SCN-PAY:321` dice que «el equipo real es de producción, sin adb». **Inferido:** son dos unidades distintas (la de producción del fix 08 y la nueva). Conviene confirmarlo con el PO antes de D1.
- **D2:** el estado de los permisos Bluetooth en el nupkg MotorDsl.Bluetooth 1.0.17 no se verificó. El Núcleo 03 ya lo marca como **Inferido**.
- **D3:** las líneas de `ide.txt` (373 y 388) no se revisaron: el archivo es texto extraído de un PDF y no está en el material.
- **D4:** el ancho de 384 px y que el APK sólo ARM no instale en x86_64 siguen marcados como **Inferido**, y la marca es correcta.
