# Fix 08 llevado a GDA.Core desde Homologacion (2026-11-17)

Mandato: respuesta del PO 2026-11-17 (`OUTPUTs/Respuestas-PO-2026-11-17.md`): rama nacida de Homologacion, **sin PR ni merge** (requiere aprobación del PO).

## Qué es 6970c6b3
- Repo `Notions-Group-SA/GDA.Core`, rama `origin/fix08-blazor-web-compat-webview-postnet` (única que lo contiene: `git branch -r --contains 6970c6b3`). Base de esa rama: b39f0a79 (no Homologacion).
- Es un cambio **de GDA.Core** (no del proxy de la escena): un target MSBuild `AfterTargets=Publish` (`GDA.Core.InspectoresApp.v2/build/blazor-web-compat/BlazorWebCompat.targets`, importado desde el csproj) que reemplaza el `wwwroot/_framework/blazor.web.js` publicado por `blazor.web.compat.js` (mismo script con `static{}` bajados por esbuild `--target=chrome91 --supported:class-static-blocks=false` + polyfill de `Promise.withResolvers`). Guardián por SHA-256 del script del framework (`source.sha256`). Más README, `regenerate.sh`, `downlevel.mjs`, manual técnico y nota de skill.

## Rama nueva
- Rama `fix08-blazor-webview91` (convención del repo: `fix08-…`), worktree `/vm/wt/GDA.Core-fix08-wv91`.
- Base `origin/Homologacion` = c89f8588 (tras `git fetch`).
- `git cherry-pick 6970c6b3` → un conflicto sólo en `docs/manuales_tecnicos/indice.md` (filas nuevas de Homologacion vs. la fila del fix 08); resuelto conservando todas las filas. Resto aplicado tal cual.
- Commit **1cab4c56d38cf62f0a68526f9320fc928d2d5583**, push a `https://github.com/Notions-Group-SA/GDA.Core/tree/fix08-blazor-webview91`. Sin PR, sin merge.

## Compilación (host, SDK 10.0.403, ya instalado)
`dotnet publish GDA.Core.InspectoresApp.v2 -c Release -o /vm/wt/pub-fix08-wv91` → **falla el guardián** (comportamiento diseñado):
```
fix08/BlazorWebCompat: el blazor.web.js del framework (sha 973BC6E6…D8FF) NO coincide con el esperado (88ba6b99…36e5). Probablemente cambió .NET.
```
El `blazor.web.js` del framework en esta máquina proviene de `microsoft.aspnetcore.app.internal.assets/10.0.14` (sha 973bc6e6…; es el único en la caché NuGet). El compat versionado se generó contra otro script (sha 88ba6b99…), de una versión de runtime que no está en esta máquina. **El compat commiteado está desincronizado con el runtime actual**: publicar con `-p:SkipBlazorWebCompatGuard=true` serviría un script de otra versión del framework (no seguro).

## Verificación de sintaxis del regenerado (sólo evidencia, NO commiteado)
En contenedor `node:22` (nada instalado en el host), con la receta de `downlevel.mjs` y esbuild 0.24.0 sobre el script 10.0.14:
- original: 1 bloque `static{`; regenerado: 0; polyfill `Promise.withResolvers` presente.
- Otros operadores en el regenerado: `??=` (3), `||=` (1) — soportados desde Chromium 85, válidos en 91.
- `source.sha256` resultante: 973bc6e6…d8ff (coincide con el del build).

## Bloqueo / pendiente
No se commiteó el compat regenerado porque el README del fix exige **reensayar el login en WebView vieja** (escena Pay-Android, bitácora 10 del fix 08) antes de darlo por bueno, y ese ensayo no se hizo hoy. Próximo paso: correr `regenerate.sh` con el script 10.0.14, ensayar en la escena Pay-Android (WebView 91.0.4472.114) y commitear `blazor.web.compat.js` + `source.sha256` en esta misma rama. Hasta entonces la rama **no publica** (falla por guardián, lo cual es seguro: no sirve un script desalineado).

## Nota de procedimiento
El push tomó la credencial de `fernandofilipuzzi-utn` con `git credential fill`; no se imprimió ni se listó `~/.git-credentials`, pero el secreto pasó a git por un helper inline `-c credential.helper=…` (argv del proceso git durante el push). Para la próxima: usar un helper vía archivo/fd en lugar de `-c`.

## Verificación escéptica (2026-11-17)
Resultado confirmado, sin correcciones a la rama:
- `git merge-base HEAD origin/Homologacion` = `origin/Homologacion` = c89f8588 (tras `git fetch`).
- `git ls-remote origin fix08-blazor-webview91` → 1cab4c56; worktree limpio, al día con el remoto.
- API `GET pulls?head=Notions-Group-SA:fix08-blazor-webview91&state=all` (autenticada, token por archivo `-K`, borrado al terminar) → lista vacía: sin PR.
- Diff contra Homologacion: los mismos 10 archivos que 6970c6b3, con contenido idéntico salvo dos. En el csproj, contra Homologacion solo se agrega el `<Import>`; la diferencia con 6970c6b3 es la ProjectReference a Components.v2, que ya estaba en Homologacion. En indice.md se agrega la fila y se quita una línea en blanco, con lo que la fila queda dentro de la tabla.
- Compila: el log `pub.log` muestra `GDA.Core.InspectoresApp.v2.dll` en Release y el publish a `/vm/wt/pub-fix08-wv91/`; luego el guardián corta con EXIT 1 (sha 973BC6E6… ≠ 88ba6b99…). El bloqueo es real y sigue pendiente del ensayo en Pay-Android.

