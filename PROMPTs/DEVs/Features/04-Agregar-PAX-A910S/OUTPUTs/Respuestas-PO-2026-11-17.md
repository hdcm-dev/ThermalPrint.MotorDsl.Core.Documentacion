# Respuestas del PO al lote de preguntas de la mesa (2026-11-17)

Respuestas textuales del PO en la sesión, con el efecto que tienen sobre el plan aprobado (`Plan-Aprobado-Mesa.md`).

| Pregunta | Respuesta del PO | Efecto |
|---|---|---|
| P1 (regla udev en `<equipo-2>`) | «mi pc es una maquina virtual que corre en `<equipo-4>`, a g42 te lo comparto desde ahi» | El A910S se conecta como el g42: enchufado al USB de la VM del PO en `<equipo-4>` y compartido por adb remoto (Tailscale, `adb -H <ip> -P 5037`). No hace falta la regla udev en `<equipo-2>` ni tocar `windows-<equipo-1>`. El host del adb remoto sale de esa VM: se mide al llegar el equipo (D1). |
| P4 (fix 08 en Homologacion) | «para todas las modificaciones sobre `<app-web>` se hace un rama y no se fusiona porque necesito aprobación, pero si nace de Homologación» | El fix 08 (6970c6b3) se lleva a una rama nueva de `<app-web>` que nace de `origin/Homologacion`. Se hace commit y push, sin PR ni merge. Rige para todo cambio en `<app-web>`. |
| P5 (firma de `<firmante-PAX>`) | «puede que dos horas» | D4: hay que prever unas 2 h de demora por cada APK que se manda a firmar. El canal no se indicó y sigue abierto. |
| P2, P3, P6, P7 | Sin respuesta | Rigen los valores por defecto del plan. |
