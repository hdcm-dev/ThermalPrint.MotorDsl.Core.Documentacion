# 05 — MAUI: controles, renderers gráficos y diagnóstico

> **Propósito**: qué aporta el paquete `MotorDsl.Maui` sobre el núcleo — controles bindeables,
> los tres renderers que necesitan gráficos, y el reporte de diagnóstico.
> **Fuentes primarias**: `src/MotorDsl.Maui/`,
> `docs/10_developer_guide/componentes-ux-maui.md`, `…/render-pixelado-y-pdf.md`, `…/diagnostics.md`.

---

## 1. Qué registra `AddMotorDslMaui()`

Fuente: [`src/MotorDsl.Maui/MotorDslMauiServiceCollectionExtensions.cs`](../../../PrintThermal_Motor_Maui/src/MotorDsl.Maui/MotorDslMauiServiceCollectionExtensions.cs).

| Servicio | Implementación | Modo |
|---|---|---|
| `IBitmapRasterizer` | `SkiaSharpRasterizer` | `AddSingleton` |
| `QrCodeRasterizer` | (clase concreta) | `AddSingleton` |
| Capa de impresión | `AddMotorDslPrinting()` | `TryAdd` |
| `IPrintErrorHandler` | `MauiPrintErrorHandler` | **`Replace`** — pisa el `DefaultPrintErrorHandler` |
| `IDiagnosticsReportProvider` | `MauiDiagnosticsReportProvider` | `TryAddSingleton` |
| Renderers | `PdfRenderer`, `BitmapEscPosRenderer`, `RasterPreviewRenderer` | `AddRenderer<T>()` |

Se encadena sobre el `MotorDslBuilder`, así que el orden es
`AddMotorDslEngine() … .AddMotorDslMaui()`. El `Replace` del error handler es intencional: es la
única forma de que gane sobre el `TryAddSingleton` que hizo `AddMotorDslPrinting()`.

Dependencias externas que entran con este paquete: **SkiaSharp.Views.Maui.Controls 3.119.2**,
**PdfSharpCore 1.3.67** y **QRCoder 1.8.0**. Además embebe la fuente `DroidSans-Regular.ttf` como
`EmbeddedResource` para el PDF.

---

## 2. Controles

Todos en `src/MotorDsl.Maui/Controls/`, namespace `MotorDsl.Maui.Controls`. Uso en XAML:

```xml
xmlns:muic="clr-namespace:MotorDsl.Maui.Controls;assembly=MotorDsl.Maui"
```

| Control | Base | BindableProperties | Eventos |
|---|---|---|---|
| `PrinterStatusBadge` | `ContentView` | `Service` | — |
| `PrinterPickerView` | `ContentView` | `Service`, `FilterKind`, `AutoConnectIfSingle` | `DeviceSelected`, `ScanError` |
| `PrinterPickerPage` | `ContentPage` | — (envuelve al picker) | — |
| `MauiRasterPreview` | `ContentView` | `ImageBytes`, `ZoomFactor` | — |
| `MauiDocumentPreview` | `ContentView` | `Document` | — |
| `MauiDiagnosticsView` | `ContentView` | `Report` | — |

`PrinterPickerView` expone además `ScanAsync()` y `ConnectAsync(PrinterDevice)` como API
imperativa. `FilterKind` acota el descubrimiento a un `Kind` (`"bluetooth"`, `"network"`), y
`AutoConnectIfSingle` conecta sin intervención cuando el escaneo devuelve un solo dispositivo.

Los controles se bindean a `IThermalPrinterService`, que implementa `INotifyPropertyChanged`: el
badge y el picker reflejan `ConnectionState`, `IsConnected` y `LastError` sin código de sincronía
en la app.

---

## 3. Renderers gráficos

### `BitmapEscPosRenderer` — `Target = "escpos-bitmap"`

Fuente: [`Renderers/BitmapEscPosRenderer.cs`](../../../PrintThermal_Motor_Maui/src/MotorDsl.Maui/Renderers/BitmapEscPosRenderer.cs).

Es `EscPosRenderer` **con rasterizador obligatorio** (lo recibe por constructor, no opcional).
Ancho efectivo de cada imagen: `min(bitmap_width * 8, bitmap_max_width_px)`, con 384 px de default.

Lo que lo distingue del renderer base es el manejo de fallas por severidad, introducido en 1.0.13:

| Situación | Resultado |
|---|---|
| La imagen **no se puede rasterizar** | `Error` con el mensaje del rasterizador y el `source` recortado a 40 caracteres; `Output` vacío; **aborta el ticket** |
| La imagen rasteriza **toda en blanco** | `Warning` («posible placeholder transparente»); el ticket se imprime igual |

El recorte del `source` en los mensajes evita volcar un base64 entero al log. El renderer base, en
cambio, degrada en silencio a un `[BITMAP]` textual (ver [`03_renderizado-base.md`](03_renderizado-base.md)).

### `PdfRenderer` — `Target = "pdf"`

Fuente: [`Renderers/PdfRenderer.cs`](../../../PrintThermal_Motor_Maui/src/MotorDsl.Maui/Renderers/PdfRenderer.cs) (304 líneas).

