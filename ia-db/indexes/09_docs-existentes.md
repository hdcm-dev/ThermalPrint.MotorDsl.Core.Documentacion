# 09 — Mapa de documentación existente

> **Propósito**: dónde está cada documento del proyecto —en el repositorio indexado y en el
> repositorio de documentación hermano— para poder ir a la fuente sin recorrer los árboles.
> Este índice **mapea**, no resume: el contenido de cada documento vive en su archivo.
> **Fuentes primarias**: árbol de `docs/` en `ThermalPrint.MotorDsl.Core`, árbol de
> `ThermalPrint.MotorDsl.Core.Documentacion`, `PrintThermal_Motor_Maui-docs/docs-manifest.yaml`.

---

## 1. Los dos repositorios

| Repositorio | Contenido | Rol |
|---|---|---|
| `/DEV/ThermalPrint.MotorDsl.Core` | Código, `docs/` (12 carpetas, ~128 archivos), samples, scripts | **Indexado** por esta ia-db |
| `/DEV/ThermalPrint.MotorDsl.Core.Documentacion` | Documentación derivada (`PrintThermal_Motor_Maui-docs/`), análisis, PROMPTs, esta `ia-db/` | **Aloja** la ia-db; su contenido no fue indexado (fuera del alcance de la invocación) |

---

## 2. `docs/` en el repositorio indexado

| Carpeta | Archivos | Contenido |
|---|---|---|
| `00_contexto/` | 4 | Visión de producto, alcance del proyecto, compatibilidad de plataformas (`v1.0` y `v1.1`) |
| `01_necesidades_negocio/` | 7 | Documento paraguas + 6 necesidades **NB-01…NB-06** (desacople, estandarización, cambios sin código, multi-dispositivo, reducción de costos, reutilización) |
| `02_especificacion_funcional/` | 51 | **32 casos de uso CU-01…CU-32** (algunos con `v2.0`), modelo conceptual, 6 reglas conceptuales **RC-01…RC-06**, 4 reglas de negocio **RN-01…RN-04**, procesos |
| `03_ux-ui/` | 4 | Experiencia de uso del motor, representación del documento en ESC/POS y en vista previa, wireframes |
| `04_prompts_ai/` | 1 | Prompt de clasificación de documento |
| `05_arquitectura_tecnica/` | 11 | Arquitectura de solución (`v1.0`/`v1.1`), contratos del motor, decisiones, extensibilidad (`v1.0`/`v1.1`), flujo de ejecución, guía de uso (`v1.0`/`v1.1`), modelo de datos lógico, modelo lógico de ejecución |
| `06_backlog-tecnico/` | 1 | Backlog técnico |
| `07_plan-sprint/` | 8 | Planes de iteración **sprint-01…sprint-08** |
| `08_calidad_y_pruebas/` | 6 | Estrategia de calidad y de testing, criterios de validación, casos referenciales, matriz de cobertura, guía de testing de extensibilidad |
| `09_devops/` | 4 | Pipeline CI/CD, estrategia de versionado, entornos de deploy, guía de publicación NuGet |
| `10_developer_guide/` | 18 | **La guía práctica**: formato DSL, perfiles de impresora, integración MAUI, componentes UX, transports y extensibilidad, render pixelado y PDF, soporte de imágenes térmicas, diagnóstico, integración API REST, conceptos fundamentales + 5 plantillas JSON de ejemplo |
| `11_examples/` | 13 | 4 ejemplos narrados + logos de prueba (`.bmp` / `.base64`) |

Punto de entrada: `docs/README.md` (visión general, stack, flujo de desarrollo, Definition of Done).

### Cuándo ir a `docs/` en vez de a un índice de esta base

