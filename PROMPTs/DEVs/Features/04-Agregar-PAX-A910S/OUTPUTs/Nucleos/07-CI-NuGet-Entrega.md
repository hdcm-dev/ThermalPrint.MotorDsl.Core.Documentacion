# Núcleo 07 — CI, NuGet y entrega

Trazabilidad: T6, D4. Depende de: N01.

## Decisión
1. `.github/workflows/cd-nuget.yml`: agregar `Pax` al job **`pack-platform` (macos-15, :108)**, que ya instala `android maui-android` (:124) — **no** al runner Linux `i7infra-dev` (el plan decía "runner Linux"; no está verificado que tenga workload android y agregarla es cambio de infra, R1 §7). Subir el conteo exacto de 8 a 9 (:183-186), agregar `MotorDsl.Pax` al final de la lista de push (:193), actualizar comentarios (:3, :26-27).
2. `CHANGELOG.md` `[Unreleased]` (:11): "Added: MotorDsl.Pax (transporte pax para PAX A910S, simulador)" y la propiedad de causa en `PrinterHardwareException`. Versión por `-p:PackageVersion` (:5-9); próxima **Inferido** 1.1.0 (feature aditiva, SemVer).
3. La app consume NuGet de nuget.org, no ProjectReference (`GDA.Core.APP.csproj:212-220`). Para probar la app antes del release: feed local `./nupkg` (`NuGet.config:5` de la librería) en el devcontainer, o preview `0.0.0-preview.N` del push a main (`cd-nuget.yml:38-45`). Versión unificada de todos los MotorDsl en la app.
4. Entrega a Leandro (D4): APK sólo ARM, un candidato por iteración, bundle definitivo (whitelist 103).

## Riesgo
La publicación queda atada a macOS: si `pack-platform` falla no sale ningún paquete (ya ocurre hoy con Bluetooth/Maui).

## Criterios
CA-07.1 workflow empaqueta 9 y publica. CA-07.2 CHANGELOG actualizado. CA-07.3 la app restaura la versión nueva.

## Evidencia
../Bitacoras/04-Agregar-PAX-A910S/Relevamiento/R1-libreria.md §7 · ../Bitacoras/04-Agregar-PAX-A910S/Mesa/informe-devops.md · ../Bitacoras/04-Agregar-PAX-A910S/Relevamiento/R2-app.md §11
