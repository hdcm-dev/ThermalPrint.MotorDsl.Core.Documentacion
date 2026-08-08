---
doc_id: DOCS-INDEX-001
doc_type: master-index
title: Documentación de MotorDsl — índice maestro
version: 1.0.0
status: draft
origin: reverse-engineered
confidence: high
owner: equipo-motordsl
last_review: 2026-07-14
audience: [dev, arquitectura, qa, producto, agentes-automaticos]
classification: uso-interno
source_ref: v1.0.13 @83677eb
---

# Documentación de MotorDsl

> **Índice maestro.** Con solo este archivo, un humano entiende qué es la solución y cómo navegar su
> documentación; un agente calcula el gap documental leyendo
> [`docs-manifest.yaml`](docs-manifest.yaml) + el frontmatter de cada `.md`. Toda la documentación
> es **`draft`** reconstruida por ingeniería inversa sobre el origen en **v1.0.13 @83677eb**;
> pendiente de revisión humana para promoverse a `approved`.

## Qué es MotorDsl

Motor de generación y renderizado de documentos para **.NET 10 / .NET MAUI**, orientado a la
**impresión térmica ESC/POS por Bluetooth**. Un documento se describe una vez en un **DSL JSON** y se
materializa en texto, ESC/POS, PDF o preview raster, eligiendo el formato por un **perfil de
dispositivo**. Se distribuye como **8 paquetes NuGet** modulares, extensibles vía *renderers* (por
`Target`) y *transports* (por `Kind`). Detalle: [visión](docs/00-overview/vision.md).

## Cómo navegar

### Empezar aquí según tu rol

| Si sos… | Empezá por |
|---|---|
| **Integrador** (querés imprimir desde tu app MAUI) | [catálogo de APIs](docs/05-apis/catalog.md) → [guía de uso MAUI](pieces/MotorDsl.Maui/usage-guide.md) → [snippets](pieces/samples/integration-snippets.md) |
| **Arquitecto** (querés entender el diseño) | [visión](docs/00-overview/vision.md) → [system-map](docs/00-overview/system-map.md) → [C4 contexto](docs/01-architecture/01-context.md) / [contenedores](docs/01-architecture/02-containers.md) |
| **Desarrollador del motor** (vas a contribuir) | [developer-setup](docs/08-onboarding/developer-setup.md) → [ia-db](../ia-db/README.md) → [ADRs](docs/04-decisions/README.md) |
| **QA** (vas a probar) | [runtime views](docs/01-architecture/04-runtime-views.md) → [ia-db 07 (tests)](../ia-db/indexes/07_tests.md) |
| **Quien va a extender** (transport o renderer nuevo) | [extension-guide](pieces/MotorDsl.Printing.Abstractions/extension-guide.md) → [crosscutting](docs/01-architecture/06-crosscutting.md) |
| **Agente de IA** | [`docs-manifest.yaml`](docs-manifest.yaml) + [ia-db](../ia-db/README.md) + [agent-policy](docs/09-agents/agent-policy.md) |

### Estructura del conjunto documental

```text
PrintThermal_Motor_Maui.Documentacion/
├── ia-db/                          ← base de conocimiento (entrada única + 9 índices)
└── PrintThermal_Motor_Maui-docs/   ← este conjunto documental
    ├── README.md                   ← este índice maestro
    ├── GLOSSARY.md                 ← vocabulario controlado
    ├── docs-manifest.yaml          ← manifiesto máquina-legible (piezas, types, gap)
    ├── docs/
    │   ├── 00-overview/            ← vision.md, system-map.md
    │   ├── 01-architecture/        ← C4 (contexto, contenedores), runtime-views, crosscutting
    │   ├── 04-decisions/           ← ADRs reconstruidos + reporte-derivas.md
    │   ├── 05-apis/                ← catalog.md (paquetes y contratos de extensión)
    │   ├── 08-onboarding/          ← developer-setup.md
    │   ├── 09-agents/              ← agent-policy.md
    │   └── gap-documental.md       ← qué se documentó y qué no
    └── pieces/                     ← doc por pieza (README + perfil de su type)
        ├── MotorDsl.Core/          ├── MotorDsl.Printing.Abstractions/
        ├── MotorDsl.Parser/        ├── MotorDsl.Bluetooth/
        ├── MotorDsl.Rendering/     ├── MotorDsl.Maui/
        ├── MotorDsl.Extensions/    └── samples/
```