| Pregunta | Ir a |
|---|---|
| Sintaxis exacta de un nodo DSL, con todos sus ejemplos | `docs/10_developer_guide/formato-dsl-templates.md` |
| Cómo medir el ancho real de una impresora / configurar codepage | `docs/10_developer_guide/formato-perfiles-impresora.md` |
| Escribir un transport nuevo, paso a paso | `docs/10_developer_guide/transports-y-extensibilidad.md` |
| Requisito funcional formal (qué debía hacer el motor y por qué) | `docs/02_especificacion_funcional/casos-de-uso/CU-XX-*.md` |
| Qué se hizo en cada sprint | `docs/07_plan-sprint/plan-iteracion_sprint-NN_v1.0.md` |

### Convenciones de la documentación

- **Sufijo de versión en el nombre**: `_v1.0`, `_v1.1`. Cuando conviven dos, **la mayor es la
  vigente** y la menor se conserva como histórica (así lo declara `docs/README.md` para
  `extensibilidad-motor`). Afecta a `compatibilidad-plataformas`, `arquitectura-solucion`,
  `extensibilidad-motor`, `guia-uso-libreria`, y a los CU `06`, `09`, `21`, `24`, `25`, `26`.
- **Trazabilidad en el código**: muchos archivos `.cs` citan en su XML-doc el sprint, el ticket
  (`TK-nn`) y el caso de uso (`CU-nn`) que los originan. Ese es el puente entre código y
  especificación funcional.
- **Archivos duplicados detectados**: `docs/10_developer_guide/` contiene
  `soporte-imagenes-termicas.md` y `soporte_imagenes_termicas.md` (guion vs. guion bajo). No se
  verificó cuál es el vigente.

---

## 3. Repositorio de documentación hermano

`/DEV/ThermalPrint.MotorDsl.Core.Documentacion/`

```text
ThermalPrint.MotorDsl.Core.Documentacion/
├── PrintThermal_Motor_Maui-docs/     Documentación derivada, estilo arc42/C4
│   ├── docs-manifest.yaml            Manifiesto máquina-legible: piezas, doc_types, gap
│   ├── GLOSSARY.md                   Vocabulario (pipeline/DSL, renderizado, impresión, build)
│   ├── README.md
│   ├── docs/
│   │   ├── 00-overview/              vision.md, system-map.md
│   │   ├── 01-architecture/          01-context (C4 L1), 02-containers (C4 L2), 04-runtime-views, 06-crosscutting
│   │   ├── 04-decisions/             ADR-0001…0005, README, reporte-derivas.md
│   │   ├── 05-apis/catalog.md
│   │   ├── 08-onboarding/developer-setup.md
│   │   ├── 09-agents/agent-policy.md
│   │   └── gap-documental.md
│   └── pieces/                       Un subdirectorio por paquete (8 + samples): README, api-reference,
│                                     usage-guide, component-catalog, extension-guide, platform-notes
├── Analisis/                         Analisis-UX-UI.md, Plan-Correcciones-UX-Impresion.md,
│                                     03-Analisis-IOs/Nuget-Multiplaforma.md
├── PROMPTs/                          Prompts de trabajo del usuario
├── CHANGELOG.md · README.md
└── ia-db/                            ← esta base de conocimiento
```

`Analisis/03-Analisis-IOs/Nuget-Multiplaforma.md` es la referencia para **soporte iOS y resolución
multiplataforma de los paquetes**: explica cómo NuGet elige `lib/net10.0-android36.0/` o
`lib/net10.0-ios26.0/` según el TFM que se esté compilando (verificado sobre los `.nupkg` de
nuget.org), evalúa 5 alternativas de transporte para iOS y registra los hallazgos de CI/CD que
motivaron el rediseño de `cd-nuget.yml`. Complementa a [08_build-devops](08_build-devops.md) §5 y
a [04_impresion-transports](04_impresion-transports.md) §5-bis.

**Los 5 ADR viven aquí, no en el repositorio de código**: `PrintThermal_Motor_Maui-docs/docs/04-decisions/`.
Sus decisiones están resumidas en [00_MASTER-INDEX](00_MASTER-INDEX.md) §4.

