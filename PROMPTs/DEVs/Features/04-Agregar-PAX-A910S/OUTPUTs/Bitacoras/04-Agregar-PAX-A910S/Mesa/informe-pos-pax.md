# Informe de la mesa: especialista en dispositivos POS/PAX

Fecha: 2026-11-17. Feature 04. Fase de sólo lectura. No se modificó código, no hubo commits ni cambios de infraestructura.

Abreviaturas: `MAT` = `Ng/Ng-Media/Instaladores/SDK-PayDroid-A910S`. `R1`…`R5` = informes en `../Relevamiento/`. Las líneas `IPrinter.java:N` y `NeptuneLiteUser:N` son del javadoc del SDK 4.15.00, citadas en R3.

## 1. Propuesta

### 1.1 Arquitectura en tres capas

1. **`MotorDsl.Pax.Binding`** (`net10.0-android`): un binding recortado de `NeptuneLiteApi_V4.15.00_20250606.jar`.
   - Contiene el jar como `<AndroidLibrary>`, `libDeviceConfig.so` (arm64-v8a y armeabi→`armeabi-v7a`) como `<AndroidNativeLibrary>`, más `libpaxcanvas.so` (arm64), y `NeptuneProguardRules.pro` como `<ProguardConfiguration>` (R3 §2, §3, §9).
   - `Metadata.xml` deja sólo `com.pax.neptunelite.api.NeptuneLiteUser`, `com.pax.dal.IDAL`, `IPrinter`, `IPrinter.IPinterListener`, `exceptions.*` y `entity.EPrintDevException`.
   - **Inferido**: si el recorte con Metadata.xml de 245 clases se vuelve costoso, la vía de respaldo es un wrapper Java mínimo (`.aar` propio con 3 métodos: `open(Context)`, `print(Bitmap)→callback`, `getStatus()`). Recomiendo intentar primero el binding recortado y fijar un límite de tiempo (*timebox*) antes de pasar al wrapper.
2. **`MotorDsl.Pax`** (transporte, `net10.0-android`): `PaxPrinterTransport : IThermalPrinterTransport` con `Kind = "pax"`, registrado por `AddPaxPrinterTransport()` con `AddSingleton`, igual que Bluetooth y Network (R1 punto 5).
   - **El transporte depende de una abstracción propia, no del binding.** Propongo `IPaxPrinterDevice` con tres operaciones: `OpenAsync`, `PrintAsync(bitmap) → PaxPrintResult(code)` y `GetStatusAsync() → int`. Hay dos implementaciones:
     - `NeptunePaxPrinterDevice` (real, usa el binding);
     - `SimulatedPaxPrinterDevice` (la impresora simulada que pide el PO, §1.4).
   - Así el transporte se testea en `net10.0` con xUnit, sin Android ni el SDK (R1 punto 11). **Inferido**: la parte que decodifica PNG a `Bitmap` queda del lado Android y se cubre con el simulador en el emulador, no en `dotnet test`.
3. **App**: elige transporte y perfil según la configuración del trío (R2 puntos 15-16). La web no cambia (R5 punto 14).

### 1.2 Vía bitmap: alternativa (a) con target propio

Es lo que R1 punto 24 llama variante de (a). El PAX no acepta ESC/POS (`MAT/README.md:38`) y la forma recomendada es `print(Bitmap, IPinterListener)` (`IPrinter.java:447`). Por eso:

- Se agrega un `DeviceProfile` PAX con target `raster-pax`, que reutiliza `RasterPreviewRenderer` (produce PNG, R1 punto 6) con `bitmap_max_width_px` igual al ancho del A910S.
- `PaxPrinterTransport.WriteBytesAsync` verifica la firma PNG (`89 50 4E 47 0D 0A 1A 0A`). Si no la encuentra, falla con `PrintErrorType.Protocol` sin llegar al dispositivo. Esto elimina la ambigüedad ESC/POS/PNG que señala R1 punto 21.
- No cambia ningún contrato público (R1 punto 21). La alternativa (b), con `WriteBitmapAsync`, rompe a `FakePrinterService` y a implementaciones externas (R1 punto 22), así que la descarto por ahora.

### 1.3 Uso de la API NeptuneLite

