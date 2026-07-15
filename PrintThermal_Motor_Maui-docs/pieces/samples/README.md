---
doc_id: samples-readme
doc_type: piece-readme
title: "Samples MAUI — Aplicaciones de ejemplo de MotorDsl"
version: 1.0.0
status: draft
origin: reverse-engineered
confidence: high
owner: equipo-motordsl
last_review: 2026-07-14
audience: [dev, arquitectura, qa, agentes-automaticos]
classification: uso-interno
source_ref: "v1.0.13 @83677eb"
---

# Samples MAUI — Aplicaciones de ejemplo de MotorDsl

> Pieza `samples`, criticidad **media** (no se distribuye; sirve de referencia de integración).
> Cinco apps .NET MAUI que demuestran cómo consumir MotorDsl end-to-end: registro DI, plantillas
> DSL, render, controles MAUI e impresión Bluetooth. El corpus de snippets curados con procedencia
> vive en [`integration-snippets.md`](./integration-snippets.md).
>
> Origen (solo lectura): `Librerias/PrintThermal_Motor_Maui/samples/`. Todas las rutas de este
> documento son relativas a la raíz del repo fuente `PrintThermal_Motor_Maui/`.

## 1. Resumen ejecutivo

| Pregunta | Respuesta |
|---|---|
| **¿Qué es?** | Un conjunto de 5 apps MAUI de demostración que ejercitan el motor MotorDsl sobre Android/iOS: desde el pipeline DSL puro (texto/ESC-POS) hasta el caso completo de acta de infracción con PDF, bitmap ESC/POS y logo NV. |
| **¿Para qué sirve?** | Servir de **referencia de integración** para un desarrollador externo: cómo cablear DI en `MauiProgram`, registrar plantillas y perfiles, invocar `Render`, usar los controles `MotorDsl.Maui.Controls` e imprimir por Bluetooth. |
| **¿A quién le sirve?** | **Devs** que integran el motor en una app MAUI; **QA** que valida los paquetes publicados; **agentes IA** que extraen snippets canónicos o generan código de integración. |
| **¿Qué NO es?** | No es código de producción ni parte de los paquetes NuGet. Los samples "históricos" (`MultaApp`, `Integrated.MultaApp`) preceden al refactor que extrajo renderers/servicios a `MotorDsl.Maui`. |
| **Punto de partida recomendado** | `MotorDsl.Nuget.Integrated.MultaApp` (formato *integrated* + controles MAUI + logo NV). Ver §4. |

Los 5 samples se diferencian por dos ejes ortogonales: **formato DSL** (classic vs integrated) y
**consumo** de la librería (ProjectReference vs PackageReference NuGet).

## 2. Tabla comparativa de los 5 samples

| Sample | Qué demuestra | Formato DSL | Consumo MotorDsl | Notas |
|---|---|---|---|---|
| `MotorDsl.SampleApp` | Pipeline DSL puro: preview a texto, hex dump ESC/POS, preview MAUI e impresión BT de un ticket de venta. Sin PDF ni bitmap. | classic | project-ref (4: Core, Parser, Rendering, Extensions) | Renderers solo del core (`text`, `escpos`); servicios de impresión **locales** (`Services/`). |
| `MotorDsl.MultaApp` | Acta de infracción completa con logo/firma base64, render a PDF (PdfSharpCore) y ESC/POS bitmap (SkiaSharp). | classic | project-ref (4) | Renderers y servicios **locales al sample** (`Renderers/`, `Services/`). Pre-refactor. |
| `MotorDsl.Integrated.MultaApp` | Misma acta pero con DSL `"format": "integrated"` (valores pre-resueltos, sin etapa Evaluate). | integrated | project-ref (4) | Idéntico a `MultaApp` salvo `Templates/*IntegratedDsl.cs`. Referencia histórica. |
| `MotorDsl.Nuget.MultaApp` | Acta classic consumiendo **7 paquetes NuGet** + controles `MotorDsl.Maui`. Valida los paquetes publicados. | classic | **nuget** (7, `Version="1.0.*"`) | Renderers vía `AddMotorDslMaui()`; transporte vía `AddBluetoothPrinterTransport()`. Sin carpetas propias. |
| `MotorDsl.Nuget.Integrated.MultaApp` | **Patrón canónico**: integrated + paquetes + controles MAUI + logo NV (fase 4). | integrated | **project-ref temporal** (7) — ver H1 | Pese al nombre "Nuget", hoy usa `<ProjectReference>` porque la fase 4 usa API no publicada. |

