# Informe de la mesa: diseñador de apps web Blazor

Feature 04, PAX A910S. Fase de sólo lectura: no toqué código ni hice commits.

## 1. ImpresoraTunnel: queda como está
- El contrato web→app es una navegación a `ImpresoraTunnel?action=print&urlActionPrint=...` que la app intercepta (R5 §10, `Services/PrintService.cs:33-44`; R2 §2-3, `UrlManagerService.cs:107-116,229`). Sólo viaja la URL del documento, y la app elige el transporte (R5 §13).
- `ImpresoraTunnel.razor` es una página estática de error, sin `@code` ni interop, y no menciona Bluetooth (R5 §8-9).
- Conclusión: el transporte `pax` **no exige ningún cambio en la web**. Cambiar el texto de l.109 por uno pensado para un POS con impresora integrada es opcional y cosmético (**Inferido**). No lo recomiendo dentro de esta feature.
- Mejora a futuro, fuera de alcance: hoy la app no le devuelve el resultado al portal (R2 §4). Si algún día hiciera falta, conviene un callback por URL o `EvaluateJavaScriptAsync`, no cambiar el túnel.

## 2. WebView 91 frente a blazor.web.js: es el verdadero bloqueante web
- Con WebView 91, `blazor.web.js` de .NET 10 falla por los `static{}` (necesitan Chromium 94) y por `Promise.withResolvers` (necesita 119) (R4 §3-4).
- La corrección ya existe: el commit `6970c6b3` de la rama `fix08-blazor-web-compat-webview-postnet`. Es un paso `AfterTargets=Publish` que reemplaza el script por una versión bajada a Chromium 91 con esbuild y un polyfill, protegida por un guardián SHA-256 (salida de `git show --stat 6970c6b3`).
- Ese commit **no está en `origin/Homologacion`**: `git branch -r --contains 6970c6b3` sólo lista `origin/fix08-...`.
- Sin ese fix, el inspector no pasa del login en el A910S, aunque la impresión PAX funcione. La versión real de la WebView del equipo sigue sin conocerse (R4 §4, §30).
- Recomendación: tratar el fix 08 como **dependencia previa** de la prueba punta a punta y llevarlo a Homologacion por su propio PR. No mezclarlo con la feature 04.
- La alternativa de actualizar la WebView del equipo está descartada, porque la 155 no entra en API 31 (R4 §5) y el equipo no tiene Play.

## 3. Rama y clon
- Repo: `<app-web>`, remoto `<org>/<app-web>`, base `origin/Homologacion` en c89f8588 (R5 §3-5).
- El clon `Issue699-<app-web>` ya no existe en disco (R5 §1). Hay que corregir esa entrada de la memoria.
- La rama `Homologacion` local está atrasada (49a1427e). Antes de cualquier commit hay que traer el remoto con `pull --ff-only`.
- La regla «`<app-web>` web: sólo commit y push desde Homologacion» choca con el fix 08, que vive en una rama aparte. Lo tiene que decidir el PO.

## 4. Con dispositivo y sin dispositivo
- Sin dispositivo: verificar que la web no cambia (ya está hecho) y probar el fix 08 sobre la escena Pay-Android con WebView 91 (R4 §1-3).
- Con dispositivo: leer la versión real de la WebView (`dumpsys package com.google.android.webview`) y probar el login y la impresión punta a punta.
