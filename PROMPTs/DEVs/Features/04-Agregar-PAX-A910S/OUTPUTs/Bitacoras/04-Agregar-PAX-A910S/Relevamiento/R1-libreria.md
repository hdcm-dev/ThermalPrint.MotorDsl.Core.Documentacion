# R1 — Relevamiento de la librería MotorDsl (Feature 04, PAX A910S)

> Fase de sólo lectura. Rutas relativas a `/Libs/NugetOrg/PrintThermal_Motor_Maui` salvo indicación.
> Commit relevado: `0f8413d` (`git log --oneline -1`). Lo marcado **Inferido** no está verificado.

## 1. Contrato de transporte

- `IThermalPrinterTransport` (`src/MotorDsl.Printing.Abstractions/Contracts/IThermalPrinterTransport.cs:5-29`):
  `Kind` (:7), `IsConnected`, `CurrentDevice`, `Capabilities => null` por defecto (:13),
  `DiscoverAsync` (:14), `ConnectAsync(string deviceId)` (:15), `DisconnectAsync` (:16),
  **`WriteBytesAsync(byte[] data, PrinterProfile profile, ct)`** (:17) — único canal de contenido, sólo bytes.
- Ya existe el patrón de **métodos con implementación por defecto** (default interface methods):
  `ProvisionLogoAsync` / `IsLogoProvisionedAsync` / `ClearLogoAsync` (:21-28). Es el precedente de la alternativa (b).
- `IThermalPrinterService` (`.../Contracts/IThermalPrinterService.cs:6-37`): la app imprime con
  `SendBytesAsync(byte[] data, PrinterProfile? profile, PrintRetryOptions? retry, ct)` (:30).

## 2. Orquestador y registro DI

- `ThermalPrinterService` (`src/MotorDsl.Printing.Abstractions/Services/ThermalPrinterService.cs`):
  recibe `IEnumerable<IThermalPrinterTransport>` y falla si no hay ninguno (:83-91); `DiscoverDevicesAsync`
  filtra por `Kind` (:103); `ConnectAsync` rutea al transporte cuyo `Kind` coincide con `PrinterDevice.Kind` (:135-136);
  `SendBytesAsync` usa `PrinterProfile.Thermal58mm` por defecto (:203) y llama `_activeTransport.WriteBytesAsync` (:213)
  con reintentos y clasificación de errores vía `PrintError.FromException` (:219).
- Registro: `AddMotorDslPrinting()` = `TryAddSingleton` de `IPrintErrorHandler` y `IThermalPrinterService`
  (`.../MotorDslPrintingServiceCollectionExtensions.cs:10-15`).
- Transportes: `AddBluetoothPrinterTransport()` → `AddSingleton<IThermalPrinterTransport, BluetoothPrinterTransport>`
  (`src/MotorDsl.Bluetooth/MotorDslBluetoothServiceCollectionExtensions.cs:8-12`);
  `AddNetworkPrinterTransport(configure)` (`src/MotorDsl.Network/MotorDslNetworkServiceCollectionExtensions.cs:16-26`),
  cuyo comentario documenta que se usa `AddSingleton` (no `TryAdd`) para que coexistan varios transportes (:11-14).
  Un `AddPaxPrinterTransport()` seguiría el mismo patrón sin tocar el orquestador.
- `AddMotorDslMaui()` registra `PdfRenderer`, `BitmapEscPosRenderer`, `RasterPreviewRenderer`, el rasterizador Skia
  y `AddMotorDslPrinting` (`src/MotorDsl.Maui/MotorDslMauiServiceCollectionExtensions.cs:22-33`).

## 3. Renderers relevantes

- `RasterPreviewRenderer` (`src/MotorDsl.Maui/Renderers/RasterPreviewRenderer.cs`): `Target="raster-preview"` (:19);
  ancho del lienzo = capacidad `bitmap_max_width_px` del `DeviceProfile`, por defecto 384 (:32); dibuja en
  `SKBitmap` (:88) y devuelve **PNG** (`Encode(Png,100)`, :144-146); libera los bitmaps pre-rasterizados (:148-150).
