# 02 — DSL y modelos

> **Propósito**: gramática del DSL JSON, el AST al que se traduce, los dos formatos de documento y
> las reglas de evaluación de bindings, condiciones y bucles.
> **Fuentes primarias**: `src/MotorDsl.Parser/DslParser.cs`, `src/MotorDsl.Core/Models/`,
> `src/MotorDsl.Core/Evaluators/Evaluator.cs`, `src/MotorDsl.Core/Validation/TemplateValidator.cs`,
> `docs/10_developer_guide/formato-dsl-templates.md`.

---

## 1. Estructura de un documento

```json
{
  "id": "acta-infraccion-001",        // requerido, string no vacío
  "version": "1.0",                    // requerido, string no vacío
  "format": "template",                // opcional: "template" (default) | "integrated"
  "metadata": { "autor": "..." },      // opcional, objeto plano
  "root": { "type": "container", ... } // requerido
}
```

`id`, `version` y `root` ausentes hacen fallar el parseo con `ArgumentException`. Un `format`
desconocido también: solo se aceptan `"template"` e `"integrated"`, comparados sin distinguir
mayúsculas (`DslParser.SupportedFormats`).

`metadata` se aplana a `Dictionary<string, object>` convirtiendo cada valor según su `JsonValueKind`
—los números **siempre** a `double` vía `GetDouble()`—; objetos y arrays anidados caen a su
representación `ToString()`.

---

## 2. Los seis tipos de nodo

| `type` | Clase C# | Campos propios | Notas |
|---|---|---|---|
| `text` | `TextNode` | `text` (o `value` en integrado), `bindPath` | El único que acepta `style` en el parser |
| `container` | `ContainerNode` | `layout` (`"vertical"` \| `"horizontal"`), `children[]` | `layout` no lo consume nadie aguas abajo |
| `conditional` | `ConditionalNode` | `expression`, `trueBranch`, `falseBranch` | Prohibido en formato integrado |
| `loop` | `LoopNode` | `source`, `itemAlias`, `body` | Prohibido en formato integrado |
| `table` | `TableNode` | `headers[]`, `rows[][]` | Sin campos obligatorios más allá de `type` |
| `image` | `ImageNode` | `source`, `width`, `height`, `imageType`, `role` | `imageType`: `"qrcode"` \| `"barcode"` \| `"bitmap"` |

Un `type` fuera de esta lista aborta el parseo nombrando los soportados
([`DslParser.SupportedTypes`](../../../PrintThermal_Motor_Maui/src/MotorDsl.Parser/DslParser.cs)).

Todos heredan de `DocumentNode`, que aporta `Type`, `Children?`, `Properties?` y `Style?`
([`src/MotorDsl.Core/Models/DocumentNode.cs`](../../../PrintThermal_Motor_Maui/src/MotorDsl.Core/Models/DocumentNode.cs)).

### Asimetría a tener presente

`LoopNode.Body` y `ConditionalNode.TrueBranch`/`FalseBranch` son propiedades **aparte** de
`Children`. El parser llena `Body`/`TrueBranch`/`FalseBranch`; el `Evaluator` los consume desde
ahí y devuelve un `ContainerNode` con hijos ya expandidos. El `LayoutEngine`, en cambio, recorre
`loopNode.Children` — que en un AST recién parseado está vacío. Es coherente porque el layout
siempre recibe un árbol ya evaluado, pero explica por qué `LayoutEngine` parece «no hacer nada» con
un `LoopNode` crudo.

### Estilos

```json
"style": { "align": "center", "bold": true }
```

El parser convierte `style` a `StyleDefinition.Attributes` **solo en nodos `text`**. Un `style` en
un `container`, `image` o `table` se ignora al parsear — aunque `LayoutEngine` sí lee
`tableNode.Style["bold"]`, lo que solo tiene efecto si el árbol se construyó a mano en C#.

