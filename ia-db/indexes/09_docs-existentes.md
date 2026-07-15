# Índice 09 — Mapa de la documentación previa existente (`docs/`)

> **Propósito:** mapa navegable de toda la documentación previa del proyecto MotorDsl bajo
> `docs/` (carpetas `00_contexto` … `11_examples`), con versión y estado declarados en el
> encabezado de cada documento. Es la base de trazabilidad de requisitos (NB / CU / RN / RC).
> **Fuentes primarias:** los propios `.md` de `docs/` (encabezados «Versión / Estado / Fecha»)
> y `docs/README.md`. No se copia contenido, solo se mapea.
> **Referencia de versión:** `v1.0.13 @83677eb`. Rutas relativas a
> `f:\repos\ng-sa\Workspace-GDA\Librerias\PrintThermal_Motor_Maui\`.
> «—» = el documento no declara ese metadato en su encabezado (No verificado).

---

## 0. Resumen por carpeta

| Carpeta | Docs .md | Tema | Otros archivos |
|---|---|---|---|
| `docs/README.md` | 1 | Portada de la documentación: descripción, stack, estructura, flujo de desarrollo, DoD | — |
| `docs/00_contexto/` | 4 | Visión, alcance, compatibilidad de plataformas | — |
| `docs/01_necesidades_negocio/` | 7 | Necesidades de negocio NB-01..06 + consolidado | — |
| `docs/02_especificacion_funcional/` | 51 | Especificación funcional, 32 CU (38 archivos), 4 RN, 6 RC, modelo conceptual, 1 proceso | — |
| `docs/03_ux-ui/` | 4 | Experiencia de uso, representaciones ESC/POS y preview, wireframes | — |
| `docs/04_prompts_ai/` | 1 | Prompt de clasificación de documentos DSL | — |
| `docs/05_arquitectura_tecnica/` | 10 | Arquitectura, contratos, extensibilidad, flujo, modelos, ADR, guía de uso | — |
| `docs/06_backlog-tecnico/` | 1 | Backlog técnico | — |
| `docs/07_plan-sprint/` | 8 | Planes de iteración Sprint 01–08 | — |
| `docs/08_calidad_y_pruebas/` | 6 | Estrategias de calidad/testing, casos de prueba, matriz, criterios | — |
| `docs/09_devops/` | 4 | Pipeline CI/CD, versionado, publicación NuGet, entornos | — |
| `docs/10_developer_guide/` | 13 | Guía para consumidores de la librería | 5 templates `.json` de ejemplo |
| `docs/11_examples/` | 5 | Ejemplos end-to-end sobre los samples | 4 logos `.base64` (excluidos imágenes binarias) |
| **Total** | **115** | | |

---

## 1. `docs/00_contexto/`

| Documento | Tema | Versión | Estado aparente |
|---|---|---|---|
| `00_contexto/vision-producto_v1.0.md` | Visión de producto | v1.0 | Propuesto |
| `00_contexto/alcance-proyecto_v1.0.md` | Alcance del proyecto | v1.0 | Propuesto |
| `00_contexto/compatibilidad-plataformas_v1.0.md` | Compatibilidad de plataformas | v1.0 | Histórico (superado por v1.1) |
| `00_contexto/compatibilidad-plataformas_v1.1.md` | Compatibilidad de plataformas | v1.1 | **Vigente** |

## 2. `docs/01_necesidades_negocio/`

| Documento | Tema | Versión | Estado aparente |
|---|---|---|---|
| `01_necesidades_negocio/necesidades-negocio_v1.0.md` | Consolidado NB-01..06 con matriz NB→capacidad | v1.0 | Propuesto |
| `01_necesidades_negocio/necesidades-de-negocio/NB-01-Desacople.v1.0.md` | NB-01 | v1.0 | Propuesto |
| `.../NB-02 Estandarización.v1.0.md` (nombre con espacio) | NB-02 | v1.0 | Propuesto |
| `.../NB-03-Cambios-sin-codigo.v1.0.md` | NB-03 | v1.0 | Propuesto |
| `.../NB-04-Multi-dispositivo.v1.0.md` | NB-04 | v1.0 | Propuesto |
| `.../NB-05-Reduccion-de-costos.v1.0.md` | NB-05 | v1.0 | Propuesto |
| `.../NB-06-Reutilizacion.v1.0.md` | NB-06 | v1.0 | Propuesto |

### IDs NB (título corto, según `necesidades-negocio_v1.0.md`)

| ID | Título |
|---|---|
| NB-01 | Desacoplar datos, diseño y dispositivo |
| NB-02 | Estandarizar la generación de documentos |
| NB-03 | Permitir cambios de diseño sin modificar código |
| NB-04 | Adaptarse a múltiples dispositivos de salida |
| NB-05 | Reducir costos de mantenimiento y desarrollo |
| NB-06 | Habilitar reutilización entre proyectos |

## 3. `docs/02_especificacion_funcional/`

### 3.1 Documentos generales

| Documento | Tema | Versión | Estado aparente |
|---|---|---|---|
| `02_especificacion_funcional/especificacion-funcional_v1.0.md` | Especificación funcional general | — (archivo `_v1.0`) | Aprobado |
| `02_especificacion_funcional/modelo-datos/modelo-conceptual_v1.0.md` | Modelo de datos conceptual | v1.0 | Aprobado |
| `02_especificacion_funcional/procesos/proceso-gestion-reclamo_v1.0.md` | Proceso de negocio: gestión de reclamo | v1.0 | Aprobado |

### 3.2 Casos de uso (`02_especificacion_funcional/casos-de-uso/`) — 32 CU, 38 archivos

Todos v1.0 = Propuesto (2026-03-28) salvo indicación. Los v2.0 (2026-05-27) son Aprobados.

| ID | Título corto | Archivos / versiones | Estado aparente |
|---|---|---|---|
| CU-01 | Interpretar plantilla DSL | `CU-01-interpretar-plantilla-dsl_v1.0.md` | Propuesto |
| CU-02 | Resolver datos del documento | `CU-02-resolver-datos-documento_v1.0.md` | Propuesto |
| CU-03 | Construir modelo interno | `CU-03-construir-modelo-interno_v1.0.md` | Propuesto |
| CU-04 | Ejecutar motor de layout | `CU-04-Ejecutar-motor-de-layout.md` (archivo sin sufijo `_v1.0`; encabezado interno dice v1.0) | Propuesto |
| CU-05 | Generar representación abstracta | `CU-05-generar-representacion-abstracta_v1.0.md` | Propuesto |
| CU-06 | Renderizar a ESC/POS | `..._v1.0.md` **y** `..._v2.0.md` coexisten | v1.0 Propuesto / **v2.0 Aprobado (vigente)** |
| CU-07 | Renderizar texto plano (debug) | `CU-07-renderizar-texto-plano-debug_v1.0.md` | Propuesto |
| CU-08 | Renderizar vista previa (UI) | `CU-08-renderizar-vista-previa-ui_v1.0.md` | Propuesto |
| CU-09 | Renderizar PDF | `..._v1.0.md` (Futuro) **y** `..._v2.0.md` coexisten | v1.0 Futuro / **v2.0: «FUERA DEL ALCANCE de MotorDsl.Core (provisto por MotorDsl.Maui)»** |
| CU-10 | Enviar a impresora Bluetooth | `CU-10-enviar-impresora-bluetooth_v1.0.md` | Propuesto |
| CU-11 | Seleccionar perfil de impresora | `CU-11-seleccionar-perfil-impresora_v1.0.md` | Propuesto |
| CU-12 | Adaptar documento al perfil | `CU-12-adaptar-documento-perfil_v1.0.md` | Propuesto |
| CU-13 | Cargar plantilla DSL | `CU-13-cargar-plantilla-dsl_v1.0.md` | Propuesto |
| CU-14 | Validar plantilla DSL | `CU-14-validar-plantilla-dsl_v1.0.md` | Propuesto |
| CU-15 | Resolver referencias a datos | `CU-15-resolver-referencias-datos_v1.0.md` | Propuesto |
| CU-16 | Ejecutar iteraciones (listas) | `CU-16-ejecutar-iteraciones-listas_v1.0.md` | Propuesto |
| CU-17 | Evaluar condiciones | `CU-17-evaluar-condiciones_v1.0.md` | Propuesto |
| CU-18 | Cargar datos del documento | `CU-18-cargar-datos-documento_v1.0.md` | Propuesto |
| CU-19 | Validar estructura de datos | `CU-19-validar-estructura-datos_v1.0.md` | Propuesto |
| CU-20 | Mapear datos a plantilla | `CU-20-mapear-datos-plantilla_v1.0.md` | Propuesto |
| CU-21 | Cargar perfil de impresora | `..._v1.0.md` **y** `..._v2.0.md` coexisten | v1.0 Propuesto / **v2.0 Aprobado (vigente; absorbe CU-26)** |
| CU-22 | Validar perfil de dispositivo | `CU-22-validar-perfil-dispositivo_v1.0.md` | Propuesto |
| CU-23 | Aplicar restricciones del dispositivo | `CU-23 Aplicar restricciones del dispositivo.md` (nombre con espacios; encabezado interno: v1.0) | Propuesto |
| CU-24 | v1.0: Descargar plantilla desde API → v2.0: **Proveer plantilla al motor** (renombrado) | `CU-24-descargar-plantilla-api_v1.0.md` **y** `CU-24-proveer-plantilla-motor_v2.0.md` | v1.0 Propuesto / **v2.0 Aprobado (vigente)** |
| CU-25 | v1.0: Descargar datos desde API → v2.0: **Proveer datos al motor** (renombrado) | `CU-25-descargar-datos-api_v1.0.md` **y** `CU-25-proveer-datos-motor_v2.0.md` | v1.0 Propuesto / **v2.0 Aprobado (vigente)** |
| CU-26 | v1.0: Descargar perfil de impresora → v2.0: **FUSIONADO con CU-21 v2.0** | `CU-26-descargar-perfil-impresora_v1.0.md` **y** `CU-26-proveer-perfil-motor_v2.0.md` (aviso de fusión) | v1.0 Propuesto / v2.0 = redirección a CU-21 v2.0 |
| CU-27 | Integrar motor en app .NET MAUI | `CU-27-integrar-motor-maui_v1.0.md` | Propuesto |
| CU-28 | Configurar motor DSL | `CU-28-configurar-motor-dsl_v1.0.md` | Propuesto |
| CU-29 | Extender motor con nuevos renderizadores | `CU-29-extender-motor-renderizadores_v1.0.md` | Propuesto |
| CU-30 | Manejar errores de plantilla inválida | `CU-30-manejar-errores-plantilla_v1.0.md` | Propuesto |
| CU-31 | Manejar errores de datos inconsistentes | `CU-31-manejar-errores-datos_v1.0.md` | Propuesto |
| CU-32 | Manejar errores de impresión | `CU-32-manejar-errores-impresion_v1.0.md` | Propuesto |

### 3.3 Reglas de negocio (`.../reglas-de-negocio/`) — RN-01..04

| ID | Título corto | Documento | Versión / Estado |
|---|---|---|---|
| RN-01 | Validación de esquema de plantilla DSL | `RN-01-validacion-esquema-dsl_v1.0.md` | v1.0 / Aprobada |
| RN-02 | Tipos de elementos soportados en DSL | `RN-02-tipos-elementos-soportados_v1.0.md` | v1.0 / Aprobada |
| RN-03 | Estructura jerárquica del documento DSL | `RN-03-estructura-jerarquica_v1.0.md` | v1.0 / Aprobada |
| RN-04 | Trazabilidad de impresión | `RN-04-trazabilidad-impresion_v1.0.md` | v1.0 / Aprobada |

### 3.4 Reglas conceptuales de modelo (`.../modelo-datos/reglas-conceptuales-de-modelo/`) — RC-01..06

| ID | Título corto | Documento | Versión / Estado |
|---|---|---|---|
| RC-01 | Todo documento debe tener datos válidos | `RC-01-datos-validos_v1.0.md` | v1.0 / Aprobada |
| RC-02 | Cumplimiento del esquema DSL por plantilla | `RC-02-esquema-dsl_v1.0.md` | v1.0 / Aprobada |
| RC-03 | Estructura jerárquica del documento | `RC-03-estructura-jerarquica_v1.0.md` | v1.0 / Aprobada |
| RC-04 | Elementos soportados por el motor | `RC-04-elementos-soportados_v1.0.md` | v1.0 / Aprobada |
| RC-05 | Independencia del documento abstracto respecto del renderizador | `RC-05-independencia-documento-abstracto_v1.0.md` | v1.0 / Aprobada |
| RC-06 | Perfil de dispositivo condiciona la salida final | `RC-06-perfil-dispositivo-salida_v1.0.md` | v1.0 / Aprobada |

## 4. `docs/03_ux-ui/`

| Documento | Tema | Versión | Estado aparente |
|---|---|---|---|
| `03_ux-ui/experiencia-de-uso-del-motor_v1.0.md` | Experiencia de uso del motor | v1.0 | Aprobado |
| `03_ux-ui/representacion-documento-escpos_v1.0.md` | Representación de documento en ESC/POS | v1.0 | Aprobado |
| `03_ux-ui/representacion-vista-previa-ui_v1.0.md` | Representación en vista previa UI | v1.0 | Aprobado |
| `03_ux-ui/wireframes-documentos_v1.0.md` | Wireframes conceptuales de documentos | — (solo nombre de archivo) | — |

## 5. `docs/04_prompts_ai/`

| Documento | Tema | Versión | Estado aparente |
|---|---|---|---|
| `04_prompts_ai/prompt-clasificacion-documento_v1.0.md` | Prompt LLM para clasificar documentos DSL por estrategia de render | v1.0 | Activo |

## 6. `docs/05_arquitectura_tecnica/`

| Documento | Tema | Versión | Estado aparente |
|---|---|---|---|
| `05_arquitectura_tecnica/arquitectura-solucion_v1.0.md` | Arquitectura de la solución | v1.0 | Histórico |
| `05_arquitectura_tecnica/arquitectura-solucion_v1.1.md` | Arquitectura de la solución | v1.1 | **Vigente** |
| `05_arquitectura_tecnica/contratos-del-motor_v1.0.md` | Contratos del motor (interfaces) | v1.0 | Borrador |
| `05_arquitectura_tecnica/decisiones-arquitectura_v1.0.md` | ADR — titulado «Sistema de Gestión de Reclamos» (ver hallazgo D6) | v1.0 | Activo |
| `05_arquitectura_tecnica/extensibilidad-motor_v1.0.md` | Extensibilidad del motor | v1.0 | Histórico |
| `05_arquitectura_tecnica/extensibilidad-motor_v1.1.md` | Extensibilidad del motor | v1.1 | **Vigente** |
| `05_arquitectura_tecnica/flujo-ejecucion-motor_v1.0.md` | Flujo de ejecución del motor | v1.0 | Borrador |
| `05_arquitectura_tecnica/guia-uso-libreria_v1.0.md` | Guía de uso de la librería | v1.0 | Histórico |
| `05_arquitectura_tecnica/guia-uso-libreria_v1.1.md` | Guía de uso de la librería | v1.1 | **Vigente** |
| `05_arquitectura_tecnica/modelo-datos-logico_v1.0.md` | Modelo de datos lógico | v1.0 | Borrador |
| `05_arquitectura_tecnica/modelo-logico-de-ejecucion_v1.0.md` | Modelo lógico de ejecución (empieza con fence ```markdown residual) | — | — |