- `BitmapEscPosRenderer` (`src/MotorDsl.Maui/Renderers/BitmapEscPosRenderer.cs`): `Target="escpos-bitmap"` (:19).
  **Sólo las imágenes** van como `GS v 0` (`0x1D 0x76 0x30 0x00`, :146; uso por `is_bitmap`, :47-52).
  El **texto se emite como ESC/POS de texto** (`Encoding.ASCII.GetBytes`, :108, con alineación/negrita :103-110),
  el QR como `GS ( k` (:90, :161) y el código de barras con su comando (:98). Esto contradice la premisa de la
  alternativa (c) del plan (ver §8).
- `bitmap_max_width_px` también lo lee `EscPosRenderer` (`src/MotorDsl.Rendering/EscPosRenderer.cs:207`).

## 4. Perfiles

- Hay **dos perfiles distintos**:
  - `DeviceProfile` (render): `Name`, `Width` (caracteres), `RenderTarget`, capacidades por diccionario
    (`src/MotorDsl.Core/Models/DeviceProfile.cs:3-31`). No hay presets estáticos en la librería: se cargan con
    `MotorDslBuilder.AddProfiles(...)` sobre `InMemoryDeviceProfileProvider`
    (`src/MotorDsl.Extensions/MotorDslBuilder.cs:28-34`; `src/MotorDsl.Core/Providers/InMemoryDeviceProfileProvider.cs:11-23`).
    `grep -rn "new DeviceProfile(" src` fuera de Tests: sin resultados.
  - `PrinterProfile` (transporte, demoras/timeouts): presets `Thermal58mm` y `Real58HB6`
    (`src/MotorDsl.Printing.Abstractions/Models/PrinterProfile.cs:41-62`); `WriteTimeoutMs` (:22),
    `ConfirmPrintTimeoutMs` (:39). Las demoras son de Bluetooth/ESC-POS; para PAX la mayoría no aplica (**Inferido**).
- Un "perfil PAX" implica probablemente ambas cosas: un `DeviceProfile` con `RenderTarget="raster-preview"` y
  `bitmap_max_width_px` = ancho real del cabezal (**dato a relevar del SDK/equipo; no verificado aquí**) y,
  opcionalmente, un preset `PrinterProfile.PaxA910S`.

## 5. Catálogo de errores

- `PrintErrorType { Connection, Timeout, Hardware, Protocol, Unknown }` (`src/MotorDsl.Core/Models/PrintError.cs:7-13`).
- `PrintError.FromException` mapea `PrinterHardwareException→Hardware`, `PrintNotConfirmedException→Protocol`,
  `IOException/SocketException→Connection`, `TimeoutException/TaskCanceledException→Timeout`, resto `Unknown`
  (`PrintError.cs` `FromException`, ~:38-50). Excepciones: `src/MotorDsl.Core/Models/PrinterHardwareException.cs:8`,
  `PrintNotConfirmedException.cs:25`.
- Para PAX: los estados de `getStatus()` (sin papel, sobrecalentamiento, ocupado) encajan en lanzar
  `PrinterHardwareException` (→ `Hardware`); "NeptuneService ausente" encaja en `Connection` o `Unknown`
  (**Inferido**; no hay hoy un código de error más fino que el enum).

## 6. Tests

- `src/MotorDsl.Tests/MotorDsl.Tests.csproj`: `net10.0` (:4), xUnit 2.9.3, runner 3.1.4, Test.Sdk 17.14.1,
  coverlet 6.0.4 (:36-40). Referencia Core, Extensions, Parser, Rendering, Printing.Abstractions, Network (:16-21);
  **no referencia MotorDsl.Maui ni MotorDsl.Bluetooth**; enlaza como fuente
  `BluetoothPrinterTransport.Chunking.cs` y `.Capabilities.cs` (:31-32).
