# 05 — Capa MAUI: controles, renderers gráficos y diagnóstico

> **Propósito**: documentar `MotorDsl.Maui`, el paquete que aporta lo que necesita plataforma —
> los controles de UI, los tres renderers gráficos, el rasterizado y el reporte de diagnóstico.
> **Fuentes primarias**: `src/MotorDsl.Maui/` (`Controls/`, `Renderers/`, `Printing/`,
> `Diagnostics/`, `MotorDslMauiServiceCollectionExtensions.cs`),
> `docs/10_developer_guide/componentes-ux-maui.md`,
> `docs/10_developer_guide/render-pixelado-y-pdf.md`,
> `docs/10_developer_guide/diagnostics.md`.
>
> Los renderers **portables** (`text`, `escpos`) están en [03](03_renderizado-base.md); el
> servicio de impresión que consumen los controles, en [04](04_impresion-transports.md).

---

## 1. Qué registra `AddMotorDslMaui()`

Se encadena sobre el `MotorDslBuilder` que devolvió `AddMotorDslEngine()`:

| Registro | Efecto |
|---|---|
| `IBitmapRasterizer` → `SkiaSharpRasterizer` | Habilita las imágenes reales en `escpos` y `escpos-bitmap` |
| `QrCodeRasterizer` | QR dibujables para PDF y vista previa |
| `AddMotorDslPrinting()` | `IPrintErrorHandler` y `IThermalPrinterService` (con `TryAdd`) |
| `Replace(IPrintErrorHandler → MauiPrintErrorHandler)` | **Reemplaza** el handler por defecto |
| `TryAddSingleton<IDiagnosticsReportProvider, MauiDiagnosticsReportProvider>` | Diagnóstico |
| `AddRenderer<PdfRenderer>()` | target `pdf` |
| `AddRenderer<BitmapEscPosRenderer>()` | target `escpos-bitmap` |
| `AddRenderer<RasterPreviewRenderer>()` | target `raster-preview` |

Nótese el `Replace` frente al `TryAdd` del resto: el handler de MAUI **sustituye** al
`DefaultPrintErrorHandler` que acaba de registrar `AddMotorDslPrinting()`, mientras que los
demás respetan un registro previo del consumidor.

TFM `net10.0-android;net10.0-ios`. Dependencias externas: `SkiaSharp.Views.Maui.Controls`
3.119.2, `PdfSharpCore` 1.3.67 y `QRCoder` 1.8.0.

---

## 2. Los cinco controles

Todos son `ContentView` (salvo uno) con propiedades bindables, usables desde XAML con
`xmlns:muic="clr-namespace:MotorDsl.Maui.Controls;assembly=MotorDsl.Maui"`.

| Control | Propiedades | Para qué |
|---|---|---|
| `PrinterStatusBadge` | `Service` | Muestra el estado de conexión; se actualiza por el `INotifyPropertyChanged` del servicio |
| `PrinterPickerView` | `Service`, `FilterKind`, `AutoConnectIfSingle`; métodos `ScanAsync()` y `ConnectAsync(device)` | Descubre y elige impresora. `FilterKind` acota el `Kind` (`"bluetooth"`, `"network"`) |
| `PrinterPickerPage` | — (`ContentPage`) | El picker como página completa, para flujos modales |
| `MauiRasterPreview` | `ImageBytes`, `ZoomFactor` | Muestra la salida del target `raster-preview` |
| `MauiDocumentPreview` | `Document` (`LayoutedDocument`) | Vista previa a partir del documento maquetado, sin renderizar a bytes |
| `MauiDiagnosticsView` | `Report` (`DiagnosticsReport`) | Muestra el reporte de diagnóstico en pantalla |

```xml
<muic:PrinterStatusBadge x:Name="StatusBadge" />
<muic:PrinterPickerView  x:Name="DevicePicker" FilterKind="bluetooth" />
<muic:MauiRasterPreview  x:Name="RasterPreview" ZoomFactor="2" />
```

