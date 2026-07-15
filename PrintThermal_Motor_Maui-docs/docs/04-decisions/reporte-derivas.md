---
doc_id: DRIFT-001
doc_type: drift-report
title: Reporte de derivas y observaciones — MotorDsl
version: 1.0.0
status: draft
origin: reverse-engineered
confidence: high
owner: equipo-motordsl
last_review: 2026-07-14
audience: [dev, arquitectura, qa, agentes-automaticos]
classification: uso-interno
source_ref: v1.0.13 @83677eb
---

# Reporte de derivas y observaciones

## Resumen ejecutivo

Este documento reúne las **contradicciones entre fuentes** y los **comportamientos del código que
sorprenden** detectados durante la documentación por ingeniería inversa de MotorDsl
(**v1.0.13 @83677eb**). Conforme al Marco (§9, §12.4 regla 5) y a `Rule-Drift-Control`, **se
reportan; no se resuelven en silencio**: cada entrada es un candidato a decisión humana (corregir
código, corregir documentación, o registrar un ADR). Nada de esto modifica el origen.

**Cómo leer la severidad:** 🔴 alta (puede causar salida incorrecta o release roto), 🟡 media
(confunde o degrada sin romper), ⚪ baja (cosmético / deuda menor).

---

## A. Contradicciones entre fuentes (documentación, build, config)

| # | Deriva | Severidad | Fuente |
|---|---|---|---|
| D1 | `cd-nuget.yml` empaqueta **solo 4 paquetes** (Core, Parser, Rendering, Extensions); el script local publica **7**. `notas.md` los llama "equivalentes": hoy no lo son. | 🔴 | `.github/workflows/cd-nuget.yml` vs `scripts/nuget/publish-motordsl-nuget.bat`, `scripts/nuget/notas.md` |
| D2 | Conteo de tests divergente: `ci.yml` menciona **185**; `copilot-instructions.md` menciona **212 (185+27)**. | 🟡 | `.github/workflows/ci.yml` vs `.github/copilot-instructions.md` |
| D3 | `cd-ios-multaapp.nuget.yml` dispara por `paths: samples/MotorDsl.MultaApp.Nuget/**` y compila `MotorDsl.MultaApp.csproj`, pero la carpeta real es `samples/MotorDsl.Nuget.MultaApp/`: **el trigger nunca coincide**. | 🔴 | `.github/workflows/cd-ios-multaapp.nuget.yml` |
| D4 | `cd-ios-multaapp.yml` y `cd-ios-multaapp.nuget.yml` comparten el mismo `name:` en Actions. | ⚪ | `.github/workflows/` |
| D5 | `copilot-instructions.md` desactualizado: destino NuGet "GitHub Packages" (real: nuget.org), sample `MotorDsl.MultaApp.Nuget` inexistente, omite 3 libs de `src` y un workflow, cita `PrintThermalDriver.sln` (real: `.slnx`). | 🟡 | `.github/copilot-instructions.md` |
| D6 | Typo en el nombre de salida: `MotorDsl.Nuget.MultaAppt.apk` (t de más). | ⚪ | `scripts/mobile/publish-MotorDsl.Nuget.MultaApp-apk.bat` |
| D7 | `docs/README.md` menciona `scripts/docker` que no existe. | ⚪ | `docs/README.md` |
| D8 | Los workflows iOS dependen de un instalador **Xcode 26.0 alojado en un Google Drive personal** (`gdown`, ID hardcodeado): no reproducible si el archivo desaparece. | 🟡 | `.github/workflows/cd-ios-*.yml` |
| D9 | `CHANGELOG.md` solo documenta **1.0.13**; la historia 1.0.0–1.0.12 no está registrada (los tags git sí existen). | 🟡 | `CHANGELOG.md` vs `git tag` |
| D10 | Nombres de archivo irregulares en requisitos: `CU-04` sin sufijo `_v1.0`; espacios en `CU-23 Aplicar restricciones del dispositivo.md` y `NB-02 Estandarización.v1.0.md`. | ⚪ | `docs/02_especificacion_funcional/`, `docs/01_necesidades_negocio/` |
| D11 | `decisiones-arquitectura_v1.0.md` se titula "ADR — Sistema de Gestión de Reclamos": parece heredado del proyecto **consumidor**, no del motor. | 🟡 | `docs/05_arquitectura_tecnica/decisiones-arquitectura_v1.0.md` |
| D12 | `docs/10_developer_guide/README.md` indexa 7 de los 12 documentos de su carpeta (quedan fuera diagnostics, integracion-api-rest, perfiles-impresoras-reales y los 2 de imágenes térmicas). | ⚪ | `docs/10_developer_guide/README.md` |
| D13 | El orden de push NuGet declara `Printing.Abstractions → Core → …`, anteponiendo `Abstractions` a `Core` pese a que `Abstractions` **depende** de `Core`. | 🟡 | `scripts/nuget/publish-motordsl-nuget.bat` |
| D14 | El sample canónico `MotorDsl.Nuget.Integrated.MultaApp` **no consume NuGet** hoy: usa `ProjectReference` temporal a los 7 proyectos porque usa API de "fase 4" (logo NV) aún no publicada. El catálogo `samples/Readme.md` quedó desactualizado. | 🟡 | `samples/MotorDsl.Nuget.Integrated.MultaApp/*.csproj#L72-L83`, `samples/Readme.md` |
| D15 | IP pública **hardcodeada** `http://190.188.36.33:5000` como `backendBaseUrl` en `motordsl-config.json` de los 5 samples (un script de publish la reescribe). | 🟡 | `samples/*/Resources/Raw/motordsl-config.json#L1-L4` |
| D16 | Los assets de logo/firma del acta son **BMP** base64 (magic `Qk0`) aunque el comentario dice PNG. | ⚪ | `samples/*/Templates/Multa*Dsl.cs` |
| D17 | Documentos previos con **versiones coexistentes** sin marca clara de vigencia: `compatibilidad-plataformas` v1.0/v1.1, `arquitectura-solucion` v1.0/v1.1, `CU-06` v1.0/v2.0, `CU-21`/`CU-26` (fusión), `CU-24`/`CU-25` (renombrados), y `soporte-imagenes-termicas.md` vs `soporte_imagenes_termicas.md`. | 🟡 | `docs/00_contexto/`, `docs/02_especificacion_funcional/`, `docs/10_developer_guide/` |

