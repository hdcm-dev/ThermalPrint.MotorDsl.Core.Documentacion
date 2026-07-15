# 06 — Índice de Samples (aplicaciones de ejemplo MotorDsl)

> **Propósito**: índice temático de las 5 apps .NET MAUI de demostración de MotorDsl.
> Cubre: qué demuestra cada sample, diferencias entre ellos (formato DSL classic vs
> integrated; consumo por ProjectReference vs PackageReference NuGet), estructura
> relevante (MauiProgram, páginas, servicios locales, renderers locales), dónde viven
> las plantillas DSL de ejemplo, permisos Android declarados y cómo correr cada app.
>
> **Fuentes primarias**: `samples/Readme.md`, `samples/notas-debug-android.md` y, por
> cada app, su `*.csproj`, `MauiProgram.cs`, `Pages/MainPage.xaml(.cs)`,
> `Platforms/Android/AndroidManifest.xml` y `Templates/*.cs`.
>
> **Versión de referencia**: `v1.0.13 @83677eb` (verificado en repo fuente:
> `git describe` → `v1.0.13-2-g83677eb`, HEAD = `83677eb`).
> Todas las rutas son relativas a la raíz del repo `PrintThermal_Motor_Maui/`.

---

## 1. Tabla comparativa de los 5 samples

| Sample | Qué demuestra | Formato DSL | Consumo MotorDsl | Renderers | Servicios de impresión | ApplicationId |
|---|---|---|---|---|---|---|
| `MotorDsl.SampleApp` | Demo mínimo: render a texto, hex dump ESC/POS, preview MAUI, impresión BT de un ticket de venta | classic (template + data) | ProjectReference (4: Core, Parser, Rendering, Extensions) | solo los del core (`text`, `escpos`) | locales (`Services/`) | `com.motordsl.sampleapp` |
| `MotorDsl.MultaApp` | Sample completo de multa de tránsito con PDF y ESC/POS bitmap | classic (template + data) | ProjectReference (4) | locales (`Renderers/`: PDF, bitmap, Skia) | locales (`Services/`) | `com.motordsl.multaapp` |
| `MotorDsl.Integrated.MultaApp` | Misma multa pero con DSL `"format": "integrated"` (datos pre-resueltos, sin Evaluator) | integrated | ProjectReference (4) | locales (`Renderers/`) | locales (`Services/`) | `com.motordsl.integrated.multaapp` |
| `MotorDsl.Nuget.MultaApp` | Equivalente a MultaApp consumiendo los 7 paquetes NuGet + controles `MotorDsl.Maui` | classic (template + data) | PackageReference NuGet (7, `Version="1.0.*"`) | de `MotorDsl.Maui` (`AddMotorDslMaui()`) | de la librería (`AddBluetoothPrinterTransport()`) | `com.motordsl.nuget.multaapp` |
| `MotorDsl.Nuget.Integrated.MultaApp` | Patrón canónico recomendado: formato integrated + paquetes + controles MAUI + logo NV (fase 4) | integrated | **ProjectReference temporal** (7) — ver Hallazgo H1 | de `MotorDsl.Maui` + `EscPosRenderer` nativo con rasterizer | de la librería | `com.motordsl.nuget.integrated.multaapp` |

Fuentes: catálogo en `samples/Readme.md#L10-L21`; csproj de cada app (referencias:
`samples/MotorDsl.SampleApp/MotorDsl.SampleApp.csproj#L73-L78`,
`samples/MotorDsl.MultaApp/MotorDsl.MultaApp.csproj#L76-L88`,
`samples/MotorDsl.Integrated.MultaApp/MotorDsl.Integrated.MultaApp.csproj#L76-L88`,
`samples/MotorDsl.Nuget.MultaApp/MotorDsl.Nuget.MultaApp.csproj#L72-L81`,
`samples/MotorDsl.Nuget.Integrated.MultaApp/MotorDsl.Nuget.Integrated.MultaApp.csproj#L72-L86`).

Ejes de diferenciación:

| Eje | Variante A | Variante B |
|---|---|---|
| Formato DSL | **classic**: template con `{{placeholders}}`, `loop`, `conditional` + diccionario de datos; `engine.Render(template, data, profile)` (3 args) | **integrated**: JSON con `"format": "integrated"` y todos los valores ya resueltos; `engine.Render(integratedJson, profile)` (2 args), sin etapa Evaluator |
| Consumo | **ProjectReference** a `src/MotorDsl.*` (iterar la librería sin publicar paquetes) | **PackageReference** NuGet `Version="1.0.*"` (valida los paquetes publicados) |
| Renderers/servicios | **locales al sample** (pre-refactor; carpetas `Renderers/` y `Services/` propias) | **de la librería** (`AddMotorDslMaui()` + `AddBluetoothPrinterTransport()`) |