`Service` se asigna desde el code-behind con la instancia inyectada de
`IThermalPrinterService`. En los samples se hace en `OnAppearing`, no en el constructor.

---

## 3. `SkiaSharpRasterizer` — de imagen a bits ESC/POS

Implementa `IBitmapRasterizer`. Convierte una imagen (base64, con o sin prefijo
`data:image/…;base64,`) en el `RasterizedImage` que espera el comando `GS v 0`:

1. decodifica con **`SKImage.FromEncodedData` + `SKBitmap.FromImage`**;
2. escala al ancho pedido conservando la relación de aspecto;
3. calcula `widthBytes = ceil(ancho / 8)` — el comando empaqueta 8 píxeles por byte;
4. convierte cada píxel a gris con los pesos ITU (`R·299 + G·587 + B·114) / 1000`) y lo
   binariza con umbral 128, exigiendo además `alpha > 128`;
5. arma el arreglo de bits, con el bit más significativo a la izquierda.

**Por qué `SKImage.FromEncodedData` y no `SKBitmap.Decode(byte[])`**: en SkiaSharp 3.x el
segundo devuelve `null` incluso para PNG válidos —reproducido con un PNG 1×1 estándar—, lo que
en la versión 1.0.13 hacía que el ticket completo saliera en cero bytes. Es una corrección
documentada en el `CHANGELOG.md`, no una preferencia de estilo. **No revertir.**

`QrCodeRasterizer` es aparte: envuelve `QRCoder` y produce un `SKBitmap` (`Rasterize`) o su
tamaño (`Measure`), parametrizado por tamaño de módulo y nivel de corrección de errores (M por
defecto). Lo usan el `PdfRenderer` y el `RasterPreviewRenderer`, que necesitan **dibujar** el
QR en vez de delegarlo a la impresora.

---

## 4. `BitmapEscPosRenderer` — target `escpos-bitmap`

Compone sobre `EscPosRenderer` y difiere en el tratamiento de las imágenes: en vez de dejar
que la impresora interprete comandos gráficos, rasteriza todo y lo emite como `GS v 0`. Es el
target recomendado cuando la impresora no soporta gráficos NV
(ver `PrintStrategySelector`, [04 §6](04_impresion-transports.md)).

Toma el ancho de la capacidad `bitmap_max_width_px` del perfil (384 por defecto).

### Manejo de fallas de imagen por severidad

La versión 1.0.13 reemplazó una degradación silenciosa por tres desenlaces explícitos:

| Situación | Desenlace |
|---|---|
| La imagen **no se puede rasterizar** | **Error** preciso que incluye el `source` recortado y la causa: `Image rasterization failed (source='…'): <causa>`. Aborta el ticket |
| La imagen decodifica pero sale **toda en blanco** (típico de un placeholder transparente) | **Warning**: `Imagen rasterizada en blanco (posible placeholder transparente)`. El ticket **sí** se imprime |
| Falla el renderizado en general | `BitmapEscPos rendering failed: …` |

El principio detrás: los problemas de imagen siempre quedan visibles en `RenderResult.Errors`
o `Warnings`, nunca desaparecen sin dejar rastro.

---

## 5. `PdfRenderer` — target `pdf`

Genera un PDF con **PdfSharpCore**. Estado de renderizado en `PdfRenderState`: márgenes de 40
puntos, interlineado de 4, paginación automática, y variantes normal y negrita de la fuente.

`MotorDslFontResolver` resuelve las tipografías desde un recurso embebido del propio ensamblado
—`DroidSans` es la familia por defecto— para no depender de las fuentes del sistema, que en
Android no son las mismas que en iOS.

Los QR se dibujan como imagen usando `QrCodeRasterizer`. **EAN-13 no tiene soporte nativo en
PDF: cae a texto**, según consta en el roadmap del `README.md`.

