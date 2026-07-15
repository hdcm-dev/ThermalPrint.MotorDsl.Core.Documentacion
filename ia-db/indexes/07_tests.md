# 07 — Índice de Tests (src/MotorDsl.Tests)

> **Propósito**: inventario de las clases de test de `src/MotorDsl.Tests/` agrupadas
> por área funcional (parser, evaluator, engine, layout, renderers, providers y
> validación, printing/bluetooth, diagnostics, formato integrated, sprints), con la
> traza a casos de uso (CU-XX), tickets (TK-XX / BT-XXX) y casos de prueba (CP-XX)
> que cada clase declara. Incluye el framework de test (según csproj) y los fakes
> compartidos de `TestFakes.cs`.
>
> **Fuentes primarias**: `src/MotorDsl.Tests/MotorDsl.Tests.csproj` y los 32
> archivos `*.cs` del proyecto (31 clases de test + `TestFakes.cs`).
>
> **Versión de referencia**: `v1.0.13 @83677eb` (verificado en repo fuente:
> `git describe` → `v1.0.13-2-g83677eb`, HEAD = `83677eb`).
> Rutas relativas a la raíz del repo `PrintThermal_Motor_Maui/`.

---

## 1. Framework y configuración del proyecto de tests

Fuente: `src/MotorDsl.Tests/MotorDsl.Tests.csproj`.

| Elemento | Valor | Fuente |
|---|---|---|
| TargetFramework | `net10.0` (no MAUI: tests puros de lógica) | `#L4` |
| Framework de test | **xUnit 2.9.3** (`<Using Include="Xunit"/>` global) | `#L12`, `#L38` |
| Runner / SDK | `Microsoft.NET.Test.Sdk 17.14.1`, `xunit.runner.visualstudio 3.1.4` | `#L37`, `#L39` |
| Cobertura | `coverlet.collector 6.0.4` | `#L35` |
| DI en tests | `Microsoft.Extensions.DependencyInjection 10.0.8` | `#L36` |
| ProjectReferences | `MotorDsl.Core`, `MotorDsl.Extensions`, `MotorDsl.Parser`, `MotorDsl.Rendering`, `MotorDsl.Printing.Abstractions` | `#L15-L21` |
| Código enlazado por fuente | `BluetoothPrinterTransport.Chunking.cs` y `BluetoothPrinterTransport.Capabilities.cs` de `MotorDsl.Bluetooth` (ese proyecto solo targetea `net10.0-android/-ios` y no puede referenciarse desde `net10.0`; se enlazan solo los partial puros sin dependencias de plataforma) | `#L23-L32` |

Volumen (conteo por `grep` de atributos, `v1.0.13 @83677eb`): **31 clases de test**,
**244 `[Fact]` + 7 `[Theory]`** (≈251 métodos de test) en 32 archivos.

---

## 2. Inventario por área

Columnas: clase | qué cubre (según su doc-comment o contenido) | tests | trazas declaradas.

### 2.1 Parser (formato classic)

| Clase | Qué cubre | Tests | Trazas |
|---|---|---|---|
| `DslParserTests` (`src/MotorDsl.Tests/DslParserTests.cs#L12-L20`) | Interpretación y validación de plantillas DSL: texto, bindings, jerarquía, loop, conditional, JSON malformado, entrada nula/vacía, metadatos | 19 Fact | CU-01, CU-13, CU-14, RN-01, RN-02, CP-03, CP-05, `Casos-prueba-referenciales_v1.0.md` |

### 2.2 Evaluator (resolución de datos)

| Clase | Qué cubre | Tests | Trazas |
|---|---|---|---|
| `EvaluatorTests` (`src/MotorDsl.Tests/EvaluatorTests.cs#L13-L20`) | Resolución de referencias simples/anidadas/por índice, colecciones para iteración, condiciones (igualdad, comparación numérica, AND/OR), flujos alternos (dato inexistente, colección vacía, expresión inválida) | 28 Fact | CU-02, CU-15, CU-16, CU-17, FA-01/FA-02, CA-02/CA-03, `plan-iteracion_sprint-02_v1.0.md` |

### 2.3 Motor de documentos (DocumentEngine y registro de renderers)

| Clase | Qué cubre | Tests | Trazas |
|---|---|---|---|
| `DocumentEngineTests` (`src/MotorDsl.Tests/DocumentEngineTests.cs#L12-L17`) | Orquestación del pipeline classic en `IDocumentEngine` | 13 Fact | Sprint 03, BT-066 a BT-071; TK-39 |
| `RendererRegistryTests` (`src/MotorDsl.Tests/RendererRegistryTests.cs#L8-L13`) | `IRendererRegistry` + `RendererRegistry` (alta y resolución de renderers por target) | 4 Fact | Sprint 04, TK-22 |
| `RenderResultHelpersTests` (`src/MotorDsl.Tests/RenderResultHelpersTests.cs#L5-L13`) | Helpers de `RenderResult`: `ToHexString()` y `ToBase64()` sobre `Output` byte[]; null si no es byte[] | 10 Fact | Sprint 05, TK-31 |

