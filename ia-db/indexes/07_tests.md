# 07 — Tests

> **Propósito**: inventario de la suite, cómo está organizada, qué cubre y dónde queda el borde sin
> cubrir.
> **Fuentes primarias**: `src/MotorDsl.Tests/` (36 archivos), `.github/workflows/ci.yml`,
> `docs/08_calidad_y_pruebas/`.

---

## 1. Datos de la suite

| Dato | Valor |
|---|---|
| Framework | xUnit 2.9.3 · `Microsoft.NET.Test.Sdk` 17.14.1 · `coverlet.collector` 6.0.4 |
| TFM | `net10.0` (`IsPackable = false`) |
| Archivos | 36 (35 de pruebas + `TestFakes.cs`) |
| Métodos `[Fact]` | 275 |
| Métodos `[Theory]` | 10, con 31 `[InlineData]` |
| Casos ejecutables | **306** (275 + 31), por conteo estático |

> El conteo es **estático**: no hay SDK .NET en la máquina donde se generó esta base, así que la
> suite no se corrió. El CHANGELOG menciona que `ci.yml` dejó de declarar un número fijo de tests
> porque «decía 185 cuando la suite ya corría 259» — otra razón para no citar un número de corrida
> sin ejecutarla.

---

## 2. Mapa por dominio

### Núcleo y pipeline

| Archivo | Casos | Cubre |
|---|---|---|
| `EvaluatorTests.cs` | 28 | Interpolación, bucles, condiciones, operadores, comillas |
| `DslParserTests.cs` | 19 | Gramática JSON, campos requeridos, tipos de nodo, errores |
| `DocumentEngineTests.cs` | 13 | Las 4 sobrecargas, propagación de errores y warnings |
| `LayoutEngineTests.cs` | 8 | Wrap, alineación, alto acumulado |
| `RendererRegistryTests.cs` | 4 | Registro, fallback a `text`, sobrescritura |
| `RenderResultHelpersTests.cs` | 10 | `ToHexString`, `ToBase64`, `IsSuccessful` |

### Validación

| Archivo | Casos | Cubre |
|---|---|---|
| `Sprint07ValidationTests.cs` | 14 | `TemplateValidator` y `ProfileValidator` |
| `DataValidatorTests.cs` | 9 | Campos faltantes, tipos, estructura |

### Formato integrado

| Archivo | Casos | Cubre |
|---|---|---|
| `IntegratedFormatParserTests.cs` | 11 | `value` vs `text`, rechazo de loop/conditional |
| `IntegratedFormatValidatorTests.cs` | 7 | `UnsupportedInIntegratedFormat`, `UnresolvedPlaceholder` |
| `IntegratedFormatEngineTests.cs` | 5 | Salto de la etapa Evaluate |
| `IntegratedFormatIntegrationTests.cs` | 4 | Punta a punta con documento integrado |

### Renderizado

| Archivo | Casos | Cubre |
|---|---|---|
| `TextRendererTests.cs` | 15 | Alineación, padding, truncado |
| `EscPosRendererTests.cs` | 6 | Init, codepage, alineación, corte |
| `QrEscPosTests.cs` | 3 | Secuencia `GS ( k` |
| `BarcodeEscPosTests.cs` | 3 | `GS k 2` + terminador NUL |
| `TableNodeEscPosTests.cs` | 4 | Cabecera, separador, anchos de columna |

### Impresión y transports

| Archivo | Casos | Cubre |
|---|---|---|
| `NetworkTransportTests.cs` | 12 | Conexión, timeouts, invalidación, escritura |
| `NetworkEndpointTests.cs` | 10 | `TryParseEndpoint` con IPv4, IPv6, puertos |
| `NetworkTransportDiTests.cs` | 4 | `AddNetworkPrinterTransport` y opciones |
| `Phase4NvLogoTests.cs` | 13 | Aprovisionamiento NV, `ParseGsV0`, recall |
| `StatusFlowControlTests.cs` | 8 | `ParseStatusByte`, `NextPacingDecision` |
| `CapabilityDetectionTests.cs` | 3 | `ClassifyStatusResponse`, bits fijos |
| `CU23CapabilityTests.cs` | 7 | Degradación por capacidad en el layout |
| `TransportChunkingTests.cs` | 8 | Helper público de troceo |
| `ChunkBufferTests.cs` | 6 | Copia `internal` del chunker Bluetooth |
| `PrintErrorHandlerTests.cs` | 5 | Política de reintento por tipo de error |
| `PrintFailureLogTests.cs` | 4 | Ring buffer de 20, sin payload |
| `DiagnosticsBuilderTests.cs` | 5 | `MaskMac`, capacidades a diccionario |

### Providers e integración por sprint

