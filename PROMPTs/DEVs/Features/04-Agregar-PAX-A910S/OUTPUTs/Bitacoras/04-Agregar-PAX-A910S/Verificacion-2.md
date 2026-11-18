# Verificación 2 — coherencia (núcleos, plan, expedientes, conocimientos U7)

Fecha: 2026-11-17 · Lente: contradicciones y reglas del prompt · Sólo documentos de OUTPUTs; sin código, git ni infraestructura.

## Hallazgos confirmados y corregidos
| # | Hallazgo | Evidencia | Acción |
|---|---|---|---|
| H1 | El plan (U7) y el Núcleo 05 §5 mandaban agregar una referencia en `…-Pay-Android.md`. La escena no se tocó, y está bien que no se toque, por la regla de la propia escena. | `Knowledge-SCENE-hpdev-com.gdi.coredesa.inspector-Pay-Android.md:350` (1.0.2: «L3 no cita L4; el índice es la puerta») | Se corrigieron `Plan-Aprobado-Mesa.md` (fila U7) y `Nucleos/05` §5 |
| H2 | La rama de U7 en el plan (`docs/04-knowledge-paydroid`) no coincidía con la rama real. | worktree `/vm/wt/Ng.IA-Context.Scene-pax`: `git log --oneline -2` → `5e468dc` sobre `4bb39c4` (rama `feature/pax-a910s-conocimientos`) | Se corrigió la fila U7 del plan: rama real, commit 5e468dc, sin push ni PR |
| H3 | D3 («Knowledge-Test PayDroid») figuraba como tarea que necesita el equipo. El conocimiento ya existe como borrador 0.1 creado sin el equipo. Lo que necesita el equipo es completarlo con la primera corrida. | `Index-Knowledge.md:191` (Borrador, sin corrida) | Se reformuló D3 en el plan y en `Nucleos/00` |
| H4 | El expediente 0001 decía «Implementación no iniciada» y no registraba U7. | ídem H2 | Se ajustó el estado y se agregó el folio 17 |

## Confirmaciones (no se pudo refutar)
- **App:** sólo existe la rama `main`. `git ls-remote --heads origin` devuelve `d6b63f39… refs/heads/main`.
- **Librería:** `main` y `origin/main` están en `0f8413d`.
- **Clon `Issue699-GDA.Core`:** **no existe**. `ls -d Ng/Ng-Core/GDA/*` → `GDA.Core`, `GDA.Core.Documentacion`, `GDA.Core-i7infra-devcontainer`. El texto de la tarea que dice «existe también» es falso. El plan y R5 tienen razón.
- **`windows-i7infra` sin USB:** `docker-compose.yml:18-20` sólo declara `/dev/kvm` y `/dev/net/tun`.
- **Reglas udev:** sólo están `51-android-motorola.rules` y `60-vboxdrv.rules`. La regla PAX no se aplicó, como corresponde, porque falta la autorización del PO.
- **`cd-nuget.yml`:** `pack-platform` corre en `runs-on: macos-15`, instala `ios android maui-android`, comprueba que haya 8 paquetes y lista el push sin Pax. Coincide con el Núcleo 07.
- **`MotorDsl.Tests.csproj`:** enlaza fuentes de Bluetooth (`Chunking.cs` y `Capabilities.cs`), que es el precedente que cita el Núcleo 01.
- **Acceso adb del g42:** `Knowledge-SCENE-Recursos.md:354` → `adb -H 100.66.63.98 -P 5037 -s ZY32GSJ88S`.
- **Reglas del prompt:**
  - GDA.Core queda sin cambios (N04, CA-04.1).
  - Cada repo trabaja en su rama, con PR (tabla U1-U7).
  - El cambio de infraestructura no se aplica sin el OK del PO (P1).
  - Los puntos D1-D4 quedan como checklist sin cerrar: los 7 puntos de D1 en el conocimiento están PENDIENTE, y CA6-CA8 requieren el equipo.
- **Umbrales de la WebView:** «≥94 mínimo» y «≥119 a salvo» coinciden entre el plan, el Núcleo 06 y el conocimiento PayDroid (`:105`).

## Dudoso, sin corregir (fuera de OUTPUTs)
- **D-1:** `Knowledge-Test-…-App-PayDroid.md:123` dice, como **Inferido**, que «el APK sólo ARM no instala en x86_64». Eso choca con R4 §2.2 (`R4-escenas-infra.md:40-43`): `abilist=x86_64,arm64-v8a` con `libndk_translation`. Según R4, también por inferencia, un binario arm64 se ejecutaría por traducción. Además, el prompt describe el emulador como «x86_64 con traducción ARM». Lo más probable es que un APK arm64 sí instale; uno armeabi-v7a solo, no, porque `abilist32` está vacío. Hay que medirlo con `adb install` del APK ARM en `pay-a12-wv91`. El conocimiento está en otro repo (5e468dc), así que no se toca acá: queda para quien mantiene U7.
- **D-2:** el Núcleo 03 §5 y el conocimiento proponen usar el modo simulado en `pay-a12-wv91`. El ingreso del inspector falla con WebView 91 sin el fix 08 (`SCN-PAY` §5). **Inferido**: desde la UI web el overlay de impresión no se alcanzaría en ese emulador. El conocimiento ya marca como PENDIENTE (U6) cómo se dispara el overlay.