`docs-manifest.yaml` declara el estado de esa documentación como **`draft`** (generada por
pipeline, revisión humana pendiente) e indexada sobre `v1.0.13 @83677eb` — el mismo commit que
esta ia-db.

Además, es la fuente de la que se toman los nombres de los índices de esta base: cada pieza
declara su `ia_db_index` (ver el manifiesto de generación en el [README](../README.md)).

### Gap documental declarado

El manifiesto declara explícitamente lo **no** generado, en vez de omitirlo en silencio:

| Omitido | Razón declarada |
|---|---|
| `02-requirements` | Los requisitos formales no se re-derivaron; existe la doc previa CU-/RN- en `docs/` |
| `03-data` | La solución no tiene base de datos propia: el «modelo» es el AST del DSL |
| `05-deployment` | Son librerías, no hay infraestructura desplegable; el CI/CD está en esta ia-db |
| `06-security-compliance` | Dominio no regulado; sin threat model formal |
| `07-operations` | Librerías, no servicios en ejecución: sin runbooks |
| `changelog-per-piece` | Hay un único `CHANGELOG.md` de solución (solo v1.0.13) |
| `openapi` | No hay API REST en la solución (los samples consumen una externa) |
| `migration-guide` | Sin breaking changes documentados; historia previa a 1.0.13 ausente del CHANGELOG |
| `test-data-matrix` | No solicitado; sin base de datos |

---

## 4. Otra documentación en el repositorio indexado

| Archivo | Contenido |
|---|---|
| `README.md` (raíz) | Quickstart MAUI completo, tabla de paquetes, arquitectura resumida, samples, roadmap |
| `CHANGELOG.md` | Keep a Changelog; entrada vigente 1.0.13 |
| `.github/copilot-instructions.md` | Contexto para Copilot: stack, estructura, modalidades de entrada del motor |
| `samples/Readme.md` | Catálogo de samples y snippets de integración |
| `samples/notas-debug-android.md` | Notas de depuración en Android |
| `scripts/{local,mobile}/Readme.md`, `scripts/nuget/notas.md` | Documentación de los scripts |

---

## 5. Observaciones sobre la documentación

Hechos verificados, sin interpretación añadida:

- **La URL del repositorio no es única**: `origin` apunta a `hdcm-dev/ThermalPrint.MotorDsl.Core`,
  mientras que los `.csproj`, el `README.md` y `docs-manifest.yaml` declaran
  `Aplicada-Streaming/PrintThermal_Motor_Maui`. Los enlaces del README apuntan a esta última.
- **Conteo de tests inconsistente entre fuentes** (ver [07_tests](07_tests.md) §1).
- **`cd-nuget.yml` empaqueta los 8 paquetes** repartidos en dos runners (ver [08_build-devops](08_build-devops.md) §5).
- **`docs/README.md` menciona `scripts/docker`**, que no existe en el árbol; las carpetas reales
  son `local`, `mobile` y `nuget`.
- **`.github/copilot-instructions.md` describe la estructura de forma desactualizada**: menciona
  `PrintThermalDriver.sln` (hoy `.slnx`), `MotorDsl.MultaApp.Nuget` (hoy `MotorDsl.Nuget.MultaApp`)
  y omite `Printing.Abstractions`, `Bluetooth` y `Maui`.
- **`docs/README.md` describe un roadmap por versiones (v1.1…v2.0)** distinto del roadmap por
  features del `README.md` de la raíz. No se verificó cuál está vigente.

---

## 6. Fuentes

| Tema | Archivo |
|---|---|
| Árbol de documentación del proyecto | `docs/` y `docs/README.md` |
| Manifiesto de la documentación derivada | `PrintThermal_Motor_Maui-docs/docs-manifest.yaml` |
| Glosario | `PrintThermal_Motor_Maui-docs/GLOSSARY.md` |
| ADR y derivas | `PrintThermal_Motor_Maui-docs/docs/04-decisions/` |
| Gap documental | `PrintThermal_Motor_Maui-docs/docs/gap-documental.md` |
