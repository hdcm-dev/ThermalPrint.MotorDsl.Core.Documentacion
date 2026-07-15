---
doc_id: ONB-SETUP-001
doc_type: developer-setup
title: Puesta a punto del desarrollador — MotorDsl
version: 1.0.0
status: draft
origin: reverse-engineered
confidence: high
owner: equipo-motordsl
last_review: 2026-07-14
audience: [dev, agentes-automaticos]
classification: uso-interno
source_ref: v1.0.13 @83677eb
---

# Puesta a punto del desarrollador — MotorDsl

## Resumen ejecutivo

Cómo levantar el entorno para **compilar el motor, correr los tests y ejecutar un sample** en
Android. Dos audiencias: quien va a **consumir** las librerías (le basta con NuGet) y quien va a
**contribuir** al motor (clona y compila la solución). Los detalles de build/CI/publicación están en
[`ia-db/indexes/08_build-devops.md`](../../../ia-db/indexes/08_build-devops.md).

## Prerrequisitos

| Herramienta | Versión | Para qué |
|---|---|---|
| .NET SDK | **10** (CI usa 10.0.102) | Compilar y testear |
| Workload `maui` | `dotnet workload install maui` | Compilar `MotorDsl.Maui` y los samples |
| Android SDK | API 25+ (piso efectivo de la app) | Correr samples en Android |
| Java | 17 (CI android) | Publicar APK |

> El piso efectivo de Android es **25.0**: `MotorDsl.Maui` exige 25.0 aunque `MotorDsl.Bluetooth`
> exija 24.0 (ver [platform-notes](../../pieces/MotorDsl.Bluetooth/platform-notes.md)).

## Camino A — Consumir las librerías (integrador)

```xml
<ItemGroup>
  <PackageReference Include="MotorDsl.Maui"      Version="<latest>" />
  <PackageReference Include="MotorDsl.Bluetooth" Version="<latest>" />
</ItemGroup>
```

`MotorDsl.Maui` arrastra `MotorDsl.Core`, `MotorDsl.Rendering`, `MotorDsl.Extensions` y
`MotorDsl.Printing.Abstractions` como dependencias transitivas. Sigue con la
[guía de uso MAUI](../../pieces/MotorDsl.Maui/usage-guide.md) y los
[snippets de integración](../../pieces/samples/integration-snippets.md).

## Camino B — Contribuir al motor

```bash
# 1. Compilar el núcleo (net10.0 puro, sin Android)
dotnet build src/MotorDsl.Core/MotorDsl.Core.csproj -c Debug

# 2. Compilar la capa MAUI
dotnet build src/MotorDsl.Maui/MotorDsl.Maui.csproj -c Debug

# 3. Correr los tests (net10.0, sin emulador)
dotnet test src/MotorDsl.Tests/MotorDsl.Tests.csproj -c Release
```

La solución es `PrintThermalDriver.slnx`. La suite de tests (xUnit) ejercita el motor completo sin
hardware; incluso las partes puras del transport Bluetooth se testean por enlace de fuente (ver
[`ia-db 07`](../../../ia-db/indexes/07_tests.md)).

### Correr un sample en Android

```bash
# Vía script (recomendado)
scripts/local/run-MotorDsl.Nuget.Integrated.MultaApp.bat

# O directo
dotnet build -t:Run -f net10.0-android \
  samples/MotorDsl.Nuget.Integrated.MultaApp/MotorDsl.Nuget.Integrated.MultaApp.csproj
```

El sample canónico recomendado es **`MotorDsl.Nuget.Integrated.MultaApp`** (formato *integrated* +
controles MAUI). Ver [samples](../../pieces/samples/README.md).

> **Nota (deriva).** Ese sample hoy usa `ProjectReference` temporal a los 7 proyectos —no los
> paquetes NuGet— porque usa API de la "fase 4" (logo NV) aún no publicada. Ver
> [reporte-derivas](../04-decisions/reporte-derivas.md).

## Empaquetado y publicación (mantenedores)

- La versión **no** vive en los `.csproj`: se inyecta en build/pack (`-p:PackageVersion` /
  `-p:MotorDslVersion`). Los 7 paquetes se publican con **versión unificada**.
- Empaquetado local: `scripts/nuget/build-motordsl-nuget.bat`; publicación:
  `scripts/nuget/publish-motordsl-nuget.bat`.
- Para probar paquetes recién empacados, `NuGet.config` declara la fuente local `./nupkg` antes de
  nuget.org (ver GLOSSARY: *local-nupkg*).

Detalle completo (CI, CD, versionado): [`ia-db 08`](../../../ia-db/indexes/08_build-devops.md).

## Verificación de que el entorno quedó bien

- [ ] `dotnet build src/MotorDsl.Core/MotorDsl.Core.csproj` compila sin errores.
- [ ] `dotnet test src/MotorDsl.Tests/MotorDsl.Tests.csproj` corre y pasa.
- [ ] Un sample arranca en un dispositivo/emulador Android API 25+.

## Preguntas guía

- ¿Necesito Android para trabajar en el núcleo? → No: `Core`/`Parser`/`Rendering`/`Extensions`/
  `Printing.Abstractions` y los tests son net10.0 puro.
- ¿Por qué mi APK no instala con `adb install`? → Falta `EmbedAssembliesIntoApk` (ver GLOSSARY).
