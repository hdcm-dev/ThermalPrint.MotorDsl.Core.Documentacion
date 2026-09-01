# 07 — Suite de pruebas

> **Propósito**: describir qué cubre `MotorDsl.Tests`, cómo está organizada, qué artificios usa
> para probar código de plataforma y dónde queda el borde no cubierto.
> **Fuentes primarias**: `src/MotorDsl.Tests/` (36 archivos), `MotorDsl.Tests.csproj`,
> `.github/workflows/ci.yml`, `docs/08_calidad_y_pruebas/`.

---

## 1. Marco y alcance

| Dato | Valor |
|---|---|
| Framework | xUnit 2.9.3 · `Microsoft.NET.Test.Sdk` 17.14.1 · coverlet 6.0.4 |
| TFM | `net10.0` — **un solo proyecto de tests, sin plataforma** |
| Empaquetado | `IsPackable=false` |
| Archivos | 35 con tests + `TestFakes.cs` |
| Métodos marcados `[Fact]` / `[Theory]` | **285** |

> El número de **casos ejecutados** es mayor que 285, porque cada `[Theory]` aporta un caso por
> `InlineData`. El `CHANGELOG.md` menciona 259 corridas en un momento anterior; el conteo real
> de la suite en este commit **no se verificó** —no se ejecutó `dotnet test` al generar esta
> base—. Para saberlo con certeza, correr el paso `Test` de `ci.yml`.

---

## 2. Cobertura por dominio

| Área | Archivos | `[Fact]`/`[Theory]` |
|---|---|---|
| Evaluador y expresiones | `EvaluatorTests` | 28 |
| Parser del DSL | `DslParserTests` | 19 |
| Formato integrado | `IntegratedFormatParserTests`, `IntegratedFormatValidatorTests`, `IntegratedFormatEngineTests`, `IntegratedFormatIntegrationTests` | 27 |
| Renderizado a texto | `TextRendererTests` | 15 |
| Renderizado ESC/POS | `EscPosRendererTests`, `TableNodeEscPosTests`, `QrEscPosTests`, `BarcodeEscPosTests` | 16 |
| Motor y registry | `DocumentEngineTests`, `RendererRegistryTests`, `RenderResultHelpersTests` | 27 |
| Layout | `LayoutEngineTests` | 8 |
| Validación | `DataValidatorTests`, `Sprint07ValidationTests` | 23 |
| Providers | `TemplateProviderTests`, `DataProviderTests`, `DeviceProfileProviderTests` | 22 |
| Logos NV | `Phase4NvLogoTests` | 13 |
| Transport de red | `NetworkTransportTests`, `NetworkEndpointTests`, `NetworkTransportDiTests` | 26 |
| Chunking | `TransportChunkingTests`, `ChunkBufferTests` | 14 |
| Capacidades y flow control | `StatusFlowControlTests`, `CapabilityDetectionTests`, `CU23CapabilityTests` | 18 |
| Errores e historial de fallos | `PrintErrorHandlerTests`, `PrintFailureLogTests` | 9 |
| Diagnóstico | `DiagnosticsBuilderTests` | 5 |
| Integraciones por sprint | `Sprint06IntegrationTests`, `Sprint07IntegrationTests`, `Sprint08CoreTests` | 15 |

La distribución refleja dónde está el riesgo real: el evaluador y el parser —las dos piezas que
interpretan entrada externa— concentran 47 tests entre ambos.

---

## 3. Cómo se prueba código que no es `net10.0`

El proyecto de tests es `net10.0` puro, así que **no puede referenciar** `MotorDsl.Bluetooth`
ni `MotorDsl.Maui`, que son multi-TFM de plataforma. Hay dos estrategias:

**a) Enlace por `<Compile Include>`.** El `.csproj` de tests incluye dos archivos concretos del
transport Bluetooth como si fueran propios:

```xml
<Compile Include="..\MotorDsl.Bluetooth\BluetoothPrinterTransport.Chunking.cs"    Link="Linked\…" />
<Compile Include="..\MotorDsl.Bluetooth\BluetoothPrinterTransport.Capabilities.cs" Link="Linked\…" />
```

