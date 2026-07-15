---
doc_id: MotorDsl.Maui-component-catalog
doc_type: component-catalog
title: Catálogo de componentes — MotorDsl.Maui
version: 1.0.0
status: draft
origin: reverse-engineered
confidence: high
owner: equipo-motordsl
last_review: 2026-07-14
audience: [dev, arquitectura, qa, agentes-automaticos]
classification: uso-interno
source_ref: v1.0.13 @83677eb
traces: []
---

# Catálogo de componentes — MotorDsl.Maui

> Catálogo de los **6 controles** MAUI (Marco §7.2), los **3 renderers** y los **2 rasterizadores**
> de la pieza. Todos los controles se construyen por código (sin XAML) y exponen
> `BindableProperty`, de modo que pueden bindearse desde el XAML del consumer.
> Reconstruido por ingeniería inversa sobre **v1.0.13 @83677eb** (`status: draft`).

**Namespaces útiles para el XAML/code-behind del consumer:**

| Símbolo | Namespace C# | Ensamblado |
|---|---|---|
| Los 6 controles | `MotorDsl.Maui.Controls` | `MotorDsl.Maui` |
| `IThermalPrinterService`, `PrinterDevice`, `PrinterConnectionState`, `DiagnosticsReport` | `MotorDsl.Printing` | `MotorDsl.Printing.Abstractions` |
| `LayoutedDocument` | `MotorDsl.Core.Models` | `MotorDsl.Core` |

> Nota de procedencia: los `using` reales de los controles confirman estos namespaces
> (p. ej. `PrinterStatusBadge.cs#L4` → `using MotorDsl.Printing;`,
> `MauiDocumentPreview.cs#L1` → `using MotorDsl.Core.Models;`).

---

## 1. `PrinterStatusBadge`

**Tipo base:** `ContentView` · **Archivo:** `MotorDsl.Maui/Controls/PrinterStatusBadge.cs#L13-L138`

**Propósito.** Badge que muestra el estado de conexión de un `IThermalPrinterService` con color +
texto. Se auto-actualiza al cambiar `ConnectionState`, `CurrentDevice` o `LastError` del servicio
(se suscribe a `PropertyChanged`), marshalando el re-render al hilo de UI, y se desuscribe en
`Unloaded`.

### Bindables

| Prop | Tipo | Default | Descripción | Fuente |
|---|---|---|---|---|
| `Service` | `IThermalPrinterService?` | `null` | Servicio observado. Al asignarlo se (re)suscribe a su `PropertyChanged`. | `PrinterStatusBadge.cs#L15-L27` |

### Eventos / métodos públicos

Ninguno propio (solo la bindable `Service`). El ciclo de suscripción es interno:
`OnServiceChanged` → `RebindService` (`#L57-L74`); limpieza en `OnUnloaded` (`#L87-L94`).

### Estados (color + texto)

| `ConnectionState` | Color | Texto | Fuente |
|---|---|---|---|
| `Service == null` / `Disconnected` | gris `#9E9E9E` | `Desconectado` | `#L101-L111` |
| `Scanning` | azul `#1976D2` | `Buscando...` | `#L112-L115` |
| `Connecting` | naranja `#F57C00` | `Conectando...` | `#L116-L119` |
| `Connected` | verde `#388E3C` | `Conectado: {CurrentDevice.Name}` | `#L120-L123` |
| `Reconnecting` | naranja `#F57C00` | `Reconectando...` | `#L124-L127` |
| `Failed` | rojo `#D32F2F` | `Error: {LastError}` | `#L128-L131` |

> **H5 (threading):** el re-render pasa por `MainThread.BeginInvokeOnMainThread` porque el
> `PropertyChanged` del servicio puede llegar desde un hilo de fondo (`#L76-L85`).

### Ejemplo de uso

Code-behind (procedencia de la API: `PrinterStatusBadge.cs#L15-L27 @83677eb`):

