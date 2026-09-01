# 09 — Mapa de la documentación existente

> **Propósito**: mapear las doce carpetas de `docs/` para poder ir directo al documento que
> corresponde, sin recorrerlas. **Este índice no resume el contenido**: dice qué hay y dónde.
> **Fuentes primarias**: `docs/` (130 archivos), `docs/README.md`, `samples/Readme.md`,
> `scripts/*/Readme.md`, `README.md` y `CHANGELOG.md` de la raíz.

---

## 1. Las doce carpetas

| Carpeta | Archivos | Qué contiene |
|---|---|---|
| `00_contexto/` | 5 | Alcance, visión de producto y compatibilidad de plataformas (v1.0, v1.1, **v1.2 vigente**) |
| `01_necesidades_negocio/` | 7 | Seis necesidades de negocio `NB-01`…`NB-06` más el documento paraguas |
| `02_especificacion_funcional/` | 51 | **32 casos de uso** `CU-01`…`CU-32`, 4 reglas de negocio `RN-`, 6 reglas conceptuales `RC-`, modelo conceptual y un proceso |
| `03_ux-ui/` | 4 | Experiencia de uso del motor, representación del documento en ESC/POS y en vista previa, wireframes |
| `04_prompts_ai/` | 1 | Prompt de clasificación de documento |
| `05_arquitectura_tecnica/` | 11 | Arquitectura de la solución (v1.0, **v1.1**), contratos, decisiones, extensibilidad (v1.0, **v1.1**), flujo de ejecución, guía de uso (v1.0, **v1.1**), modelo de datos lógico y modelo lógico de ejecución |
| `06_backlog-tecnico/` | 1 | Backlog técnico |
| `07_plan-sprint/` | 8 | Planes de iteración, **sprints 01 a 08** |
| `08_calidad_y_pruebas/` | 6 | Estrategias de calidad y testing, criterios de validación, casos de prueba referenciales, matriz de cobertura, guía de testing de extensibilidad |
| `09_devops/` | 4 | Versionado, publicación NuGet, pipeline CI/CD, entornos de deploy |
| `10_developer_guide/` | 18 | La guía práctica para quien integra la librería. Ver §3 |
| `11_examples/` | 13 | Cuatro ejemplos narrados más los logotipos en `.bmp` y `.base64` |

---

## 2. Cómo leer los sufijos de versión

Los documentos usan el patrón `<nombre>_v<N.N>.md` y **conviven las versiones**: la anterior no
se borra al publicar la nueva. Al buscar información, **tomar siempre la de mayor número**.

| Documento | Versiones presentes | Vigente |
|---|---|---|
| `00_contexto/compatibilidad-plataformas` | v1.0, v1.1, v1.2 | **v1.2** (2026-08-08, incorpora la impresión en iOS por red) |
| `05_arquitectura_tecnica/arquitectura-solucion` | v1.0, v1.1 | **v1.1** |
| `05_arquitectura_tecnica/extensibilidad-motor` | v1.0, v1.1 | **v1.1** |
| `05_arquitectura_tecnica/guia-uso-libreria` | v1.0, v1.1 | **v1.1** |
| `casos-de-uso/CU-06-renderizar-escpos` | v1.0, v2.0 | **v2.0** |
| `casos-de-uso/CU-09-renderizar-pdf` | v1.0, v2.0 | **v2.0** |
| `casos-de-uso/CU-21-cargar-perfil-impresora` | v1.0, v2.0 | **v2.0** |
| `casos-de-uso/CU-24/25/26` | `descargar-*_v1.0` → `proveer-*_v2.0` | las **v2.0**, que además cambiaron de nombre |

El renombre de `CU-24/25/26` de «descargar … api» a «proveer … motor» refleja un cambio de
enfoque: el motor **recibe** plantilla, datos y perfil, en lugar de ir a buscarlos.

---

## 3. `10_developer_guide/` — la guía práctica

Es la carpeta más útil para integrar la librería.

