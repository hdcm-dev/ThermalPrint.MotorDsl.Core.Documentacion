# R5-web — Relevamiento de la parte web (GDA.Core / InspectoresApp.v2)

Fecha: 2026-11-17. Fase de sólo lectura: no se modificó código ni se hizo commit. Se ejecutó `git ls-remote` (lectura) y no `git fetch`.

## 1. Clones y tensión prompt vs memoria

| Afirmación | Evidencia |
|---|---|
| `Ng/Ng-Core/GDA/Issue699-GDA.Core` **no existe** en disco. | `cd .../GDA/Issue699-GDA.Core` → "No existe el fichero o el directorio"; `ls Ng/Ng-Core/GDA/` → `GDA.Core  GDA.Core.Documentacion  GDA.Core-i7infra-devcontainer`; `find Ng -maxdepth 4 -iname '*699*' -type d` → sin resultados. |
| Hay un único repo local `GDA/GDA.Core` con worktrees (`GDA.Core-i7infra-devcontainer` en `i7infra-devcontainer` d53bd23b; otro en scratchpad `wt-pf-c4` f48c3eda). | `git worktree list` |
| Remoto: `https://github.com/Notions-Group-SA/GDA.Core.git`. | `git remote -v` |
| Rama actual de `GDA/GDA.Core`: `fix08-blazor-web-compat-webview-postnet` (6970c6b3, 2026-11-12). | `git branch --show-current`; `git log -1` |
| `origin/HEAD -> origin/Homologacion`; existe además `origin/Issue-699-FF-Escenario-Homologacion` (2a17f245) y `master` (7a636609). | `git branch -a`; `git ls-remote --heads origin` |
| **Homologacion remota = c89f8588** (Merge PR #1022, 2026-11-17), coincide con el commit citado por el plan. La ref de seguimiento local `origin/Homologacion` ya está en c89f8588. | `git ls-remote` → `c89f85885b29... refs/heads/Homologacion`; `git rev-parse origin/Homologacion` |
| La rama local `Homologacion` está **atrasada**: 49a1427e (Merge PR #997, 2026-11-10). | `git rev-parse Homologacion` |

**Resolución:** el prompt (GDA/GDA.Core, rama Homologacion) es correcto en cuanto a repo; la "fuente Issue699" de la memoria corresponde hoy a la rama remota `Issue-699-FF-Escenario-Homologacion` del mismo remoto, no a un clon separado (el clon `Issue699-GDA.Core` no está en disco). La referencia al día es `origin/Homologacion` (c89f8588); la rama local `Homologacion` no lo está. Todas las lecturas de código de abajo se hicieron sobre `origin/Homologacion` vía `git show`/`git grep`. **Inferido:** el clon Issue699 fue eliminado o renombrado; la memoria quedó desactualizada.

## 2. ImpresoraTunnel.razor

Ruta: `GDA.Core.InspectoresApp.v2/Components/Pages/Impresora/ImpresoraTunnel.razor` (121 líneas; sin diferencias entre HEAD y origin/Homologacion; último commit que lo toca 421d90e9 "fix: Agregado proyecto v2").

- Es una página `@page "/ImpresoraTunnel"` (línea 1) **puramente estática**: CSS (3-82) y un mensaje de error (84-122).
- No tiene `@code`, no inyecta `IJSRuntime`, no usa `postMessage`, ni JS interop, ni esquema de URL propio.
- Texto: "No se pudo imprimir el acta" (99), "Confirmá que la impresora esté encendida y en línea" (109), "versión de la app sea la correcta" (113), "el acta quedó guardada y podés reimprimirla" (117). **No menciona Bluetooth** ni ofrece selección de impresora.
- **Inferido:** la página sólo se renderiza si la app nativa NO intercepta la navegación (navegador común o app sin soporte), de ahí que sea un mensaje de falla.

## 3. Cómo dialoga la web con la app nativa

Mecanismo: **navegación HTTP interceptada por el WebView** (no JS interop).

- `GDA.Core.InspectoresApp.v2/Services/PrintService.cs:33-44` (origin/Homologacion): lee el parámetro `GDA_CORE_Enpoint`, cifra el id con `NgCrypto`, arma `{baseUrl}/Print/{PrintActaById|PrintCausaById}?id=...` y navega a `ImpresoraTunnel?action=print&urlActionPrint={url codificada}` con `forceLoad: true` (41-43). Comentario 30-31: "la App MAUI intercepta ImpresoraTunnel, pide el JSON a la API ... y lo envía a la impresora térmica".
- Invocadores: `Components/Pages/Actas/ActaCreada.razor.cs:98` y `DetalleActa.razor.cs:89` (`_PrintService.PrintActa`); registro `Program.cs:81`.
- Lado app: `GDA.Core.APP/GDA.Core.APP/Services/UrlManagerService.cs:109-111` extrae `urlActionPrint`; `Services/PrintCoordinator.cs:53-62` lo consume (error `DocumentoInvalido` si falta). `Services/Printing/DTOs/PrintDocument.cs:7`: el JSON obtenido pasa a `MotorDsl.IDocumentEngine.Render`.
- El contrato web→app es **agnóstico del transporte**: sólo viaja la URL del documento. La elección Bluetooth/impresora vive en la app.

## 4. ¿Qué cambiar en la web para un transporte `pax`?

- **Nada obligatorio.** Ni `PrintService` ni `ImpresoraTunnel` asumen Bluetooth (evidencia §2 y §3; `git grep -i bluetooth` en `*.cs`/`*.razor` del proyecto sólo encuentra `logcat.txt`, no código).
- Opcional/**Inferido**: si se quisiera texto específico para POS integrado, la viñeta "impresora encendida y en línea" (línea 109) podría ajustarse; no es necesario para la feature.

## 5. Contexto: PosicionGps.cs (bug GPS)

- En origin/Homologacion vive en `Notions.Core.Services.GDI/Utils/PosicionGps.cs` (último commit b06a159f, 2026-11-17); en el worktree i7infra-devcontainer está en `GDA.Core.InspectoresApp.v2/Utils/PosicionGps.cs`.
- Lee el JSON `{"Latitude","Longitude"}` que la app MAUI inyecta en el input oculto `idInputCoordenada` (líneas 8-10); devuelve null ante vacío/"null"/JSON inválido/0,0 (24-55) para no cortar el circuito Blazor (comentario 12-13).
- Relación con PAX: **Inferido** — la app debe seguir inyectando la coordenada igual en el A910S; ajeno a la impresión.
