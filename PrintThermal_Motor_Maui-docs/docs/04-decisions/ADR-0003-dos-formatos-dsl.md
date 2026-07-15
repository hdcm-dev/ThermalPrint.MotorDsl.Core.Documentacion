---
doc_id: ADR-0003
doc_type: adr
title: "ADR-0003: Dos formatos de DSL — classic e integrated"
status: draft
origin: reverse-engineered
confidence: medium
date: 2026-07-14
deciders: [reconstruido]
owner: equipo-motordsl
last_review: 2026-07-14
audience: [dev, arquitectura, agentes-automaticos]
classification: uso-interno
traces: [ADR-0001]
source_ref: v1.0.13 @83677eb
---

# ADR-0003: Dos formatos de DSL — classic e integrated

> `origin: reverse-engineered` — decisión inferida del código en v1.0.13 @83677eb.

## Contexto

Hay dos escenarios de uso distintos: (a) una plantilla reutilizable que se rellena con datos
variables en runtime, y (b) un documento ya resuelto (por ejemplo, generado por un backend o por el
propio diagnóstico) que solo hay que imprimir. Forzar el escenario (b) a pasar por la resolución de
plantillas es innecesario y abre la puerta a errores de binding.

## Decisión

El DSL soporta dos formatos, discriminados por el campo `format`:

- **`template`** (*classic*, default): admite placeholders `{{…}}`, `loop` y `conditional`; se
  resuelve con el `Evaluator` contra datos externos (`IDataProvider`). Invocación de 3 args:
  `Render(template, datos, profile)`.
- **`integrated`**: AST pre-resuelto con datos embebidos; **se salta la etapa `Evaluate`** y se
  **prohíben** placeholders/loops/conditionals. Invocación de 2 args: `Render(json, profile)`.

## Alternativas

- **Solo *classic***: obligaría a envolver todo documento ya resuelto en una plantilla trivial + un
  diccionario de datos vacío.
- **Solo *integrated***: perdería la reutilización de plantillas con datos variables.

## Consecuencias

- (+) El camino *integrated* es más simple y predecible (sin binding que pueda fallar).
- (+) El diagnóstico se imprime como DSL *integrated* generado en código.
- (+) *Integrated* preserva `Style` (align/bold), que *classic* pierde en el `Evaluator` (deriva
  T2): para documentos donde el estilo es crítico, *integrated* es hoy más fiel.
- (–) Dos caminos que mantener y testear; el `format` incorrecto o mezclar constructos entre
  formatos es un error de autor.
- (–) La superficie de `Render` tiene overloads (2 y 3 args) que un integrador debe elegir bien.

Fuente: [ia-db 02](../../../ia-db/indexes/02_dsl-y-modelos.md),
[pieza Parser](../../pieces/MotorDsl.Parser/README.md), GLOSSARY (*Formato classic*/*integrated*).
