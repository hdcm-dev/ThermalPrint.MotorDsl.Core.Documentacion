# 00 — Índice maestro

> **Propósito**: visión general de MotorDsl como sistema — qué resuelve, cómo se reparte en paquetes,
> qué decisiones estructurales lo condicionan y dónde está cada cosa.
> **Versión del índice**: 3.0 — repo de código en `main` @ `0f8413d` (2026-09-24); base anterior `e688f3c`.
> **Fuentes primarias**: `README.md`, `CHANGELOG.md`, `PrintThermalDriver.slnx`, `src/*/*.csproj`,
> `PrintThermal_Motor_Maui-docs/docs/04-decisions/` (en el repo de documentación).

---

## 1. Qué resuelve

Una app .NET MAUI que tiene que imprimir un comprobante en una térmica de bajo costo enfrenta tres
problemas juntos: describir el documento sin recompilar la app, adaptarlo al ancho y a las
capacidades del dispositivo concreto, y hablarle a la impresora por un canal físico que varía por
plataforma. MotorDsl separa los tres: un **DSL JSON** describe el documento, un **pipeline** lo
adapta y lo convierte a la salida pedida, y un **transport** lo entrega.

Lo que la librería **no** hace: no persiste nada, no expone REST, no descubre impresoras de red, no
gestiona la UI de la app más allá de los controles que ofrece `MotorDsl.Maui`.

---

## 2. Los 8 paquetes

| Paquete | TFM | Rol | Depende de |
|---|---|---|---|
| `MotorDsl.Core` | `net10.0` | Contratos, modelos/AST, `Evaluator`, `LayoutEngine`, validadores, providers en memoria | — |
| `MotorDsl.Parser` | `net10.0` | `DslParser`: JSON → `DocumentTemplate` | Core |
| `MotorDsl.Rendering` | `net10.0` | `EscPosRenderer`, `TextRenderer`, `EscPosCommands` | Core |
| `MotorDsl.Extensions` | `net10.0` | `AddMotorDslEngine()` + `MotorDslBuilder` (fluent DI) | Core, Parser, Rendering |
| `MotorDsl.Printing.Abstractions` | `net10.0` | `IThermalPrinterTransport`, `IThermalPrinterService`, `ThermalPrinterService`, capacidades, chunking | Core |
| `MotorDsl.Network` | `net10.0` | Transport TCP 9100 (RAW / JetDirect) | Printing.Abstractions |
| `MotorDsl.Bluetooth` | `net10.0-android;net10.0-ios` | Transport BT Classic SPP. En iOS lanza `PlatformNotSupportedException` | Printing.Abstractions |
| `MotorDsl.Maui` | `net10.0-android;net10.0-ios` | Controles MAUI, renderers PDF/bitmap/preview, `MauiPrintErrorHandler`, diagnóstico | Core, Rendering, Extensions, Printing.Abstractions |

Metadatos verificables en cada `src/MotorDsl.*/MotorDsl.*.csproj`: `PackageId`, `Description`,
`PackageLicenseExpression` = MIT, `RepositoryUrl` común. `Authors` es `Fernando Rafael Filipuzzi`
en siete paquetes y `UTN FRP TUP Aplicada 2025` en `MotorDsl.Bluetooth` — divergencia real, no
error de índice ([`src/MotorDsl.Bluetooth/MotorDsl.Bluetooth.csproj`](../../../PrintThermal_Motor_Maui/src/MotorDsl.Bluetooth/MotorDsl.Bluetooth.csproj)).

### Grafo de dependencias

```text
                       Core
                        │
        ┌───────────────┼───────────────┬──────────────────────┐
     Parser         Rendering    Printing.Abstractions         │
        │               │           │            │             │
        └──── Extensions ┘        Network    Bluetooth          │
                  │                                            │
                  └────────────────── Maui ────────────────────┘
```

`MotorDsl.Maui` es la única pieza que depende de las cuatro ramas a la vez, y por eso es el paquete
que una app instala primero: arrastra `Core`, `Rendering`, `Extensions` y `Printing.Abstractions`
como dependencias transitivas ([`README.md`](../../../PrintThermal_Motor_Maui/README.md), sección
«TL;DR»).

---

## 3. El pipeline en una pantalla

