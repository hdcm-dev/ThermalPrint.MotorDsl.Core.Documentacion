# 01 — Núcleo y pipeline

> **Propósito**: cómo corre el pipeline de cuatro etapas, qué contrato cumple cada pieza y cómo se
> arma el motor por inyección de dependencias.
> **Fuentes primarias**: `src/MotorDsl.Core/Contracts/`, `src/MotorDsl.Core/Engine/DocumentEngine.cs`,
> `src/MotorDsl.Core/Layout/LayoutEngine.cs`, `src/MotorDsl.Core/Validation/`,
> `src/MotorDsl.Extensions/`.

---

## 1. Contratos de `MotorDsl.Core/Contracts/` (15)

| Interfaz | Método clave | Quién lo implementa |
|---|---|---|
| `IDocumentEngine` | `Render(...)` ×3 sobrecargas + `RenderLayout(...)` | `DocumentEngine` |
| `IDslParser` | `DocumentTemplate Parse(string dsl)` | `DslParser` (paquete Parser) |
| `IEvaluator` | `Evaluate`, `ResolveVariable`, `EvaluateCondition`, `ResolveCollection` | `Evaluator` |
| `IDataResolver` | `Resolve(data, path)`, `ResolveCollection(data, path)` | `DataResolver` |
| `ILayoutEngine` | `LayoutedDocument ApplyLayout(EvaluatedDocument, DeviceProfile)` | `LayoutEngine` |
| `IRenderer` | `string Target { get; }` + `Render(LayoutedDocument, DeviceProfile)` | 5 renderers (índices 03 y 05) |
| `IRendererRegistry` | `Register`, `GetRenderer`, `GetAvailableTargets` | `RendererRegistry` |
| `ITemplateValidator` | `ValidateTemplate(string dslJson)` | `TemplateValidator` |
| `IDataValidator` | `Validate(DocumentNode ast, object? data)` | `DataValidator` |
| `IProfileValidator` | `ValidateProfile(DeviceProfile)` | `ProfileValidator` |
| `IBitmapRasterizer` | `RasterizedImage Rasterize(string source, int widthPixels)` | `SkiaSharpRasterizer` (Maui) |
| `IPrintErrorHandler` | `HandleErrorAsync`, `OnRetryAttempt`, `OnPrintSuccess` | `DefaultPrintErrorHandler`, `MauiPrintErrorHandler` |
| `ITemplateProvider` | `GetTemplate(id)`, `GetAvailableTemplateIds()` | `InMemoryTemplateProvider` |
| `IDataProvider` | `GetData(dataKey)` | `InMemoryDataProvider` |
| `IDeviceProfileProvider` | `GetProfile(name)`, `GetAll()` | `InMemoryDeviceProfileProvider` |

Los tres providers son **read-only por contrato**: la fuente real de plantillas, datos y perfiles es
responsabilidad del consumidor (comentarios XML en `Contracts/ITemplateProvider.cs`,
`IDataProvider.cs`, `IDeviceProfileProvider.cs`).

---

## 2. `DocumentEngine` — las cuatro entradas

Fuente: [`src/MotorDsl.Core/Engine/DocumentEngine.cs`](../../../PrintThermal_Motor_Maui/src/MotorDsl.Core/Engine/DocumentEngine.cs) (257 líneas).

| Sobrecarga | Para qué | Etapas que corre |
|---|---|---|
| `Render(string templateDsl, object data, DeviceProfile)` | Plantilla clásica desde JSON crudo | valida plantilla → Parse → *(delega en la 2.ª)* |
| `Render(DocumentTemplate, object data, DeviceProfile)` | Plantilla ya parseada | valida datos → valida perfil → Evaluate → Layout → Render |
| `Render(string integratedJson, DeviceProfile)` | Documento **integrado** (pre-resuelto) | valida plantilla → Parse → guarda de formato → valida perfil → **salta Evaluate** → Layout → Render |
| `RenderLayout(string, object, DeviceProfile)` | Vista previa en UI sin renderizar | valida ×3 → Parse → Evaluate → Layout |

### Contrato de errores

Las tres sobrecargas de `Render` **nunca lanzan**: capturan toda excepción y devuelven un
`RenderResult` con `Errors` poblado y `Output = ""`. `RenderLayout` sí lanza
`InvalidOperationException` cuando una validación falla — es la única asimetría del tipo, y es
deliberada: devuelve un `LayoutedDocument`, que no tiene dónde alojar errores.

### Severidad y propagación

| Origen | Severidad `Error` | Severidad `Warning` |
|---|---|---|
| `TemplateValidator` | aborta, `Output = ""` | se acumula y se agrega al `RenderResult` final |
| `DataValidator` | aborta | se acumula y se propaga |
| `ProfileValidator` | aborta | — |
| `LayoutEngine` | — | `layouted.Warnings` se vuelca al `RenderResult` (degradaciones por capacidad, CU-23) |

