# 09 — Documentación existente en el repositorio

> **Propósito**: mapa de las 120+ piezas de documentación funcional y técnica que ya viven en
> `docs/`, para poder ir directo a la fuente sin recorrer el árbol.
> **Fuente primaria**: `docs/` del repositorio indexado (12 carpetas) + `README.md` de cada una.
> Este índice **mapea**; no re-deriva ni resume el contenido de cada documento.

---

## 1. Las doce carpetas

| Carpeta | Contiene | Piezas |
|---|---|---|
| `00_contexto/` | Visión de producto, alcance, compatibilidad de plataformas (v1.0, v1.1, v1.2) | 4 |
| `01_necesidades_negocio/` | Documento marco + 6 necesidades `NB-01..NB-06` | 7 |
| `02_especificacion_funcional/` | 32 casos de uso, modelo conceptual, 6 reglas `RC-`, 4 reglas `RN-`, un proceso | ~46 |
| `03_ux-ui/` | Experiencia de uso, representación ESC/POS, vista previa, wireframes | 4 |
| `04_prompts_ai/` | Prompt de clasificación de documento | 1 |
| `05_arquitectura_tecnica/` | Arquitectura (v1.0/v1.1), contratos, decisiones, extensibilidad (v1.0/v1.1), flujo de ejecución, guía de uso (v1.0/v1.1), modelo lógico | 10 |
| `06_backlog-tecnico/` | Backlog técnico | 1 |
| `07_plan-sprint/` | Planes de iteración sprint 01 a 08 | 8 |
| `08_calidad_y_pruebas/` | Estrategia de calidad y testing, criterios, matriz de cobertura, casos referenciales, guía de extensibilidad | 6 |
| `09_devops/` | Entornos, versionado, publicación NuGet, pipeline CI/CD | 4 |
| `10_developer_guide/` | 7 guías + 5 templates JSON de ejemplo + README | 14 |
| `11_examples/` | 4 recorridos de ejemplo + logos y firmas de prueba | 5 + binarios |

---

## 2. Los 32 casos de uso

`docs/02_especificacion_funcional/casos-de-uso/` — agrupados por etapa del pipeline:

| Rango | Tema | CU |
|---|---|---|
| Interpretación | DSL → AST | CU-01 interpretar plantilla · CU-03 construir modelo interno · CU-13 cargar plantilla · CU-14 validar plantilla |
| Datos | Resolución y validación | CU-02 resolver datos · CU-15 resolver referencias · CU-16 iteraciones · CU-17 condiciones · CU-18 cargar datos · CU-19 validar estructura · CU-20 mapear datos |
| Layout | Adaptación al dispositivo | CU-04 ejecutar motor de layout · CU-05 representación abstracta · CU-12 adaptar al perfil · CU-23 aplicar restricciones del dispositivo |
| Render | Salidas | CU-06 ESC/POS (v1.0 y **v2.0**) · CU-07 texto plano · CU-08 vista previa UI · CU-09 PDF (v1.0 y **v2.0**) |
| Impresión | Canal físico | CU-10 enviar a impresora Bluetooth · CU-11 seleccionar perfil |
| Perfiles | Dispositivo | CU-21 cargar perfil (v1.0 y **v2.0**) · CU-22 validar perfil |
| Provisión | Origen de artefactos | CU-24, CU-25, CU-26 — **cada uno con dos versiones**: v1.0 «descargar de API» y v2.0 «proveer al motor» |
| Integración | Consumo | CU-27 integrar en MAUI · CU-28 configurar el motor · CU-29 extender con renderizadores |
| Errores | Manejo | CU-30 errores de plantilla · CU-31 errores de datos · CU-32 errores de impresión |

**Cuidado con las versiones**: seis CU tienen dos archivos. El cambio de nombre de CU-24/25/26
—de «descargar de API» a «proveer al motor»— refleja una decisión de diseño real: el motor **no**
descarga nada, recibe lo que el consumidor le provee por los contratos `ITemplateProvider`,
`IDataProvider` e `IDeviceProfileProvider`. Al citar, usar la versión más alta.

Lo mismo aplica a `compatibilidad-plataformas` (v1.0, v1.1, **v1.2**), `arquitectura-solucion`
(v1.0, **v1.1**), `extensibilidad-motor` (v1.0, **v1.1**) y `guia-uso-libreria` (v1.0, **v1.1**).

---

## 3. Reglas y necesidades

| Grupo | Archivos |
|---|---|
| `NB-` necesidades de negocio | Desacople · Estandarización · Cambios sin código · Multi-dispositivo · Reducción de costos · Reutilización |
| `RN-` reglas de negocio | Validación de esquema DSL · Tipos de elementos soportados · Estructura jerárquica · Trazabilidad de impresión |
| `RC-` reglas conceptuales de modelo | Datos válidos · Esquema DSL · Estructura jerárquica · Elementos soportados · Independencia del documento abstracto · Perfil dispositivo-salida |