Del bolsón de atributos, aguas abajo sobreviven dos: `align` (`left` \| `center` \| `right`) y
`bold`.

---

## 3. `template` vs `integrated`

| | `template` (default) | `integrated` |
|---|---|---|
| Campo de texto | `"text"` | `"value"` |
| `{{placeholders}}` | Sí, los resuelve el Evaluator | **Prohibidos** (error `UnresolvedPlaceholder`) |
| `loop` / `conditional` | Permitidos | **Prohibidos** (error `UnsupportedInIntegratedFormat`) |
| Etapa Evaluate | Se ejecuta | **Se salta** |
| Sobrecarga a usar | `Render(dsl, data, profile)` | `Render(json, profile)` |

La prohibición se aplica en **dos lugares independientes**: el parser lanza `ArgumentException` y
el `TemplateValidator` produce un `ValidationError`. Que un documento integrado con un `loop` falle
no depende de que el validador esté registrado.

La verificación de placeholders en integrado es **parcial y deliberada**: `TemplateValidator` mira
`text.value` e `image.source`, pero no las celdas de `table` ni los `headers`. Un `{{dato}}` en una
tabla integrada llega crudo a la salida.

Ejemplo real de cada formato: `samples/MotorDsl.MultaApp/Templates/MultaDsl.cs` (clásico, con loop
de infracciones) frente a `samples/MotorDsl.Integrated.MultaApp/Templates/MultaIntegratedDsl.cs`
(el mismo acta con el loop ya expandido en dos containers).

---

## 4. Resolución de datos

Fuente: [`src/MotorDsl.Core/Models/DataResolver.cs`](../../../PrintThermal_Motor_Maui/src/MotorDsl.Core/Models/DataResolver.cs).

Sintaxis de path: segmentos separados por `.`, con indexado opcional por corchetes.

```text
cliente.nombre        → propiedad anidada
items[0]              → índice sobre colección
ordenes[2].total      → combinación
```

Orden de resolución de cada segmento (`ResolveProperty`):

1. `IDictionary<string, object>`
2. `IDictionary<string, object?>`
3. Reflexión: `GetProperty(nombre, Public | Instance)`

Cualquier fallo intermedio devuelve `null` sin lanzar — los `try/catch` internos se tragan las
excepciones de reflexión. **La resolución distingue mayúsculas**: es `GetProperty` con el nombre
exacto y `TryGetValue` sobre diccionarios ordinales.

`ResolveCollection` acepta `IEnumerable<object>`, cualquier `IEnumerable` no genérico (que copia a
`List<object>`, comentado como *AOT-safe* para evitar `.Cast<>()`) y, como último recurso, envuelve
un valor suelto en un array de un elemento. Nunca devuelve `null`: si no encuentra nada, devuelve
vacío.

---

## 5. Interpolación y bucles

Fuente: [`src/MotorDsl.Core/Evaluators/Evaluator.cs`](../../../PrintThermal_Motor_Maui/src/MotorDsl.Core/Evaluators/Evaluator.cs) (456 líneas).

**Placeholders**: el patrón es `\{\{([^}]+)\}\}` sobre `TextNode.Text` e `ImageNode.Source`.

| Caso | Texto | Imagen |
|---|---|---|
| Variable resuelta | se sustituye por `value.ToString()` | ídem |
| Variable no resuelta | queda `{{UNRESOLVED:path}}` + warning | **se conserva el placeholder original** + warning |

**Bucles**: por cada ítem de la colección, `EvaluateLoopNode` arma un `ExpandoObject` que copia el
contexto padre —desde un diccionario, o por reflexión sobre las propiedades públicas si es un
objeto— y le agrega la clave `itemAlias`. Es decir, **dentro del bucle se ven a la vez las
variables externas y el ítem**. Un bucle sin ítems produce un `ContainerNode` vacío, no `null`.

---

## 6. Expresiones condicionales

