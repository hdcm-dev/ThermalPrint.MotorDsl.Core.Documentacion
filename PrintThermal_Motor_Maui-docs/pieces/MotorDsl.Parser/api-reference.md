---
doc_id: MotorDsl.Parser-api-reference
doc_type: api-reference
title: MotorDsl.Parser — Referencia de API
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

# MotorDsl.Parser — Referencia de API

> Superficie pública del paquete `MotorDsl.Parser`. Firmas verificadas contra
> **v1.0.13 @83677eb**. Los `#Lx-Ly` valen para ese commit.

## Superficie pública

| Miembro | Firma | Propósito | Archivo |
|---|---|---|---|
| `DslParser` (clase) | `public class DslParser : IDslParser` | Implementación única del parser DSL JSON | `src/MotorDsl.Parser/DslParser.cs#L15 @83677eb` |
| `DslParser.Parse` | `public DocumentTemplate Parse(string dsl)` | Parsea el DSL JSON a `DocumentTemplate`; valida estructura y formato | `src/MotorDsl.Parser/DslParser.cs#L33 @83677eb` |

> `DslParser` no expone constructor explícito (usa el implícito sin parámetros) ni estado público.
> El resto de métodos (`ParseNode`, `ParseTextNode`, …) son `private` — no son API.

### Contrato implementado

`IDslParser` (definido en `MotorDsl.Core`):

```csharp
// src/MotorDsl.Core/Contracts/IDslParser.cs @83677eb
public interface IDslParser
{
    /// <exception cref="ArgumentException">If DSL is invalid or malformed</exception>
    DocumentTemplate Parse(string dsl);
}
```

Procedencia: `src/MotorDsl.Core/Contracts/IDslParser.cs#L11-L20 @83677eb`.

## `Parse` — validaciones y excepciones

Todas las rutas de error lanzan `ArgumentException` (nunca devuelve `null`):

| Condición | Mensaje (prefijo) | Fuente |
|---|---|---|
| `dsl` nulo/vacío/whitespace | `"DSL cannot be null or empty"` | `DslParser.cs#L36-L37 @83677eb` |
| Falta `id` | `"DSL must contain 'id' property"` | `DslParser.cs#L46-L47 @83677eb` |
| `id` vacío | `"'id' cannot be null or empty"` | `DslParser.cs#L50-L51 @83677eb` |
| Falta `version` | `"DSL must contain 'version' property"` | `DslParser.cs#L54-L55 @83677eb` |
| `version` vacío | `"'version' cannot be null or empty"` | `DslParser.cs#L58-L59 @83677eb` |
| `format` no soportado | `"Unsupported 'format' value: …"` | `DslParser.cs#L69-L71 @83677eb` |
| Falta `root` | `"DSL must contain 'root' property"` | `DslParser.cs#L77-L78 @83677eb` |
| Nodo no es objeto JSON | `"Node must be a JSON object"` | `DslParser.cs#L115-L116 @83677eb` |
| Nodo sin `type` | `"Node must have a 'type' property"` | `DslParser.cs#L118-L119 @83677eb` |
| `type` no soportado | `"Unsupported element type: '…'"` | `DslParser.cs#L125-L126 @83677eb` |
| `loop`/`conditional` en integrated | `"Node type '…' is not allowed in integrated format…"` | `DslParser.cs#L128-L130 @83677eb` |
| JSON malformado | `"Invalid JSON format: …"` (envuelve `JsonException`) | `DslParser.cs#L107-L110 @83677eb` |

## Snippet — cuerpo de `Parse` (esqueleto de validación)

```csharp
public DocumentTemplate Parse(string dsl)
{
    if (string.IsNullOrWhiteSpace(dsl))
        throw new ArgumentException("DSL cannot be null or empty");

    try
    {
        var doc = JsonDocument.Parse(dsl);
        var root = doc.RootElement;

        if (!root.TryGetProperty("id", out var idToken))
            throw new ArgumentException("DSL must contain 'id' property");
        var id = idToken.GetString();
        // … version, format (default "template"), root, metadata …

        var isIntegrated = string.Equals(format, DocumentTemplate.FormatIntegrated,
            StringComparison.OrdinalIgnoreCase);
        var parsedRoot = ParseNode(rootNodeToken, isIntegrated);

        return new DocumentTemplate(id, version, parsedRoot)
        {
            Format = format,
            Metadata = metadata
        };
    }
    catch (JsonException ex)
    {
        throw new ArgumentException("Invalid JSON format: " + ex.Message, ex);
    }
}
```