## 7. `docs/06_backlog-tecnico/` y `docs/07_plan-sprint/`

| Documento | Tema | Versión | Estado aparente |
|---|---|---|---|
| `06_backlog-tecnico/backlog-tecnico_v1.0.md` | Backlog técnico | v1.0 | Activo |
| `07_plan-sprint/plan-iteracion_sprint-01_v1.0.md` … `sprint-03` | Planes de iteración (2026-03-28) | v1.0 | — (sin campo Estado) |
| `07_plan-sprint/plan-iteracion_sprint-04_v1.0.md` | Plan Sprint 04 (2026-05-13) | v1.0 | — |
| `07_plan-sprint/plan-iteracion_sprint-05_v1.0.md` | Plan Sprint 05 (2026-05-27) | v1.0 | — |
| `07_plan-sprint/plan-iteracion_sprint-06_v1.0.md` | Plan Sprint 06 (2026-06-10) | v1.0 | — |
| `07_plan-sprint/plan-iteracion_sprint-07_v1.0.md` | Plan Sprint 07 (2026-06-24) | v1.0 | — |
| `07_plan-sprint/plan-iteracion_sprint-08_v1.0.md` | Plan Sprint 08 (2026-07-08) | v1.0 | — |

## 8. `docs/08_calidad_y_pruebas/`

