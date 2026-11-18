# Informe de la comisión DevOps (feature 04, PAX A910S)

Las rutas son relativas a la librería `Libs/NugetOrg/PrintThermal_Motor_Maui` salvo que se indique otra cosa.

## 1. Propuesta

1. **Un paquete nuevo, `MotorDsl.Pax`, sólo para `net10.0-android`, que trae adentro el binding del jar NeptuneLite.** No se publica un paquete de binding aparte, así que se pasa de 8 a 9 paquetes y no a 10.
2. **CI: se empaqueta en el job `pack-platform` (macos-15), que ya instala `android` y `maui-android`** (`.github/workflows/cd-nuget.yml:108`, `:123-124`). Hay que tocar tres cosas:
   - agregar `Pax` a la lista de proyectos que empaqueta ese job (`:141`);
   - subir el conteo de 8 a 9 (`:184-185`) y corregir el comentario de `:3` y `:26-27`;
   - agregar `Pax` al final del bucle de push (`:193`).

   No hace falta ningún runner nuevo.
3. **Builds x86 o x64 (emulador y devcontainer):**
   - El paquete se compila igual, porque el jar es Java y compila en cualquier ABI.
   - Las `.so` sólo vienen para `arm64-v8a` y `armeabi` (R3 punto 3), así que en x86 la librería nativa falta en tiempo de ejecución.
   - Los tipos del binding se resuelven en forma perezosa (**Inferido**: lazy JNI). Si el transporte PAX carga el SDK de manera diferida y atrapa `Java.Lang.UnsatisfiedLinkError` o `Exception("LOAD DAL ERR")`, puede devolver `PrintErrorType.Connection` sin hacer caer la app.
   - Que la app quede en 4 RID (`<app>.csproj:54`) no se ve afectado.
   - **Inferido**: conviene declarar `<AndroidNativeLibrary>` sólo para `arm64-v8a` y `armeabi-v7a` (renombrando `armeabi`, R3 punto 4).
4. **Devcontainer y pruebas sin el dispositivo:**
   - Los tests `net10.0` siguen en el runner `<equipo-1>-dev`. La lógica que no depende de Android (detección de PNG, mapeo de códigos a `PrintError`) se puede escribir como fuente enlazada en los tests. Ya hay un antecedente: `MotorDsl.Tests.csproj:31-32` enlaza archivos de Bluetooth.
   - La compilación Android local se hace con `scripts/local-devcontainer/Dockerfile`, que trae `maui-android` y adb (`:4-8`).
   - **Inferido**: la escena Pay-Android (API 31, x86_64 con libndk_translation, R4 puntos 9-11) sirve para probar que la app **degrada** sin el servicio PAX, no para probar la impresión.
5. **Vía de conexión física del A910S: adb por USB en `<equipo-2>`, usando el adb del contenedor `local-devcontainer` o `/usr/bin/adb`.**
   - Requiere una sola regla udev nueva para el vendor de PAX, que se conoce con `lsusb` al enchufar el equipo (R4 punto 16). Ese cambio es de infraestructura del host y **necesita autorización del PO**.
   - No toca a `windows-<equipo-1>`.
   - Plan B sin cambiar infraestructura: enchufar el A910S en la PC del PO y usar `adb -H 203.0.113.30 -P 5037`, el mismo mecanismo que ya se usa con el g42 (R4 punto 17).
6. **PayDroid Tool (SDT) y el USB driver de Windows sólo hacen falta si NeptuneService no viene preinstalado** (`ide.txt:373`, `:388`). En ese caso se usa la PC Windows del PO, no `windows-<equipo-1>`.
   - Darle USB a `windows-<equipo-1>` obliga a cambiar su `docker-compose.yml` y reiniciarlo, y de su IIS dependen unas diez escenas (R4 puntos 12-15).
   - Se descarta salvo que el PO lo pida.

## 2. Alternativas evaluadas

- **Binding en un paquete separado (`MotorDsl.Pax.Binding`).** Llevaría el conteo a 10 y agregaría un orden de push más. Sólo conviene si otro consumidor quiere el SDK crudo. Hoy no hay ninguno (**Inferido**).
- **Empaquetar PAX en el runner self-hosted `<equipo-1>-dev`.** Ahorraría minutos de macOS, pero no está verificado que ese runner tenga el workload `android` (R1 punto 26). Además, instalarlo cambia la infraestructura. Se descarta.
- **Que `MotorDsl.Pax` declare también `net10.0-ios` o `net10.0` vacíos** para mantener la simetría con Bluetooth y Maui. No sirve: el SDK es sólo Android y sumaría superficie sin uso.
- **El binding dentro de la app (`<app>`) en lugar de la librería.** Evita tocar `cd-nuget.yml`, pero rompe el patrón de transportes registrados por DI (R1 punto 5) y no escala a otras apps.
- **Conexión física:**
  - USB a `windows-<equipo-1>`: se descarta por el impacto en las escenas IIS.
  - Un Windows aparte: sólo sirve para SDT.
  - adb por red del terminal: no hay evidencia de que PayDroid lo permita (R4 punto 18).

## 3. Riesgos

- **La firma PAX de las `.so` en Release.** Si el terminal exige que la app esté firmada o en una whitelist (código 103 `NOT_IN_WHITELIST`, R3 punto 14), el build Debug puede andar y el Release no.
- **R8/ProGuard.** Si no se agregan las reglas `-keep` (R3 punto 5) y la app tiene R8 activo en Release, `DALProxy` falla por reflexión. Hay que comprobar que el `ProguardConfiguration` viaje en el nupkg, con un `.targets` o con `AndroidLibrary` (**Inferido**).
- **`extractNativeLibs`.** Puede hacer falta (`ide.txt` ~423-437) y afecta al manifiesto de cada trío.
- **El conjunto de 9 paquetes queda atado a macOS.** Si falla el job macOS, no se publica ninguno, igual que hoy con Bluetooth y Maui.
- **Nada del flujo físico está probado.** El ancho en px, el API level y si NeptuneService está instalado dependen del equipo (R3 punto 21).

## 4. Qué se hace sin el dispositivo y qué lo necesita

**Sin el dispositivo:**
- el proyecto `MotorDsl.Pax`;
- el binding y `Metadata.xml`;
- el transporte con carga diferida;
- los tests `net10.0` del mapeo de errores y de la detección de PNG;
- los cambios en `cd-nuget.yml`;
- compilar el APK en `local-devcontainer`;
- probar la degradación en la escena Pay-Android.

**Con el dispositivo:**
- `lsusb` (vendor id) y la regla udev;
- `adb shell pm list packages | grep -i pax`;
- `getprop ro.build.version.sdk`;
- medir el ancho imprimible;
- la impresión real;
- el comportamiento de `getDal` sin el servicio;
- Release firmado y whitelist.

## 5. Cambios de infraestructura (no se aplican sin autorización del PO)

1. Una regla udev para el vendor de PAX en `<equipo-2>`, con impacto nulo en las escenas.
2. Si se descartan las dos vías anteriores, USB en `windows-<equipo-1>`, con impacto alto: reinicio y unas diez escenas IIS caídas mientras dure.
