---
doc_id: GAP-001
doc_type: gap-report
title: Reporte de gap documental — MotorDsl
version: 1.0.0
status: draft
origin: reverse-engineered
confidence: high
owner: equipo-motordsl
last_review: 2026-07-14
audience: [dev, arquitectura, qa, agentes-automaticos]
classification: uso-interno
source_ref: v1.0.13 @83677eb
---

# Reporte de gap documental

## Resumen ejecutivo

Qué documentó este pipeline, qué **no**, y por qué. Un agente calcula el gap de forma determinística
leyendo [`docs-manifest.yaml`](../docs-manifest.yaml) + el frontmatter de cada `.md`; este documento
lo explica para humanos. Todo lo generado está en `status: draft`, pendiente de revisión.

## Cobertura por pieza (required_docs vs generados)

| Pieza | `type` | Requeridos | Generados | Gap |
|---|---|---|---|---|
| MotorDsl.Core | library | readme, api-reference, usage-guide | readme, api-reference | `usage-guide` (cubierto por snippets de samples) |
| MotorDsl.Parser | library | readme, api-reference, usage-guide | readme, api-reference | `usage-guide` |
| MotorDsl.Rendering | library | readme, api-reference, usage-guide | readme, api-reference | `usage-guide` |
| MotorDsl.Extensions | library | readme, api-reference, usage-guide | readme, api-reference | `usage-guide` |
| MotorDsl.Printing.Abstractions | library | readme, api-reference, usage-guide, extension-guide | readme, api-reference, extension-guide | `usage-guide` |
| MotorDsl.Bluetooth | library | readme, api-reference, platform-notes | readme, api-reference, platform-notes | — completo |
| MotorDsl.Maui | component-library | readme, component-catalog, usage-guide | readme, component-catalog, usage-guide | — completo |
| MotorDsl.Tests | test-suite | test-inventory | (ia-db 07) | — cubierto por índice |
| samples | sample-app | readme, integration-snippets | readme, integration-snippets | — completo |

> La `usage-guide` por librería individual se consideró cubierta por la
> [guía de uso MAUI](../pieces/MotorDsl.Maui/usage-guide.md) y los
> [snippets de integración](../pieces/samples/integration-snippets.md), que muestran el stack en
> conjunto. Generar una por paquete queda como mejora, no como bloqueante.

## Carpetas del Marco §5.2 omitidas (omisión declarada, estilo arc42)

| Carpeta | Motivo de omisión |
|---|---|
| `02-requirements/` | No se reconstruyeron requisitos formales `RF-`/`RNF-`. Existe doc funcional previa extensa en el origen (`docs/02_especificacion_funcional`: 32 `CU-`, reglas `RN-`/`RC-`, `NB-`), **mapeada** en [`ia-db 09`](../../ia-db/indexes/09_docs-existentes.md) pero no re-derivada a este árbol. |
| `03-data/` | La solución **no tiene base de datos**. Su "modelo de datos" es el AST del DSL, documentado en [`ia-db 02`](../../ia-db/indexes/02_dsl-y-modelos.md). No aplica §14 (diccionario/ER) ni §15 (matriz de casos). |
| `05-deployment/` | Son librerías, no hay infraestructura desplegable. El build/CI/CD está en [`ia-db 08`](../../ia-db/indexes/08_build-devops.md). |
| `06-security-compliance/` | Dominio **no regulado** (`solution.regulated: false`). Sin *threat model* formal; las notas de privacidad están en [crosscutting §7](01-architecture/06-crosscutting.md). |
| `07-operations/` | Sin *runbooks*: no hay servicios en ejecución que operar. |

## Documentos no generados (y por qué)

| No generado | Motivo |
|---|---|
| `openapi.yaml` / AsyncAPI | No hay REST API ni eventos en la solución (la API que consumen los samples es externa). |
| CHANGELOG por paquete | Existe un `CHANGELOG.md` único a nivel solución y **solo cubre 1.0.13** (deriva D9). Reconstruir la historia 1.0.0–1.0.12 requiere decisión humana. |
| Guía de migración entre mayores | Sin breaking changes documentados; historia previa ausente. |
| `test-data-matrix` / fixtures (§15) | No solicitado (`{énfasis}` no especificado) y sin base de datos de la cual derivar. |

## Insumos no provistos

- **`{conexiones}`**: no aplica — la solución no tiene base de datos. No hubo acceso a datos que
  documentar ni riesgo de PII real en los entregables (los ejemplos son sintéticos).
- **`{énfasis}`**: no especificado en la invocación. Se derivó del `type` de cada pieza (Marco §7):
  para librerías → API pública, guía de uso e implementación con snippets (§13). Los snippets de
  integración se extrajeron de los samples reales.

## Estado global

- **7 piezas publicables + samples**: documentadas (README + perfil de su `type`).
- **Nivel solución**: visión, C4 (contexto/contenedores), runtime views, crosscutting, catálogo de
  APIs, 4 ADRs reconstruidos, reporte de derivas.
- **ia-db**: 9 índices + entrada única, sincronizada.
- **Todo en `draft`**: la promoción a `approved` es humana (Marco §12.4).

## Preguntas guía

- ¿Qué falta para cerrar `02-requirements`? → Re-derivar los `CU-`/`RN-` previos (ya mapeados) a
  requisitos `RF-`/`RNF-` con matriz de trazabilidad. Es el gap de mayor valor pendiente.
- ¿Qué falta para un release NuGet confiable? → Resolver las derivas D1/D3/D9 del
  [reporte de derivas](04-decisions/reporte-derivas.md).
