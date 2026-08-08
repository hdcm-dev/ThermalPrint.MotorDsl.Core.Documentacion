# 05 — MAUI: controles y renderers

> **Propósito**: lo que aporta el paquete `MotorDsl.Maui` — controles de UI listos para usar,
> tres renderers adicionales, los rasterizadores y el proveedor de diagnóstico.
> **Fuentes primarias**: `src/MotorDsl.Maui/` (`Controls/`, `Renderers/`, `Diagnostics/`,
> `Printing/`, `MotorDslMauiServiceCollectionExtensions.cs`),
> `docs/10_developer_guide/{componentes-ux-maui,render-pixelado-y-pdf,guia-integracion-maui,diagnostics}.md`.
> El contrato `IRenderer` y los renderers base están en [03_renderizado-base](03_renderizado-base.md);
> el servicio de impresión en [04_impresion-transports](04_impresion-transports.md).

---

## 1. Registro: qué hace `AddMotorDslMaui()`

```csharp
builder.Services.AddMotorDslEngine()
    .AddTemplates(...).AddProfiles(...)
    .AddMotorDslMaui();
```

En una sola llamada (`MotorDslMauiServiceCollectionExtensions.cs`):

| Acción | Servicio |
|---|---|
| `AddSingleton` | `IBitmapRasterizer` → `SkiaSharpRasterizer` |
| `AddSingleton` | `QrCodeRasterizer` |
| `AddMotorDslPrinting()` | `IPrintErrorHandler` (default) e `IThermalPrinterService` |
| `Replace` | `IPrintErrorHandler` → `MauiPrintErrorHandler` (reemplaza al default) |
| `TryAddSingleton` | `IDiagnosticsReportProvider` → `MauiDiagnosticsReportProvider` |
| `AddRenderer<T>` | `PdfRenderer`, `BitmapEscPosRenderer`, `RasterPreviewRenderer` |

> El uso de `TryAddSingleton` para el provider de diagnóstico es intencional: si la app registra
> el suyo **antes**, el suyo prevalece. En cambio el error handler se registra con `Replace`, así
> que la versión MAUI **siempre** gana sobre el default.

TFMs del paquete: `net10.0-android;net10.0-ios`. Dependencias externas:
`SkiaSharp.Views.Maui.Controls` 3.119.2, `PdfSharpCore` 1.3.67, `QRCoder` 1.8.0.

---

## 2. Controles (`MotorDsl.Maui.Controls`)

| Control | Tipo base | Propiedades enlazables | Eventos |
|---|---|---|---|
| `PrinterStatusBadge` | `ContentView` | `Service` | — |
| `PrinterPickerView` | `ContentView` | `Service`, `FilterKind`, `AutoConnectIfSingle` (default `true`) | `DeviceSelected`, `ScanError` |
| `PrinterPickerPage` | `ContentPage` | envuelve `PrinterPickerView` | — |
| `MauiRasterPreview` | `ContentView` | `ImageBytes` (`byte[]`), `ZoomFactor` (default `2.0`) | — |
| `MauiDocumentPreview` | `ContentView` | `Document` (`LayoutedDocument`) | — |
| `MauiDiagnosticsView` | `ContentView` | `Report` (`DiagnosticsReport`) | — |

- **`PrinterStatusBadge`**: muestra el estado del `IThermalPrinterService` con color y texto; se
  actualiza solo al cambiar `ConnectionState`, `CurrentDevice` o `LastError` (el servicio implementa
  `INotifyPropertyChanged`).
- **`PrinterPickerView`**: descubre dispositivos y conecta al seleccionar uno. Con
  `AutoConnectIfSingle` activo y un único dispositivo descubierto, conecta automáticamente.
  `FilterKind="bluetooth"` restringe el barrido a ese transport.