**Fuentes** — csproj de cada app:
`samples/MotorDsl.SampleApp/MotorDsl.SampleApp.csproj#L73-L78 @83677eb` (4 project-ref),
`samples/MotorDsl.Nuget.MultaApp/MotorDsl.Nuget.MultaApp.csproj#L72-L81 @83677eb` (7 NuGet `1.0.*`),
`samples/MotorDsl.Nuget.Integrated.MultaApp/MotorDsl.Nuget.Integrated.MultaApp.csproj#L72-L83 @83677eb` (7 project-ref temporales).
Catálogo y ejes: índice [`06_samples.md`](../../../ia-db/indexes/06_samples.md) §1.

## 3. Cómo correr cada sample

### 3.1 Directo con `dotnet`

```bash
dotnet build -t:Run -f net10.0-android samples/<NombreSample>/<NombreSample>.csproj
```

### 3.2 Scripts (verificados presentes en el repo fuente)

| Script | Función | Nombres reales |
|---|---|---|
| `scripts/local/run-MotorDsl.<Nombre>.bat` | Corre el sample en el dispositivo conectado por ADB | `run-MotorDsl.SampleApp.bat`, `run-MotorDsl.MultaApp.bat`, `run-MotorDsl.Integrated.MultaApp.bat`, `run-MotorDsl.Nuget.MultaApp.bat`, `run-MotorDsl.Nuget.Integrated.MultaApp.bat` |
| `scripts/local/run-All.bat` | Corre todos en orden | — |
| `scripts/mobile/publish-MotorDsl.<Nombre>-apk.bat` | Empaqueta APK firmado | uno por sample + `publish-all.bat` |

Fuente de la mecánica de ejecución: `samples/Readme.md#L242-L257 @83677eb`. Presencia de scripts
verificada en `scripts/local/` y `scripts/mobile/`.

> Precondiciones comunes: Android con depuración USB (BT es **Android-only**; en iOS los controles
> de impresión se ocultan por `OnPlatform`). Config de backend en `Resources/Raw/motordsl-config.json`
> (ver H3).

## 4. Patrón canónico recomendado

**`MotorDsl.Nuget.Integrated.MultaApp`** es el punto de partida recomendado para un proyecto nuevo,
porque combina las tres decisiones "de producción":

| Decisión | Valor canónico | Por qué |
|---|---|---|
| Formato DSL | **integrated** (`"format": "integrated"`) | El JSON llega con todos los valores resueltos; el motor salta la etapa Evaluate. Es el formato que produciría un backend que serializa el documento ya armado. |
| Consumo | **paquetes NuGet** (objetivo) | Valida los paquetes publicados, no el código local. *Hoy* usa project-ref temporal (H1). |
| Controles/servicios | `AddMotorDslMaui()` + `AddBluetoothPrinterTransport()` | Renderers (PDF, bitmap, Skia) y transporte BT provienen de la librería, no de carpetas copiadas en el sample. |
| Controles MAUI | `PrinterStatusBadge`, `PrinterPickerView`, `MauiRasterPreview` | UI de estado/selección/preview lista para usar, sin reimplementar el picker BT. |
| Extra (fase 4) | Logo por **recall NV** + firmas inline + selección de estrategia | Muestra el flujo de aprovisionar un logo en memoria no volátil y elegir `escpos` vs `escpos-bitmap` según capacidades. |

