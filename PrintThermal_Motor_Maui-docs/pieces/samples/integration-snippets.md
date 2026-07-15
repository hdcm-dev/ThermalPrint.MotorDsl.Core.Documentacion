---
doc_id: samples-integration-snippets
doc_type: integration-snippets
title: "Snippets de integración — Samples MAUI de MotorDsl"
version: 1.0.0
status: draft
origin: reverse-engineered
confidence: high
owner: equipo-motordsl
last_review: 2026-07-14
audience: [dev, agentes-automaticos]
classification: uso-interno
source_ref: "v1.0.13 @83677eb"
---

# Snippets de integración — Samples MAUI de MotorDsl

> Corpus **curado** de fragmentos de integración (Marco de Documentación §13.2: se muestra el
> **uso canónico**, no archivos enteros). Cada snippet es un fragmento mínimo representativo,
> extraído de los samples reales; las elisiones se marcan con `// …`.
>
> Complementa a [`README.md`](./README.md) (visión de los 5 samples) y al índice
> [`06_samples.md`](../../../ia-db/indexes/06_samples.md).

## Convenciones de procedencia

- Toda cita usa el formato `src: ruta#Lx-Ly @83677eb`.
- Las rutas son relativas a la raíz del repo fuente `PrintThermal_Motor_Maui/` (origen solo lectura).
- `@83677eb` = commit de referencia (`v1.0.13`, `HEAD = 83677eb`).
- `// …` marca líneas omitidas respecto del archivo original.
- Los rangos de línea corresponden al archivo **completo** en el origen, no al fragmento recortado.
- Lo no confirmable desde los samples se marca explícitamente como **No verificado**.

---

## 1. Bootstrap DI en MauiProgram (canónico)

**Qué demuestra**: el cableado completo de MotorDsl en el contenedor DI de MAUI: pipeline del
motor + plantillas + perfiles + renderers MAUI + transporte Bluetooth. Es el orden y las llamadas
que un dev externo debe replicar.

**Precondiciones**: proyecto .NET MAUI (`net10.0-android`/`net10.0-ios`) con referencia a
`MotorDsl.Extensions` (`AddMotorDslEngine`, `AddTemplates`, `AddProfiles`), `MotorDsl.Maui`
(`AddMotorDslMaui`) y `MotorDsl.Bluetooth` (`AddBluetoothPrinterTransport`).

**Resultado esperado**: `IDocumentEngine`, `IThermalPrinterService`, `IBitmapRasterizer`,
`IDiagnosticsReportProvider` y los renderers quedan resolubles por DI; el catálogo tiene la
plantilla `acta-infraccion-integrada` y 4 perfiles.

`src: samples/MotorDsl.Nuget.Integrated.MultaApp/MauiProgram.cs#L29-L54 @83677eb`

```csharp
// El template registrado es un JSON integrado: ya tiene todos los valores resueltos.
builder.Services.AddMotorDslEngine()
    .AddTemplates(t =>
    {
        t.Add("acta-infraccion-integrada", MultaIntegratedDsl.Document);
    })
    .AddProfiles(p =>
    {
        p.Add(new DeviceProfile("thermal_58mm", 32, "escpos-bitmap"));
        p.Add(new DeviceProfile("preview", 32, "raster-preview"));
        p.Add(new DeviceProfile("a4-pdf", 80, "pdf"));
        p.Add(new DeviceProfile("pdf", 48, "pdf"));
    })
    .AddMotorDslMaui();

// Renderer "escpos" nativo CON rasterizer: pisa por Target al "escpos" del core (RendererRegistry
// reemplaza por Target) para que firmas (role=signature) salgan inline y el logo (role=logo) por NV.
builder.Services.AddSingleton<MotorDsl.Core.Contracts.IRenderer>(sp =>
    new MotorDsl.Rendering.EscPosRenderer(
        sp.GetRequiredService<MotorDsl.Core.Contracts.IBitmapRasterizer>()));

// Transport Bluetooth (Android Classic SPP)
builder.Services.AddBluetoothPrinterTransport();

builder.Services.AddTransient<MainPage>();
```

> **Variante mínima** (sample sin controles MAUI ni BT de librería): `MotorDsl.SampleApp` cablea solo
> `AddMotorDslEngine().AddTemplates(...).AddProfiles(...)` y registra servicios de impresión locales
> (`IThermalPrinterService → ThermalPrinterService`). `src: samples/MotorDsl.SampleApp/MauiProgram.cs#L26-L39 @83677eb`.

---

## 2. Definición de un DeviceProfile

**Qué demuestra**: cómo se construye un `DeviceProfile` (ctor de 3 args: `name`, ancho en columnas,
`RenderTarget`) y cómo se afinan sus *capabilities* en tiempo de render.