- **`PrinterPickerPage`**: página modal con botón Cancelar; se cierra al conectar o cancelar.
- **`MauiRasterPreview`**: muestra el PNG de `RasterPreviewRenderer` con zoom configurable dentro
  de un `ScrollView`; placeholder «(sin vista previa)» cuando no hay bytes.
- **`MauiDocumentPreview`**: vista previa a partir del `LayoutedDocument` (salida de
  `RenderLayout`), sin pasar por un renderer.
- **`MauiDiagnosticsView`**: renderiza el `DiagnosticsReport` en secciones (Librería, Aplicación,
  Dispositivo, Impresora, Permisos, Notas, fecha de captura).

Uso declarativo en XAML:

```xml
xmlns:muic="clr-namespace:MotorDsl.Maui.Controls;assembly=MotorDsl.Maui"

<muic:PrinterStatusBadge x:Name="StatusBadge" />
<muic:PrinterPickerView  x:Name="DevicePicker" FilterKind="bluetooth" />
<muic:MauiRasterPreview  x:Name="RasterPreview" ZoomFactor="2" />
```

Los controles se enlazan al servicio desde code-behind (`StatusBadge.Service = _printer;`).
En los samples se los oculta en iOS con `IsVisible="{OnPlatform Android=True, iOS=False}"`,
porque el transport Bluetooth no aplica ahí.

---

## 3. Renderers MAUI

### `BitmapEscPosRenderer` — target `escpos-bitmap`

Extiende el camino ESC/POS con soporte real de imágenes: para las entradas con
`is_bitmap = true` en el `DeviceMetadata` usa el `IBitmapRasterizer` y emite `GS v 0`
(`1D 76 30 00 xL xH yL yH` + datos); para el resto delega en `EscPosRenderer`.

**Manejo de fallas por severidad** (comportamiento fijado en v1.0.13):

| Situación | Resultado |
|---|---|
| La imagen **no se puede rasterizar** | `Error` **preciso**, con el `source` recortado y la causa: `Image rasterization failed (source='…'): <causa>`. Aborta el ticket |
| La imagen **decodifica pero sale en blanco** (placeholder transparente) | `Warning`; el ticket **sí** se imprime |

No hay degradación silenciosa: todo problema de imagen queda visible en `RenderResult.Errors` o
`Warnings`. Antes de v1.0.13 cualquier fallo de imagen descartaba **todo** el documento con un
`Output` de 0 bytes y el mensaje genérico `BitmapEscPos rendering failed`.

### `PdfRenderer` — target `pdf`

Construido sobre PdfSharpCore. Soporta texto con **word-wrap por medición real**
(`XGraphics.MeasureString`) y **salto de página automático**, QR (vía `QrCodeRasterizer`) y
código de barras con **fallback a texto** (EAN-13 nativo está en el roadmap). Márgenes de 40 pt,
interlineado de 4 pt e imágenes de 150×150 pt. El estado del render (documento, página actual,
`XGraphics`, cursor vertical) se encapsula en una clase interna con `EnsureSpace(needed)`, que
abre página nueva y resetea el cursor cuando no alcanza el espacio.

### `RasterPreviewRenderer` — target `raster-preview`

Produce un **PNG** que simula lo que rasterizaría la impresora térmica: texto monoespaciado a
1 bit, bitmaps, QR y el fallback de barcode. Convierte el bit array *packed* de `RasterizedImage`
a `SKBitmap` blanco/negro. Sirve para vista previa fiel sin enviar nada al hardware; se muestra
con `MauiRasterPreview`.

---

## 4. Rasterizadores

| Clase | Contrato | Qué hace |
|---|---|---|
| `SkiaSharpRasterizer` | `IBitmapRasterizer` | Decodifica `data:image/png;base64,…` a raster 1-bit apto para `GS v 0` |
| `QrCodeRasterizer` | — (clase concreta) | Genera el QR a `SKBitmap` con módulos 1-bit sin antialias; `Measure(data, moduleSize, ecc)` calcula el tamaño para el layout. Reutilizado por `PdfRenderer` y `RasterPreviewRenderer` |

