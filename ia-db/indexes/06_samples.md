# 06 — Samples

> **Propósito**: decir qué demuestra cada una de las cinco apps de ejemplo, cuál mirar como
> referencia y cómo correrlas.
> **Fuentes primarias**: `samples/` (los cinco `.csproj`, `MauiProgram.cs`, `Pages/`,
> `Templates/`), `samples/Readme.md`, `samples/notas-debug-android.md`,
> `scripts/local/Readme.md`, `scripts/mobile/Readme.md`, `docs/11_examples/`.

---

## 1. Catálogo

Las cinco son apps .NET MAUI. Se diferencian en **dos ejes independientes**: cómo consumen la
librería (proyecto o paquete) y qué formato del DSL usan (`template + data` o `integrated`).

| Sample | `ApplicationId` | Formato DSL | Consumo | Qué demuestra |
|---|---|---|---|---|
| `MotorDsl.SampleApp` | `com.motordsl.sampleapp` | template | `ProjectReference` (4) | El pipeline DSL puro: render a `text` y `escpos`, sin transport, sin PDF, sin bitmap |
| `MotorDsl.MultaApp` | `com.motordsl.multaapp` | template | `ProjectReference` (4) | Caso completo de multa de tránsito, con renderers y servicios **locales** al sample |
| `MotorDsl.Integrated.MultaApp` | `com.motordsl.integrated.multaapp` | integrated | `ProjectReference` (4) | El mismo caso con los datos ya resueltos en la plantilla |
| `MotorDsl.Nuget.MultaApp` | `com.motordsl.nuget.multaapp` | template | **`PackageReference` (7), `Version="1.0.*"`** | Valida que los paquetes publicados funcionen tal como se consumen |
| `MotorDsl.Nuget.Integrated.MultaApp` | `com.motordsl.nuget.integrated.multaapp` | integrated | `ProjectReference` (7) — ver §4 | El patrón canónico recomendado a un desarrollador externo |

**Cuál mirar primero**: `MotorDsl.Nuget.Integrated.MultaApp` es el punto de partida
recomendado en `samples/Readme.md` — combina formato integrado, controles MAUI y el registro
completo de servicios.

---

## 2. Los dos ejes

### Formato del DSL

| | `template + data` | `integrated` |
|---|---|---|
| Samples | `SampleApp`, `MultaApp`, `Nuget.MultaApp` | `Integrated.MultaApp`, `Nuget.Integrated.MultaApp` |
| Plantillas | con `{{placeholders}}`, `loop`, `conditional` | JSON ya resuelto |
| Llamada al motor | `_engine.Render(template, data, profile)` | `_engine.Render(json, profile)` |
| Pipeline | incluye la etapa Evaluator | la saltea |

Detalle de la diferencia en [02 §3](02_dsl-y-modelos.md).

### Modo de consumo

Los samples con `ProjectReference` a `src/MotorDsl.*` sirven para iterar sobre la librería sin
publicar paquetes. `MotorDsl.Nuget.MultaApp` es el único que consume **exclusivamente** por
`PackageReference` con `Version="1.0.*"`, y por eso es la prueba real de que lo publicado
funciona.

---

## 3. Dos generaciones de código

`MotorDsl.MultaApp` y `MotorDsl.Integrated.MultaApp` son **anteriores al refactor** que extrajo
los renderers gráficos y el servicio de impresión a `MotorDsl.Maui` y
`MotorDsl.Printing.Abstractions`. Por eso traen copias locales en sus propias carpetas
`Renderers/` (`BitmapEscPosRenderer`, `PdfRenderer`, `SkiaSharpRasterizer`) y `Services/`
(`IThermalPrinterService`, `ThermalPrinterService`, `PrinterProfile`), y las registran a mano:

```csharp
builder.Services.AddMotorDslEngine()
    .AddTemplates(…).AddProfiles(…)
    .AddRenderer<PdfRenderer>()          // clases locales del sample
    .AddRenderer<BitmapEscPosRenderer>();

builder.Services.AddSingleton<IBitmapRasterizer, SkiaSharpRasterizer>();
builder.Services.AddSingleton<IPrintErrorHandler, DefaultPrintErrorHandler>();
builder.Services.AddSingleton<IThermalPrinterService, ThermalPrinterService>();
```

Los dos samples `Nuget.*` usan la forma actual, que reemplaza todo eso por una llamada:

```csharp
builder.Services.AddMotorDslEngine()
    .AddTemplates(t => t.Add("acta-infraccion-integrada", MultaIntegratedDsl.Document))
    .AddProfiles(p =>
    {
        p.Add(new DeviceProfile("thermal_58mm", 32, "escpos-bitmap"));
        p.Add(new DeviceProfile("preview",      32, "raster-preview"));
        p.Add(new DeviceProfile("a4-pdf",       80, "pdf"));
        p.Add(new DeviceProfile("pdf",          48, "pdf"));
    })
    .AddMotorDslMaui();

builder.Services.AddBluetoothPrinterTransport();
```

