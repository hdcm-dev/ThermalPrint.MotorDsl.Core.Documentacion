# ia-db — PrintThermal_Motor_Maui (MotorDsl)

> **Instrucción para IA**
>
> Este archivo es el **punto de entrada único** a la base de conocimiento del repositorio
> `PrintThermal_Motor_Maui`. Antes de leer código o documentación completa:
>
> 1. leé el resumen ejecutivo de abajo para ubicarte;
> 2. buscá tu necesidad en la tabla de navegación;
> 3. cargá **solo** el índice —o los dos índices— que te indique;
> 4. abrí las fuentes citadas únicamente si el índice resulta insuficiente.
>
> Nunca recorras el repositorio entero cuando la respuesta ya está indexada. Cada índice cita
> sus fuentes con rutas relativas a la raíz del repositorio indexado
> (`/Libs/NugetOrg/PrintThermal_Motor_Maui`).

---

## Navegación — «Necesitás saber… → leé este índice»

| Necesitás saber… | Leé este índice |
|---|---|
| Qué es el proyecto, qué stack usa, cómo se reparten los 8 paquetes, qué decisiones lo condicionan | [`00_MASTER-INDEX.md`](indexes/00_MASTER-INDEX.md) |
| Cómo corre el pipeline (parse → evaluar → layout → render), qué contratos existen, cómo se arma el motor por DI | [`01_nucleo-pipeline.md`](indexes/01_nucleo-pipeline.md) |
| Cómo se escribe una plantilla DSL, qué nodos hay, `template` vs `integrated`, cómo se resuelven bindings y condiciones | [`02_dsl-y-modelos.md`](indexes/02_dsl-y-modelos.md) |
| Qué renderers existen, qué `Target` usa cada uno, qué bytes ESC/POS se emiten, cómo agregar un renderer propio | [`03_renderizado-base.md`](indexes/03_renderizado-base.md) |
| Cómo se imprime: transports, orquestador, retry, capacidades, red TCP, Bluetooth, logos NV | [`04_impresion-transports.md`](indexes/04_impresion-transports.md) |
| Qué controles MAUI trae la librería, qué renderers gráficos hay, cómo funciona el diagnóstico | [`05_maui-ui-renderers.md`](indexes/05_maui-ui-renderers.md) |
| Qué sample mirar como referencia, qué demuestra cada uno, cómo correrlos | [`06_samples.md`](indexes/06_samples.md) |
| Qué cubre la suite de tests, cómo está organizada, dónde está el borde sin cubrir | [`07_tests.md`](indexes/07_tests.md) |
| Cómo compila y publica el proyecto, qué hace cada workflow, cómo se versiona, cómo desarrollar en Linux | [`08_build-devops.md`](indexes/08_build-devops.md) |
| Dónde está la documentación funcional previa (casos de uso, reglas, sprints, guías de developer) | [`09_docs-existentes.md`](indexes/09_docs-existentes.md) |

---

## Resumen ejecutivo

| Dato | Valor |
|---|---|
| Proyecto | **MotorDsl** — repositorio `PrintThermal_Motor_Maui` |
| Tipo | Librería .NET distribuida como **8 paquetes NuGet**. No es una app ni un servicio |
| Stack | .NET 10 · C# · `net10.0` puro en 6 paquetes; `net10.0-android` + `net10.0-ios` en 2 |
| Repo | `https://github.com/Aplicada-Streaming/PrintThermal_Motor_Maui` · licencia MIT |
| Solución | `PrintThermalDriver.slnx` (formato slnx: 9 proyectos en `src/` + 5 samples) |
| Versión publicada | `1.0.13` (2026-07-13). El octavo paquete `MotorDsl.Network` está en `[Unreleased]` |
| Dependencias externas | SkiaSharp 3.119.2, PdfSharpCore 1.3.67, QRCoder 1.8.0 (solo `MotorDsl.Maui`); `Microsoft.Extensions.DependencyInjection.Abstractions` 10.0.8 |

**Función principal**: convierte un documento descrito en un **DSL JSON** en la salida concreta
que consume un dispositivo —texto plano, bytes ESC/POS, PDF o un raster de vista previa— y lo
envía a una impresora térmica por Bluetooth Classic SPP (Android) o por socket TCP al puerto 9100
(Android, iOS y escritorio).

**Arquitectura en una línea**: pipeline de cuatro etapas con representaciones intermedias
(`Parse → Evaluate → Layout → Render`), extensible por dos puntos de enchufe string —`IRenderer.Target`
para el formato de salida y `IThermalPrinterTransport.Kind` para el canal físico—, sin que el núcleo
conozca ninguna implementación concreta.

```text
[DSL JSON] → Parser → Evaluator → LayoutEngine → Renderer → Output (string | byte[])
                                                      ↓
                                   Transport (Bluetooth SPP / TCP 9100 / futuros)
                                                      ↓
                                              Impresora física
```

