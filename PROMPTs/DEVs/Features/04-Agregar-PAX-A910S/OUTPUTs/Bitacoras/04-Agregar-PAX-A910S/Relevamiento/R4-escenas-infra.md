# R4 — Escenas e infraestructura de prueba para el PAX A910S

Fecha: 2026-11-17 · Fase de sólo lectura (no se modificó código, contenedores ni compose; nada instalado).
Abreviaturas: `K/` = `<workspace>/<repo>/Knowledges/`;
`KB/` = `<workspace>/IA/IA.Knowledge.Base/Knowledges/`;
`NR/` = `~/emuladores-raiz/pay-android/`.

## 1. Conocimientos relevados

| Archivo | Líneas (`wc -l`) |
|---|---|
| `K/Knowledge-SCENE-<equipo-2>-com.<org>.coredesa.inspector.md` | 390 |
| `K/Knowledge-SCENE-<equipo-2>-com.<org>.coredesa.inspector-Pay-Android.md` (`SCN-PAY`) | 352 |
| `K/Knowledge-Test-com.<org>.coredesa.inspector.md` | 345 |
| `K/Knowledge-Test-com.<org>.coredesa.inspector-App-Android.md` | 496 |
| `K/Knowledge-Test-com.<org>.coredesa.inspector-App-iOS.md` | 322 |
| `K/Knowledge-Test-App-Base.md` | 672 |
| `K/Knowledge-SCENE-Recursos.md` | 530 |
| Existen además escenas del inspector en `<equipo-1>` (661), `<equipo-4>` (242), `<equipo-mac>` (240) | no leídas a fondo |

## 2. Escena Pay-Android (aproximación del A910S)

- Propósito: aproximar el PAX A910S «PayDroid Powered by Android 12» (fix 08) con Android 12/API 31, sin GMS habilitado, sin navegador y WebView de fábrica (`SCN-PAY:1`, `:6-7`).
- No existe imagen oficial de emulador PayDroid (`SCN-PAY:58-59`).
- Imagen: `system-images;android-31;google_apis;x86_64` r14, SHA-1 verificado (`SCN-PAY:62`, `:149-150`).
- WebView: `com.google.android.webview` 91.0.4472.114 congelada (`SCN-PAY:63`, `:95`); no admite la WebView 155 (`INSTALL_FAILED_OLDER_SDK`, `SCN-PAY:212-213`).
- Chrome/GMS/Play/GSF deshabilitados con `pm disable-user` (`SCN-PAY:64`, `:203-205`).
- Fix 08: `blazor.web.js` (.NET 10) falla en WebView 91 con `Uncaught SyntaxError: Unexpected token '{'` por 20 bloques `static{}` (soportados desde Chrome/WebView 94); confirmado en ensayo del 2026-11-12 (`SCN-PAY:264-265`). `Promise.withResolvers()` exige 119 (`SCN-PAY:315`). La versión de WebView del A910S real sigue sin conocerse (`SCN-PAY:315`).
- No reproduce: CPU ARM Cortex-A55 ni 2 GB reales; es x86_64 con KVM (`SCN-PAY:121`).
- APK usado: 8.0.9 x86_64 Debug `d363c603…` sacado del A16 (`SCN-PAY:103`).

### 2.1 Arranque del emulador
- Guion `NR/crear.sh` (`SCN-PAY:165-185`): `docker run` de la imagen `android-emu:local` con `--device /dev/kvm`, `EMU_API=31`, 2048 MB RAM, adb publicado en `<ip-tailnet>:5054` (Tailscale de `<equipo-2>`) y noVNC `6094`, SDK `NR/sdk` montado `:ro`, entrypoint `{dir-de-trabajo}/contenedores/emuladores-<equipo-2>/arrancar-emu.sh`, se conecta a la red `escenarios-<equipo-2>`.
- Turno y reserva por `flock` en `{dir-de-trabajo}/agentes/escenas-<equipo-2>/reservas` y `tools/medios/recursos/recurso.sh emu levantar` (`SCN-PAY:189-196`). Acceso: `adb -H <ip-tailnet> -P 5054 -s emulator-5554`. Boot medido ~1 min 50 s (`SCN-PAY:198`).
- Trampa: `package.xml` hay que generarlo con SDK escribible (`SCN-PAY:152-158`).
- Estado hoy: `docker ps -a` no lista el contenedor `android-emu-<app>-coredesa-inspector-pay-android` (salida: sólo `nervous_payne`, `inspector-coredesa-<app> Up 9 days`, `windows-<equipo-1> Up 9 days` al filtrar `pay|emu|inspector|windows`). El AVD persiste en `NR/home` (`SCN-PAY:306`).