Fuente de la semántica classic vs integrated: `samples/Readme.md#L128-L161` y doc-comment de
`samples/MotorDsl.Integrated.MultaApp/Templates/MultaIntegratedDsl.cs#L3-L8`.

---

## 2. Propiedades comunes a los 5 csproj

| Propiedad | Valor | Fuente (ejemplo) |
|---|---|---|
| TargetFrameworks | `net10.0-android;net10.0-ios` | `samples/MotorDsl.SampleApp/MotorDsl.SampleApp.csproj#L4` |
| SupportedOSPlatformVersion | Android 25.0 / iOS 15.0 | `...csproj#L23-L24` |
| AndroidLdFlags | `-Wl,-z,max-page-size=16384` (16k pages) | `...csproj#L30` |
| RuntimeIdentifiers Android | `android-arm;android-arm64;android-x86;android-x64` | `...csproj#L31` |
| AndroidPackageFormat | `apk` (Debug y Release) | `...csproj#L34-L46` |
| iOS Release | `UseInterpreter`, `PublishTrimmed`, `MtouchLink=SdkOnly`, AOT solo `ios-arm64` | `...csproj#L50-L60` |
| Config runtime | `Resources/Raw/motordsl-config.json` con `backendBaseUrl` (reescrito por script de publish) | `samples/MotorDsl.SampleApp/Resources/Raw/motordsl-config.json#L1-L4` |

Extras por sample: `MultaApp` e `Integrated.MultaApp` agregan `SkiaSharp.Views.Maui.Controls 3.119.2`
y `PdfSharpCore 1.3.67` para sus renderers locales (`samples/MotorDsl.MultaApp/MotorDsl.MultaApp.csproj#L83-L88`).

---

## 3. Detalle por sample

### 3.1 MotorDsl.SampleApp

- **Qué demuestra**: el pipeline DSL puro, sin PDF ni bitmap. Cuatro acciones en
  `Pages/MainPage.xaml.cs`: preview a texto plano (`#L234-L265`), hex dump ESC/POS
  (`#L269-L302`), vista previa MAUI vía `RenderLayout` (`#L306-L324`) e impresión BT
  (`#L328-L358`). Incluye el flujo completo de permisos BT Android 12+/legacy (`#L37-L101`).
- **Registro del motor**: `samples/MotorDsl.SampleApp/MauiProgram.cs#L26-L38` —
  `AddMotorDslEngine()` + template `ticket-venta` + perfil único
  `DeviceProfile("thermal_58mm", 32, "escpos")`; servicios locales
  `DefaultPrintErrorHandler` y `ThermalPrinterService`.
- **Estructura relevante**:

```
samples/MotorDsl.SampleApp/
├── MauiProgram.cs                  # registro del engine (L26-L38)
├── Pages/MainPage.xaml(.cs)        # scan/connect BT + 4 acciones de render
├── Controls/MauiDocumentPreview.cs # preview del documento layouteado
├── Services/                       # IThermalPrinterService, ThermalPrinterService, PrinterProfile (locales)
└── Templates/TicketDsl.cs          # plantilla DSL classic + GetSampleData()
```

- **Cómo correrlo**: `dotnet build -t:Run -f net10.0-android samples/MotorDsl.SampleApp/MotorDsl.SampleApp.csproj`
  o `scripts/local/run-MotorDsl.SampleApp.bat` (`samples/Readme.md#L242-L253`).

### 3.2 MotorDsl.MultaApp

- **Qué demuestra**: sample "histórico" completo (pre-refactor a `MotorDsl.Maui`):
  acta de infracción de tránsito con logo/firma en base64, render a PDF
  (PdfSharpCore) y ESC/POS bitmap (SkiaSharp), todo con renderers y servicios
  locales al sample (`samples/Readme.md#L199-L222`).
- **Registro del motor**: `samples/MotorDsl.MultaApp/MauiProgram.cs#L31-L52` —
  3 templates (`acta-infraccion`, `ticket-simple`, `comprobante-pago`), 3 perfiles
  (`thermal_58mm/32/escpos-bitmap`, `a4-pdf/80/pdf`, `pdf/48/pdf`),
  `AddRenderer<PdfRenderer>()`, `AddRenderer<BitmapEscPosRenderer>()`,
  `IBitmapRasterizer → SkiaSharpRasterizer`.
- **Página**: `Pages/MainPage.xaml.cs` usa un picker de 3 documentos y llama
  `_engine.Render(doc.Value.Template, doc.Value.Data, profile)` (3 args, classic)
  (`#L33-L35`, `#L229`, `#L267`, `#L321`).
