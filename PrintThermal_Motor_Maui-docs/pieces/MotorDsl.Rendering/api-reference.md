---
doc_id: MotorDsl.Rendering-api-reference
doc_type: api-reference
title: MotorDsl.Rendering — Referencia de API
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

# MotorDsl.Rendering — Referencia de API

> Superficie pública del paquete `MotorDsl.Rendering`. Firmas verificadas contra
> **v1.0.13 @83677eb**.

## Superficie pública

### `TextRenderer : IRenderer`

| Miembro | Firma | Propósito | Archivo |
|---|---|---|---|
| `TextRenderer` (clase) | `public class TextRenderer : IRenderer` | Renderer de texto plano | `src/MotorDsl.Rendering/TextRenderer.cs#L12 @83677eb` |
| `Target` | `public string Target => "text"` | Identidad del renderer en el registry | `TextRenderer.cs#L14 @83677eb` |
| `Render` | `public RenderResult Render(LayoutedDocument document, DeviceProfile profile)` | Texto plano; `Output` es `string`, cada línea padeada a `profile.Width` | `TextRenderer.cs#L16 @83677eb` |

### `EscPosRenderer : IRenderer`

| Miembro | Firma | Propósito | Archivo |
|---|---|---|---|
| `EscPosRenderer` (clase) | `public class EscPosRenderer : IRenderer` | Renderer ESC/POS sin dependencias externas | `src/MotorDsl.Rendering/EscPosRenderer.cs#L13 @83677eb` |
| ctor | `public EscPosRenderer(IBitmapRasterizer? rasterizer = null)` | Rasterizador opcional; sin él, los bitmaps degradan a `"[BITMAP]"` | `EscPosRenderer.cs#L17 @83677eb` |
| `Target` | `public string Target => "escpos"` | Identidad en el registry | `EscPosRenderer.cs#L22 @83677eb` |
| `Render` | `public RenderResult Render(LayoutedDocument document, DeviceProfile profile)` | `byte[]` de comandos ESC/POS; `Output` es `byte[]` | `EscPosRenderer.cs#L24 @83677eb` |

### `EscPosCommands` (static)

