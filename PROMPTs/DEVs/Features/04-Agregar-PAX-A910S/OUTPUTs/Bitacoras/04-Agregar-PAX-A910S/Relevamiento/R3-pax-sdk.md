# R3 — Relevamiento del material PAX (SDK NeptuneLite, A910S)

Fecha: 2026-11-17. Fase de sólo lectura. Abreviaturas de rutas:

- `MAT` = `Ng/Ng-Media/Instaladores/SDK-PayDroid-A910S`
- `SDK` = `MAT/000. Herramientas paydroid/sdk/libs + API doc/NeptuneLiteApi_V4.15.00_20250606.zip`
- `EXT` = `/vm/claude-tmp/claude-1000/pax-sdk-extract` (extracción temporal del zip, fuera del repo)
- Las líneas `IPrinter.java:N` son las del código fuente que trae el javadoc en `EXT/doc/en/src-html/com/pax/dal/IPrinter.html`.

## 1. Inventario del material

| Pieza | Evidencia |
|---|---|
| README del material (lo escribió una sesión anterior): describe el SDK, NeptuneService, la firma vía Leandro y el análisis de la APK firmada | `MAT/README.md` |
| SDK NeptuneLite 4.15.00 (zip de 45 MB, 1117 entradas) | `unzip -l SDK` → `45103306 … 1117 files` |
| NeptuneService 3.10.02 (APK) | `MAT/000. Herramientas paydroid/sdk/service/NeptuneService V3.10.02 20250109.apk` |
| Guía del IDE 1.0.4 y Paydroid_Training (PDF) | leídos con `pdftotext -layout` |
| PayDroid Tool SDT y driver USB (zip, sólo Windows según el README) | no se abrieron |
| `doc_tool_sdk_ paydroid-Pax/` | el README dice que es un duplicado (mismos MD5); no lo volví a verificar |
| `equipo-A910S.jpg`: 630x1190, foto del frente del equipo con la marca "PAX A910S" | `file` + vista de la imagen. No muestra el papel ni el rótulo de la impresora |
| `Libs/NugetOrg/PrintThermal_Motor_Maui-Media` | sólo tiene `COMPILACIONES/`. **El material PAX no está ahí, está en `MAT`** (`ls -la`) |

## 2. Contenido del zip NeptuneLiteApi (sin la documentación)

```
jniLibs/NeptuneProguardRules.pro   jniLibs/readme.txt
jniLibs/arm64-v8a/ libdecoder_jni, libDeviceConfig, libHDSD, libiconv, libIGLBarDecoder, libpaxcanvas, libZBarDecoder
jniLibs/armeabi/   libDCL, libdecoder_jni, libDeviceConfig, libHDSD, libiconv, libIGLBarDecoder, libZBarDecoder
libs/NeptuneLiteApi_V4.15.00_20250606.jar   (821031 bytes)
doc/en/…, doc/zh/…                          (javadoc)
```

- **ABIs:** sólo `arm64-v8a` y `armeabi`. **No hay** x86 ni x86_64, ni carpeta `armeabi-v7a` (`unzip -l`).
- **Asimetrías:** `libpaxcanvas.so` sólo está en arm64-v8a y `libDCL.so` sólo en armeabi (`unzip -l`). El README de `MAT` no menciona `libpaxcanvas`.
- **Única `.so` obligatoria:** `libDeviceConfig.so`. Las demás son del ScanCodec (`EXT/jniLibs/readme.txt`). `libpaxcanvas` no aparece en esa lista. **Inferido:** sirve para el render de canvas o bitmap; no consta como obligatoria.
- **Guía del IDE sobre el ABI:** si el proyecto no reconoce la `.so`, renombrar `armeabi` a `armeabi-v7a` con `abiFilters "armeabi-v7a"` y agregar `android:extractNativeLibs="true"` en el manifiesto, cosa que suele pasar con sdk > 23 (`ide.txt`, líneas ~423-437).
- **El jar:** 264 entradas; 245 clases en `com/pax/dal`, 2 en `com/pax/neptunelite` y 1 en `com/pax/nep`. Bytecode de Java 8: cabecera `cafebabe 0000 0034`, major 52. No trae `AndroidManifest`, así que **el SDK no declara minSdk**.