| Documento | Tema | Versión | Estado aparente |
|---|---|---|---|
| `08_calidad_y_pruebas/estrategia-calidad-motor_v1.0.md` | Estrategia de calidad | v1.0 | Activo |
| `08_calidad_y_pruebas/estrategia-testing-motor_v1.0.md` | Estrategia de testing | v1.0 | Activo |
| `08_calidad_y_pruebas/casos-prueba-referenciales_v1.0.md` | Casos de prueba referenciales | v1.0 | Activo |
| `08_calidad_y_pruebas/matriz-cobertura-pruebas_v1.0.md` | Matriz de cobertura de pruebas | v1.0 | Activo |
| `08_calidad_y_pruebas/criterios-validacion-motor_v1.0.md` | Criterios de validación del motor | — (solo nombre) | — |
| `08_calidad_y_pruebas/guia-testing-extensibilidad_v1.0.md` | Guía de testing de extensibilidad | — (solo nombre) | — |

## 9. `docs/09_devops/`

| Documento | Tema | Versión | Estado aparente |
|---|---|---|---|
| `09_devops/pipeline-ci-cd_v1.0.md` | Pipeline CI/CD (build, tests, pack, publish, APK, iOS) | v1.0 | Aprobado |
| `09_devops/estrategia-versionado_v1.0.md` | Versionado SemVer, inyección de versión, versión unificada | v1.0 | Aprobado |
| `09_devops/guia-publicacion-nuget_v1.0.md` | Publicación y consumo de paquetes NuGet | v1.0 | Aprobado |
| `09_devops/entornos-deploy_v1.0.md` | Entornos DEV→QA→STAGING→PROD | v1.0 | Aprobado |

