# 06 — Samples

> **Propósito**: qué demuestra cada app de ejemplo, cuál mirar según lo que se busque y cómo
> correrlas.
> **Fuentes primarias**: `samples/` (5 proyectos + `Readme.md` + `notas-debug-android.md`),
> `scripts/local/`, `scripts/mobile/`, `docs/11_examples/`.

---

## 1. Catálogo

| Sample | Qué demuestra | Formato DSL | Consumo declarado |
|---|---|---|---|
| `MotorDsl.SampleApp` | Demo mínimo: render a texto y a ESC/POS, **sin transport** | clásico | `ProjectReference` |
| `MotorDsl.MultaApp` | Acta de infracción completa con servicios MAUI locales | clásico | `ProjectReference` |
| `MotorDsl.Integrated.MultaApp` | La misma acta con datos pre-resueltos | **integrado** | `ProjectReference` |
| `MotorDsl.Nuget.MultaApp` | Equivalente a MultaApp validando los paquetes publicados | clásico | `PackageReference 1.0.*` |
| `MotorDsl.Nuget.Integrated.MultaApp` | Punto de partida recomendado: integrado + controles MAUI | **integrado** | ver §3 |

Todos targetean `net10.0-android`, y agregan `net10.0-ios` condicionalmente cuando el build corre
en Windows o macOS. `ApplicationId`: `com.motordsl.<sample>`.

---

## 2. Dos ejes que distinguen los samples

**Eje formato** — clásico (`{{placeholders}}` + `loop` + datos aparte) contra integrado (JSON ya
resuelto, sin etapa Evaluate). Comparar
`samples/MotorDsl.MultaApp/Templates/MultaDsl.cs` con
`samples/MotorDsl.Integrated.MultaApp/Templates/MultaIntegratedDsl.cs`: es el mismo acta, y en el
integrado el loop de infracciones aparece expandido a mano en dos `container`.

**Eje consumo** — `ProjectReference` (compila contra el código local) contra `PackageReference`
(valida que los paquetes publicados en nuget.org realmente sirvan). Los samples «Nuget» existen
justamente para detectar que un paquete quedó incompleto.

---

## 3. Divergencia real: `MotorDsl.Nuget.Integrated.MultaApp`

`samples/Readme.md` afirma que los **dos** samples NuGet referencian los 7 paquetes exclusivamente
por `<PackageReference>`. En el código, `MotorDsl.Nuget.Integrated.MultaApp.csproj` usa
`<ProjectReference>` a los siete proyectos locales, con este comentario:

> *ProjectReferences locales: la fase 4 usa API aun no publicada (`ProvisionLogoAsync`,
> `CurrentCapabilities`, `PrintStrategySelector`, `role` de imagen). Repuntado desde los
> PackageReference NuGet 1.0.\* para compilar contra el codigo local de las 4 fases.
> Volver a NuGet cuando se republiquen los paquetes.*

Es un estado transitorio conocido y documentado en el propio archivo, no un error: la API de logos
NV y capacidades es posterior a `1.0.13`. `MotorDsl.Nuget.MultaApp` sí conserva sus
`PackageReference 1.0.*`.

---

## 4. Cableado por DI de cada sample

| Sample | Extensiones que llama | Transport |
|---|---|---|
| `SampleApp` | `AddMotorDslEngine().AddTemplates().AddProfiles()` | ninguno |
| `MultaApp` | `… .AddRenderer<PdfRenderer>().AddRenderer<BitmapEscPosRenderer>()` | servicio propio local |
| `Integrated.MultaApp` | ídem MultaApp | servicio propio local |
| `Nuget.MultaApp` | `… .AddMotorDslMaui()` | `AddBluetoothPrinterTransport()` |
| `Nuget.Integrated.MultaApp` | `… .AddMotorDslMaui()` | `AddBluetoothPrinterTransport()` |

Diferencia que importa al copiar código: los tres samples con `ProjectReference` **traen copias
propias** de `PdfRenderer`, `BitmapEscPosRenderer` y de un `ThermalPrinterService` en sus carpetas
`Renderers/` y `Services/` —son anteriores a que esos tipos vivieran en `MotorDsl.Maui`—. Los dos
samples NuGet no: usan los del paquete. **Para un patrón de integración actual, copiar de los
samples NuGet, no de los otros tres.**

---

## 5. Cuál mirar según lo que busques

| Busco… | Sample |
|---|---|
| El mínimo para renderizar algo | `MotorDsl.SampleApp` |
| Un documento realista con loop, QR, tabla, logo y firma | `MotorDsl.MultaApp` |
| Cómo se ve un documento integrado | `MotorDsl.Integrated.MultaApp` |
| El patrón canónico de integración (DI + controles MAUI + Bluetooth) | `MotorDsl.Nuget.Integrated.MultaApp` |
| Verificar que los paquetes publicados funcionan | `MotorDsl.Nuget.MultaApp` |

---

## 6. Cómo correrlos

Scripts `.bat` (pensados para Windows):

| Carpeta | Qué hace |
|---|---|
| `scripts/local/` | `run-<Sample>.bat` por cada uno, `run-All.bat`, `update-packages.bat` |
| `scripts/mobile/` | `publish-<Sample>-apk.bat` por cada uno, `publish-all.bat` |

Equivalente multiplataforma por línea de comandos:

```bash
dotnet build -t:Run -f net10.0-android \
  samples/MotorDsl.Nuget.Integrated.MultaApp/MotorDsl.Nuget.Integrated.MultaApp.csproj
```

Requiere .NET 10 SDK y el workload `maui`. Notas de depuración sobre dispositivo Android real:
`samples/notas-debug-android.md`. Detalle de los scripts: `scripts/local/Readme.md` y
`scripts/mobile/Readme.md`.

---

## 7. Documentación narrativa de los ejemplos

`docs/11_examples/` acompaña a los samples con recorridos paso a paso:

| Archivo | Cubre |
|---|---|
| `ejemplo-01-simple.md` | El caso mínimo |
| `ejemplo-02-multa.md` | El acta de infracción |
| `ejemplo-03-multaapp-nuget.md` | Consumo vía NuGet |
| `ejemplo-03-multa-integrada.md` | Formato integrado |
| `imagenes_logos/` | Logos y firmas de prueba en `.bmp` y `.base64` (excluidos de este índice por binarios) |

---

## 8. Advertencia sobre el estado del árbol

Al generar esta base, `samples/MotorDsl.MultaApp/` tenía tres archivos modificados sin commitear
(`Pages/MainPage.xaml`, `Pages/MainPage.xaml.cs`, `Templates/MultaDsl.cs`). **Lo indexado aquí es
el contenido commiteado en `e688f3c`**; esos cambios locales no se leyeron. Antes de razonar sobre
la UI o la plantilla de ese sample, verificar el estado del árbol de trabajo.