**Precondiciones**: `using MotorDsl.Core.Models;`. El `RenderTarget` (3er arg) debe corresponder a
un renderer registrado (p. ej. `escpos-bitmap`, `raster-preview`, `pdf`, `text`); si no existe, el
`RendererRegistry` cae a `"text"` (**No verificado** desde el sample — comportamiento del core).

**Resultado esperado**: un perfil que el `LayoutEngine`/renderer usa para ancho, wrap y degradación.

Registro de perfiles (construcción con el ctor de 3 args):

`src: samples/MotorDsl.Nuget.Integrated.MultaApp/MauiProgram.cs#L34-L40 @83677eb`

```csharp
.AddProfiles(p =>
{
    p.Add(new DeviceProfile("thermal_58mm", 32, "escpos-bitmap"));
    p.Add(new DeviceProfile("preview", 32, "raster-preview"));
    p.Add(new DeviceProfile("a4-pdf", 80, "pdf"));
    p.Add(new DeviceProfile("pdf", 48, "pdf"));
})
```

Afinado de *capabilities* por render (creado ad-hoc en el code-behind, no en el catálogo):

`src: samples/MotorDsl.Nuget.Integrated.MultaApp/Pages/MainPage.xaml.cs#L262-L265 @83677eb`

```csharp
profile = new DeviceProfile("58HB6", 32, "escpos-bitmap");
profile.SetCapability("supports_bitmap", true);
profile.SetCapability("bitmap_max_width_px", 320);
profile.SetCapability("bitmap_binarization_threshold", 128);
```

> Símbolos usados y confirmados en el sample: `DeviceProfile(string, int, string)`,
> `DeviceProfile.SetCapability(string, object)`. Claves de capability observadas:
> `supports_bitmap`, `bitmap_max_width_px`, `bitmap_binarization_threshold`, `nv_logo_keycode`,
> `nv_logo_kind` (`#L253-L257`).

---

## 3. Registro de una plantilla DSL (classic e integrated)

**Qué demuestra**: las dos formas del DSL y su registro. La diferencia sintáctica clave: classic usa
`"text": "{{placeholder}}"` y admite `loop`; integrated usa `"value": "texto resuelto"` y declara
`"format": "integrated"` a nivel raíz.

**Precondiciones**: la plantilla es un `string` C# (raw string literal) expuesto como miembro estático;
se registra con `AddTemplates(t => t.Add(id, plantilla))`.

**Resultado esperado**: classic requiere `Render(dsl, data, profile)` (3 args, con diccionario de
datos); integrated requiere `Render(json, profile)` (2 args, sin datos — se salta Evaluate).

### 3.1 Classic — `{{placeholders}}` + `loop`

`src: samples/MotorDsl.SampleApp/Templates/TicketDsl.cs#L8-L51 @83677eb`

```csharp
public const string Template = """
{
  "id": "ticket-venta-001",
  "version": "1.0",
  "root": {
    "type": "container",
    "layout": "vertical",
    "children": [
      { "type": "text", "text": "{{storeName}}", "style": { "align": "center", "bold": true } },
      // …
      {
        "type": "loop",
        "source": "items",
        "itemAlias": "item",
        "body": {
          "type": "container",
          "layout": "vertical",
          "children": [
            { "type": "text", "text": "{{item.nombre}}" },
            { "type": "text", "text": "  {{item.cantidad}} x ${{item.precio}}          ${{item.total}}" }
          ]
        }
      }
      // …
    ]
  }
}
""";
```

Registro y datos de acompañamiento (`GetSampleData()` provee el diccionario para los `{{...}}`):

`src: samples/MotorDsl.SampleApp/MauiProgram.cs#L27-L30 @83677eb`

```csharp
.AddTemplates(t =>
{
    t.Add("ticket-venta", TicketDsl.Template);
})
```

### 3.2 Integrated — `"format": "integrated"` + `"value"`

`src: samples/MotorDsl.Nuget.Integrated.MultaApp/Templates/MultaIntegratedDsl.cs#L25-L57 @83677eb`

```csharp
public static readonly string Document = $$"""
{
  "id": "acta-infraccion-001",
  "version": "1.0",
  "format": "integrated",
  "root": {
    "type": "container",
    "layout": "vertical",
    "children": [
      {
        "type": "image",
        "source": "data:image/bmp;base64,{{LogoBase64}}",
        "imageType": "bitmap",
        "role": "logo",
        "width": 200,
        "style": { "align": "center" }
      },
      { "type": "text", "value": "MUNICIPALIDAD DE EJEMPLO", "style": { "align": "center", "bold": true } },
      // …
      { "type": "text", "value": "ACTA DE INFRACCIÓN N°: 2026-00123", "style": { "bold": true } }
      // …
    ]
  }
}
""";
```