> **Detalle de implementación con historia**: `SkiaSharpRasterizer` decodifica con
> `SKImage.FromEncodedData` + `SKBitmap.FromImage`, **no** con `SKBitmap.Decode(byte[])`. En
> SkiaSharp 3.x ese último devuelve `null` incluso para PNG válidos (reproducido con un PNG 1×1
> estándar), lo que hacía fallar el rasterizado y descartar el ticket completo. Cambiarlo de
> vuelta reintroduce el bug corregido en v1.0.13. Además, `Convert.FromBase64String` está envuelto
> para reportar un mensaje claro cuando el `source` no es base64 válido, y se eliminaron las
> trazas `Console.WriteLine` que volcaban parte del base64 a la salida estándar en cada render.

---

## 5. `MauiPrintErrorHandler`

Hereda de `DefaultPrintErrorHandler`, conservando su política de retry/abort
(ver [04_impresion-transports](04_impresion-transports.md) §3), y agrega logging vía
`Debug.WriteLine` más eventos públicos consumibles para feedback en UI (snackbar / toast).
**No bloquea** la UI. Se registra con `Replace`, desplazando al handler default.

---

## 6. `MauiDiagnosticsReportProvider`

Implementa `IDiagnosticsReportProvider` capturando datos reales de la plataforma: versiones de
las librerías `MotorDsl.*` cargadas, info de la app (nombre, versión, build, package), del
dispositivo (fabricante, modelo, plataforma, versión de OS, idiom, tipo), de la impresora
vinculada y del estado de los permisos Android (Bluetooth, ubicación).

El reporte se puede: **ver** en pantalla con `MauiDiagnosticsView`; **imprimir** como ticket
térmico —`ToDslJson()` devuelve un documento DSL `integrated` que se pasa a
`IDocumentEngine.Render` con cualquier perfil, con QR de correlación—; o **compartir** por
email / WhatsApp / portapapeles vía la Share API. El patrón completo de los tres botones está en
`docs/10_developer_guide/diagnostics.md`.

---

## 7. Configuración de plataforma

Permisos Android requeridos por el transport Bluetooth (`Platforms/Android/AndroidManifest.xml`
de la app consumidora):

```xml
<uses-permission android:name="android.permission.BLUETOOTH_SCAN"
                 android:usesPermissionFlags="neverForLocation" />
<uses-permission android:name="android.permission.BLUETOOTH_CONNECT" />
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
```

Versiones mínimas de plataforma declaradas en `MotorDsl.Maui.csproj`: Android 25.0, iOS 15.0
(en `MotorDsl.Bluetooth.csproj`, Android 24.0). Ambos paquetes fijan
`AndroidLdFlags = -Wl,-z,max-page-size=16384` para compatibilidad con dispositivos de página de
16 KB. `MotorDsl.Maui` embebe `Resources/Fonts/DroidSans-Regular.ttf` como `EmbeddedResource`
(la usa el renderer raster para el texto monoespaciado).

---

## 8. Fuentes

| Tema | Archivo |
|---|---|
| Registro DI | `src/MotorDsl.Maui/MotorDslMauiServiceCollectionExtensions.cs` |
| Controles | `src/MotorDsl.Maui/Controls/*.cs` |
| Renderers | `src/MotorDsl.Maui/Renderers/*.cs` |
| Diagnóstico | `src/MotorDsl.Maui/Diagnostics/MauiDiagnosticsReportProvider.cs` |
| Error handler | `src/MotorDsl.Maui/Printing/MauiPrintErrorHandler.cs` |
| Guías | `docs/10_developer_guide/{componentes-ux-maui,render-pixelado-y-pdf,guia-integracion-maui,diagnostics,soporte-imagenes-termicas}.md` |
| Historia de los fixes de imagen | `CHANGELOG.md` (1.0.13) |
