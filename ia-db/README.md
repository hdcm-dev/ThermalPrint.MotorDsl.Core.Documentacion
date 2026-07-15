# ia-db — PrintThermal_Motor_Maui (MotorDsl)

> **🤖 Punto de entrada único de la base de conocimiento.** Este archivo es lo primero
> que lee un agente de IA que necesite contexto del proyecto **MotorDsl** sin releer el
> código fuente completo. Uso: (1) ubicá tu tema en la *tabla de navegación*, (2) cargá
> **solo** ese índice de `indexes/`, (3) ampliá a la fuente real (en el origen) únicamente
> ante insuficiencia comprobada. No recorras el repositorio entero cuando la respuesta ya
> está indexada aquí. Todo dato de esta ia-db es trazable a una ruta del origen en la
> versión de referencia **v1.0.13 @83677eb**.

---

## Tabla de navegación — «Necesitás saber… → Leé este índice»

| Necesitás saber… | Índice |
|---|---|
| Cómo fluye un documento (JSON → bytes): pipeline, `DocumentEngine`, contratos, registry | [`indexes/01_nucleo-pipeline.md`](indexes/01_nucleo-pipeline.md) |
| El DSL JSON, los formatos *classic* vs *integrated*, y el modelo de nodos / documento | [`indexes/02_dsl-y-modelos.md`](indexes/02_dsl-y-modelos.md) |
| Renderers base (texto, ESC/POS), comandos ESC/POS y el fluent DI `AddMotorDslEngine` | [`indexes/03_renderizado-base.md`](indexes/03_renderizado-base.md) |
| Impresión térmica: orquestador, retry, capacidades, transport Bluetooth SPP (Android) | [`indexes/04_impresion-transports.md`](indexes/04_impresion-transports.md) |
| Capa MAUI: controles UI, renderers PDF / bitmap / raster-preview, diagnóstico | [`indexes/05_maui-ui-renderers.md`](indexes/05_maui-ui-renderers.md) |
| Los 5 samples: qué demuestra cada uno, classic vs integrated, project-ref vs NuGet | [`indexes/06_samples.md`](indexes/06_samples.md) |
| Los tests: qué cubre cada clase, framework, trazas a casos de uso | [`indexes/07_tests.md`](indexes/07_tests.md) |
| Build, scripts, CI/CD (GitHub Actions), versionado y empaquetado NuGet | [`indexes/08_build-devops.md`](indexes/08_build-devops.md) |
| Mapa de la documentación previa (`docs/`): casos de uso, reglas, IDs de requisitos | [`indexes/09_docs-existentes.md`](indexes/09_docs-existentes.md) |

---

## Resumen ejecutivo (1 pantalla)

| Dato | Valor |
|---|---|
| Proyecto | **PrintThermal_Motor_Maui** (producto: **MotorDsl**) |
| Tipo | Solución multi-proyecto de **librerías .NET** (7 paquetes NuGet) + 5 samples MAUI |
| Función | Generar documentos desde un **DSL JSON** y renderizarlos a **texto, ESC/POS, PDF y preview raster**, con **impresión térmica Bluetooth SPP** desde apps .NET MAUI |
| Stack | .NET 10; C#; System.Text.Json; SkiaSharp, PdfSharpCore, QRCoder (capa MAUI); xUnit (tests) |
| Repo | `github.com/Aplicada-Streaming/PrintThermal_Motor_Maui` · Licencia MIT |
| Versión de referencia | **v1.0.13** (`@83677eb`, `git describe` = `v1.0.13-2-g83677eb`) |
| Autor / owner | Fernando Rafael Filipuzzi — Aplicada Streaming |

**Arquitectura en una línea:** pipeline `JSON → Parser → Evaluator → LayoutEngine → Renderer → bytes`,
con `Renderer` seleccionable por `Target` y `Transport` seleccionable por `Kind` — ambos extensibles
sin tocar el núcleo (`MotorDsl.Core`).

