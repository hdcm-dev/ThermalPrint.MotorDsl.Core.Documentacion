# 04 — Impresión y transports

> **Propósito**: cómo viaja el `byte[]` desde el motor hasta la impresora — orquestador, retry,
> detección de capacidades, los dos transports concretos y el aprovisionamiento de logos NV.
> **Fuentes primarias**: `src/MotorDsl.Printing.Abstractions/`, `src/MotorDsl.Bluetooth/`,
> `src/MotorDsl.Network/`, `docs/10_developer_guide/transports-y-extensibilidad.md`.

---

## 1. Las dos capas

```text
App  →  IThermalPrinterService  →  IThermalPrinterTransport  →  Impresora
        (orquesta: retry,           (habla el canal:
         eventos, historial,         SPP / TCP / futuros)
         ruteo por Kind)
```

`ThermalPrinterService` es único y agnóstico; los transports son intercambiables y se registran
tantos como haga falta. El ruteo es por el string `Kind`.

| `Kind` | Transport | Plataformas | Registro |
|---|---|---|---|
| `bluetooth` | `BluetoothPrinterTransport` | Android (iOS lanza `PlatformNotSupportedException`) | `AddBluetoothPrinterTransport()` |
| `network` | `NetworkPrinterTransport` | Android, iOS, escritorio | `AddNetworkPrinterTransport(o => o.AddPrinter("192.168.1.50"))` |
| `fake` | `FakeTransport` | solo tests | `src/MotorDsl.Tests/TestFakes.cs` |

Ambos pueden convivir en el mismo contenedor: `DiscoverDevicesAsync` combina lo que reporta cada
uno y `ConnectAsync` elige el transport cuyo `Kind` coincide con `device.Kind`.

---

## 2. `IThermalPrinterTransport`

Fuente: [`src/MotorDsl.Printing.Abstractions/Contracts/IThermalPrinterTransport.cs`](../../../PrintThermal_Motor_Maui/src/MotorDsl.Printing.Abstractions/Contracts/IThermalPrinterTransport.cs).

| Miembro | Obligatorio | Notas |
|---|---|---|
| `Kind`, `IsConnected`, `CurrentDevice` | Sí | identidad y estado |
| `DiscoverAsync`, `ConnectAsync`, `DisconnectAsync`, `WriteBytesAsync` | Sí | ciclo de vida y envío |
| `Capabilities` | No — default `null` | tri-estado detectado al conectar |
| `ProvisionLogoAsync`, `IsLogoProvisionedAsync`, `ClearLogoAsync` | No — **default interface methods** | no-op para transports que no soportan NV |

Los tres métodos de NV traen implementación por defecto en la interfaz precisamente para que un
transport nuevo no tenga que saber nada de logos: `ProvisionLogoAsync` devuelve
`NvLogoResult(false, null, "transport no soporta NV")`.

---

## 3. `ThermalPrinterService` — el orquestador

Fuente: [`src/MotorDsl.Printing.Abstractions/Services/ThermalPrinterService.cs`](../../../PrintThermal_Motor_Maui/src/MotorDsl.Printing.Abstractions/Services/ThermalPrinterService.cs) (281 líneas).

Implementa `INotifyPropertyChanged`: `IsConnected`, `CurrentDevice`, `ConnectionState` y
`LastError` notifican cambios, que es lo que hace bindeables los controles de `MotorDsl.Maui`.

### Estados

```text
Disconnected → Scanning → Disconnected        (descubrimiento sin conexión previa)
Disconnected → Connecting → Connected | Failed
Connected    → Reconnecting → Connected | Failed
```

`PrinterConnectionState` tiene seis valores: `Disconnected`, `Scanning`, `Connecting`, `Connected`,
`Reconnecting`, `Failed`.

### Construcción

Exige **al menos un transport**: con la colección vacía lanza `InvalidOperationException` nombrando
`AddBluetoothPrinterTransport` como ejemplo. Es un fallo temprano deliberado, no un fallo al
imprimir.

### `SendBytesAsync` — el bucle de retry

```text
para intento = 1 .. retry.MaxRetries (default 3):
    escribir por el transport activo
    éxito  → errorHandler.OnPrintSuccess(intento); return
    fallo  → PrintError.FromException(...)
             disparar ErrorOccurred
             preguntar al IPrintErrorHandler si reintentar
             si NO reintenta o se agotaron los intentos:
                 registrar el fallo en el historial y relanzar envuelto
             esperar InitialDelayMs * 2^(intento-1)   (500, 1000, 2000 ms)
             intentar reconectar en silencio
```

El backoff es exponencial con base `InitialDelayMs = 500`. La reconexión silenciosa solo actúa si
el transport quedó con `IsConnected == false` — que es exactamente lo que ambos transports hacen al
invalidar su estado ante un error de socket.

### Clasificación de errores

`PrintError.FromException` mapea la excepción a un `PrintErrorType`:

| Excepción | Tipo | ¿Reintenta el handler por defecto? |
|---|---|---|
| `PrinterHardwareException` | `Hardware` | **No** — papel o tapa, reintentar no arregla nada |
| `IOException`, `SocketException` | `Connection` | Sí |
| `TimeoutException`, `TaskCanceledException` | `Timeout` | Sí |
| cualquier otra | `Unknown` | Sí |

