---
doc_id: MotorDsl.Network-api-reference
doc_type: api-reference
title: MotorDsl.Network — referencia de API
version: 1.0.0
status: draft
origin: human
confidence: high
owner: equipo-motordsl
last_review: 2026-08-08
audience: [dev, agentes-automaticos]
classification: uso-interno
source_ref: feature/ios-network-transport
---

# MotorDsl.Network — referencia de API

> Namespace raíz: `MotorDsl.Network`. TFM: `net10.0`. Depende de
> `MotorDsl.Printing.Abstractions` y de `Microsoft.Extensions.DependencyInjection.Abstractions`.

## `NetworkPrinterTransport`

`public partial class NetworkPrinterTransport : IThermalPrinterTransport, IDisposable`

Implementa el contrato de transport sobre `System.Net.Sockets.TcpClient`.

### Constructor

| Firma | Descripción |
|---|---|
| `NetworkPrinterTransport(NetworkPrinterOptions? options = null)` | Sin opciones usa los valores por defecto y `DiscoverAsync` devuelve vacío |

### Constantes

| Miembro | Valor | Descripción |
|---|---|---|
| `DefaultPort` | `9100` | Puerto RAW / JetDirect |

### Propiedades

| Miembro | Tipo | Comportamiento |
|---|---|---|
| `Kind` | `string` | Siempre `"network"`. Discriminador de ruteo del servicio |
| `IsConnected` | `bool` | `true` entre una conexión exitosa y su cierre o invalidación |
| `CurrentDevice` | `PrinterDevice?` | El dispositivo conectado, con `Id` en forma canónica; `null` si no hay conexión |
| `Capabilities` | `PrinterCapabilities?` | Siempre `null` en esta versión: no hay detección de capacidades |

### Métodos del contrato

| Firma | Comportamiento |
|---|---|
| `Task<IReadOnlyList<PrinterDevice>> DiscoverAsync(CancellationToken)` | Devuelve un `PrinterDevice` por cada endpoint válido de las opciones. Descarta los inválidos sin lanzar. No hace I/O de red |
| `Task<bool> ConnectAsync(string deviceId, CancellationToken)` | Abre el socket. Devuelve `true` o lanza. Limpia cualquier conexión previa antes de abrir |
| `Task DisconnectAsync()` | Cierra y limpia. **Nunca lanza.** Idempotente |
| `Task WriteBytesAsync(byte[] data, PrinterProfile profile, CancellationToken)` | Escribe con chunking y pacing |

Los tres métodos de memoria NV (`ProvisionLogoAsync`, `IsLogoProvisionedAsync`, `ClearLogoAsync`)
no se implementan: se usan las implementaciones default de `IThermalPrinterTransport`, que degradan
sin lanzar.

### Métodos estáticos puros

| Firma | Comportamiento |
|---|---|
| `static bool TryParseEndpoint(string? deviceId, out string? host, out int port)` | Interpreta `host`, `host:puerto` o `[ipv6]:puerto`. Devuelve `false` ante entrada inválida en vez de lanzar |
| `static string FormatEndpoint(string host, int port)` | Forma canónica del `Id`. Es la inversa de `TryParseEndpoint`: reparsear el resultado devuelve los mismos valores. Pone corchetes solo en IPv6 |

### Excepciones

| Situación | Excepción |
|---|---|
| `deviceId` no parsea | `ArgumentException` |
| Vence `ConnectTimeout` | `TimeoutException` |
| Vence `WriteTimeout` | `TimeoutException` |
| Fallo de socket al conectar o escribir | `SocketException` / `IOException`, **sin envolver** |
| `WriteBytesAsync` sin conexión | `InvalidOperationException` |
| `data` o `profile` en `null` | `ArgumentNullException` |

Una cancelación disparada por el `CancellationToken` del llamador se propaga como
`OperationCanceledException`; solo el vencimiento del timeout propio se traduce a
`TimeoutException`.

## `NetworkPrinterOptions`

`public sealed class NetworkPrinterOptions`

| Miembro | Tipo | Defecto | Descripción |
|---|---|---|---|
| `KnownEndpoints` | `IList<string>` | vacío | Endpoints que devuelve `DiscoverAsync` |
| `ConnectTimeout` | `TimeSpan` | 5 s | Timeout de establecimiento de conexión |
| `WriteTimeout` | `TimeSpan` | 30 s | Timeout de escritura sobre el socket establecido |
| `ChunkSize` | `int` | 256 | Tamaño de bloque de escritura |
| `AddPrinter(string endpoint)` | `NetworkPrinterOptions` | — | Agrega un endpoint y devuelve las opciones, para encadenar. Ignora nulos y vacíos |

## `MotorDslNetworkServiceCollectionExtensions`

`public static class MotorDslNetworkServiceCollectionExtensions`

```csharp
public static IServiceCollection AddNetworkPrinterTransport(
    this IServiceCollection services,
    Action<NetworkPrinterOptions>? configure = null)
```

Registra `NetworkPrinterOptions` y el transport como **singleton**, con `AddSingleton` y no
`TryAdd`: el servicio consume `IEnumerable<IThermalPrinterTransport>` y varios transports deben
poder coexistir.

## `TransportChunking` (en `MotorDsl.Printing.Abstractions`)

Helper público compartido que este paquete consume.

| Miembro | Descripción |
|---|---|
| `const int DefaultChunkSize` | `256` |
| `static IEnumerable<ArraySegment<byte>> ChunkBuffer(byte[] data, int size = DefaultChunkSize)` | Segmentos contiguos de tamaño fijo, independientes del contenido. Vistas sin copia; reensamblarlos en orden reproduce el array original |

Lanza `ArgumentNullException` si `data` es `null` y `ArgumentOutOfRangeException` si `size` no es
positivo.
