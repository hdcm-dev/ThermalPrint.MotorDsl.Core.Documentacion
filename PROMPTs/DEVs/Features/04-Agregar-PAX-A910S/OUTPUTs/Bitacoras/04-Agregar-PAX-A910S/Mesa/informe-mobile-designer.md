# Informe de la mesa: diseño de app móvil MAUI (feature 04, PAX A910S)

Rutas de la app relativas a `<app>/<app>/`.

## Evidencia de partida (verificada en esta sesión)
- `Services/Printing/IPrinterService.cs:11-40`: la interfaz ya es casi agnóstica (Discover, GetDefaultIfPresent, Connect, Send(byte[]), SaveDefault, alias). Lo único atado a Bluetooth es `EnsurePermissionsAsync()` que devuelve `BluetoothPermissionResult` (`:16`) y el comentario de `IsSupported` (`:13`).
- `Services/Printing/PrinterService.cs:25-30`: `IsSupported` es `#if ANDROID true`; `:97` descubre con `kind: "bluetooth"` fijo; `:136` `SendAsync(byte[])`.
- `PrintCoordinator.cs:90-93`: perfil fijo `DeviceProfile("58HB6", 32, "escpos-bitmap")`, 320 px, umbral 128.
- R1 punto 21/24: la alternativa (a) (PNG por `WriteBytesAsync`, target propio tipo `raster-pax`) no cambia contratos de la librería.
- R3 puntos 7, 14, 16, 20: `print(Bitmap, IPinterListener)` asíncrona; dos numeraciones de error; el SDK no detecta la falta de NeptuneService; sin ABIs x86.
- R5 punto 14: la web no cambia.

## Propuesta
1. **Un perfil de impresión por trío, no por código.** Sacar el perfil de `PrintCoordinator.cs:90-93` a una opción del trío (`Config.cs`, junto a las de `:94-104`) con dos valores: `Bluetooth58HB6` (actual) y `PaxIntegrada`. El coordinador pide el `DeviceProfile` a un proveedor (`IPrintProfileProvider`) en vez de construirlo. Sin trío configurado, default = Bluetooth (comportamiento actual intacto).
2. **Generalizar `IPrinterService` mínimamente:** renombrar `EnsurePermissionsAsync` a un resultado neutral (`PrinterReadiness`: Ok / Denegado / Bloqueado / ServicioAusente / NoSoportado) y agregar `string Kind`. Dos implementaciones: `BluetoothPrinterService` (el actual, renombrado) y `PaxPrinterService`.
3. **`PaxPrinterService`** (sólo `#if ANDROID`, y en runtime sólo si el ABI es arm/arm64):
   - `EnsurePermissionsAsync` = verificar que el paquete NeptuneService esté instalado con `PackageManager` (nombre **Inferido** `com.pax.ipp.neptune`, R3 punto 16, confirmar en equipo) y que `getDal` no lance; no pide permisos de runtime (`com.pax.permission.PRINTER` es de manifiesto, R3 punto 6).
   - `DiscoverAsync` devuelve un único `PrinterDevice("pax-integrada")`; con eso el overlay toma la rama "única impresora" sin selector (`PrinterOverlayViewModel.cs:104-271`, R2 punto 10) y no hay que tocar su flujo.
   - `ConnectAsync` = `true` si el DAL cargó; `SendAsync` delega en `IThermalPrinterService` con transporte `pax` (librería, alternativa a de R1).
4. **Overlay:** sin vista nueva. Sólo textos por `Kind`: no mostrar "encendé el Bluetooth"/"elegí impresora" cuando es PAX; agregar mensajes para `ServicioAusente` ("Falta el servicio de impresión del terminal (NeptuneService). Contactá a soporte.") y para los códigos de hardware (2 sin papel, 8 sobrecalentamiento, 9 batería baja, 1 ocupada → reintentar).
5. **Registro DI (`MauiProgram.cs:66-75`):** registrar ambos transportes (patrón `AddSingleton` de R1 punto 5) y resolver `IPrinterService` según el trío. Agregar el `DeviceProfile` PAX a `AddProfiles` en lugar del perfil fantasma 58HB6 (R2 punto 12).
6. **Permisos Bluetooth:** declararlos explícitamente en los manifiestos del trío (hoy no aparecen, R2 punto 13) o confirmar que MotorDsl.Bluetooth los mergea; en el trío PAX agregar `com.pax.permission.PRINTER`. Independiente del PAX, es un riesgo actual del flujo Bluetooth.
7. **Fallo sin NeptuneService:** degradar, nunca crashear. Cualquier `Exception("LOAD DAL ERR")` (R3 punto 15) y el error 99 CONNECT se mapean a `ServicioAusente`; el resto del inspector (GPS, actas) sigue funcionando.

## Sin dispositivo / con dispositivo
- **Sin dispositivo:** pasos 1, 2, 4, 5, 6; `PaxPrinterService` contra un fake del DAL; tests xUnit del mapeo de códigos (dos tablas separadas, R3 punto 14) y de la selección por trío; build en devcontainer (R2 punto 22); verificar en el emulador x86_64 que el trío PAX degrada a `NoSoportado`/`ServicioAusente` sin romper (R3 punto 20, R4 punto 11).
- **Con dispositivo:** ancho real en px (inicial **Inferido** 384, R3 punto 12; medir con un patrón, lo que sobra se recorta a la derecha), nombre del paquete NeptuneService, versión de WebView (R4 punto 4 — puede bloquear la app entera antes que la impresión), firma de las `.so` en Release, tiempos de `onSucc`/`onError`.

## Alternativas consideradas
- Elegir transporte por detección en runtime (si existe NeptuneService → PAX): más mágico, pero en un A910S con servicio ausente caería a Bluetooth y daría un error engañoso. Mejor trío explícito; la detección queda como diagnóstico.
- Overlay propio para PAX: duplica flujo; descartado.
- Selector de transporte para el usuario: innecesario, el trío ya identifica el equipo.

## Riesgos
- WebView vieja del A910S (R4 punto 3-4) puede impedir usar la app independientemente de la impresión.
- `armeabi` sin `armeabi-v7a` (R3 punto 4) y aab con x86: el transporte debe cargarse lazy para no romper en arranque.
- Nombre del paquete NeptuneService no confirmado.
- Renombrar `BluetoothPermissionResult` toca tests y overlay existentes (cambio interno, sin consumidores externos).

## Decisiones recomendadas
Ver lista del objeto estructurado (idéntica).