```csharp
using MotorDsl.Maui.Controls;

var badge = new PrinterStatusBadge { Service = printerService };
myLayout.Children.Add(badge);
```

XAML (bindable `Service` resuelta por binding — no verificado como snippet literal del repo,
derivado de la definición de la bindable):

```xml
<ContentPage xmlns:ctl="clr-namespace:MotorDsl.Maui.Controls;assembly=MotorDsl.Maui">
    <ctl:PrinterStatusBadge Service="{Binding PrinterService}" />
</ContentPage>
```

---

## 2. `PrinterPickerView`

**Tipo base:** `ContentView` · **Archivo:** `MotorDsl.Maui/Controls/PrinterPickerView.cs#L10-L211`

**Propósito.** Descubre dispositivos vía `IThermalPrinterService.DiscoverDevicesAsync(FilterKind)`
(botón "Escanear") y conecta al seleccionar uno de la lista. Si descubre exactamente uno y
`AutoConnectIfSingle` está activo, conecta solo. Si la conexión falla **no** notifica por el
control: el contrato es que el servicio emite `ErrorOccurred` y el badge refleja el estado
(Hallazgo H6).

### Bindables

| Prop | Tipo | Default | Descripción | Fuente |
|---|---|---|---|---|
| `Service` | `IThermalPrinterService?` | `null` | Servicio usado para descubrir y conectar. Si es `null` al escanear, dispara `ScanError`. | `PrinterPickerView.cs#L12-L17`, `#L150-L155` |
| `FilterKind` | `string?` | `null` | Filtro por `Kind` de transporte (ej. `"bluetooth"`); `null` = todos los transports. | `PrinterPickerView.cs#L19-L24` |
| `AutoConnectIfSingle` | `bool` | `true` | Si el scan devuelve exactamente 1 dispositivo, conecta automáticamente. | `PrinterPickerView.cs#L26-L31`, `#L174-L179` |

### Eventos / métodos públicos

| Miembro | Firma | Semántica | Fuente |
|---|---|---|---|
| `DeviceSelected` | `event EventHandler<PrinterDevice>` | Se dispara tras una conexión **exitosa**. | `#L51`, `#L207-L208` |
| `ScanError` | `event EventHandler<Exception>` | `Service` sin setear, o excepción durante el descubrimiento. | `#L52`, `#L152-L153`, `#L191` |
| `ScanAsync()` | `Task` | Ejecuta el descubrimiento; gestiona spinner, lista vacía y auto-connect. | `#L147-L199` |
| `ConnectAsync(PrinterDevice device)` | `Task` | Conecta; en éxito dispara `DeviceSelected`. En fallo **no** notifica (H6). | `#L201-L210` |

### Estados de la vista

Escaneando (spinner visible, botón deshabilitado) · "Sin escanear" (inicial) · "Sin dispositivos
encontrados" (scan vacío) · lista de dispositivos (`CollectionView`, selección simple) ·
`Error: {msg}` en el label (`#L157-L198`).

### Ejemplo de uso

Code-behind (procedencia: `PrinterPickerView.cs#L51-L52`, `#L147`, `#L201 @83677eb`):

```csharp
using MotorDsl.Maui.Controls;

var picker = new PrinterPickerView
{
    Service = printerService,
    FilterKind = "bluetooth",     // opcional; null = todos los transports
    AutoConnectIfSingle = true
};
picker.DeviceSelected += (_, device) => Console.WriteLine($"Conectado a {device.Name}");
picker.ScanError += (_, ex) => Console.WriteLine($"Fallo de scan: {ex.Message}");
myLayout.Children.Add(picker);
```

---

## 3. `PrinterPickerPage`

**Tipo base:** `ContentPage` (modal) · **Archivo:** `MotorDsl.Maui/Controls/PrinterPickerPage.cs#L9-L47`

**Propósito.** Página **modal** que envuelve un `PrinterPickerView` + botón "Cancelar". Hace
`Navigation.PopModalAsync()` tanto al conectar (`DeviceSelected`) como al cancelar. Título fijo
`"Seleccionar impresora"`.