### 2.4 Layout

| Clase | Qué cubre | Tests | Trazas |
|---|---|---|---|
| `LayoutEngineTests` (`src/MotorDsl.Tests/LayoutEngineTests.cs#L7-L12`) | `ILayoutEngine`/`LayoutEngine`: cálculo de layout del documento evaluado | 8 Fact | Sprint 03, BT-050 a BT-057 |

### 2.5 Renderers (text y ESC/POS)

| Clase | Qué cubre | Tests | Trazas |
|---|---|---|---|
| `TextRendererTests` (`src/MotorDsl.Tests/TextRendererTests.cs#L8-L13`) | `TextRenderer` (`IRenderer`): salida a texto plano | 15 Fact | Sprint 03, BT-058 a BT-065; TK-32 |
| `EscPosRendererTests` (`src/MotorDsl.Tests/EscPosRendererTests.cs#L9`) | `EscPosRenderer`: generación de bytes ESC/POS sobre documentos layouteados (perfil 80mm/48 col); sin doc-comment | 6 Fact | — (No verificado: sin traza declarada) |
| `BarcodeEscPosTests` (`src/MotorDsl.Tests/BarcodeEscPosTests.cs#L9`) | Render de códigos de barras en `EscPosRenderer` (targets escpos y text); sin doc-comment | 3 Fact | TK-43, TK-44 (en cuerpos de test) |
| `QrEscPosTests` (`src/MotorDsl.Tests/QrEscPosTests.cs#L9-L14`) | Render de QR en `EscPosRenderer` | 3 Fact | Sprint 05, TK-34 |
| `TableNodeEscPosTests` (`src/MotorDsl.Tests/TableNodeEscPosTests.cs#L9-L14`) | Render de `TableNode` en `EscPosRenderer` | 4 Fact | Sprint 05, TK-33 |

### 2.6 Providers y validación de datos

| Clase | Qué cubre | Tests | Trazas |
|---|---|---|---|
| `TemplateProviderTests` (`src/MotorDsl.Tests/TemplateProviderTests.cs#L8-L16`) | Contrato `ITemplateProvider` (`GetTemplate`, `GetAvailableTemplateIds`) e `InMemoryTemplateProvider.Add` | 8 Fact | Sprint 05, TK-27 |
| `DataProviderTests` (`src/MotorDsl.Tests/DataProviderTests.cs#L7-L15`) | Contrato `IDataProvider` (`GetData`) e `InMemoryDataProvider.Add` | 6 Fact | Sprint 05, TK-28 |
| `DeviceProfileProviderTests` (`src/MotorDsl.Tests/DeviceProfileProviderTests.cs#L8`) | `InMemoryDeviceProfileProvider`: registro y resolución de `DeviceProfile` por nombre; sin doc-comment | 8 Fact | — (No verificado: sin traza declarada) |
| `DataValidatorTests` (`src/MotorDsl.Tests/DataValidatorTests.cs#L7-L12`) | `DataValidator` (`IDataValidator`): validación de datos contra la plantilla | 9 Fact | Sprint 06, TK-36, TK-37, TK-38 |

### 2.7 Printing / Bluetooth (partes puras del transport y servicio)

| Clase | Qué cubre | Tests | Trazas |
|---|---|---|---|
| `ChunkBufferTests` (`src/MotorDsl.Tests/ChunkBufferTests.cs#L6-L11`) | `BluetoothPrinterTransport.ChunkBuffer`: chunker de tamaño fijo (reemplazo de `SplitByLineFeed`); parte por TAMAÑO, no por contenido — datos con `0x0A` intercalados (bitmap escpos) se reensamblan exactos | 6 Fact | — |
| `CapabilityDetectionTests` (`src/MotorDsl.Tests/CapabilityDetectionTests.cs#L6-L10`) | `ClassifyStatusResponse`: mapeo del byte de respuesta `DLE EOT n=1` (o null por timeout) a `CapabilitySupport` | 1 Fact + 2 Theory | — |
| `StatusFlowControlTests` (`src/MotorDsl.Tests/StatusFlowControlTests.cs#L6-L11`) | Flow control por status (fase 3): parseo del byte `DLE EOT n=1` a `PrinterStatus`, latch de degradación (tras un `Unknown` se usa pacing fijo el resto del envío), mapeo de `PrinterHardwareException` a `PrintErrorType.Hardware` | 5 Fact + 3 Theory | fase 3 |
| `PrintErrorHandlerTests` (`src/MotorDsl.Tests/PrintErrorHandlerTests.cs#L7-L12`) | `PrintError`, `IPrintErrorHandler`, `PrintRetryOptions` | 5 Fact | Sprint 06, TK-40, TK-41, TK-42 |
| `PrintFailureLogTests` (`src/MotorDsl.Tests/PrintFailureLogTests.cs#L7-L11`) | Ring buffer de fallos de `ThermalPrinterService`: acotado a MAX_FAILURES, orden, `ClearFailures`, concurrencia, una entrada (sin payload) al agotar retry | 4 Fact | — |
| `CU23CapabilityTests` (`src/MotorDsl.Tests/CU23CapabilityTests.cs#L12-L18`) | **CU-23 — Aplicar Restricciones del Dispositivo** (TDD, tests escritos antes de la implementación). Semántica PERMISIVA: capability no declarada → soportada por defecto; solo restringe con `false` explícito | 7 Fact | **CU-23** |
| `Phase4NvLogoTests` (`src/MotorDsl.Tests/Phase4NvLogoTests.cs#L10-L14`) | Fase 4 (logo NV): parseo `GS v 0`, builders de recall NV, propagación de rol de imagen, ruteo del renderer por rol (logo recall / inline; firmas siempre inline) y selección de estrategia | 11 Fact + 2 Theory | fase 4 |

