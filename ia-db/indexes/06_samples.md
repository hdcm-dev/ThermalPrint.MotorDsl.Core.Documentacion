# 06 — Samples

> **Propósito**: qué demuestra cada app de ejemplo, cuál mirar según lo que se busque y cómo
> correrlas.
> **Fuentes primarias**: `samples/` (5 proyectos + `Readme.md` + `notas-debug-android.md`),
> `scripts/local/`, `scripts/mobile/`, `scripts/local-devcontainer/`, `docs/11_examples/`.
> **Base**: contenido commiteado en `main` @ `0f8413d` (2026-09-24). Versión 3.0 de este índice
> (la anterior era sobre `e688f3c`). Sin SDK .NET en el host de indexado: nada de lo aquí dicho
> afirma que los samples compilen; las observaciones sobre `.csproj` son lectura estática.

---

## 1. Catálogo

| Sample | Qué demuestra | Formato DSL | Consumo de MotorDsl (real, en el `.csproj`) |
|---|---|---|---|
| `MotorDsl.SampleApp` | Demo mínimo: render a texto y a ESC/POS, **sin transport** | clásico | `ProjectReference` ×4 (Core, Parser, Rendering, Extensions) |
| `MotorDsl.MultaApp` | Acta de infracción completa con servicios MAUI locales; incluye acta de carga de 200 infracciones (§6) | clásico | `ProjectReference` ×4 |
| `MotorDsl.Integrated.MultaApp` | La misma acta con datos pre-resueltos | **integrado** | `PackageReference` ×7 `1.0.17` — ver §3.2 |
| `MotorDsl.Nuget.MultaApp` | Equivalente a MultaApp validando los paquetes publicados | clásico | `PackageReference` ×7 `1.0.*` |
| `MotorDsl.Nuget.Integrated.MultaApp` | Punto de partida recomendado: integrado + controles MAUI + Bluetooth | **integrado** | `PackageReference` ×7 `1.0.17` |

Fuentes: `samples/*/*.csproj`, `samples/Readme.md`.

Todos targetean `net10.0-android` y agregan `net10.0-ios` sólo si el build corre en Windows o
macOS (`<TargetFrameworks Condition="…IsOSPlatform('windows') or …('osx')">` en cada `.csproj`).
`SupportedOSPlatformVersion`: Android 25.0, iOS 15.0. `ApplicationId`: `com.motordsl.<sample>`.

---

## 2. Dos ejes que distinguen los samples

**Eje formato** — clásico (`{{placeholders}}` + `loop` + datos aparte) contra integrado (JSON ya
resuelto, sin etapa Evaluate; ver `02_dsl-y-modelos.md`). Comparar
`samples/MotorDsl.MultaApp/Templates/MultaDsl.cs` con
`samples/MotorDsl.Integrated.MultaApp/Templates/MultaIntegratedDsl.cs`: es la misma acta, y en el
integrado el loop de infracciones aparece expandido a mano en dos `container`.

**Eje consumo** — `ProjectReference` (compila contra `src/`) contra `PackageReference` (valida
que los paquetes publicados en nuget.org sirvan). Desde `0f8413d` el eje ya no coincide con el
nombre del sample: `Integrated.MultaApp` (sin «Nuget» en el nombre) consume paquetes (§3.2).

---

## 3. Cambios de consumo desde `e688f3c` y divergencias

### 3.1 `MotorDsl.Nuget.Integrated.MultaApp` volvió a NuGet

En la base anterior usaba `ProjectReference` a los 7 proyectos (repuntado temporal porque la API
de fase 4 no estaba publicada). Ahora el comentario del `.csproj` dice:

> *Vuelto a PackageReference en 1.0.16: la API de la fase 4 (ProvisionLogoAsync,
> CurrentCapabilities, PrintStrategySelector, role de imagen) ya esta publicada […] Este sample
> vuelve a cumplir su proposito: validar los paquetes PUBLICADOS.*

y fija los 7 paquetes en `Version="1.0.17"` (no `1.0.*`); el salto 1.0.16 → 1.0.17 vino en `01a4151`.
Fuente: `samples/MotorDsl.Nuget.Integrated.MultaApp/MotorDsl.Nuget.Integrated.MultaApp.csproj`.

### 3.2 `MotorDsl.Integrated.MultaApp`: pasó a paquetes y su `.csproj` quedó mal formado