### Constructor y API

| Miembro | Firma | Fuente |
|---|---|---|
| Constructor | `PrinterPickerPage(IThermalPrinterService service, string? filterKind = null)` | `PrinterPickerPage.cs#L13` |

No expone bindables propias: recibe el servicio y el filtro por constructor y los pasa al
`PrinterPickerView` interno (`#L17-L21`). No hay evento propio; el cierre del modal es la señal.

### Ejemplo de uso

Code-behind (procedencia: `PrinterPickerPage.cs#L13 @83677eb`):

```csharp
using MotorDsl.Maui.Controls;

var page = new PrinterPickerPage(printerService, filterKind: "bluetooth");
await Navigation.PushModalAsync(page);
// El modal se cierra solo al conectar o al pulsar Cancelar.
```

---

## 4. `MauiRasterPreview`

**Tipo base:** `ContentView` · **Archivo:** `MotorDsl.Maui/Controls/MauiRasterPreview.cs#L9-L124`

**Propósito.** Muestra el PNG producido por `RasterPreviewRenderer` (`Target raster-preview`) con
zoom para simular la vista pixelada del papel térmico; scroll en ambos ejes; placeholder
`"(sin vista previa)"` cuando no hay bytes. Mide el tamaño nativo del PNG con `SKBitmap.Decode`
para fijar `WidthRequest = anchoNativo * ZoomFactor` (y análogo en alto).

### Bindables

| Prop | Tipo | Default | Descripción | Fuente |
|---|---|---|---|---|
| `ImageBytes` | `byte[]?` | `null` | Bytes PNG a mostrar (típicamente `RenderResult.Output` del renderer `raster-preview`). `null`/vacío → placeholder. | `MauiRasterPreview.cs#L11-L17`, `#L80-L88` |
| `ZoomFactor` | `double` | `2.0` | Factor de escala aplicado al ancho/alto nativos del PNG. | `MauiRasterPreview.cs#L19-L25`, `#L113-L117` |

### Eventos / métodos públicos

Ninguno propio. Cambiar cualquiera de las dos bindables dispara `UpdateImage` internamente
(`OnImageChanged` → `UpdateImage`, `#L72-L123`).

### Ejemplo de uso

Code-behind (procedencia: `MauiRasterPreview.cs#L11-L25 @83677eb`):

```csharp
using MotorDsl.Maui.Controls;

var preview = new MauiRasterPreview { ZoomFactor = 2.0 };
// pngBytes = (byte[])renderResult.Output del renderer "raster-preview"
preview.ImageBytes = pngBytes;
myLayout.Children.Add(preview);
```

---

## 5. `MauiDocumentPreview`

**Tipo base:** `ContentView` · **Archivo:** `MotorDsl.Maui/Controls/MauiDocumentPreview.cs#L9-L102`

**Propósito.** Preview **textual** de un `LayoutedDocument`: labels monoespaciadas (Consolas)
ordenadas por `LineNumber`/`ColumnNumber`; bold desde la metadata `bold`; QR/barcode se muestran
en azul itálica y bitmap en verde itálica. Origen: reutilizado de SampleApp (Sprint 08, TK-66,
docstring `#L6-L7`).

### Bindables

| Prop | Tipo | Default | Descripción | Fuente |
|---|---|---|---|---|
| `Document` | `LayoutedDocument?` | `null` | Documento ya *layouteado* (de `MotorDsl.Core`) a previsualizar como texto. | `MauiDocumentPreview.cs#L11-L23` |

### Eventos / métodos públicos

Ninguno propio. Asignar `Document` dispara `BuildPreview` internamente (`OnDocumentChanged`,
`#L37-L40`).

### Ejemplo de uso

Code-behind (procedencia: `MauiDocumentPreview.cs#L11-L23 @83677eb`):

