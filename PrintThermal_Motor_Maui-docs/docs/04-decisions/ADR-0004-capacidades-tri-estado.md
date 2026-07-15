---
doc_id: ADR-0004
doc_type: adr
title: "ADR-0004: Capacidades de impresora tri-estado y detección best-effort"
status: draft
origin: reverse-engineered
confidence: medium
date: 2026-07-14
deciders: [reconstruido]
owner: equipo-motordsl
last_review: 2026-07-14
audience: [dev, arquitectura, qa, agentes-automaticos]
classification: uso-interno
traces: [ARCH-CC-001]
source_ref: v1.0.13 @83677eb
---

# ADR-0004: Capacidades de impresora tri-estado y detección best-effort

> `origin: reverse-engineered` — decisión inferida del código en v1.0.13 @83677eb.

## Contexto

Las impresoras térmicas Bluetooth de bajo costo responden de forma inconsistente a los sondeos de
estado y capacidades: a veces no contestan por estar ocupadas, no por no soportar la función. Un
modelo binario (`bool soporta`) mentiría en el caso "no contestó", y un sondeo que bloquee o falle
la conexión dejaría inutilizable a la impresora ante el menor ruido.

## Decisión

1. Las capacidades se modelan como **tri-estado** `CapabilitySupport`: `Unknown` (no se sondeó),
   `NotDetected` (se sondeó sin respuesta válida), `Supported` (respondió confirmando). Nunca `bool`.
2. La detección es **best-effort y no bloqueante**: todos los reads se gatean por `Available()` con
   *timeout*; la detección **jamás hace fallar la conexión** (ante error → `Unknown`).
3. Ante status ilegible durante el envío, el transport **degrada** a *pacing* fijo (latch por el
   resto del envío) en vez de abortar.

## Alternativas

- **`bool` por capacidad**: colapsa "desconocido" y "no soportado"; induce decisiones erróneas.
- **Sondeo bloqueante y estricto**: cuelga o rompe la conexión con impresoras ruidosas.

## Consecuencias

- (+) La app puede distinguir "no sé" de "no puede" y decidir en consecuencia
  (`PrintStrategySelector` recomienda `escpos` vs `escpos-bitmap`).
- (+) La impresión es robusta ante feedback intermitente: degrada, no falla.
- (–) El logo NV por `FS q` no tiene query limpia: su confirmación es limitada (deriva T17).
- (–) Más complejidad que un flag; el consumidor debe entender el tri-estado (documentado en
  GLOSSARY y [pieza Printing.Abstractions](../../pieces/MotorDsl.Printing.Abstractions/README.md)).

Fuente: [ia-db 04](../../../ia-db/indexes/04_impresion-transports.md) §3.2, §4,
[crosscutting](../01-architecture/06-crosscutting.md) §4.