> El doc-comment de la clase documenta la regla: en integrated **no** hay `{{placeholders}}`, `loop`
> ni `conditional`; el motor lo procesa con `IDocumentEngine.Render(integratedJson, profile)` sin
> Evaluate. `src: samples/MotorDsl.Nuget.Integrated.MultaApp/Templates/MultaIntegratedDsl.cs#L3-L8 @83677eb`.
>
> Nota (H4): `LogoBase64`/`FirmaBase64` son **BMP** (magic `Qk0`), pese a que el comentario los llama
> "PNG". `src: .../MultaIntegratedDsl.cs#L11-L18 @83677eb`.

---

## 4. Code-behind de impresión (Render + SendBytesAsync)

**Qué demuestra**: el flujo canónico de impresión: **render primero** (diagnóstico independiente de
la impresora), verificación de conexión y envío de bytes ESC/POS por el transporte.

**Precondiciones**: `IDocumentEngine _engine` e `IThermalPrinterService _printer` inyectados por
constructor. Impresora emparejada y conectada (BT, Android).

**Resultado esperado**: si `result.IsSuccessful` y `result.Output is byte[]`, se envían los bytes con
`SendBytesAsync`; si no hay conexión, el render igual funciona (offline) y se avisa.

`src: samples/MotorDsl.Nuget.Integrated.MultaApp/Pages/MainPage.xaml.cs#L268-L293 @83677eb`

```csharp
var result = _engine.Render(doc, profile);

if (!result.IsSuccessful || result.Output is not byte[] bytes)
{
    var firstErr = result.Errors.FirstOrDefault() ?? "sin errores";
    // … log de errores/warnings …
    return;
}

// Verificar impresora antes de enviar
if (!_printer.IsConnected)
{
    ShowMessage($"Render OK ({bytes.Length} bytes) pero no hay impresora conectada.");
    return;
}

await Task.Delay(500);
await _printer.SendBytesAsync(bytes);
ShowMessage($"Impreso OK — {bytes.Length} bytes enviados.");
```