Detalle operativo de esta carpeta: ver índice `08_build-devops.md` §3–4.

## 10. `docs/10_developer_guide/` (sin metadatos de versión, salvo indicación)

| Documento | Tema |
|---|---|
| `10_developer_guide/README.md` | Índice de la guía (7 documentos numerados + templates de ejemplo); audiencia: consumidores de la librería |
| `10_developer_guide/conceptos-fundamentales.md` | Pipeline de renderizado, conceptos clave, qué NO hace la librería |
| `10_developer_guide/formato-dsl-templates.md` | Especificación del formato JSON DSL (nodos, binding, estilos, validación) |
| `10_developer_guide/formato-perfiles-impresora.md` | `DeviceProfile` y `PrinterProfile`, perfiles predefinidos, anchos |
| `10_developer_guide/guia-integracion-maui.md` | Integración en app MAUI: DI, render, Bluetooth, errores |
| `10_developer_guide/componentes-ux-maui.md` | Controles MAUI bindeables (API, BindableProperties, XAML) |
| `10_developer_guide/transports-y-extensibilidad.md` | Cómo escribir un `IThermalPrinterTransport` propio |
| `10_developer_guide/render-pixelado-y-pdf.md` | `RasterPreviewRenderer`, `QrCodeRasterizer`, `PdfRenderer` |
| `10_developer_guide/diagnostics.md` | Diagnóstico y reporte de fallos (patrón de 3 botones; referenciado desde `README.md` raíz) |
| `10_developer_guide/integracion-api-rest.md` | Integración con API REST (no listado en el README de la guía) |
| `10_developer_guide/perfiles-impresoras-reales.md` | Perfiles de impresoras reales (no listado en el README de la guía) |
| `10_developer_guide/soporte-imagenes-termicas.md` | Soporte de imágenes bitmap ESC/POS — restricciones 58HB6 (sin metadatos) |
| `10_developer_guide/soporte_imagenes_termicas.md` | Soporte de imágenes bitmap ESC/POS — v1.0, «Sprint 08 (extensión)». **Duplicado temático del anterior** (ver D5) |
| `10_developer_guide/ejemplos-templates/*.json` (5) | Templates de ejemplo: ticket-simple, ticket-con-qr, ticket-con-barcode, acta-infraccion, factura-simplificada |

