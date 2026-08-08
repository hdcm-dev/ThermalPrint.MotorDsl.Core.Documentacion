---
doc_id: API-CATALOG-001
doc_type: api-catalog
title: Catálogo de APIs y paquetes — MotorDsl
version: 1.0.0
status: draft
origin: reverse-engineered
confidence: high
owner: equipo-motordsl
last_review: 2026-07-14
audience: [dev, arquitectura, agentes-automaticos]
classification: uso-interno
traces: [SYS-MAP-001, ARCH-CNT-001]
source_ref: v1.0.13 @83677eb
---

# Catálogo de APIs y paquetes

## Resumen ejecutivo

MotorDsl **no expone una API de red** (no hay servicio REST; ver
[gap-documental](../gap-documental.md)). Sus "APIs" son las **superficies públicas de sus 7
paquetes NuGet** y los **contratos de extensión** por los que se enchufan renderers y transports.
Este catálogo es el punto de entrada para un integrador: qué paquete referenciar, qué expone y dónde
está su documentación.

## Paquetes publicados

Todos comparten **versión unificada** (última: **1.0.13**), licencia **MIT**, repo
`Aplicada-Streaming/PrintThermal_Motor_Maui`.

| Paquete | TFM | API pública clave | Estado | Doc |
|---|---|---|---|---|
| `MotorDsl.Core` | net10.0 | `IDocumentEngine.Render`, 15 contratos, AST y modelos, `RenderResult` | Activa | [pieza](../../pieces/MotorDsl.Core/README.md) · [api](../../pieces/MotorDsl.Core/api-reference.md) |
| `MotorDsl.Parser` | net10.0 | `DslParser.Parse(string) → DocumentTemplate` | Activa | [pieza](../../pieces/MotorDsl.Parser/README.md) · [api](../../pieces/MotorDsl.Parser/api-reference.md) |
| `MotorDsl.Rendering` | net10.0 | `TextRenderer` (`text`), `EscPosRenderer` (`escpos`), `EscPosCommands` | Activa | [pieza](../../pieces/MotorDsl.Rendering/README.md) · [api](../../pieces/MotorDsl.Rendering/api-reference.md) |
| `MotorDsl.Extensions` | net10.0 | `AddMotorDslEngine`, `MotorDslBuilder` (`AddTemplates`/`AddProfiles`/`AddRenderer<T>`) | Activa | [pieza](../../pieces/MotorDsl.Extensions/README.md) · [api](../../pieces/MotorDsl.Extensions/api-reference.md) |
| `MotorDsl.Printing.Abstractions` | net10.0 | `IThermalPrinterTransport`, `IThermalPrinterService`, `ThermalPrinterService`, `AddMotorDslPrinting` | Activa | [pieza](../../pieces/MotorDsl.Printing.Abstractions/README.md) · [api](../../pieces/MotorDsl.Printing.Abstractions/api-reference.md) |
| `MotorDsl.Bluetooth` | net10.0-android/ios | `BluetoothPrinterTransport` (`Kind="bluetooth"`), `AddBluetoothPrinterTransport` | Activa (Android) | [pieza](../../pieces/MotorDsl.Bluetooth/README.md) · [api](../../pieces/MotorDsl.Bluetooth/api-reference.md) |
| `MotorDsl.Maui` | net10.0-android/ios | 6 controles, renderers `pdf`/`escpos-bitmap`/`raster-preview`, `AddMotorDslMaui` | Activa | [pieza](../../pieces/MotorDsl.Maui/README.md) · [catálogo](../../pieces/MotorDsl.Maui/component-catalog.md) |

## Adopción mínima

```xml
<!-- Con estos dos, el stack MAUI + impresión Bluetooth queda completo -->
<PackageReference Include="MotorDsl.Maui"      Version="1.0.13" />
<PackageReference Include="MotorDsl.Bluetooth" Version="1.0.13" />
```

`MotorDsl.Maui` arrastra `Core`, `Rendering`, `Extensions` y `Printing.Abstractions` como
dependencias transitivas. Guía paso a paso: [usage-guide](../../pieces/MotorDsl.Maui/usage-guide.md);
snippets: [integration-snippets](../../pieces/samples/integration-snippets.md).

## Contratos de extensión (las "APIs" que un integrador implementa)

| Contrato | Paquete | Para qué | Selección | Guía |
|---|---|---|---|---|
| `IRenderer` | Core | Formato de salida nuevo (HTML, otro raster…) | por `Target` (string) | [ia-db 03](../../../ia-db/indexes/03_renderizado-base.md) |
| `IThermalPrinterTransport` | Printing.Abstractions | Medio físico nuevo (USB, BLE, red) | por `Kind` (string) | [extension-guide](../../pieces/MotorDsl.Printing.Abstractions/extension-guide.md) |
| `IBitmapRasterizer` | Core | Rasterizado de imágenes a 1-bit | inyección DI | [ia-db 05](../../../ia-db/indexes/05_maui-ui-renderers.md) |
| `IDiagnosticsReportProvider` | Printing.Abstractions | Provider de diagnóstico propio | `TryAdd` (el consumer prevalece) | [api](../../pieces/MotorDsl.Printing.Abstractions/api-reference.md) |
| `IDataProvider` / `ITemplateProvider` / `IDeviceProfileProvider` | Core | Fuentes de datos/plantillas/perfiles | inyección DI | [ia-db 01](../../../ia-db/indexes/01_nucleo-pipeline.md) |

## Targets de render y Kinds de transport registrados

| `Target` | Renderer | Paquete |
|---|---|---|
| `text` | `TextRenderer` | Rendering |
| `escpos` | `EscPosRenderer` | Rendering |
| `pdf` | `PdfRenderer` | Maui |
| `escpos-bitmap` | `BitmapEscPosRenderer` | Maui |
| `raster-preview` | `RasterPreviewRenderer` | Maui |

| `Kind` | Transport | Paquete | Plataforma |
|---|---|---|---|
| `bluetooth` | `BluetoothPrinterTransport` | Bluetooth | Android (iOS lanza) |
| `usb` / `ble` / `red` | — (roadmap) | — | No implementado |

## Política de versionado

- **SemVer con versión unificada**: los 8 paquetes se publican con el mismo número; un consumidor
  fija una sola versión para todo el stack (ver GLOSSARY: *Versión unificada*).
- La versión **no** vive en los `.csproj`; se inyecta en build/pack. Detalle:
  [`ia-db 08`](../../../ia-db/indexes/08_build-devops.md).
- No hay guía de migración entre mayores (la historia previa a 1.0.13 no está en el CHANGELOG; ver
  [reporte-derivas](../04-decisions/reporte-derivas.md) D9).

## Preguntas guía

- ¿Otro equipo puede integrarse solo con este catálogo + la guía de uso? → Sí para el camino
  canónico (MAUI + Bluetooth). Para extender, con las guías de extensión enlazadas.
- ¿Hay contrato OpenAPI/AsyncAPI? → No aplica: no hay REST ni eventos en la solución.