**Piezas (proyectos `src/`):** `MotorDsl.Core` (núcleo, sin dependencias) · `MotorDsl.Parser`
(JSON→AST) · `MotorDsl.Rendering` (texto + ESC/POS) · `MotorDsl.Extensions` (DI fluent) ·
`MotorDsl.Printing.Abstractions` (contratos transport + orquestador) · `MotorDsl.Bluetooth`
(transport BT Android; iOS lanza `PlatformNotSupportedException`) · `MotorDsl.Maui` (controles +
renderers PDF/bitmap/preview + diagnóstico) · `MotorDsl.Tests` (xUnit).

---

## Estructura de la ia-db

```text
ia-db/
├── README.md                        ← este archivo: entrada única + navegación
└── indexes/
    ├── 01_nucleo-pipeline.md        ← DocumentEngine, contratos, registry, providers
    ├── 02_dsl-y-modelos.md          ← DSL JSON, formatos classic/integrated, nodos
    ├── 03_renderizado-base.md       ← TextRenderer, EscPosRenderer, EscPosCommands, DI fluent
    ├── 04_impresion-transports.md   ← ThermalPrinterService, capacidades, transport Bluetooth
    ├── 05_maui-ui-renderers.md      ← controles MAUI, PDF/bitmap/raster renderers, diagnóstico
    ├── 06_samples.md                ← los 5 samples MAUI
    ├── 07_tests.md                  ← inventario de tests (xUnit)
    ├── 08_build-devops.md           ← scripts, CI/CD, versionado, NuGet
    └── 09_docs-existentes.md        ← mapa de docs/ previa (CU/RN/RC/NB)
```

Cada índice abre con un blockquote de **propósito + fuentes primarias**, privilegia tablas y
diagramas Mermaid sobre prosa, respeta un presupuesto de 300–500 líneas y referencia las fuentes
del origen para el detalle. Todos usan la misma versión de referencia (**v1.0.13 @83677eb**).

---

## Restricciones para agentes que consuman esta ia-db

- **La ia-db es un punto de entrada, no una copia** del código: recuperá desde el índice antes de
  releer fuentes; ampliá a la fuente real solo ante insuficiencia comprobada.
- **Todo es trazable**: cada afirmación cita una ruta del origen (y `#Lx-Ly` cuando corresponde).
  Lo no verificable está marcado «No verificado»; no lo tomes como hecho.
- **La versión importa**: los `#Lx-Ly` valen para **v1.0.13 @83677eb**. Si el origen avanzó,
  reverificá antes de recomendar.
- **Solo lectura del origen**: esta base documenta; no habilita a modificar
  `PrintThermal_Motor_Maui`. Toda escritura vive bajo `PrintThermal_Motor_Maui.Documentacion`.
- La documentación humana derivada de esta ia-db vive en `../PrintThermal_Motor_Maui-docs/`
  (índice maestro en su `README.md`).

---

## Manifiesto de generación

- **Generado por** : `/IA.Prompting.Templates/Tool-Prompts/Documentar-Fuentes-Software.md`
  (Profile `Solution-Documentation` → Fase 1, Profile delegado `Knowledge-Indexing`)
- **Alcance**      : solución `PrintThermal_Motor_Maui` (8 proyectos `src/`, 5 samples, `docs/`,
  `scripts/`, `.github/workflows/`)
- **Fuentes**      : `src/`, `samples/`, `docs/`, `scripts/`, `.github/`, `README.md`, `CHANGELOG.md`,
  `NuGet.config`, `PrintThermalDriver.slnx`
- **Exclusiones**  : `.git`, `bin/`, `obj/`, `nupkg/` (artefactos), binarios (imágenes, fuentes),
  la propia ia-db
- **Generado**     : 2026-07-14 · **Versión**: 1.0 · **Origen indexado**: v1.0.13 @83677eb
- **Actualizar**   : reejecutar el Tool-Prompt en modo incremental, o
  `/IA.Prompting.Templates/Tool-Prompts/Actualizar-Indexado.md` sobre esta base
