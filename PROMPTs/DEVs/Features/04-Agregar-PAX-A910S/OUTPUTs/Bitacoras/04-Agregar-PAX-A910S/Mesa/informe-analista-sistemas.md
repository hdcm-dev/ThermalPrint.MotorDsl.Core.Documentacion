# Informe del analista de sistemas — Feature 04 (PAX A910S)

Base: informes R1 a R5 de `Relevamiento/`. Lo no medido se marca **Inferido**.

## 1. Propuesta de arquitectura

### 1.1 Contrato: no se toca
- El transporte recibe bytes: `WriteBytesAsync(byte[], PrinterProfile, ct)` (`src/MotorDsl.Printing.Abstractions/Contracts/IThermalPrinterTransport.cs:17`). El orquestador elige por `Kind` (R1 §4). Un transporte `Kind="pax"` entra sin cambiar `IThermalPrinterService`.
- La web no cambia: sólo viaja la URL del documento (R5 §13-14).

### 1.2 Vía bitmap: (a) con PNG, endurecida
- Se elige **(a)**: el `DeviceProfile` PAX usa target `raster-preview` (`RasterPreviewRenderer`, ancho por `bitmap_max_width_px`, R1 §6) y el transporte PAX decodifica el PNG y llama `print(Bitmap, IPinterListener)` (R3 §7).
- El transporte valida la firma PNG (`89 50 4E 47 0D 0A 1A 0A`) y rechaza lo demás con `PrintErrorType.Protocol` (R1 §21). Eso cubre la ambigüedad sin crear contrato nuevo.
- (b) se descarta ahora: rompe `IThermalPrinterService`, `FakePrinterService` e implementaciones externas (R1 §22). Queda como evolución si aparece un segundo transporte no ESC/POS que no acepte PNG.
- (c) se descarta: el renderer emite ESC/POS mixto (texto, `GS ( k`, barras), R1 §7-8.
- Alias opcional `raster-pax`: **Inferido** que no aporta; se evita mientras el mismo renderer alcance.

### 1.3 Un solo proyecto nuevo: `MotorDsl.Pax`
- Multi-target `net10.0;net10.0-android`:
  - `net10.0`: `PaxPrinterTransport`, abstracción propia `IPaxPrinter` (print PNG/bitmap, getStatus, setGray), mapeo de códigos a `PrintError`, `SimulatedPaxPrinter` (vuelca el PNG exacto a archivo y simula 1 ocupada, 2 sin papel, 8 sobrecalentamiento, 9 voltaje). Se prueba con `dotnet test` en el host sin workloads (R1 §11, §14).
  - `net10.0-android`: `NeptunePaxPrinter` sobre el binding (`<AndroidLibrary>` del jar NeptuneLite 4.15.00, `<AndroidNativeLibrary>` arm64-v8a/armeabi-v7a, `Metadata.xml` recortado a `NeptuneLiteUser`, `IDAL`, `IPrinter`, `IPinterListener`, excepciones; ProGuard `-keep com.pax.**`; permiso `com.pax.permission.PRINTER`) (R3 §2-6, §19).
- Binding dentro del mismo proyecto, no separado: un paquete más (8 → 9 en `cd-nuget.yml:183-186`) en vez de 10 (R1 §18). Separarlo sólo si otro PAX exige otro SDK.
- Escalabilidad a otros PAX: la variabilidad va en datos (`DeviceProfile` por modelo: ancho, gray) y en `IPaxPrinter`; el mapeo de errores se hace por tabla, separando `getStatus/start/onError` de `EPrintDevException` porque las numeraciones difieren (R3 §14).
- Registro: `AddPaxPrinterTransport(options)` con `AddSingleton`, igual que Bluetooth y Network (R1 §5); la opción elige `Neptune` o `Simulated`.
- Degradación: si `getDal` lanza o falta `com.pax.ipp.neptune` (**Inferido**, R3 §16), el transporte devuelve `Connection` con mensaje claro; nunca excepción no controlada. En x86 (sin `.so`, R3 §3, §20) `IsAvailable=false`.

### 1.4 App
- Configuración por trío: `transporte` (bluetooth|pax|simulado) y nombre del `DeviceProfile`; reemplaza el perfil fijo `PrintCoordinator.cs:90-93` y el `kind:"bluetooth"` fijo `PrinterService.cs:97` (R2 §7-8).
- `IPrinterService` generalizado: los chequeos Bluetooth (`PrinterService.cs:68-97`) pasan a la estrategia Bluetooth; la PAX no busca ni elige impresora (interna); el overlay saltea pasos.
- Permisos Bluetooth faltantes en manifiestos (R2 §13) en la misma rama.

## 2. Sin dispositivo / con dispositivo
Sin dispositivo: proyecto `MotorDsl.Pax`, binding (compila en devcontainer o macOS de CI), simulador, tests, `cd-nuget.yml` + CHANGELOG `[Unreleased]`, app configurable, conocimiento PayDroid, prueba de no-caída en emulador Pay-Android.
Con dispositivo: ancho real px y dpi (R3 §12; 384 es **Inferido**), paquete/versión NeptuneService, WebView real (riesgo fix 08, R4 §3-4), vendor USB, impresión real, firma PAX en Release.

## 3. Riesgos
- Ancho desconocido: el perfil queda parametrizable; se mide con una regla impresa (el sobrante se recorta, R3 §12).
- WebView < 94 en el A910S invalida el inspector web aunque imprima (R4 §3).
- Binding: reflexión de `DALProxy` + R8 puede romper en Release sin ProGuard (R3 §5).
- `pack-platform` corre en macos-15; el runner `<equipo-1>-dev` no verificado con workload android (R1 §16, §26).

## 4. Reglas de entrega
Librería: rama propia + PR. App: rama desde `main` (único remoto, R2 §1) + PR. Web: sin cambios; si se ajusta el texto de `ImpresoraTunnel.razor:109`, desde `origin/Homologacion` (c89f8588), sólo commit y push (R5 §5-7). Infraestructura (USB a `windows-<equipo-1>`, regla udev PAX en `<equipo-2>`) sólo con autorización del PO (R4 §12-16).
