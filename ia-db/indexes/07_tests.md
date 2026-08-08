# 07 — Pruebas

> **Propósito**: qué cubre la suite, dónde buscar el test de un comportamiento concreto, qué
> fakes existen y por qué hay código de Bluetooth enlazado por fuente.
> **Fuentes primarias**: `src/MotorDsl.Tests/` (32 archivos), `src/MotorDsl.Tests/MotorDsl.Tests.csproj`,
> `.github/workflows/ci.yml`, `docs/08_calidad_y_pruebas/`.

---

## 1. La suite en números

| Dato | Valor | Fuente |
|---|---|---|
| Framework | xUnit 2.9.3 + `Microsoft.NET.Test.Sdk` 17.14.1 + `coverlet.collector` 6.0.4 | `MotorDsl.Tests.csproj` |
| TFM | `net10.0` (`IsPackable=false`) | `MotorDsl.Tests.csproj` |
| Archivos de test | 35 + `TestFakes.cs` | `src/MotorDsl.Tests/` |
| Atributos `[Fact]` / `[Theory]` | **285** (medido) | conteo sobre `src/MotorDsl.Tests/*.cs` |
| Casos ejecutados | **306** (medido con `dotnet test`) | corrida en devcontainer `net10.0` |
| Cobertura mínima exigida | 70 % | `docs/README.md` §Definition of Done |

> **Discrepancia resuelta**: el conteo declarado variaba según la fuente — `ci.yml` decía «185
> tests» y `.github/copilot-instructions.md` dice «212 tests (185 originales + 27 del formato
> integrado)», mientras los atributos del código sumaban 251. Se ejecutó `dotnet test`: **eran 259**
> antes del transport de red y son **306** después. Los números nunca fueron comparables, porque un
> `[Theory]` expande a varios casos ejecutados.
>
> `ci.yml` **dejó de declarar un número fijo**: un contador hardcodeado ahí se desactualiza en
> cuanto se agrega un test, que es exactamente lo que había pasado. `copilot-instructions.md` sigue
> con la cifra vieja.

---

## 2. Mapa: qué archivo cubre qué

### Pipeline y núcleo

| Archivo | Casos | Cubre |
|---|---|---|
| `EvaluatorTests.cs` | 28 | Resolución de variables, paths anidados, indexación, condiciones, expansión de loops |
| `DslParserTests.cs` | 19 | Parseo de cada tipo de nodo, campos obligatorios, JSON inválido, metadata |
| `DocumentEngineTests.cs` | 13 | Orquestación, orden de validaciones, propagación de errores y warnings |
| `LayoutEngineTests.cs` | 8 | Wrap, alineación, cálculo de líneas, layout de tablas |
| `DataValidatorTests.cs` | 9 | Campos faltantes vs. campos null (Error vs. Warning), alias de loop |
| `Sprint07ValidationTests.cs` | 14 | `TemplateValidator` y `ProfileValidator` |
| `RenderResultHelpersTests.cs` | 10 | `IsSuccessful`, `ToHexString()`, `ToBase64()` |

### Renderizado

| Archivo | Casos | Cubre |
|---|---|---|
| `TextRendererTests.cs` | 15 | Alineación, padding, truncado, orden por línea |
| `EscPosRendererTests.cs` | 6 | Secuencia init → contenido → corte, bold, alineación |
| `QrEscPosTests.cs` | 3 | Secuencia `GS ( k` |
| `BarcodeEscPosTests.cs` | 3 | Secuencia `GS k 2` EAN-13 |
| `TableNodeEscPosTests.cs` | 4 | Render de tablas a ESC/POS |
| `RendererRegistryTests.cs` | 4 | Registro, búsqueda por target, sobrescritura |

### Formato integrado

| Archivo | Casos | Cubre |
|---|---|---|
| `IntegratedFormatParserTests.cs` | 11 | Campo `value` vs. `text`, discriminador `format` |
| `IntegratedFormatValidatorTests.cs` | 7 | `UnsupportedInIntegratedFormat`, `UnresolvedPlaceholder` |
| `IntegratedFormatEngineTests.cs` | 5 | Sobrecarga `Render(json, profile)` y guarda defensiva de formato |
| `IntegratedFormatIntegrationTests.cs` | 4 | Recorrido completo con documentos integrados |

### Impresión y transports

| Archivo | Casos | Cubre |
|---|---|---|
| `Phase4NvLogoTests.cs` | 13 | Aprovisionamiento y *recall* del logo NV, familias `gsl` / `fs` |
| `StatusFlowControlTests.cs` | 8 | `ParseStatusByte`, decisión de pacing, degradación |
| `CU23CapabilityTests.cs` | 7 | Degradación de QR / barcode / imágenes por capacidad en `false` |
| `ChunkBufferTests.cs` | 6 | Partición en bloques y reensamblado exacto |
| `PrintErrorHandlerTests.cs` | 5 | Política retry/abort por `PrintErrorType` |
| `DiagnosticsBuilderTests.cs` | 5 | Construcción del reporte de diagnóstico |
| `PrintFailureLogTests.cs` | 4 | Ring buffer de fallos, descarte del más viejo, ausencia de payload |
| `CapabilityDetectionTests.cs` | 3 | `ClassifyStatusResponse`, bits fijos del status |

### Providers e integración por sprint

