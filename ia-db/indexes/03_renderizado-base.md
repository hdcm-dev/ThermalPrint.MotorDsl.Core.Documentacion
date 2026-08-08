# 03 — Renderizado base y extensibilidad

> **Propósito**: los renderers que viven en `MotorDsl.Rendering` (`text` y `escpos`), el catálogo
> de comandos ESC/POS, cómo se registran los renderers y cómo agregar uno propio.
> **Fuentes primarias**: `src/MotorDsl.Rendering/{TextRenderer,EscPosRenderer,EscPosCommands}.cs`,
> `src/MotorDsl.Core/Engine/RendererRegistry.cs`, `src/MotorDsl.Extensions/`,
> `docs/05_arquitectura_tecnica/extensibilidad-motor_v1.1.md`.
> Los renderers de `MotorDsl.Maui` (`pdf`, `escpos-bitmap`, `raster-preview`) están en
> [05_maui-ui-renderers](05_maui-ui-renderers.md).

---

## 1. El contrato `IRenderer`

```csharp
public interface IRenderer
{
    string Target { get; }                                        // "escpos", "pdf", "text", …
    RenderResult Render(LayoutedDocument document, DeviceProfile profile);
}
```

Un renderer recibe el documento **ya maquetado** (líneas, alineación, wrap y `DeviceMetadata`
resueltos por `LayoutEngine`) y solo traduce a su formato de salida. No parsea, no evalúa
bindings, no conoce los datos originales ni el transport.

`Target` es el discriminador: `DeviceProfile.RenderTarget` decide qué renderer se invoca.

---

## 2. Catálogo de targets

| `Target` | Renderer | Paquete | `Output` | Registro |
|---|---|---|---|---|
| `text` | `TextRenderer` | Rendering | `string` | siempre (`AddMotorDslEngine`) |
| `escpos` | `EscPosRenderer` | Rendering | `byte[]` | siempre (`AddMotorDslEngine`) |
| `escpos-bitmap` | `BitmapEscPosRenderer` | Maui | `byte[]` | `AddMotorDslMaui()` |
| `pdf` | `PdfRenderer` | Maui | `byte[]` | `AddMotorDslMaui()` |
| `raster-preview` | `RasterPreviewRenderer` | Maui | `byte[]` (PNG) | `AddMotorDslMaui()` |

---

## 3. `TextRenderer` — target `text`

Salida `string` legible, pensada para depuración y para comparar en tests. Recorre
`NodeLayoutInfo` ordenado por `LineNumber` y luego `ColumnNumber`, descartando entradas sin
`WrappedText`, y aplica alineación **por relleno de espacios** a `profile.Width`:

- `left`: `PadRight(width)`; si el texto excede, **trunca** desde el inicio.
- `right`: `PadLeft(width)`; si excede, conserva los últimos `width` caracteres.
- `center`: reparte el padding, con el sobrante a la derecha.

Ante excepción devuelve `RenderResult` con error y `Output = ""` (no lanza).

---

## 4. `EscPosRenderer` — target `escpos`

Emite `byte[]` con comandos ESC/POS **sin dependencias externas** (no usa ESCPOS_NET ni similar).
Acepta opcionalmente un `IBitmapRasterizer` por constructor; si no lo recibe, las imágenes
bitmap caen a un placeholder textual.

### Secuencia de salida

1. `ESC @` — inicializar impresora.
2. `ESC t 0` — seleccionar codepage PC437.
3. Por cada entrada de `NodeLayoutInfo` con texto, ordenada por línea y columna, se despacha
   **en este orden de prioridad**:

   | Condición en `DeviceMetadata` | Emisión |
   |---|---|
   | `is_qr` | secuencia `GS ( k`: tamaño de módulo 3, corrección M, *store data*, *print* |
   | `is_barcode` | `GS k 2` (EAN-13, modo 2) + datos + terminador `NUL` |
   | `is_bitmap` y `image_role == "logo"` y el perfil tiene `nv_logo_keycode` | *recall* del logo desde memoria NV (pocos bytes, sin rasterizar) |
   | `is_bitmap` (resto, incluidas las firmas) | rasterizado inline → `GS v 0` |
   | texto | comando de alineación → `ESC ! 8` si `bold` → texto codificado → `ESC ! 0` si venía bold → `LF` |

4. `GS V 0` — corte total de papel.

### Codificación de caracteres

El texto se codifica en **CP437** vía `CodePagesEncodingProvider` (fallback a ASCII), que ubica
los caracteres españoles en las posiciones correctas. Para QR y códigos de barras, el encoding se
toma de la capacidad `codepage` del perfil (`"437"`, `"850"`; si no hay, ASCII).

### Ruteo del logo NV

El renderer **no conoce el transport ni las capacidades reales de la impresora**: solo lee del
`DeviceProfile` lo que la app haya seteado (`nv_logo_keycode`, `nv_logo_kind`). Si
`nv_logo_kind == "fs"` emite `FS p` (NV bit image clásica por número); en cualquier otro caso
emite `GS ( L` función 69 (*recall* por keycode, escala 1×1). Aprovisionar ese logo es
responsabilidad del transport — ver [04_impresion-transports](04_impresion-transports.md).

