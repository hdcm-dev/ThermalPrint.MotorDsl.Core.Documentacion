---
doc_id: GLOSSARY-001
doc_type: glossary
title: Glosario — MotorDsl
version: 1.0.0
status: draft
origin: reverse-engineered
confidence: high
owner: equipo-motordsl
last_review: 2026-07-14
audience: [dev, arquitectura, qa, agentes-automaticos]
classification: uso-interno
source_ref: v1.0.13 @83677eb
---

# Glosario — MotorDsl

> Vocabulario controlado y normativo de la solución. Humanos y agentes usan estos términos; los
> sinónimos se registran como `alias` del término canónico. Cada entrada cita su fuente en el
> origen (**v1.0.13 @83677eb**). Ordenado alfabéticamente.

## Conceptos del pipeline y el DSL

| Término | Definición | Fuente |
|---|---|---|
| **DSL** | *Domain Specific Language* JSON de MotorDsl que describe un documento (contenedores, texto, tablas, imágenes, loops y condicionales). Se parsea a un `DocumentTemplate`. | `src/MotorDsl.Parser/DslParser.cs` |
| **Formato classic** (alias: `template`) | Modalidad del DSL (`format: "template"`, default) con placeholders `{{…}}`, `loop` y `conditional`, resueltos por el `Evaluator` contra datos externos (`IDataProvider`). Invocación de 3 args: `Render(template, data, profile)`. | `src/MotorDsl.Core/Models/DocumentTemplate.cs#L11-L12` |
| **Formato integrated** | Modalidad del DSL (`format: "integrated"`) con AST **pre-resuelto** y datos embebidos; se **salta la etapa Evaluate** y se prohíben placeholders/loops/conditionals. Invocación de 2 args: `Render(json, profile)`. | `src/MotorDsl.Core/Engine/DocumentEngine.cs#L139-L216` |
| **Pipeline** | Cadena `JSON → Parser → Evaluator → LayoutEngine → Renderer → RenderResult`. En *integrated* se omite `Evaluator`. | `src/MotorDsl.Core/Engine/DocumentEngine.cs` |
| **`DocumentTemplate`** | AST del documento producido por el parser: metadatos (`format`, `Id`, `Version`) + árbol de nodos. | `src/MotorDsl.Core/Models/DocumentTemplate.cs` |
| **`LayoutedDocument`** | Representación intermedia `Evaluator/LayoutEngine → Renderer`: diccionario `node_N → LayoutInfo` con texto ya *wrapeado* y `DeviceMetadata`; los renderers **no** recorren el AST. | `src/MotorDsl.Core/Models/LayoutedDocument.cs#L7-L16` |
| **`DeviceMetadata`** | Diccionario por nodo que `LayoutEngine` llena (`bold`, `is_qr`, `is_barcode`, `is_bitmap`, `image_role`, `qr_data`, `bitmap_source`…) y los renderers consumen para discriminar cómo dibujar cada nodo. | `src/MotorDsl.Core/Layout/LayoutEngine.cs#L58-L169` |
| **`DeviceProfile`** | Perfil de salida: `Name`, ancho en columnas (`Width`), `RenderTarget` (`escpos`, `escpos-bitmap`, `pdf`, `text`, `raster-preview`) y *capabilities*. Selecciona el renderer en el registry. | `src/MotorDsl.Core/Models/DeviceProfile.cs` |
| **`RenderResult`** | Resultado del pipeline: `Output` (string o `byte[]`), `IsSuccessful`, `Errors`, `Warnings`. | `src/MotorDsl.Core/Models/RenderResult.cs` |
| **`{{UNRESOLVED:path}}`** | Marcador que el `Evaluator` inserta en el texto cuando un placeholder *classic* no resuelve contra los datos. | `src/MotorDsl.Core/Evaluators/Evaluator.cs#L150-L160` |
| **Degradación por capability** | Si una `capability` (`supports_qr`, `supports_bitmap`…) está explícitamente en `false`, el nodo QR/barcode/bitmap se degrada a texto placeholder + *warning*. | `src/MotorDsl.Core/Layout/LayoutEngine.cs#L117-L182` |

## Conceptos de renderizado

| Término | Definición | Fuente |
|---|---|---|
| **Renderer** | Implementación de `IRenderer` que transforma un `LayoutedDocument` + `DeviceProfile` en bytes de salida (`RenderResult.Output`). | `src/MotorDsl.Core/Contracts/IRenderer.cs` |
| **Target** | String que identifica a un `IRenderer` en el `RendererRegistry`; la app (o `PrintStrategySelector`) elige el renderer por él. | `src/MotorDsl.Core/Contracts/IRenderer.cs`, `Renderers/*.cs` |
| **Rasterizer** | Convierte una fuente de imagen (base64) o payload QR en raster 1-bit / `SKBitmap`. **No** es un renderer. | `src/MotorDsl.Maui/Renderers/SkiaSharpRasterizer.cs#L13` |
| **`RasterizedImage`** | Struct de `MotorDsl.Core`: `Bits` empaquetados + `WidthBytes` + `HeightDots`, en el formato que consume `GS v 0`. | `src/MotorDsl.Core/Contracts/IBitmapRasterizer.cs` |
| **ESC/POS** | Lenguaje de comandos de impresoras térmicas (Epson Standard Code for Point of Sale) que emite `EscPosRenderer`. | `src/MotorDsl.Rendering/EscPosCommands.cs` |
| **`GS v 0`** | Comando raster inline ESC/POS (`1D 76 30 m xL xH yL yH [bits]`); formato de entrada único del aprovisionamiento de logo NV. | `src/MotorDsl.Rendering/EscPosCommands.cs`, `Contracts/IThermalPrinterTransport.cs#L19-L22` |
| **Fail-loud** | Política del renderer `escpos-bitmap`: ante una imagen irrecuperable **aborta el ticket** con un error preciso (que incluye el `source`) en vez de imprimir un ticket incompleto en silencio. | `src/MotorDsl.Maui/Renderers/BitmapEscPosRenderer.cs#L60-L73` |
| **EmbeddedResource font** | `DroidSans-Regular.ttf` embebida en `MotorDsl.Maui`; única fuente del PDF y del raster preview. | `src/MotorDsl.Maui/MotorDsl.Maui.csproj#L44-L46` |