**Al buscar el patrón vigente, mirar los `Nuget.*`.** Los otros dos son válidos como referencia
histórica, y `samples/Readme.md` lo advierte explícitamente.

Ninguno de los cinco registra todavía `AddNetworkPrinterTransport()`: el transport de red es
posterior y su ejemplo de uso está en el `README.md` de la raíz, no en un sample.

---

## 4. Observación — divergencia con `samples/Readme.md`

`samples/Readme.md` afirma que **los dos** samples `Nuget.*` referencian los paquetes
«exclusivamente por `<PackageReference>`… No usan `<ProjectReference>`».

Verificado sobre los `.csproj` en el commit `e688f3c`, eso vale para
`MotorDsl.Nuget.MultaApp`, pero **no** para `MotorDsl.Nuget.Integrated.MultaApp`, que declara
siete `<ProjectReference>` a `src/MotorDsl.*` (líneas 91-97 de su `.csproj`) y ningún
`PackageReference` a MotorDsl. El cambio entró en el commit `ebe03ef`
(*feat(printing): logo NV con recall…*), presumiblemente para poder iterar sobre la librería
sin publicar.

**Hecho**: el `.csproj` usa `ProjectReference`. **Interpretación**: la documentación quedó
desactualizada respecto del código. No se corrigió nada: indexar no modifica el proyecto.

---

## 5. Estructura típica de un sample

```text
samples/<Nombre>/
├── MauiProgram.cs              Registro de servicios: motor, plantillas, perfiles, transport
├── App.xaml / AppShell.xaml    Andamiaje MAUI
├── Pages/MainPage.xaml(.cs)    UI: picker, badge, vista previa, botones
├── Templates/*.cs              Las plantillas DSL como constantes string
├── Platforms/Android/          AndroidManifest.xml con los permisos, MainActivity
├── Platforms/iOS/              Info.plist, Entitlements, AppDelegate
└── Resources/Raw/motordsl-config.json
```

Las plantillas viven como constantes `string` en clases de `Templates/` (`MultaDsl`,
`TicketSimpleDsl`, `ComprobanteDsl`, y sus variantes `*IntegratedDsl`), no como archivos
sueltos: así se registran directo con `AddTemplates`.

Los tres samples que muestran vista previa traen además `Controls/MauiDocumentPreview.cs`
local, por la misma razón histórica de la §3.

### TFM condicional

Los cinco `.csproj` declaran:

```xml
<TargetFrameworks>net10.0-android</TargetFrameworks>
<TargetFrameworks Condition="…IsOSPlatform('windows') or …IsOSPlatform('osx')">$(TargetFrameworks);net10.0-ios</TargetFrameworks>
```

El TFM de iOS se agrega **solo si el SO puede compilarlo**. La razón: `-f net10.0-android`
filtra el *build* pero no el *restore*, que evalúa todos los TFM igual y en Linux muere con
`NETSDK1178` porque el workload `ios` no existe ahí.

**Este patrón vale para las apps, no para las librerías.** Aplicarlo a `MotorDsl.Bluetooth` o
`MotorDsl.Maui` haría que empaquetar en Linux produjera **en silencio** un `.nupkg` sin el
asset de iOS. Ver [08](08_build-devops.md).

---

## 6. Cómo correrlos

```bash
dotnet build -t:Run -f net10.0-android samples/<Nombre>/<Nombre>.csproj
```

Atajos en `scripts/local/` (Windows, `.bat`, requieren dispositivo por ADB):

| Script | Efecto |
|---|---|
| `run-MotorDsl.<Nombre>.bat` | Compila y lanza ese sample |
| `run-All.bat` | Los cinco en cadena; corre `update-packages.bat` antes |
| `update-packages.bat` | Actualiza las `PackageReference` de los samples Nuget a la última estable publicada, vía `dotnet-outdated` |

`scripts/mobile/publish-MotorDsl.<Nombre>-apk.bat` empaqueta el APK firmado; `publish-all.bat`
hace los cinco. El workflow `cd-android.yml` publica APK solo de `SampleApp` y `MultaApp`; ver
[08](08_build-devops.md).

---

## 7. Debugging en Android

`samples/notas-debug-android.md` reúne comandos `adb`, inspección de paquetes instalados y el
troubleshooting recurrente: Skia, `libstdc++` y las páginas de 16 KB.

Incluye, como referencia histórica, el crash de `libQuestPdfSkia.so` —`libstdc++.so.6` no
encontrada— que motivó migrar el renderer de PDF a **PdfSharpCore**. Ver
[05 §5](05_maui-ui-renderers.md).

---

## 8. Documentación narrada de los ejemplos

`docs/11_examples/` explica los casos paso a paso: `ejemplo-01-simple.md`,
`ejemplo-02-multa.md`, `ejemplo-03-multa-integrada.md` y `ejemplo-03-multaapp-nuget.md`. La
carpeta `imagenes_logos/` guarda los logotipos usados en los ejemplos, en `.bmp` y en
`.base64` listo para pegar en un nodo `image`. Ver [09](09_docs-existentes.md).
