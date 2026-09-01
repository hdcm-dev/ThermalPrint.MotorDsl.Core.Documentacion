# 02 — El DSL y los modelos del documento

> **Propósito**: describir el lenguaje JSON con el que se declara un documento, los nodos del
> AST que produce el parser, los dos formatos soportados y cómo el evaluador resuelve
> bindings, bucles y condiciones.
> **Fuentes primarias**: `src/MotorDsl.Parser/DslParser.cs`,
> `src/MotorDsl.Core/Models/`, `src/MotorDsl.Core/Evaluators/Evaluator.cs`,
> `src/MotorDsl.Core/Validation/TemplateValidator.cs`,
> `docs/10_developer_guide/formato-dsl-templates.md`,
> `docs/10_developer_guide/ejemplos-templates/*.json`.
>
> El **pipeline que consume estos modelos** está en [01](01_nucleo-pipeline.md).

---

## 1. Estructura de un documento

```json
{
  "id": "ticket-simple",
  "version": "1.0",
  "format": "template",
  "metadata": { "descripcion": "…", "anchoRecomendado": 32 },
  "root": { "type": "container", "layout": "vertical", "children": [ … ] }
}
```

| Campo raíz | Obligatorio | Notas |
|---|---|---|
| `id` | sí | String no vacío; identifica la plantilla |
| `version` | sí | String no vacío |
| `root` | sí | El nodo raíz, típicamente un `container` |
| `format` | no | `"template"` (por defecto) o `"integrated"`. Cualquier otro valor es error |
| `metadata` | no | Objeto libre; valores string, number, bool — el resto se guarda como texto |

Cualquier incumplimiento hace que `DslParser.Parse` lance `ArgumentException`; un JSON
sintácticamente inválido se reenvía como `ArgumentException("Invalid JSON format: …")`.

---

## 2. Los seis tipos de nodo

El parser acepta exactamente estos `type` y rechaza cualquier otro con
`"Unsupported element type: …"`.

| `type` | Clase del AST | Campos que lee el parser |
|---|---|---|
| `text` | `TextNode` | `text` (o `value` en integrado), `bindPath`, `style` |
| `container` | `ContainerNode` | `layout`, `children[]` |
| `conditional` | `ConditionalNode` | `expression`, `trueBranch`, `falseBranch` |
| `loop` | `LoopNode` | `source`, `itemAlias`, `body` |
| `table` | `TableNode` | `headers[]`, `rows[][]` |
| `image` | `ImageNode` | `source`, `width`, `height`, `imageType`, `role` |

Todos derivan de `DocumentNode` (`Models/DocumentNode.cs`), que aporta `Type`, `Children`,
un diccionario `Properties` y un `Style` opcional (`StyleDefinition`, un diccionario de
atributos).

### Detalle por nodo

- **`text`** — El contenido va en `text` en formato clásico y en `value` en integrado. `style`
  es un objeto libre; los atributos que el motor efectivamente propaga hasta el renderer son
  **`align`** (`left` | `center` | `right`) y **`bold`**. `bindPath` queda registrado en el
  nodo pero la resolución de valores se hace por los `{{placeholders}}` del propio texto.
- **`container`** — `layout` acepta cualquier string; el valor por defecto es `"vertical"`. Es
  el nodo de agrupación y anida recursivamente.
- **`conditional`** — Si la expresión da verdadero se emite `trueBranch`; si da falso se emite
  `falseBranch`, y si no hay `falseBranch` **el nodo desaparece** del documento.
- **`loop`** — Recorre la colección en `source` exponiendo cada elemento bajo el nombre
  `itemAlias`, y emite `body` una vez por elemento. El resultado se envuelve en un
  `ContainerNode` vertical; con cero elementos, el contenedor sale vacío.
- **`table`** — `headers` es un array de strings y `rows` un array de arrays de strings. El
  reparto de columnas lo hace el `LayoutEngine`.
- **`image`** — `source` es la imagen (típicamente base64). `role` es opcional y rutea el
  tratamiento: `qr`, `barcode`, `logo`, `signature`. `width` y `height` solo se leen si el
  JSON los trae como número.

---

## 3. Los dos formatos

| | `template` (clásico) | `integrated` |
|---|---|---|
| Campo del texto | `text` | `value` |
| `{{placeholders}}` | sí | **prohibidos** |
| `loop` / `conditional` | sí | **prohibidos** — el parser los rechaza |
| Requiere `data` | sí | no |
| Etapa de evaluación | se ejecuta | **se saltea** |
| Sobrecarga del motor | `Render(dsl, data, profile)` | `Render(json, profile)` |

El formato integrado existe para el caso en que **quien produce el documento ya resolvió los
datos** —un backend, por ejemplo— y la app solo tiene que imprimirlo. Al no haber evaluación
no hay bindings sin resolver ni sorpresas de contexto.

Las prohibiciones se aplican en dos lugares: el parser lanza al encontrar un `loop` o
`conditional` en integrado, y el `TemplateValidator` reporta un `UnsupportedInIntegratedFormat`
o un `UnresolvedPlaceholder` (regex `\{\{[^}]+\}\}`) antes de parsear.

---

## 4. Resolución de datos

