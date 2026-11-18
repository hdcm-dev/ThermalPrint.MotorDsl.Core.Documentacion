# R2 — Relevamiento de la app `<app>` (impresión, GPS, trío inspector)

Fase de sólo lectura (2026-11-17). Rutas relativas a `<app>/` salvo indicación.
Toda afirmación lleva evidencia `ruta:línea` o comando. Lo inferido está marcado **Inferido**.

## 1. Ramas

- `git ls-remote --heads origin` → única rama remota: `d6b63f39b8a8… refs/heads/main`. Local: `main` en `d6b63f3 "arreglo bundle coredesa y desa"`.
- **No existe rama Issue699 en la app.** Coincide con la memoria: Issue699 refiere a `<app-web>` (web), no a la app.

## 2. Flujo web → nativo de impresión (no hay JS bridge)

No hay `AddJavascriptInterface` ni puente JS para imprimir; el portal se comunica **navegando a una URL-comando** que la app intercepta en `Navigating`:

1. `<app>/Pages/MainPage.xaml.cs:131` `Navegador_Navigating` → `_urlManagerService.GetParametros(...)` (`:152`) → `EjecutarComandoAsync(...)` (`:177`).
2. `<app>/Services/UrlManagerService.cs:229` `IsPrint = e.Url.Contains("action=print", …)`.
3. `UrlManagerService.cs:107-116`: si `IsPrint`, toma `urlActionPrint` de la query (`:111`) y llama `await _printCoordinator.ImprimirAsync(urlApi)` (`:116`). Ejemplo de URL en el comentario `:109`: `https://<host-publico>/ImpresoraTunnel?action=print&urlActionPrint=https%3A%2F%2F<host-publico>%2FPrint%2FPrintActaById%3Fid%3D…`.
4. Comentario `:113-115`: "Nada de lo que pase aca vuelve a la web" → **no hay respuesta de resultado al portal**.
- `ImpresoraTunnel` sólo aparece en comentarios de la app (`grep -rn -i tunnel` → `UrlManagerService.cs:109,124,173,240`); la página vive en el portal web (fuera de este relevamiento).

## 3. GPS (mismo mecanismo de URL-comando)

- `UrlManagerService.cs:224` `IsCoordenadas = Url.Contains("Coordenadas=Coordenadas")`; `:71-77` redirige con coordenadas o las inyecta al DOM (`<Org>LocationsService.InjectCoordenadasAlDOMAsync`).
- `Services/<Org>LocationsService.cs:134` `_gpsDevice.TakeLocation(page, modo)`; `:203` log `[GPS→DOM] inject` (inyección vía `EvaluateJavaScriptAsync`). **Inferido**: el GPS de un PAX A910S entra por la misma vía de MAUI Essentials, sin cambio específico.

## 4. PrintCoordinator (`<app>/Services/PrintCoordinator.cs`)

- Constructor `:38` recibe `IDocumentEngine` (MotorDsl) e `IPrinterService`; crea el `PrinterOverlayViewModel` (`:44`).
- `ImprimirAsync(string urlDocumento)` `:55`: GET del documento con `HttpClient`, timeout 30 s (`:26`, `:115`), valida contrato `PrintDocument` con `Root.Type` (`:118-124`).
- **Perfil de dispositivo fijo en código** `:90-93`: `new DeviceProfile("58HB6", 32, "escpos-bitmap")`, `supports_bitmap=true`, `bitmap_max_width_px=320`, `bitmap_binarization_threshold=128`. Luego `_engine.Render(json, profile)` `:95` y delega al overlay `:101`.
- Comentario `:100`: "Requiere los permisos Bluetooth declarados en el AndroidManifest del módulo" (ver §8: **no están declarados**).
- Punto de extensión para PAX: aquí se decide perfil (58HB6 BT). **Inferido**: para A910S habría que elegir perfil/transporte según dispositivo en este punto o en el overlay.

## 5. Services/Printing

- `IPrinterService.cs:11-44`: `IsSupported`, `EnsurePermissionsAsync`, `DiscoverAsync`, `GetDefaultIfPresent`, `ConnectAsync(PrinterDevice)`, `SendAsync(byte[])`, `SaveDefault/ClearDefault`, `GetAlias/SetAlias`, `OpenAppSettings`, `OpenBluetoothSettings`. Doc `:13` "BT Classic SPP: sólo soportado en Android".
- `PrinterService.cs:17-22` envuelve `MotorDsl.Printing.IThermalPrinterService`.
  - `:25-30` `IsSupported` = `true` sólo `#if ANDROID`.
  - `:66-109` `DiscoverAsync`: chequea `BluetoothManager.Adapter` (`:75-78`), `adapter.IsEnabled` (`:80`), `BLUETOOTH_CONNECT` en API≥31 (`:86-92`), y luego `_printer.DiscoverDevicesAsync(kind: "bluetooth")` **hardcodeado** (`:97`).
  - `:136-152` `SendAsync` → `_printer.SendBytesAsync(bytes)` (bytes ESC/POS ya renderizados).
  - Predeterminada en `Preferences` (`:14-15`, `:154-169`).