Procedencia: `src/MotorDsl.Parser/DslParser.cs#L33-L111 @83677eb` (condensado; elipsis marcan
código omitido, no reescrito).

## Snippet — ruteo de nodo y prohibición en integrated

```csharp
if (isIntegrated && (type == "loop" || type == "conditional"))
    throw new ArgumentException(
        $"Node type '{type}' is not allowed in integrated format. " +
        "Loops and conditionals must be pre-resolved by the producer.");

return type switch
{
    "text"        => ParseTextNode(nodeToken, isIntegrated),
    "container"   => ParseContainerNode(nodeToken, isIntegrated),
    "conditional" => ParseConditionalNode(nodeToken, isIntegrated),
    "loop"        => ParseLoopNode(nodeToken, isIntegrated),
    "table"       => ParseTableNode(nodeToken),
    "image"       => ParseImageNode(nodeToken),
    _ => throw new ArgumentException($"Unsupported element type: '{type}'")
};
```

Procedencia: `src/MotorDsl.Parser/DslParser.cs#L128-L141 @83677eb`.

## Snippet — text: `text` (classic) vs `value` (integrated)

```csharp
string text;
if (isIntegrated)
    text = nodeToken.TryGetProperty("value", out var valueToken)
        ? valueToken.GetString() ?? "" : "";
else
    text = nodeToken.TryGetProperty("text", out var textToken)
        ? textToken.GetString() ?? "" : "";
```

Procedencia: `src/MotorDsl.Parser/DslParser.cs#L148-L160 @83677eb`.

## Uso mínimo verificado

DSL classic mínimo aceptado por el parser (usado contra el pipeline real en el test BT-066):

```json
{ "id": "test-001", "version": "1.0", "root": { "type": "text", "text": "Hola Motor DSL" } }
```

Procedencia del JSON: `src/MotorDsl.Tests/DocumentEngineTests.cs#L38-L47 @83677eb`.

```csharp
IDslParser parser = new DslParser();
DocumentTemplate template = parser.Parse(dslJson); // Format == "template" por defecto
```

## 🤖 Para agentes

- **Punto de entrada único**: `DslParser.Parse(string) : DocumentTemplate`. No hay overloads, ni
  async, ni streaming. Todo el resto de la clase es `private`.
- **Nunca devuelve `null`**: éxito → `DocumentTemplate`; fallo → `ArgumentException` (incluida la de
  JSON malformado, que envuelve `JsonException`). No captures otras excepciones aquí.
- **Formato**: leído del campo `format` (case-insensitive). Solo `"template"` (default) e
  `"integrated"` son válidos. Si el productor genera `integrated`, **no** incluyas `loop`/
  `conditional` ni uses `text` (usa `value`) — el parser lanza `ArgumentException`.
- **`style` solo se materializa en nodos `text`** (`DslParser.cs#L168-L183 @83677eb`). Para tablas,
  `style` en el JSON se ignora por el parser. «No verificado» otra vía no-código.
- **`metadata`** solo admite valores string/number(double)/bool; otros tipos JSON se serializan con
  `ToString()` (`DslParser.cs#L89-L96 @83677eb`).
- **El parser no resuelve datos ni placeholders**: `{{path}}` queda literal en `TextNode.Text`; lo
  resuelve el `Evaluator` (classic) aguas abajo. Ver [ia-db 02 §3](../../../ia-db/indexes/02_dsl-y-modelos.md).
- **Enlaces**: modelos de nodo → [ia-db 02](../../../ia-db/indexes/02_dsl-y-modelos.md); términos →
  [`GLOSSARY.md`](../../GLOSSARY.md).
