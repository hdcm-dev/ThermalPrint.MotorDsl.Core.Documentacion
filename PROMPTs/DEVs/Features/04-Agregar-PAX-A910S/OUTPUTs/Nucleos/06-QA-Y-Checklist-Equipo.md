# Núcleo 06 — Estrategia de prueba y checklist del equipo

Trazabilidad: T5, D1, D2, D3, D4. Depende de: N01-N05.

## Niveles (decisión, de informe-qa)
- **N1 unitarios (net10.0):** fake `IPaxPrinterDevice`; firma PNG→Protocol; ambas tablas de códigos; servicio ausente; callback con timeout; DI junto a Bluetooth; ancho del perfil. Base: `FakeTransport` (`src/MotorDsl.Tests/TestFakes.cs:16-42`).
- **N2 simulador:** goldens PNG del acta como prueba de integración fuera de `MotorDsl.Tests` (sample/devcontainer), imágenes en `Images/` junto al md que las use.
- **N3 emulador Pay-Android:** app no se cae y muestra `PRN-PAX-SVC`; regresión BT; PNG del simulador por `adb pull`.
- **N4 equipo físico (checklist, no se da por cerrado sin el A910S):**
  1. `adb devices`; `getprop ro.build.version.sdk`, `ro.product.cpu.abilist`, versión PayDroid.
  2. **WebView:** `adb shell dumpsys webviewupdate`, `pm list packages -f | grep -i webview`, `dumpsys package <pkg> | grep versionName`. Bloqueante: ≥94 mínimo (`static{}`), ≥119 a salvo (`Promise.withResolvers`) (`SCN-PAY:264-265,315` para 94; `SCN-PAY:319,342` para `Promise.withResolvers`/119; cita completada en Verificación 1).
  3. NeptuneService: `pm list packages | grep -i neptune` (nombre `com.pax.ipp.neptune` **Inferido**).
  4. GMS/GPS: `pm list packages | grep -i gms`; prueba de coordenadas.
  5. Ticket de calibración (regla 576 px) → ancho real.
  6. Acta real vs PNG del simulador; estados reales (sin papel, tapa, calor); tiempo de impresión; diálogo del permiso PRINTER; botón Atrás.
  7. Release con ProGuard/R8 y firma PAX (Leandro): `DALProxy` carga; código 103 whitelist; `dumpsys package com.gdi.coredesa.inspector | grep -i extractNativeLibs` y `run-as … ls` del `nativeLibraryDir` con `libDeviceConfig.so` presente [Verificacion-3 H3].

## Criterios (CA1..CA8 de informe-qa, consolidados)
CA1 tests verdes; CA2 todos los códigos mapeados; CA3 simulador cubre estados; CA4 emulador sin crash; CA5 sin regresión BT; CA6 WebView ≥119 o riesgo aceptado por escrito por el PO; CA7 acta real legible al ancho medido; CA8 Release firmado imprime.

## Evidencia
../Bitacoras/04-Agregar-PAX-A910S/Mesa/informe-qa.md · ../Bitacoras/04-Agregar-PAX-A910S/Relevamiento/R4-escenas-infra.md §2 · ../Bitacoras/04-Agregar-PAX-A910S/Relevamiento/R3-pax-sdk.md §4-6, §10