Usa PdfSharpCore con un `MotorDslFontResolver` propio que sirve la `DroidSans-Regular.ttf` embebida
—PdfSharpCore no tiene resolución de fuentes por defecto en móvil—. Un `PdfPageWriter` interno
maneja `EnsureSpace` (salto de página automático), `RenderText` con alineación y negrita,
`RenderQr`, `RenderBitmap` y `RenderBarcodeText`.

Límite conocido: el **EAN-13 cae a texto** en PDF; no se dibuja el simbolismo.

### `RasterPreviewRenderer` — `Target = "raster-preview"`

Fuente: [`Renderers/RasterPreviewRenderer.cs`](../../../PrintThermal_Motor_Maui/src/MotorDsl.Maui/Renderers/RasterPreviewRenderer.cs) (252 líneas).

Produce un **PNG** que simula el ticket impreso, para mostrar en pantalla antes de gastar papel.
Deriva el tamaño de fuente del ancho en caracteres del perfil asumiendo monoespaciado
(`fontSize = (canvasWidth / chars) / 0.6`, con piso de 10) y `lineHeight = fontSize * 1.4`.

Trabaja en **dos pases**: el primero pre-calcula el alto total y pre-rasteriza bitmaps y QR en un
diccionario; el segundo dibuja reutilizando lo ya generado, para no rasterizar dos veces la misma
imagen.

### Rasterizadores

| Clase | Qué hace |
|---|---|
| `SkiaSharpRasterizer` (`IBitmapRasterizer`) | base64 → 1 bit por píxel para `GS v 0` |
| `QrCodeRasterizer` | datos → `SKBitmap` del QR vía QRCoder; `Measure()` para el pase de medición |

`SkiaSharpRasterizer` escala manteniendo relación de aspecto, calcula
`widthBytes = ceil(ancho / 8)` y binariza con luma ITU-R 601 (`0.299R + 0.587G + 0.114B`) contra
umbral 128, exigiendo además `alpha > 128` — los píxeles transparentes cuentan como blanco.

**Detalle histórico que conviene no revertir**: la decodificación usa
`SKImage.FromEncodedData` + `SKBitmap.FromImage`, no `SKBitmap.Decode(byte[])`. En SkiaSharp 3.x
ese último devuelve `null` incluso para PNGs válidos, lo que hacía que el ticket completo saliera
en 0 bytes ([`CHANGELOG.md`](../../../PrintThermal_Motor_Maui/CHANGELOG.md) § 1.0.13). El base64 se
limpia de saltos de línea y espacios antes de decodificar, y un base64 inválido lanza
`InvalidOperationException` con mensaje propio.

---

## 4. `MauiPrintErrorHandler`

Fuente: [`Printing/MauiPrintErrorHandler.cs`](../../../PrintThermal_Motor_Maui/src/MotorDsl.Maui/Printing/MauiPrintErrorHandler.cs).

Hereda de `DefaultPrintErrorHandler` y sobrescribe los tres métodos virtuales, agregando logging
(`LogRetries`, activable). La política de reintento la mantiene el padre: no reintenta ante
`PrintErrorType.Hardware`.

---

## 5. Diagnóstico

Fuente: [`Diagnostics/MauiDiagnosticsReportProvider.cs`](../../../PrintThermal_Motor_Maui/src/MotorDsl.Maui/Diagnostics/MauiDiagnosticsReportProvider.cs) (406 líneas), contrato en
`MotorDsl.Printing.Abstractions/Contracts/IDiagnosticsReportProvider.cs`.

```csharp
DiagnosticsReport Build(string? notes = null, bool includePii = false);
string ToJson(DiagnosticsReport report);
string ToPlainText(DiagnosticsReport report);
string ToDslJson(DiagnosticsReport report, int paperWidthChars = 32);
```

`ToDslJson` cierra el círculo: el reporte de diagnóstico se convierte en un documento DSL y se
**imprime como ticket térmico** por el mismo motor, con un QR de correlación.

Un `DiagnosticsReport` agrupa `LibraryInfo[]`, `AppInfoSnapshot`, `DeviceInfoSnapshot`,
`PrinterInfoSnapshot?`, `PermissionsSnapshot?`, `CapturedAt`, `Notes?` y `Failures?`.

### Privacidad

`includePii = false` (el default) enmascara identificadores mediante
`DiagnosticsBuilder.MaskMac`: una MAC válida queda como `AA:BB:CC**:**:**`; cualquier otro id se
recorta a sus primeros 4 caracteres más `...`. El enmascarado se aplica también a los
`PrintFailureEntry` del historial. Los helpers de `DiagnosticsBuilder` están en
`MotorDsl.Printing.Abstractions` —no en MAUI— y se cubren con tests (`DiagnosticsBuilderTests`).

Patrón de UI de los tres botones (ver en pantalla / imprimir / compartir por Share API):
`docs/10_developer_guide/diagnostics.md`.

---

## 6. Notas de plataforma

- El paquete targetea `net10.0-android` (mínimo API 25) y `net10.0-ios` (mínimo 15.0).
- Lleva `AndroidLdFlags = -Wl,-z,max-page-size=16384` para páginas de 16 KB.
- Compilar este paquete requiere los workloads `maui-android` y `ios`; en la práctica solo se
  empaqueta en `macos-15` (ver [`08_build-devops.md`](08_build-devops.md)).
- Tiene **una sola** directiva de compilación condicional en todo el proyecto — es lo que hace que
  el motor funcione en iOS y que el problema de iOS fuera solo el transport (ADR-0005).