- **Estructura relevante**:

```
samples/MotorDsl.MultaApp/
├── MauiProgram.cs
├── Pages/MainPage.xaml(.cs)
├── Controls/MauiDocumentPreview.cs
├── Renderers/                       # locales: BitmapEscPosRenderer, PdfRenderer, SkiaSharpRasterizer
├── Services/                        # locales: IThermalPrinterService, ThermalPrinterService, PrinterProfile
└── Templates/                       # MultaDsl, TicketSimpleDsl, ComprobanteDsl (classic)
```

### 3.3 MotorDsl.Integrated.MultaApp

- **Qué demuestra**: el formato `integrated` con consumo por ProjectReference:
  el JSON registrado ya tiene todos los valores resueltos (sin `{{placeholders}}`,
  sin `loop`/`conditional`) y el motor lo procesa con
  `IDocumentEngine.Render(integratedJson, profile)` sin etapa Evaluate
  (doc-comment en `samples/MotorDsl.Integrated.MultaApp/Templates/MultaIntegratedDsl.cs#L3-L8`).
- **Registro del motor**: `samples/MotorDsl.Integrated.MultaApp/MauiProgram.cs#L32-L52` —
  registra solo `acta-infraccion-integrada` en el catálogo; mismos 3 perfiles y
  renderers locales que MultaApp. La página consume los 3 documentos integrated
  directamente por referencia de clase (`Pages/MainPage.xaml.cs#L34-L36`) y llama
  `_engine.Render(doc, profile)` (2 args) (`#L229`, `#L267`, `#L321`).
- **Estructura**: idéntica a MultaApp salvo `Templates/` (versiones `*IntegratedDsl.cs`).
- **Nota del Readme**: existe *antes* del refactor que extrajo los renderers a
  `MotorDsl.Maui`; se conserva como referencia histórica y la forma recomendada
  para proyectos nuevos es `Nuget.Integrated.MultaApp` (`samples/Readme.md#L193-L195`).

### 3.4 MotorDsl.Nuget.MultaApp

- **Qué demuestra**: el mismo caso de multa classic pero consumiendo los **7
  paquetes NuGet** exclusivamente por `<PackageReference Version="1.0.*">`:
  `Core`, `Parser`, `Rendering`, `Extensions`, `Printing.Abstractions`,
  `Bluetooth`, `Maui` (`samples/MotorDsl.Nuget.MultaApp/MotorDsl.Nuget.MultaApp.csproj#L72-L81`;
  regla en `samples/Readme.md#L18-L21`). Valida los paquetes publicados.
- **Registro del motor**: `samples/MotorDsl.Nuget.MultaApp/MauiProgram.cs#L28-L48` —
  3 templates classic, 4 perfiles (agrega `preview/32/raster-preview`),
  `AddMotorDslMaui()` (renderers PDF/bitmap/Skia de la librería) y
  `AddBluetoothPrinterTransport()` (Android Classic SPP). Sin carpetas
  `Renderers/` ni `Services/` propias.
- **Página**: usa controles publicados `PrinterStatusBadge` y `PrinterPickerView`
  de `MotorDsl.Maui.Controls` (patrón mostrado en `samples/Readme.md#L70-L87`) y
  llama `_engine.Render(template, data, profile)` (`Pages/MainPage.xaml.cs#L166` y ss.).

### 3.5 MotorDsl.Nuget.Integrated.MultaApp (punto de partida recomendado)

- **Qué demuestra**: la combinación canónica recomendada a un desarrollador
  externo: formato integrated + paquetes NuGet + controles MAUI
  (`samples/Readme.md#L25-L29`). Además ejercita la fase 4 (logo NV):
  `Pages/MainPage.xaml.cs#L322` rasteriza el logo con
  `_rasterizer.Rasterize("data:image/bmp;base64," + MultaIntegratedDsl.LogoBase64, 320)`
  para aprovisionarlo, y `MauiProgram.cs#L43-L48` registra un `EscPosRenderer`
  nativo **con** rasterizer que pisa por Target al `escpos` sin rasterizer del
  core, para que las firmas (`role=signature`) salgan inline (GS v 0) y el logo
  (`role=logo`) por recall NV.
- **Registro del motor**: `samples/MotorDsl.Nuget.Integrated.MultaApp/MauiProgram.cs#L29-L51` —
  template `acta-infraccion-integrada`, 4 perfiles (incl. `preview`),
  `AddMotorDslMaui()`, `AddBluetoothPrinterTransport()`.
