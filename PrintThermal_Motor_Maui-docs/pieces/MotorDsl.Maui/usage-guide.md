---
doc_id: MotorDsl.Maui-usage-guide
doc_type: usage-guide
title: Guía de uso e integración — MotorDsl.Maui
version: 1.0.0
status: draft
origin: reverse-engineered
confidence: high
owner: equipo-motordsl
last_review: 2026-07-14
audience: [dev, arquitectura, agentes-automaticos]
classification: uso-interno
source_ref: v1.0.13 @83677eb
traces: []
---

# Guía de uso e integración — MotorDsl.Maui

> How-to (Diátaxis): integrar `MotorDsl.Maui` en una app .NET MAUI para descubrir/conectar una
> impresora térmica Bluetooth, previsualizar el documento y emitir la impresión. Los snippets con
> ruta `archivo#Lx-Ly @83677eb` son literales de la fuente/índice; los marcados **derivado** son
> patrones compuestos sobre firmas reales (se cita la firma). Reconstruido sobre **v1.0.13
> @83677eb** (`status: draft`).

## Requisitos previos

- .NET 10 con carga de trabajo MAUI. TFMs de la pieza: `net10.0-android`, `net10.0-ios`
  (`MotorDsl.Maui.csproj#L4`).
- Piso de plataforma: **Android 25.0** e **iOS 15.0** (`MotorDsl.Maui.csproj#L11-L12`). Si además
  usas `MotorDsl.Bluetooth` (Android 24.0), el piso efectivo es **25.0** — Hallazgo H3.