---

## B. Comportamientos del código que sorprenden (deuda técnica)

Reportados como observación, no como bug confirmado: requieren decisión humana (¿es intencional?).

| # | Observación | Severidad | Fuente |
|---|---|---|---|
| T1 | En el camino *classic*, `Evaluator.Evaluate` hardcodea `Id="evaluated-doc"` y `Version="1.0"`, **perdiendo** el `Id`/`Version` del template. `EvaluateTemplate` sí los preserva, pero no está en `IEvaluator` ni lo usa el engine. | 🟡 | `Evaluators/Evaluator.cs#L30-L81` vs `Engine/DocumentEngine.cs#L111` |
| T2 | En *classic*, el `Evaluator` recrea `TextNode`/`ImageNode`/`ContainerNode` **sin copiar `Style`** → `align`/`bold` del DSL se pierden antes del layout; en *integrated* sobreviven. | 🔴 | `Evaluators/Evaluator.cs#L162,#L185,#L277` |
| T3 | Los *warnings* de evaluación (variables no resueltas) **no** se propagan a `RenderResult`: solo quedan como texto `{{UNRESOLVED:…}}` en la salida. | 🟡 | `Engine/DocumentEngine.cs#L110-L128` |
| T4 | `RendererRegistry` hace **fallback silencioso a `text`** ante un `Target` desconocido: un `RenderTarget` mal escrito degrada sin aviso. | 🔴 | `Engine/RendererRegistry.cs#L19-L29` |
| T5 | `EscPosRenderer` fija **CP437** para texto (`ESC t 0`) ignorando la capability `codepage` y `DeviceProfile.CodePage`/`CodePageCommand`; solo QR/barcode respetan `codepage`. | 🟡 | `EscPosRenderer.cs#L33-L34,#L121-L145` |
| T6 | `DeviceProfile.CodePage`/`CodePageCommand`/`BaudRate`/`SupportedBarcodes` **sin consumidor** en los proyectos indexados (uso presumible en transports fuera de alcance; no verificado). | ⚪ | `Models/DeviceProfile.cs#L8-L12` |
| T7 | El `EscPosRenderer` que registra `AddMotorDslEngine` se instancia **sin `IBitmapRasterizer`** → los bitmaps degradan a `[BITMAP]` salvo que se registre un renderer propio (lo hace `AddMotorDslMaui`). | 🟡 | `MotorDslServiceCollectionExtensions.cs#L23` |
| T8 | No existe método fluent `AddData()` para `IDataProvider`; `IPrintErrorHandler`/`IBitmapRasterizer` no se registran por defecto en `MotorDslBuilder`. | ⚪ | `MotorDslBuilder.cs#L20-L40` |
| T9 | `TextNode.BindPath` se parsea y propaga pero **nada lo usa** para resolver texto. | ⚪ | `Models/TextNode.cs#L17-L23`, `Evaluators/Evaluator.cs#L142-L163` |
| T10 | `LayoutInfo.IsTruncated` **nunca** se setea a `true`: las celdas de tabla truncan sin marcarlo. | 🟡 | `Layout/LayoutEngine.cs#L275-L286` |
| T11 | Constantes públicas sin consumidor en alcance: `EscPosCommands.QrStoreData`, `CutPartial`, `FeedLines`. | ⚪ | `EscPosCommands.cs#L29-L48` |
| T12 | El `catch` del overload *classic* `string` etiqueta cualquier excepción como `"Parse failed"`, aun si proviene del validador. | ⚪ | `Engine/DocumentEngine.cs#L65-L71` |
| T13 | `BitmapEscPosRenderer` declara `_baseRenderer = new EscPosRenderer()` y el docstring dice "delega al base", pero `Render` emite todo por sí mismo y **nunca** lo referencia. | ⚪ | `Renderers/BitmapEscPosRenderer.cs#L10-L17` vs `#L26-L127` |
| T14 | Min Android inconsistente entre paquetes: `MotorDsl.Maui` exige 25.0, `MotorDsl.Bluetooth` 24.0 (piso efectivo 25.0). | 🟡 | `MotorDsl.Maui.csproj#L12` vs `MotorDsl.Bluetooth.csproj#L11` |
| T15 | *Sync-over-async* en el diagnóstico: `SnapshotPermissions` resuelve `CheckStatusAsync().GetAwaiter().GetResult()` dentro de `Build`. | 🟡 | `Diagnostics/MauiDiagnosticsReportProvider.cs#L144-L153` |
| T16 | El parser materializa `style` **solo** en nodos `text`; en tablas el `style` del JSON se ignora (no verificado por otra vía). | 🟡 | `Parser/DslParser.cs#L168-L183` |
| T17 | El logo NV por `FS q` (clásico) **no tiene query limpia**: su `Success` es de confirmación limitada (verificar con impresión de prueba). | ⚪ | `MotorDsl.Bluetooth/BluetoothPrinterTransport.Nv.cs#L9-L18` |