- **Entrada:** `NeptuneLiteUser.getInstance().getDal(context)` (`NeptuneLiteUser:55,70`), luego `IDAL.getPrinter()` (`MAT/README.md:34`). Se hace de forma perezosa, en la primera impresión o en `ConnectAsync`, y no al arrancar la app.
- **Impresión:** `print(Bitmap, listener)`, envuelto en un `TaskCompletionSource` que resuelve `onSucc()` y `onError(int)` (`IPrinter.java:470-514`), con timeout tomado de `PrinterProfile`. Si el listener nunca responde, se devuelve `Timeout`.
- **Antes de imprimir:** se llama a `getStatus()` (`IPrinter.java:299`). Si devuelve un código distinto de 0, no se imprime y se informa el error. Es barato y da un mensaje claro de "sin papel" antes de rasterizar.
- **No se mezcla** `print(Bitmap)` con `init/printBitmap/start` (`IPrinter.java:438-445`). `setGray` se expone como opción del perfil, por defecto `1` (`IPrinter.java:352`).
- **Hilo:** **Inferido**: las llamadas al DAL son RPC al servicio, así que deben correr fuera del hilo de UI (`Task.Run`).

### 1.4 Mapeo de errores: dos tablas separadas

R3 §6 muestra que las numeraciones de `getStatus/onError` y de `EPrintDevException` no coinciden. Se mapean así:

| Origen | Código | `PrintErrorType` | Mensaje para el usuario |
|---|---|---|---|
| status | 1 ocupada, -16 sin terminar | `Hardware` (reintentable) | "La impresora está ocupada" |
| status | 2 | `Hardware` | "Sin papel" |
| status | 8 / 9 | `Hardware` | "Sobrecalentamiento" / "Batería baja" |
| status | 3, -2, -4 | `Protocol` | "Ticket inválido o demasiado largo" |
| status | 4, -5, -6 | `Hardware` | "Falla de impresora" |
| excepción | 99 CONNECT | `Connection` | "Servicio de impresión PAX no disponible" |
| excepción | 101 / 103 | `Connection` | "Sin permiso / app no habilitada por PAX" |
| excepción | 100 NO_SUPPORT, 102 DISABLED | `Hardware` | "Impresora no soportada o deshabilitada" |
| `getDal` | `Exception("LOAD DAL ERR")` (`NeptuneLiteUser:134-136`) | `Connection` | "Este equipo no es un PAX o falta NeptuneService" |

Los códigos de estado se transportan como `PrinterHardwareException(code)`, que `FromException` ya traduce a `Hardware` (R1 punto 10). Para `Connection` y `Protocol` se usan las excepciones existentes. Conviene conservar el código PAX crudo en el mensaje para diagnóstico.

### 1.5 NeptuneService

- El SDK no comprueba si el servicio está, porque la llamada está comentada (`NeptuneLiteUser:71`, R3 §5).
- Propuesta: `IsAvailableAsync()` del transporte que devuelve `false` si `PackageManager.GetPackageInfo("com.pax.ipp.neptune")` falla.
  - El nombre del paquete es **Inferido** (strings del AXML, R3 §5) y debe confirmarse en el equipo.
  - Esto se complementa con try/catch sobre `getDal`.
- Como `minSdk` es 25 y `targetSdk` 36 (R2 punto 14), desde API 30 la visibilidad de paquetes exige `<queries><package android:name="com.pax.ipp.neptune"/></queries>` en el manifiesto. Es un estándar de Android; **Inferido** que se aplica, porque PayDroid del A910S es Android 12 según la escena (R4 punto 1).
- El servicio suele venir preinstalado (`ide.txt:373`). Si falta, se instala con PayDroid Tool (`ide.txt:388`), y eso necesita Windows.

### 1.6 Ancho del papel

- El material no lo documenta (R3 §8). Los 384 px son **Inferido** (`MAT/README.md:38`).
- El perfil PAX nace con 384 px marcado como provisional, configurable desde la app y no fijo en el código.
- En el equipo se mide imprimiendo una regla de 576 px con marcas cada 8 px. Lo que excede el ancho se recorta a la derecha (`IPrinter.java:601`), así que la última marca visible da el ancho real.
- También hay que respetar el límite de alto de `start()` (< 30000 puntos, `IPrinter.java:220`). **Inferido**: no está claro si se aplica a `print(Bitmap)`. Hay que probar un acta larga y, si falla con -2, partir el bitmap en franjas.

### 1.7 Impresora simulada fiel

`SimulatedPaxPrinterDevice`, seleccionable por configuración (`Pax:Mode = Simulated|Real`):