`EvaluateCondition` es un evaluador propio, sin dependencias externas. Precedencia:

1. `||` (corta al primer verdadero)
2. `&&` (corta al primer falso)
3. Comparadores, probados en este orden: `==`, `!=`, `>=`, `<=`, `>`, `<`

`FindOperatorIndex` y `SplitExpression` respetan las comillas simples y dobles, así que
`nombre == 'a && b'` no se parte por el `&&` interno.

Operandos: literales entre comillas → `string`; `int.TryParse` → `int`; `double.TryParse` →
`double`; `true`/`false` → `bool`; cualquier otra cosa → path de datos.

| Comportamiento | Regla |
|---|---|
| Expresión vacía o solo espacios | `ArgumentException` |
| `===` o `!==` | `ArgumentException` explícita («Invalid operator») |
| Expresión sin operador reconocible | `ArgumentException("Cannot parse expression: …")` |
| Igualdad | `Equals(left, right)` — **sin coerción de tipos**: `"50" == 50` es falso |
| Orden con `null` | `null` es menor que todo; dos `null` son iguales |
| Sin paréntesis | No están soportados: no hay agrupación explícita |

Como `EvaluateOperand` usa `int.TryParse`/`double.TryParse` **sin cultura**, y `Compare` cae a
comparación de strings cuando el operando izquierdo no es `IComparable`, conviene mantener los tipos
de los datos alineados con los literales de la expresión.

---

## 7. Validación de plantillas

Fuente: [`src/MotorDsl.Core/Validation/TemplateValidator.cs`](../../../PrintThermal_Motor_Maui/src/MotorDsl.Core/Validation/TemplateValidator.cs) (243 líneas).

Orden: sintaxis JSON → campos raíz (`id`, `version`) → `format` válido → existencia de `root` →
recorrido recursivo de nodos. Los primeros tres cortan de inmediato y devuelven sin seguir.

Campos obligatorios por tipo:

| Tipo | Obligatorios |
|---|---|
| `loop` | `source`, `itemAlias`, `body` |
| `conditional` | `expression` |
| `image` | `source` |
| `text`, `container`, `table` | solo `type` |

Cada error lleva `Field`, `Type` (enum `ValidationErrorType`), `Message`, `NodeType`, `Severity`
(default `Error`) y `Location` — una ruta legible del estilo
`root.children[3].body.trueBranch` que permite señalar el nodo exacto.

`ValidationErrorType` cubre: `MissingField`, `TypeMismatch`, `InvalidStructure`, `InvalidSyntax`,
`MissingRequiredField`, `UnknownNodeType`, `UnsupportedInIntegratedFormat`, `UnresolvedPlaceholder`.

`ValidationResult.IsValid` es `true` mientras no haya ningún error de severidad `Error`: los
`Warning` no invalidan.

> Nota: `ValidationResult.AddError(...)` crea siempre errores con severidad `Error`. Los warnings se
> construyen agregando a `Errors` un `ValidationError` con `Severity = Warning` por inicializador de
> objeto, no por ese método.

---

## 8. Ejemplos de referencia

| Archivo | Qué muestra |
|---|---|
| `docs/10_developer_guide/ejemplos-templates/ticket-simple.json` | Ticket de venta con items, totales y footer |
| `…/ticket-con-qr.json` | QR de verificación |
| `…/ticket-con-barcode.json` | EAN-13 |
| `…/acta-infraccion.json` | Acta con infractor, loop de infracciones, QR y firma |
| `…/factura-simplificada.json` | Tabla de items + condiciones de pago + QR |
| `samples/MotorDsl.MultaApp/Templates/MultaDsl.cs` | Plantilla clásica embebida en C# + datos de ejemplo |
| `samples/MotorDsl.Integrated.MultaApp/Templates/MultaIntegratedDsl.cs` | La misma acta en formato integrado |

Especificación narrativa completa: `docs/10_developer_guide/formato-dsl-templates.md`.
