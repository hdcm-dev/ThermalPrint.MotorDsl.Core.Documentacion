---
doc_id: ADR-0001
doc_type: adr
title: "ADR-0001: Pipeline en etapas con representaciones intermedias"
status: draft
origin: reverse-engineered
confidence: medium
date: 2026-07-14
deciders: [reconstruido]
owner: equipo-motordsl
last_review: 2026-07-14
audience: [dev, arquitectura, agentes-automaticos]
classification: uso-interno
traces: [ARCH-CNT-001, ARCH-RTV-001]
source_ref: v1.0.13 @83677eb
---

# ADR-0001: Pipeline en etapas con representaciones intermedias

> `origin: reverse-engineered` — decisión inferida del código en v1.0.13 @83677eb, no registrada en
> su momento. Pendiente de validación humana.

## Contexto

MotorDsl debe convertir un DSL JSON en salidas heterogéneas (texto, ESC/POS, PDF, preview) para
distintos dispositivos. Mezclar parseo, resolución de datos, cálculo de layout y emisión de bytes en
un solo paso ataría cada formato de salida al DSL y haría intratable el soporte multi-dispositivo.

## Decisión

El motor procesa en **etapas con representaciones intermedias explícitas**, cada una con su contrato:

`DSL JSON → (IDslParser) → DocumentTemplate → (IEvaluator) → EvaluatedDocument → (ILayoutEngine) → LayoutedDocument → (IRenderer) → RenderResult`

Los renderers consumen el `LayoutedDocument` (texto ya *wrapeado* + `DeviceMetadata` por nodo) y
**no recorren el AST**: toda la lógica de negocio del documento queda resuelta aguas arriba.

## Alternativas

- **Render directo desde el AST**: cada renderer reimplementaría wrapping, alineación y degradación
  → duplicación y divergencia entre formatos.
- **Un único modelo mutable compartido**: acoplaría etapas y dificultaría testear cada una en
  aislamiento.

## Consecuencias

- (+) Cada etapa se testea por separado; los renderers son simples (leen `LayoutInfo` + metadata).
- (+) Agregar un renderer no toca parser/evaluator/layout.
- (+) El formato *integrated* puede **saltarse** la etapa `Evaluator` reusando el resto (ver
  [ADR-0003](ADR-0003-dos-formatos-dsl.md)).
- (–) Más tipos y copias intermedias; en el camino *classic* la copia del `Evaluator` **pierde**
  `Style` e `Id`/`Version` (derivas T1, T2 en [reporte-derivas](reporte-derivas.md)).
- (–) Los *warnings* de una etapa no siempre se propagan al `RenderResult` (deriva T3).

Fuente: [ia-db 01](../../../ia-db/indexes/01_nucleo-pipeline.md),
[runtime-views](../01-architecture/04-runtime-views.md).
