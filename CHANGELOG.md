# Changelog

Todos los cambios notables de la **documentación de MotorDsl** se registran en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/). Este repositorio
contiene el conjunto documental (`PrintThermal_Motor_Maui-docs`) y la base de conocimiento
(`ia-db`) del repositorio de código [`PrintThermal_Motor_Maui`](https://github.com/Aplicada-Streaming/PrintThermal_Motor_Maui),
generados conforme al Marco de Documentación de Software.

## [Unreleased]

### Cambiado

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