| Miembro | Firma | Propósito | Archivo |
|---|---|---|---|
| `Init` | `public static readonly byte[]` | ESC @ — inicializar | `EscPosCommands.cs#L11 @83677eb` |
| `AlignLeft` / `AlignCenter` / `AlignRight` | `public static readonly byte[]` | ESC a n — alineación | `EscPosCommands.cs#L14-L20 @83677eb` |
| `StyleNormal` / `StyleBold` | `public static readonly byte[]` | ESC ! n — estilo (bold on/off) | `EscPosCommands.cs#L23-L26 @83677eb` |
| `CutFull` / `CutPartial` | `public static readonly byte[]` | GS V n — corte total / parcial | `EscPosCommands.cs#L29-L32 @83677eb` |
| `LineFeed` | `public static readonly byte[]` | LF | `EscPosCommands.cs#L35 @83677eb` |
| `FeedLines` | `public static byte[] FeedLines(byte n)` | ESC d n — alimentar n líneas | `EscPosCommands.cs#L38 @83677eb` |
| `BarcodeEan13` | `public static readonly byte[]` | GS k 2 — EAN-13 (prefijo) | `EscPosCommands.cs#L43 @83677eb` |
| `QrStoreData` / `QrSetSize3` / `QrSetErrorM` / `QrPrint` | `public static readonly byte[]` | GS ( k — secuencia QR | `EscPosCommands.cs#L48-L57 @83677eb` |
| `BuildRasterImageGsV0` | `public static byte[] BuildRasterImageGsV0(byte[] bits, int widthBytes, int heightDots)` | GS v 0 m=0 — raster bit image (header 8 bytes + bits) | `EscPosCommands.cs#L66 @83677eb` |
| `RecallNvGraphicsGsL` | `public static byte[] RecallNvGraphicsGsL(int keycode)` | GS ( L fn 69 — recall NV graphics por keycode | `EscPosCommands.cs#L84 @83677eb` |
| `RecallNvBitImageFsP` | `public static byte[] RecallNvBitImageFsP(int imageNumber, byte mode = 0x00)` | FS p n m — recall NV bit image clásica | `EscPosCommands.cs#L94 @83677eb` |

## Snippet — `TextRenderer.Render` (núcleo)

```csharp
public RenderResult Render(LayoutedDocument document, DeviceProfile profile)
{
    var result = new RenderResult("text");
    if (document == null || document.Root == null) { result.Output = ""; return result; }

    var output = new StringBuilder();
    var orderedEntries = document.NodeLayoutInfo
        .Where(kvp => !string.IsNullOrEmpty(kvp.Value.WrappedText))
        .OrderBy(kvp => kvp.Value.LineNumber)
        .ThenBy(kvp => kvp.Value.ColumnNumber);

    foreach (var kvp in orderedEntries)
        output.AppendLine(ApplyAlignment(kvp.Value.WrappedText, kvp.Value.Alignment, profile.Width));

    result.Output = output.ToString();
    return result;
}
```

Procedencia: `src/MotorDsl.Rendering/TextRenderer.cs#L16-L44 @83677eb`.

## Snippet — `EscPosRenderer.Render` (init + rama de texto + corte)

```csharp
buffer.AddRange(EscPosCommands.Init);          // ESC @
buffer.AddRange(new byte[] { 0x1B, 0x74, 0x00 }); // ESC t 0 — codepage PC437
// … por cada entrada (QR / barcode / bitmap / texto) …

buffer.AddRange(GetAlignmentCommand(layoutInfo.Alignment));
bool isBold = layoutInfo.DeviceMetadata.TryGetValue("bold", out var bv) && bv is true;
if (isBold) buffer.AddRange(EscPosCommands.StyleBold);
buffer.AddRange(EncodeText(layoutInfo.WrappedText ?? ""));   // CP437
if (isBold) buffer.AddRange(EscPosCommands.StyleNormal);
buffer.AddRange(EscPosCommands.LineFeed);

// … fin del loop …
buffer.AddRange(EscPosCommands.CutFull);       // GS V 0
```

Procedencia: `src/MotorDsl.Rendering/EscPosRenderer.cs#L32-L107 @83677eb` (condensado).

## Snippet — encoding (texto CP437 fijo vs QR/barcode por capability)

```csharp
private static byte[] EncodeText(string text) =>
    (System.Text.CodePagesEncodingProvider.Instance.GetEncoding(437)
        ?? System.Text.Encoding.ASCII).GetBytes(text);

private static Encoding GetEncoding(DeviceProfile profile) =>
    profile.GetCapability("codepage")?.ToString() switch
    {
        "850" => Encoding.GetEncoding(850),
        "437" => Encoding.GetEncoding(437),
        _     => Encoding.ASCII
    };
```

Procedencia: `src/MotorDsl.Rendering/EscPosRenderer.cs#L121-L145 @83677eb`.

## Snippet — `BuildRasterImageGsV0`

```csharp
public static byte[] BuildRasterImageGsV0(byte[] bits, int widthBytes, int heightDots)
{
    var cmd = new byte[8 + bits.Length];
    cmd[0]=0x1D; cmd[1]=0x76; cmd[2]=0x30; cmd[3]=0x00;        // GS v 0, m=0
    cmd[4]=(byte)(widthBytes & 0xFF); cmd[5]=(byte)((widthBytes >> 8) & 0xFF);
    cmd[6]=(byte)(heightDots & 0xFF); cmd[7]=(byte)((heightDots >> 8) & 0xFF);
    Array.Copy(bits, 0, cmd, 8, bits.Length);
    return cmd;
}
```

Procedencia: `src/MotorDsl.Rendering/EscPosCommands.cs#L66-L76 @83677eb`.

## Comportamiento de error

| Renderer | Condición | Resultado | Fuente |
|---|---|---|---|
| `TextRenderer` | `document`/`Root` null | `Output = ""`, sin error | `TextRenderer.cs#L22-L26 @83677eb` |
| `TextRenderer` | excepción interna | `RenderResult` con error `"Text rendering failed: …"`, `Output = ""` | `TextRenderer.cs#L46-L52 @83677eb` |
| `EscPosRenderer` | excepción interna | `RenderResult` con error `"ESC/POS rendering failed: …"`, `Output = byte[0]` | `EscPosRenderer.cs#L112-L118 @83677eb` |
| `EscPosRenderer` | bitmap sin rasterizador / error rasterizando | placeholder ASCII `"[BITMAP]"` + LF (no aborta el ticket) | `EscPosRenderer.cs#L195-L223 @83677eb` |

## 🤖 Para agentes

- **Los renderers no recorren el AST**: iteran `document.NodeLayoutInfo` filtrando `WrappedText` no
  vacío y ordenando por `LineNumber`, luego `ColumnNumber`. La decisión QR/barcode/bitmap/texto sale
  de `LayoutInfo.DeviceMetadata` (`is_qr`, `is_barcode`, `is_bitmap`, `bold`, `image_role`), que
  llena el `LayoutEngine` (ver [ia-db 02 §4.1](../../../ia-db/indexes/02_dsl-y-modelos.md)).
- **Tipo de `Output`**: `string` para `TextRenderer`, `byte[]` para `EscPosRenderer`. Para `escpos`
  usa `RenderResult.ToHexString()` / `ToBase64()` (solo válidos cuando `Output is byte[]`).
- **Texto ESC/POS = CP437 fijo**: `EncodeText` **ignora** la capability `codepage` y las propiedades
  `CodePage`/`CodePageCommand` de `DeviceProfile`; solo QR/barcode respetan `codepage`. No asumas
  que cambiar `codepage` altera el texto.
- **Sin padding en ESC/POS**: a diferencia de `TextRenderer`, el `EscPosRenderer` no padea ni trunca
  al ancho — confía en el wrap del `LayoutEngine` (`EscPosRenderer.cs#L95 @83677eb`).
- **Barcode**: solo EAN-13 (`GS k 2`), sin validar dígitos ni usar `DeviceProfile.SupportedBarcodes`
  (`EscPosRenderer.cs#L168-L178 @83677eb`).
- **Bitmaps reales requieren `IBitmapRasterizer`** por constructor. El `EscPosRenderer` que registra
  `AddMotorDslEngine` se instancia **sin** rasterizador → para bitmaps hay que registrar un renderer
  propio (ver pieza `MotorDsl.Extensions`).
- **Constantes sin consumidor** en estos proyectos: `QrStoreData`, `CutPartial`, `FeedLines`
  (`EscPosCommands.cs @83677eb`). Útiles para transports externos, «No verificado» aquí.