```csharp
using MotorDsl.Maui.Controls;
using MotorDsl.Core.Models;

var preview = new MauiDocumentPreview();
preview.Document = layoutedDocument; // LayoutedDocument del pipeline (MotorDsl.Core)
myLayout.Children.Add(preview);
```

> Diferencia con `MauiRasterPreview`: este muestra el documento como **texto** aproximado (rápido,
> sin rasterizar); `MauiRasterPreview` muestra el **PNG** raster real del renderer `raster-preview`.

---

## 6. `MauiDiagnosticsView`

**Tipo base:** `ContentView` · **Archivo:** `MotorDsl.Maui/Controls/MauiDiagnosticsView.cs#L12-L200`

**Propósito.** Vista de detalle de un `DiagnosticsReport` en secciones con borde: Librería,
Aplicación, Dispositivo, Impresora (opcional), Permisos (opcional), Notas (opcional) + footer
`"Capturado: {fecha}"`. Pensada para mostrar la captura antes de compartirla o imprimirla
(docstring `#L5-L11`).

### Bindables

| Prop | Tipo | Default | Descripción | Fuente |
|---|---|---|---|---|
| `Report` | `DiagnosticsReport?` | `null` | Reporte a renderizar (producido por `MauiDiagnosticsReportProvider.Build`). `null` → vista vacía. | `MauiDiagnosticsView.cs#L14-L26`, `#L30-L35` |

### Eventos / métodos públicos

Ninguno propio. Asignar `Report` dispara `Render` internamente (`OnReportChanged`, `#L37-L40`).

### Ejemplo de uso

Code-behind (procedencia: `MauiDiagnosticsView.cs#L14-L26 @83677eb`; API del provider:
`MauiDiagnosticsReportProvider.cs#L18-L48`):

```csharp
using MotorDsl.Maui.Controls;
using MotorDsl.Printing;

// provider: IDiagnosticsReportProvider resuelto por DI (MauiDiagnosticsReportProvider)
DiagnosticsReport report = provider.Build(notes: "prueba de impresión", includePii: false);

var view = new MauiDiagnosticsView { Report = report };
myLayout.Children.Add(view);
```

---

## 7. Renderers (`IRenderer` por `Target`)

Los tres implementan `IRenderer` (`MotorDsl.Core/Contracts/IRenderer.cs`) y se registran en el
`RendererRegistry` del motor vía `AddMotorDslMaui` (`AddRenderer<T>`). La app elige por el string
`Target` del `DeviceProfile`.

| Renderer | `Target` | Qué produce | Dependencias | Archivo |
|---|---|---|---|---|
| `PdfRenderer` | `"pdf"` | PDF A4 multipágina: texto con word-wrap por medición real y page-break; QR como imagen (vía `QrCodeRasterizer`); bitmap base64 embebido (máx. 400 pt); barcode como texto fallback `[Código: data]`. | PdfSharpCore, SkiaSharp, QRCoder (indirecta). Fuente: `MotorDslFontResolver` (siempre `DroidSans` embebida). | `Renderers/PdfRenderer.cs#L48-L123` (resolver `#L15-L42`, estado `#L129-L302`) |
| `BitmapEscPosRenderer` | `"escpos-bitmap"` | Bytes ESC/POS: Init + nodos ordenados + CutFull. `is_bitmap`→`GS v 0`; `is_qr`→`GS ( k`; `is_barcode`→EAN13; texto con alineación/bold. Ancho de imagen acotado por capability `bitmap_max_width_px` (default 384). **Fail-loud** (aborta el ticket ante imagen irrecuperable). | `MotorDsl.Rendering` (`EscPosCommands`), `IBitmapRasterizer`. | `Renderers/BitmapEscPosRenderer.cs#L14-L177` |
| `RasterPreviewRenderer` | `"raster-preview"` | PNG que simula el raster térmico (texto mono 1-bit sin antialias, bitmaps, QR, barcode-fallback) para preview sin hardware. | SkiaSharp, `IBitmapRasterizer`, `QrCodeRasterizer`. | `Renderers/RasterPreviewRenderer.cs#L14-L252` |