## Documentación por pieza

| Pieza | `type` | Documentos |
|---|---|---|
| [MotorDsl.Core](pieces/MotorDsl.Core/README.md) | library | README · [api-reference](pieces/MotorDsl.Core/api-reference.md) |
| [MotorDsl.Parser](pieces/MotorDsl.Parser/README.md) | library | README · [api-reference](pieces/MotorDsl.Parser/api-reference.md) |
| [MotorDsl.Rendering](pieces/MotorDsl.Rendering/README.md) | library | README · [api-reference](pieces/MotorDsl.Rendering/api-reference.md) |
| [MotorDsl.Extensions](pieces/MotorDsl.Extensions/README.md) | library | README · [api-reference](pieces/MotorDsl.Extensions/api-reference.md) |
| [MotorDsl.Printing.Abstractions](pieces/MotorDsl.Printing.Abstractions/README.md) | library | README · [api-reference](pieces/MotorDsl.Printing.Abstractions/api-reference.md) · [extension-guide](pieces/MotorDsl.Printing.Abstractions/extension-guide.md) |
| [MotorDsl.Bluetooth](pieces/MotorDsl.Bluetooth/README.md) | library | README · [api-reference](pieces/MotorDsl.Bluetooth/api-reference.md) · [platform-notes](pieces/MotorDsl.Bluetooth/platform-notes.md) |
| [MotorDsl.Maui](pieces/MotorDsl.Maui/README.md) | component-library | README · [component-catalog](pieces/MotorDsl.Maui/component-catalog.md) · [usage-guide](pieces/MotorDsl.Maui/usage-guide.md) |
| [samples](pieces/samples/README.md) | sample-app | README · [integration-snippets](pieces/samples/integration-snippets.md) |

## Estado documental (gap)

- **Piezas**: 7 publicables + samples, todas documentadas con el perfil de su `type`.
- **Nivel solución**: visión, C4 (L1/L2), runtime views, crosscutting, catálogo de APIs, 4 ADRs
  reconstruidos, reporte de derivas.
- **Omisiones declaradas** (arc42): `02-requirements`, `03-data`, `05-deployment`,
  `06-security-compliance`, `07-operations`. Motivos en [gap-documental](docs/gap-documental.md).
- **Derivas detectadas**: 17 entre fuentes + 17 de comportamiento del código, en el
  [reporte de derivas](docs/04-decisions/reporte-derivas.md).

## Trazabilidad y confianza

- Cada documento declara `origin`, `confidence` y `source_ref` en su frontmatter.
- Toda afirmación es trazable a la [ia-db](../ia-db/README.md) o a una ruta del origen; los `#Lx-Ly`
  valen para **v1.0.13 @83677eb**.
- Contradicciones no resueltas → [reporte de derivas](docs/04-decisions/reporte-derivas.md).

## Cómo se generó y cómo se regenera

- **Generado por**: `/IA.Prompting.Templates/Tool-Prompts/Documentar-Fuentes-Software.md` (Profile
  `Solution-Documentation`), en 5 fases: indexar → clasificar → documentar por pieza → nivel
  solución → consolidar.
- **Regenerar/actualizar**: reejecutar el Tool-Prompt (modo incremental) sobre un origen más nuevo;
  la ia-db guía el análisis y su [manifiesto de generación](../ia-db/README.md#manifiesto-de-generación)
  fija alcance y fuentes.