## 3. ProGuard

Contenido de `EXT/jniLibs/NeptuneProguardRules.pro`, idéntico al de la guía del IDE (`ide.txt` ~457-470):
```
-keep class com.pax.dal.** { <fields>; <methods>; }
-keep class com.pax.nep.** { <fields>; <methods>; }
-keep class com.pax.neptunelite.** { <fields>; <methods>; }
```
Es obligatorio, porque `NeptuneLiteUser` carga clases por reflexión (`com.pax.dal.impl.DALProxy`, ver §5). En .NET hay que pasarlo como `@(ProguardConfiguration)` si se usa R8. **Inferido:** es el ítem estándar de .NET Android.

## 4. `com.pax.dal.IPrinter`: firmas exactas

Javadoc de la interfaz: si la verificación de permisos está activa, hay que declarar `com.pax.permission.PRINTER` en el manifiesto (`IPrinter.java:27-28`). El Training la incluye en su lista de permisos (`tr.txt:272`).

| Firma | Línea | Nota |
|---|---|---|
| `void init() throws PrinterDevException` | 36 | |
| `void fontSet(EFontTypeAscii, EFontTypeExtCode)` | 94 | |
| `void spaceSet(byte wordSpace, byte lineSpace)` | 123 | |
| `void step(int pixel)` | 146 | avance de papel en px |
| `void printStr(String str, String charset)` | 178 | buffer de 2048 bytes como máximo (154/162) |
| `void printBitmap(Bitmap bitmap)` | 188 | |
| `void printBitmapWithMonoThreshold(Bitmap, int grayThreshold)` | 200 | umbral 0-255 |
| `int start() throws PrinterDevException` | 260 | **sincrónica**; devuelve el estado. Total de puntos < 30000 (220) |
| `int getStatus() throws PrinterDevException` | 299 | |
| `void leftIndent(int indent)` | 314 | 0~300 |
| `int getDotLine()` | 323 | "current printed dot line": **no es el ancho** |
| `void setGray(int level)` | 352 | 1 = default; 3/4 = papel doble capa; 50~500 = % del default |
| `void doubleWidth/doubleHeight(boolean, boolean)`, `void invert(boolean)` | 368/382/402 | |
| `void cutPaper(int mode)`, `int getCutMode()` | 412/434 | getCutMode -1 = sin cuchilla |
| **`void print(Bitmap bitmap, IPinterListener listener)`** | **447** | asíncrona; no se mezcla con el resto salvo `setGray`; hace init antes y después; listener null = sin callback (438-445). **No declara `throws`** |
| `void print(Bitmap bitmap, int cutMode, IPinterListener listener)` | 464 | desde V2.03.00 |
| `interface IPinterListener { void onSucc(); void onError(int errCode); }` | 470/475/514 | el nombre está mal escrito en el SDK, "Pinter" |
| `setFontPath(String)`, `presetCutPaper(int)` (V3.22), `setPrinterSize/getPrinterSize` ("currently supported by SK700"), `isLowPowerPrintEnabled/enableLowPowerPrint`, `setAlignMode(short)` 0/1/2 | 525-594 | |
| `printColorBitmap[WithMonoThreshold]`, `setColorGray` (V4.09) | 609/622/637 | si el bitmap supera el ancho de la impresora, **se recorta a la derecha** (601/616) |

### Códigos de retorno de `start()`, `getStatus()` y `onError(errCode)`

Las líneas 243-254, 282-293 y 498-509 dan la misma lista:

| Código | Significado |
|---|---|
| 0 | Success |
| 1 | Printer is busy |
| 2 | Out of paper |
| 3 | Data packet format error |
| 4 | Printer malfunctions |
| 8 | Over heats |
| 9 | Voltage too low |
| -16 | Printing unfinished |
| -6 | Cut jam (sólo E500/E800) |
| -5 | Cover open (E500/E800, SK600/SK800 en getStatus) |
| -4 | No font library |
| -2 | Data package too long |

## 5. `NeptuneLiteUser.getDal` y la dependencia de NeptuneService

Fuente: `EXT/doc/en/src-html/com/pax/neptunelite/api/NeptuneLiteUser.html`.

- `public static synchronized NeptuneLiteUser getInstance()` (l.55)
- `public synchronized IDAL getDal(Context context) throws Exception` (l.70). También existe `getDalWithProcessSafe(Context)`, desde V3.22.00 (l.86).
- **Cómo funciona `getDal`:** escribe un `nepcore.dex` embebido en `filesDir`, lo verifica con SHA-256, lo carga con `DexClassLoader` usando `nativeLibraryDir` como ruta de las librerías, instancia `com.pax.dal.impl.DALProxy` y luego borra el archivo (l.103-142).
- **Cualquier fallo** termina en `throw new Exception("LOAD DAL ERR")`, una `java.lang.Exception` genérica (l.134-136). Las otras variantes son `"DEX INTEGRITY CHECK ERR"` y `"GET FILE HASH ERR"`, pero el catch las vuelve a envolver como `LOAD DAL ERR`.
- **La comprobación del servicio está comentada:** `// NeptuneLiteProvider neptune = Utils.checkNeptuneLiteService(context);` (l.71). **El SDK no detecta explícitamente que falte NeptuneService en `getDal`.**
- **Inferido:** si falta el servicio, el error aparece después, al usar el periférico, como `PrinterDevException` con `DEVICES_ERR_CONNECT(99, "connect error")` (RPC I/O). Ver `EPrintDevException`, l.33. No lo verifiqué en el equipo.
- **Detección en la app (propuesta, Inferido):**
  1. `PackageManager.getPackageInfo("com.pax.ipp.neptune")`. El nombre del paquete sale de los strings del manifiesto binario de la APK (`unzip -p … AndroidManifest.xml | strings -el` → `com.pax.ipp.neptune`, `com.pax.neptunelite.service.NeptuneLiteService`, `…provider.NeptuneLiteProvider`). **Hay que confirmarlo con `adb shell pm list packages | grep pax` en el equipo**, porque no hay aapt para leer el atributo `package`.
  2. Envolver `getDal` y la primera llamada en try/catch.
- **Preinstalación:** la guía dice que NeptuneService "usually, it has been preloaded" (`ide.txt:373`). Si no está, se instala con PayDroid Tool (`ide.txt:388`).

## 6. Excepciones

- `PrinterDevException extends AGeneralException` (MODULE = `"PRINTER"`). Constructores: `(EPrintDevException)` y `(int code, String errMsg)`.
- `AGeneralException extends Exception`. Expone `getErrModule()`, `getErrCode()` y `getErrMsg()`, y define `CUSTOMER_ERRCODE_BASE = 10000`.
- Códigos de `EPrintDevException`:

| Código | Constante |
|---|---|
| 97 | UNEXPECTED |
| 98 | INVALID_ARGUMENT |
| 99 | CONNECT |
| 100 | NO_SUPPORT |
| 101 | NO_PERMISSION |
| 102 | DISABLED |
| 103 | NOT_IN_WHITELIST |
| 1 | BUSY |
| 2 | OUT_OF_PAPER |
| 3 | DATA_PACKET |
| 4 | PRINTER_PROBLEMS |
| **5** | **OVER_HEATING** |
| 6 | UNFINISHED |
| 7 | LACK_OF_FONT |
| 8 | TOO_LONG |
| 9 | VOLTAGE_TOO_LOW |
| 10 | CUT_PAPER |
| 11 | COVER_OPEN |
| 12 | CUTTER_JAM |
| 13 | UNSUPPORTED_ENCODING |
| 14 | FONT_FORMAT |
| 15 | FONT_NOT_EXIST |