---

## C. Adaptaciones declaradas de este pipeline documental

No son derivas del origen, sino decisiones de esta documentación (transparencia, Marco §5.3):

- La doc de pieza vive **espejada** en `pieces/<id>/` (no dentro de cada proyecto) porque el pipeline
  tiene **prohibido modificar el origen**. Lista para moverse al repo de cada pieza cuando un humano
  la apruebe.
- `test-suite` y `sample-app` son **tipos extendidos** (no están en el Marco §7.1); declarados en el
  [manifiesto](../../docs-manifest.yaml) y el [system-map](../00-overview/system-map.md).
- Se **omiten** carpetas del Marco §5.2 sin contenido reconstruible (`02-requirements`, `03-data`,
  `05-deployment`, `06-security-compliance`, `07-operations`); el detalle está en
  [`gap-documental.md`](../gap-documental.md).

---

## Recomendaciones (para decisión humana)

1. **Reconciliar el empaquetado NuGet** (D1, D3): alinear `cd-nuget.yml` con el script de 7
   paquetes y corregir los `paths` del workflow iOS, o el release quedará incompleto/roto.
2. **Registrar un ADR** sobre la pérdida de estilo en *classic* (T2) y el fallback silencioso del
   registry (T4): definir si son intencionales o bugs a corregir.
3. **Sanear la configuración de los samples** (D15): mover la IP del backend a configuración por
   entorno, no hardcodeada en el repo.
4. **Poner al día** `copilot-instructions.md` (D5) y el `CHANGELOG.md` histórico (D9).
5. **Fijar vigencia** de los documentos previos con versiones coexistentes (D17): marcar
   `superseded`/`vigente` en el frontmatter.

> Todas las entradas quedan en `status: draft` para revisión humana. Este reporte no prescribe
> cambios en el código: los propone.