El guarda de formato de la tercera sobrecarga es explícito: si el JSON no declara
`"format": "integrated"`, devuelve un error que nombra la sobrecarga correcta en lugar de renderizar
mal en silencio.

---

## 3. `RendererRegistry` — resolución por `Target`

Fuente: [`src/MotorDsl.Core/Engine/RendererRegistry.cs`](../../../PrintThermal_Motor_Maui/src/MotorDsl.Core/Engine/RendererRegistry.cs).

Un `Dictionary<string, IRenderer>` indexado por `renderer.Target`. `Register` **sobrescribe** si el
target ya existía, así que el último registrado gana. `GetRenderer(target)` cae a `"text"` cuando no
encuentra el target pedido, y devuelve `null` solo si tampoco hay un renderer de texto — en ese caso
`DocumentEngine.GetRenderer` lanza `InvalidOperationException("No renderer found for target: …")`,
que el `catch` externo convierte en `RenderResult` con error.

---

## 4. `LayoutEngine` — de AST evaluado a líneas

Fuente: [`src/MotorDsl.Core/Layout/LayoutEngine.cs`](../../../PrintThermal_Motor_Maui/src/MotorDsl.Core/Layout/LayoutEngine.cs) (337 líneas).

Recorre el AST asignando a cada nodo un `LayoutInfo` bajo una clave sintética `node_{contador}`, y
acumula un `currentLine` global. **El diccionario `NodeLayoutInfo` —no el árbol— es lo que los
renderers consumen**: recorren sus entradas ordenadas por `LineNumber`, y todo nodo sin
`WrappedText` es invisible para la salida.

| Tipo de nodo | Qué hace el layout |
|---|---|
| `TextNode` | Si el texto entra en `profile.Width`, una línea; si no, `WrapText` corta por palabras y `Height` = nº de líneas |
| `ContainerNode` | `Height = 0`, recursa en los hijos |
| `TableNode` | Genera **líneas propias**: cabecera + separador de guiones + una línea por fila, con anchos calculados |
| `ImageNode` | Una línea con marcador textual y metadata (`is_qr`, `is_barcode`, `is_bitmap`) |
| `ConditionalNode` | Solo recursa en `TrueBranch` (el Evaluator ya resolvió antes) |
| `LoopNode` | Recursa en `Children` (el Evaluator ya lo expandió a un `ContainerNode`) |

### Anchos de tabla

`CalculateColumnWidths(numCols, totalWidth)`: una columna → todo el ancho. Con N columnas, reserva
`N-1` caracteres de separación, le da **la mitad del ancho útil a la columna 0** y reparte el resto
en partes iguales, distribuyendo el sobrante de a un carácter en las primeras columnas. Las celdas
que exceden su ancho se **truncan**, no se envuelven (`FormatTableRow`).

### Estilos que sobreviven al layout

Solo dos atributos de `Style.Attributes` cruzan al `LayoutInfo`: `align` (a `LayoutInfo.Alignment`)
y `bold` (a `DeviceMetadata["bold"]`). Cualquier otro atributo del JSON se pierde en esta etapa.
La propagación de `bold` es un arreglo posterior al release 1.0.13 —antes solo se leía `align`, y
los textos con `"bold": true` salían sin negrita ([`CHANGELOG.md`](../../../PrintThermal_Motor_Maui/CHANGELOG.md) § 1.0.13).

### Degradación por capacidades (CU-23)

`ApplyImageNodeLayout` consulta `profile.GetCapability(...)` con la regla
`IsCapabilityExplicitlyFalse`: solo degrada cuando la capacidad está declarada **explícitamente en
`false`**; ausente o `Unknown` significa «intentalo». Al degradar agrega un warning a
`layoutedDoc.Warnings`, que `DocumentEngine` propaga al `RenderResult`.

| Capacidad | Si es `false` |
|---|---|
| `supports_qrcode` | El QR sale como texto plano del dato + warning «QR degradado» |
| `supports_barcode` | Sale `[BARCODE: dato]` + warning «Barcode degradado» |
| `supports_images` | Sale `[IMG-DEGRADED: …]` truncado a 20 caracteres + warning |

---

## 5. `DeviceProfile` — el contrato con el dispositivo

Fuente: [`src/MotorDsl.Core/Models/DeviceProfile.cs`](../../../PrintThermal_Motor_Maui/src/MotorDsl.Core/Models/DeviceProfile.cs).

Tres propiedades de solo lectura fijadas en el constructor —`Name`, `Width` (en **caracteres**, no
en píxeles) y `RenderTarget`— más un bolsón de capacidades `string → object` con
`SetCapability` / `GetCapability` / `HasCapability`. Hay además cuatro propiedades opcionales
declaradas y **no consumidas por el motor**: `CodePage`, `CodePageCommand`, `BaudRate`,
`SupportedBarcodes`.