---

## 4. Developer guide — el punto de entrada práctico

`docs/10_developer_guide/README.md` indexa siete documentos. Es la documentación **más cercana al
código actual** y la que conviene leer primero al integrar:

| # | Documento | Cubre |
|---|---|---|
| 1 | `conceptos-fundamentales.md` | Qué es MotorDsl, el pipeline, qué **no** hace |
| 2 | `formato-dsl-templates.md` | Especificación completa del JSON DSL |
| 3 | `formato-perfiles-impresora.md` | `DeviceProfile` vs `PrinterProfile`, anchos por modelo |
| 4 | `guia-integracion-maui.md` | DI, inyección, render, envío, errores |
| 5 | `componentes-ux-maui.md` | API de los controles bindeables |
| 6 | `transports-y-extensibilidad.md` | Escribir un `IThermalPrinterTransport` propio |
| 7 | `render-pixelado-y-pdf.md` | `RasterPreviewRenderer`, `QrCodeRasterizer`, `PdfRenderer` |

Fuera de ese índice pero en la misma carpeta: `diagnostics.md` (patrón de los tres botones),
`integracion-api-rest.md`, `perfiles-impresoras-reales.md` y **dos archivos casi homónimos**,
`soporte-imagenes-termicas.md` y `soporte_imagenes_termicas.md` (guion vs guion bajo) — verificar
cuál está vigente antes de citarlos.

---

## 5. Documentación derivada, en el repo de documentación

Además de `docs/`, existe un cuerpo generado que **no vive en el repositorio indexado** sino en
`/Libs/NugetOrg/PrintThermal_Motor_Maui.Documentacion`:

| Ruta | Contenido |
|---|---|
| `PrintThermal_Motor_Maui-docs/docs-manifest.yaml` | Manifiesto máquina-legible: piezas, `required_docs`, `doc_types` con vigencia, y el `gap` declarado |
| `…/docs/00-overview/` | Visión y mapa del sistema |
| `…/docs/01-architecture/` | C4 contexto y contenedores, vistas de runtime, transversales |
| `…/docs/04-decisions/` | ADR-0001 a ADR-0005 + índice + reporte de derivas |
| `…/docs/05-apis/catalog.md` | Catálogo de API pública |
| `…/docs/08-onboarding/developer-setup.md` | Puesta a punto |
| `…/docs/09-agents/agent-policy.md` | Política para agentes |
| `…/pieces/<paquete>/` | README, api-reference, usage-guide, etc. por paquete |
| `…/GLOSSARY.md` | Vocabulario (incluye «Versión unificada») |
| `Analisis/` | Análisis UX/UI, plan de correcciones de impresión, análisis de multiplataforma iOS |

Todo ese cuerpo está marcado `status: draft` y `source_ref: v1.0.13 @83677eb`: es **anterior** al
commit indexado aquí (`e688f3c`), así que no incorpora `MotorDsl.Network`. Los cuatro primeros ADR
son `origin: reverse-engineered` y esperan validación humana.

---

## 6. Gap documental declarado

De `docs-manifest.yaml` § `gap` — lo que **no** se generó, dicho explícitamente en lugar de omitido:

| Carpeta / artefacto | Motivo declarado |
|---|---|
| `02-requirements` | Los requisitos formales no se re-derivaron; existe la doc previa CU-/RN-/NB- |
| `03-data` | La solución no tiene base de datos: el «modelo» es el AST del DSL |
| `05-deployment` | Son librerías, no hay infraestructura desplegable; el CI/CD está en el índice 08 |
| `06-security-compliance` | Dominio no regulado, sin threat model formal |
| `07-operations` | Sin runbooks: librerías, no servicios en ejecución |
| changelog por paquete | Hay un `CHANGELOG.md` único a nivel solución |
| OpenAPI | No hay REST API en la solución |
| guía de migración | Sin breaking changes documentados |
| matriz de datos de prueba | No solicitada |

---

## 7. Cómo usar esta documentación

1. **Para integrar**: `docs/10_developer_guide/` y los samples (índice 06).
2. **Para entender por qué**: los ADR del repo de documentación (índice 00 §4).
3. **Para entender qué debía hacer**: los CU de `docs/02_especificacion_funcional/`.
4. **Para saber qué hace hoy**: los índices 01 a 05 de esta ia-db, que se generaron leyendo el
   código en `e688f3c`.

Ante discrepancia entre un documento y el código, **manda el código** — buena parte de `docs/` es
anterior a los sprints 07 y 08 y a la incorporación de `MotorDsl.Network`.
