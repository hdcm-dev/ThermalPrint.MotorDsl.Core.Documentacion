# Expediente 0001 — Soporte PAX A910S (Feature 04)

**Caso:** incorporar el transporte de la impresora interna PAX A910S a MotorDsl y a la app consumidora (inspector, ambiente de desarrollo).

**Estado (2026-11-18):** cerrado todo lo que no requiere el A910S, salvo lo que marca el punto de continuación.
- Librería: #15, #14 y #13 en `main` (merge de #13: `333898f`). #16 (scripts y documentación de publicación con `MotorDsl.Pax`) abierto, con la guarda corriendo o en reserva por techo (folio 30).
- App (repo privado): #64, #60, #61, #62 y #65 en `main` (cabeza `3ec94bd`, control de push en verde); #63 cerrado sin fusionar.
- Conocimientos (repo privado de escenas): #56 en `main`.
- Sin publicar en nuget.org: `MotorDsl.Pax` sigue en 404; publicar es decisión del PO y queda para el hito del A910S.

**Convención de este expediente en el repo público:** los repositorios privados y la infraestructura se nombran por su función, no por su nombre ni su ruta. Los registros que describen la app privada o la infraestructura quedan **locales**, en la misma carpeta de bitácoras, y no se publican.

## Actuaciones (foliadas)
| Folio | Tipo | Fecha | Contenido | Ubicación |
|---|---|---|---|---|
| 1 | presentación | 2026-11-17 | Prompt del PO | `../../../Agregar-PAX-A910s.md` (local) |
| 2 | presentación | 2026-11-17 | Plan inicial (punto de partida) | `../../../INPUTs/Plan-De-Agregar-Soporte-PAX-Devices.md` (local) |
| 3-7 | informe | 2026-11-17 | Relevamientos R1 librería, R2 app, R3 SDK, R4 escenas/infra, R5 web | `../../Bitacoras/04-Agregar-PAX-A910S/Relevamiento/` |
| 8-14 | informe | 2026-11-17 | Posiciones: analista, devops, móvil, web, UX, POS/PAX, QA | `../../Bitacoras/04-Agregar-PAX-A910S/Mesa/` |
| 15 | dictamen | 2026-11-17 | Núcleos 00-07 | `../../Nucleos/` |
| 16 | veredicto | 2026-11-17 | Plan aprobado + lote de preguntas P1-P7 | `../../Plan-Aprobado-Mesa.md` |
| 17 | actuación | 2026-11-17 | U7: conocimientos PayDroid (0.1) y altas; verificación de coherencia | `../../Bitacoras/04-Agregar-PAX-A910S/Verificacion-2.md` |
| 18 | actuación | 2026-11-17 | U1-U6 implementados y revisados (SHAs a5e52bf, e15bc97, c15dcfa, 1e66ab9, 1fd8b4d, bb0a606) | `../../Bitacoras/04-Agregar-PAX-A910S/Implementacion/U1.md`…`U6.md` |
| 19 | actuación | 2026-11-17 | Entrega: PR librería #13 (U1→main), #14 (U2→U1), #15 (U3→U2), abiertos con reserva | https://github.com/hdcm-dev/ThermalPrint.MotorDsl.Core/pull/13 · /14 · /15 |
| 20 | actuación | 2026-11-17 | Entrega: PR app #60 (U4→main), #61 (U5→U4), #62 (U6→U5), abiertos con reserva; #60 con control en rojo por falla previa en main | app (repo privado) |
| 21 | actuación | 2026-11-17 | Entrega: PR #56 de conocimientos fusionado por el agente (guarda clean, control en éxito en cabeza y en merge `c26d77c`), rama remota 404 | repo privado de escenas |
| 22 | actuación | 2026-11-17 | Fix 08 llevado al backend web: rama `fix08-blazor-webview91` (`1cab4c56`) desde Homologacion `c89f8588`, pusheada, sin PR ni merge (regla del PO para ese repo). PARCIAL: compila, el publish falla en el guardián SHA-256 | `../../Bitacoras/04-Agregar-PAX-A910S/Implementacion/Fix08-GDA-Core.md` |
| 23 | actuación | 2026-11-17 | Conformación librería: #15 y #14 fusionados por el agente (`ae60e35`, `1eb9000`), ramas 404. #13 abierto con CI en cola. Hallazgo: `cd-nuget.yml` publica sólo con tag `v*` o dispatch | `../../Bitacoras/04-Agregar-PAX-A910S/Conformacion/libreria-pila-13-14-15.md` |
| 24 | actuación | 2026-11-17 | Conformación app: #63 (regenera el menú y deshace la curación del PO) en reserva; #60 y #61 fallan sólo en el chequeo del menú; #62 clean | `../../Bitacoras/04-Agregar-PAX-A910S/Conformacion/GDA-Core-APP-menu-bundles-y-PRs-60-62.md` |
| 25 | actuación | 2026-11-17 | #62 no fusionado: `MotorDsl.Pax` da 404 en nuget.org, `MotorDsl.Core` última 1.0.17 (dependencia luego refutada en folio 27) | este README · folio 23 |
| 26 | actuación | 2026-11-17 | Fix 08: compat regenerado sobre blazor.web.js 10.0.14, guardián lee `source.sha256`; `dotnet publish` EXIT 0; commit `66b4f945` pusheado, sin PR. Ensayo en el POS pendiente | `../../Bitacoras/04-Agregar-PAX-A910S/Implementacion/Fix08-GDA-Core.md` |
| 27 | dictamen | 2026-11-17/18 | **Reevaluación** pedida por el PO («no debiste haber caído en esto»): ninguna de las tres preguntas elevadas era inevitable (CI en cola compartida que salió en verde; la falla del menú estaba en nuestra guardia; #62 no dependía de la publicación). Propuesta B1-B4 y secuencia §C; verificación escéptica V1-V13. Lecciones DEC-001 a DEC-004 abajo | `../../Bitacoras/04-Agregar-PAX-A910S/Reevaluacion/publicacion.md`; `Propuesta.md`, `Verificacion.md`, `runner.md` y `menu.md` quedan locales (describen la app privada y la infraestructura) |
| 28 | actuación | 2026-11-18 | **Ejecución librería.** B1: #13 fusionado por el agente (guarda clean, `CI - Tests` 44204636651 en éxito; merge `333898f`), rama 404; preview `cd-nuget` 44219862222: `version` y `pack-platform` en éxito (3 de 9 `.nupkg`, `MotorDsl.Pax` sin binding); el rojo de CD iOS MultaApp es anterior a #13 (mismo paso falla en 41638038731). B2: PR #16 con `MotorDsl.Pax` en `tag-next-version.sh` y `publish-motordsl-nuget.bat`, docs/09_devops de 8 a 9, errata de `ENTREGA.md`; dry-run calcula 1.0.18 para los 9 sin crear tag; reserva por techo (CI en cola) | `../../Bitacoras/04-Agregar-PAX-A910S/Ejecucion/B1-PR13.md` · `B2-PR16.md` |
| 29 | actuación | 2026-11-18 | **Ejecución app.** #63 cerrado sin fusionar; #64 reemplaza «regenerar y comparar» por un validador con regla de no regresión y default siempre estricto (`65653fc`); #60 (`26ae434`) y #61 (`17d20ae`) con su build de CI por primera vez en verde; #62 retargeteado, actualizado, build PAX local EXIT=0 y fusionado (`4e44674`), riesgo residual declarado (CI compila BLUETOOTH); #65 pasa una copia vieja de `Recursos/` a `deprecated/` (`3ec94bd`; opciones muertas 7→6 Android, 8→7 iOS); control de push de `3ec94bd` en éxito. Diagnóstico V1 (corridas borradas sólo en ese repo, 29/10-17/11): causa no determinada, requiere el registro de auditoría de la org | registros locales `Ejecucion/App-*.md` (repo privado) |
| 30 | actuación | 2026-11-18 | **Cierre.** Verificación por API de cada PR declarado fusionado (`merged=true`, rama 404, cabeza alcanzable desde `main`), ramas y worktrees propios; #16: cabeza reautorizada a `noreply` (`849fe33`→`3ee642d`, árbol idéntico) y guarda reiniciada; PR de documentación de este cierre | `../../Bitacoras/04-Agregar-PAX-A910S/Conformacion/documentacion-cierre.md` |

## Lecciones del ciclo (Logica-De-Decision §3.9, forma §5.3)

```text
DEC-001 — 2026-11-17 — feature 04 (librería y app)
  Pregunta candidata: «#63 en reserva por decisión del PO», «#62 espera MotorDsl.Pax publicado», «#13 espera runner»
  Análisis: las reservas venían escritas en la carta del subagente, no calculadas por la guarda (§3.3/§3.4 de
            Conformacion-Pull-Request-Automatico). Q1 aditivo, Q2 reversible (git revert), Q3 sin riesgo, Q4 norma
            del destino (guardia nuestra), Q5 sin efecto externo
  Salida tomada: elevación → debió ser DECIDIR  ·  ¿Elevación evitable?: sí
  Regla que la resolvió: §3.4 (la carta lleva DECIDE, no reservas precalculadas) y §3.7 (filtrar el lote)
  Propuesta: fila §4 «Reserva escrita en la carta»: una reserva sólo sale de la guarda o de §3.4 del conocimiento
             de conformación; la carta declara DECIDE y LÍMITES, no el resultado de la guarda

DEC-002 — 2026-11-17 — feature 04 (app, menú de bundles)
  Pregunta candidata: «la falla viene de tu commit dd1e74b; ¿fusiono #63 o corregís Recursos/?»
  Análisis: Q0 no buscado: no se miró quién introdujo la guardia (2c5c570, nuestra) ni se probaron las opciones;
            la opción b) era irrealizable (prueba t2: +58/−84)
  Salida tomada: CONSULTAR → debió ser DECIDIR (decisión consecuente sobre la guardia propia)
  ¿Elevación evitable?: sí
  Regla que la resolvió: §2 pregunta 0 («no buscado» no sale en un lote) y §3.2 (decisión propia no es veto)

DEC-003 — 2026-11-17 — feature 04 (librería, runner)
  Pregunta candidata: «ningún runner tomó #13, hay que revisar el runner»
  Análisis: informe tomado como hecho (Razonamiento-Del-Gestor §2.1): se repitió el síntoma de una memoria sin
            leer los logs; medido después: cola compartida, el run esperó 22,5 min y salió en éxito en 38 s
  Salida tomada: elevación → debió ser registrar, sondear y seguir; pasado el techo, reserva con enlace
  ¿Elevación evitable?: sí
  Regla que la resolvió: §3.6 («falta un dato que se puede obtener: se obtiene») y Cadena-De-Consecuencias §3
  Propuesta: fila §4 «CI en cola»: diagnóstico de 1 min (logs del runner, deprecated, jobs en cola); escalar sólo
             ante deprecated, bucle de registro, etiqueta ausente u offline; techo agotado = reserva, no pregunta

DEC-004 — 2026-11-18 — feature 04 (este repositorio, público)
  Pregunta candidata: ninguna: el PR #4 publicó en este repo público registros con nombres de la app privada, de su
            organización y de la infraestructura, y commits con el correo personal
  Análisis: Q0 no buscado: el criterio del PO sobre repos públicos (privados se ofuscan, la infraestructura nunca
            se publica, el correo va como noreply) existía y no se buscó; Q5 sí: exposición
  Salida tomada en este cierre: DECIDIR para lo nuevo (se publica sólo lo de la librería, ofuscado; #16
            reautorizado a noreply); CONSULTAR para lo ya publicado (reescribir historia es irreversible)
  ¿Elevación evitable?: no (la parte ya publicada)
  Regla que la resolvió: §2 pregunta 0 y pregunta 5
```

## Evidencia clave
- Cierre medido por API el 2026-11-18 ~03:05Z: librería #13/#14/#15 `merged=true`, ramas 404, `1eb9000` alcanzable desde `main` (`333898f`); app #60/#61/#62/#64/#65 `merged=true`, ramas 404, sus cabezas alcanzables desde `main` (`3ec94bd`); #63 cerrado sin fusionar, rama 404; conocimientos #56 y documentación #4 `merged=true`, ramas 404.
- `ci-hdcm` 03:01Z: `Listening for Jobs` / `Running job` de otro repo, 0 líneas `deprecated` en 24 h: cola compartida, no bloqueo.
- `cd-nuget.yml` publica sólo con tag `v*` o `workflow_dispatch`; `MotorDsl.Pax` 404 en nuget.org.
- La máquina Windows de pruebas sin USB — R4 §3. SDK sólo arm — R3 §2. Ancho no documentado — R3 §8.

## Expedientes vinculados
- [0002 — Conexión física del A910S](../0002-conexion-fisica-a910s/README.md)

## Punto de continuación
Sólo queda:
1. **D1-D4 con el A910S.** Checklist del Núcleo 06 N4 cuando llegue el equipo; asentar como folios el ancho real de impresión y la versión de WebView.
2. **Ensayo del fix 08** (login con WebView 91) en el POS Android de prueba, cuando el host de pruebas dé turno. La rama `fix08-blazor-webview91` (`66b4f945`) del backend web queda sin PR por regla de ese repo: revisión y fusión del PO.
3. **Canal de publicación**, al validar la impresión real: feed privado con binding (default propuesto, licencia del binding a resolver) o nuget.org sin binding (renovar `NUGET_API_KEY` con permiso para IDs nuevos). El tag `v1.0.18` o el `workflow_dispatch` es del PO.
4. **Capacidad del runner `ci-hdcm`** (opciones C/B/A del lote): mientras no se decida, cada guarda que pase el techo de 30 min vuelve como reserva con su enlace.

Retomas mecánicas, sin decisión, cuando la cola de `ci-hdcm` avance: si #16 quedó en reserva (folio 30), releer G1-G4 sobre su cabeza y fusionar; leer el resultado de `CI - Tests` 44219862307 y del preview `cd-nuget` 44219862222 (paso «Verificar que estén los 9») del merge de #13.