### 2.8 Diagnostics

| Clase | Qué cubre | Tests | Trazas |
|---|---|---|---|
| `DiagnosticsBuilderTests` (`src/MotorDsl.Tests/DiagnosticsBuilderTests.cs#L5-L10`) | `DiagnosticsBuilder` (parte pura del `Build()` del provider de Maui): mapeo de capabilities, snapshot de impresora, lista de fallos con enmascarado de MAC según `includePii` | 5 Fact | — |

### 2.9 Formato integrated

| Clase | Qué cubre | Tests | Trazas |
|---|---|---|---|
| `IntegratedFormatParserTests` (`src/MotorDsl.Tests/IntegratedFormatParserTests.cs#L7-L12`) | Soporte integrated en `DslParser`: detección de `"format": "integrated"`, mapeo de `value` a `TextNode.Text`, rechazo de nodos `loop`/`conditional` | 11 Fact | — |
| `IntegratedFormatValidatorTests` (`src/MotorDsl.Tests/IntegratedFormatValidatorTests.cs#L7-L12`) | Reglas integrated de `TemplateValidator`: loops/conditionals prohibidos, `{{placeholders}}` residuales reportados, el formato classic conserva su comportamiento | 7 Fact | — |
| `IntegratedFormatEngineTests` (`src/MotorDsl.Tests/IntegratedFormatEngineTests.cs#L12-L16`) | Sobrecarga integrated `DocumentEngine.Render(string, DeviceProfile)`: pipeline simplificado Parse → Validate → Layout → Render, con Evaluator bypasseado | 5 Fact | — |
| `IntegratedFormatIntegrationTests` (`src/MotorDsl.Tests/IntegratedFormatIntegrationTests.cs#L12-L17`) | End-to-end integrated: el pipeline integrated produce la misma salida que el classic con template + data equivalentes | 4 Fact | — |

### 2.10 Sprints (integración y validación formal, TDD)

| Clase | Qué cubre | Tests | Trazas |
|---|---|---|---|
| `Sprint06IntegrationTests` (`src/MotorDsl.Tests/Sprint06IntegrationTests.cs#L13-L20`) | Pipeline completo con las features del Sprint 06: validación, barcode, QR, `RenderLayout` | 5 Fact | Sprint 06, TK-47 |
| `Sprint07IntegrationTests` (`src/MotorDsl.Tests/Sprint07IntegrationTests.cs#L12-L16`) | Pipeline completo con validación (Sprint 07) | 5 Fact | Sprint 07, TK-58 |
| `Sprint07ValidationTests` (`src/MotorDsl.Tests/Sprint07ValidationTests.cs#L6-L13`) | Validación formal TDD: `Severity` + `Location` en `ValidationError` (TK-48), `ITemplateValidator`/`TemplateValidator` (TK-49/50), `IProfileValidator`/`ProfileValidator` (TK-52/53) | 14 Fact | Sprint 07, TK-48, TK-49/50, TK-51, TK-52/53, TK-57 |
| `Sprint08CoreTests` (`src/MotorDsl.Tests/Sprint08CoreTests.cs#L9-L16`) | Core changes Sprint 08 (TDD, tests antes de la implementación): metadata bitmap en `LayoutEngine` (TK-59), extensibilidad `AddRenderer<T>()` (TK-60), contrato `IBitmapRasterizer` (TK-61) | 5 Fact | Sprint 08, TK-59, TK-60, TK-61 |

---

## 3. TestFakes.cs — fakes compartidos

Fuente: `src/MotorDsl.Tests/TestFakes.cs` (3 clases `internal sealed`, sin tests propios).