Capacidades que el código sí lee, con su consumidor:

| Clave | Tipo | Leída en |
|---|---|---|
| `supports_qrcode`, `supports_barcode`, `supports_images` | `bool` | `LayoutEngine` (degradación) |
| `bitmap_max_width_px` | `int` (default 384) | `EscPosRenderer`, `BitmapEscPosRenderer` |
| `nv_logo_keycode` | `int` | `EscPosRenderer` (ruteo a recall NV) |
| `nv_logo_kind` | `"gsl"` \| `"fs"` | `EscPosRenderer` (qué familia de comando emitir) |
| `codepage` | `"437"` \| `"850"` | `EscPosRenderer.GetEncoding` (solo QR y barcode) |

`ProfileValidator` exige lo mínimo: `Name` no vacío, `Width > 0`, `RenderTarget` no vacío.

---

## 6. Armado por DI

Fuente: [`src/MotorDsl.Extensions/MotorDslServiceCollectionExtensions.cs`](../../../PrintThermal_Motor_Maui/src/MotorDsl.Extensions/MotorDslServiceCollectionExtensions.cs).

```csharp
services.AddMotorDslEngine()          // registra el pipeline completo, devuelve MotorDslBuilder
        .AddTemplates(t => t.Add("id", dslJson))
        .AddProfiles(p => p.Add(new DeviceProfile("thermal_58mm", 32, "escpos-bitmap")))
        .AddRenderer<MiRenderer>()
        .AddMotorDslMaui();           // extensión del paquete Maui
```

`AddMotorDslEngine()` registra como **singleton**: `IDslParser`, `IEvaluator`, `ILayoutEngine`,
`IDataValidator`, `ITemplateValidator`, `IProfileValidator`, `IDocumentEngine` y un
`IRendererRegistry` construido por fábrica. Esa fábrica registra primero `TextRenderer` y
`EscPosRenderer` —siempre presentes— y después **todos los `IRenderer` del contenedor**, de modo
que un `AddRenderer<T>()` con `Target = "escpos"` reemplaza al built-in.

`MotorDslBuilder` no es un contenedor propio: expone `Services` y tres métodos que arman providers
en memoria y los registran ya poblados
([`src/MotorDsl.Extensions/MotorDslBuilder.cs`](../../../PrintThermal_Motor_Maui/src/MotorDsl.Extensions/MotorDslBuilder.cs)).

---

## 7. Modelos de resultado

| Tipo | Campos | Notas |
|---|---|---|
| `EvaluatedDocument` | `Id`, `Version` (`required`), `Root?`, `Warnings`, `Errors` | `Root` puede ser `null` si un conditional sin rama falsa se descarta |
| `LayoutedDocument` | `Root?`, `NodeLayoutInfo`, `TotalWidth/Height`, `DeviceProfile?`, `LayoutMetadata`, `Warnings` | `Warnings` es get-only |
| `RenderResult` | `Target`, `Output?` (`string` o `byte[]`), `Warnings`, `Errors` | `IsSuccessful => Errors.Count == 0`; helpers `ToHexString()` y `ToBase64()` devuelven `null` si `Output` no es `byte[]` |
| `LayoutInfo` | `LineNumber`, `ColumnNumber`, `Width`, `Height`, `Alignment`, `IsWrapped`, `WrappedText`, `IsTruncated`, `DeviceMetadata` | `IsTruncated` se declara pero el `LayoutEngine` nunca lo pone en `true` |

---

## 8. Puntos de atención

- **`LayoutEngine` guarda estado**: `_nodeCounter` es un campo de instancia reseteado al inicio de
  `ApplyLayout`. Registrado como singleton, no es seguro para llamadas concurrentes.
- **El árbol y el diccionario pueden divergir**: `LayoutedDocument.Root` es el AST evaluado, pero
  los renderers leen `NodeLayoutInfo`. Un nodo sin `WrappedText` existe en el árbol y no aparece en
  la salida.
- **`Evaluator` tiene sobrecargas privadas muertas**: varias versiones sin el parámetro `warnings`
  (`EvaluateNode`, `EvaluateTextNode`, `EvaluateConditionalNode`, `EvaluateLoopNode`,
  `EvaluateContainerNode`) no las llama nadie dentro de la clase.
- **`EvaluateTemplate` es API pública fuera del contrato**: `Evaluator` la expone pero `IEvaluator`
  no la declara, así que se pierde al inyectar por la interfaz.

Ver también: [`02_dsl-y-modelos.md`](02_dsl-y-modelos.md) para el AST y la gramática,
[`03_renderizado-base.md`](03_renderizado-base.md) para lo que hace cada renderer con el
`NodeLayoutInfo`.
