# Conformación de la pila #13/#14/#15 de hdcm-dev/ThermalPrint.MotorDsl.Core (2026-11-17)

Orden del PO (2026-11-17): «conforma los prs usando este conocimiento … / arregla los conflictos / si, segui».
Conocimiento: `IA/IA.Knowledge.Base/Knowledges/Knowledge-Conformacion-Pull-Request-Automatico.md` 2.0.
Credencial `fernandofilipuzzi-utn` por `git credential fill`; git por `GIT_ASKPASS` leyendo archivo 0600, curl por `-K` archivo 0600; nunca en argv. `permissions.push=true`.

## Delegación (§3.1)

No estaba asentada en el repo de la librería (sí en `PrintThermal_Motor_Maui.Documentacion/ENTREGA.md`). Se asentó en `ENTREGA.md` de la librería (commit `0b86cbe`, dentro de #15): fecha 2026-10-25 / reiterada 2026-11-17, decidió Fernando Filipuzzi (PO), techo 30 min, intervalo 20 s, G3 = `CI - Tests`.

## Pasos

| # | Qué | Evidencia |
|---|---|---|
| 1 | `feature/04-pax-ci` actualizada con `feature/04-pax-binding` (trae `e15bc97`) | merge `10d456a`, **sin conflictos** (sólo `NeptunePaxPrinterDevice.cs`); `git merge-tree` contra `origin/main` sin conflictos |
| 2 | `ENTREGA.md` con la delegación | `0b86cbe` |
| 3 | Build + tests locales sobre `0b86cbe` | dotnet 10.0.403, `MotorDsl.Tests` 364/364 en éxito |
| 4 | #15 → `feature/04-pax-binding` | informe pre-merge https://github.com/hdcm-dev/ThermalPrint.MotorDsl.Core/pull/15#issuecomment-6964699204 · guarda: open, head=`0b86cbe`, mergeable=true, clean, runs=0 · **fusionado por el agente**, merge `ae60e35` · rama `feature/04-pax-ci` 404 |
| 5 | #14 → `feature/04-pax-transporte` | informe https://github.com/hdcm-dev/ThermalPrint.MotorDsl.Core/pull/14#issuecomment-6964707810 · head=`ae60e35` (árbol idéntico a `0b86cbe`), clean, runs=0 · **fusionado por el agente**, merge `1eb9000` · rama `feature/04-pax-binding` 404 |
| 6 | Local | worktrees `{raíz-de-worktrees}/PrintThermal-pax-u2` y `-u3` retirados, ramas locales borradas; `0b86cbe` y `e15bc97` alcanzables desde `origin/feature/04-pax-transporte` |
| 7 | #13 → `main` | cabeza `1eb9000`; CI `CI - Tests` run 44204636651 (`pull_request`) **en cola**: job pide `[self-hosted, ci-hdcm]` y ningún runner lo tomó en ~4 min; `mergeable_state=unstable` mientras tanto. **No fusionado** |

**Apartamiento declarado de G3 en #15 y #14:** el conocimiento pide al menos una corrida para la cabeza («ninguna: reserva»). `ci.yml` sólo corre en `pull_request` a `main`; por instrucción del pedido, G3 de esas bases intermedias se apoyó en los tests locales registrados y en la CI de #13, que es la que entra a `main`. Ese merge no tocó `main` (efecto acotado a ramas de la pila).

## Publicación — hallazgo

`cd-nuget.yml` corre con push a `main`, pero el paso `Publish to NuGet.org` tiene `if: startsWith(github.ref, 'refs/tags/v') || github.event_name == 'workflow_dispatch'`. En push a `main` la versión es `0.0.0-preview.<run_number>` y **sólo se suben artefactos**: el merge de #13 **no publica** en nuget.org. Evidencia: run 46 (9a6c229, éxito) no dejó ninguna preview en `motordsl.core` (índice termina en 1.0.17, 0 previews). `motordsl.pax` hoy no existe en nuget.org (BlobNotFound). Publicar requiere tag `v*` o dispatch con versión: no delegado. Próxima versión libre si se etiqueta: cualquiera > 1.0.17 (p. ej. `v1.0.18`).