`DataResolver` (`Models/DataResolver.cs`) implementa el acceso por ruta con punto:
`cliente.direccion.ciudad`. Cada segmento se resuelve primero como clave de diccionario y, si
no, por reflexión sobre las propiedades del objeto; un segmento con corchetes
(`items[0]`) se trata como índice de colección. Cualquier eslabón nulo corta la cadena y
devuelve `null`.

`ResolveCollection` devuelve la ruta como `IEnumerable<object>`, aceptando tanto colecciones
genéricas como no genéricas, y una colección vacía cuando la ruta no resuelve.

---

## 5. Interpolación de `{{bindings}}`

El evaluador reemplaza el patrón `\{\{([^}]+)\}\}` en el `text` de cada `TextNode` y en el
`source` de cada `ImageNode`.

| Situación | Qué pasa |
|---|---|
| La variable resuelve | Se sustituye por `value.ToString()` |
| No resuelve, en un `text` | Se emite el literal `{{UNRESOLVED:<ruta>}}` y se agrega la advertencia `"Unresolved variable: <ruta>"` |
| No resuelve, en el `source` de una imagen | Se **conserva el placeholder** tal cual y se advierte `"Unresolved variable in image source: <ruta>"` |

Que el texto no resuelto salga marcado en la salida en lugar de vacío es deliberado: el
problema se ve en el ticket impreso en vez de pasar inadvertido.

---

## 6. Expresiones de `conditional`

`Evaluator.EvaluateExpression` implementa un evaluador propio, deliberadamente chico.

| Elemento | Soportado |
|---|---|
| Comparación | `==`, `!=`, `>`, `<`, `>=`, `<=` |
| Lógicos | `\|\|` (menor precedencia), `&&` |
| Operandos literales | string entre comillas simples o dobles, entero, decimal, `true`, `false` |
| Operandos variables | cualquier ruta resoluble por `DataResolver` |
| Paréntesis | **no** |
| Aritmética | **no** |

```text
status == 'activo'
cantidad > 50
a == 1 && b == 2
tipo == 'A' || tipo == 'B'
```

Los operadores dentro de literales de string se ignoran: tanto la búsqueda del operador
(`FindOperatorIndex`) como el corte por `&&`/`||` (`SplitExpression`) llevan la cuenta de las
comillas abiertas. Una expresión que no encaja en ninguna forma lanza
`ArgumentException("Cannot parse expression: …")`.

La comparación usa `Equals` para `==` y `!=`, y `IComparable.CompareTo` para las de orden, con
`ToString()` como último recurso. **No hay coerción de tipos**: comparar el string `"50"` con
el número `50` no da verdadero.

---

## 7. Contexto de datos dentro de un `loop`

Por cada elemento, el evaluador arma un `ExpandoObject` nuevo que copia el contexto exterior y
le agrega la clave `itemAlias`. Así, dentro del cuerpo conviven `{{item.nombre}}` y las
variables del documento.

La copia intenta primero tratar los datos como `IDictionary<string, object>` o
`IDictionary<string, object?>`, y solo cae a reflexión sobre propiedades si no son
diccionarios. El comentario en el código lo justifica como *dictionary-first for AOT safety*:
la reflexión es el camino frágil bajo compilación AOT.

Consecuencia práctica para el `DataValidator`: los alias de bucle **no** existen en los datos
de entrada, así que el validador los rastrea aparte (`IsLoopAlias`) para no reportarlos como
bindings rotos.

---

## 8. Modelos que atraviesan el pipeline

| Modelo | Qué transporta |
|---|---|
| `DocumentTemplate` | `Id`, `Version`, `Root`, `Metadata`, `Format`. Las constantes `FormatTemplate` / `FormatIntegrated` |
| `EvaluatedDocument` | El AST resuelto, más `Warnings`, `Errors`, `EvaluatedAt` e `IsSuccessful` |
| `LayoutedDocument` | El AST más `NodeLayoutInfo`, `TotalWidth`/`TotalHeight`, el `DeviceProfile` usado, `LayoutMetadata` y `Warnings` |
| `RenderResult` | `Target`, `Output` (`object?`: `string` o `byte[]`), `Warnings`, `Errors`, `IsSuccessful`, y los helpers `ToHexString()` y `ToBase64()` |
| `RasterizedImage` | `Bits`, `WidthBytes`, `HeightDots` — el formato que espera el comando `GS v 0` |
| `ValidationResult` | Lista de `ValidationError` con severidad; ver [01 §6](01_nucleo-pipeline.md) |

`RenderResult.Output` es `object?` porque el tipo depende del target: `string` para `text`,
`byte[]` para `escpos`, `escpos-bitmap`, `pdf` y `raster-preview`. Quien lo consume debe
comprobar el tipo. `ToHexString()` y `ToBase64()` devuelven `null` si la salida no es `byte[]`.

---

## 9. Plantillas de ejemplo

Cinco plantillas completas y comentadas viven en
`docs/10_developer_guide/ejemplos-templates/`:

| Archivo | Qué demuestra |
|---|---|
| `ticket-simple.json` | Contenedores, estilos, `loop` sobre ítems de venta |
| `factura-simplificada.json` | Documento más largo con tabla |
| `ticket-con-qr.json` | Nodo `image` con rol QR |
| `ticket-con-barcode.json` | Nodo `image` con rol barcode |
| `acta-infraccion.json` | El caso real de multa de tránsito |

La especificación en prosa del formato está en
`docs/10_developer_guide/formato-dsl-templates.md`; ver [09](09_docs-existentes.md).
