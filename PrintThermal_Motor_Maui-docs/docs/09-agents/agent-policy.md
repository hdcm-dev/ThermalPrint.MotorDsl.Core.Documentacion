---
doc_id: AGENT-POLICY-001
doc_type: agent-policy
title: Política de agentes documentales — MotorDsl
version: 1.0.0
status: draft
origin: reverse-engineered
confidence: high
owner: equipo-motordsl
last_review: 2026-07-14
audience: [agentes-automaticos, dev, arquitectura]
classification: uso-interno
source_ref: v1.0.13 @83677eb
---

# Política de agentes documentales — MotorDsl

> Perímetro de acción de cualquier agente que genere o actualice esta documentación
> (Marco §12.4). Precondición de cualquier otra acción.

1. Los agentes crean y actualizan documentos **solo** en `status: draft`. La promoción
   `draft → approved` la ejecuta un humano (revisor registrado en el PR).
2. Toda la documentación vive bajo `PrintThermal_Motor_Maui.Documentacion/`. El código fuente de
   `PrintThermal_Motor_Maui` es **solo lectura**: ningún agente lo modifica.
3. Los agentes **nunca** modifican: el `CHANGELOG.md` del origen, este `GLOSSARY.md` sin PR
   revisado, ni ninguna evidencia histórica.
4. Contenido inferido lleva `origin: reverse-engineered` (o `ai-assisted`) y `confidence` en el
   frontmatter. Toda afirmación es trazable a la ia-db o a una ruta del origen.
5. Ante una contradicción entre fuentes (código ↔ doc previa ↔ README), el agente la **reporta**
   en [`reporte-derivas.md`](../04-decisions/reporte-derivas.md); no elige una versión en silencio.
6. Los `#Lx-Ly` de las citas valen para **v1.0.13 @83677eb**. Un agente que actúe sobre un origen
   más nuevo reverifica antes de recomendar, y actualiza la ia-db de forma incremental.
7. Ningún agente promueve su propio output ni hace `commit`, `push` o `pull request`.
