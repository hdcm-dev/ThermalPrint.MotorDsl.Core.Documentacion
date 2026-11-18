# Bitácora — Feature 04, fase 1 (relevamiento, mesa y plan)

Fecha: 2026-11-17. Fase sólo lectura: sin cambios de código, git ni infraestructura; nada instalado.

## Qué se hizo
1. Relevamiento en 5 líneas → `Relevamiento/R1-libreria.md` … `R5-web.md`.
2. Mesa con 7 especialistas → `Mesa/informe-*.md`.
3. Integración del presidente: contradicciones resueltas (paquetes, TFM, target, selección de transporte, runner de pack, fuente de `<app-web>`) → `../../Nucleos/00-Cohesion-Global.md`.
4. Núcleos 01-07 → `../../Nucleos/`.
5. Plan aprobado + lote P1-P7 → `../../Plan-Aprobado-Mesa.md`.
6. Expedientes 0001 (caso) y 0002 (conexión física) → `../../Expedientes/`.

## Estado
Fase 1 cerrada. Bloqueos: ninguno para U1-U7 salvo defaults del lote. D1-D4 esperan el equipo.

## Hallazgos para memoria
- El clon `Issue699-<app-web>` ya no existe (R5 §1): la memoria "Issue699 única fuente" está desactualizada.
- Ningún manifiesto del inspector declara permisos Bluetooth (R2 §8).
- Ortografía del prompt: pendiente de revisión pedida por el PO (no se modificó el archivo en esta fase).

## Qué sigue
U1 en la librería desde `main` (0f8413d) en `feature/04-pax-transporte`; luego U2, U3, U4… según `Plan-Aprobado-Mesa.md`.

# Fase 2 — Entrega (2026-11-17)

Conformación según `IA/IA.Knowledge.Base/Knowledges/Knowledge-Conformacion-Pull-Request-Automatico.md` 2.0. Credencial `fernandofilipuzzi-utn` por `git credential fill` (push por GIT_ASKPASS desde el entorno, nunca en argv); `permissions.push=true` en los tres repos.

| Unidad | PR | Base | Estado | Reserva |
|---|---|---|---|---|
| U1 | hdcm-dev/ThermalPrint.MotorDsl.Core#13 | main | abierto, cabeza 1eb9000 (pila colapsada) | guarda no pasa: CI run 44204636651 en cola sin runner `ci-hdcm`, `unstable`. Corrección: el merge a main NO publica; `cd-nuget.yml` publica sólo con tag `v*` o dispatch |
| U2 | #14 | feature/04-pax-transporte | **fusionado por el agente**, merge 1eb9000 | — (licencia: el paquete público sale con `-p:PaxNeptune=false`); rama remota 404 |
| U3 | #15 | feature/04-pax-binding | **fusionado por el agente**, merge ae60e35 (cabeza 0b86cbe, trae e15bc97) | apartamiento G3 declarado: 0 corridas (ci.yml sólo en PR a main), pruebas locales 364/364; rama remota 404 |
| U4 | `<org>/<app>#60` | main | abierto, reserva | `Verificar PR - Android` en rojo (menú de bundles); la falla está en `origin/main` d6b63f3 (generar-menu-bundles.sh deja +56/−84 en cd-main-*). Comentario con evidencia en el PR |
| U5 | #61 | main (retargeteado) | abierto, reserva | run 44204475929 falla sólo en el chequeo del menú de bundles (falla previa de main); regresión BT en g42 sin medir (CA-03.1) |
| U6 | #62 | feature/04-impresora-por-trio | abierto, clean | MotorDsl.Pax no publicado (nuget.org 404), sin A910S (D1/D2) + apilado |
| U7 | `<org>/<repo>#56` | main | **fusionado por el agente**, merge c26d77c | — (guarda clean, Verificar 1/1 en éxito; controles del merge 1/1 en éxito; rama remota 404; worktree retirado; main local al día) |
| — | `<org>/<app>#63` | main | abierto, reserva | regenera el menú de bundles y deshace la edición a mano dd1e74b: qué apps se compilan lo decide el PO |
| Fix 08 | `<app-web>` `fix08-blazor-webview91` | — | rama 66b4f945, sin PR | publish en verde; ensayo Pay-Android pendiente |
| Docs | hdcm-dev/ThermalPrint.MotorDsl.Core.Documentacion (`docs/04-pax-a910s`) | main | ver `Conformacion/documentacion.md` | — |

Registros de la conformación: `Conformacion/libreria-pila-13-14-15.md`, `Conformacion/App-menu-bundles-y-PRs-60-62.md`, `Conformacion/documentacion.md`.

Pendiente con dispositivo: D1-D4 (Núcleo 06 N4).
