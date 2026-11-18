# Plan aprobado por la mesa — Feature 04: soporte PAX A910S

Fecha: 2026-11-17 · Estado: **aprobado por la mesa, pendiente de respuestas del PO (lote abajo)** · Fase 1 sólo lectura: no se tocó código, git ni infraestructura.
Mesa: analista de sistemas, devops, diseñador móvil, diseñador web, UX/flujo/UI, POS/PAX, QA; presidente integrador. Informes en `Bitacoras/04-Agregar-PAX-A910S/Mesa/`, relevamientos R1-R5 en `.../Relevamiento/`. Detalle por eje en `Nucleos/` (cohesión: `Nucleos/00-Cohesion-Global.md`).

## Decisiones firmes
1. **Vía bitmap (a):** PNG de `RasterPreviewRenderer` (`raster-preview`) por el `WriteBytesAsync` existente; firma PNG validada, otra cosa → `Protocol`; `print(Bitmap, IPinterListener)` + `getStatus()` previo. Sin cambios de contrato. (Núcleo 01)
2. **Estructura:** un proyecto/paquete nuevo `src/MotorDsl.Pax` (`net10.0-android`) con el binding NeptuneLite 4.15.00 embebido (jar + `.so` arm64-v8a/armeabi-v7a + Metadata.xml + ProGuard). Abstracción `IPaxPrinterDevice` con `NeptunePaxPrinterDevice` y `SimulatedPaxPrinterDevice`; la lógica pura se enlaza como fuente en `MotorDsl.Tests`. 9 paquetes. Plan B con timebox: binding aparte o wrapper Java mínimo.
3. **Nombre/Kind:** `PaxPrinterTransport`, `Kind = "pax"`, `AddPaxPrinterTransport(o => …)` con `AddSingleton`.
4. **Errores:** dos tablas separadas (getStatus/onError vs EPrintDevException); LOAD DAL ERR / 99 / 101 / 103 / UnsatisfiedLinkError → `Connection`; estados de hardware → `PrinterHardwareException` con enum de causa aditivo en MotorDsl.Core.
5. **Perfil PAX parametrizable:** `PaxProfiles.A910S(widthPx = 384)` → `DeviceProfile("pax_a910s", 32, "raster-preview")`; 384 px **provisional (Inferido)** hasta medirlo; `PrinterProfile.PaxA910S`.
6. **Impresora simulada:** `PaxPrinterOptions.Mode = Real|Simulated`; vuelca el PNG exacto al ancho del perfil y simula 0/1/2/8/9/-2, LOAD DAL ERR y 99.
7. **App:** rama base **`main`** (única remota, `git ls-remote --heads origin` → d6b63f3; no hay Issue699 en la app). Transporte y perfil por **interruptor de trío** `-p:Impresora=BLUETOOTH|PAX` (patrón `Refresco`, `WhiteLabel.props:101`), default BLUETOOTH; se quita el 58HB6 fijo (`PrintCoordinator.cs:90-93`); `IPrinterService` con `PrinterReadiness` y `Kind`; overlay genérico sin vista nueva; códigos `PRN-HW-HEAT/BUSY/BATT`, `PRN-PAX-SVC`; textos BT neutralizados; permisos BT en manifiestos; APK sólo ARM para el A910S con `extractNativeLibs="true"` (Verificacion-3 H3).
8. **Web:** **no se toca GDA.Core** ni `ImpresoraTunnel` (contrato agnóstico, R5 §3-4). Base de referencia `origin/Homologacion` c89f8588; el clon Issue699-GDA.Core no existe (R5 §1). El fix 08 (6970c6b3) es dependencia previa externa, fuera de esta feature.
9. **Conexión física:** inicial adb remoto por la PC del PO (sin cambio de infra). **Cambio de infra requerido, no aplicado:** regla udev `51-android-pax.rules` en hpdev con el idVendor del A910S (requiere OK del PO). `windows-i7infra` **descartado** (sin USB; sostiene el IIS de ~10 escenas). SDT sólo en Windows físico si falta NeptuneService.
10. **CI:** `Pax` en `pack-platform` (macos-15), conteo 8→9, lista de push; CHANGELOG `[Unreleased]`.

