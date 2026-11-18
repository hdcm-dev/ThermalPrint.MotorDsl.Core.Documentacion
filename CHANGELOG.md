# Changelog

Todos los cambios notables de la **documentación de MotorDsl** se registran en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/). Este repositorio
contiene el conjunto documental (`PrintThermal_Motor_Maui-docs`) y la base de conocimiento
(`ia-db`) del repositorio de código [`PrintThermal_Motor_Maui`](https://github.com/Aplicada-Streaming/PrintThermal_Motor_Maui),
generados conforme al Marco de Documentación de Software.

## [Unreleased]

### Cambiado

- **`ia-db/` regenerada desde cero (versión 3.0)** sobre `PrintThermal_Motor_Maui` @`0f8413d`
  (rama `main`, 2026-09-24), reemplazando la 2.0 sobre `@e688f3c`. Incorpora los 12 commits
  intermedios: `PrintNotConfirmedException` y la barrera de confirmación de impresión (`GS I 67`),
  la cola del ticket (`EndOfTicket`) y sus tests, Bluetooth sin sondeos DLE EOT dentro de la carga
  útil, `scripts/local-devcontainer/`, `cd-ios-multaapp.nuget.yml`, el acta de 200 infracciones de
  MultaApp y la versión publicada `1.0.17`. Se conserva la numeración `00`…`09` del
  `docs-manifest.yaml`.

  Observaciones sobre el repositorio de código, registradas sin corregirse —indexar no lo
  modifica—: `samples/MotorDsl.Integrated.MultaApp/MotorDsl.Integrated.MultaApp.csproj` queda con un
  `<ItemGroup>` sin cerrar desde `4b18745` (no se pudo comprobar sin SDK si MSBuild lo rechaza), y
  `samples/Readme.md` sigue desactualizado respecto de las referencias de los samples.

  Verificación: 11 archivos (2267 líneas; ninguno supera el techo de 500 del perfil), 0 enlaces
  internos rotos, 119/119 rutas de código citadas existen en `git ls-files` de `0f8413d`; cada
  índice pasó una verificación adversarial contra el código. Conteo de tests **estático**
  (315 casos: 281 `[Fact]` y 34 `InlineData`); no se corrió `dotnet test`.

- **`ia-db/` regenerada desde cero** sobre `PrintThermal_Motor_Maui` @`e688f3c` (rama `main`),
  reemplazando la base del 2026-08-07, que reflejaba `@83677eb` (v1.0.13). Se regeneró en lugar de
  actualizarse de forma incremental por decisión del PO. Incorpora lo que el commit indexado agrega
  sobre el anterior: el octavo paquete `MotorDsl.Network` (transport TCP 9100, que habilita la
  impresión en iOS), el helper público `TransportChunking`, el devcontainer para los TFM `net10.0`,
  el reparto del `pack` entre dos runners en `cd-nuget.yml` y cuatro suites de tests nuevas.
  También corrige el manifiesto, que aún declaraba las rutas previas
  `/DEV/ThermalPrint.MotorDsl.Core[.Documentacion]`.

  Se conserva la numeración `01_nucleo-pipeline` … `09_docs-existentes`, tomada del campo
  `ia_db_index` de `PrintThermal_Motor_Maui-docs/docs-manifest.yaml`, para mantener la trazabilidad
  manifiesto ↔ ia-db.

  Dos divergencias entre la documentación del repositorio de código y su código quedan registradas
  como observaciones, sin corregirse —indexar no modifica el proyecto indexado—: `samples/Readme.md`
  afirma que los dos samples `Nuget.*` consumen la librería solo por `PackageReference`, pero
  `MotorDsl.Nuget.Integrated.MultaApp` usa siete `ProjectReference` desde `@ebe03ef`; y coexisten
  `soporte-imagenes-termicas.md` y `soporte_imagenes_termicas.md`, con contenido distinto y sin que
  ninguna fuente declare cuál rige.

  Verificación: 11 archivos (README + 10 índices), 0 enlaces internos rotos, todos los índices dentro
  del presupuesto de 300–500 líneas del perfil de indexado. El conteo de tests ejecutados quedó
  **sin verificar** (285 métodos `[Fact]`/`[Theory]`, pero cada `[Theory]` aporta varios casos; no se
  corrió `dotnet test`).

- **`PROMPTs/` reorganizada por tema**: `01-Crear-Indexado/` → `Indexado/`,
  `02-Crear-Analisis-IOs/` → `Analisis/02-Crear-Analisis-IOs/` y `03-Extender-A-IOs/` →
  `Features/03-Extender-A-IOs/`. Solo movimientos: el contenido de los cuatro prompts no cambia.

### Añadido

- **`ENTREGA.md`**: delegación del merge al agente asentada (regla del PO del 2026-10-25), con
  techo, intervalo y guardas G1–G4.
- **CI `Verificar`** (`.github/workflows/verificar.yml` + `scripts/verificar_ia_db.py`): enlaces
  internos de la ia-db y tabla de delegación, en cada PR (control G3).

- **Análisis UX/UI del flujo de impresión** (`Analisis/Analisis-UX-UI.md`): relevamiento de los flujos
  de usuario de los PoC `Ejemplo_Maui_Hibrida` y `Ejemplo_MotorDSL_Dialog`, con 7 hallazgos
  verificados contra el código fuente (`Ejemplos_Maui_Devices @fd6a1ed`, `PrintThermal_Motor_Maui`
  v1.0.13 `@83677eb`) y propuestas de mejora sobre el patrón de diálogos overlay.
- **Plan de correcciones UX de impresión** (`Analisis/Plan-Correcciones-UX-Impresion.md`): plan
  ejecutado sobre ambos PoC, con el modelo de errores con código, la divergencia adoptada sobre H-5
  y el resultado de la ejecución. La librería `MotorDsl.*` no fue modificada (sigue en v1.0.13).
- **Análisis de soporte iOS y NuGet multiplataforma**
  (`Analisis/03-Analisis-IOs/Nuget-Multiplaforma.md`): evaluación del desarrollo actual frente al
  objetivo de dar soporte a dispositivos iOS, con 5 alternativas de transporte y su estructura de
  solución resultante. Incluye la verificación empírica de cómo NuGet resuelve los assets por
  plataforma, hecha sobre los `.nupkg` descargados de nuget.org (`MotorDsl.* 1.0.13`,
  commit `ebe03ef`), y 5 hallazgos colaterales de CI/CD que condicionan la publicación. La
  recomendación es un paquete `MotorDsl.Network` con TFM `net10.0` puro. No se modificó código.
- Carpeta `PROMPTs/` para el material de generación documental.

### Seguridad

- **Datos privados fuera de la punta pública** (2026-11-18): en las bitácoras, núcleos,
  expedientes y relevamientos de `PROMPTs/DEVs/Features/04-Agregar-PAX-A910S/OUTPUTs/` y en
  `reporte-derivas.md`, los nombres de la app consumidora y de su sistema web, la organización, los
  repositorios privados, los clientes, los servicios privados, los equipos, las IP, las rutas
  locales, la serie del dispositivo y los nombres de terceros pasan a marcadores (`<app>`,
  `<app-web>`, `<org>`, `<repo>`, `<cliente>`, `<servicio-privado>`, `<equipo-N>`, `<ip-tailnet>`,
  `<ip-privada>`, `<host-publico>`, `<serie-del-g42>`, `<workspace>`, `{raíz-de-worktrees}`,
  `{dir-de-trabajo}`, `{tmp-de-sesiones}`). Tres archivos cambian de nombre por el mismo motivo
  (`Fix08-App-Web.md`, `App-menu-bundles-y-PRs-60-62.md` y `Nucleos/04-Web-App.md`), y dos
  capturas de `Implementacion/Images/` tapan el nombre de la organización. Sólo cambia la punta:
  la historia no se reescribe. Queda sin tocar `PROMPTs/Features/03-Extender-A-IOs/Crear-Extender-A-IOs.md`,
  que es un prompt del PO.

## [1.0.0] - 2026-07-15

Primera generación completa del conjunto documental por ingeniería inversa sobre el código en
**v1.0.13 @83677eb**. Todo el material queda en `status: draft`, pendiente de revisión humana para
promoverse a `approved`.

### Añadido

- **Base de conocimiento `ia-db/`**: punto de entrada único (`README.md`) más 9 índices temáticos
  (núcleo/pipeline, DSL y modelos, renderizado base, impresión y transports, capa MAUI, samples,
  tests, build/devops y mapa de la documentación previa).
- **Índice maestro** `PrintThermal_Motor_Maui-docs/README.md`, `GLOSSARY.md` (vocabulario
  controlado) y `docs-manifest.yaml` (manifiesto máquina-legible con el `type` de cada pieza y el
  gap documental calculable).
- **Documentación por pieza** (`pieces/`) de las 7 librerías y los samples:
  - `MotorDsl.Core`, `MotorDsl.Parser`, `MotorDsl.Rendering`, `MotorDsl.Extensions`: README +
    `api-reference`.
  - `MotorDsl.Printing.Abstractions`: README + `api-reference` + `extension-guide`.
  - `MotorDsl.Bluetooth`: README + `api-reference` + `platform-notes`.
  - `MotorDsl.Maui`: README + `component-catalog` + `usage-guide`.
  - `samples`: README + `integration-snippets` (snippets con procedencia, Marco §13).
- **Nivel solución** (`docs/`): visión, C4 de contexto y contenedores, vistas de runtime con datos
  sintéticos, conceptos transversales y extensibilidad, catálogo de APIs, 4 ADRs reconstruidos y la
  política de agentes.
- **Reporte de derivas** (`docs/04-decisions/reporte-derivas.md`): 17 contradicciones entre fuentes
  y 17 observaciones de comportamiento del código, reportadas para decisión humana.
- **Reporte de gap documental** (`docs/gap-documental.md`) con las omisiones declaradas (estilo
  arc42) y su justificación.

### Notas

- El repositorio de código de origen no fue modificado (documentación de solo lectura).
- Verificación: 0 enlaces relativos rotos; frontmatter completo en los 37 documentos del conjunto
  documental (los índices de la `ia-db` abren con blockquote de propósito, sin frontmatter, según el
  perfil de indexado).

[Unreleased]: https://github.com/Aplicada-Streaming/PrintThermal_Motor_Maui.Documentacion/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/Aplicada-Streaming/PrintThermal_Motor_Maui.Documentacion/releases/tag/v1.0.0