| Fake | Implementa | Comportamiento | Fuente |
|---|---|---|---|
| `FakeRasterizer` | `IBitmapRasterizer` | Rasterizador determinista para tests del renderer: devuelve siempre 4 bytes fijos (`0xAA 0xBB 0xCC 0xDD`), 2 bytes/fila × 2 dots | `#L8-L13` |
| `FakeTransport` | `IThermalPrinterTransport` | Transport para tests del servicio: `Kind="fake"`, `ConnectAsync` siempre conecta, `DiscoverAsync` devuelve lista vacía; `ThrowOnWrite` opcional lanza `IOException("Broken pipe (fake)")` en `WriteBytesAsync` | `#L15-L45` |
| `FakePrinterService` | `IThermalPrinterService` | Stub para tests del `DiagnosticsBuilder`: solo expone estado (`IsConnected=true`, `CurrentDevice`, `ConnectionState`, `CurrentCapabilities`, `RecentFailures` seteables); operaciones lanzan `NotImplementedException`; API NV logo devuelve resultados vacíos (`ProvisionLogoAsync` → `NvLogoResult(false, null, "fake")`) | `#L47-L79` |

---

## 4. Matriz de trazabilidad a casos de uso (CU-XX)

Solo se listan los CU declarados textualmente en los tests (`grep 'CU-[0-9]+'`).

| CU | Descripción (según el test) | Clases que lo trazan |
|---|---|---|
| CU-01 | Interpretar Plantilla DSL | `DslParserTests` (`#L13`, casos en `#L30`, `#L62`, `#L220`, `#L262`, `#L299`, `#L441`) |
| CU-02 | Resolver Datos del Documento | `EvaluatorTests` (`#L14`, `#L27`) |
| CU-13 | Cargar Plantilla DSL | `DslParserTests` (`#L14`) |
| CU-14 | Validar Plantilla DSL | `DslParserTests` (`#L15`, casos en `#L142`, `#L168`, `#L181`, `#L198`, `#L404-L426`) |
| CU-15 | Resolver Referencias a Datos en Plantilla | `EvaluatorTests` (`#L15`, casos en `#L27-L84`) |
| CU-16 | Ejecutar Iteraciones (Listas) | `EvaluatorTests` (`#L16`, casos en `#L99-L177`) |
| CU-17 | Evaluar Condiciones en Plantilla | `EvaluatorTests` (`#L17`, casos en `#L197-L342`) |
| CU-23 | Aplicar Restricciones del Dispositivo | `CU23CapabilityTests` (`#L13`) |

Otras trazas presentes (no CU): reglas RN-01/RN-02 y casos CP-001/CP-002/CP-03/CP-05
(`DslParserTests`, `Casos-prueba-referenciales_v1.0.md`); tickets BT-050…BT-071
(Sprint 03) y TK-22…TK-61 (Sprints 04–08); flujos FA-01/FA-02 y criterios CA-02/CA-03
(`EvaluatorTests`).

---

## 5. Observaciones

| # | Observación | Fuente |
|---|---|---|
| O1 | El proyecto de tests NO referencia `MotorDsl.Maui` ni `MotorDsl.Bluetooth` como proyectos: la lógica Bluetooth se cubre enlazando por fuente solo los partial puros (`Chunking`, `Capabilities`), para no contaminar el paquete NuGet con un target `net10.0` | `src/MotorDsl.Tests/MotorDsl.Tests.csproj#L23-L32` |
| O2 | Hay clases TDD explícitas ("tests escritos ANTES de la implementación"): `CU23CapabilityTests` y `Sprint08CoreTests` | `CU23CapabilityTests.cs#L16`, `Sprint08CoreTests.cs#L11` |
| O3 | Tres clases carecen de doc-comment y de traza declarada: `EscPosRendererTests`, `BarcodeEscPosTests` (trazas TK-43/44 solo en cuerpos), `DeviceProfileProviderTests` | `EscPosRendererTests.cs#L9`, `BarcodeEscPosTests.cs#L9`, `DeviceProfileProviderTests.cs#L8` |
| O4 | Varias clases de renderer registran `CodePagesEncodingProvider` en constructor estático (necesario para encodings ESC/POS fuera de MAUI) | `EscPosRendererTests.cs#L11-L14`, `BarcodeEscPosTests.cs#L11-L14`, `DeviceProfileProviderTests.cs#L10-L13` |
| O5 | El área integrated tiene cobertura en 4 niveles: parser, validator, engine (overload de 2 args) e integración end-to-end contra el pipeline classic | sección 2.9 |
| O6 | Los nombres `Sprint0X*Tests` corresponden a los planes de iteración del proyecto (Sprint 03–08); la numeración BT-/TK- referencia el backlog de esos sprints | doc-comments citados en 2.3, 2.4, 2.10 |