- La impresión Bluetooth Classic SPP **solo funciona en Android**; en iOS los métodos del transport
  lanzan `PlatformNotSupportedException` (índice 04 §4.1). Ver [Advertencias](#advertencias).

---

## Paso 1 — Instalar los paquetes

Adoptar el stack completo requiere **dos** `PackageReference`; las demás librerías entran como
dependencias transitivas (`MotorDsl.Core`, `Rendering`, `Extensions`, `Printing.Abstractions`):

```xml
<ItemGroup>
  <PackageReference Include="MotorDsl.Maui" Version="1.0.13" />
  <PackageReference Include="MotorDsl.Bluetooth" Version="1.0.13" />
</ItemGroup>
```

> Versión **unificada**: los 7 paquetes se publican con la misma versión para evitar el downgrade
> NU1605 (GLOSSARY: "Versión unificada"). Las dependencias NuGet nativas de `MotorDsl.Maui`
> (`SkiaSharp.Views.Maui.Controls 3.119.2`, `PdfSharpCore 1.3.67`, `QRCoder 1.8.0`) llegan
> transitivamente (`MotorDsl.Maui.csproj#L48-L52`).

---

## Paso 2 — Registrar los servicios (DI)

En `MauiProgram.cs`, encadena el motor, la capa MAUI y **al menos un transport**. Snippet literal
del índice (`ia-db/indexes/05_maui-ui-renderers.md` §11 — "firmas reales de la librería",
`@83677eb`):

```csharp
// MauiProgram.cs
builder.Services
    .AddMotorDslEngine()        // motor + registry (MotorDsl.Extensions)
    .AddMotorDslMaui();         // renderers pdf/escpos-bitmap/raster-preview,
                                // SkiaSharpRasterizer, QrCodeRasterizer,
                                // ThermalPrinterService, MauiPrintErrorHandler,
                                // MauiDiagnosticsReportProvider
builder.Services.AddBluetoothPrinterTransport();  // MotorDsl.Bluetooth (ver indice 04)
```

Qué deja registrado `AddMotorDslMaui` (firma real
`MotorDslMauiServiceCollectionExtensions.cs#L22-L33 @83677eb`):

| Servicio | Implementación | Método |
|---|---|---|
| `IBitmapRasterizer` | `SkiaSharpRasterizer` | `AddSingleton` |
| `QrCodeRasterizer` | (concreto) | `AddSingleton` |
| `IThermalPrinterService` | `ThermalPrinterService` | `TryAdd` (vía `AddMotorDslPrinting`) |
| `IPrintErrorHandler` | `MauiPrintErrorHandler` | **`Replace`** (pisa el default) |
| `IDiagnosticsReportProvider` | `MauiDiagnosticsReportProvider` | **`TryAddSingleton`** (el consumer puede prevalecer) |
| Renderers `pdf`/`escpos-bitmap`/`raster-preview` | (los 3) | `AddRenderer<T>` |

> Orden importante: para sustituir el `IDiagnosticsReportProvider` por uno propio, regístralo
> **antes** de `AddMotorDslMaui` (es `TryAddSingleton`). Para el `IPrintErrorHandler` no sirve
> registrarlo antes: `AddMotorDslMaui` usa `Replace` y siempre gana `MauiPrintErrorHandler`.

---

## Paso 3 — Permisos Android

Para el descubrimiento y la conexión BT, `MotorDsl.Bluetooth` exige Bluetooth habilitado y el
permiso `BLUETOOTH_CONNECT` en API 31+ (índice 04 §4, `BluetoothPrinterTransport.cs#L52-L96`). El
`MauiDiagnosticsReportProvider` además sondea `Permissions.Bluetooth` y `LocationWhenInUse` solo en
Android (índice 05 §4, `MauiDiagnosticsReportProvider.cs#L135-L168`).

**Solicitud en runtime** (MAUI Essentials — patrón **derivado**; firma de `Permissions.Bluetooth`
de MAUI Essentials, uso confirmado por el provider en `#L144-L153`):

```csharp
var status = await Permissions.RequestAsync<Permissions.Bluetooth>();
if (status != PermissionStatus.Granted)
{
    // informar al usuario; sin permiso el discover devuelve lista vacía
    return;
}
```

**Entradas del `AndroidManifest.xml`** — *No verificado* en la fuente destilada (el índice no
incluye el manifest). Guía derivada del requisito `BLUETOOTH_CONNECT` (API 31+) documentado en el
índice 04; ajusta según tu `targetSdkVersion` y valida contra los samples
(`samples/**`, índice 06):

```xml
<!-- No verificado: derivado del requisito BLUETOOTH_CONNECT del transport (indice 04 §4) -->
<uses-permission android:name="android.permission.BLUETOOTH_CONNECT" />
<uses-permission android:name="android.permission.BLUETOOTH_SCAN" />
<!-- En API <= 30 el pairing/descubrimiento clasico suele requerir ubicacion; validar por proyecto -->
```

---

## Paso 4 — UI declarativa con los controles

Los controles viven en `MotorDsl.Maui.Controls` (sin XAML propio, bindeables desde tu XAML). El
servicio inyectado (`IThermalPrinterService`) implementa `INotifyPropertyChanged`, así que el
`PrinterStatusBadge` se auto-actualiza.

**XAML** (patrón **derivado** de las bindables reales — `PrinterStatusBadge.cs#L15-L27`,
`PrinterPickerView.cs#L12-L31`, `MauiRasterPreview.cs#L11-L25`):

```xml
<ContentPage xmlns="http://schemas.microsoft.com/dotnet/2021/maui"
             xmlns:x="http://schemas.microsoft.com/winfx/2009/xaml"
             xmlns:ctl="clr-namespace:MotorDsl.Maui.Controls;assembly=MotorDsl.Maui"
             x:Class="MiApp.PrintPage">
    <VerticalStackLayout Padding="16" Spacing="12">

        <ctl:PrinterStatusBadge Service="{Binding Printer}" />

        <ctl:PrinterPickerView Service="{Binding Printer}"
                               FilterKind="bluetooth"
                               AutoConnectIfSingle="True" />

        <ctl:MauiRasterPreview x:Name="Preview" ZoomFactor="2" />

        <Button Text="Imprimir" Clicked="OnPrintClicked" />
    </VerticalStackLayout>
</ContentPage>
```

Alternativa: en vez de embeber `PrinterPickerView`, abre la página modal
`PrinterPickerPage(service, filterKind)` (`PrinterPickerPage.cs#L13`):

```csharp
await Navigation.PushModalAsync(new PrinterPickerPage(printerService, "bluetooth"));
```

---

## Paso 5 — Code-behind: previsualizar e imprimir

El flujo es: **DSL JSON → `IDocumentEngine.Render` → `RenderResult.Output` (bytes) →
`IThermalPrinterService.SendBytesAsync`**. El renderer se elige por el `Target` del
`DeviceProfile` (`escpos-bitmap` para imprimir, `raster-preview` para el PNG de preview).

**Preview raster** (patrón **derivado**; firma `Render(json, profile)` para formato *integrated* en
`DocumentEngine.cs#L139-L216`, GLOSSARY "Formato integrated"; `RenderResult.Output` en GLOSSARY):

```csharp
// engine: IDocumentEngine resuelto por DI; previewProfile.RenderTarget == "raster-preview"
var previewResult = engine.Render(dslIntegratedJson, previewProfile);
if (previewResult.IsSuccessful)
    Preview.ImageBytes = (byte[])previewResult.Output;   // MauiRasterPreview
```

**Imprimir** (patrón **derivado**; `Render` como arriba; `SendBytesAsync(data, profile?, retry?)`
en `IThermalPrinterService`, índice 04 §2/§3, `IThermalPrinterService.cs#L6-L37`):

```csharp
async void OnPrintClicked(object? sender, EventArgs e)
{
    // printerProfile.RenderTarget == "escpos-bitmap"
    var result = engine.Render(dslIntegratedJson, printerProfile);
    if (!result.IsSuccessful)
    {
        await DisplayAlert("Render", string.Join("\n", result.Errors), "OK");
        return;
    }

    try
    {
        // SendBytesAsync aplica retry (default MaxRetries=3) y relanza si agota intentos
        await printerService.SendBytesAsync((byte[])result.Output, printerProfile);
    }
    catch (Exception ex)
    {
        await DisplayAlert("Impresión", ex.Message, "OK");
    }
}
```

> `SendBytesAsync` gestiona el retry con backoff y, al agotar intentos, **relanza** una excepción
> `"Print failed after N attempt(s)…"` (índice 04 §3, `ThermalPrinterService.cs#L201-L244`). Para
> feedback no intrusivo, suscríbete a los eventos `RetryAttempted`/`Succeeded` de
> `MauiPrintErrorHandler` (`MauiPrintErrorHandler.cs#L12-L36`).

**Diagnóstico** (opcional; muestra un `DiagnosticsReport` antes de compartir/imprimir —
`MauiDiagnosticsReportProvider.cs#L18-L48`, `MauiDiagnosticsView.cs#L14-L26`):

```csharp
// provider: IDiagnosticsReportProvider (MauiDiagnosticsReportProvider) por DI
var report = provider.Build(notes: "diagnóstico", includePii: false);
var view = new MauiDiagnosticsView { Report = report };
// ...o exportar: provider.ToJson(report) / provider.ToPlainText(report) / provider.ToDslJson(report)
```

---

## Advertencias

- **Transport obligatorio.** Si no registras ningún transport (`AddBluetoothPrinterTransport()` u
  otro), `ThermalPrinterService` lanza `InvalidOperationException` **al construirse** — la app
  falla al resolver `IThermalPrinterService` (índice 05 §11, `ThermalPrinterService.cs#L86-L88`).
- **iOS oculta la impresión BT.** En iOS, `DiscoverAsync`/`ConnectAsync`/`WriteBytesAsync` del
  transport Bluetooth lanzan `PlatformNotSupportedException` (índice 04 §4.1,
  `BluetoothPrinterTransport.cs#L92-L93,L136-L138,L251-L253`). Oculta o deshabilita la UI de
  descubrimiento/impresión BT en iOS (los renderers PDF y raster-preview sí funcionan multiplataforma).
- **`PrinterPickerView` no notifica el fallo de conexión** (H6): si la conexión falla, el picker no
  dispara evento; el estado se refleja vía `ErrorOccurred` del servicio + `PrinterStatusBadge`
  (`PrinterPickerView.cs#L201-L210`). Mantén siempre un badge visible.
- **Un solo tipo de letra en PDF** (H7): `PdfRenderer` resuelve toda familia/estilo a `DroidSans`
  embebida; no esperes tipografías personalizadas en el PDF (`PdfRenderer.cs#L38-L41`).

---

## 🤖 Para agentes

- **Receta mínima verificada**: `AddMotorDslEngine().AddMotorDslMaui()` +
  `AddBluetoothPrinterTransport()`. Sin transport, la resolución de `IThermalPrinterService`
  **lanza** (no lo omitas).
- **Elección de `Target`**: imprimir → perfil con `RenderTarget = "escpos-bitmap"`; preview PNG →
  `"raster-preview"` → `MauiRasterPreview.ImageBytes`; documento/archivo → `"pdf"`.
- **Formato del DSL**: los ejemplos asumen *integrated* → `engine.Render(json, profile)` (2 args,
  sin etapa Evaluate). Para *classic* la firma es `Render(template, data, profile)` (3 args,
  GLOSSARY "Formato classic"/"integrated").
- **Plataforma**: encierra la impresión BT en `#if ANDROID` o comprueba plataforma; en iOS el
  transport lanza `PlatformNotSupportedException`.
- **No verificado en esta guía**: las líneas exactas del `AndroidManifest.xml` (el índice no
  incluye el manifest) y los snippets marcados **derivado** (compuestos sobre firmas reales
  citadas). El bootstrap DI del Paso 2 sí es literal del índice (§11). Todo lo demás es trazable a
  `MotorDsl.Maui/**` en **v1.0.13 @83677eb**.