- **Consumo real hoy**: pese al nombre, el csproj usa `<ProjectReference>` a los
  7 proyectos `src/MotorDsl.*` de forma **temporal**, porque la fase 4 usa API aún
  no publicada (`ProvisionLogoAsync`, `CurrentCapabilities`, `PrintStrategySelector`,
  role de imagen); el comentario indica volver a NuGet al republicar
  (`samples/MotorDsl.Nuget.Integrated.MultaApp/MotorDsl.Nuget.Integrated.MultaApp.csproj#L72-L86`).
  Ver Hallazgo H1.
- **iOS**: los controles de impresión BT se ocultan con
  `IsVisible="{OnPlatform Android=True, iOS=False}"` (patrón en `samples/Readme.md#L76-L84`).

---

## 4. Plantillas DSL de ejemplo (insumo para documentar el DSL)

Todas las plantillas viven como strings C# (raw string literals) en `Templates/*.cs`
de cada sample. No hay archivos `.json` sueltos con DSL; el único `.json` en
`Resources/Raw/` es configuración de backend, no DSL.

### 4.1 Formato classic (template con `{{placeholders}}`, `loop`, `conditional` + `GetSampleData()`)

| Archivo | Id de plantilla | Contenido | Miembros |
|---|---|---|---|
| `samples/MotorDsl.SampleApp/Templates/TicketDsl.cs` | `ticket-venta-001` | Ticket de venta: header, `loop` de items, subtotal/impuesto/total | `Template` (`#L8`), `GetSampleData()` (`#L88`) |
| `samples/MotorDsl.MultaApp/Templates/MultaDsl.cs` | `acta-infraccion-001` | Acta de infracción: imágenes `image/bitmap` base64 (logo y firma), datos de infractor/vehículo, `loop` de infracciones | `LogoBase64` (`#L10`), `FirmaBase64` (`#L14`), `Template` (`#L17`), `GetSampleData()` (`#L176`) |
| `samples/MotorDsl.MultaApp/Templates/TicketSimpleDsl.cs` | — | Ticket simple de multa | `Template` (`#L8`), `GetSampleData()` (`#L72`) |
| `samples/MotorDsl.MultaApp/Templates/ComprobanteDsl.cs` | — | Comprobante de pago | `Template` (`#L8`), `GetSampleData()` (`#L76`) |
| `samples/MotorDsl.Nuget.MultaApp/Templates/{MultaDsl,TicketSimpleDsl,ComprobanteDsl}.cs` | ídem | copias de las de MultaApp (mismas líneas) | ídem |

### 4.2 Formato integrated (`"format": "integrated"`, valores resueltos, propiedad `value` en textos)

| Archivo | Id documento | Contenido | Miembro |
|---|---|---|---|
| `samples/MotorDsl.Integrated.MultaApp/Templates/MultaIntegratedDsl.cs` | `acta-infraccion-001` | Acta con datos ya resueltos (loop expandido en containers concretos, imágenes base64 embebidas) | `Document` (`#L24`), `"format": "integrated"` en `#L28` |
| `samples/MotorDsl.Integrated.MultaApp/Templates/TicketSimpleIntegratedDsl.cs` | — | Ticket simple integrated | `Document` (`#L9`), format en `#L13` |
| `samples/MotorDsl.Integrated.MultaApp/Templates/ComprobanteIntegratedDsl.cs` | — | Comprobante integrated | `Document` (`#L9`), format en `#L13` |
| `samples/MotorDsl.Nuget.Integrated.MultaApp/Templates/MultaIntegratedDsl.cs` | `acta-infraccion-001` | ídem, con `LogoBase64` **público** para el aprovisionado NV de fase 4 | `LogoBase64` (`#L13`, `public const`), `Document` (`#L25`), format en `#L29` |
| `samples/MotorDsl.Nuget.Integrated.MultaApp/Templates/{TicketSimple,Comprobante}IntegratedDsl.cs` | — | ídem Integrated.MultaApp | `Document` (`#L9`) |

Diferencias sintácticas observables entre formatos (útiles para documentar el DSL):

- classic usa `"text": "{{placeholder}}"` (`TicketDsl.cs#L27`); integrated usa
  `"value": "texto ya resuelto"` (`MultaIntegratedDsl.cs#L42`).
- classic admite nodos `loop` (`TicketDsl.cs#L34-L51`) y `conditional`; integrated
  los prohíbe (doc-comment `MultaIntegratedDsl.cs#L3-L8`).
- integrated declara `"format": "integrated"` a nivel raíz junto a `id`/`version`.
- Nodos observados en las plantillas: `container` (layout `vertical`), `text`
  (style: `align`, `bold`), `image` (`source` data-URI base64, `imageType: bitmap`,
  `width`), `loop` (`source`, `itemAlias`, `body`).

