# Expediente 0002 — Conexión física del PAX A910S

**Caso:** cómo se conecta el A910S (llega en modo Debug) para adb y, si hace falta, PayDroid SDT.
**Estado:** decisión de la mesa tomada; **cambio de infra pendiente de autorización del PO (P1)**; nada aplicado.

## Actuaciones
| Folio | Tipo | Contenido |
|---|---|---|
| 1 | presentación | Idea original: USB al Windows dockerizado con SDT (prompt) |
| 2 | informe | R4 §3-4: `windows-<equipo-1>` sin USB (`{dir-de-trabajo}/contenedores/windows-<equipo-1>/docker-compose.yml`, devices kvm/tun); udev sólo Motorola `22b8`; adb 29.0.6 en `<equipo-2>`; patrón g42 por PC del PO |
| 3 | veredicto | Inicial: adb remoto por la PC del PO. Objetivo: regla udev `51-android-pax.rules` en `<equipo-2>` (requiere OK). Descartado: USB en `windows-<equipo-1>`. SDT sólo en Windows físico si falta NeptuneService. |

## Cambio de infraestructura requerido (NO aplicado)
`/etc/udev/rules.d/51-android-pax.rules`: `SUBSYSTEM=="usb", ATTR{idVendor}=="<id de lsusb>", MODE="0660", GROUP="plugdev"` + `udevadm control --reload-rules`. El idVendor se mide al enchufar el equipo (**no medido**).

## Punto de continuación
Respuesta a P1 → si sí, aplicar y registrar folio con `lsusb` y `adb devices`; si no, conectar por la PC del PO.
