# Informe de QA — Feature 04 (PAX A910S)

Rol: QA. Fase de sólo lectura. No modifiqué código, no hice commits ni cambié infraestructura.

## 1. Propuesta: cuatro niveles de prueba

Las pruebas se ordenan por cuánto dependen del equipo. Los niveles N1 a N3 se hacen **sin el A910S**. N4 lo necesita.

### N1. Tests unitarios con fake (net10.0, xUnit; corren en CI `pack-managed`)
- Base: `FakeTransport` (`Kind="fake"`, `ThrowOnWrite`) en `src/MotorDsl.Tests/TestFakes.cs:16-42`. Hoy la suite tiene 315 casos en verde (R1 §13).
- Para que se pueda probar sin Android, la lógica del transporte va contra una abstracción propia, por ejemplo `IPaxPrinterDevice` con `Print(png) -> status` y `GetStatus()`. **Inferido**: con eso, la clase de mapeo de estados y la validación de PNG quedan en código `net10.0`, que los tests pueden compilar. Se puede enlazar como fuente, igual que se hace hoy con Bluetooth (`MotorDsl.Tests.csproj:31-32`).
- Casos mínimos:
  1. Firma PNG válida: delega en el dispositivo.
  2. Bytes ESC/POS o basura: falla con `PrintErrorType.Protocol` (R1 §21).
  3. Mapeo de `getStatus`/`start`/`onError` (R3 §10):
     - 0 da éxito;
     - 1 (ocupada), 2 (sin papel), 8 (sobrecalentamiento) y 9 (voltaje bajo) dan `Hardware`;
     - 3 (formato) y -2 (datos largos) dan `Protocol`;
     - un código desconocido da `Unknown`.
  4. Mapeo aparte de `EPrintDevException`, con 99 CONNECT, 101 NO_PERMISSION y 103 NOT_IN_WHITELIST. Las dos tablas no coinciden (R3 §14), así que se prueban por separado y no se reusan constantes.
  5. "NeptuneService ausente" (falla `getDal`, `LOAD DAL ERR`) da `Connection`, con un mensaje claro.
  6. Callback asíncrono: el `onSucc` y el `onError` del listener completan la Task, y si no llegan, vence por timeout del `PrinterProfile`.
  7. Registro DI: `AddPaxPrinterTransport` convive con Bluetooth y `ThermalPrinterService` lo elige por `Kind="pax"` (`ThermalPrinterService.cs:103,135-136`).
  8. El ancho que manda el perfil PAX se respeta: el PNG no supera `bitmap_max_width_px`.

### N2. Impresora PAX simulada (pedido explícito del PO)
- Es una implementación de `IPaxPrinterDevice` que se elige por configuración (por ejemplo `Pax:Simulated=true`, o un trío o perfil de desarrollo). Hace dos cosas:
  - vuelca a archivo el PNG exacto que iría a `print(Bitmap)`, con un nombre que lleva fecha, ancho y alto;
  - simula los estados con una secuencia que se puede configurar, por ejemplo `ok`, `sin-papel`, `sobrecalentado` u `ocupada`.
- Golden tests del ticket:
  - **Inferido / riesgo**: `RasterPreviewRenderer` está en `MotorDsl.Maui` (`src/MotorDsl.Maui/Renderers/RasterPreviewRenderer.cs:32`), con SkiaSharp. El proyecto de tests no referencia Maui (R1 §11).
  - Opción simple: test de integración en el sample o en el devcontainer de la librería. Ahí se renderiza un `PrintDocument` real, como el acta, y se comparan contra un PNG de referencia el ancho (exacto al perfil), el alto (> 0) y un hash o diferencia de píxeles con tolerancia.
  - Las imágenes de referencia van en `Images/` junto al md de pruebas.
- En la app: con el simulador se recorre todo el flujo `action=print`, pasando por `PrintCoordinator` y el overlay, y se verifica el mensaje de cada estado. Esto no necesita hardware.

### N3. Emulador Pay-Android (escena existente, API 31, WebView 91, x86_64 con libndk_translation)
Lo que sirve para verificar:
- **Degradación**: sin NeptuneService ni hardware PAX, la app no se cae y el overlay informa el error.
- **ABI**: el SDK sólo trae `arm64-v8a` y `armeabi` (R3 §3). Hay que verificar que el APK x86_64 instale y abra. Hay dos resultados posibles:
  - la `.so` carga por traducción;
  - falla de forma controlada (`UnsatisfiedLinkError` atrapado).
  Hace falta medir `getprop ro.dalvik.vm.native.bridge` en vivo (R4 §11, §29).