---

## 5. Permisos Android declarados

Los 5 manifests son **idénticos** (verificado archivo por archivo). Fuente ejemplo:
`samples/MotorDsl.SampleApp/Platforms/Android/AndroidManifest.xml#L10-L31`.

| Permiso | Motivo |
|---|---|
| `ACCESS_NETWORK_STATE`, `INTERNET` | red / backend |
| `BLUETOOTH`, `BLUETOOTH_ADMIN` | BT legacy (API < 31) |
| `BLUETOOTH_SCAN` (`neverForLocation`), `BLUETOOTH_CONNECT` | BT Android 12+ (API 31+) |
| `ACCESS_FINE_LOCATION`, `ACCESS_COARSE_LOCATION` | requerido para escaneo BT en Android < 12 |

Además: `<queries>` con intent `android.bluetooth.adapter.action.REQUEST_ENABLE`
(`#L25-L29`) y `<uses-sdk minSdkVersion=25 targetSdkVersion=36>` (`#L31`).
La solicitud runtime de permisos está implementada en cada `MainPage.xaml.cs`
(p.ej. `samples/MotorDsl.SampleApp/Pages/MainPage.xaml.cs#L38-L101`).

---

## 6. Cómo correr los samples

Fuente: `samples/Readme.md#L242-L257`.

```bash
dotnet build -t:Run -f net10.0-android samples/<NombreSample>/<NombreSample>.csproj
```

| Atajo | Función |
|---|---|
| `scripts/local/run-MotorDsl.<Nombre>.bat` | corre el sample en dispositivo conectado por ADB |
| `scripts/local/run-All.bat` | corre todos en orden |
| `scripts/mobile/publish-MotorDsl.<Nombre>-apk.bat` | empaqueta APK firmado |

Debugging Android (logs adb, inspección de packages, troubleshooting
Skia/`libstdc++`/16k pages): `samples/notas-debug-android.md`. Incluye como
referencia histórica el crash de `libQuestPdfSkia.so` (`libstdc++.so.6` no
encontrada) que motivó migrar el renderer PDF a **PdfSharpCore**
(`samples/Readme.md#L262-L267`).

---

## 7. Hallazgos

| # | Hallazgo | Fuente |
|---|---|---|
| H1 | `MotorDsl.Nuget.Integrated.MultaApp` **no consume NuGet hoy**: usa `<ProjectReference>` a los 7 proyectos de forma temporal porque la fase 4 requiere API no publicada; el catálogo de `samples/Readme.md#L15-L21` lo describe como PackageReference (desactualizado respecto del csproj) | `samples/MotorDsl.Nuget.Integrated.MultaApp/MotorDsl.Nuget.Integrated.MultaApp.csproj#L72-L86` |
| H2 | Los samples integrated registran solo `acta-infraccion-integrada` en el catálogo del engine; los otros 2 documentos integrated se pasan al motor directamente desde la página, sin registrarse | `samples/MotorDsl.Integrated.MultaApp/MauiProgram.cs#L33-L36` vs `Pages/MainPage.xaml.cs#L34-L36` |
| H3 | `Resources/Raw/motordsl-config.json` (presente en los 5 samples) apunta a una IP pública `http://190.188.36.33:5000` como `backendBaseUrl`; el comentario indica que un script la reescribe al publicar | `samples/MotorDsl.SampleApp/Resources/Raw/motordsl-config.json#L1-L4` |
| H4 | Los assets de imagen del acta (logo municipio y firma) son BMP base64 embebidos como `const string` en las plantillas — el comentario dice "PNG" pero el magic number `Qk0` corresponde a BMP | `samples/MotorDsl.MultaApp/Templates/MultaDsl.cs#L9-L15` |
| H5 | En iOS los botones de impresión/estado BT se ocultan por `OnPlatform` (la impresión BT del sample es Android-only: transport "Android Classic SPP") | `samples/Readme.md#L76-L84`; `samples/MotorDsl.Nuget.MultaApp/MauiProgram.cs#L44-L45` |
| H6 | El registro de un `EscPosRenderer` con rasterizer en Nuget.Integrated demuestra que `RendererRegistry` reemplaza renderers por Target (el registro de la app pisa al del core) | `samples/MotorDsl.Nuget.Integrated.MultaApp/MauiProgram.cs#L43-L48` |
| H7 | `samples/notas-debug-android.md` es un log de sesión de debugging (transcripción cruda de PowerShell/adb), no documentación formal | `samples/notas-debug-android.md#L1-L60` |
