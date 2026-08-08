---
doc_id: MotorDsl.Network-readme
doc_type: piece-readme
title: MotorDsl.Network — transport de impresión por red TCP 9100
version: 1.0.0
status: draft
origin: human
confidence: high
owner: equipo-motordsl
last_review: 2026-08-08
audience: [dev, arquitectura, agentes-automaticos]
classification: uso-interno
source_ref: feature/ios-network-transport
---

# MotorDsl.Network

> Pieza `library` (transport concreto) del stack de impresión de MotorDsl. Documentada junto con
> su implementación; estado `draft`.

## Resumen ejecutivo

`MotorDsl.Network` implementa `IThermalPrinterTransport` sobre un **socket TCP al puerto 9100**
(RAW / JetDirect), el estándar de facto de impresión cruda que expone prácticamente toda impresora
térmica con Ethernet o WiFi. Escribe exactamente los mismos bytes ESC/POS que el transport
Bluetooth: lo que cambia es el medio, no el contenido.

Su rasgo definitorio es el TFM. El paquete targetea **`net10.0` puro**, sin sufijo de plataforma,
porque no usa una sola API nativa —`System.Net.Sockets` es BCL—. De ahí se siguen tres propiedades
que ningún otro transport del proyecto tiene:

- **Habilita impresión en iOS.** Un paquete `net10.0` es consumible desde `net10.0-ios` por
  herencia de TFM. Es la respuesta a la limitación que documenta
  [ADR-0005](../../docs/04-decisions/ADR-0005-transport-red-net10-puro.md): Apple no expone
  Bluetooth Classic SPP, así que `MotorDsl.Bluetooth` no puede funcionar ahí.
- **Se construye en cualquier sistema operativo**, incluido el runner self-hosted Linux, a
  diferencia de `MotorDsl.Bluetooth` y `MotorDsl.Maui`, que exigen macOS para empaquetarse porque
  el workload `ios` no existe para Linux.
- **Es testeable de verdad.** `MotorDsl.Tests` (`net10.0`) lo referencia directamente, sin el
  enlace por `<Compile Include>` que necesitan las partes puras del transport Bluetooth.

## Uso

```csharp
builder.Services.AddMotorDslEngine()
    .AddTemplates(t => t.Add("ticket", TicketDsl.Document))
    .AddProfiles(p => p.Add(new DeviceProfile("thermal_58mm", 32, "escpos-bitmap")))
    .AddMotorDslMaui();

#if ANDROID
builder.Services.AddBluetoothPrinterTransport();     // Kind = "bluetooth"
#endif

builder.Services.AddNetworkPrinterTransport(o => o
    .AddPrinter("192.168.1.50")                      // puerto 9100 por defecto
    .AddPrinter("192.168.1.51:9101"));               // Kind = "network"
```

Los dos transports conviven: `ThermalPrinterService` recibe
`IEnumerable<IThermalPrinterTransport>` y rutea por `PrinterDevice.Kind`.

## Superficie pública

| Tipo | Rol |
|---|---|
| `NetworkPrinterTransport` | Implementación de `IThermalPrinterTransport`. `Kind = "network"` |
| `NetworkPrinterOptions` | Endpoints conocidos, timeouts y tamaño de bloque |
| `MotorDslNetworkServiceCollectionExtensions.AddNetworkPrinterTransport` | Registro en DI |

El detalle de miembros y contratos está en [api-reference](api-reference.md); el comportamiento por
plataforma, en [platform-notes](platform-notes.md).

## Identificación de la impresora

`IThermalPrinterTransport` define `deviceId` como `string` libre. En Bluetooth es una MAC; acá es
un endpoint de red, y se aceptan tres formas:

| Entrada | Host | Puerto |
|---|---|---|
| `192.168.1.50` | `192.168.1.50` | 9100 (defecto) |
| `192.168.1.50:9101` | `192.168.1.50` | 9101 |
| `[fe80::1]:9100` | `fe80::1` | 9100 |

También se admite un nombre de host: la resolución la hace el socket, no el parser.

## Descubrimiento

No hay equivalente al barrido de dispositivos emparejados de Bluetooth: en una red no existe una
lista que consultar. `DiscoverAsync` devuelve los endpoints declarados en `NetworkPrinterOptions`,
descartando en silencio los sintácticamente inválidos —una entrada mal cargada no debe romper el
barrido completo—.

Deliberadamente **no** se barre la subred probando el puerto 9100 host por host: es lento y se
parece a un escaneo de puertos. El descubrimiento por mDNS / Bonjour (`_pdl-datastream._tcp`) queda
como extensión futura y no cambiaría el contrato.

## Comportamiento de escritura

Replica el del transport Bluetooth para que un mismo documento salga igual por cualquier medio:

1. `Task.Delay(profile.InitDelayMs)` antes del primer bloque.
2. Chunking de **tamaño fijo** (256 bytes por defecto), **independiente del contenido**: la salida
   `escpos-bitmap` contiene `0x0A` arbitrarios en los datos de píxeles, así que partir por LF
   corrompería la imagen.
3. Un retardo de pacing por bloque, con piso de 1 ms.
4. `Task.Delay(profile.FinalDelayMs)` al cerrar.

Sobre TCP el pacing es conservador más que imprescindible: el control de flujo real lo aporta el
propio protocolo, a diferencia de SPP, que emula el canal de datos pero no las líneas RTS/CTS.

## Errores

| Situación | Excepción | Clasificación | ¿Reintenta? |
|---|---|---|---|
| Endpoint mal formado | `ArgumentException` | — | Falla al conectar |
| Nada escuchando en el puerto | `SocketException` **sin envolver** | `Connection` | Sí |
| Timeout de conexión o escritura | `TimeoutException` | `Timeout` | Sí |
| Socket roto durante el envío | `IOException` / `SocketException` **sin envolver** | `Connection` | Sí |
| Escribir sin conexión establecida | `InvalidOperationException` | `Unknown` | Sí |

No envolver es un requisito, no un detalle de estilo: `PrintError.FromException` mapea
`IOException` y `SocketException` a `Connection`, y envolverlas en `Exception` las degradaría a
`Unknown`. Además, ante error el transport deja `IsConnected = false`, porque
`ThermalPrinterService.ReconnectInternalAsync` solo reconecta bajo esa condición.

`DisconnectAsync` **nunca lanza**: el código de limpieza suele llamarla sin `try/catch`.

## Limitaciones conocidas

- **Sin detección de capacidades.** `Capabilities` devuelve `null` y los métodos de memoria NV se
  apoyan en las implementaciones default del contrato. El sondeo por `DLE EOT` es posible sobre TCP
  y queda como extensión; mientras tanto el envío usa pacing fijo, equivalente al camino degradado
  del transport Bluetooth.
- **Requiere impresoras con red.** No sirve para el parque de térmicas Bluetooth económicas.
- **Sin descubrimiento automático.** Ver arriba.

## Trazas

- Decisión: [ADR-0005](../../docs/04-decisions/ADR-0005-transport-red-net10-puro.md)
- Contrato y orquestador: [MotorDsl.Printing.Abstractions](../MotorDsl.Printing.Abstractions/README.md)
- Índice: [ia-db 04 — impresión y transports](../../../ia-db/indexes/04_impresion-transports.md)
- Análisis de origen: [`Analisis/03-Analisis-IOs/Nuget-Multiplaforma.md`](../../../Analisis/03-Analisis-IOs/Nuget-Multiplaforma.md)