| Archivo | Casos | Cubre |
|---|---|---|
| `TemplateProviderTests.cs` | 8 | `InMemoryTemplateProvider` |
| `DeviceProfileProviderTests.cs` | 8 | `InMemoryDeviceProfileProvider` |
| `DataProviderTests.cs` | 6 | `InMemoryDataProvider` |
| `Sprint06IntegrationTests.cs` | 5 | Validación + retry de impresión |
| `Sprint07IntegrationTests.cs` | 5 | Validaciones encadenadas en el pipeline |
| `Sprint08CoreTests.cs` | 5 | Rasterizado y nodos imagen |

---

## 3. Fakes (`TestFakes.cs`)

| Fake | Implementa | Comportamiento |
|---|---|---|
| `FakeRasterizer` | `IBitmapRasterizer` | Devuelve un raster determinista de 2 bytes/fila × 2 dots (`AA BB CC DD`) |
| `FakeTransport` | `IThermalPrinterTransport` | `Kind = "fake"`; `ThrowOnWrite` permite forzar el camino de error y ejercitar el retry |

Ambos son `internal sealed`: los tests viven en el mismo ensamblado.

---

## 4. Código de Bluetooth enlazado por fuente

`MotorDsl.Bluetooth` solo targetea `net10.0-android;net10.0-ios`, así que un proyecto de tests
`net10.0` **no puede referenciarlo**. La solución adoptada: enlazar por fuente únicamente los dos
archivos `partial` **puros** (sin dependencias de plataforma, fuera de todo `#if`):

```xml
<Compile Include="..\MotorDsl.Bluetooth\BluetoothPrinterTransport.Chunking.cs"
         Link="Linked\BluetoothPrinterTransport.Chunking.cs" />
<Compile Include="..\MotorDsl.Bluetooth\BluetoothPrinterTransport.Capabilities.cs"
         Link="Linked\BluetoothPrinterTransport.Capabilities.cs" />
```

Eso da cobertura a `ChunkBuffer`, `HasValidStatusFixedBits`, `ClassifyStatusResponse`,
`ParseStatusByte` y `NextPacingDecision` **sin contaminar el paquete NuGet con un target
`net10.0`**. Es la razón por la que esa lógica vive separada del archivo principal del transport:
si se mueve dentro de un bloque `#if ANDROID`, se pierde su cobertura.

> **Contraste con `MotorDsl.Network`**: ese paquete es `net10.0` puro, así que **no necesita este
> rodeo** — `MotorDsl.Tests` lo referencia con un `<ProjectReference>` normal y puede testear el
> transport completo, no solo sus partes puras. `NetworkTransportTests` levanta un `TcpListener`
> local que hace de impresora y verifica paridad byte a byte del payload. Es una de las ventajas
> concretas de haber elegido un TFM sin sufijo de plataforma
> (ver [04_impresion-transports](04_impresion-transports.md) §5-bis).

`MotorDsl.Printing.Abstractions` expone además sus miembros `internal` al proyecto de tests
(`<InternalsVisibleTo Include="MotorDsl.Tests" />`), lo que permite testear la semántica del ring
buffer de fallos (`RecordFailure`) sin pasar por el bucle de retry.

---

## 5. Ejecución

```bash
dotnet test src/MotorDsl.Tests/MotorDsl.Tests.csproj
```

No requiere workload MAUI ni Android SDK: la suite es `net10.0` puro. En CI corre en
`ubuntu-latest` (`ci.yml`), sube los resultados como artefacto y comenta el PR si falla. El
script de publicación NuGet corre los tests antes de empaquetar y **aborta la publicación si
fallan** (ver [08_build-devops](08_build-devops.md)).

---

## 6. Qué **no** está cubierto

- El código de `MotorDsl.Bluetooth` con dependencias de plataforma (I/O real sobre el socket,
  `DiscoverAsync`, `ConnectAsync`, la ejecución de `WriteBytesAsync`) — solo se cubren sus partes
  puras.
- `MotorDsl.Maui` completo: controles, `PdfRenderer`, `RasterPreviewRenderer`,
  `SkiaSharpRasterizer`, `QrCodeRasterizer`, `MauiDiagnosticsReportProvider`. No hay proyecto de
  tests que targetee `net10.0-android`.
- Las apps de `samples/`.

Consecuencia práctica: un cambio en los renderers MAUI o en el transport Bluetooth **no lo atrapa
CI**; requiere prueba manual en dispositivo. Los dos bugs corregidos en v1.0.13 (decodificación
de PNG en SkiaSharp 3.x y propagación de `bold`) estaban justamente en esa zona.

---

## 7. Fuentes

| Tema | Archivo |
|---|---|
| Suite | `src/MotorDsl.Tests/*.cs` |
| Configuración del proyecto | `src/MotorDsl.Tests/MotorDsl.Tests.csproj` |
| Workflow de CI | `.github/workflows/ci.yml` |
| Estrategia de calidad y testing | `docs/08_calidad_y_pruebas/{estrategia-calidad-motor_v1.0,estrategia-testing-motor_v1.0,guia-testing-extensibilidad_v1.0}.md` |
| Casos y cobertura | `docs/08_calidad_y_pruebas/{casos-prueba-referenciales_v1.0,matriz-cobertura-pruebas_v1.0,criterios-validacion-motor_v1.0}.md` |
