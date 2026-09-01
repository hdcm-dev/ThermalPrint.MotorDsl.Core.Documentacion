# 03 — Renderizado base y extensibilidad

> **Propósito**: documentar los renderers portables (`text` y `escpos`), la tabla de comandos
> ESC/POS que emiten, y cómo se agrega un renderer propio.
> **Fuentes primarias**: `src/MotorDsl.Rendering/` (`TextRenderer.cs`, `EscPosRenderer.cs`,
> `EscPosCommands.cs`), `src/MotorDsl.Extensions/`,
> `docs/05_arquitectura_tecnica/extensibilidad-motor_v1.1.md`.
>
> Los renderers **gráficos** (`escpos-bitmap`, `pdf`, `raster-preview`) viven en
> `MotorDsl.Maui` y se documentan en [05](05_maui-ui-renderers.md). El contrato `IRenderer` y
> el registry están en [01](01_nucleo-pipeline.md).

---

## 1. Los cinco targets

| `Target` | Renderer | Paquete | Tipo de `Output` |
|---|---|---|---|
| `text` | `TextRenderer` | `MotorDsl.Rendering` | `string` |
| `escpos` | `EscPosRenderer` | `MotorDsl.Rendering` | `byte[]` |
| `escpos-bitmap` | `BitmapEscPosRenderer` | `MotorDsl.Maui` | `byte[]` |
| `pdf` | `PdfRenderer` | `MotorDsl.Maui` | `byte[]` |
| `raster-preview` | `RasterPreviewRenderer` | `MotorDsl.Maui` | `byte[]` |

Los dos primeros se **prerregistran** en `AddMotorDslEngine()`; los tres de MAUI los agrega
`AddMotorDslMaui()`.

Un `DeviceProfile` apuntando a un target no registrado **no falla**: el registry cae a `text`.
Ver [01 §7](01_nucleo-pipeline.md).

---

## 2. Lo que ambos renderers tienen en común

Los dos recorren `LayoutedDocument.NodeLayoutInfo` —no el árbol— filtrando las entradas con
`WrappedText` no vacío y ordenando por `LineNumber` y luego `ColumnNumber`. El layout ya
resolvió el envolvido y la alineación; el renderer solo traduce a su formato de salida.

Los dos capturan toda excepción y devuelven un `RenderResult` con el error en `Errors` y una
salida vacía (`""` o `byte[0]`), en vez de propagar.

---

## 3. `TextRenderer` — target `text`

El más simple: por cada entrada aplica la alineación sobre el ancho del perfil
(`ApplyAlignment` → `LeftAlignText` / `CenterText` / `RightAlignText`, con soporte de saltos
internos) y agrega la línea al `StringBuilder`.

Su valor es doble: es la salida de depuración legible del pipeline, y es el **fallback** del
registry cuando un target no existe.

---

## 4. `EscPosRenderer` — target `escpos`

Emite el flujo de bytes que entiende una impresora térmica ESC/POS.

### Estructura del flujo

```text
ESC @            (init)
ESC t 0          (codepage PC437)
  … por cada entrada del layout …
GS V 0           (corte total)
```

### Ruteo por entrada

El renderer decide qué emitir mirando banderas que el `LayoutEngine` dejó en
`LayoutInfo.DeviceMetadata`:

| Bandera en `DeviceMetadata` | Emite |
|---|---|
| `is_qr` = true | Secuencia `GS ( k` con `qr_data` |
| `is_barcode` = true | Secuencia `GS k 2` (EAN-13) con `barcode_data`, terminada en NUL |
| `is_bitmap` = true | Recall de logo NV **o** imagen inline `GS v 0`, según §5 |
| ninguna | Comando de alineación + `ESC ! 8` si `bold` + texto en CP437 + `LF` |

El texto se codifica en **CP437** (`CodePagesEncodingProvider`), el codepage IBM original en
el que los caracteres del español caen en las posiciones correctas; si no está disponible, cae
a ASCII. Para QR y barcode el codepage se toma de la capacidad `codepage` del perfil (`437`,
`850`, o ASCII por defecto).

### Ruteo de imágenes (§5)