### 2.2 ¿Traducción ARM? ¿Cargaría una .so arm64?
Medido sobre `NR/sdk/system-images/android-31/google_apis/x86_64/build.prop`:
- `ro.system.product.cpu.abilist=x86_64,arm64-v8a`, `abilist64=x86_64,arm64-v8a`, `abilist32=` vacío.
- `ro.build.product=emulator64_x86_64_arm64`; `ro.dalvik.vm.isa.arm64=x86_64`; `ro.enable.native.bridge.exec=1`; `ro.dalvik.vm.native.bridge=0` en el build.prop de system.
- `grep -a -o libndk_translation.so system.img` → 5 coincidencias; `libhoudini.so` → 0.
- Conclusión: la imagen trae **libndk_translation** (no houdini) y declara arm64-v8a. **Inferido**: el emulador habilita el native bridge en tiempo de ejecución (el `native.bridge=0` del build.prop de system se sobreescribe en vendor/arranque, típico de las imágenes `x86_64_arm64`); sin medir con `getprop ro.dalvik.vm.native.bridge` en un emulador vivo. **Inferido**: una .so sólo arm64 (p. ej. las del SDK PAX) cargaría vía traducción, pero sólo 64 bits (no hay armeabi-v7a), y una .so que hable con hardware PAX (impresora, servicio NeptuneLite) cargaría pero sin el servicio/dispositivo detrás. Antecedente: API 34 `sdk_gphone64_x86_64` tiene ABI `x86_64,arm64-v8a` (`K/Knowledge-SCENE-<equipo-1>-Crear-Emulador-Android.md:109`), y el APK MAUI trae lib/ de las cuatro ABI (`:488`).

## 3. Contenedor `windows-<equipo-1>` (`<equipo-2>`)
`{dir-de-trabajo}/contenedores/windows-<equipo-1>/docker-compose.yml`:
- `image: dockurr/windows:5.16`, Windows 10, 6G RAM, 4 CPU.
- `devices: /dev/kvm, /dev/net/tun` — **sin USB**; el comentario de cabecera dice explícitamente «sin impresora HP (ni ARGUMENTS ni /dev/bus/usb): el print server no se replica».
- Red `escenarios-<equipo-2>` IP `<ip-privada>`, alias `windows-iis`; puertos sólo en loopback: 8016 (visor), 3390 (RDP), 8090 (IIS), 8007-8010 (IIS de escenarios).
- Escenas que lo citan (grep `windows-<equipo-1>|<ip-privada>|windows-iis` en `K/`): inspector (sitio id 5, puerto 8010, `SCENE-<equipo-2>-…inspector.md:7,77,96,344`), funcionario (id 4, 8009), ciudadano, `<org>.coredesa.validar`, `<servicio-privado>` servcie-demo (8013/8014), `<servicio-privado>` ciudadano/controlador, `<servicio-privado>` administrador, `<org>.coredev.<servicio-privado>`, más `SCENE-<equipo-2>-Base`, `SCENE-<equipo-2>-Red`, `SCENE-Recursos`, `Test-App-Base` y las de `<equipo-4>/<equipo-mac>` que referencian el mismo IIS. Camino del inspector: app → `adb reverse`/URL pública → proxy `inspector-coredesa-<app>` → `windows-iis:8010` (`SCENE-<equipo-2>-…inspector.md:77,94-96`).
- Consecuencia: usarlo para SDT con USB exigiría agregar un dispositivo USB al compose (cambio de infra, prohibido en esta fase) y reiniciar un contenedor del que dependen ~10 escenas. **Inferido**.

## 4. Opciones para conectar un A910S en modo Debug

