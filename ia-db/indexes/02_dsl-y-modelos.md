# 02 — DSL y modelos

> **Propósito**: la gramática del DSL JSON (tipos de nodo, bindings, estilos, condicionales), los
> dos formatos de documento y las clases del AST que los representan en memoria.
> **Fuentes primarias**: `docs/10_developer_guide/formato-dsl-templates.md`,
> `docs/10_developer_guide/formato-perfiles-impresora.md`, `src/MotorDsl.Core/Models/`,
> `src/MotorDsl.Parser/DslParser.cs`, `docs/10_developer_guide/ejemplos-templates/*.json`.
> El recorrido del pipeline sobre estos modelos está en [01_nucleo-pipeline](01_nucleo-pipeline.md).

---

## 1. Estructura raíz

| Propiedad | Tipo | Obligatoria | Descripción |
|---|---|---|---|
| `id` | string | Sí | Identificador del template |
| `version` | string | Sí | Versión del template (semántica libre) |
| `root` | object | Sí | Nodo raíz (habitualmente un `container`) |
| `format` | string | No | `"template"` (default) o `"integrated"` |
| `metadata` | object | No | Información libre (autor, fecha, descripción) |

```json
{ "id": "mi-template", "version": "1.0", "root": { "type": "text", "text": "Hola mundo" } }
```

---

## 2. Tipos de nodo

| `type` | Descripción | Obligatorias | Opcionales |
|---|---|---|---|
| `text` | Texto estático o con binding. Hoja. | `type` | `text` (o `value` en integrado), `bindPath`, `style` |
| `container` | Agrupa hijos con un layout | `type` | `layout`, `children`, `style` |
| `loop` | Itera una colección y repite `body` | `type`, `source`, `itemAlias` | `body` |
| `conditional` | Incluye contenido si la expresión es verdadera | `type`, `expression` | `trueBranch`, `falseBranch` |
| `table` | Tabla con encabezados y filas | `type` | `headers`, `rows`, `style` |
| `image` | Imagen, QR o código de barras | `type`, `source` | `width`, `height`, `imageType`, `role`, `style` |

`type` es obligatorio en **todos** los nodos: es el discriminador que usa `DslParser` para
instanciar la clase correcta. Un `type` desconocido es error de validación (`UnknownNodeType`).

### Ejemplos por tipo

```json
{ "type": "text", "text": "Cliente: {{cliente.nombre}}", "style": { "align": "left" } }

{ "type": "container", "layout": "vertical",
  "children": [ { "type": "text", "text": "Línea 1" }, { "type": "text", "text": "Línea 2" } ] }

{ "type": "loop", "source": "items", "itemAlias": "item",
  "body": { "type": "text", "text": "{{item.descripcion}}  {{item.precio}}" } }

{ "type": "conditional", "expression": "total > 1000",
  "trueBranch": { "type": "text", "text": "Envío gratis" },
  "falseBranch": { "type": "text", "text": "Costo de envío: $500" } }

{ "type": "table", "headers": ["Producto", "Cant", "Subtotal"],
  "rows": [["Café", "2", "$800"], ["Té", "1", "$300"]] }

{ "type": "image", "source": "https://ejemplo/pago/123", "imageType": "qrcode" }
```

`imageType` distingue el tratamiento en layout y render: `"qrcode"`, `"barcode"`, o bitmap cuando
`source` empieza con `data:image/`. El campo opcional `role` (`"logo"` | `"signature"`) enruta el
logo por *recall* de memoria NV cuando la impresora lo soporta; las firmas siempre van inline
(ver [04_impresion-transports](04_impresion-transports.md)).

---

## 3. Bindings

Sintaxis `{{path}}` dentro de `text`. El path admite campos simples, anidados (`cliente.nombre`)
e indexación (`items[0].precio`). Varios bindings pueden convivir en un mismo string.

Dentro de un `loop`, el `itemAlias` queda disponible como raíz del path
(`{{item.descripcion}}`). `DataValidator` excluye los alias de loop de su chequeo de campos
faltantes: se validan a nivel del loop, no del texto.

Alternativa a `{{…}}`: la propiedad `bindPath` de un nodo `text`, que resuelve el valor
directamente desde los datos.

---

## 4. Estilos

Objeto `style` con atributos clave-valor. Los reconocidos por el pipeline:

| Atributo | Valores | Efecto |
|---|---|---|
| `align` | `left` (default), `center`, `right` | `LayoutEngine` lo copia a `LayoutInfo.Alignment` y el renderer lo aplica |
| `bold` | `true` / `false` | Se propaga a `LayoutInfo.DeviceMetadata`; en ESC/POS emite `ESC ! 8` |

`StyleDefinition.Attributes` es un diccionario abierto: atributos adicionales se parsean y quedan
disponibles, pero solo `align` y `bold` tienen efecto en las implementaciones actuales.

---

## 5. Operadores en `conditional`

Comparación: `==`, `!=`, `>`, `<`, `>=`, `<=`. Lógicos: `&&`, `||`. Los literales de texto van
entre comillas simples (`status == 'activo'`) y el parser de expresiones respeta las comillas al
buscar operadores, de modo que un operador dentro de un literal no rompe el split.

```text
status == 'activo'
cantidad > 50
tipo == 'premium' && saldo >= 1000
```

Implementación: `Evaluator.EvaluateCondition` (`src/MotorDsl.Core/Evaluators/Evaluator.cs`). No es
un intérprete de expresiones general: no soporta paréntesis, funciones ni aritmética.

---

## 6. Los dos formatos de documento

| Aspecto | `template` (clásico) | `integrated` |
|---|---|---|
| Campo `format` | ausente o `"template"` | `"integrated"` |
| Texto | `{ "type":"text", "text":"Hola {{nombre}}" }` | `{ "type":"text", "value":"Hola Juan" }` |
| `loop` / `conditional` | permitidos | **prohibidos** (ya expandidos/resueltos) |
| Datos | diccionario requerido | no se usa |
| Llamada al motor | `engine.Render(json, data, profile)` | `engine.Render(json, profile)` |
| Pipeline | Parse → Validate → **Evaluate** → Layout → Render | Parse → Validate → Layout → Render |

> El cambio de campo `text` → `value` en modo integrado lo hace el propio parser
> (`DslParser.ParseTextNode`, rama `isIntegrated`). Un documento integrado que use `text` en vez
> de `value` parsea sin error pero deja el nodo **vacío**.

Validaciones exclusivas del modo integrado (`TemplateValidator`): un `loop` o `conditional`
presente es `UnsupportedInIntegratedFormat`; un `{{…}}` sin resolver en `value` o en
`image.source` es `UnresolvedPlaceholder`. Ambas con severidad `Error`.

Cuándo usar cada uno (fuente: `formato-dsl-templates.md` §9.6): clásico para documentos
parametrizables y plantillas reutilizables con lógica; integrado para documentos armados por un
backend, snapshots inmutables de auditoría/reimpresión y AST serializado entre servicios.

---

## 7. Clases del AST (`src/MotorDsl.Core/Models/`)

```text
DocumentTemplate            Id · Version · Root · Format · Metadata
└── DocumentNode (abstracta) Type · Children · Properties · Style
    ├── TextNode             Text · BindPath
    ├── ContainerNode        Layout
    ├── LoopNode             Source · ItemAlias · Body
    ├── ConditionalNode      Expression · TrueBranch · FalseBranch
    ├── TableNode            Headers · Rows
    └── ImageNode            Source · Width · Height · ImageType · Role
```

`DocumentTemplate` expone los discriminadores como constantes: `FormatTemplate = "template"` y
`FormatIntegrated = "integrated"`. `DocumentNode` incluye un diccionario `Properties` abierto que
permite extender un nodo sin modificar la clase.

### Modelos de resultado

| Clase | Contenido |
|---|---|
| `EvaluatedDocument` | `Id`, `Version`, `Root` (puede ser null), `Warnings`, `Errors`, `EvaluatedAt`, `IsSuccessful` |
| `LayoutedDocument` | `Root`, `NodeLayoutInfo` (mapa nodo → `LayoutInfo`), `TotalWidth`, `TotalHeight`, `DeviceProfile`, `LayoutMetadata`, `Warnings` |
| `LayoutInfo` | `LineNumber`, `ColumnNumber`, `Width`, `Height`, `Alignment`, `IsWrapped`, `WrappedText`, `IsTruncated`, `DeviceMetadata` |
| `RenderResult` | `Target`, `Output` (`object?`), `Warnings`, `Errors`, `IsSuccessful`, helpers `ToHexString()` y `ToBase64()` |
| `ValidationResult` / `ValidationError` | `IsValid` (sin errores de severidad `Error`), lista de errores con `Field`, `Type`, `Message`, `NodeType`, `Severity`, `Location` |
| `RasterizedImage` | `Bits`, `WidthBytes`, `HeightDots` — salida de `IBitmapRasterizer` |