## 11. `docs/11_examples/`

| Documento | Tema | Estado aparente |
|---|---|---|
| `11_examples/README.md` | Índice de 5 ejemplos sobre los samples y los 7 paquetes | — |
| `11_examples/ejemplo-01-simple.md` | Ejemplo 01 — MotorDsl.SampleApp (ticket simple) | — |
| `11_examples/ejemplo-02-multa.md` | Ejemplo 02 — MotorDsl.MultaApp (template + datos) | Implementado |
| `11_examples/ejemplo-03-multa-integrada.md` | Ejemplo 03 — MotorDsl.Integrated.MultaApp (formato integrado) | — |
| `11_examples/ejemplo-03-multaapp-nuget.md` | «Ejemplo 03» — MotorDsl.Nuget.MultaApp vía `<PackageReference Version="1.0.*">` (numeración duplicada con el anterior, ver D4) | Implementado |
| `11_examples/imagenes_logos/*.base64` (4) | Logos/firma en base64 para los ejemplos (excluidos del indexado de contenido) | — |

---

## 12. Documentos con múltiples versiones coexistiendo (cuál parece vigente)

| Documento | Versiones | Vigente aparente | Evidencia |
|---|---|---|---|
| `00_contexto/compatibilidad-plataformas` | v1.0 + v1.1 | v1.1 | v1.0 declara «Histórico», v1.1 «Vigente» |
| `05_arquitectura_tecnica/arquitectura-solucion` | v1.0 + v1.1 | v1.1 | Ídem; `README.md` raíz y `docs/README.md` enlazan a v1.1 |
| `05_arquitectura_tecnica/extensibilidad-motor` | v1.0 + v1.1 | v1.1 | Ídem; `docs/README.md` marca explícitamente «(histórico)» / «(vigente)» |
| `05_arquitectura_tecnica/guia-uso-libreria` | v1.0 + v1.1 | v1.1 | v1.0 «Histórico», v1.1 «Vigente» |
| `casos-de-uso/CU-06-renderizar-escpos` | v1.0 + v2.0 | v2.0 | v1.0 «Propuesto», v2.0 «Aprobado» (2026-05-27) |
| `casos-de-uso/CU-09-renderizar-pdf` | v1.0 + v2.0 | v2.0 | v1.0 «Futuro»; v2.0 reubica el alcance en `MotorDsl.Maui` |
| `casos-de-uso/CU-21-cargar-perfil-impresora` | v1.0 + v2.0 | v2.0 | v2.0 «Aprobado»; además absorbe CU-26 |
| `casos-de-uso/CU-24` | v1.0 (descargar-plantilla-api) + v2.0 (proveer-plantilla-motor) | v2.0 | Renombrado conceptual API→motor; v2.0 «Aprobado» |
| `casos-de-uso/CU-25` | v1.0 (descargar-datos-api) + v2.0 (proveer-datos-motor) | v2.0 | Ídem |
| `casos-de-uso/CU-26` | v1.0 + v2.0 (aviso) | CU-21 v2.0 | v2.0 declara «⚠️ FUSIONADO con CU-21 v2.0» |
| `10_developer_guide/soporte[-_]imagenes[-_]termicas` | 2 archivos sin relación declarada | No verificado | Ver D5 |

