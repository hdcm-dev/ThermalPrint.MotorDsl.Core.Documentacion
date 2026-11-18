# 00 — Cohesión global de la feature 04 (PAX A910S)

## Núcleos
| # | Núcleo | Repo |
|---|---|---|
| 01 | [Binding, transporte `pax`, vía bitmap](01-Transporte-Binding-Via-Bitmap.md) | Librería |
| 02 | [Perfil PAX e impresora simulada](02-Perfil-E-Impresora-Simulada.md) | Librería |
| 03 | [App inspector](03-App-Inspector.md) | GDA.Core.APP |
| 04 | [Web GDA.Core](04-Web-GDA-Core.md) | GDA.Core (sin cambios) |
| 05 | [Conexión física, escenas, conocimientos](05-Infra-Conexion-Fisica-Y-Escenas.md) | Ng.IA-Context.Scene / hpdev |
| 06 | [QA y checklist del equipo](06-QA-Y-Checklist-Equipo.md) | transversal |
| 07 | [CI, NuGet, entrega](07-CI-NuGet-Entrega.md) | Librería |

## Dependencias
```
N01 ──► N02 ──► N07 (paquete) ──► N03 (app consume NuGet) ──► N06 N3 (emulador)
 │                                   ▲
 └──── causa enum (MotorDsl.Core) ───┘ (PrinterErrorCatalog de la app)
N04 (fix08, externo) ──► N06 D3 (inspector web en el equipo)
N05 (vía adb) ──► N06 N4 (D1..D4)
```
Contratos entre núcleos: Kind `"pax"`; target `raster-preview` + `bitmap_max_width_px`; `PaxPrinterOptions.Mode`; enum de causa de `PrinterHardwareException`; interruptor `-p:Impresora=PAX`.

## Contradicciones resueltas en la integración
| Tema | Posiciones | Resolución |
|---|---|---|
| Nº de paquetes | pos-pax: Binding aparte (10); analista/devops: 1 (9) | 9, binding embebido; plan B Binding aparte |
| TFM | analista: net10.0+android; devops: sólo android | sólo android + fuentes enlazadas en tests (precedente `MotorDsl.Tests.csproj:31-32`) |
| Target | pos-pax: `raster-pax`; resto: `raster-preview` | `raster-preview` |
| Selección de transporte | ux: runtime; resto: por trío | por trío (lo exige el prompt) vía interruptor de build |
| Runner de pack | plan T6: Linux | macos-15 `pack-platform` |
| Fuente GDA.Core | memoria: Issue699; prompt: Homologacion | Homologacion; clon Issue699 inexistente |

## Trazabilidad T/D → núcleos
| Tarea | Núcleo | Unidad (Plan) |
|---|---|---|
| T1 binding | 01 | U2 |
| T2 transporte + mapeo | 01 | U1 |
| T3 vía bitmap | 01 | U1 |
| T4 perfil | 02 | U1 |
| T5 tests fake | 01, 02, 06 | U1, U2 |
| T6 cd-nuget + CHANGELOG | 07 | U3 |
| T7 permisos BT | 03 | U4 |
| T8 transporte/perfil por trío | 03 | U5 |
| T9 IPrinterService + overlay | 03 | U5 |
| T10 x86 | 01, 03 | U6 |
| T11 conocimientos | 05 | U7 |
| T12 conexión física | 05 | U7 / Exp. 0002 |
| D1 relevar equipo | 05, 06 | D-fase |
| D2 acta real | 01, 06 | D-fase |
| D3 completar Knowledge-Test PayDroid con la corrida real (borrador 0.1 creado en U7) | 05, 06 | D-fase |
| D4 firma Leandro | 06, 07 | D-fase |
