# 03 — Renderizado base

> **Propósito**: qué renderers existen, qué produce cada uno, qué bytes ESC/POS se emiten y cómo
> escribir un renderer propio.
> **Fuentes primarias**: `src/MotorDsl.Rendering/` (`EscPosRenderer.cs`, `TextRenderer.cs`,
> `EscPosCommands.cs`), `src/MotorDsl.Core/Contracts/IRenderer.cs`,
> `docs/05_arquitectura_tecnica/extensibilidad-motor_v1.1.md`.

---

## 1. Catálogo de renderers

| `Target` | Clase | Paquete | `Output` |
|---|---|---|---|
| `text` | `TextRenderer` | Rendering | `string` |
| `escpos` | `EscPosRenderer` | Rendering | `byte[]` |
| `escpos-bitmap` | `BitmapEscPosRenderer` | Maui | `byte[]` |
| `pdf` | `PdfRenderer` | Maui | `byte[]` |
| `raster-preview` | `RasterPreviewRenderer` | Maui | `byte[]` (PNG) |

Los dos primeros se registran siempre en `AddMotorDslEngine()`; los tres de MAUI, al llamar
`AddMotorDslMaui()`. Detalle de los de MAUI en [`05_maui-ui-renderers.md`](05_maui-ui-renderers.md).

El `Target` se elige por `DeviceProfile.RenderTarget`, no por parámetro del método: cambiar de
salida es cambiar de perfil.

---

## 2. El contrato

```csharp
public interface IRenderer
{
    string Target { get; }
    RenderResult Render(LayoutedDocument document, DeviceProfile profile);
}
```

Ambos renderers de este paquete comparten el mismo patrón de recorrido:

```csharp
document.NodeLayoutInfo
    .Where(kvp => !string.IsNullOrEmpty(kvp.Value.WrappedText))
    .OrderBy(kvp => kvp.Value.LineNumber)
    .ThenBy(kvp => kvp.Value.ColumnNumber)
```

Consecuencia directa: **lo que no tiene `WrappedText` no se imprime**, aunque exista en el árbol.

Ambos envuelven todo en un `try/catch` que devuelve un `RenderResult` con error y `Output` vacío
(`""` o `byte[0]`) en lugar de propagar la excepción.

---

## 3. `TextRenderer`

Fuente: [`src/MotorDsl.Rendering/TextRenderer.cs`](../../../PrintThermal_Motor_Maui/src/MotorDsl.Rendering/TextRenderer.cs).

Emite un `string` con una línea por entrada, alineada a `profile.Width`. Las líneas se **rellenan
con espacios hasta el ancho completo** y las que exceden se **truncan** con `Substring(0, width)` —
tanto en `left` como en `center`/`right`.

Un `document.Root == null` devuelve `Output = ""` sin error.

Uso típico: depuración y tests. Es también el destino del fallback de `RendererRegistry`, así que
un `Target` inexistente termina produciendo texto plano en vez de fallar.

---

## 4. `EscPosCommands` — la tabla de bytes

Fuente: [`src/MotorDsl.Rendering/EscPosCommands.cs`](../../../PrintThermal_Motor_Maui/src/MotorDsl.Rendering/EscPosCommands.cs).