> Miembros usados y confirmados en el sample: `IDocumentEngine.Render(string, DeviceProfile)`,
> `RenderResult.IsSuccessful`, `.Output`, `.Errors`; `IThermalPrinterService.IsConnected`,
> `.SendBytesAsync(byte[])`. En este sample `IThermalPrinterService` viene de `MotorDsl.Printing`
> (línea `using` #L5). La **firma completa** del `SendBytesAsync` de librería es **No verificado**
> desde los samples; el sample `MotorDsl.SampleApp` define una interfaz local homónima con firma
> `Task SendBytesAsync(byte[] data, PrinterProfile? profile = null, PrintRetryOptions? retryOptions = null)`
> (`src: samples/MotorDsl.SampleApp/Services/IThermalPrinterService.cs#L23 @83677eb`).

---

## 5. Uso de controles MAUI en XAML (PrinterStatusBadge / PrinterPickerView / MauiRasterPreview)

**Qué demuestra**: cómo declarar los controles publicados de `MotorDsl.Maui.Controls` en XAML y
cablearlos al servicio de impresión en el code-behind.

**Precondiciones**: `AddMotorDslMaui()` + `AddBluetoothPrinterTransport()` registrados (snippet §1).
Namespace XAML `muic` apuntando al assembly `MotorDsl.Maui`.

**Resultado esperado**: el badge muestra estado de conexión; el picker escanea/lista dispositivos BT;
el `MauiRasterPreview` pinta el PNG del render de preview. En iOS se ocultan por `OnPlatform`.

Declaración XAML (namespace + controles):

`src: samples/MotorDsl.Nuget.Integrated.MultaApp/Pages/MainPage.xaml#L4, L12-L13, L48-L50 @83677eb`

```xml
<ContentPage xmlns:muic="clr-namespace:MotorDsl.Maui.Controls;assembly=MotorDsl.Maui" …>
    <!-- … -->
    <muic:PrinterStatusBadge x:Name="StatusBadge" IsVisible="{OnPlatform Android=True, iOS=False}" />
    <muic:PrinterPickerView x:Name="DevicePicker" FilterKind="bluetooth"
                            IsVisible="{OnPlatform Android=True, iOS=False}" />
    <!-- … -->
    <Frame x:Name="RasterFrame" IsVisible="False">
        <muic:MauiRasterPreview x:Name="RasterPreview" ZoomFactor="2" HeightRequest="320" />
    </Frame>
</ContentPage>
```

Cableado en code-behind (asignar el servicio y suscribir eventos del picker):

`src: samples/MotorDsl.Nuget.Integrated.MultaApp/Pages/MainPage.xaml.cs#L57-L60 @83677eb`

```csharp
StatusBadge.Service = _printer;
DevicePicker.Service = _printer;
DevicePicker.DeviceSelected += (_, device) => ShowMessage($"Conectado a {device.Name}.");
DevicePicker.ScanError += (_, ex) => ShowMessage($"BT Error: {ex.Message}");
```

Alimentar el preview con el PNG del render:

`src: samples/MotorDsl.Nuget.Integrated.MultaApp/Pages/MainPage.xaml.cs#L210-L214 @83677eb`

```csharp
if (result.IsSuccessful && result.Output is byte[] bytes)
{
    RasterPreview.ImageBytes = bytes;
    RasterFrame.IsVisible = true;
}
```

> Símbolos de `MotorDsl.Maui.Controls` confirmados en uso: controles `PrinterStatusBadge`,
> `PrinterPickerView` (props `Service`, `FilterKind`; eventos `DeviceSelected`, `ScanError`;
> método `ScanAsync()` en `#L65`), `MauiRasterPreview` (props `ZoomFactor`, `ImageBytes`).

---

## 6. Permisos Android (AndroidManifest.xml)

**Qué demuestra**: los permisos y `<queries>` que una app MAUI necesita para escanear e imprimir por
Bluetooth en Android 12+ y legacy. Idéntico en los 5 samples.

**Precondiciones**: app Android; la solicitud **runtime** de `BLUETOOTH_SCAN`/`BLUETOOTH_CONNECT`
(API 31+) se hace además en código (`MainPage.xaml.cs#L77-L131`).

**Resultado esperado**: el escaneo BT funciona en Android 12+ (con `neverForLocation`) y en < 12
(vía permisos de ubicación).

`src: samples/MotorDsl.SampleApp/Platforms/Android/AndroidManifest.xml#L10-L31 @83677eb`

```xml
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
<uses-permission android:name="android.permission.INTERNET" />

<!-- Bluetooth (legacy API < 31) -->
<uses-permission android:name="android.permission.BLUETOOTH" />
<uses-permission android:name="android.permission.BLUETOOTH_ADMIN" />
<!-- Bluetooth (API 31+ / Android 12+) -->
<uses-permission android:name="android.permission.BLUETOOTH_SCAN"
                 android:usesPermissionFlags="neverForLocation" />
<uses-permission android:name="android.permission.BLUETOOTH_CONNECT" />

<!-- Ubicación (necesario para escaneo Bluetooth) -->
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />

<queries>
    <intent>
        <action android:name="android.bluetooth.adapter.action.REQUEST_ENABLE" />
    </intent>
</queries>

<uses-sdk android:minSdkVersion="25" android:targetSdkVersion="36" />
```

---

## 🤖 Para agentes

Validaciones antes de consumir/emitir estos snippets:

| Validación | Regla | Cómo verificar |
|---|---|---|
| Procedencia presente | Todo snippet debe llevar `src: ruta#Lx-Ly @83677eb`. | Cada bloque de arriba tiene su línea `src:` inmediatamente antes. |
| Símbolos existen | No inventar tipos/miembros; cada símbolo citado existe en el archivo/rango indicado. | Abrir `ruta` en el origen (solo lectura) y confirmar en el rango de líneas. Símbolos clave: `AddMotorDslEngine`, `AddTemplates`, `AddProfiles`, `AddMotorDslMaui`, `AddBluetoothPrinterTransport`, `DeviceProfile(string,int,string)`, `DeviceProfile.SetCapability`, `IDocumentEngine.Render`, `RenderResult.{IsSuccessful,Output,Errors}`, `IThermalPrinterService.{IsConnected,SendBytesAsync}`, `PrinterStatusBadge`, `PrinterPickerView`, `MauiRasterPreview`. |
| Formato correcto por sobrecarga | classic → `Render(dsl, data, profile)` (3 args); integrated → `Render(json, profile)` (2 args). | Ver §3 y §4; el sample integrado usa 2 args (`MainPage.xaml.cs#L176`, `#L268`). |
| No copiar archivos enteros | Solo fragmento mínimo representativo con `// …` en elisiones. | Ningún bloque reproduce el archivo completo (p. ej. los base64 de imágenes se omiten). |
| Marcar lo no confirmado | Lo no verificable desde los samples se rotula **No verificado**. | Firma completa de `SendBytesAsync` de librería y fallback del `RendererRegistry` están así marcados. |
| Rutas | Relativas a `PrintThermal_Motor_Maui/`; el origen es **solo lectura**. | No escribir en `samples/`. |

Enlaces: [`README.md`](./README.md) · índice [`06_samples.md`](../../../ia-db/indexes/06_samples.md) ·
[`GLOSSARY.md`](../../GLOSSARY.md).