| Archivo | Casos | Cubre |
|---|---|---|
| `TemplateProviderTests.cs` | 8 | `InMemoryTemplateProvider` |
| `DeviceProfileProviderTests.cs` | 8 | `InMemoryDeviceProfileProvider` |
| `DataProviderTests.cs` | 6 | `InMemoryDataProvider` |
| `Sprint06IntegrationTests.cs` | 5 | Pipeline completo con validación |
| `Sprint07IntegrationTests.cs` | 5 | Validación de plantilla y perfil integradas |
| `Sprint08CoreTests.cs` | 5 | Imágenes, rasterizado, nodos nuevos |

---

## 3. El truco del enlace por fuente

`MotorDsl.Bluetooth` targetea `net10.0-android`/`-ios` y **no se puede referenciar** desde un
proyecto `net10.0`. Para cubrir igual su lógica pura, el `.csproj` de tests enlaza dos archivos
`partial` por código fuente:

```xml
<Compile Include="..\MotorDsl.Bluetooth\BluetoothPrinterTransport.Chunking.cs"     Link="Linked\..." />
<Compile Include="..\MotorDsl.Bluetooth\BluetoothPrinterTransport.Capabilities.cs" Link="Linked\..." />
```

Son justamente los dos archivos sin dependencias de plataforma. Así se testean `ChunkBuffer`,
`ClassifyStatusResponse`, `ParseStatusByte`, `NextPacingDecision` y `ParseGsV0` sin contaminar el
paquete NuGet con un TFM `net10.0` que no le corresponde.

`MotorDsl.Network`, en cambio, se referencia como proyecto normal — es una de las ventajas
declaradas de haberlo hecho `net10.0` puro (ADR-0005).

`MotorDsl.Printing.Abstractions` declara `<InternalsVisibleTo Include="MotorDsl.Tests" />` para
exponer miembros `internal` como `ThermalPrinterService.RecordFailure`, y así probar la semántica
del ring buffer sin pasar por el bucle de retry completo.

---

## 4. Dobles de prueba

`src/MotorDsl.Tests/TestFakes.cs` (`internal sealed`):

| Fake | Sustituye | Particularidad |
|---|---|---|
| `FakeRasterizer` | `IBitmapRasterizer` | Devuelve un raster fijo, sin SkiaSharp |
| `FakeTransport` | `IThermalPrinterTransport` | `Kind = "fake"`, con `ThrowOnWrite` para forzar fallos |
| `FakePrinterService` | `IThermalPrinterService` | Siempre conectado; capacidades y fallos inyectables |

---

## 5. El borde sin cubrir

Lo que la suite **no** puede alcanzar, por construcción:

- **Todo lo que vive detrás de `#if ANDROID`**: `BluetoothSocket`, streams RFCOMM, permisos, la
  detección real por `DLE EOT`. Solo se prueban las funciones puras extraídas a los dos partials.
- **`MotorDsl.Maui` entero**: TFM de plataforma, no referenciable desde `net10.0`. Quedan sin
  cobertura `SkiaSharpRasterizer`, `PdfRenderer`, `RasterPreviewRenderer`,
  `BitmapEscPosRenderer`, los seis controles y `MauiDiagnosticsReportProvider`.
- **Los samples**: no hay pruebas de UI ni de integración sobre las apps.
- **Hardware real**: no hay pruebas contra una impresora física ni contra un socket TCP vivo.

Los dos primeros huecos son estructurales, no descuidos: cubrirlos exigiría un proyecto de pruebas
con TFM de plataforma y un runner con emulador.

---

## 6. Cómo se ejecuta

En CI (`.github/workflows/ci.yml`, runner `[self-hosted, <etiqueta del runner>]`, .NET 10.0.102):

```bash
dotnet restore src/MotorDsl.Tests/MotorDsl.Tests.csproj
dotnet build   src/MotorDsl.Tests/MotorDsl.Tests.csproj -c Release --no-restore
dotnet test    src/MotorDsl.Tests/MotorDsl.Tests.csproj -c Release --no-build \
  --logger "trx;LogFileName=test-results.trx" --results-directory ./TestResults
```

Los `.trx` se suben como artefacto (retención 7 días) y, si el job falla en un PR, un
`github-script` comenta el PR con el enlace a los logs.

`cd-nuget.yml` vuelve a correr la suite antes de empaquetar: **ningún paquete se publica sin tests
verdes**.

Localmente, el devcontainer hace `dotnet restore` de este mismo proyecto en su `postCreateCommand`
— restaurarlo arrastra por `ProjectReference` los seis proyectos `net10.0`, que es todo lo
compilable en Linux.

Documentación de estrategia y criterios: `docs/08_calidad_y_pruebas/` (estrategia de testing,
criterios de validación, matriz de cobertura, casos de prueba referenciales).
