# Informe de la comisión UX, flujo de usuario e UI (feature 04, PAX A910S)

Las rutas de la app son relativas a `Ng/Ng-Core/GDA.APP/GDA.Core.APP/`.

## 1. Estado actual: lo que el inspector ve hoy

- El overlay es genérico. Tiene un estado ocupado (título, subtítulo y gif) y un estado de error (ícono, título, mensaje y botones generados desde `Actions`) (`Controls/StatusOverlayView.xaml:29-55`).
- La secuencia de Bluetooth es esta (`ViewModels/PrinterOverlayViewModel.cs`):
  1. «Preparando impresión / Obteniendo el comprobante…» (`:82`).
  2. «Verificando permisos…» (`:125`).
  3. «Buscando impresoras» (`:140`).
  4. El selector «Elegí una impresora» (`:210`).
  5. «Conectando a X…» (`:224`).
  6. «Imprimiendo / Enviando el documento…» (`:270`).
- La botonera de error depende de la causa (`:286-313`):
  - sin papel muestra «Ya cargué papel — Reintentar» (`:293`);
  - tapa abierta muestra «Ya la cerré — Reintentar» (`:297`).
- El catálogo de errores tiene códigos estables `PRN-*` (`Services/Printing/PrinterErrorCatalog.cs:20-39`).
- El catálogo distingue papel y tapa comparando el texto de la excepción con «paper» y «cover» (`:136-147`). Todo lo demás cae en `PRN-HW-OTHER`, «Problema en la impresora».
- Hay textos que dicen Bluetooth de forma explícita:
  - «Este dispositivo no puede imprimir por Bluetooth.» (`:120` y `:180`);
  - los permisos, «Permiso Bluetooth necesario» (`:321-336`);
  - el botón «Emparejar impresora» (`:160`).

## 2. Propuesta: lo que el inspector ve en PAX

Principio: en el A910S la impresora es parte del equipo. El inspector no tiene que ver nada que tenga que ver con Bluetooth ni con elegir impresora.

| Paso | Bluetooth (hoy) | PAX (propuesto) |
|---|---|---|
| Documento | «Obteniendo el comprobante…» | igual |
| Permisos | BLUETOOTH_SCAN/CONNECT | sin diálogo: `com.pax.permission.PRINTER` se declara en el manifiesto y no se pide en tiempo de ejecución (**Inferido**, R3 punto 6) |
| Buscar / elegir | búsqueda y selector | se omite |
| Conectar | «Conectando a X…» | se omite, o «Preparando la impresora…» mientras corre `getDal` |
| Imprimir | «Enviando el documento…» | «Imprimiendo…», hasta `onSucc` u `onError` (`IPrinter.java:470-514`, R3) |
| Éxito | igual | igual |

El flujo PAX queda en tres estados: obtener el documento, imprimir y mostrar el resultado. Las ramas de búsqueda, conexión y permisos no se tocan; sólo se saltean cuando el transporte activo es `pax`.

## 3. Mensajes de error nuevos o mapeados (códigos de R3, punto 10)

| Código PAX | Código `PRN-*` | Título / mensaje | Botón primario |
|---|---|---|---|
| 2 sin papel | `PRN-HW-PAPER` (existe) | «Sin papel» / «Cargá un rollo nuevo y reintentá.» (el texto de `:139-140` sirve tal cual) | «Ya cargué papel — Reintentar» |
| 8 sobrecalentamiento | nuevo `PRN-HW-HEAT` | «Impresora caliente» / «Esperá un minuto a que se enfríe y reintentá.» | «Reintentar» |
| 1 ocupada | nuevo `PRN-HW-BUSY` | «Impresora ocupada» / «Está terminando otra impresión. Reintentá en unos segundos.» | «Reintentar»; **Inferido**: conviene un reintento automático corto antes de mostrarlo |
| 9 voltaje bajo | nuevo `PRN-HW-BATT` | «Batería baja» / «Conectá el cargador para imprimir.» | «Reintentar» |
| 3, 4, -2, -4 y otros | `PRN-HW-OTHER` / `PRN-UNKNOWN` | los textos genéricos actuales, más el código técnico en el log | «Reintentar» |
| NeptuneService ausente / `LOAD DAL ERR` / 99 / 101 / 103 | nuevo `PRN-PAX-SVC` | «Impresora del equipo no disponible» / «Falta el servicio de impresión del equipo. Avisá a soporte.» | sólo «Cerrar», porque reintentar no lo arregla |

En la tabla de R3 hay códigos de -6/-5 (cuchilla o tapa), pero sólo aplican al E500/E800. Para el A910S no hace falta un botón de tapa.

Recomendación técnica para la UX: el mapeo no tiene que depender de textos en inglés, como pasa hoy en `:136`. La librería debería exponer un subtipo o código estable en `PrinterHardwareException` (por ejemplo `HardwareReason.PaperOut`, `Overheat`, `Busy`, `LowVoltage`). Así el catálogo de la app mapea por enum. Las dos numeraciones de PAX, la de `getStatus` y la de `EPrintDevException` (R3 punto 14), se traducen dentro del transporte y no llegan a la UI.

## 4. Textos que hay que neutralizar (no dependen del dispositivo)

- `:120` y `:180`: cambiar «no puede imprimir por Bluetooth» por «Este dispositivo no tiene una impresora disponible.»
- Web, `ImpresoraTunnel.razor:109`: no hace falta cambiarlo. R5 indica que el texto ya es genérico y que la página sólo aparece si la app no intercepta la navegación.

## 5. Qué decide el transporte (sin opción por trío)

- **Inferido**: conviene detectarlo en tiempo de ejecución. Si el paquete NeptuneService (R3 punto 16, falta confirmar el nombre) y el transporte PAX están, se usa `pax`; si no, `bluetooth`.
- Así un mismo APK sirve en el teléfono y en el POS, y no hace falta tocar `Config.cs` (R2 punto 15).
- La impresora PAX simulada se elige por configuración de Debug y usa las mismas pantallas.

## 6. Sin el dispositivo / con el dispositivo

**Sin el dispositivo:**
- la rama PAX del overlay;
- los códigos y textos nuevos del catálogo;
- la neutralización de textos;
- los tests de UI con el simulador de estados (sin papel, caliente, ocupado, servicio ausente);
- en el emulador Pay-Android, comprobar que aparece «Impresora del equipo no disponible» y que la app no se cae.

**Con el dispositivo:**
- confirmar que `onError` devuelve los códigos esperados al sacar el papel o calentar el cabezal;
- medir el tiempo real de impresión, para el subtítulo y el timeout;
- confirmar que el permiso PRINTER no muestra ningún diálogo;
- revisar legibilidad y contraste del overlay en la pantalla del A910S;
- comprobar el comportamiento del botón Atrás físico con el overlay abierto.

## 7. Riesgos de UX

- WebView 91 (R4 punto 3): si la WebView del A910S es anterior a la 94, el inspector web no carga y el flujo de impresión ni siquiera empieza. Es el riesgo de UX más grave y no depende de la impresora.
- La app no le informa el resultado al portal (R2 punto 4). El inspector sólo se entera del éxito por el overlay. No es nuevo, pero en el POS la impresión es más rápida y el overlay puede pasar muy rápido.
- Si se toma el error 1 (ocupada) como fallo sin reintento automático, aparecen errores molestos cuando el inspector toca dos veces.