Ante excepción devuelve error y `Output = Array.Empty<byte>()`.

---

## 5. `EscPosCommands` — catálogo de comandos

`src/MotorDsl.Rendering/EscPosCommands.cs` centraliza los bytes crudos:

| Constante / método | Bytes | Significado |
|---|---|---|
| `Init` | `1B 40` | `ESC @` — inicializar |
| `AlignLeft` / `AlignCenter` / `AlignRight` | `1B 61 00/01/02` | `ESC a n` |
| `StyleBold` / `StyleNormal` | `1B 21 08` / `1B 21 00` | `ESC ! n` |
| `CutFull` / `CutPartial` | `1D 56 00` / `1D 56 01` | `GS V n` |
| `LineFeed` | `0A` | `LF` |
| `FeedLines(n)` | `1B 64 n` | `ESC d n` |
| `BarcodeEan13` | `1D 6B 02` | `GS k 2` |
| `QrSetSize3`, `QrSetErrorM`, `QrStoreData`, `QrPrint` | `1D 28 6B …` | `GS ( k` |
| `BuildRasterImageGsV0(bits, widthBytes, heightDots)` | `1D 76 30 00 xL xH yL yH` + bits | `GS v 0` — imagen raster |
| `RecallNvGraphicsGsL(keycode)` | `1D 28 4C 06 00 30 45 kc1 kc2 01 01` | `GS ( L` fn 69 — recall NV |
| `RecallNvBitImageFsP(n, mode)` | `1C 70 n m` | `FS p` — recall NV clásico |

`BuildRasterImageGsV0` es el **formato común** entre la imagen inline y el aprovisionamiento del
logo en NV: el mismo `byte[]` sirve para ambos caminos.

---

## 6. Registro y resolución

`RendererRegistry` (`src/MotorDsl.Core/Engine/RendererRegistry.cs`) es un diccionario
`Target → IRenderer` con `Register(IRenderer)`, `GetRenderer(target)` y `GetAvailableTargets()`.

`AddMotorDslEngine()` lo construye con una factory que:

1. registra `TextRenderer` y `EscPosRenderer`;
2. resuelve **todos** los `IRenderer` del contenedor (`sp.GetServices<IRenderer>()`) y los registra.

Consecuencia práctica: registrar un `IRenderer` en DI —directamente o vía `AddRenderer<T>()`—
alcanza para que quede disponible. Registrar uno con un `Target` ya existente lo **sobrescribe**.

Si `DeviceProfile.RenderTarget` no tiene renderer, `DocumentEngine` produce un `RenderResult` con
el error `"No renderer found for target: <target>"`.

---

## 7. Cómo agregar un renderer propio

```csharp
public class CsvRenderer : IRenderer
{
    public string Target => "csv";

    public RenderResult Render(LayoutedDocument document, DeviceProfile profile)
    {
        var result = new RenderResult("csv");
        // recorrer document.NodeLayoutInfo ordenado por LineNumber / ColumnNumber
        result.Output = /* string o byte[] */;
        return result;
    }
}

builder.Services.AddMotorDslEngine()
    .AddRenderer<CsvRenderer>()
    .AddProfiles(p => p.Add(new DeviceProfile("export-csv", 80, "csv")));
```

Convenciones a respetar (observadas en los renderers existentes):

- Ordenar por `LineNumber` y luego `ColumnNumber`; ignorar entradas sin `WrappedText`.
- Consultar `DeviceMetadata` antes que el texto: `is_qr`, `is_barcode`, `is_bitmap` indican que la
  entrada **no** es texto plano.
- Capturar toda excepción y devolverla como `Errors` del `RenderResult` con un `Output` vacío
  coherente con el tipo, en lugar de propagar.
- No asumir que existe un `IBitmapRasterizer`: hacerlo opcional y degradar con un warning.

Guía extendida: `docs/05_arquitectura_tecnica/extensibilidad-motor_v1.1.md`
(`_v1.0.md` es la versión histórica).

---

## 8. Fuentes

| Tema | Archivo |
|---|---|
| Renderer de texto | `src/MotorDsl.Rendering/TextRenderer.cs` |
| Renderer ESC/POS | `src/MotorDsl.Rendering/EscPosRenderer.cs` |
| Comandos ESC/POS | `src/MotorDsl.Rendering/EscPosCommands.cs` |
| Registro de renderers | `src/MotorDsl.Core/Engine/RendererRegistry.cs`, `src/MotorDsl.Extensions/MotorDslServiceCollectionExtensions.cs` |
| Extensibilidad (guía) | `docs/05_arquitectura_tecnica/extensibilidad-motor_v1.1.md`, `docs/10_developer_guide/transports-y-extensibilidad.md` |
| Tests | `src/MotorDsl.Tests/{EscPosRendererTests,TextRendererTests,QrEscPosTests,BarcodeEscPosTests,TableNodeEscPosTests,RendererRegistryTests}.cs` |