Una imagen con `role == "logo"` **y** un perfil que declare la capacidad `nv_logo_keycode` se
emite como *recall* del logo grabado en la memoria no volátil de la impresora: unos pocos
bytes en lugar del bitmap completo. La familia de comando la elige la capacidad
`nv_logo_kind`: `"fs"` usa `FS p` (NV bit image por número) y cualquier otro valor usa
`GS ( L` (recall por keycode).

Las firmas (`role == "signature"`) y todo el resto van **siempre inline** por `GS v 0`.

El renderer **no conoce el transport ni sus capacidades**: solo lee del `DeviceProfile` lo que
la app dejó ahí. Es lo que mantiene a `MotorDsl.Rendering` en `net10.0` puro, sin dependencia
de la capa de impresión.

Para el inline, `EmitBitmap` recorta el prefijo `data:image/…;base64,` si lo hay, toma el
ancho máximo de la capacidad `bitmap_max_width_px` (384 por defecto), delega en el
`IBitmapRasterizer` y construye el `GS v 0` centrado. **Si no hay rasterizador registrado o la
rasterización falla, emite el literal `[BITMAP]` seguido de un salto de línea** — el ticket
sale, con el hueco visible.

---

## 5. Tabla de comandos — `EscPosCommands`

`src/MotorDsl.Rendering/EscPosCommands.cs` centraliza los bytes. Es estática y pública: un
renderer externo puede reutilizarla.

| Miembro | Bytes | Significado |
|---|---|---|
| `Init` | `1B 40` | `ESC @` — reinicia la impresora |
| `AlignLeft` / `AlignCenter` / `AlignRight` | `1B 61 00/01/02` | `ESC a n` |
| `StyleNormal` / `StyleBold` | `1B 21 00` / `1B 21 08` | `ESC ! n` |
| `CutFull` / `CutPartial` | `1D 56 00` / `1D 56 01` | `GS V n` |
| `LineFeed` | `0A` | salto de línea |
| `FeedLines(n)` | `1B 64 n` | `ESC d n` — avanza n líneas |
| `BarcodeEan13` | `1D 6B 02` | `GS k 2` |
| `QrSetSize3` / `QrSetErrorM` / `QrStoreData` / `QrPrint` | `1D 28 6B …` | `GS ( k` — tamaño de módulo 3, corrección M, carga e impresión |
| `BuildRasterImageGsV0(bits, widthBytes, heightDots)` | `1D 76 30 00 xL xH yL yH …` | `GS v 0` — imagen raster |
| `RecallNvGraphicsGsL(keycode)` | `1D 28 4C …` | `GS ( L` — recall de logo NV por keycode |
| `RecallNvBitImageFsP(n, mode)` | `1C 70 n mode` | `FS p` — recall de NV bit image por número |

Los comandos de **definición** y borrado de logos NV no están acá: viven en el transport
Bluetooth, porque requieren diálogo con el dispositivo. Ver [04](04_impresion-transports.md).

---

## 6. Agregar un renderer propio

1. Implementar `IRenderer`: un `Target` único y el método `Render(LayoutedDocument, DeviceProfile)`.
2. Registrarlo con `AddRenderer<T>()` sobre el `MotorDslBuilder`, **antes** de que se resuelva
   el `IRendererRegistry`.
3. Crear un `DeviceProfile` cuyo `RenderTarget` sea ese string.

```csharp
public class CsvRenderer : IRenderer
{
    public string Target => "csv";

    public RenderResult Render(LayoutedDocument document, DeviceProfile profile)
    {
        var result = new RenderResult(Target);
        // recorrer document.NodeLayoutInfo ordenado por LineNumber
        result.Output = /* string o byte[] */;
        return result;
    }
}

builder.Services.AddMotorDslEngine()
    .AddRenderer<CsvRenderer>()
    .AddProfiles(p => p.Add(new DeviceProfile("export-csv", 80, "csv")));
```

Un renderer nuevo **no requiere tocar** `DocumentEngine`, `LayoutEngine` ni el parser: la
resolución es por string en el registry. Ese es el sentido de la decisión D2 del
[índice maestro](00_MASTER-INDEX.md).

Guía extendida, con el caso de los transports: `docs/05_arquitectura_tecnica/extensibilidad-motor_v1.1.md`
y `docs/10_developer_guide/transports-y-extensibilidad.md`.