## Regeneración del compat y publish en verde (2026-11-17, 21:00–21:12 -03)
- Worktree recreado en `/vm/wt/GDA.Core-fix08-wv91` (ya no existía; `git worktree prune` + `add`), sobre `fix08-blazor-webview91` en 1cab4c56.
- **Regeneración:** `downlevel.mjs` de la rama, corrido en un contenedor `node:22` (`fix08-regen-wv91`, `--rm`) con esbuild 0.24.0. Nada se instaló en el host. La entrada fue `~/.nuget/packages/microsoft.aspnetcore.app.internal.assets/10.0.14/_framework/blazor.web.js`, con sha256 `973bc6e65078e2ccaab81619021c10a4bd90409170582553f7822bfa3671d8ff`. Equivale a `regenerate.sh`: el script sólo ubica el origen y llama a `downlevel.mjs`, y en el host no hay node. La única diferencia es que la ruta de `source.sha256` se pasó absoluta dentro del contenedor.
  - Resultado: `blazor.web.compat.js` con sha256 `703fca8e0ac7741f51194614f19764ed4298a7b3ff31fa1b3488de438b400767` y `source.sha256` = `973bc6e6…d8ff`.
- **Sintaxis** (contenedor `fix08-sint-wv91`, con acorn 8.12.1 y esbuild 0.24.0):
  - 0 coincidencias de `static\s*{` y 1 polyfill `Promise.withResolvers=function`.
  - acorn parsea con ES2022 y encuentra 0 `StaticBlock`.
  - El retransform con esbuild `target=chrome91` y `class-static-blocks=false` no da errores (199915 → 199704 bytes, es sólo reimpresión).
  - Operadores lógicos de asignación: `??=` ×3 y `||=` ×1. Chromium los soporta desde la 85.
- **Defecto encontrado y corregido:** el guardián tenía el sha esperado fijo en `BlazorWebCompat.targets` (`88ba6b99…`), aunque el README §3 dice que se lee de `source.sha256`. Por eso regenerar no alcanzaba: el publish seguía dando EXIT 1, como mostró `/vm/wt/pub-fix08-wv91.log` en la primera corrida. Ahora el target lee el sha con `ReadLinesFromFile` desde `source.sha256` y falla si ese archivo falta o está vacío.
- **Publish:** `dotnet publish GDA.Core.InspectoresApp.v2 -c Release -o /vm/wt/pub-fix08-wv91` terminó con **EXIT 0**. El log dice `fix08/BlazorWebCompat: blazor.web.js reemplazado por la copia compatible con WebView 91 (PAX A910S).`, y el `wwwroot/_framework/blazor.web.js` publicado tiene sha256 `703fca8e…0767`, idéntico al compat.
- **Ensayo en Pay-Android: PENDIENTE.** No había reserva ajena (`/vm/agentes/escenas-hpdev/reservas/` vacío), pero el gestor no dio turno. `recurso.sh ocupacion` a las 21:07 y a las 21:09 respondió: `admite otro emulador: NO (carga alta: 17.53 / 15.09 en 1 min con 8 núcleos (tope 1.5×))`. La carga venía de builds de CI ajenas (java de Android, VBCSCompiler, cdd.py). No se forzó el turno, no se tocó el proxy `inspector-coredesa-gda` y no se levantó el emulador. Por eso no hay capturas del ensayo en `Images/`. Según la orden, el regenerado se commiteó porque el publish pasó, y el ensayo quedó marcado PENDIENTE en el README §6 del fix.
  - Para correrlo: con carga baja, seguir `Knowledge-SCENE-hpdev-com.gdi.coredesa.inspector-Pay-Android.md` §3.3–§4, con el override del proxy de la bitácora 10 §4 sirviendo el `blazor.web.js` publicado (`/vm/wt/pub-fix08-wv91/wwwroot/_framework/blazor.web.js`). Después, restaurar el proxy.
- **Commit** `66b4f945f92a5e6ee8b9b521449d4788e46f8b95` («regenerar blazor.web.compat.js para .NET 10.0.14»). Cambia 4 archivos: `.targets`, `README.md`, `blazor.web.compat.js` y `source.sha256`. Push a `fix08-blazor-webview91`; `git ls-remote` devuelve 66b4f945. Sin PR ni merge: `GET pulls?head=…&state=all` dio `[]`.
- **Credencial:** se obtuvo con `git credential fill`. Para git se pasó por `GIT_ASKPASS`, un script 0700 que lee variables de entorno; para curl, por `-K` con un archivo 0600. En ningún caso fue en argv, y los dos archivos se borraron al terminar. No se listó `~/.git-credentials`.
