---
doc_id: MotorDsl.Network-platform-notes
doc_type: platform-notes
title: MotorDsl.Network — notas por plataforma
version: 1.0.0
status: draft
origin: human
confidence: high
owner: equipo-motordsl
last_review: 2026-08-08
audience: [dev, devops, arquitectura, agentes-automaticos]
classification: uso-interno
source_ref: feature/ios-network-transport
---

# MotorDsl.Network — notas por plataforma

## Soporte

| Plataforma | Estado | Requisito de la app consumidora |
|---|---|---|
| Android | ✅ | Permisos `INTERNET` y `ACCESS_NETWORK_STATE` |
| iOS | ✅ | Clave `NSLocalNetworkUsageDescription` en `Info.plist` |
| Windows / Linux / macOS | ✅ | Ninguno |

A diferencia de `MotorDsl.Bluetooth`, este paquete **no tiene ninguna rama de plataforma**: el
mismo ensamblado corre en todos lados.

## Por qué el TFM es `net10.0` y no `net10.0-android;net10.0-ios`

El paquete no usa una sola API nativa: `System.Net.Sockets` es BCL. Declarar sufijos de plataforma
no aportaría nada y costaría tres cosas concretas:

1. **Perdería iOS por la vía fácil.** Un `lib/net10.0/` resuelve para `net10.0-ios` por herencia de
   TFM. Es exactamente lo que hace que este paquete habilite impresión en iOS.
2. **Perdería portabilidad de build.** `dotnet pack` de un proyecto multi-TFM exige compilar todos
   sus TFM, y el workload `ios` **no existe para Linux** — `dotnet workload install ios` responde
   *«Workload ID ios isn't supported on this platform»* y el build corta con `NETSDK1178`. Es la
   razón por la que `MotorDsl.Bluetooth` y `MotorDsl.Maui` solo se empaquetan en macOS.
3. **Perdería testeabilidad.** `MotorDsl.Tests` es `net10.0` y no puede referenciar un paquete que
   solo publique TFM de plataforma; por eso las partes puras del transport Bluetooth se enlazan por
   `<Compile Include>`. Acá el `ProjectReference` es directo.

Verificable abriendo el `.nupkg`: contiene una sola carpeta, `lib/net10.0/`.

## Android

```xml
<!-- Platforms/Android/AndroidManifest.xml -->
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
```

Sin `INTERNET` el socket falla con `SocketException`, que la política de error clasifica como
`Connection` y por lo tanto **reintenta**: el síntoma es una impresión que agota los reintentos en
vez de fallar de inmediato con una causa clara.

Desde Android 9 el tráfico en claro hacia hosts arbitrarios puede estar restringido por la política
de seguridad de red. La impresión RAW al puerto 9100 no es HTTP y no la atraviesa `usesCleartext`,
pero si la app declara una `network_security_config` restrictiva conviene verificar que no bloquee
la subred local.

## iOS

```xml
<!-- Platforms/iOS/Info.plist -->
<key>NSLocalNetworkUsageDescription</key>
<string>Se usa para enviar los documentos a la impresora térmica de la red local.</string>
```

**Esta clave no es opcional.** Desde iOS 14 el acceso a la red local requiere consentimiento
explícito, y su ausencia no produce un error manejable: el sistema **termina la app** sin un mensaje
útil. Es el modo de falla más probable al integrar este paquete en iOS por primera vez.

El usuario ve un diálogo de permiso la primera vez que la app intenta contactar un host de la red
local. Si lo rechaza, las conexiones fallan con `SocketException` y solo puede revertirlo desde
Ajustes del sistema: no hay API para volver a pedirlo.

Si más adelante se agrega descubrimiento por mDNS habrá que declarar además `NSBonjourServices` con
el servicio `_pdl-datastream._tcp`.

## Compilación y empaquetado

| Entorno | ¿Compila? | ¿Empaqueta? |
|---|---|---|
| Linux (runner self-hosted, devcontainer) | ✅ | ✅ |
| Windows | ✅ | ✅ |
| macOS | ✅ | ✅ |

Es el único transport del proyecto que se empaqueta en cualquier plataforma. En `cd-nuget.yml` sale
del job `pack-managed`, que corre en el runner self-hosted, junto con los otros cinco paquetes
`net10.0`.

## AOT y trimming

El paquete es especialmente benigno para las configuraciones de iOS Release: no usa reflexión, ni
serialización por reflexión, ni generación dinámica de código. `System.Net.Sockets` no le da
trabajo al compilador AOT, así que funciona igual bajo `RunAOTCompilation`, `UseInterpreter` o
`PublishTrimmed` sin necesidad de directivas de preservación.
