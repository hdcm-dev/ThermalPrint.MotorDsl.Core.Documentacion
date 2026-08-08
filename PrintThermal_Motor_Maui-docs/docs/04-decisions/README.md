---
doc_id: ADR-INDEX-001
doc_type: adr-index
title: Índice de decisiones de arquitectura (ADR) — MotorDsl
version: 1.0.0
status: draft
origin: reverse-engineered
confidence: medium
owner: equipo-motordsl
last_review: 2026-07-14
audience: [dev, arquitectura, agentes-automaticos]
classification: uso-interno
source_ref: v1.0.13 @83677eb
---

# Decisiones de arquitectura (ADR)

## Resumen ejecutivo

Registro de las decisiones estructurales de MotorDsl. Como la solución **no** tenía ADRs formales,
estos se **reconstruyeron por ingeniería inversa** a partir del código (`origin:
reverse-engineered`, `confidence: medium`): documentan el *porqué* inferido de un diseño ya
existente, no una decisión tomada en el momento. Un humano debe validarlos antes de promoverlos a
`approved`.

> Los ADR son **inmutables** una vez aprobados: una decisión superada se marca `superseded by
> ADR-NNNN`, no se edita (Marco §11.3).

## Catálogo

| ADR | Título | Estado | Traza |
|---|---|---|---|
| [ADR-0001](ADR-0001-pipeline-en-etapas.md) | Pipeline en etapas con representaciones intermedias | draft (reconstruido) | ARCH-CNT-001 |
| [ADR-0002](ADR-0002-extensibilidad-target-kind.md) | Extensibilidad por `Target` (renderers) y `Kind` (transports) | draft (reconstruido) | ARCH-CC-001 |
| [ADR-0003](ADR-0003-dos-formatos-dsl.md) | Dos formatos de DSL: *classic* e *integrated* | draft (reconstruido) | — |
| [ADR-0004](ADR-0004-capacidades-tri-estado.md) | Capacidades de impresora tri-estado y detección best-effort | draft (reconstruido) | — |
| [ADR-0005](ADR-0005-transport-red-net10-puro.md) | Transport de red en un paquete `net10.0` puro para habilitar iOS | draft | ADR-0002, ARCH-CC-001 |

## Decisiones históricas no reconstruidas

El origen contiene `docs/05_arquitectura_tecnica/decisiones-arquitectura_v1.0.md`, pero su contenido
corresponde al **proyecto consumidor** ("Sistema de Gestión de Reclamos"), no al motor (ver
[reporte-derivas](reporte-derivas.md) D11). No se reutilizó aquí.
