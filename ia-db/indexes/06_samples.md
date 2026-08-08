# 06 — Samples e integración

> **Propósito**: qué demuestra cada una de las 5 apps MAUI de ejemplo, cuál tomar como punto de
> partida y cuál es el patrón canónico de integración en una app externa.
> **Fuentes primarias**: `samples/Readme.md`, `samples/*/MauiProgram.cs`, `samples/*/Pages/`,
> `samples/*/Templates/`, `README.md` (Quickstart), `docs/11_examples/`.
> Cómo lanzarlos: [08_build-devops](08_build-devops.md).

---

## 1. Catálogo

| Sample | Qué demuestra | Modo de consumo |
|---|---|---|
| `MotorDsl.SampleApp` | Demo mínimo: render a texto y ESC/POS **sin transport** | `ProjectReference` |
| `MotorDsl.MultaApp` | Multa de tránsito completa con servicios MAUI locales; formato **clásico** (template + datos) | `ProjectReference` |
| `MotorDsl.Integrated.MultaApp` | Lo mismo con DSL en formato **`integrated`** (datos pre-resueltos) | `ProjectReference` |
| `MotorDsl.Nuget.MultaApp` | Equivalente a `MultaApp` consumiendo los paquetes publicados | `PackageReference` (7 paquetes, `Version="1.0.*"`) |
| `MotorDsl.Nuget.Integrated.MultaApp` | Equivalente al integrado, vía NuGet | `PackageReference` (7 paquetes, `Version="1.0.*"`) |

Los dos samples NuGet referencian los 7 paquetes **exclusivamente** por `<PackageReference>`;
no usan `<ProjectReference>`. Sirven como prueba de que los paquetes publicados son
autosuficientes.

**Punto de partida recomendado**: `MotorDsl.Nuget.Integrated.MultaApp` — combina formato
integrado + consumo desde NuGet + controles MAUI, y es el más cercano al patrón que se recomienda
a un desarrollador externo (fuente: `samples/Readme.md`).

---

## 2. Anatomía de un sample

```text
samples/<Sample>/
├── MauiProgram.cs              Cableado DI del motor, perfiles, plantillas y transport
├── App.xaml / AppShell.xaml    Bootstrap MAUI estándar
├── Pages/MainPage.xaml(.cs)    UI: picker de impresora, preview, botón imprimir
├── Templates/*.cs              Plantillas DSL como constantes string en C#
├── Controls/                   (SampleApp y MultaApp) Controles propios previos a MotorDsl.Maui
├── Renderers/                  (MultaApp e Integrated) Copias locales de renderers
├── Services/                   (SampleApp/MultaApp) Servicio de impresión local previo al paquete
├── Platforms/{Android,iOS}/    Manifest, permisos, entry points
└── Resources/Raw/motordsl-config.json   URL base del backend
```

Las plantillas viven como **constantes C#** (`MultaIntegratedDsl.Document`,
`TicketSimpleDsl`, `ComprobanteDsl`, `TicketDsl`), no como archivos `.json` embebidos: se
registran con `AddTemplates(t => t.Add("id", Xxx.Document))`.

> Los samples con carpetas `Controls/`, `Renderers/` y `Services/` propias
> (`MotorDsl.SampleApp`, `MotorDsl.MultaApp`, `MotorDsl.Integrated.MultaApp`) conservan copias
> locales anteriores a que esa funcionalidad se empaquetara en `MotorDsl.Maui`. Los samples
> `Nuget.*` ya usan solo los controles del paquete. Para copiar código, tomarlo de los `Nuget.*`.

---

## 3. Patrón canónico de integración

### 3.1 Paquetes

```xml
<PackageReference Include="MotorDsl.Maui"      Version="<latest>" />
<PackageReference Include="MotorDsl.Bluetooth" Version="<latest>" />
```

Los otros 5 paquetes llegan como dependencias transitivas.

### 3.2 `MauiProgram.cs`