Registro DI canónico: `samples/MotorDsl.Nuget.Integrated.MultaApp/MauiProgram.cs#L29-L51 @83677eb`.
Snippet extraído con detalle en [`integration-snippets.md` §1](./integration-snippets.md#1-bootstrap-di-en-mauiprogram-canónico).

> **Advertencia (H1)**: pese al nombre, el csproj de este sample referencia los 7 proyectos
> `src/MotorDsl.*` por `<ProjectReference>` de forma temporal, porque la fase 4 usa API aún no
> publicada (`ProvisionLogoAsync`, `CurrentCapabilities`, `PrintStrategySelector`, `role` de imagen).
> El comentario del csproj indica volver a NuGet al republicar. Fuente:
> `samples/MotorDsl.Nuget.Integrated.MultaApp/MotorDsl.Nuget.Integrated.MultaApp.csproj#L72-L83 @83677eb`.

## 5. Dónde viven las plantillas DSL de ejemplo

Todas las plantillas son strings C# (raw string literals) en `Templates/*.cs` de cada sample.
**No** hay archivos `.json` sueltos con DSL; el único `.json` en `Resources/Raw/` es config de backend.

### 5.1 Formato classic (`{{placeholders}}` + `loop`/`conditional` + `GetSampleData()`)

| Archivo | Id de plantilla | Miembros clave |
|---|---|---|
| `samples/MotorDsl.SampleApp/Templates/TicketDsl.cs` | `ticket-venta-001` | `Template` (#L8), `GetSampleData()` (#L88) |
| `samples/MotorDsl.MultaApp/Templates/MultaDsl.cs` | `acta-infraccion-001` | `LogoBase64` (#L10), `FirmaBase64` (#L14), `Template` (#L17), `GetSampleData()` (#L176) |
| `samples/MotorDsl.MultaApp/Templates/TicketSimpleDsl.cs` | — | `Template` (#L8) |
| `samples/MotorDsl.MultaApp/Templates/ComprobanteDsl.cs` | — | `Template` (#L8) |
| `samples/MotorDsl.Nuget.MultaApp/Templates/{MultaDsl,TicketSimpleDsl,ComprobanteDsl}.cs` | ídem | copias de las de `MultaApp` |

### 5.2 Formato integrated (`"format": "integrated"`, valores resueltos, propiedad `value`)

| Archivo | Id documento | Miembros clave |
|---|---|---|
| `samples/MotorDsl.Integrated.MultaApp/Templates/MultaIntegratedDsl.cs` | `acta-infraccion-001` | `Document` (#L24), `"format"` en #L28 |
| `samples/MotorDsl.Integrated.MultaApp/Templates/{TicketSimple,Comprobante}IntegratedDsl.cs` | — | `Document` (#L9) |
| `samples/MotorDsl.Nuget.Integrated.MultaApp/Templates/MultaIntegratedDsl.cs` | `acta-infraccion-001` | `LogoBase64` **public** (#L13), `Document` (#L25), `"format"` en #L29 |
| `samples/MotorDsl.Nuget.Integrated.MultaApp/Templates/{TicketSimple,Comprobante}IntegratedDsl.cs` | — | `Document` (#L9) |

Fragmentos reales de cada formato en [`integration-snippets.md` §3](./integration-snippets.md#3-registro-de-una-plantilla-dsl-classic-e-integrated).

## 6. Permisos Android

Los 5 `AndroidManifest.xml` son **idénticos** (verificado). Declaran red (`INTERNET`,
`ACCESS_NETWORK_STATE`), Bluetooth legacy (`BLUETOOTH`, `BLUETOOTH_ADMIN`), BT Android 12+
(`BLUETOOTH_SCAN` con `neverForLocation`, `BLUETOOTH_CONNECT`) y ubicación para escaneo en < 12.
Snippet en [`integration-snippets.md` §6](./integration-snippets.md#6-permisos-android-androidmanifestxml).
Fuente ejemplo: `samples/MotorDsl.SampleApp/Platforms/Android/AndroidManifest.xml#L10-L31 @83677eb`.

## 7. Hallazgos

| # | Hallazgo | Fuente |
|---|---|---|
| H1 | `Nuget.Integrated.MultaApp` **no consume NuGet hoy**: usa `<ProjectReference>` a 7 proyectos por API no publicada (fase 4). El catálogo del índice lo describe como PackageReference (desactualizado). | `samples/MotorDsl.Nuget.Integrated.MultaApp/MotorDsl.Nuget.Integrated.MultaApp.csproj#L72-L83 @83677eb` |
| H2 | Los samples integrated registran solo `acta-infraccion-integrada` en el catálogo del engine; los otros 2 documentos integrated se pasan a `Render` directamente desde la página, sin registrarse. | `samples/MotorDsl.Nuget.Integrated.MultaApp/MauiProgram.cs#L30-L33` vs `Pages/MainPage.xaml.cs#L45-L50 @83677eb` |
| H3 | `Resources/Raw/motordsl-config.json` apunta a una IP pública como `backendBaseUrl`; un script la reescribe al publicar. | índice `06_samples.md#L262`, `samples/.../Resources/Raw/motordsl-config.json @83677eb` |
| H4 | Los assets del acta (logo, firma) son **BMP** base64 (magic `Qk0`), aunque los comentarios los llaman "PNG". | `samples/MotorDsl.Nuget.Integrated.MultaApp/Templates/MultaIntegratedDsl.cs#L11-L18 @83677eb` |
| H5 | **Enlace al glosario**: el encargo indicó `../../../GLOSSARY.md`, pero el glosario resuelve realmente en `../../GLOSSARY.md` desde `pieces/samples/` (`GLOSSARY.md` está en la raíz de `PrintThermal_Motor_Maui-docs/`). Se usa la ruta correcta, siguiendo la misma decisión del piece `MotorDsl.Core`. | `PrintThermal_Motor_Maui-docs/GLOSSARY.md`; convención en `pieces/MotorDsl.Core/README.md#L111-L115` |

## 8. Enlaces

| Recurso | Ruta |
|---|---|
| Corpus de snippets de integración | [`integration-snippets.md`](./integration-snippets.md) |
| Índice — samples | [`06_samples.md`](../../../ia-db/indexes/06_samples.md) |
| Índice — DSL y modelos | [`02_dsl-y-modelos.md`](../../../ia-db/indexes/02_dsl-y-modelos.md) |
| Glosario de la solución | [`GLOSSARY.md`](../../GLOSSARY.md) |