## Orden de implementación (unidades / PR)
| U | Repo | Rama propuesta | Alcance | Requiere equipo |
|---|---|---|---|---|
| U1 | Librería `Libs/NugetOrg/PrintThermal_Motor_Maui` (base `main` 0f8413d) | `feature/04-pax-transporte` | `MotorDsl.Pax` sin binding real: `IPaxPrinterDevice`, transporte, mapeo, simulador, perfil, DI, enum de causa en Core; tests N1 | No |
| U2 | Librería | `feature/04-pax-binding` (sobre U1) | Binding NeptuneLite + `NeptunePaxPrinterDevice`, ProGuard, `.so`, carga diferida; build en `scripts/local-devcontainer/` | No |
| U3 | Librería | `feature/04-pax-ci` | `cd-nuget.yml` (9 paquetes, macos-15), CHANGELOG, sample opcional | No |
| U4 | App `GDA.Core.APP` (base `main` d6b63f3) | `fix/permisos-bluetooth-inspector` | T7 permisos BT coredesa/msm | No |
| U5 | App | `feature/04-impresora-por-trio` | T8+T9: perfiles registrados, interruptor `Impresora`, `PrinterReadiness`, `BluetoothPrinterService`, overlay y catálogo | No |
| U6 | App | `feature/04-pax-a910s` (sobre U5, con paquete de U1-U3) | `PaxPrinterService`, registro `AddPaxPrinterTransport`, permiso PRINTER, APK sólo ARM, modo simulado; prueba en Pay-Android | No |
| U7 | `Ng/Ng-IA/Ng.IA-Context.Scene` | `feature/pax-a910s-conocimientos` (desde origin/main 4bb39c4; commit 5e468dc, sin push ni PR) | T11/T12: Knowledge-Test-…-App-PayDroid.md 0.1, refs en App-Android/TEST-inspector/Recursos/Index. **Pay-Android no se toca** (su 1.0.2: L3 no cita L4; el índice es la puerta) | No |
| D1-D4 | — | — | Checklist `Nucleos/06` N4: relevar equipo (WebView, ancho, NeptuneService), acta real, completar Knowledge-Test PayDroid con la primera corrida (el borrador 0.1 ya existe, U7), firma Leandro | **Sí** |

Cada PR: build + `dotnet test` en verde, conformación automática. GDA.Core: sin cambios.

## Checklist del equipo (resumen; detalle Núcleo 06)
adb/API/ABI · **versión WebView (≥94 mínimo, ≥119 a salvo)** · NeptuneService · GMS/GPS · ancho real por ticket de calibración · acta real vs PNG simulado · estados reales · permiso PRINTER · Release ProGuard + firma PAX (whitelist 103).

## Preguntas al PO (lote único)
| # | Pregunta | SI NO RESPONDÉS |
|---|---|---|
| P1 | ¿Autorizás la regla udev para el vendor PAX en hpdev? | Uso adb remoto por tu PC (patrón g42) y no toco hpdev. |
| P2 | ¿Aceptás 9 paquetes con el binding dentro de `MotorDsl.Pax`? | Sigo con 9; si el binding no compila embebido, paso a paquete aparte (10) y te aviso. |
| P3 | ¿El A910S usa el trío `com.gdi.coredesa.inspector` con el interruptor `Impresora=PAX`, o un trío/bundle nuevo? | Mismo trío con interruptor, APK sólo ARM aparte del aab. |
| P4 | ¿Se lleva el fix 08 (6970c6b3) a Homologacion? Si la WebView del A910S es <94, ¿es bloqueante de la feature? | No toco GDA.Core; la feature 04 se cierra en impresión y el fix 08 queda como riesgo abierto registrado. |
| P5 | ¿Tiempo y canal de firma con Leandro; bundle a firmar (coredesa o msm)? | D4 queda en checklist sin cerrar; candidato con `com.gdi.coredesa.inspector`. |
| P6 | ¿El modo simulado puede ir en builds de desarrollo (emulador/g42) o sólo Debug? | Builds de desarrollo con `-p:PaxModo=SIMULADO`, nunca Release de tienda. |
| P7 | Texto si falta NeptuneService: ¿"Avisá a soporte" o hay procedimiento? | "Avisá a soporte" sólo con botón Cerrar. |