```text
 string DSL           DocumentTemplate      EvaluatedDocument     LayoutedDocument      RenderResult
    │                       │                      │                     │                   │
    ├── DslParser ─────────►├── Evaluator ────────►├── LayoutEngine ────►├── IRenderer ─────►│
    │                       │                      │                     │                   │
  valida             AST tipado           placeholders/loops     líneas, wrap,        string | byte[]
 TemplateValidator                        /condiciones ya         alineación,          + Warnings
                                          resueltos               metadata             + Errors
```

Las tres validaciones son **opcionales por construcción** (parámetros con default `null` en el
constructor de `DocumentEngine`), pero `AddMotorDslEngine()` las registra siempre. Detalle en
[`01_nucleo-pipeline.md`](01_nucleo-pipeline.md).

---

## 4. Decisiones estructurales

| # | Decisión | Consecuencia práctica | ADR |
|---|---|---|---|
| D1 | Pipeline en etapas con representaciones intermedias | Cada etapa se testea y se sustituye sola; agregar un formato de salida no toca el parser | ADR-0001 |
| D2 | Extensibilidad por strings: `Target` (renderers) y `Kind` (transports) | Un renderer o transport nuevo se registra por DI sin tocar el núcleo | ADR-0002 |
| D3 | Dos formatos de DSL: `template` e `integrated` | El documento pre-resuelto salta la etapa Evaluate; el parser y el validador prohíben loops/condicionales ahí | ADR-0003 |
| D4 | Capacidades de impresora **tri-estado** (`Unknown` / `NotDetected` / `Supported`) | «No contestó» nunca se confunde con «no soporta»; la detección jamás hace fallar la conexión | ADR-0004 |
| D5 | El transport de red se empaqueta como `net10.0` **puro** | Habilita impresión en iOS sin que ninguna máquina Apple participe del build, y lo hace referenciable desde los tests | ADR-0005 |

Los ADR viven en el repositorio de documentación:
`PrintThermal_Motor_Maui-docs/docs/04-decisions/`. Los cuatro primeros están marcados
`origin: reverse-engineered` (inferidos del código en `v1.0.13`, pendientes de validación humana);
el quinto es `origin: human`, derivado de
`Analisis/03-Analisis-IOs/Nuget-Multiplaforma.md`.

---

## 5. Restricciones de plataforma

| Capacidad | Android | iOS | Escritorio / tests |
|---|---|---|---|
| Motor completo (parse → render) | ✅ | ✅ | ✅ |
| Impresión Bluetooth Classic SPP | ✅ | ❌ `PlatformNotSupportedException` | ❌ |
| Impresión por red TCP 9100 | ✅ | ✅ | ✅ |
| Controles y renderers MAUI | ✅ | ✅ | ❌ (TFM de plataforma) |

Apple no expone el perfil SPP a apps de terceros: por eso existe `MotorDsl.Network` y por eso una
app iOS que imprima por red **debe** declarar `NSLocalNetworkUsageDescription` en su `Info.plist`
—sin esa clave iOS 14+ termina la app sin mensaje útil ([`README.md`](../../../PrintThermal_Motor_Maui/README.md),
[`CHANGELOG.md`](../../../PrintThermal_Motor_Maui/CHANGELOG.md) § Unreleased).

---

## 6. Dónde está cada cosa

| Busco… | Ruta | Índice |
|---|---|---|
| Contratos del motor | `src/MotorDsl.Core/Contracts/` (15 interfaces) | 01 |
| Orquestador del pipeline | `src/MotorDsl.Core/Engine/DocumentEngine.cs` | 01 |
| Nodos del AST | `src/MotorDsl.Core/Models/` | 02 |
| Gramática JSON del DSL | `src/MotorDsl.Parser/DslParser.cs` + `Validation/TemplateValidator.cs` | 02 |
| Bytes ESC/POS | `src/MotorDsl.Rendering/EscPosCommands.cs` | 03 |
| Orquestador de impresión con retry | `src/MotorDsl.Printing.Abstractions/Services/ThermalPrinterService.cs` | 04 |
| Transports concretos | `src/MotorDsl.Bluetooth/`, `src/MotorDsl.Network/` | 04 |
| Controles XAML | `src/MotorDsl.Maui/Controls/` | 05 |
| Apps de ejemplo | `samples/` (5 apps) | 06 |
| Tests | `src/MotorDsl.Tests/` (37 archivos `.cs`, conteo estático) | 07 |
| CI/CD | `.github/workflows/` (7 workflows) | 08 |
| Build local de samples desde Linux (Docker efímero) | `scripts/local-devcontainer/` | 08 |
| Cola del ticket (`end_of_ticket`) | `src/MotorDsl.Rendering/EscPosCommands.cs` | 03 |
| Confirmación de impresión BT (`GS I 67`) | `src/MotorDsl.Bluetooth/BluetoothPrinterTransport.cs`, `src/MotorDsl.Core/Models/PrintNotConfirmedException.cs` | 04 |
| Casos de uso, reglas de negocio, sprints | `docs/` (12 carpetas) | 09 |