---

## Estructura del repositorio indexado

```text
PrintThermal_Motor_Maui/
├── src/
│   ├── MotorDsl.Core/                    Contratos, modelos/AST, Evaluator, LayoutEngine, validadores
│   ├── MotorDsl.Parser/                  DslParser: JSON → DocumentTemplate
│   ├── MotorDsl.Rendering/               EscPosRenderer, TextRenderer, tabla de comandos ESC/POS
│   ├── MotorDsl.Extensions/              Fluent DI: AddMotorDslEngine + MotorDslBuilder
│   ├── MotorDsl.Printing.Abstractions/   IThermalPrinterTransport, ThermalPrinterService, capacidades
│   ├── MotorDsl.Network/                 Transport TCP 9100 — net10.0 puro (habilita iOS)
│   ├── MotorDsl.Bluetooth/               Transport BT Classic SPP — solo Android
│   ├── MotorDsl.Maui/                    Controles MAUI, renderers PDF/bitmap/preview, diagnóstico
│   └── MotorDsl.Tests/                   xUnit — 285 métodos de prueba
├── samples/                              5 apps MAUI de demostración
├── docs/                                 Documentación funcional y técnica previa (12 carpetas)
├── scripts/{local,mobile,nuget}/         Build local, publicación APK, publicación NuGet
├── .github/workflows/                    ci.yml + 5 workflows de CD
└── .devcontainer/                        Contenedor .NET 10 para desarrollar en Linux
```

---

## Restricciones para un agente que consuma este índice

- **No confundir el repositorio con su documentación.** El código vive en
  `/Libs/NugetOrg/PrintThermal_Motor_Maui`; esta ia-db y la documentación derivada viven en
  `/Libs/NugetOrg/PrintThermal_Motor_Maui.Documentacion`. Son dos repositorios git distintos.
- **Los índices son un destilado, no la fuente.** Si vas a modificar código, abrí el archivo citado.
  Ninguna afirmación de esta base autoriza a editar sin leer.
- **No inventes versiones ni fechas.** Lo publicado es `1.0.13`; `MotorDsl.Network` todavía no salió
  a nuget.org y por eso los samples «Nuget» apuntan a `ProjectReference` (ver `06_samples`).
- **No supongas que hay build en esta máquina.** No hay SDK .NET instalado en el host: los TFM
  `net10.0` se compilan en el devcontainer, `net10.0-android` en el runner self-hosted y
  `net10.0-ios` solo en macOS.
- **La cobertura declarada aquí es estática** (conteo de atributos `[Fact]`/`[Theory]`), no una
  corrida verificada. Ver `07_tests` antes de afirmar «los tests pasan».

---

## Manifiesto de generación

- Generado por : `/IA/PROMPTs/IA.Prompts/Tool-Prompts/Indexado-Documentado/Iniciar-Indexado.md`
- Profile      : `/IA/PROMPTs/IA.Prompts/PromptFramework/Profiles/Knowledge-Indexing.md`
- Invocado por : `/Libs/NugetOrg/PrintThermal_Motor_Maui.Documentacion/PROMPTs/Indexado/Crear-Indexado.md`
- Alcance      : `/Libs/NugetOrg/PrintThermal_Motor_Maui` (modo proyecto único)
- Destino      : `/Libs/NugetOrg/PrintThermal_Motor_Maui.Documentacion/ia-db` (indicado en la invocación)
- Fuentes      : `src/`, `samples/`, `docs/`, `scripts/`, `.github/workflows/`, `.devcontainer/`, `README.md`, `CHANGELOG.md`, `PrintThermalDriver.slnx`
- Exclusiones  : `.git`, `.vs`, `.vscode`, `bin`, `obj`, `nupkg`, binarios (`.ttf`, `.bmp`, `.svg`, `.base64`) y lo ignorado por el `.gitignore` del proyecto
- Estado fuente: rama `main` · commit `e688f3c` · última versión publicada `1.0.13`
- Generado     : 2026-09-02 · Versión: 2.0 (regeneración completa desde cero)
- Actualizar   : `/IA/PROMPTs/IA.Prompts/Tool-Prompts/Indexado-Documentado/Actualizar-Indexado.md`

**Trabajo sin commitear no indexado**: al momento de generar, el repositorio tenía tres archivos
modificados en `samples/MotorDsl.MultaApp/` (`Pages/MainPage.xaml`, `Pages/MainPage.xaml.cs`,
`Templates/MultaDsl.cs`). Se indexó el contenido **commiteado** en `e688f3c`; esos cambios locales
quedan fuera.

**Nomenclatura de índices**: los nombres `01_nucleo-pipeline` … `09_docs-existentes` provienen del
campo `ia_db_index` de `PrintThermal_Motor_Maui-docs/docs-manifest.yaml`, en este mismo repositorio
de documentación. Se respetan para mantener la trazabilidad manifiesto ↔ ia-db.