- **Bluetooth sin regresión**: con el trío Bluetooth, el flujo sigue igual.
- **Simulador PAX activo**: genera el PNG en el almacenamiento de la app y se recupera con `adb pull`.

Lo que no sirve para verificar:
- la impresión real;
- la WebView del A910S;
- el rendimiento ARM con 2 GB.

El arranque de la escena necesita turno (`flock` y `recurso.sh`; R4 §6). Eso es uso de un recurso existente, no un cambio de infraestructura.

### N4. Equipo físico A910S (checklist; no se da por cerrado sin evidencia)
1. Identificación:
   - `adb devices` por USB en hpdev (`lsusb`: vendor id);
   - regla udev nueva. **Es un cambio de infraestructura y pide autorización del PO** (R4 §16).
   - Alternativa sin tocar infraestructura: adb por la PC del PO (R4 §17).
2. `getprop ro.build.version.sdk`, `ro.build.version.release`, versión de PayDroid y `ro.product.cpu.abilist`.
3. **Versión real de WebView**: `adb shell dumpsys webviewupdate` y `pm list packages -f | grep -i webview`, más `dumpsys package com.android.webview | grep versionName`.
   - Criterio: ≥ 94 para que parsee `blazor.web.js` (`static{}`) y ≥ 119 por `Promise.withResolvers` (R4 §3-4).
   - Si da menos, se bloquea la aceptación del inspector web (fix 08), con independencia de la impresión.
4. `pm list packages | grep -i neptune`: confirmar `com.pax.ipp.neptune` y su versión (R3 §16).
5. Instalar el APK Debug del trío. Primer arranque, login y GPS inyectado (`idInputCoordenada`, R5 §15-16).
6. Imprimir el ticket de calibración (regla o patrón de 400 px o más). Como el sobrante se recorta a la derecha (R3 §12), eso mide el **ancho real en px**. Fotografiarlo y archivarlo como evidencia.
7. Imprimir un acta real desde `ActaCreada` y desde `DetalleActa`. Compararla con el PNG del simulador para el mismo documento: misma geometría.
8. Estados reales:
   - sin papel (tapa abierta o rollo retirado);
   - impresión repetida rápida (ocupada);
   - ticket largo (sobrecalentamiento o datos largos, si se puede provocar).
   Cada uno se verifica con el mensaje del overlay y el código de logcat.
9. `setGray`: contraste aceptable en el valor por defecto.
10. Pruebas en Release:
    - ProGuard o R8 conserva `com.pax.**` (R3 §5);
    - las `.so` cargan con la firma de Release.
    La firma con Leandro queda pendiente.
11. Permiso `com.pax.permission.PRINTER`: comportamiento con él y sin él (R3 §6).

## 2. Criterios de aceptación

- CA1: `dotnet test` en verde, sin bajar de los 315 casos actuales, con los casos nuevos de N1. El CI `cd-nuget.yml` publica el paquete nuevo y el conteo de paquetes se actualiza.
- CA2: el simulador genera un PNG del ancho exacto del perfil PAX y reproduce los estados ok, sin papel, sobrecalentamiento y ocupada. La app muestra un mensaje distinto y en español para cada uno.
- CA3: en el emulador Pay-Android, la app no se cae sin NeptuneService. Informa un error de conexión y el resto del inspector sigue usable.
- CA4: no hay regresión en Bluetooth (trío actual, g42).
- CA5: en el A910S, la impresión real del acta es legible, sin recorte a la derecha y con el ancho medido documentado.
- CA6: WebView del A910S ≥ 119, o en su defecto un riesgo aceptado por escrito por el PO.
- CA7: el build Release imprime, con ProGuard y firma.
- CA8: el conocimiento `Knowledge-Test-com.gdi.coredesa.inspector-App-PayDroid.md` contiene los checklists N3 y N4, con evidencias enlazadas.

## 3. Riesgos (QA)
- La WebView del A910S es desconocida. Si es < 94, el inspector web no carga, aunque la impresión funcione. Es el riesgo mayor, porque no depende de esta feature.
- El ancho en px no está documentado. El perfil PAX arranca con un valor **Inferido** (384) que se corrige en N4. Los golden tests se regeneran después.
- Las dos numeraciones de error, si se mezclan, darían mensajes equivocados.
- Golden PNG con SkiaSharp fuera de `net10.0`: si se ponen en la suite actual, se rompe la regla de que los tests no dependan de Maui.
- El emulador puede dar falsos positivos, porque la traducción ARM no es el equipo.

## 4. Separación
- Sin el equipo: N1, N2, N3, CA1-CA4 y CA8 (borrador).
- Con el equipo: N4, CA5-CA7, y CA8 con evidencias.