| Documento | Tema | Índice de esta base que lo cubre |
|---|---|---|
| `README.md` | Entrada de la guía | — |
| `conceptos-fundamentales.md` | Vocabulario y modelo mental | [00](00_MASTER-INDEX.md) |
| `formato-dsl-templates.md` | **Especificación del DSL** | [02](02_dsl-y-modelos.md) |
| `ejemplos-templates/*.json` | 5 plantillas completas | [02 §9](02_dsl-y-modelos.md) |
| `formato-perfiles-impresora.md` | Estructura del `DeviceProfile` | [01 §4](01_nucleo-pipeline.md) |
| `perfiles-impresoras-reales.md` | Perfiles calibrados con hardware real | [04 §4](04_impresion-transports.md) |
| `guia-integracion-maui.md` | Integrar en una app MAUI | [05](05_maui-ui-renderers.md) |
| `componentes-ux-maui.md` | Los controles | [05 §2](05_maui-ui-renderers.md) |
| `render-pixelado-y-pdf.md` | Renderers gráficos | [05](05_maui-ui-renderers.md) |
| `soporte-imagenes-termicas.md` | Imágenes en impresión térmica | [03](03_renderizado-base.md), [05 §3](05_maui-ui-renderers.md) |
| `transports-y-extensibilidad.md` | Escribir un transport | [04 §9](04_impresion-transports.md) |
| `diagnostics.md` | Reporte de diagnóstico y el patrón de 3 botones | [05 §8](05_maui-ui-renderers.md) |
| `integracion-api-rest.md` | Traer plantillas y datos de una API | — |

> **Duplicado detectado**: existen `soporte-imagenes-termicas.md` y
> `soporte_imagenes_termicas.md` —guion medio y guion bajo—. Verificado con `diff`: **son dos
> archivos con contenido distinto**, no una copia. Cuál es el vigente no está declarado en
> ninguna parte, así que al citar el tema conviene abrir los dos.

---

## 4. Documentación fuera de `docs/`

| Archivo | Contenido |
|---|---|
| `README.md` (raíz) | TL;DR de instalación, tabla de los 8 paquetes, quickstart MAUI completo con permisos de Android e iOS, arquitectura resumida, estructura, catálogo de samples, build, publicación y **roadmap** |
| `CHANGELOG.md` | Keep a Changelog en español. `[Unreleased]` + `[1.0.13]`. **La historia previa a 1.0.13 no está** |
| `docs/README.md` | Entrada de la documentación: descripción, objetivos, stack y arquitectura |
| `samples/Readme.md` | Catálogo de los cinco samples con el código relevante de cada uno. Ver la divergencia señalada en [06 §4](06_samples.md) |
| `samples/notas-debug-android.md` | Troubleshooting de Android: `adb`, Skia, `libstdc++`, páginas de 16 KB |
| `scripts/local/Readme.md`, `scripts/mobile/Readme.md`, `scripts/nuget/notas.md` | Uso de cada familia de scripts |
| `.github/copilot-instructions.md` | Instrucciones para el asistente de código del repositorio |

---

## 5. Relación entre la documentación previa y esta base

La documentación de `docs/` es **anterior y más amplia en lo funcional**: 32 casos de uso,
reglas de negocio, planes de sprint y modelo conceptual que esta ia-db **no re-deriva**.

Esta base indexa el **código tal como está** en el commit `e688f3c` y usa la documentación como
fuente secundaria. Donde ambas difieren, prevalece el código: los casos detectados quedaron
anotados como observaciones en [06 §4](06_samples.md) y en la §3 de este índice.

El `docs-manifest.yaml` del repositorio de documentación
(`PrintThermal_Motor_Maui-docs/docs-manifest.yaml`) declara qué piezas de la solución mapean a
qué índice de esta base —campo `ia_db_index`— y registra también lo **deliberadamente no
documentado**: no hay requisitos formales `RF-`/`RNF-` porque existe la documentación previa
`CU-`/`RN-`; no hay modelo de datos porque la solución no tiene base de datos —el «modelo» es
el AST del DSL—; no hay deployment ni runbooks operativos porque son librerías, no servicios;
no hay OpenAPI porque no hay API REST; y no hay changelog por paquete porque el `CHANGELOG.md`
es único a nivel solución.