- Antes: `ProjectReference` a 4 proyectos. Ahora (cambio hecho en `4b18745`, el commit del acta de carga): `PackageReference` a los 7 paquetes `1.0.17`
  (incluye `Printing.Abstractions`, `Bluetooth`, `Maui`, que su `MauiProgram.cs` no usa por DI).
- **Defecto observado (estático)**: el `ItemGroup` de esos `PackageReference` se cierra con
  `<ItemGroup>` en vez de `</ItemGroup>` (línea 96). Un parser XML falla con *mismatched tag* en la
  línea 105 (`</Project>`). Es de esperar que MSBuild rechace el proyecto hasta corregirlo; no se
  verificó con SDK. El mismo diff de `4b18745` reemplaza `</ItemGroup>` por `<ItemGroup>`.
  Fuente: `samples/MotorDsl.Integrated.MultaApp/MotorDsl.Integrated.MultaApp.csproj`.
- El sample conserva sus copias locales `Renderers/` y `Services/` (§4), ahora coexistiendo con
  los tipos equivalentes que trae el paquete `MotorDsl.Maui`.

### 3.3 `samples/Readme.md` desactualizado

| Afirma el Readme | Dice el código |
|---|---|
| `Integrated.MultaApp` consume por `ProjectReference` (Core, Parser, Rendering, Extensions) | `PackageReference` ×7 `1.0.17` |
| Ambos samples NuGet usan `Version="1.0.*"` | `Nuget.MultaApp` sí; `Nuget.Integrated.MultaApp` fija `1.0.17` |

En la base anterior la divergencia era la inversa (el Readme decía PackageReference y el código
tenía ProjectReference); hoy el Readme acierta en «sólo PackageReference» para los samples NuGet,
pero no en la versión ni en `Integrated.MultaApp`.

---

## 4. Cableado por DI de cada sample

| Sample | Extensiones que llama | Transport |
|---|---|---|
| `SampleApp` | `AddMotorDslEngine().AddTemplates().AddProfiles()` + `ThermalPrinterService` local | ninguno |
| `MultaApp` | `… .AddRenderer<PdfRenderer>().AddRenderer<BitmapEscPosRenderer>()` + `SkiaSharpRasterizer` local | servicio propio local |
| `Integrated.MultaApp` | ídem MultaApp | servicio propio local |
| `Nuget.MultaApp` | `… .AddMotorDslMaui()` | `AddBluetoothPrinterTransport()` |
| `Nuget.Integrated.MultaApp` | `… .AddMotorDslMaui()` + `IRenderer` = `EscPosRenderer(IBitmapRasterizer)` | `AddBluetoothPrinterTransport()` |

Fuentes: `samples/*/MauiProgram.cs`. En `Nuget.Integrated.MultaApp` el `EscPosRenderer` con
rasterizer pisa al `escpos` del core (el registry reemplaza por Target) para que las firmas
(`role=signature`) salgan inline `GS v 0` y el logo (`role=logo`) por recall NV — comentario en
`samples/MotorDsl.Nuget.Integrated.MultaApp/MauiProgram.cs`. Detalle de renderers: `03_renderizado-base.md`
y `05_maui-ui-renderers.md`; transports: `04_impresion-transports.md`.

Los samples `SampleApp`, `MultaApp` e `Integrated.MultaApp` **traen copias propias** de
`PdfRenderer`, `BitmapEscPosRenderer`, `SkiaSharpRasterizer` y/o `ThermalPrinterService`
(`Renderers/`, `Services/`), anteriores a que esos tipos vivieran en `MotorDsl.Maui`. **Para un
patrón de integración actual, copiar de los samples NuGet.**

---

## 5. Cuál mirar según lo que busques

| Busco… | Sample |
|---|---|
| El mínimo para renderizar algo | `MotorDsl.SampleApp` |
| Un documento realista con loop, QR, tabla, logo y firma | `MotorDsl.MultaApp` |
| Una prueba de carga (acta larga) sobre impresora real | `MotorDsl.MultaApp` → «Acta de 200 infracciones (carga)» |
| Cómo se ve un documento integrado | `MotorDsl.Integrated.MultaApp` |
| El patrón canónico (DI + controles MAUI + Bluetooth + logo NV) | `MotorDsl.Nuget.Integrated.MultaApp` |
| Verificar que los paquetes publicados funcionan | `MotorDsl.Nuget.MultaApp` (flotante `1.0.*`) / `Nuget.Integrated` (fijo `1.0.17`) |