- Guarda en archivo el PNG exacto que recibiría `print(Bitmap)`, ya recortado al ancho del perfil, igual que el equipo (`IPrinter.java:601`). Así se ve si el ticket se sale del papel.
- Simula `getStatus()` y `onError` con los códigos reales (0, 1, 2, 8, 9, -2) y también 99 CONNECT y `LOAD DAL ERR`, elegidos por configuración o por una secuencia programada.
- Simula la latencia asíncrona del listener.
- Vive en `MotorDsl.Pax`, compilado para `net10.0`, para que los tests lo usen. **Inferido**: el guardado como PNG usa los bytes que ya llegan, sin Android. El recorte al ancho se hace con SkiaSharp, que ya es dependencia de MotorDsl.Maui (R1 punto 15).

### 1.8 Firma PAX, Release y Debug

- **Debug** (nuestro equipo): adb e instalación directa (`MAT/README.md:42`).
- **Release** (el equipo de la tester): PayDroid verifica la firma PAX del APK y de las `.so` (`MAT/README.md:43`). Firma Leandro, por intermedio de Martín (`MAT/README.md:44`).
  - Consecuencia: el APK para Release tiene que estar **terminado y con las `.so` dentro** antes de mandarlo. Cada cambio vuelve a pasar por Leandro. Conviene juntar los cambios y mandar un candidato por iteración.
- La APK firmada que se recibió está firmada con `CN=Android Debug` (`MAT/README.md:65`). **Inferido**: la firma PAX se agrega por encima de la firma Android; no se ve con `keytool`.
- Formato: hoy la app genera un `aab` (R2 punto 18). Para Leandro hace falta un **APK** (`-p:AndroidPackageFormat=apk`, como en `dev.sh`, R2 punto 22).
- ABIs del APK para PAX: sólo `android-arm64` y `android-arm`. Así se evitan las `.so` x86, que no sirven en el equipo, y baja el tamaño (la APK actual pesa 99,9 MB con 4 ABIs, `MAT/README.md:63-64`).

### 1.9 x86 y emulador

- El SDK no trae `.so` x86 (R3 punto 3).
- La escena Pay-Android tiene libndk_translation para arm64 (R4 puntos 9-11). **Inferido**: `libDeviceConfig` podría cargar, pero sin servicio ni hardware PAX.
- Criterio: la app **no debe romperse**. Hay que capturar `DllNotFoundException`, `Java.Lang.UnsatisfiedLinkError` y `LOAD DAL ERR`, devolver `Connection` con un mensaje claro, y permitir `Pax:Mode=Simulated` en el emulador.

## 2. Qué se hace sin el dispositivo y qué lo necesita

**Sin el dispositivo:**

- binding y compilación (en el devcontainer, R1 punto 14);
- abstracción, transporte, mapeo de errores y simulador;
- target `raster-pax` y perfil provisional de 384 px;
- tests con fake y simulador;
- detección de NeptuneService y su manejo en el emulador;
- permisos y `<queries>` en el manifiesto del trío;
- selección de transporte en la app;
- APK arm sólo con las `.so`;
- checklist del equipo.

**Con el dispositivo (checklist, no se da por cerrado):**

1. `adb shell getprop ro.build.version.sdk` y la versión de PayDroid.
2. `adb shell pm list packages | grep -i pax` (paquete de NeptuneService) y `dumpsys package com.pax.ipp.neptune | grep versionName`.
3. La versión de la WebView (`dumpsys package com.google.android.webview`, o el paquete que corresponda). Si es menor que 94, `blazor.web.js` no parsea (R4 punto 3), y si es menor que 119 falla `Promise.withResolvers` (R4 punto 4).
4. `lsusb`: vendor id, para la regla udev (R4 punto 16).
5. Medir el ancho con la regla de 576 px (§1.6) y confirmar los dpi.
6. Imprimir un acta real larga (límite de alto) y forzar sin papel y tapa abierta.
7. Ver si `com.pax.permission.PRINTER` es obligatorio (hacer la prueba sin declararlo).
8. Ciclo de firma Release con Leandro: tiempo y medio de envío (pendiente en `MAT/README.md:51`).

## 3. Riesgos

- Ancho real distinto de 384 px.
- El binding de 245 clases podría no compilar sin un recorte fuerte.
- El paquete NeptuneService no está confirmado.
- WebView del A910S < 94: el inspector web quedaría inutilizable, sin importar la impresora. **Este es el riesgo bloqueante mayor.**
- La firma Release depende de un tercero y no tiene plazo conocido.
- Sin servicios de Google, no llegan los push de Firebase y ML Kit puede fallar (`MAT/README.md:68`). Queda fuera del alcance de la impresión, pero afecta a la app en el PAX.
- Hay que reservar la identidad del paquete para Release. **Inferido**: si PAX pone las apps en una lista blanca por nombre de paquete (código 103 NOT_IN_WHITELIST), el bundle con el que se firma tiene que ser el definitivo.
