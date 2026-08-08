# ia-db — MotorDsl (ThermalPrint.MotorDsl.Core)

> **Instrucción para IA**: este archivo es el **punto de entrada único** a la base de
> conocimiento del proyecto. Antes de explorar el repositorio, leé la tabla de navegación,
> identificá el índice que cubre tu tema y cargá **solo ese índice** (a lo sumo dos). Ampliá a
> los archivos fuente únicamente cuando el índice resulte insuficiente. No recorras el
> repositorio completo: cada índice referencia sus fuentes exactas.
>
> **Convención de rutas**: todas las rutas de fuente son relativas a la raíz del repositorio
> indexado, `/DEV/ThermalPrint.MotorDsl.Core`. Esta ia-db vive en el repositorio hermano
> `/DEV/ThermalPrint.MotorDsl.Core.Documentacion`.

---

## Navegación — «Necesitas saber… → Leé este índice»

| Necesitás saber… | Leé este índice |
|---|---|
| Qué es el proyecto, stack, paquetes, decisiones clave | [00_MASTER-INDEX](indexes/00_MASTER-INDEX.md) |
| Cómo funciona el pipeline Parse → Evaluate → Layout → Render; contratos del motor; validaciones | [01_nucleo-pipeline](indexes/01_nucleo-pipeline.md) |
| Sintaxis del DSL JSON, tipos de nodo, formatos `template` / `integrated`, modelos del AST | [02_dsl-y-modelos](indexes/02_dsl-y-modelos.md) |
| Renderers `text` y `escpos`, comandos ESC/POS, registro y DI fluent | [03_renderizado-base](indexes/03_renderizado-base.md) |
| Impresión térmica: orquestador, transports, Bluetooth SPP, capacidades, logo NV, diagnóstico | [04_impresion-transports](indexes/04_impresion-transports.md) |
| Controles MAUI, renderers PDF / bitmap ESC/POS / raster preview, rasterizadores | [05_maui-ui-renderers](indexes/05_maui-ui-renderers.md) |
| Las 5 apps de ejemplo y el patrón canónico de integración | [06_samples](indexes/06_samples.md) |
| Suite de pruebas: qué cubre cada archivo, fakes, código enlazado por fuente | [07_tests](indexes/07_tests.md) |
| Build, TFMs, versionado unificado, publicación NuGet, workflows CI/CD, scripts | [08_build-devops](indexes/08_build-devops.md) |
| Dónde está la documentación previa (32 CU, reglas, sprints, guías) y la doc derivada | [09_docs-existentes](indexes/09_docs-existentes.md) |

---

## Resumen ejecutivo

| Dato | Valor |
|---|---|
| Proyecto | **MotorDsl** (repo `PrintThermal_Motor_Maui` / carpeta local `ThermalPrint.MotorDsl.Core`) |
| Tipo | Librería .NET distribuida como **7 paquetes NuGet** + 5 apps MAUI de ejemplo |
| Stack | .NET 10 · C# · .NET MAUI (Android/iOS) · xUnit · SkiaSharp · PdfSharpCore · QRCoder |
| Repositorio | `origin` = `https://github.com/hdcm-dev/ThermalPrint.MotorDsl.Core.git`; los `.csproj` y el README declaran `RepositoryUrl` = `https://github.com/Aplicada-Streaming/PrintThermal_Motor_Maui` |
| Versión indexada | `1.0.13` (CHANGELOG) · rama `main` · commit `83677eb` (2026-07-13) |
| Licencia | MIT |

**Función principal.** Interpreta plantillas de documento escritas en un DSL JSON, resuelve los
datos contra un contexto, calcula el layout según el perfil del dispositivo de salida y
renderiza el resultado a texto plano, ESC/POS (`byte[]`), PDF o PNG de vista previa. La salida
ESC/POS se envía a una impresora térmica por un *transport* (hoy Bluetooth Classic SPP en
Android).

**Arquitectura en una línea.** Pipeline de 4 etapas (`Parse → Evaluate → Layout → Render`) sobre
contratos por interfaz, con dos puntos de extensión abiertos: `IRenderer` (por `Target` string) e
`IThermalPrinterTransport` (por `Kind` string), ambos cableados por DI fluent.