## Conceptos de impresión / transporte

| Término | Definición | Fuente |
|---|---|---|
| **Transport** | Implementación de `IThermalPrinterTransport`: capa física de **un** medio; solo mueve bytes y detecta capacidades, sin retry propio. | `src/MotorDsl.Bluetooth/BluetoothPrinterTransport.cs#L12-L16` |
| **Kind** | String que identifica el medio de transporte (`"bluetooth"`, `"usb"`, …); clave del enrutamiento del `ThermalPrinterService`. | `Contracts/IThermalPrinterTransport.cs#L7` |
| **`ThermalPrinterService`** | Orquestador/fachada de impresión: ciclo de vida de conexión, retry con backoff, eventos, enrutamiento por `Kind`, historial de fallos, diagnóstico. Implementa `INotifyPropertyChanged`. | `src/MotorDsl.Printing.Abstractions/Services/ThermalPrinterService.cs` |
| **`CapabilitySupport`** | Tri-estado deliberado (nunca `bool`): `Unknown` (no se sondeó), `NotDetected` (se sondeó sin respuesta), `Supported` (respondió confirmando). | `Models/CapabilitySupport.cs#L7-L17` |
| **`PrintStrategySelector`** | Helper puro que **recomienda** el `Target` según capacidades (`escpos` si hay NV graphics, si no `escpos-bitmap`); la decisión final es de la app. | `Models/PrintStrategySelector.cs#L7-L21` |
| **Status gating** | Consultar `DLE EOT n=1` antes de escribir un bloque y gatear la escritura por `Ready`/`Busy`. | `BluetoothPrinterTransport.cs#L194-L199` |
| **Degradación (latch)** | Tras un status ilegible (`Unknown`) el transport pasa a *pacing* fijo por el resto del envío, sin volver a consultar. | `BluetoothPrinterTransport.Capabilities.cs#L62-L78` |
| **Pacing** | Delay fijo por bloque como respaldo cuando no hay (o se degradó) el feedback de status. | `BluetoothPrinterTransport.cs#L190-L192` |
| **NV / keycode** (alias: recall NV) | Memoria no volátil de la impresora donde se define un logo direccionable por *keycode*; permite reimprimirlo sin reenviar los bits. | `BluetoothPrinterTransport.Nv.cs#L6-L19` |
| **ChunkBuffer** | Chunker de tamaño fijo (256 bytes) del transport BT; parte por tamaño y **no** por contenido, para que payloads bitmap con `0x0A` se reensamblen exactos. | `src/MotorDsl.Tests/ChunkBufferTests.cs#L6-L11` |
| **Ring buffer de fallos** | Historial acotado (20 entradas) de `PrintFailureEntry` en memoria, sin payload ni persistencia. | `Services/ThermalPrinterService.cs#L24-L27` |
| **PII masking** | Enmascarado de MAC (`xx:xx:xx:**:**:**`) aplicado al **construir** el reporte de diagnóstico, no al registrar el fallo. | `Models/DiagnosticsBuilder.cs#L16-L28` |

## Conceptos de build / release

| Término | Definición | Fuente |
|---|---|---|
| **Versión unificada** | Los 8 paquetes se publican siempre con la misma versión = `max(next(patch))`, para evitar el *downgrade* NU1605. | `docs/09_devops/estrategia-versionado_v1.0.md`; `scripts/nuget/notas.md` |
| **`MotorDslVersion`** | Propiedad MSBuild inyectada en build/pack para que los `.csproj` referencien la versión en los `PackageReference` internos. | `scripts/nuget/notas.md` |
| **Auto-bump de patch** | `get-next-version.ps1` consulta el *flat container* de nuget.org y devuelve `X.Y.(Z+1)`; *fallback* `1.0.0` si el paquete no existe. | `scripts/nuget/get-next-version.ps1` |
| **`EmbedAssembliesIntoApk`** | Flag obligatorio en el publish Android para que el APK firmado sea instalable vía `adb install`. | `scripts/mobile/Readme.md` |
| **local-nupkg** | Fuente NuGet local `./nupkg` declarada antes de nuget.org en `NuGet.config`, para probar paquetes recién empacados. | `NuGet.config`; `nupkg/Readme.md` |