---

## 6. Nuevo: acta de carga de 200 infracciones (`MultaApp`)

Commit `4b18745`. El `Picker` de `Pages/MainPage.xaml` suma la opción
«Acta de 200 infracciones (carga)»; `Pages/MainPage.xaml.cs` la asocia a `MultaDsl.Template` con
datos de `MultaDsl.GetCargaData(200)`.

`GetCargaData(int cantidad = 200)` (`samples/MotorDsl.MultaApp/Templates/MultaDsl.cs`) parte de
`GetSampleData()`, genera `cantidad` infracciones sintéticas (monto `1000*i`, `puntos` `i%5+1`) y
sobrescribe `nroActa = "CARGA-<n>"`, `infracciones` y `totalMonto`.

Su XML-doc declara mediciones hechas fuera de la impresora (citadas, no re-verificadas aquí):
200 infracciones rinden sin errores por `text` y `escpos`; 22 057 bytes ESC/POS; 87 bloques de
256 B en el troceado del transporte; 831 líneas de 32 columnas (≈2,8–3,5 m de rollo). Lo que queda
por ver en hardware: si la impresora aguanta los 87 bloques y si alcanza el papel. Relación con el
cambio de sondeo `DLE EOT` en Bluetooth: ver `04_impresion-transports.md`.

---

## 7. Cómo correrlos

| Carpeta | Plataforma | Qué hace |
|---|---|---|
| `scripts/local/` | Windows (`.bat`) | `run-<Sample>.bat` por cada uno, `run-All.bat`, `update-packages.bat` |
| `scripts/mobile/` | Windows (`.bat`) | `publish-<Sample>-apk.bat`, `publish-all.bat`, `update-packages.bat` |
| `scripts/local-devcontainer/` (**nuevo**, `347ebfb`) | Linux + Docker | `run-<Sample>.sh` por cada uno, `run-All.sh`, `update-packages.sh`, `limpiar.sh` |

`scripts/local-devcontainer/run-sample.sh <Sample> [--sin-instalar] [--rid <rid>] [--url <url>]`
compila el APK Release en un contenedor efímero (repo montado de sólo lectura), lo deja en
`scripts/local-devcontainer/OUTPUTs/<Sample>.apk` y, si hay teléfono, lo instala y lanza. `--url`
reescribe `backendBaseUrl` de `Resources/Raw/motordsl-config.json` sólo en la copia del contenedor.
Si otro contenedor ya tiene un `adb` con el USB tomado, instala a través de él
(`ADB_CONTENEDOR=<nombre>|ninguno` lo fuerza). Los `run-<Sample>.sh` son envoltorios de una línea.
Imagen, `lib.sh` e `interno/`: ver `08_build-devops.md` y `scripts/local-devcontainer/Readme.md`.

Equivalente directo (requiere .NET 10 SDK y workload `maui`):

```bash
dotnet build -t:Run -f net10.0-android \
  samples/MotorDsl.Nuget.Integrated.MultaApp/MotorDsl.Nuget.Integrated.MultaApp.csproj
```

Depuración en dispositivo Android real: `samples/notas-debug-android.md`.

---

## 8. Documentación narrativa de los ejemplos

`docs/11_examples/` (sin cambios en `e688f3c..0f8413d`):

| Archivo | Cubre |
|---|---|
| `README.md` | Índice de la carpeta |
| `ejemplo-01-simple.md` | El caso mínimo |
| `ejemplo-02-multa.md` | El acta de infracción |
| `ejemplo-03-multaapp-nuget.md` | Consumo vía NuGet |
| `ejemplo-03-multa-integrada.md` | Formato integrado |
| `imagenes_logos/` | Logos y firmas de prueba `.bmp`/`.base64` (binarios, no indexados) |

Inventario general de docs: `09_docs-existentes.md`.

---

## 9. Advertencias

- La advertencia de la base anterior (tres archivos de `MultaApp` sin commitear) quedó resuelta:
  esos cambios entraron en `4b18745` y se indexan en §6.
- El `.csproj` de `Integrated.MultaApp` está mal formado en `0f8413d` (§3.2).
- `samples/Readme.md` no refleja el estado de consumo actual (§3.3).