---

## 7. Versiones publicadas (según `CHANGELOG.md`)

La versión no vive en los `.csproj`: se inyecta en pack con `-p:PackageVersion` / `-p:MotorDslVersion`
([`CHANGELOG.md`](../../../PrintThermal_Motor_Maui/CHANGELOG.md), encabezado).

| Versión | Fecha | Hito en el dominio global | Detalle |
|---|---|---|---|
| 1.0.13 | 2026-07-13 | Primera versión registrada en el CHANGELOG | — |
| 1.0.15 | 2026-08-26 | `MotorDsl.Network` entra como **octavo paquete** (habilita iOS) | 04 |
| 1.0.16 | 2026-08-26 | `WriteTimeout` en BT; API de fase 4 publicada | 04, 06 |
| 1.0.17 | 2026-08-27 | **Cambio de comportamiento**: cola por defecto `GS V 1` (corte parcial) en lugar de `GS V 0`; capability `end_of_ticket` en `DeviceProfile`; barrera de drenaje `GS I 67` en BT con `PrinterProfile.ConfirmPrintTimeoutMs` (default 120 s, `0` la desactiva) | 03, 04 |
| Unreleased | — | `scripts/local-devcontainer/` (APK de los cinco samples en contenedor Docker) | 08 |

Reparto de responsabilidades que fija 1.0.17: `DeviceProfile` describe **qué y cómo se renderiza**
(la cola la emite el renderer); `PrinterProfile`, **las temporizaciones del envío**
([`CHANGELOG.md`](../../../PrintThermal_Motor_Maui/CHANGELOG.md) § 1.0.17; `ConfirmPrintTimeoutMs = 120_000` en `src/MotorDsl.Printing.Abstractions/Models/PrinterProfile.cs`).

---

## 8. Estado y deuda declarada

- **`MotorDsl.Nuget.Integrated.MultaApp` volvió a `PackageReference` 1.0.17** (antes `ProjectReference`
  por API no publicada); vuelve a validar los paquetes publicados. No referencia `MotorDsl.Network`
  ([`samples/MotorDsl.Nuget.Integrated.MultaApp/MotorDsl.Nuget.Integrated.MultaApp.csproj`](../../../PrintThermal_Motor_Maui/samples/MotorDsl.Nuget.Integrated.MultaApp/MotorDsl.Nuget.Integrated.MultaApp.csproj); ver 06).
- **Roadmap abierto** ([`README.md`](../../../PrintThermal_Motor_Maui/README.md) § Roadmap):
  transport USB, transport BLE, descubrimiento mDNS/Bonjour, raster nearest-neighbor real con
  `SKCanvasView`, EAN-13 nativo en raster preview y PDF (hoy caen a texto).
- **Gap documental declarado** en `docs-manifest.yaml` § `gap` (repo de documentación): sin
  `02-requirements` formales, sin `03-data` (el «modelo» es el AST), sin `05-deployment`, sin
  `06-security-compliance`, sin `07-operations`, sin changelog por paquete, sin OpenAPI, sin guía
  de migración.
- **Divergencia del manifest con el código**: `docs-manifest.yaml` dice que el CHANGELOG cubre «solo
  v1.0.13» y que no hay breaking changes documentados; el CHANGELOG actual registra 1.0.15–1.0.17 y
  marca 1.0.17 como cambio de comportamiento. Las ADR 0001–0005 no cubren las decisiones de 1.0.17
  (cola del ticket, barrera de drenaje).
- Lo anterior es análisis estático: no hay SDK .NET en el host de indexado; no se afirma que
  compile ni que los tests pasen.