| Constante | Bytes | Comando |
|---|---|---|
| `Init` | `1B 40` | ESC @ |
| `AlignLeft` / `AlignCenter` / `AlignRight` | `1B 61 00/01/02` | ESC a n |
| `StyleNormal` / `StyleBold` | `1B 21 00/08` | ESC ! n |
| `CutFull` / `CutPartial` | `1D 56 00/01` | GS V m |
| `LineFeed` | `0A` | LF |
| `FeedLines(n)` | `1B 64 n` | ESC d n |
| `BarcodeEan13` | `1D 6B 02` | GS k 2 |
| `QrSetSize3` | `1D 28 6B 03 00 31 43 03` | GS ( k — módulo tamaño 3 |
| `QrSetErrorM` | `1D 28 6B 03 00 31 45 33` | GS ( k — corrección M |
| `QrStoreData` / `QrPrint` | `1D 28 6B …` | almacenar / imprimir |
| `BuildRasterImageGsV0(bits, wBytes, hDots)` | `1D 76 30 00 xL xH yL yH …` | GS v 0 |
| `RecallNvGraphicsGsL(keycode)` | `1D 28 4C 06 00 30 45 kc1 kc2 01 01` | GS ( L — recall NV |
| `RecallNvBitImageFsP(n, mode)` | `1C 70 n mode` | FS p — recall NV legacy |

Solo hay **recall** de logos NV en esta tabla; definir, consultar y borrar viven en el transport
Bluetooth (ver [`04_impresion-transports.md`](04_impresion-transports.md)).

---

## 5. `EscPosRenderer` — el ensamblado de la tira

Fuente: [`src/MotorDsl.Rendering/EscPosRenderer.cs`](../../../PrintThermal_Motor_Maui/src/MotorDsl.Rendering/EscPosRenderer.cs) (244 líneas).

Estructura de la salida:

```text
ESC @              inicializar
1B 74 00           seleccionar codepage PC437 (fijo, no configurable)
  ── por cada entrada con WrappedText, en orden de línea ──
  QR        → GS ( k (tamaño, corrección, datos, imprimir)
  barcode   → GS k 2 + datos + NUL
  bitmap    → recall NV (si role="logo" y hay keycode) o GS v 0 inline
  texto     → ESC a n · [ESC ! 08] · bytes CP437 · [ESC ! 00] · LF
GS V 0             corte completo
```

### Decisiones de codificación

El texto se codifica siempre en **CP437** vía `CodePagesEncodingProvider`, con `ASCII` como
fallback. El acompañante `1B 74 00` al inicio le dice a la impresora que interprete esa tabla —es la
combinación que hace salir bien los acentos del español.

Pero `GetEncoding(profile)` —que sí mira la capacidad `codepage` y admite `437`, `850` o `ASCII`—
**solo se usa para los datos de QR y de barcode**, no para el texto del documento. Es una asimetría
real del código: la capacidad `codepage` no cambia cómo se codifica el cuerpo del ticket.

### Ruteo de imágenes

```text
is_bitmap = true
   ├── role == "logo" Y profile tiene "nv_logo_keycode"  → recall NV (pocos bytes)
   └── cualquier otro caso (incluye role == "signature") → GS v 0 inline
```

`EmitNvLogoRecall` elige entre `RecallNvBitImageFsP` y `RecallNvGraphicsGsL` según la capacidad
`nv_logo_kind` (`"fs"` o cualquier otro valor). El renderer **no conoce el transport ni las
capacidades detectadas**: solo lee del `DeviceProfile` lo que la app le puso — es lo que mantiene
`MotorDsl.Rendering` en `net10.0` puro y sin dependencias de plataforma.

### Comportamiento del bitmap inline

`EmitBitmap` recorta el prefijo `data:image/...;base64,`, lee `bitmap_max_width_px` (default 384) y
delega en el `IBitmapRasterizer` inyectado. Si **no hay rasterizador** o el base64 está vacío,
escribe el literal ASCII `[BITMAP]` y sigue. Cualquier excepción cae al mismo placeholder: este
renderer **degrada en silencio**, a diferencia de `BitmapEscPosRenderer`, que aborta con un error
preciso (ver índice 05). El bitmap se emite centrado y vuelve a `AlignLeft` después.

`EscPosRenderer` recibe el rasterizador por constructor opcional (`IBitmapRasterizer? = null`), y
el registro por defecto en `AddMotorDslEngine()` lo construye **sin** rasterizador — de ahí que una
app que quiera imágenes reales use `escpos-bitmap`.

---

## 6. Escribir un renderer propio

```csharp
public class MiRenderer : IRenderer
{
    public string Target => "mi-formato";

    public RenderResult Render(LayoutedDocument document, DeviceProfile profile)
    {
        var result = new RenderResult(Target);
        foreach (var kvp in document.NodeLayoutInfo
                     .Where(k => !string.IsNullOrEmpty(k.Value.WrappedText))
                     .OrderBy(k => k.Value.LineNumber))
        {
            // kvp.Value.Alignment, .DeviceMetadata["bold"], ["is_qr"], ["is_bitmap"], …
        }
        result.Output = /* string o byte[] */;
        return result;
    }
}
```

Registro: `builder.AddRenderer<MiRenderer>()`. Para usarlo, un perfil con
`RenderTarget = "mi-formato"`.

Reglas a respetar, tomadas de los renderers existentes:

- No lanzar: capturar y devolver `RenderResult` con `Errors`.
- Distinguir severidad: lo que impide imprimir es `Error` con `Output` vacío; lo que degrada la
  calidad es `Warning` con la salida igual emitida.
- Leer `DeviceMetadata` para QR (`is_qr`/`qr_data`), barcode (`is_barcode`/`barcode_data`), bitmap
  (`is_bitmap`/`bitmap_source`/`bitmap_width`/`image_role`) y `bold`.
- Un `Target` que colisione con uno existente lo reemplaza silenciosamente en el registry.

Guía extensa: `docs/05_arquitectura_tecnica/extensibilidad-motor_v1.1.md`.

---

## 7. Cobertura y límites conocidos

- Tests de este paquete: `EscPosRendererTests`, `TextRendererTests`, `QrEscPosTests`,
  `BarcodeEscPosTests`, `TableNodeEscPosTests` (ver [`07_tests.md`](07_tests.md)).
- El único simbolismo de código de barras implementado es **EAN-13**; no hay Code128, Code39 ni
  QR con niveles de corrección configurables desde el DSL.
- El corte de papel es siempre `CutFull`: `CutPartial` está definido pero no se emite nunca.
- El tamaño de módulo QR es fijo (3) y la corrección fija (M).
