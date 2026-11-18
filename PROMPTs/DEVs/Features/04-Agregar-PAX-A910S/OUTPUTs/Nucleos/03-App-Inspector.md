# Núcleo 03 — App `com.gdi.coredesa.inspector` (GDA.Core.APP)

Trazabilidad: T7, T8, T9, T10. Depende de: N01, N02 (paquete publicado), N07 (versión NuGet). Lo consumen: N05, N06.

## Rama
**`main`**: es la única rama remota (`git ls-remote --heads origin` → `d6b63f3 refs/heads/main`, R2 §1); no existe Issue699 en la app (Issue699 es de la web). Trabajo en ramas nuevas desde `main` con PR.

## Decisión
1. **T7 permisos Bluetooth:** ningún manifiesto los declara (`grep -rli bluetooth Recursos GDA.Core.APP/Platforms Utils` vacío, R2 §8). Se agregan `BLUETOOTH_SCAN`/`BLUETOOTH_CONNECT` (API≥31) y `BLUETOOTH`/`BLUETOOTH_ADMIN` con `maxSdkVersion=30` en coredesa y msm inspector (`Recursos/AMB_DESARROLLO/.../MOD_GDI_INSPECTOR/Resources/Android/AndroidManifest.xml`, `Recursos/AMB_PRODUCCION/MUN_MSM/...`). Antes, revisar si el nupkg MotorDsl.Bluetooth 1.0.17 ya los mergea (R2 §8 **Inferido**). PR independiente y previo.
2. **T8 selección por configuración del trío:** interruptor de build `-p:Impresora=BLUETOOTH|PAX` (default BLUETOOTH) que agrega `IMPRESORA_PAX` a `DefineConstants`, con el mismo patrón que `Refresco` (`WhiteLabel.props:101`), pasado por los workflows como `TRIO_PROPS` (`cd-main-android-build.yml:294`). `Config.cs` expone `Impresora` y el perfil. Se elimina el `DeviceProfile("58HB6",…)` fijo (`PrintCoordinator.cs:90-93`): el coordinador pide el perfil a `IDeviceProfileProvider` por nombre; se registran `bt_58hb6` (los valores actuales: 32, escpos-bitmap, 320 px, umbral 128) y `pax_a910s` en `AddProfiles` (`MauiProgram.cs:66-75`).
3. **T9 generalización:** `IPrinterService.EnsurePermissionsAsync` devuelve `PrinterReadiness { Ok, Denegado, Bloqueado, ServicioAusente, NoSoportado }` y se agrega `Kind`. `BluetoothPrinterService` (el actual `PrinterService` renombrado) y `PaxPrinterService` (`#if ANDROID`, sin chequeo BT, `Discover` = una impresora integrada). El overlay (`PrinterOverlayViewModel.cs:104-271`) usa la rama "impresora única" existente (`:149-150`), sin vista nueva; se neutralizan los textos "por Bluetooth" (`:120,:180`). Códigos nuevos en `PrinterErrorCatalog`: `PRN-HW-HEAT`, `PRN-HW-BUSY` (un reintento automático corto), `PRN-HW-BATT`, `PRN-PAX-SVC` (sólo "Cerrar" + "Avisá a soporte"); `PRN-HW-PAPER` reutiliza "Ya cargué papel — Reintentar" (`PrinterOverlayViewModel.cs:283-293`; corregido en Verificación 1). Mapeo por la causa (enum) de N01, no por texto.
4. **T10 x86:** los `RuntimeIdentifiers` incluyen x86/x64 (`GDA.Core.APP.csproj:54`) y el SDK sólo trae arm (R3 §2). El transporte degrada a `Connection` (N01 §6). Para el candidato que va al A910S se genera APK sólo `android-arm64;android-arm` (pos-pax); el aab de tienda no cambia. Permiso `com.pax.permission.PRINTER` y `android:extractNativeLibs="true"` en `<application>` sólo cuando `IMPRESORA_PAX` (`getDal` busca las `.so` en `nativeLibraryDir`, N01 §6; guía del IDE `ide.txt` ~423-437) [Verificacion-3 H3].
5. **Simulador:** con `IMPRESORA_PAX` y `-p:PaxModo=SIMULADO` se registra el modo simulado (para emulador Pay-Android y g42); nunca en Release de tienda.

## Alternativas descartadas
- **Detección en tiempo de ejecución (ux-flujo-ui):** el prompt exige "transporte y perfil elegidos por configuración del trío"; además, en un A910S sin NeptuneService caería a Bluetooth con un error engañoso (mobile-designer). Queda sólo como diagnóstico en `PRN-PAX-SVC`. El costo (un APK por equipo) se acota con un interruptor, no con un trío nuevo.
- Overlay propio PAX, selección manual del transporte: duplican UI.

## Tareas
- Sin dispositivo: T7, T8, T9, T10; build en el devcontainer de la app (`.devcontainer/dev.sh:103-104`); tests de la app; prueba en emulador Pay-Android (N05/N06).
- Con dispositivo: D2, D3, D4 (firma Leandro).

## Criterios de aceptación
CA-03.1 trío por defecto se comporta igual que hoy (regresión BT en g42). CA-03.2 con `IMPRESORA_PAX` el overlay no pide permisos BT ni muestra selector. CA-03.3 en emulador x86_64 sin servicio: overlay muestra `PRN-PAX-SVC`, la app sigue viva. CA-03.4 manifiestos con permisos BT. CA-03.5 PR verde (build + tests).

## Evidencia
../Bitacoras/04-Agregar-PAX-A910S/Relevamiento/R2-app.md §1-14 · ../Bitacoras/04-Agregar-PAX-A910S/Mesa/informe-mobile-designer.md · ../Bitacoras/04-Agregar-PAX-A910S/Mesa/informe-ux-flujo-ui.md
