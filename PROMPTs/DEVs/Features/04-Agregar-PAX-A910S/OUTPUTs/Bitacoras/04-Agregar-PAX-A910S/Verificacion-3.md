# Verificación 3 — Factibilidad técnica (binding, vía bitmap, x86, simulador, tests)

Fecha: 2026-11-17 · Verificador escéptico · Sólo lectura de código/SDK; se editaron únicamente documentos de OUTPUTs.
Jar extraído en scratchpad (fuera del repo) desde `NeptuneLiteApi_V4.15.00_20250606.zip`.

## Lo que se intentó refutar y se sostiene
- `print(Bitmap, IPinterListener)` existe (`IPrinter.java:447`, también `:464` con cutMode) y `getStatus()` (`:299`).
- `WriteBytesAsync(byte[], PrinterProfile, ct)` (`IThermalPrinterTransport.cs:16`); `RasterPreviewRenderer` emite PNG (`:144-146`) con ancho `bitmap_max_width_px ?? 384` (`:32`): la vía (a) no requiere cambio de contrato.
- Enlace por fuente en tests: patrón real (`MotorDsl.Tests.csproj:31-32`).
- `.so` sólo `arm64-v8a` y `armeabi` (`unzip -l`); jar de 248 `.class`, ninguna llama `loadLibrary` (`grep -rla loadLibrary` vacío): las nativas las carga el `nepcore.dex` embebido.
- `getDal` llama `setReadOnly` sobre el dex (`strings NeptuneLiteUser.class`): no choca con la restricción de carga dinámica de Android 14 (**Inferido**, conocimiento de plataforma).
- CI: `pack-platform` en `macos-15` (`cd-nuget.yml:108`), `maui-android` (`:124`), conteo `-ne 8` (`:184`).
- La app tiene `RuntimeIdentifiers` con x86/x64 (`GDA.Core.APP.csproj:54`) y consume MotorDsl.Maui 1.0.17 (`:220`).

## Hallazgos
| # | Hallazgo | Evidencia | Acción |
|---|---|---|---|
| H1 | El tope de 30000 puntos citado (`IPrinter.java:220`) es de `start()` (búfer de texto), no de `print(Bitmap)`, que es la vía elegida. | `IPrinter.java:211-221` (doc de `start()`). | Corregido N01 «Tareas con dispositivo»: límite de la vía (a) no documentado, se mide en D2. |
| H2 | El «recorte a la derecha» (`IPrinter.java:601`) está documentado para `printColorBitmapWithMonoThreshold`/`printColorBitmap`, no para `print(Bitmap, …)`. | `IPrinter.java:598-622`. | Corregido N02 punto 2: el recorte del simulador pasa a **Inferido**, se confirma en D1 punto 5. |
| H3 | Falta en las decisiones `android:extractNativeLibs="true"`: `getDal` pasa `nativeLibraryDir` al `DexClassLoader`; si las `.so` no se extraen, la DAL no carga en el equipo real. Sólo figuraba como «puede hacer falta» en informe-devops:47. | R3 l.100; `strings NeptuneLiteUser.class` → `nativeLibraryDir`, `getApplicationInfo`; guía IDE (R3 l.36). | Agregado a N01 §6, N03 punto 4, N06 N4.7 y Plan-Aprobado decisión 7. |
| H4 | El conocimiento PayDroid (worktree `/vm/wt/Ng.IA-Context.Scene-pax`, `Knowledge-Test-…-App-PayDroid.md:123-124`) afirma (Inferido) que el APK sólo ARM «no instala en x86_64». R4 midió `abilist=x86_64,arm64-v8a` con `libndk_translation` en la imagen de `pay-a12-wv91`, así que probablemente sí instale (bajo traducción). | `R4-escenas-infra.md:40-43`. | **No corregido** (fuera de OUTPUTs). Recomendación: reformular como «puede instalar bajo traducción arm64; la receta usa el build con todas las ABI para no depender de eso». La receta en sí sigue siendo válida. |
| H5 | El mapeo `UnsatisfiedLinkError → Connection` supone que el error llega tal cual; el fallo nativo ocurre dentro del dex cargado por reflexión y puede llegar envuelto o como `NoClassDefFoundError` en reintentos. | Estructura de `NeptuneLiteUser` (`loadDalDex`, `Constructor`, `LOAD DAL ERR`). | **Inferido**; N01 §6 pide capturar `Java.Lang.Throwable` en `ConnectAsync`. |

## Queda dudoso (no refutado ni confirmado)
- Que el binding de las 245 clases de `com.pax.dal` compile con el recorte de Metadata.xml: sólo se sabe al compilar en U2 (plan B ya previsto).
- Renombrar `armeabi`→`armeabi-v7a`: lo indica la guía PAX; que las `.so` ARMv5 funcionen en v7a es **Inferido**.
- Default de `extractNativeLibs` que genera .NET 10 Android: no verificado; por eso se fija explícito.
- Ancho 384 px y nombre `com.pax.ipp.neptune`: siguen **Inferido** (D1).