```text
[DSL JSON] → Parser → Evaluator → LayoutEngine → Renderer → Output (text | byte[] | PDF | PNG)
                                                               ↓
                                                    IThermalPrinterTransport
                                                               ↓
                                                       Impresora física
```

---

## Estructura del repositorio indexado

```text
ThermalPrint.MotorDsl.Core/
├── src/
│   ├── MotorDsl.Core/                    Contratos, modelos/AST, Evaluator, LayoutEngine, validadores, DocumentEngine
│   ├── MotorDsl.Parser/                  DslParser: JSON → DocumentTemplate (AST)
│   ├── MotorDsl.Rendering/               TextRenderer, EscPosRenderer, EscPosCommands
│   ├── MotorDsl.Extensions/              DI fluent: AddMotorDslEngine / AddTemplates / AddProfiles / AddRenderer
│   ├── MotorDsl.Printing.Abstractions/   Contratos de transport + ThermalPrinterService (retry, eventos, diagnóstico)
│   ├── MotorDsl.Bluetooth/               Transport Bluetooth Classic SPP (Android); iOS no soportado
│   ├── MotorDsl.Maui/                    Controles MAUI + renderers PDF / escpos-bitmap / raster-preview
│   └── MotorDsl.Tests/                   Suite xUnit (net10.0)
├── samples/                              5 apps MAUI de ejemplo (ProjectReference y PackageReference)
├── docs/                                 Documentación previa del proyecto (12 carpetas temáticas)
├── scripts/                              local/ (run Android) · mobile/ (APK) · nuget/ (publicación)
├── .github/workflows/                    ci.yml, cd-nuget.yml, cd-android.yml, 3 × cd-ios-*.yml
├── PrintThermalDriver.slnx               Solución (formato slnx)
├── CHANGELOG.md                          Keep a Changelog; entrada vigente 1.0.13
└── nupkg/                                .nupkg generados (gitignored)
```

---

## Restricciones para IA que consuma este índice

- **No modificar el repositorio indexado desde esta base.** La ia-db documenta; no autoriza cambios.
- **No tratar los índices como fuente de verdad por encima del código.** Si la evidencia del
  repositorio contradice un índice, prevalece la evidencia: corregí el índice
  (ver `Actualizar-Indexado.md`) y no propagues el dato obsoleto.
- **No duplicar contenido entre índices.** Cada dominio vive en un único índice; el resto referencia.
- **No inferir lo que no está indexado.** Lo marcado como «no verificado» requiere abrir la fuente.
- **Vigencia**: esta base refleja el estado del commit `83677eb` (v1.0.13). Commits posteriores no
  están reflejados.

---

## Manifiesto de generación

- Generado por : `/IA/IA.Prompts/Tool-Prompts/Indexado-Documentado/Iniciar-Indexado.md`
- Profile      : `/IA/IA.Prompts/PromptFramework/Profiles/Knowledge-Indexing.md`
- Alcance      : `/DEV/ThermalPrint.MotorDsl.Core` (modo proyecto único)
- Destino      : `/DEV/ThermalPrint.MotorDsl.Core.Documentacion/ia-db` (indicado en la invocación)
- Fuentes      : `src/`, `samples/`, `docs/`, `scripts/`, `.github/workflows/`, `README.md`, `CHANGELOG.md`, `PrintThermalDriver.slnx`
- Exclusiones  : `.git`, `bin`, `obj`, `nupkg`, `.vs`, binarios (`.ttf`, `.bmp`, `.base64`, `.svg`), lo ignorado por `.gitignore`
- Estado fuente: rama `main` · commit `83677eb` · versión `1.0.13`
- Generado     : 2026-08-07 · Versión: 1.0
- Actualizar   : `/IA/IA.Prompts/Tool-Prompts/Indexado-Documentado/Actualizar-Indexado.md`

**Nomenclatura de índices**: los nombres `01_nucleo-pipeline` … `09_docs-existentes` se toman de
`PrintThermal_Motor_Maui-docs/docs-manifest.yaml` (campo `ia_db_index` de cada pieza), que ya los
declaraba antes de existir esta base. Se respetan para mantener la trazabilidad manifiesto ↔ ia-db.