Por eso los transports relanzan `IOException`/`SocketException` **sin envolver**: envolverlas en
`Exception` las degradaría a `Unknown` y se perdería la precisión de la clasificación. Está
comentado así en el código de ambos.

### Historial de fallos

Ring buffer de **20 entradas** (`MAX_FAILURES`), protegido por `lock`, no persistido a disco. Se
registra **una** entrada por envío agotado, no una por intento. Cada `PrintFailureEntry` guarda
timestamp, identidad del dispositivo, snapshot de capacidades, tipo y mensaje del error, número de
intentos y la **longitud** del payload —nunca el payload—. `RecentFailures` devuelve una copia;
`ClearFailures()` lo vacía.

---

## 4. Capacidades tri-estado (ADR-0004)

```csharp
enum CapabilitySupport { Unknown, NotDetected, Supported }

record PrinterCapabilities(
    CapabilitySupport StatusFeedback,
    CapabilitySupport NvGraphics,
    string? NvGraphicsKind,   // "gsl" | "fs" | null
    string? ModelId);         // best-effort desde GS I
```

La distinción que justifica el enum: en térmicas de bajo costo, «no contestó» suele significar
«estaba ocupada», no «no lo soporta». `Unknown` es el valor de partida
(`PrinterCapabilities.Unknown()`) y también el destino cuando la detección falla.

`PrintStrategySelector.RecommendTarget(caps, docNeedsGraphics)` recomienda `"escpos"` si el soporte
NV es `Supported` y `"escpos-bitmap"` en cualquier otro caso. El parámetro `docNeedsGraphics` está
declarado, descartado con `_ = docNeedsGraphics` y reservado para heurísticas futuras.

---

## 5. `BluetoothPrinterTransport` (Android)

Cinco archivos `partial` en [`src/MotorDsl.Bluetooth/`](../../../PrintThermal_Motor_Maui/src/MotorDsl.Bluetooth/):