Semántica de aborto/degradación por renderer: índice 05 §9. Constantes visuales (márgenes,
tamaños de QR, umbral 1-bit): índice 05 §10.

## 8. Rasterizadores auxiliares (no son `IRenderer`)

| Clase | Rol | Registro DI | Detalles clave | Archivo |
|---|---|---|---|---|
| `SkiaSharpRasterizer` | Implementa `IBitmapRasterizer`: base64 (`data:image/...;base64,` o crudo) → `RasterizedImage` 1-bit apto para `GS v 0`. | `AddSingleton<IBitmapRasterizer, SkiaSharpRasterizer>` | Escala manteniendo aspecto; umbral: luma (299/587/114) `< 128` **y** alpha `> 128` → bit encendido; `widthBytes = ceil(px/8)`. Decodifica con `SKImage.FromEncodedData` (workaround H2, no `SKBitmap.Decode`). | `Renderers/SkiaSharpRasterizer.cs#L13-L91` |
| `QrCodeRasterizer` | QR string → `SKBitmap` 1-bit sin antialias. Reutilizado por `PdfRenderer` y `RasterPreviewRenderer`. | `AddSingleton<QrCodeRasterizer>` (concreto, sin interfaz) | `Rasterize(data, moduleSize=4, ecc=M)` vía QRCoder `PngByteQRCode` + `SKBitmap.Decode`; `Measure` devuelve tamaño en px. | `Renderers/QrCodeRasterizer.cs#L11-L46` |

## 9. Utilidades de diagnóstico / errores (referencia)

No son controles, pero forman parte de la superficie pública de la pieza y alimentan
`MauiDiagnosticsView`:

| Clase | Interfaz | Rol | Archivo |
|---|---|---|---|
| `MauiPrintErrorHandler` | `IPrintErrorHandler` | Política retry/abort heredada de `DefaultPrintErrorHandler` + eventos `RetryAttempted`/`Succeeded` y flag `LogRetries` (default `true`). No bloquea el retry loop con diálogos. | `Printing/MauiPrintErrorHandler.cs#L12-L36` |
| `MauiDiagnosticsReportProvider` | `IDiagnosticsReportProvider` | `Build(notes?, includePii=false)` (snapshot librería/app/dispositivo/impresora/permisos), `ToJson`, `ToPlainText`, `ToDslJson(paperWidthChars=32)`. Permisos solo en Android. | `Diagnostics/MauiDiagnosticsReportProvider.cs#L18-L48` |

---

## 🤖 Para agentes

- **6 controles**, todos `MotorDsl.Maui.Controls`, sin XAML propio, construidos por código con
  `BindableProperty`. No inventes propiedades: la superficie bindeable completa es la de las
  tablas de arriba (`Service`, `FilterKind`, `AutoConnectIfSingle`, `ImageBytes`, `ZoomFactor`,
  `Document`, `Report`).
- **Namespace de los tipos de dominio** (`IThermalPrinterService`, `PrinterDevice`,
  `DiagnosticsReport`): `MotorDsl.Printing` (ensamblado `MotorDsl.Printing.Abstractions`), **no**
  `MotorDsl.Printing.Abstractions` como namespace. `LayoutedDocument` es `MotorDsl.Core.Models`.
- `PrinterPickerView.ConnectAsync` **no** propaga el fallo de conexión (H6): para reflejar error
  usa `PrinterStatusBadge` + el evento `ErrorOccurred` del servicio.
- Elige el control de preview según lo que tengas: `LayoutedDocument` → `MauiDocumentPreview`;
  PNG del renderer `raster-preview` → `MauiRasterPreview`.
- Toda afirmación de este catálogo es trazable a `MotorDsl.Maui/**` en **v1.0.13 @83677eb**; los
  `#Lx-Ly` valen para ese commit.