- **Atención: la numeración de la excepción no coincide con la de `getStatus`.** En la excepción, sobrecalentamiento es 5 y "too long" es 8. En `getStatus`, sobrecalentamiento es 8 y "too long" es -2. Hay que mapear las dos tablas por separado.

## 7. minSdk

- **No está documentado en el material.** El jar no trae manifiesto. Los PDFs no lo mencionan (`grep -i minSdk` sobre ide.txt y tr.txt no da resultados).
- La APK de NeptuneService sí declara `minSdkVersion` y `targetSdkVersion`, pero los valores están en el AXML binario y no los pude leer sin aapt.
- **Inferido:** la API usa sólo `android.graphics.Bitmap`, `Context` y `DexClassLoader`, así que no impone un mínimo alto. El límite real lo pone la versión de PayDroid del equipo, que está pendiente según `MAT/README.md`, "Pendientes".

## 8. Ancho del papel en px

- **El material no lo documenta.** `grep 384` en `doc/en/com` sólo aparece en clases ajenas a la impresora (IDalCommManager, ITypeA, PiccPara, ModemParam). Los PDFs tampoco lo dan.
- `getDotLine()` no es el ancho (l.317-323). `getPrinterSize` es sólo para SK700.
- El README de `MAT` lo da como "estimado 384 px para 58 mm, a confirmar". Ese dato es **Inferido** y no tiene fuente PAX en el material.
- **Cómo medirlo:** imprimir en el equipo un bitmap de prueba más ancho que 384, porque lo que excede se recorta a la derecha (l.601).

## 9. Lo que hace falta para el binding .NET Android del `.jar` (Inferido, conocimiento de la plataforma; no hay binding previo en la app)

`grep AndroidLibrary|AndroidJavaLibrary|EmbeddedJar` en los csproj de GDA.Core.APP no encuentra nada.

1. **Proyecto de binding.** Crear un proyecto `net9.0-android` (o el TFM de la app) con `<AndroidLibrary Include="NeptuneLiteApi_V4.15.00_20250606.jar" />`. Genera los wrappers C#. Es Java 8, así que el bytecode es compatible.
2. **`.so` nativas.** Agregarlas como `<AndroidNativeLibrary Include="…/arm64-v8a/libDeviceConfig.so" Abi="arm64-v8a" />` y la de armeabi con `Abi="armeabi-v7a"`, siguiendo el renombre que indica la guía del IDE. Como mínimo hace falta `libDeviceConfig`. **Inferido:** conviene incluir también `libpaxcanvas` (arm64).
3. **`Transforms/Metadata.xml`.** Para recortar el binding a lo necesario (`com.pax.dal`, `IDAL`, `IPrinter`, `exceptions`, `entity`, `com.pax.neptunelite.api`) y quitar lo que no compile. 245 clases es mucho; lo esperable es que algunas fallen (**Inferido**).
4. **Alternativa sin binding completo:** llamar por JNI (`Android.Runtime.JNIEnv`) o con un wrapper Java mínimo dentro de un `.aar` propio.
5. **ProGuard.** `<ProguardConfiguration Include="NeptuneProguardRules.pro" />`.
6. **Manifiesto.** `com.pax.permission.PRINTER` y quizá `android:extractNativeLibs="true"`.
7. **Sin x86.** Las `.so` y la DAL sólo funcionan en el equipo. El código tiene que degradar con elegancia en el emulador, o el transporte PAX tiene que ir aislado (README de `MAT`).

## 10. Abierto, a verificar en el equipo

Ancho real en px y dpi · paquete exacto de NeptuneService y si está preinstalado · versión de PayDroid y API level · comportamiento real de `getDal` sin el servicio · si la verificación de permisos está activa · firma PAX de las `.so` en modo Release (README de `MAT`).