> Nota histórica útil: el renderer de PDF fue **migrado a PdfSharpCore desde QuestPDF** porque
> `libQuestPdfSkia.so` no encontraba `libstdc++.so.6` en Android y la app crasheaba. El detalle
> está en `samples/notas-debug-android.md`.

---

## 6. `RasterPreviewRenderer` — target `raster-preview`

Dibuja el documento en un canvas SkiaSharp y devuelve la imagen en `byte[]`: es la vista previa
«como saldría impreso», pensada para `MauiRasterPreview`.

Ancho del canvas: la capacidad `bitmap_max_width_px` (384 por defecto). Detecta el tipo de cada
entrada con `IsQr` / `IsBitmap` / `IsBarcode` sobre el `DeviceMetadata`, calcula la posición
horizontal según la alineación (`AlignmentToX`), y convierte los bits de un `RasterizedImage` a
`SKBitmap` (`ConvertRasterToBitmap`) para poder dibujarlos. La tipografía sale del recurso
embebido (`LoadEmbeddedTypeface`).

Un bitmap que no se puede rasterizar genera una **advertencia** con el número de línea y la
vista previa continúa: `No se pudo rasterizar bitmap en línea N: …`.

Dos limitaciones declaradas en el roadmap: el escalado no usa *nearest-neighbor* real (haría
falta `SKCanvasView`) y EAN-13 cae a texto.

---

## 7. `MauiPrintErrorHandler`

Extiende `DefaultPrintErrorHandler` sin cambiar su política de reintentos —sigue reintentando
`Connection`, `Timeout` y `Unknown`— y agrega lo que la UI necesita:

| Miembro | Rol |
|---|---|
| `LogRetries` (bool, `true`) | Escribe cada intento en `Debug.WriteLine` con intento, tipo y mensaje |
| `RetryAttempted` (evento) | Se dispara en cada reintento, con el `PrintError` |
| `Succeeded` (evento) | Se dispara al imprimir bien, con la cantidad total de intentos |

Los dos eventos son el enganche para mostrar un *toast* o un indicador de progreso sin acoplar
la lógica de impresión a la vista.

---

## 8. Diagnóstico

`MauiDiagnosticsReportProvider` implementa `IDiagnosticsReportProvider` y arma un
`DiagnosticsReport` con:

| Sección | Contenido |
|---|---|
| `Libraries` | Versión e `InformationalVersion` de los ensamblados escaneados |
| `App` | Nombre, versión, build y package name |
| `Device` | Fabricante, modelo, plataforma, versión de SO, idiom |
| `Printer` | Snapshot de la impresora actual: kind, nombre, id, estado, perfil, ancho y capacidades |
| `Permissions` | Estado de los permisos `Bluetooth` y `LocationWhenInUse` |
| `Failures` | Las entradas recientes de `RecentFailures` del servicio |
| `Notes`, `CapturedAt` | Nota libre y timestamp |

**Privacidad**: `Build(notes, includePii)` recibe `includePii = false` por defecto y en ese modo
`DiagnosticsBuilder.MaskMac` enmascara la MAC del dispositivo —`AA:BB:CC**:**:**`— o, si el id
no es una MAC, deja los primeros cuatro caracteres y agrega `...`. El armado de estos snapshots
vive en `DiagnosticsBuilder`, dentro de `MotorDsl.Printing.Abstractions`, precisamente para que
sea **código puro y testeable** sin dependencia de MAUI.

Cuatro salidas: `ToJson`, `ToPlainText`, `ToDslJson(report, paperWidthChars)` —que convierte el
reporte en una plantilla DSL para imprimirlo como ticket, con QR de correlación— y el control
`MauiDiagnosticsView` para verlo en pantalla.

El patrón de UI recomendado —tres botones: ver, imprimir, compartir por email/WhatsApp/portapapeles
vía Share API— está en `docs/10_developer_guide/diagnostics.md`.