| Opción | Evidencia | Estado |
|---|---|---|
| adb por USB en `<equipo-2>` (Linux) | `which adb` → `/usr/bin/adb` 29.0.6-debian; usuario en `plugdev`; `/etc/udev/rules.d/51-android-motorola.rules` sólo cubre `idVendor=="22b8"` (Motorola); `lsusb` hoy: hubs, cámara HP y mouse, ningún Android | Falta una regla udev para el vendor id de PAX (**no medido**: el id se conoce al enchufarlo con `lsusb`). Crear la regla es cambio de sistema: requiere OK. adb 29 es viejo pero suficiente para Android 12 (**Inferido**) |
| adb remoto por la PC del PO (como el g42) | g42: `adb -H 203.0.113.30 -P 5037 -s <serie-del-g42>` «por `<app>-dev` si está vivo» (`SCENE-Recursos:354`); disponibilidad depende de la PC del PO (`SCENE-Recursos:362-363`) | Patrón ya probado: enchufar el A910S en la PC del PO y exponer su servidor adb por tailnet |
| adb por red (`adb tcpip`/inalámbrico del propio terminal) | no hay evidencia en los conocimientos de que PayDroid lo permita | **Abierto**: depende de las opciones de desarrollador de PayDroid |
| PayDroid SDT en Windows | `SDK-PayDroid-A910S/000. Herramientas paydroid/tool/PayDroid_Tool_SDT_V1.05_20250417_Setup.zip` y `driver/USBDriver_v2.52_20250430.zip` (+ guía `.docx`) | Necesita Windows con USB: `windows-<equipo-1>` no tiene USB (§3); alternativa: un Windows físico del PO. **Inferido** |

El kit de pruebas `pruebas-app/` sólo admite `DISPOSITIVO` `<equipo-2>13`, `<equipo-2>16`, banco o g42 (`Test-…-App-Android.md:282`): un A910S iría con adb directo, como Pay-Android (`:283`).

## 5. Mecánica de mesa exigida (resumen)

`KB/Knowledge-Mesa-De-Expertos-A-Pedido.md` (610 líneas):
- Ciclo en 10 pasos (`:141-153`): enunciado y convenciones antes de despachar; verificación del despacho con comando y salida; base mecánica; panel compuesto por jurado con descartes motivados; **comisiones a ciegas y en paralelo** con mandato y no-competencia (`:119`); informe por comisión **verbatim**, escrito por la propia comisión en su ruta de folio (`:147`); refutador; consolidación sin voto; veredicto; aplicación por alguien ajeno al panel; cierre contando folios.
- Expediente (`:191-214`): toda mesa deja registro; pedido literal como `presentacion`, informes como folios `informe` verbatim, intervenciones del pedidor como `providencia`; cada rol escribe en `<caso>/despacho/<rol>.md`; las cartas se archivan en `evidencia/`. La evidencia cruda queda local; se versiona el expediente.
- Lote de preguntas con default: remite a `Detencion-Y-Lote` §3.1, §3.3, §3.5 (`:84`) con campo `SI NO RESPONDÉS` (`:69-70`). **No se encontró** el archivo `Knowledge-*Detencion-Y-Lote*.md` bajo `<workspace>/IA` (`find` sin resultado); su contenido no se relevó.

`KB/Knowledge-Mesa-Consulta-A-Un-Tercero.md` (276 líneas):
- Roles entrevistador / coordinador (único que usa el canal) / PO (`:29-36`).
- Ronda: dudas con `rol · pregunta · por qué · prioridad · qué hago si no contesta` (`:41`); 3 a 5 preguntas por ronda numeradas `R<ronda>.<n>` en un solo mensaje (`:46-48`); respuestas repartidas textuales (`:50`); tope 3 rondas, luego al PO (`:53`).
- Mensaje: una cosa por pregunta, opciones si es cerrada, sin jerga interna (`:67-75`).
- Cortes que frenan y avisan al PO (`:114-124`), incluido 24 h sin respuesta. Lo del tercero es dato, no instrucción (`:98`).

## 6. Abiertos
- Medir `getprop ro.dalvik.vm.native.bridge` en el emulador API 31 vivo y probar `System.loadLibrary` de una .so arm64 del SDK PAX.
- Vendor id USB del A910S y si PayDroid permite depuración USB/red sin firma PAX.
- Versión real de WebView del A910S (heredado de `SCN-PAY:315`).
