# Núcleo 05 — Conexión física del A910S, escenas y conocimientos

Trazabilidad: T11, T12, D1, D3. Expediente: 0002-conexion-fisica-a910s.

## Decisión de vía
1. **Vía inicial (sin cambio de infra): adb remoto por la PC del PO** por tailnet, patrón ya usado con el g42 (`adb -H 100.66.63.98 -P 5037`, `Knowledge-SCENE-Recursos.md:354,362-363`). El A910S llega en Debug, así que el SDT no es necesario para depurar.
2. **Vía objetivo (cambio de infra requerido, NO aplicado):** adb USB en hpdev. Requiere crear `/etc/udev/rules.d/51-android-pax.rules` con el `idVendor` del A910S (se obtiene con `lsusb` al enchufarlo; hoy sólo existe `51-android-motorola.rules` con `22b8`, R4 §4). adb 29.0.6 presente. **Requiere autorización del PO.**
3. **SDT/USBDriver (sólo Windows):** únicamente si NeptuneService no viene preinstalado ("usually preloaded", `ide.txt:373`), en un Windows físico con USB. **Se descarta `windows-i7infra`**: sin USB (`/vm/contenedores/windows-i7infra/docker-compose.yml`: devices sólo kvm y tun) y sirve el IIS de ~10 escenas (R4 §3); agregar USB y reiniciarlo es de alto impacto.
4. **Escena Pay-Android:** se reutiliza (no se crea otra) para degradación, ABI y fix08, no para impresión (no hay `.so` x86; imagen con `libndk_translation` y abilist `x86_64,arm64-v8a`, R4 §2.2).
5. **Conocimientos (T11):** crear `Ng/Ng-IA/Ng.IA-Context.Scene/Knowledges/Knowledge-Test-com.gdi.coredesa.inspector-App-PayDroid.md` siguiendo `Knowledge-Test-…-App-Android.md`; agregar referencia cruzada en `…-App-Android.md` (`:282-283`, el kit `pruebas-app/` no admite el A910S); alta del tipo de dispositivo en `Knowledge-SCENE-Recursos.md`. `…-Pay-Android.md` **no** lleva referencia: su versión 1.0.2 fija «L3 no cita L4; el índice es la puerta» (corrección de Verificacion-2). Se redactan sin dispositivo con los datos marcados "a medir". Estado: creado en `feature/pax-a910s-conocimientos` (5e468dc, sin push).

## Criterios
CA-05.1 conocimiento PayDroid creado y enlazado. CA-05.2 decisión del PO sobre udev registrada. CA-05.3 `adb devices` ve el A910S por la vía elegida (D1).

## Evidencia
../Bitacoras/04-Agregar-PAX-A910S/Relevamiento/R4-escenas-infra.md §2-4 · ../Bitacoras/04-Agregar-PAX-A910S/Mesa/informe-devops.md · ../Bitacoras/04-Agregar-PAX-A910S/Mesa/informe-qa.md