Patrón general: los v2.0 de CU datan de 2026-05-27 y los v1.1 de arquitectura/contexto de
2026-05-06; el resto del corpus quedó en v1.0 (mayormente «Propuesto» del 2026-03-28 para CU
y «Aprobado/Activo» para el resto).

## 13. Hallazgos del mapeo (con fuente)

| # | Observación | Fuente |
|---|---|---|
| D1 | Nombres de archivo inconsistentes en CU: `CU-04-Ejecutar-motor-de-layout.md` (sin `_v1.0`) y `CU-23 Aplicar restricciones del dispositivo.md` (espacios, sin sufijo); ambos declaran v1.0 en el encabezado interno con otro nombre de archivo (`CU-04-ejecutar-motor-layout_v1.0.md`, `CU-23-aplicar-restricciones-dispositivo_v1.0.md`) | Los 2 archivos en `02_especificacion_funcional/casos-de-uso/` |
| D2 | `NB-02 Estandarización.v1.0.md` usa espacio y acento en el nombre (los otros NB usan guiones) | `01_necesidades_negocio/necesidades-de-negocio/` |
| D3 | RN declaradas: solo RN-01..RN-04 (no hay RN-05+); RC: RC-01..RC-06 completas | Listado de `reglas-de-negocio/` y `reglas-conceptuales-de-modelo/` |
| D4 | Numeración duplicada en ejemplos: `ejemplo-03-multa-integrada.md` y `ejemplo-03-multaapp-nuget.md` son ambos «Ejemplo 03» pero el índice de `11_examples/README.md` los lista como 03 y 04/05 | `11_examples/` |
| D5 | Dos documentos casi homónimos sobre imágenes térmicas: `soporte-imagenes-termicas.md` (restricciones 58HB6, sin metadatos) y `soporte_imagenes_termicas.md` (v1.0, Sprint 08); ninguno referencia al otro y el `10_developer_guide/README.md` no lista a ninguno de los dos | `10_developer_guide/` |
| D6 | `decisiones-arquitectura_v1.0.md` se titula «ADR — Sistema de Gestión de Reclamos» (fecha 2026-03-02, igual que `proceso-gestion-reclamo_v1.0.md`): parece heredado del proyecto consumidor de reclamos/multas más que del motor | `05_arquitectura_tecnica/decisiones-arquitectura_v1.0.md` |
| D7 | 4 documentos sin encabezado de metadatos (título = nombre de archivo): `wireframes-documentos_v1.0.md`, `modelo-logico-de-ejecucion_v1.0.md` (además arranca con un fence ```markdown residual y el título interno invierte el nombre: `modelo-ejecucion-logico`), `criterios-validacion-motor_v1.0.md`, `guia-testing-extensibilidad_v1.0.md` | Cada archivo citado |
| D8 | `docs/README.md` referencia `/scripts (local | mobile | nuget | docker)` pero `scripts/docker/` no existe; también fija «cobertura mínima 70%» como criterio de calidad | `docs/README.md` §Estructura y §Pruebas; `ls scripts/` |
| D9 | `10_developer_guide/README.md` indexa 7 documentos, pero la carpeta contiene 12 (quedan fuera: `diagnostics.md`, `integracion-api-rest.md`, `perfiles-impresoras-reales.md` y los 2 de imágenes térmicas) | `10_developer_guide/README.md` vs listado de la carpeta |
| D10 | El README raíz enlaza docs por URL absoluta de GitHub (`github.com/Aplicada-Streaming/PrintThermal_Motor_Maui/...`), lo que ancla la documentación al remoto | `README.md` raíz §Arquitectura y §Samples |

## 14. Conteo de IDs para trazabilidad

| Familia | IDs | Cantidad |
|---|---|---|
| NB | NB-01 … NB-06 | 6 |
| CU | CU-01 … CU-32 (38 archivos; 6 CU con doble versión) | 32 |
| RN | RN-01 … RN-04 | 4 |
| RC | RC-01 … RC-06 | 6 |
