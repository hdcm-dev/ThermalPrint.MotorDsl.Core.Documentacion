---
doc_id: ADR-0002
doc_type: adr
title: "ADR-0002: Extensibilidad por Target (renderers) y Kind (transports)"
status: draft
origin: reverse-engineered
confidence: medium
date: 2026-07-14
deciders: [reconstruido]
owner: equipo-motordsl
last_review: 2026-07-14
audience: [dev, arquitectura, agentes-automaticos]
classification: uso-interno
traces: [ARCH-CC-001, API-CATALOG-001]
source_ref: v1.0.13 @83677eb
---

# ADR-0002: Extensibilidad por Target (renderers) y Kind (transports)

> `origin: reverse-engineered` — decisión inferida del código en v1.0.13 @83677eb.

## Contexto

El roadmap del producto contempla nuevos formatos de salida y nuevos canales físicos (USB, BLE,
red). Si el motor conociera cada formato/canal por tipo concreto, cada adición obligaría a modificar
el núcleo y a recompilar a los consumidores.

## Decisión

Extensibilidad por **dos registries basados en string, ortogonales**:

- **Salida** → `IRenderer` con una propiedad `Target` (string). `RendererRegistry` lo resuelve; el
  `DeviceProfile` elige el `Target`.
- **Canal** → `IThermalPrinterTransport` con una propiedad `Kind` (string). `ThermalPrinterService`
  enruta el `PrinterDevice` al transport cuyo `Kind` coincide.

Ambos se registran por inyección de dependencias (`AddRenderer<T>`, `AddSingleton` para transports —
el servicio acepta **varios** transports a la vez).

## Alternativas

- **`enum` de formatos/canales**: cerrado; agregar uno es un breaking change del núcleo.
- **Reflexión/descubrimiento por convención**: mágico y difícil de auditar.

## Consecuencias

- (+) Un formato o canal nuevo es un tipo nuevo + un registro DI; el núcleo no cambia.
- (+) Los dos ejes no se cruzan: un renderer ignora el canal y un transport ignora el contenido.
- (–) Un `Target` mal escrito **no** falla: `RendererRegistry` cae en silencio a `text` (deriva T4
  en [reporte-derivas](reporte-derivas.md)) — el precio de resolver por string sin validación.
- (–) La correspondencia `Target`/`Kind` ↔ implementación no es verificable en compilación.

Fuente: [extension-guide](../../pieces/MotorDsl.Printing.Abstractions/extension-guide.md),
[crosscutting](../01-architecture/06-crosscutting.md).
