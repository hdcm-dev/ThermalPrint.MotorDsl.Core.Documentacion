# 09 — Documentación existente en el repositorio

> **Propósito**: mapa de la documentación commiteada en el repo de código (`docs/`, `README.md`,
> `CHANGELOG.md` y los `Readme` sueltos) y de sus divergencias con el código actual.
> **Fuente primaria**: `git ls-files` del repo indexado en `0f8413d` (main, 2026-09-24).
> Este índice **mapea**; no resume cada documento ni re-deriva lo que cubren los índices 01–08.
> Conteos: estáticos, por `git ls-files` (no hay SDK .NET en el host; nada se compiló).

---

## 1. `docs/` — 130 archivos commiteados en 12 carpetas + `docs/README.md`

| Carpeta | Contiene | Archivos |
|---|---|---|
| `docs/00_contexto/` | Visión de producto, alcance, compatibilidad de plataformas (v1.0, v1.1, **v1.2**) | 5 |
| `docs/01_necesidades_negocio/` | Documento marco `necesidades-negocio_v1.0.md` + `NB-01`..`NB-06` | 7 |
| `docs/02_especificacion_funcional/` | 38 archivos de CU (32 CU, 6 con v2.0: CU-06/09/21/24/25/26), especificación funcional, modelo conceptual, 6 `RC-`, 4 `RN-`, un proceso | 51 |
| `docs/03_ux-ui/` | Experiencia de uso, representación ESC/POS, vista previa, wireframes | 4 |
| `docs/04_prompts_ai/` | Prompt de clasificación de documento | 1 |
| `docs/05_arquitectura_tecnica/` | Arquitectura (v1.0/**v1.1**), contratos, decisiones, extensibilidad (v1.0/**v1.1**), flujo de ejecución, guía de uso (v1.0/**v1.1**), modelo de datos lógico, modelo lógico de ejecución | 11 |
| `docs/06_backlog-tecnico/` | Backlog técnico | 1 |
| `docs/07_plan-sprint/` | Planes de iteración sprint 01 a 08 | 8 |
| `docs/08_calidad_y_pruebas/` | Estrategia de calidad y de testing, criterios, matriz de cobertura, casos referenciales, guía de extensibilidad | 6 |
| `docs/09_devops/` | Entornos, versionado, publicación NuGet, pipeline CI/CD (detalle técnico en `08_build-devops.md`) | 4 |
| `docs/10_developer_guide/` | README + 12 guías `.md` + 5 templates JSON en `ejemplos-templates/` | 18 |
| `docs/11_examples/` | README + 4 recorridos + 8 binarios/base64 en `imagenes_logos/` (no indexados) | 13 |

Fuente: `git ls-files docs`. `docs/README.md` (234 líneas no vacías) es el índice humano de la carpeta.

---

## 2. Casos de uso — `docs/02_especificacion_funcional/casos-de-uso/`

| Etapa | CU |
|---|---|
| Interpretación | CU-01 interpretar plantilla · CU-03 construir modelo interno · CU-13 cargar plantilla · CU-14 validar plantilla |
| Datos | CU-02 resolver datos · CU-15 referencias · CU-16 iteraciones · CU-17 condiciones · CU-18 cargar datos · CU-19 validar estructura · CU-20 mapear datos |
| Layout | CU-04 ejecutar motor de layout · CU-05 representación abstracta · CU-12 adaptar al perfil · CU-23 restricciones del dispositivo |
| Render | CU-06 ESC/POS (v1.0, **v2.0**) · CU-07 texto plano · CU-08 vista previa UI · CU-09 PDF (v1.0, **v2.0**) |
| Impresión | CU-10 enviar a Bluetooth · CU-11 seleccionar perfil |
| Perfiles | CU-21 cargar perfil (v1.0, **v2.0**) · CU-22 validar perfil |
| Provisión | CU-24/25/26: v1.0 «descargar de API» y v2.0 «proveer al motor» |
| Integración | CU-27 integrar en MAUI · CU-28 configurar · CU-29 extender renderizadores |
| Errores | CU-30 plantilla · CU-31 datos · CU-32 impresión |

Al citar, usar la versión más alta. El renombre de CU-24/25/26 refleja que el motor no descarga:
recibe por los contratos de proveedor (ver `01_nucleo-pipeline.md`).

**Nombres irregulares** (sin sufijo `_vX.Y` o con espacios): `CU-04-Ejecutar-motor-de-layout.md` y
`CU-23 Aplicar restricciones del dispositivo.md`.

---

## 3. Reglas y necesidades

| Grupo | Archivos |
|---|---|
| `NB-` (`docs/01_necesidades_negocio/necesidades-de-negocio/`) | NB-01 Desacople · NB-02 Estandarización · NB-03 Cambios sin código · NB-04 Multi-dispositivo · NB-05 Reducción de costos · NB-06 Reutilización |
| `RN-` (`…/reglas-de-negocio/`) | Validación de esquema DSL · Tipos de elementos · Estructura jerárquica · Trazabilidad de impresión |
| `RC-` (`…/modelo-datos/reglas-conceptuales-de-modelo/`) | Datos válidos · Esquema DSL · Estructura jerárquica · Elementos soportados · Independencia del documento abstracto · Perfil dispositivo-salida |

`NB-02 Estandarización.v1.0.md` existe pero con espacio y acento en el nombre (a diferencia de los demás, con guiones); `git ls-files` lo muestra entrecomillado salvo con `core.quotepath=off`.

---

## 4. Developer guide — `docs/10_developer_guide/`

`docs/10_developer_guide/README.md` indexa siete documentos; es la doc más cercana al código:

| # | Documento | Cubre |
|---|---|---|
| 1 | `conceptos-fundamentales.md` | Qué es MotorDsl, pipeline, qué **no** hace |
| 2 | `formato-dsl-templates.md` | Formato JSON DSL (código en `02_dsl-y-modelos.md`) |
| 3 | `formato-perfiles-impresora.md` | `DeviceProfile` vs `PrinterProfile`, anchos |
| 4 | `guia-integracion-maui.md` | DI, render, envío, errores |
| 5 | `componentes-ux-maui.md` | Controles bindeables (código en `05_maui-ui-renderers.md`) |
| 6 | `transports-y-extensibilidad.md` | `IThermalPrinterTransport` propio (código en `04_impresion-transports.md`) |
| 7 | `render-pixelado-y-pdf.md` | `RasterPreviewRenderer`, `QrCodeRasterizer`, `PdfRenderer` |

Fuera del índice del README pero en la carpeta: `diagnostics.md`, `integracion-api-rest.md`,
`perfiles-impresoras-reales.md` y dos casi homónimos **con contenido distinto**:
`soporte-imagenes-termicas.md` (96 líneas) y `soporte_imagenes_termicas.md` (324 líneas).

`docs/11_examples/`: `ejemplo-01-simple.md`, `ejemplo-02-multa.md`, y **dos** `ejemplo-03-*`
(`multa-integrada` y `multaapp-nuget`) que comparten número. Samples reales: `06_samples.md`.

---

## 5. Documentos fuera de `docs/`

| Archivo | Contenido |
|---|---|
| `README.md` | Presentación, estructura del repo, build local. Desde `347ebfb` menciona `scripts/local-devcontainer/` |
| `CHANGELOG.md` | Keep a Changelog, único a nivel solución (§6) |
| `.github/copilot-instructions.md` | Instrucciones para asistentes |
| `samples/Readme.md`, `samples/notas-debug-android.md` | Guía de samples y notas de depuración (ver `06_samples.md`) |
| `scripts/local/Readme.md`, `scripts/mobile/Readme.md`, `scripts/nuget/notas.md`, `nupkg/Readme.md` | Build/publicación (ver `08_build-devops.md`) |
| `scripts/local-devcontainer/Readme.md` | **Nuevo** (`347ebfb`): build de los cinco samples a APK en contenedor Docker efímero; catálogo de `run-*.sh`, `limpiar.sh`, `update-packages.sh` (detalle en `08_build-devops.md`) |

---

## 6. `CHANGELOG.md` en `0f8413d`

| Sección | Línea | Tema principal |
|---|---|---|
| `[Unreleased]` | 11 | Añadido `scripts/local-devcontainer/` |
| `[1.0.17] - 2026-08-27` | 31 | **Cambio de comportamiento**: cola del ticket pasa de `GS V 0` a `GS V 1`; capability `end_of_ticket` (`cut_partial`/`cut_full`/`feed`/`none`) + `end_feed_lines`; barrera de confirmación `GS I 67`; `PrintNotConfirmedException` (`PrintErrorType.Protocol`) |
| `[1.0.16] - 2026-08-26` | 92 | Bluetooth: no intercalar sondeos `DLE EOT` en la carga útil |
| `[1.0.15] - 2026-08-26` | 156 | Bluetooth: espera de teardown del enlace antes de reconectar (`LINK_TEARDOWN_SETTLE_MS`) |
| `[1.0.13] - 2026-07-13` | 240 | Versión previa |

Entre e688f3c y 0f8413d: el CHANGELOG creció ~194 líneas; `558e0c1` reparó la sección 1.0.15 rota
por un merge y reapuntó los links. El código de estos cambios se describe en `03_renderizado-base.md`
y `04_impresion-transports.md`; los tests en `07_tests.md`.

---

## 7. Divergencias doc ↔ código detectadas

| # | Divergencia | Evidencia |
|---|---|---|
| D1 | La doc de perfiles no menciona `end_of_ticket` / `end_feed_lines` ni el nuevo default `GS V 1` | `grep` sin resultados en `docs/`; definido en `CHANGELOG.md` §1.0.17 y `src/MotorDsl.Rendering/EscPosCommands.cs` |
| D2 | `CU-06-renderizar-escpos_v2.0.md` habla de «corte de papel (`GS V`)» sin el modo configurable | `docs/02_especificacion_funcional/casos-de-uso/CU-06-renderizar-escpos_v2.0.md:89` |
| D3 | Ningún doc de `docs/` cita `PrintNotConfirmedException`, `ConfirmPrintTimeoutMs`/`WriteTimeoutMs` ni la barrera `GS I 67`; `CU-32` no la contempla | `src/MotorDsl.Core/Models/PrintNotConfirmedException.cs`; `grep` vacío en `docs/` |
| D4 | Links de repo inconsistentes: `README.md` apunta a `github.com/Aplicada-Streaming/PrintThermal_Motor_Maui`; `CHANGELOG.md` (líneas 276-279) y `origin` a `hdcm-dev/ThermalPrint.MotorDsl.Core` | `README.md`, `CHANGELOG.md`, `git remote -v` |
| D5 | El CHANGELOG salta de 1.0.13 a 1.0.15: no hay entrada 1.0.14 | `grep '^## \[' CHANGELOG.md` |
| D6 | Duplicados de nombre: `soporte-imagenes-termicas.md` vs `soporte_imagenes_termicas.md`; dos `ejemplo-03-*`. Nombres irregulares con espacios: `CU-23 …`, `NB-02 Estandarización…`; `CU-04` sin `_vX.Y` | §2, §3, §4 |
| D7 | Buena parte de `docs/` (00–08) es anterior a los sprints 07–08 y a `MotorDsl.Network`; sólo `00_contexto/compatibilidad-plataformas_v1.1/v1.2`, `docs/09_devops/`, `docs/README.md` y `transports-y-extensibilidad.md` mencionan `Network` | `grep -l Network docs -r` |

Ante discrepancia, **manda el código** (índices 01–05).

---

## 8. Documentación derivada (repo de documentación)

El cuerpo generado (`docs-manifest.yaml`, C4, ADR, `pieces/`, `GLOSSARY.md`, `Analisis/`) vive en el
repo de documentación, no en el indexado; su mapa y vigencia están en `00_MASTER-INDEX.md`. La
versión previa de este índice lo registraba con `source_ref: v1.0.13 @83677eb`, anterior a
`e688f3c` y a `0f8413d`: no incorpora los cambios de 1.0.15–1.0.17 (no re-verificado aquí).

---

## 9. Cómo usar esta documentación

1. **Integrar**: `docs/10_developer_guide/` + `06_samples.md`, y **leer `CHANGELOG.md` §1.0.17** (cambio de corte).
2. **Qué debía hacer**: CU de `docs/02_especificacion_funcional/`.
3. **Qué hace hoy**: índices 01–05 de esta ia-db, generados sobre `0f8413d`.