- `BluetoothPermissions.cs:9-21`: permiso MAUI custom; API≥31 pide `BLUETOOTH_SCAN` + `BLUETOOTH_CONNECT`; antes `ACCESS_FINE_LOCATION`.
- **Inferido**: todo el servicio asume transporte Bluetooth (adapter, permisos, kind "bluetooth"); una impresora integrada PAX (SDK PayDroid, sin BT) requiere un camino que saltee esos chequeos.

## 6. PrinterOverlayViewModel y vista

- `<app>/ViewModels/PrinterOverlayViewModel.cs:19` hereda `StatusOverlayViewModel`. `ImprimirAsync(RenderResult)` `:104`: valida `render.Output is byte[]` (`:108`), `EnsurePermissionsAsync` (`:126`), `BuscarYImprimirAsync` (`:138`, usa `DiscoverAsync` `:141`; predeterminada o único dispositivo `:149-150`, si no selector `:206`), `ConectarEImprimirAsync` (`:220-233`), `EnviarAsync` (`:268-271`).
- Vista: no hay vista propia; se usa el control genérico `Controls/StatusOverlayView.xaml` (`x:DataType="vm:StatusOverlayViewModel"`, `:6`), instanciado en `Pages/MainPage.xaml:36` con `BindingContext="{Binding PrintOverlay}"`; `ViewModels/MainPageViewModel.cs:304` `PrintOverlay => _print.Overlay`.

## 7. MauiProgram (registro MotorDsl)

- `<app>/MauiProgram.cs:66-75`: `.Services.AddMotorDslEngine().AddProfiles(p => { thermal_58mm(32,"escpos-bitmap"); a4-pdf(80,"pdf"); pdf(48,"pdf") }).AddMotorDslMaui().Services.AddBluetoothPrinterTransport();`
- `MauiProgram.cs:243-244`: `IPrinterService→PrinterService` y `PrintCoordinator` singleton.
- Nota: el perfil registrado `thermal_58mm` no es el que usa `PrintCoordinator` (`"58HB6"` creado ad hoc, `PrintCoordinator.cs:90`).
- Sólo un transporte registrado (Bluetooth). **Inferido**: el soporte PAX implicaría un `AddPaxPrinterTransport()` (o similar) en la librería y su registro aquí.

## 8. Manifiestos y permisos — hallazgo

- `grep -rli bluetooth Recursos <app>/Platforms Utils` → **sin resultados**: ningún AndroidManifest (ni de Recursos ni de Platforms ni de la plantilla trío-prueba) declara `BLUETOOTH*`.
- Trío dev: `Recursos/AMB_DESARROLLO/MUN_<desarrollo>/MOD_<APP>_INSPECTOR/Resources/Android/AndroidManifest.xml:3` `package="com.<org>.coredesa.inspector"`, permisos `:20-47` (INTERNET, LOCATION, CAMERA, CALL_PHONE, POST_NOTIFICATIONS…), `:65` `minSdk 25 / targetSdk 36`.
- Trío prod: `Recursos/AMB_PRODUCCION/MUN_<cliente>/MOD_<APP>_INSPECTOR/Resources/Android/AndroidManifest.xml:3` `package="com.<org>.<cliente>.inspector"`, mismos permisos y SDK (`:65`).
- `<app>/Platforms/Android/AndroidManifest.xml:3` `package="com.<org>.coredesa.ciudadano"` (se pisa en build con el del trío, §10).
- **Inferido**: o MotorDsl.Bluetooth aporta los permisos por merge de manifiesto del paquete, o el flujo BT falla en runtime (`RequestAsync` de un permiso no declarado devuelve Denied). No verificado en esta fase; revisar el .nupkg de MotorDsl.Bluetooth 1.0.17. Para PAX, el SDK PayDroid puede requerir permisos propios en este manifiesto.

## 9. Config.cs (trío inspector)

