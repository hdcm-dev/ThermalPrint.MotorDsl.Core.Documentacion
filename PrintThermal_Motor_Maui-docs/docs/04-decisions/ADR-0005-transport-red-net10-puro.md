---
doc_id: ADR-0005
doc_type: adr
title: "ADR-0005: Transport de red en un paquete net10.0 puro para habilitar iOS"
status: draft
origin: human
confidence: high
date: 2026-08-08
deciders: [equipo-motordsl]
owner: equipo-motordsl
last_review: 2026-08-08
audience: [dev, arquitectura, devops, agentes-automaticos]
classification: uso-interno
traces: [ADR-0002, ARCH-CC-001]
source_ref: feature/ios-network-transport
---

# ADR-0005: Transport de red en un paquete `net10.0` puro para habilitar iOS

> `origin: human` — decisión tomada a partir del análisis
> [`Analisis/03-Analisis-IOs/Nuget-Multiplaforma.md`](../../../Analisis/03-Analisis-IOs/Nuget-Multiplaforma.md),
> que evaluó cinco alternativas de soporte iOS con evidencia verificable.

## Contexto

El motor compila y renderiza correctamente en iOS: los cinco paquetes base son `net10.0` sin
dependencias de plataforma y `MotorDsl.Maui` tiene una sola directiva de compilación condicional
en todo el proyecto. Lo que no funciona es la última etapa del pipeline, la que va del `byte[]` al
papel: el único transport del repositorio es Bluetooth Classic SPP, y Apple no expone ese perfil a
apps de terceros sin certificación MFi. Sus cuatro métodos operativos lanzan
`PlatformNotSupportedException` en el TFM de iOS.

A esa restricción de plataforma se suma una de infraestructura, verificada empíricamente: el
workload `ios` **no existe para Linux** (`Workload ID ios isn't supported on this platform`), y el
CI del proyecto corre sobre un runner self-hosted Ubuntu. Cualquier paquete que declare
`net10.0-ios` queda fuera del alcance de ese runner, porque `dotnet pack` de un proyecto multi-TFM
exige compilar todos sus TFM.

## Decisión

1. El soporte de impresión en iOS se resuelve con un **transport de red TCP al puerto 9100**
   (RAW / JetDirect), publicado como paquete propio `MotorDsl.Network`.
2. El paquete targetea **`net10.0` puro**, sin sufijo de plataforma. No usa ninguna API nativa:
   `System.Net.Sockets` es BCL.
3. `MotorDsl.Bluetooth` **conserva su TFM de iOS** y su `PlatformNotSupportedException`. Quitarlo
   obligaría a toda app multiplataforma a condicionar el `PackageReference` por TFM.
4. El transport nuevo expone `Kind = "network"` y se registra con `AddSingleton`, de modo que
   **coexiste** con el de Bluetooth: el servicio rutea por `PrinterDevice.Kind` (ADR-0002).

## Alternativas

- **Transport BLE** (`CoreBluetooth` en iOS, `Android.Bluetooth.LE` en Android). Encaja mejor con
  el escenario de campo, pero exige dos implementaciones nativas y, sobre todo, **la mayoría de las
  térmicas económicas no expone BLE**: la tecnología que iOS permite no es la que el hardware trae.
  Queda como candidata para una segunda etapa, condicionada a una definición de negocio sobre el
  parque de impresoras.
- **MFi / `ExternalAccessory`**. Único camino legítimo para hablar SPP desde iOS, pero obliga a
  comprar hardware certificado e integrar el SDK propietario de cada fabricante, sin API genérica.
- **AirPrint vía PDF**. Costo casi nulo y complementario, pero no produce un ticket térmico: no
  sustituye al transport.
- **Servidor de impresión intermedio**. Convierte un problema de plataforma en uno de
  infraestructura y rompe la operación en campo sin conectividad.
- **Empaquetar el transport de red con TFM de plataforma** (`net10.0-android;net10.0-ios`).
  Funcionaría, pero renunciaría a todas las ventajas del punto siguiente sin ganar nada: no hay
  código nativo que justifique el sufijo.

## Consecuencias

- (+) **iOS puede imprimir.** El escenario que estaba bloqueado deja de estarlo.
- (+) Un paquete `net10.0` es consumible desde `net10.0-android`, `net10.0-ios` y escritorio por
  herencia de TFM. **Un solo cuerpo de código cubre todas las plataformas**, sin `#if`.
- (+) Se construye, testea y empaqueta en Linux, incluido el runner self-hosted. El soporte iOS se
  entrega **sin que ninguna máquina Apple participe del build de la librería**.
- (+) `MotorDsl.Tests` (`net10.0`) lo referencia directamente, sin el enlace por `<Compile Include>`
  que `MotorDsl.Bluetooth` necesita por targetear solo android/ios. La cobertura es real, con
  verificación de paridad byte a byte contra un `TcpListener`.
- (+) Sobre TCP el control de flujo lo aporta el protocolo, a diferencia de SPP, que no tiene
  RTS/CTS y obliga al pacing artificial de `PrinterProfile`.
- (–) **Exige impresoras con red.** No sirve para el parque de térmicas Bluetooth económicas: es un
  costo de hardware, no de software.
- (–) El descubrimiento no tiene equivalente al barrido Bluetooth. La primera iteración usa
  endpoints declarados por la app; mDNS queda pendiente.
- (–) Un octavo paquete suma superficie a la versión unificada y al pipeline de publicación.
- (–) La app consumidora debe declarar `NSLocalNetworkUsageDescription` en iOS. Sin esa clave el
  sistema termina la app sin mensaje útil.

Fuente: [ia-db 04](../../../ia-db/indexes/04_impresion-transports.md),
[análisis de soporte iOS](../../../Analisis/03-Analisis-IOs/Nuget-Multiplaforma.md) §6 y §7.