`RenderResult.Output` es `object?` porque el tipo depende del renderer: `string` para `text`,
`byte[]` para `escpos` / `escpos-bitmap` / `pdf` / `raster-preview`.

---

## 8. `DeviceProfile` — el perfil de salida

Es el parámetro que decide **cómo** se calcula el layout y **qué** renderer se usa.

| Miembro | Tipo | Rol |
|---|---|---|
| `Name` | string (solo lectura) | Nombre del perfil; clave en `IDeviceProfileProvider` |
| `Width` | int (solo lectura) | **Ancho en caracteres**, no en píxeles ni mm |
| `RenderTarget` | string (solo lectura) | Selecciona el `IRenderer` (`text`, `escpos`, `escpos-bitmap`, `pdf`, `raster-preview`) |
| `CodePage` / `CodePageCommand` | `int?` / `byte[]?` | Página de códigos para acentos y ñ |
| `BaudRate` | `int?` | Informativo |
| `SupportedBarcodes` | `List<string>?` | Simbologías admitidas |
| Capacidades | `SetCapability` / `GetCapability` / `HasCapability` | Diccionario abierto: `supports_qrcode`, `supports_barcode`, `supports_images`, `nv_logo_keycode`, `nv_logo_kind`, … |

Anchos típicos: **32 caracteres** para papel de 58 mm, **48** para 80 mm
(fuente: `docs/10_developer_guide/formato-perfiles-impresora.md`, §«Tabla de anchos típicos»).

Perfiles habituales en los samples:

```csharp
new DeviceProfile("thermal_58mm", 32, "escpos-bitmap")
new DeviceProfile("preview",      32, "raster-preview")
new DeviceProfile("a4-pdf",       80, "pdf")
```

> **No confundir `DeviceProfile` con `PrinterProfile`.** `DeviceProfile` (en `MotorDsl.Core`)
> describe la **salida del documento**: ancho y renderer. `PrinterProfile` (en
> `MotorDsl.Printing.Abstractions`) describe el **temporizado del envío físico**: delays por
> línea, por byte, tras la inicialización, tras un QR o una imagen. Ver
> [04_impresion-transports](04_impresion-transports.md).

Solo el `false` **explícito** de una capacidad degrada un nodo; una capacidad ausente no degrada
(§6 de [01_nucleo-pipeline](01_nucleo-pipeline.md)).

---

## 9. Plantillas de ejemplo

`docs/10_developer_guide/ejemplos-templates/` contiene 5 documentos JSON listos para usar:
`ticket-simple.json`, `ticket-con-qr.json`, `ticket-con-barcode.json`,
`factura-simplificada.json`, `acta-infraccion.json`.

Ejemplos comentados paso a paso en `docs/11_examples/` (`ejemplo-01-simple.md`,
`ejemplo-02-multa.md`, `ejemplo-03-multa-integrada.md`, `ejemplo-03-multaapp-nuget.md`), con logos
de prueba en `docs/11_examples/imagenes_logos/` (`.bmp` y `.base64`).

---

## 10. Fuentes

| Tema | Archivo |
|---|---|
| Gramática completa del DSL, ejemplos y errores comunes | `docs/10_developer_guide/formato-dsl-templates.md` |
| Perfiles, anchos, codepage, cómo medir el ancho real | `docs/10_developer_guide/formato-perfiles-impresora.md` |
| Perfiles de impresoras reales probadas | `docs/10_developer_guide/perfiles-impresoras-reales.md` |
| Clases del AST y de resultado | `src/MotorDsl.Core/Models/*.cs` |
| Parseo por tipo de nodo | `src/MotorDsl.Parser/DslParser.cs` |
| Modelo conceptual y reglas | `docs/02_especificacion_funcional/modelo-datos/`, `docs/05_arquitectura_tecnica/modelo-datos-logico_v1.0.md` |
| Conceptos y vocabulario | `docs/10_developer_guide/conceptos-fundamentales.md` |
