# Núcleo 02 — Perfil PAX e impresora PAX simulada

Trazabilidad: T4, T5, D1 (ancho). Depende de: N01. Lo consumen: N03, N06.

## Alcance
Perfil de render/transporte del A910S con ancho parametrizable, e impresora simulada seleccionable por configuración.

## Decisión
1. **Perfil:** la librería no trae presets de `DeviceProfile` (R1 §4: se cargan con `AddProfiles`, `MotorDslBuilder.cs:28-34`). Se documenta y se expone una ayuda `PaxProfiles.A910S(int widthPx = 384)` que devuelve `DeviceProfile("pax_a910s", 32, "raster-preview")` con `supports_bitmap=true` y `bitmap_max_width_px=widthPx`, más un `PrinterProfile.PaxA910S` con timeouts propios (las demoras BT no aplican, R1 §4 **Inferido**). **384 px es provisional e Inferido**: el material no documenta el ancho (R3 §8); `MAT/README.md:38` lo estima.
2. **`SimulatedPaxPrinterDevice`**, implementa `IPaxPrinterDevice`: recibe el PNG exacto que iría a `print(Bitmap)`, lo recorta al ancho del perfil (**Inferido**: el recorte a la derecha está documentado para `printColorBitmap*` (`IPrinter.java:598-622`), no para `print(Bitmap, IPinterListener)`; se confirma en D1 punto 5) [Verificacion-3 H2], lo vuelca a `<carpeta>/pax-<timestamp>.png` y responde según un estado configurable: `Ok, Busy(1), PaperOut(2), Overheat(8), LowVoltage(9), TooLong(-2), ServiceMissing(LOAD DAL ERR), Connect(99)`.
3. **Selección:** `PaxPrinterOptions.Mode = Real | Simulated` (+ `OutputDirectory`, `SimulatedStatus`). En la app la fija el interruptor de build (N03); default `Real`.

## Alternativas descartadas
Golden PNG dentro de `MotorDsl.Tests`: exige SkiaSharp/Maui en tests (R1 §6). Va como prueba de integración aparte (N06). Ancho fijo en código: se descarta hasta medirlo (D1).

## Tareas
- Sin dispositivo: ayuda de perfil, simulador, tests de cada estado, PNG volcado y recuperable con `adb pull` en el emulador.
- Con dispositivo: ticket de calibración (regla de 576 px) para fijar el ancho real y regenerar goldens.

## Criterios de aceptación
CA-02.1 el simulador produce un PNG del ancho del perfil. CA-02.2 cada estado simulado da el `PrintErrorType` y la causa esperados. CA-02.3 el ancho real queda medido y asentado en el expediente 0001.

## Evidencia
../Bitacoras/04-Agregar-PAX-A910S/Relevamiento/R1-libreria.md §3-4, §6 · ../Bitacoras/04-Agregar-PAX-A910S/Relevamiento/R3-pax-sdk.md §4, §8 · ../Bitacoras/04-Agregar-PAX-A910S/Mesa/informe-qa.md N2 · ../Bitacoras/04-Agregar-PAX-A910S/Mesa/informe-pos-pax.md