- Fakes: `FakeRasterizer`, `FakeTransport` (`Kind="fake"`, `ThrowOnWrite` → `IOException`), `FakePrinterService`
  (`src/MotorDsl.Tests/TestFakes.cs:9,16-46,48`).
- Corrida en este host (copia en scratchpad para no ensuciar el árbol, con `nupkg/` vacío creado porque
  `NuGet.config:5` declara la fuente local `./nupkg`):
  `dotnet test src/MotorDsl.Tests/MotorDsl.Tests.csproj` →
  `Correctas! - Con error: 0, Superado: 315, Omitido: 0, Total: 315` (12,4 s reales).
  El ia-db decía 292 métodos por conteo estático (`ia-db/README.md`, fila Tests); 315 son casos ejecutados (los
  `[Theory]` expanden), no contradice.
- Consecuencia: la lógica PAX que deba testearse en `net10.0` (decodificación de entrada, mapeo de estados a
  errores, impresora simulada que vuelca PNG) tiene que vivir en código sin dependencias Android, o enlazarse como
  fuente igual que el chunking de Bluetooth. `RasterPreviewRenderer` (en MotorDsl.Maui, TFM android/ios) **no** es
  testeable en este host hoy.

## 7. Build, TFMs y CI

- TFMs: `net10.0` en Core, Parser, Rendering, Extensions, Printing.Abstractions, Network, Tests;
  `net10.0-android;net10.0-ios` en Bluetooth (`MotorDsl.Bluetooth.csproj:4`, Android min 24.0 :11) y Maui
  (`MotorDsl.Maui.csproj:4`, Android min 25.0 :12). Dependencias de Maui: SkiaSharp.Views.Maui.Controls 3.119.2,
  PdfSharpCore 1.3.67, QRCoder 1.8.0 (:49-51).
- **No hay `Directory.Build.props/targets`** (`find . -maxdepth 3 -name "Directory.*"`: vacío).
- Host: `dotnet --info` → SDK 10.0.403, host 10.0.14, Debian 12 x64; `dotnet workload list` → **ninguna workload**.
  No se pueden compilar Bluetooth/Maui/un futuro paquete PAX Android aquí sin instalar `android`/`maui-android`
  (no se instaló, por regla). Existe `scripts/local-devcontainer/` que compila los samples a APK en un contenedor
  efímero con `maui-android` (`CHANGELOG.md:15-29`) — vía candidata para compilar sin tocar el host.
- `.github/workflows/cd-nuget.yml`:
  - Disparo: tags `v*`, push a `main`, `workflow_dispatch` con `version` (:12-20). `DOTNET_VERSION: 10.0.102` (:23).
  - Job `version` en `[self-hosted, <equipo-1>-dev]` (:31): tag→versión, dispatch→input, si no `0.0.0-preview.N` (:38-45).
  - `pack-managed` en `[self-hosted, <equipo-1>-dev]` (:53): restore/build/pack de
    `Core Parser Rendering Extensions Printing.Abstractions Network` (:70,:76,:87) y `dotnet test` (:80-83).
  - `pack-platform` en `macos-15` (:108): `dotnet workload install ios android maui-android` (:124), build/pack de
    `Bluetooth Maui` (:128,:134,:140). Motivo: el workload `ios` no existe en Linux (:5-10).
  - `publish` en self-hosted (:161): exige **exactamente 8** `.nupkg` (:183-186) y empuja en el orden
    `Printing.Abstractions Core Parser Rendering Extensions Network Bluetooth Maui` (:193) con `--skip-duplicate`.
    Observación: el comentario dice "Printing.Abstractions primero" (:192), pero Printing.Abstractions depende de
    Core (`MotorDsl.Printing.Abstractions.csproj:23`); nuget.org no valida dependencias al subir, así que no rompe
    (**Inferido**).
  - Un 9.º paquete (p. ej. `MotorDsl.Pax`, sólo `net10.0-android`) obliga a: agregarlo a un job de pack (macOS, o
    Linux si el runner tuviera `android` — **no verificado** en `<equipo-1>-dev`), subir el conteo a 9 (:184-185) y
    agregarlo a la lista de push (:193). Si el binding de NeptuneLite fuera un proyecto aparte empaquetado, serían 10.
