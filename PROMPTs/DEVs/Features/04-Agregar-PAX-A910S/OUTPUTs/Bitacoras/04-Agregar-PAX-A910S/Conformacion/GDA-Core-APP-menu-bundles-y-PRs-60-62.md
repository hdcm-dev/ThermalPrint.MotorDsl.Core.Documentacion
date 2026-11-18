# Conformación en GDA.Core.APP: menú de bundles y PRs #60–#62 (2026-11-17)

Orden del PO (2026-11-17): «conforma los prs usando este conocimiento …/Knowledge-Conformacion-Pull-Request-Automatico.md / arregla los conflictos / si, segui».
Delegación encontrada: `README.md` de la raíz de GDA.Core.APP, fila «Delegación 2026-10-28 (Notions-Group-SA/GDA.Core.APP)», con decisión de Fernando Filipuzzi (PO), techo de 30 min e intervalo de 30 s. Credencial: `fernandofilipuzzi-utn`, con `permissions.push` en true. El token se pasó por archivo 0600 (`curl -K`) y por `GIT_ASKPASS`, nunca en argv. Los archivos se borraron al terminar.

## Unidad: fix/menu-bundles-regenerado → PR #63
- Worktree `/vm/wt/gda-app-menu-bundles`, creado desde `origin/main` `d6b63f3`. Commit `b35673ac`.
- `bash ci/generar-menu-bundles.sh` deja +56/−84 en `cd-main-android-build.yml` y `cd-main-ios-build.yml`, siempre entre los marcadores del menú. La lógica de los workflows no cambia.
- **No es un reformateo.** Revierte la curación a mano de `dd1e74b` («correccion listado de apps», fernandofilipuzzi-utn, 2026-11-16). Salen `com.movilparkingesperanza` (dos tríos: Esperanza y Concepción, regla D1), `com.gda.esperanza.funcionario`, `com.gda.zarate.funcionario`, `com.gda.corehomol.*`, `com.gda.homol.ciudadano` y `com.bd.coredesa.ciudadano`. Entran las opciones que declara `Recursos/`.
- **Reserva (§3.4, una decisión que no le corresponde al agente).** El agente no lo fusiona; el merge vuelve al PO. CI: corrida 44204403852 en curso al cierre de este registro.
- https://github.com/Notions-Group-SA/GDA.Core.APP/pull/63

## PR #60 (U4)
- La rama está al día con `main` (0 commits atrás). La corrida 44201383447 sobre `1e66ab9a` falla sólo en «CHEQUEO. Menú de bundles…».
- **Reserva (falla que ya viene de main).** Comentario con la evidencia: https://github.com/Notions-Group-SA/GDA.Core.APP/pull/60#issuecomment-6964693460. No se fusionó.

## PR #61 (U5)
- Retargeteado a `main` con PATCH base, y cerrado y reabierto para disparar CI. Estaba al día con `main` y sin conflictos.
- La corrida 44204475929 sobre `1fd8b4dd` falla en el mismo chequeo. **Reserva (falla que ya viene de main).** Comentario: https://github.com/Notions-Group-SA/GDA.Core.APP/pull/61#issuecomment-6964775096. No se fusionó.

## PR #62 (U6)
- La base es `feature/04-impresora-por-trio` y la rama está al día (0 atrás de `main` y de su base); `mergeable_state` es clean. No se fusiona: depende de que MotorDsl.Pax esté publicado. Queda listo para retargetear a `main` después de #61.

## Qué falta (PO)
Decidir #63: fusionarlo tal cual, o corregir `Recursos/` para que el generador produzca el menú curado. Después, actualizar #60 y #61 con main y conformarlos.