- `<app>/Config.cs:94-104` región `<APP>` INSPECTOR: `MUN_<cliente> && AMB_PRODUCCION && MOD_<APP>_INSPECTOR` → `https://<host-publico>/<cliente>/Login…` (`:97`); `MUN_<desarrollo> && AMB_DESARROLLO && MOD_<APP>_INSPECTOR` → `https://<host-publico>/Login…` (`:101`).
- `Config.cs:246-256` claves del servicio de notificaciones (`<servicio-privado>`) por trío inspector.
- `Config.cs:367-369` refresco desactivado para `MOD_<APP>_INSPECTOR`; `:393-394` `atrasProlijo = true`.
- No hay ninguna bandera de impresión por trío en Config.cs (grep de "print" no la muestra). **Inferido**: el switch "PAX sí/no" no existe hoy.

## 10. WhiteLabel.props y trío

- `WhiteLabel.props:11-16` precedencia: `-p:` CLI > `WhiteLabel.local.props` > defaults. Defaults (`:65-67`): `MUN_<desarrollo> / AMB_DESARROLLO / MOD_<APP>_CIUDADANO`. `:98` el trío entra como `DefineConstants`. Interruptores extra: `EnvCore`, `Escenario` (ESC_EMPRESA/ESC_LOCAL), `Refresco`.
- csproj `:323` target `CopiarRecursos` copia los recursos del trío en local, `Condition="'$(GITHUB_ACTIONS)' != 'true'"`.

## 11. csproj

- `<app>/<app>.csproj:17` `net10.0-android` (+ iOS sólo en macOS `:18`); `:28` `ApplicationId com.<org>` (el package real lo fija el manifiesto del trío); `:35` minSdk Android 25.
- `:54` `RuntimeIdentifiers android-arm;android-arm64;android-x86;android-x64`; `:61`/`:80` `AndroidCreatePackagePerAbi False`; `:59`/`:81` formato `aab`. **Inferido**: incluye `android-arm`(armeabi-v7a), relevante si el SDK PAX trae `.so` sólo de 32 bits.
- Paquetes MotorDsl 1.0.17 (NuGet, no ProjectReference, comentario `:212`): Core, Parser, Rendering, Extensions, Printing.Abstractions, Bluetooth, Maui (`:214-220`).
- Firma: Release `:71-75` keystore `..\..\<app>.Certificados\android\my-upload-key.keystore` con pass por variables de entorno; Debug `:100-105` `Firma-Debug/debug.keystore` pass `android`.

## 12. Workflows

- `.github/workflows/cd-main-android-build.yml`: `workflow_dispatch` con `package_name` (`:44-49`); opciones incluyen `com.<org>.<cliente>.inspector` (`:71`) y `com.<org>.coredesa.inspector` (`:72`). El trío se deriva con `bash ci/resolver-trio.sh android "$PACKAGE_NAME"` (`:285-294`) y viaja como `TRIO_PROPS=-p:Municipio… -p:Ambiente… -p:Modulo… -p:Refresco…` (`:294`) a cada `dotnet publish` (`:885-895`). Runner `[self-hosted, ci-hdcm]` (`:262`). Copia del manifiesto y AppIcon del trío al proyecto `:398-421`.
- `.github/workflows/cd-dev-android-trio-prueba.yml`: trío de prueba con plantilla `Utils/trio-prueba/AndroidManifest.xml` (`:5`) y `TRIO_PROPS` fijo a `MOD_<APP>_CIUDADANO` (`:131`).

## 13. Devcontainer

- `.devcontainer/Dockerfile:9` `FROM mcr.microsoft.com/dotnet/sdk:10.0`; SDK Android en `/opt/android-sdk` (`:30-47`); `dotnet workload install maui-android` (`:58`).
- `.devcontainer/devcontainer.json`: monta la carpeta padre en `/work` (para alcanzar `<app>.Certificados`), `--privileged` + `/dev/bus/usb` para adb.
- `.devcontainer/dev.sh:103-104` build: `dotnet build … -c Debug -f net10.0-android -p:AndroidPackageFormat=apk ${TRIO_ARGS}`.
- `nuget.config` sin fuentes propias: MotorDsl se restaura de nuget.org; `<servicio-privado>` del feed de la org vía config de usuario (comentario del archivo).

## 14. Puntos de impacto para PAX A910S (resumen, **Inferido**)

1. `MauiProgram.cs:66-75`: registrar transporte PAX de la librería.
2. `PrintCoordinator.cs:90-93`: perfil fijo 58HB6 → seleccionar perfil de la A910S.
3. `PrinterService.cs:68-97` / `BluetoothPermissions.cs`: chequeos BT y `kind:"bluetooth"` fijos.
4. Manifiesto del trío `com.<org>.coredesa.inspector`: permisos del SDK PAX (y verificar los BT ausentes).
5. csproj `:214-220`: nueva versión de paquetes MotorDsl (+ paquete PAX si se separa).