- `CHANGELOG.md`: Keep a Changelog + SemVer, versión inyectada por `-p:PackageVersion` y no en los `.csproj` (:5-9);
  `[Unreleased]` (:11) sólo con `scripts/local-devcontainer/`; última versión `1.0.17` (2026-08-27) (:31).
  La entrada PAX iría bajo `[Unreleased]`.

## 8. Cambios de contrato por alternativa de vía bitmap (plan §3.3)

| Alt. | Qué viaja por `WriteBytesAsync` | Cambio de contrato | Impacto |
|---|---|---|---|
| **(a)** PNG de `RasterPreviewRenderer` | bytes PNG | **Ninguno** en `IThermalPrinterTransport` ni `IThermalPrinterService`. | El transporte PAX detecta la firma PNG (`89 50 4E 47`), decodifica a `Android.Graphics.Bitmap` y llama `print(Bitmap)`. La app debe usar un `DeviceProfile` con `RenderTarget="raster-preview"` y `bitmap_max_width_px` = ancho PAX. El contrato queda semánticamente ambiguo ("bytes" puede ser ESC/POS o PNG): conviene que el transporte rechace con error claro (`Protocol`) lo que no sea PNG. `PrinterProfile` (demoras) se ignora. Documento entero = un solo bitmap alto (**Inferido**: límite de memoria/alto a verificar con el SDK). |
| **(b)** `WriteBitmapAsync` opcional | — (método nuevo) | Agregar a `IThermalPrinterTransport` un método con default (p. ej. `Task WriteBitmapAsync(byte[] png, PrinterProfile, ct) => throw new NotSupportedException()` o un `bool SupportsBitmap => false`), siguiendo el patrón de :21-28. Para que la app lo use, también **`IThermalPrinterService`** necesita un `SendBitmapAsync` (o equivalente) y `ThermalPrinterService` duplicar el bucle de reintento de `SendBytesAsync`. `FakePrinterService` (`TestFakes.cs:48`) y cualquier implementación externa de `IThermalPrinterService` tendrían que implementarlo (la interfaz del servicio no tiene defaults hoy). | Contrato explícito y autodescriptivo; cambio aditivo en minor. Más superficie que (a). |
| **(c)** Decodificar `GS v 0` de `BitmapEscPosRenderer` | ESC/POS | Ninguno en la interfaz. | **No es viable tal como está planteada**: `BitmapEscPosRenderer` sólo emite `GS v 0` para imágenes; el texto sale como ESC/POS de texto ASCII (:108), QR como `GS ( k` (:90) y barras como comando (:98). El transporte tendría que ser un intérprete ESC/POS completo (o el renderer cambiar a "todo raster"), lo que equivale a otro renderer. |

**Inferido**: (a) es la de menor cambio y no toca contratos públicos; (b) es la evolución limpia si en el futuro hay
más transportes no-ESC/POS. Una variante de (a) sin ambigüedad sería un renderer/target dedicado
(p. ej. `raster-pax`) que reuse `RasterPreviewRenderer`; es decisión de la mesa.

## 9. Pendientes para otras líneas
- Ancho de cabezal del A910S y API real de NeptuneLite (`print(Bitmap, listener)`, `getStatus`): relevar del material
  PAX (R de SDK), no de esta librería.
- Estado de workloads en el runner `<equipo-1>-dev`: no verificado.
