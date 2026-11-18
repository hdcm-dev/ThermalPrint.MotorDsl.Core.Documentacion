# Núcleo 04 — Web GDA.Core (InspectoresApp.v2, ImpresoraTunnel)

Trazabilidad: ninguna tarea T del plan; riesgo WebView (fix 08). Depende de: nada. Afecta a: N05, N06 (D3).

## Decisión
1. **No se toca la web por la feature 04.** El contrato web→app es una URL interceptada (`PrintService.cs:33-44` en origin/Homologacion → `ImpresoraTunnel?action=print&urlActionPrint=…`; app `UrlManagerService.cs:107-116,229`), agnóstico del transporte. `ImpresoraTunnel.razor` es estático y no menciona Bluetooth (R5 §2-4).
2. **Repo/rama:** `Ng/Ng-Core/GDA/GDA.Core`, base `origin/Homologacion` = c89f8588 (`git ls-remote`, R5 §1). El clon `Issue699-GDA.Core` **no existe** en disco (R5 §1); la memoria está desactualizada (lo vigente es la rama remota `Issue-699-FF-Escenario-Homologacion` del mismo remoto). La `Homologacion` local está atrasada (49a1427e): `pull --ff-only` antes de cualquier commit.
3. **Dependencia previa externa:** el fix 08 (6970c6b3, rama `fix08-blazor-web-compat-webview-postnet`, no contenida en Homologacion: `git branch -r --contains 6970c6b3`) es necesario para que el inspector cargue con WebView < 94/119. Se trata **fuera** de la feature 04 y su integración requiere decisión del PO (regla del repo: sólo commit y push desde Homologacion).

## Alternativas descartadas
Texto de ImpresoraTunnel para POS (cosmético, opcional); devolver resultado al portal (fuera de alcance, R2 §2.4); actualizar WebView del equipo (la 155 no instala en API 31, `SCN-PAY:212-213`).

## Tareas
Sin dispositivo: validar fix08 en Pay-Android (el 2026-11-12 se ensayó el mecanismo con un `blazor.web.js` bajado a sintaxis Chrome 91 y polyfill de `Promise.withResolvers`, servido por el proxy de la escena: `SCN-PAY:318-320`; no es el equipo real; cita corregida en Verificación 1). Con dispositivo: medir WebView real (N06).

## Criterios de aceptación
CA-04.1 ningún cambio en GDA.Core en la feature 04. CA-04.2 decisión del PO sobre fix08 registrada en expediente 0001.

## Evidencia
../Bitacoras/04-Agregar-PAX-A910S/Relevamiento/R5-web.md · ../Bitacoras/04-Agregar-PAX-A910S/Mesa/informe-web-designer.md · ../Bitacoras/04-Agregar-PAX-A910S/Relevamiento/R4-escenas-infra.md §2