Esto funciona porque esos dos archivos están escritos deliberadamente **fuera de todo bloque
`#if ANDROID` y sin dependencias de plataforma**. Es lo que hace testeables el chunking, el
parseo del byte de status, la decisión de pacing y el desarmado de `GS v 0`. Ver
[04 §6](04_impresion-transports.md).

**b) `MotorDsl.Network` se referencia directo.** Al ser `net10.0` puro
—`System.Net.Sockets` es BCL— entra por `<ProjectReference>` normal, sin artificios. Es una de
las ventajas concretas de la decisión D4 del [índice maestro](00_MASTER-INDEX.md).

Referencias del proyecto de tests: `Core`, `Extensions`, `Parser`, `Rendering`,
`Printing.Abstractions` y `Network`, más los dos archivos enlazados.

---

## 4. Dobles de prueba — `TestFakes.cs`

Tres implementaciones internas, deterministas y sin E/S:

| Fake | Implementa | Comportamiento |
|---|---|---|
| `FakeRasterizer` | `IBitmapRasterizer` | Devuelve siempre el mismo `RasterizedImage`: 4 bytes, 2 bytes por fila × 2 dots. Hace que los bytes ESC/POS esperados sean estables |
| `FakeTransport` | `IThermalPrinterTransport` | `Kind = "fake"`; `ThrowOnWrite` fuerza el fallo al escribir, para ejercitar la lógica de reintentos y el historial de fallos |
| `FakePrinterService` | `IThermalPrinterService` | Sustituye al orquestador donde se prueba lo que lo consume |

El `Kind = "fake"` es la demostración práctica de que el ruteo por string del servicio no
conoce los transports concretos.

---

## 5. Ejecución

```bash
dotnet test src/MotorDsl.Tests/MotorDsl.Tests.csproj -c Release
```

En el devcontainer, `dotnet restore` del proyecto de tests arrastra por `ProjectReference` los
seis proyectos `net10.0` — es todo lo compilable en Linux, y por eso es el
`postCreateCommand`. Ver [08](08_build-devops.md).

En CI, `ci.yml` corre exactamente:

```bash
dotnet test src/MotorDsl.Tests/MotorDsl.Tests.csproj -c Release --no-build \
  --logger "trx;LogFileName=test-results.trx" --results-directory ./TestResults
```

Los `.trx` se suben como artefacto con 7 días de retención, y un fallo en un pull request deja
un comentario automático. `cd-nuget.yml` corre la misma suite antes de empaquetar: **no se
publica sin tests en verde**.

---

## 6. Qué no cubre

Hechos, no estimaciones:

- **Nada de `MotorDsl.Maui`**: los renderers `pdf`, `escpos-bitmap` y `raster-preview`, el
  `SkiaSharpRasterizer`, los cinco controles y el proveedor de diagnóstico no tienen tests
  automatizados en esta suite. Solo `DiagnosticsBuilder` —que vive en
  `Printing.Abstractions` justamente para ser testeable— está cubierto.
- **Del transport Bluetooth, solo las dos piezas enlazadas.** El código bajo `#if ANDROID`
  —conexión SPP, sondeo de capacidades, definición de logos NV— requiere hardware o un runner
  Android y no se ejercita acá.
- **No hay tests de UI ni de integración sobre los samples.**
- **El transport de red se prueba sin impresora real**: parseo de endpoints, registro en DI y
  comportamiento del transport, no un ciclo completo contra un dispositivo físico.

No se midió cobertura de líneas al generar esta base; `coverlet.collector` está incluido, así
que el dato puede obtenerse agregando `--collect:"XPlat Code Coverage"` a `dotnet test`.

---

## 7. Documentación de calidad

`docs/08_calidad_y_pruebas/` contiene la estrategia formal previa: `estrategia-calidad-motor`,
`estrategia-testing-motor`, `criterios-validacion-motor`, `casos-prueba-referenciales`,
`matriz-cobertura-pruebas` y `guia-testing-extensibilidad`. Ver [09](09_docs-existentes.md).