| Archivo | Contenido | ¿Puro? |
|---|---|---|
| `BluetoothPrinterTransport.cs` | Ciclo de vida y `WriteBytesAsync` | No (`#if ANDROID`) |
| `.Detection.cs` | Sondeos DLE EOT / GS ( L / GS I, lectura no bloqueante | No |
| `.Nv.cs` | Definir / consultar / borrar logos NV | No |
| `.Capabilities.cs` | Clasificación de bytes de status, decisión de pacing, `ParseGsV0` | **Sí** |
| `.Chunking.cs` | `ChunkBuffer` | **Sí** |

Los dos últimos son código puro sin dependencias de plataforma, y por eso `MotorDsl.Tests` los
enlaza **por fuente** (`<Compile Include=… Link=…>`): el proyecto targetea `net10.0-android`/`-ios`
y no se puede referenciar desde un `net10.0`.

### Conexión

UUID SPP estándar `00001101-0000-1000-8000-00805F9B34FB` sobre RFCOMM. `DiscoverAsync` **solo lista
dispositivos ya emparejados** (`BondedDevices`) — no hace descubrimiento activo. Verifica que el
adaptador exista, esté encendido y, desde Android 12 (API 31), que `BLUETOOTH_CONNECT` esté
concedido; cada caso lanza con un mensaje accionable.

Tras conectar se captura el `InputStream` Java subyacente para poder usar `Available()` y leer sin
bloquear. Si no se logra, el flow control degrada solo. La detección de capacidades corre
inmediatamente después y está envuelta en su propio `try/catch`: **nunca puede hacer fallar la
conexión**.

### Escritura y flow control

Chunks fijos de **256 bytes** sobre todo el buffer. El tamaño es fijo a propósito: la salida
`escpos-bitmap` contiene `0x0A` arbitrarios dentro de los datos de píxeles, así que no se puede
partir por saltos de línea.

Con `StatusFeedback == Supported`, antes de cada bloque consulta `DLE EOT n=1` y decide:

| Status leído | Decisión |
|---|---|
| `Ready` | escribir ya, sin pacing fijo |
| `Busy` | escribir igual, con pacing de respaldo |
| `Unknown` | **degradar** a pacing fijo para todo el resto del envío |

La degradación es irreversible dentro de un mismo envío (`NextPacingDecision`). El límite está
declarado en el propio código: `DLE EOT` da liveness, papel y error en tiempo real, **no** bytes
libres del buffer — no es flow control perfecto, pero evita escribir a ciegas.

Antes del primer bloque hay un fast-fail de hardware (`DLE EOT n=4` y `n=2`): fin de papel o tapa
abierta lanzan `PrinterHardwareException`, que el handler clasifica como `Hardware` y **no**
reintenta.

Ante `IOException` (típicamente *broken pipe* por overrun), invalida la conexión y relanza sin
envolver, para que el servicio reconecte en el próximo intento.

### Logos NV

`ProvisionLogoAsync` recibe **el mismo `byte[]` GS v 0** que la app ya produce para imágenes
inline: `ParseGsV0` lo desarma en `(widthBytes, heightDots, bits)` y lo re-emite como definición NV,
probando primero `GS ( L` (moderno) y cayendo a `FS q` (legacy). `IsLogoProvisionedAsync` consulta
`GS ( L fn=64`; `ClearLogoAsync` emite el borrado por keycode. El resultado viaja en
`NvLogoResult(Success, Kind, Message)` y actualiza las capacidades del transport.

La ganancia: un logo aprovisionado se imprime después con **11 bytes** de recall en vez de re-enviar
el raster completo en cada ticket.

---

## 6. `NetworkPrinterTransport` (multiplataforma)

Fuente: [`src/MotorDsl.Network/`](../../../PrintThermal_Motor_Maui/src/MotorDsl.Network/).

TCP crudo al puerto **9100** (RAW / JetDirect). El TFM es `net10.0` **puro y deliberado**: no usa
ninguna API nativa —`System.Net.Sockets` es BCL—, así que se consume desde `net10.0-android` y
`net10.0-ios` por herencia de TFM, se empaqueta en cualquier sistema operativo y es referenciable
directamente desde los tests (ADR-0005, y el comentario extenso en el `.csproj`).

### Opciones

| Propiedad | Default |
|---|---|
| `KnownEndpoints` | vacío — hay que sembrarlo con `AddPrinter(...)` |
| `ConnectTimeout` | 5 s |
| `WriteTimeout` | 30 s |
| `ChunkSize` | 256 (`TransportChunking.DefaultChunkSize`) |

**No hay descubrimiento**: `DiscoverAsync` devuelve los endpoints preconfigurados. mDNS/Bonjour
está en el roadmap.

### Parseo de endpoints

`TryParseEndpoint` acepta cuatro formas y valida el rango de puerto 1–65535:

| Entrada | Host | Puerto |
|---|---|---|
| `192.168.1.50` | `192.168.1.50` | 9100 |
| `192.168.1.50:9100` | `192.168.1.50` | 9100 |
| `[fe80::1]:9100` | `fe80::1` | 9100 |
| `fe80::1` (sin corchetes) | `fe80::1` | 9100 — no se le puede separar el puerto sin ambigüedad |

`FormatEndpoint` re-encorcheta las IPv6 al normalizar el id del dispositivo.

### Timeouts y errores

`ConnectAsync` traduce su propio vencimiento a `TimeoutException` —distinguiendo el timeout interno
de una cancelación del llamador con `when (!ct.IsCancellationRequested)`— para que el handler lo
clasifique como `Timeout` y reintente. `SocketException` e `IOException` suben sin envolver.
`WriteBytesAsync` aplica el mismo criterio y, ante cualquiera de los dos, invalida la conexión.

El pacing por bloque se mantiene aunque sobre TCP el control de flujo real lo aporta el protocolo:
está documentado en el código como conservador, no imprescindible —a diferencia de SPP, que no
tiene RTS/CTS.

Implementa `IDisposable`.

---

## 7. Chunking compartido

`TransportChunking.ChunkBuffer(data, size = 256)` en `MotorDsl.Printing.Abstractions` es el helper
público para que cualquier transport reutilice el troceo. Valida `data != null` y `size > 0`, y
devuelve `ArraySegment<byte>` perezosos, sin copiar.

`MotorDsl.Bluetooth` conserva su propia copia `internal` en `.Chunking.cs` —para poder testearla por
enlace de fuente— con la misma semántica.

---

## 8. Escribir un transport propio

1. Implementar `IThermalPrinterTransport` con un `Kind` nuevo.
2. Dejar `Capabilities` en `null` si no se detecta nada, y no implementar los métodos NV si no
   aplican: sus defaults ya responden correctamente.
3. Ante error de canal, **invalidar el estado interno** (`IsConnected = false`, liberar recursos) y
   **relanzar sin envolver** las excepciones que `PrintError.FromException` ya clasifica bien.
4. Traducir los timeouts propios a `TimeoutException`.
5. Registrar con `services.AddSingleton<IThermalPrinterTransport, MiTransport>()`.

`NetworkPrinterTransport` es la referencia más corta y limpia; `BluetoothPrinterTransport` la más
completa. Guía narrativa: `docs/10_developer_guide/transports-y-extensibilidad.md`.

---

## 9. Perfiles de temporizado

`PrinterProfile` (distinto de `DeviceProfile`, que describe el papel y el render) agrupa los delays
del canal: `LineDelayMs` 150, `ByteDelayMs` 5, `InitDelayMs` 100, `FinalDelayMs` 500, `QrDelayMs`
300, `ImageDelayMs` 500, `CutDelayMs` 500, `InitCommandDelayMs` 300.

Dos perfiles estáticos: `Thermal58mm` (genérico, el default de `SendBytesAsync`) y `Real58HB6`
(medido sobre una 58HB6-6101 real). De los ocho campos, los transports consumen tres:
`InitDelayMs`, `ByteDelayMs` (como pacing por bloque, con piso de 1 ms) y `FinalDelayMs`.
