# Núcleo 01 — Binding NeptuneLite, transporte `pax` y vía bitmap

Trazabilidad: T1, T2, T3, T5 (parte), D2. Depende de: nada. Lo consumen: N02, N03, N06, N07.

## Alcance
Paquete nuevo de la librería que imprime en la impresora interna del A910S a través del SDK NeptuneLite 4.15.00, sin cambiar contratos públicos.

## Decisión de la mesa
1. **Vía bitmap (a):** el PNG que produce `RasterPreviewRenderer` (target `raster-preview`, `src/MotorDsl.Maui/Renderers/RasterPreviewRenderer.cs:19,144-146`) viaja por el `WriteBytesAsync` existente (`src/MotorDsl.Printing.Abstractions/Contracts/IThermalPrinterTransport.cs:17`). El transporte valida la firma PNG `89 50 4E 47`; cualquier otra entrada → error `Protocol`. Se decodifica a `Android.Graphics.Bitmap` y se llama `print(Bitmap, IPinterListener)` (R3 §4, `IPrinter.java:447`), envuelto en `TaskCompletionSource` con timeout, fuera del hilo de UI, con `getStatus()` previo (`IPrinter.java:299`). No se mezcla con `init/printBitmap/start` (`IPrinter.java:438-445`).
2. **Un solo paquete `MotorDsl.Pax`**, TFM `net10.0-android`, con el binding dentro (`<AndroidLibrary>` del jar, `.so` `libDeviceConfig` arm64-v8a y armeabi→armeabi-v7a, `libpaxcanvas` arm64, `Transforms/Metadata.xml` recortado a `com.pax.dal`/`IDAL`/`IPrinter`/`exceptions`/`entity`/`com.pax.neptunelite.api`, reglas ProGuard -keep) (R3 §2-3, §9). Total de paquetes: 9.
3. **Abstracción propia `IPaxPrinterDevice`** (open/getStatus/print(png)/close) entre transporte y SDK: `NeptunePaxPrinterDevice` (real) y `SimulatedPaxPrinterDevice` (N02). El transporte, el mapeo de errores y el simulador se escriben **sin tipos Android** en archivos que `MotorDsl.Tests` (net10.0) enlaza como fuente, igual que hoy con `BluetoothPrinterTransport.Chunking.cs` (`src/MotorDsl.Tests/MotorDsl.Tests.csproj:31-32`). La decodificación PNG→Bitmap vive en la implementación Neptune.
4. **Kind = `"pax"`**, registro `AddPaxPrinterTransport(Action<PaxPrinterOptions>?)` con `AddSingleton` (patrón de `src/MotorDsl.Network/MotorDslNetworkServiceCollectionExtensions.cs:11-26`), coexistiendo con Bluetooth. `DiscoverAsync` devuelve una única impresora integrada `pax-internal`.
5. **Mapeo de errores en dos tablas separadas** (las numeraciones no coinciden, R3 §6 l.140): (i) `getStatus/start/onError`: 0 ok; 1 ocupada; 2 sin papel; 8 sobrecalentamiento; 9 voltaje; -2 too long; resto → `Hardware`; (ii) `EPrintDevException`: 5 OVER_HEATING, 8 TOO_LONG → `Hardware`; 99 CONNECT, 101 NO_PERMISSION, 103 NOT_IN_WHITELIST → `Connection`. `Exception("LOAD DAL ERR")` (`NeptuneLiteUser` l.134-136) y `UnsatisfiedLinkError` → `Connection`. Se lanza `PrinterHardwareException` (→ `Hardware`, R1 §5) con una propiedad **aditiva** de causa (`PaperOut, Overheat, Busy, LowVoltage, TooLong, Other`) en MotorDsl.Core para que la app no compare texto (hoy `PrinterErrorCatalog.cs:136-147` lo hace).
6. **Carga diferida:** `getDal` se llama recién en `ConnectAsync`; detección de NeptuneService con PackageManager + `<queries>` como diagnóstico (el SDK no la hace: `NeptuneLiteUser:71` comentado). Nunca tira la app en x86 ni sin servicio. `getDal` carga un `nepcore.dex` con `DexClassLoader` usando `nativeLibraryDir` como ruta de librerías (R3 §5 l.100; `strings NeptuneLiteUser.class` → `nativeLibraryDir`, `LOAD DAL ERR`): las `.so` tienen que estar **extraídas** en el dispositivo, por eso el manifiesto del trío PAX lleva `android:extractNativeLibs="true"` (guía del IDE, R3 §2; N03 punto 4). **Inferido:** como el fallo nativo ocurre dentro del dex cargado por reflexión, puede llegar envuelto (`LOAD DAL ERR`, `InvocationTargetException`, `ExceptionInInitializerError`, `NoClassDefFoundError` en reintentos); el transporte captura `Java.Lang.Throwable` en `ConnectAsync` y lo mapea a `Connection` [Verificacion-3 H3, H5].

## Alternativas descartadas
- **(b) `WriteBitmapAsync`:** obliga a tocar `IThermalPrinterService` y `FakePrinterService` (R1 §8). Se reabre si aparece un segundo transporte no ESC/POS.
- **(c) decodificar `GS v 0`:** inviable, el renderer emite texto ESC/POS ASCII (`BitmapEscPosRenderer.cs:108`), QR `GS ( k` (:90) (R1 §3, §8).
- **Target `raster-pax` (pos-pax):** no aporta mientras `raster-preview` con `bitmap_max_width_px` alcance; se evita código nuevo. **Inferido**.
- **Paquete `MotorDsl.Pax.Binding` separado (pos-pax):** 10 paquetes sin consumidor del SDK crudo. Queda como plan B si el binding embebido no compila.
- **Agregar TFM `net10.0` al paquete (analista):** superficie sin uso; la testeabilidad se logra enlazando fuentes (devops).
- **Wrapper Java .aar / JNI:** plan B con timebox si el recorte de 245 clases no compila (R3 §9.4).

## Tareas
- **Sin dispositivo:** crear proyecto y binding; compilar en `scripts/local-devcontainer/` (imagen con `maui-android`, `Dockerfile:4-8`; el host no tiene workloads, R1 §7); transporte, mapeo, DI; tests (N06).
- **Con dispositivo (D2):** imprimir un acta real; verificar que la DAL carga (`getDal`) y los códigos reales de `onError`; límite de alto en actas largas: el material sólo documenta el tope de 30000 puntos para `start()` (búfer de texto, `IPrinter.java:211-221`), no para `print(Bitmap, IPinterListener)`; para la vía (a) el límite de alto **no está documentado** y se mide en D2 con el acta más larga [Verificacion-3 H1].

## Criterios de aceptación
CA-01.1 compila `net10.0-android` en el devcontainer. CA-01.2 `dotnet test` en verde con los tests nuevos (base 315, R1 §6). CA-01.3 entrada no PNG → `PrintErrorType.Protocol`. CA-01.4 cada código de ambas tablas tiene test. CA-01.5 sin NeptuneService / en x86 → `Connection`, sin crash. CA-01.6 Bluetooth y `pax` coexisten en DI.

## Evidencia
../Bitacoras/04-Agregar-PAX-A910S/Relevamiento/R1-libreria.md §1-8 · ../Bitacoras/04-Agregar-PAX-A910S/Relevamiento/R3-pax-sdk.md §2-9 · ../Bitacoras/04-Agregar-PAX-A910S/Mesa/informe-analista-sistemas.md · ../Bitacoras/04-Agregar-PAX-A910S/Mesa/informe-pos-pax.md · ../Bitacoras/04-Agregar-PAX-A910S/Mesa/informe-devops.md
