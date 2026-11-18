# Expediente 0001 — Soporte PAX A910S (Feature 04)

**Caso:** incorporar el transporte de la impresora interna PAX A910S a MotorDsl y a la app `com.gdi.coredesa.inspector`.
**Estado:** fase 2 en conformación (2026-11-17). U7 fusionado (Ng.IA-Context.Scene #56, c26d77c). Librería: #15 y #14 fusionados por el agente (ae60e35, 1eb9000); #13 abierto, CI run 44204636651 en cola sin runner `ci-hdcm`. Publicar en nuget.org exige tag `v*` o dispatch (decisión del PO); MotorDsl.Pax no existe en nuget.org. App: nada fusionado, #63 (menú de bundles) en reserva por decisión del PO; #60/#61/#62 en reserva. Fix 08: publish en verde (66b4f945), ensayo en Pay-Android pendiente. D1-D4 pendientes del equipo.

## Actuaciones (foliadas)
| Folio | Tipo | Fecha | Contenido | Ubicación |
|---|---|---|---|---|
| 1 | presentación | 2026-11-17 | Prompt del PO | `../../../Agregar-PAX-A910s.md` |
| 2 | presentación | 2026-11-17 | Plan inicial (punto de partida) | `../../../INPUTs/Plan-De-Agregar-Soporte-PAX-Devices.md` |
| 3-7 | informe | 2026-11-17 | Relevamientos R1 librería, R2 app, R3 SDK, R4 escenas/infra, R5 web | `../../Bitacoras/04-Agregar-PAX-A910S/Relevamiento/` |
| 8-14 | informe | 2026-11-17 | Posiciones: analista, devops, móvil, web, UX, POS/PAX, QA | `../../Bitacoras/04-Agregar-PAX-A910S/Mesa/` |
| 15 | dictamen | 2026-11-17 | Núcleos 00-07 | `../../Nucleos/` |
| 17 | actuación | 2026-11-17 | U7: conocimientos PayDroid (0.1) y altas; verificación de coherencia | `/vm/wt/Ng.IA-Context.Scene-pax` 5e468dc · `../../Bitacoras/04-Agregar-PAX-A910S/Verificacion-2.md` |
| 16 | veredicto | 2026-11-17 | Plan aprobado + lote de preguntas P1-P7 | `../../Plan-Aprobado-Mesa.md` |
| 18 | actuación | 2026-11-17 | U1-U6 implementados y revisados (SHAs a5e52bf, e15bc97, c15dcfa, 1e66ab9, 1fd8b4d, bb0a606) | `../../Bitacoras/04-Agregar-PAX-A910S/Implementacion/U1.md`…`U6.md` |
| 19 | actuación | 2026-11-17 | Entrega: PR librería #13 (U1→main), #14 (U2→U1), #15 (U3→U2), abiertos con reserva | https://github.com/hdcm-dev/ThermalPrint.MotorDsl.Core/pull/13 · /14 · /15 |
| 20 | actuación | 2026-11-17 | Entrega: PR app #60 (U4→main), #61 (U5→U4), #62 (U6→U5), abiertos con reserva; #60 con control en rojo por falla previa en main (comentario con evidencia) | https://github.com/Notions-Group-SA/GDA.Core.APP/pull/60 · /61 · /62 |
| 21 | actuación | 2026-11-17 | Entrega: PR #56 de conocimientos fusionado por el agente (guarda clean, Verificar en éxito en cabeza y en merge c26d77c), rama remota 404, worktree retirado | https://github.com/Notions-Group-SA/Ng.IA-Context.Scene/pull/56 |
| 22 | actuación | 2026-11-17 | Fix 08 llevado a GDA.Core: rama `fix08-blazor-webview91` (1cab4c56) desde origin/Homologacion c89f8588, pusheada, sin PR ni merge (aprobación del PO). Verificada: el merge-base coincide, ls-remote coincide, la API de PR da vacío y el diff es el de 6970c6b3. PARCIAL: compila, pero el publish falla en el guardián SHA-256 (runtime 10.0.14); falta regenerar el compat y ensayar en Pay-Android. Worktree retirado | Bitacoras/04-Agregar-PAX-A910S/Implementacion/Fix08-GDA-Core.md |
| 23 | actuación | 2026-11-17 | Conformación librería: #15 fusionado por el agente en feature/04-pax-binding (merge ae60e35, cabeza 0b86cbe), #14 en feature/04-pax-transporte (merge 1eb9000); ramas remotas 404. #13 abierto: CI 44204636651 en cola (runner ci-hdcm), `unstable`. Hallazgo: `cd-nuget.yml` publica sólo con tag `v*` o dispatch | `../../Bitacoras/04-Agregar-PAX-A910S/Conformacion/libreria-pila-13-14-15.md` |
| 24 | actuación | 2026-11-17 | Conformación app: PR #63 (`fix/menu-bundles-regenerado`, b35673ac) regenera el menú y deshace dd1e74b → reserva (decisión del PO); #60 y #61 (retargeteado a main) fallan sólo en el chequeo del menú → reserva con comentario; #62 clean, espera MotorDsl.Pax | `../../Bitacoras/04-Agregar-PAX-A910S/Conformacion/GDA-Core-APP-menu-bundles-y-PRs-60-62.md` |
| 25 | actuación | 2026-11-17 | U6/#62 no fusionado: motordsl.pax da 404 en nuget.org, motordsl.core última 1.0.17 | este README · folio 23 |
| 26 | actuación | 2026-11-17 | Fix 08: compat regenerado sobre blazor.web.js 10.0.14 (sha256 703fca8e…), guardián lee `source.sha256`; `dotnet publish` EXIT 0; commit 66b4f945 pusheado a `fix08-blazor-webview91`, sin PR. Ensayo Pay-Android pendiente (sin turno por carga de hpdev) | `../../Bitacoras/04-Agregar-PAX-A910S/Implementacion/Fix08-GDA-Core.md` |

## Evidencia clave
- App sólo tiene `main` (`git ls-remote --heads origin` → d6b63f3) — R2 §1.
- Clon Issue699-GDA.Core inexistente; `origin/Homologacion` = c89f8588 — R5 §1.
- `windows-i7infra` sin USB — R4 §3. SDK sólo arm — R3 §2. Ancho no documentado — R3 §8.
- `cd-nuget.yml:183-186` exige 8 paquetes — R1 §7.

## Expedientes vinculados
- [0002 — Conexión física del A910S](../0002-conexion-fisica-a910s/README.md)

## Punto de continuación
1. Librería: conformar #13 en main cuando el run 44204636651 termine en verde y el PR esté `clean` (cabeza auditada 1eb9000); si sigue en cola, revisar el runner `ci-hdcm` de hdcm-dev. Después: controles del merge, borrar `feature/04-pax-transporte`.
2. PO: publicar MotorDsl.* en nuget.org con tag `v1.0.18` (o superior) o `workflow_dispatch` (el paquete público sale con `-p:PaxNeptune=false`).
3. PO: decidir #63 (fusionar tal cual o corregir `Recursos/` y regenerar); luego conformar #60 y #61.
4. #62: con MotorDsl.Pax publicado y #61 fusionado, pasar a la versión publicada, retargetear a main y conformar.
5. Fix 08: ensayo del login en Pay-Android (WebView 91) cuando hpdev dé turno; aprobación del PO para PR.
6. Al llegar el equipo: checklist Núcleo 06 N4 (D1-D4); asentar ancho real y versión de WebView como folios.