```csharp
builder.Services.AddMotorDslEngine()
    .AddTemplates(t =>
    {
        t.Add("acta-infraccion-integrada", MultaIntegratedDsl.Document);
    })
    .AddProfiles(p =>
    {
        p.Add(new DeviceProfile("thermal_58mm", 32, "escpos-bitmap"));
        p.Add(new DeviceProfile("preview",      32, "raster-preview"));
        p.Add(new DeviceProfile("a4-pdf",       80, "pdf"));
    })
    .AddMotorDslMaui();

builder.Services.AddBluetoothPrinterTransport();
builder.Services.AddTransient<MainPage>();
```

Un perfil por **modo de salida**: impresión térmica, vista previa y PDF comparten el mismo
documento y solo cambian de `RenderTarget`.

### 3.3 UI

```xml
xmlns:muic="clr-namespace:MotorDsl.Maui.Controls;assembly=MotorDsl.Maui"

<muic:PrinterStatusBadge x:Name="StatusBadge"
                         IsVisible="{OnPlatform Android=True, iOS=False}" />
<muic:PrinterPickerView  x:Name="DevicePicker" FilterKind="bluetooth"
                         IsVisible="{OnPlatform Android=True, iOS=False}" />
<muic:MauiRasterPreview  x:Name="RasterPreview" ZoomFactor="2" />
```

Los controles Bluetooth se ocultan en iOS porque el transport Classic SPP no aplica ahí.

### 3.4 Code-behind

```csharp
public MainPage(IDocumentEngine engine, IThermalPrinterService printer)
{
    InitializeComponent();
    _engine = engine;
    _printer = printer;
    StatusBadge.Service  = _printer;   // enlace manual al servicio
    DevicePicker.Service = _printer;
}

private async void OnImprimir(object? sender, EventArgs e)
{
    var profile = new DeviceProfile("thermal_58mm", 32, "escpos-bitmap");
    var result  = _engine.Render(json, profile);          // sobrecarga integrada
    if (result.IsSuccessful && _printer.IsConnected)
        await _printer.SendBytesAsync((byte[])result.Output!);
}
```

Puntos a respetar: chequear `result.IsSuccessful` **antes** de enviar; el `Output` es `object?` y
requiere cast al tipo del target; `SendBytesAsync` ya trae retry propio, no envolverlo en otro
bucle de reintentos.

### 3.5 Permisos Android

`BLUETOOTH_SCAN` (con `usesPermissionFlags="neverForLocation"`), `BLUETOOTH_CONNECT` y
`ACCESS_FINE_LOCATION` en `Platforms/Android/AndroidManifest.xml`.

---

## 4. Configuración de backend

Cada sample de multa incluye `Resources/Raw/motordsl-config.json` con `backendBaseUrl`, la URL
base del backend externo del que la app toma los datos de la infracción. El valor versionado
apunta a una IP concreta y el script de publicación de la app host lo reescribe antes de compilar
el APK. **No es parte del motor**: es configuración de la app de ejemplo.

---

## 5. Ejemplos documentados

`docs/11_examples/` explica los casos paso a paso:

| Documento | Contenido |
|---|---|
| `ejemplo-01-simple.md` | Ticket mínimo de punta a punta |
| `ejemplo-02-multa.md` | Acta de infracción con formato clásico |
| `ejemplo-03-multa-integrada.md` | La misma acta en formato integrado |
| `ejemplo-03-multaapp-nuget.md` | La misma app consumiendo los paquetes NuGet |
| `imagenes_logos/` | Logos de prueba en `.bmp` y `.base64` (municipios) |

Plantillas JSON listas para usar en `docs/10_developer_guide/ejemplos-templates/`
(ver [02_dsl-y-modelos](02_dsl-y-modelos.md) §9).

Notas de depuración en Android: `samples/notas-debug-android.md`.

---

## 6. Fuentes

| Tema | Archivo |
|---|---|
| Catálogo y snippets | `samples/Readme.md` |
| Cableado por sample | `samples/*/MauiProgram.cs` |
| Plantillas de ejemplo | `samples/*/Templates/*.cs` |
| Quickstart oficial | `README.md` (raíz del repositorio) |
| Guía de integración | `docs/10_developer_guide/guia-integracion-maui.md` |
| Ejemplos narrados | `docs/11_examples/*.md` |
| Depuración Android | `samples/notas-debug-android.md` |
