---
doc_id: MotorDsl.Bluetooth-api-reference
doc_type: api-reference
title: MotorDsl.Bluetooth — referencia de API
version: 1.0.0
status: draft
origin: reverse-engineered
confidence: high
owner: equipo-motordsl
last_review: 2026-07-15
audience: [dev, arquitectura, agentes-automaticos]
classification: uso-interno
source_ref: v1.0.13 @83677eb
---

# API — MotorDsl.Bluetooth

> Superficie pública y constantes operativas del transport Bluetooth Classic SPP en
> **v1.0.13 @83677eb**. Ver también [README](./README.md) y [platform-notes](./platform-notes.md).

## 1. Superficie pública

La pieza expone **una** clase de transport y **una** extensión de DI. Todo lo demás
(builders/sondeos ESC/POS, constantes internas, parseo) es **privado** del transport.

| Tipo | Kind | Descripción | Fuente |
|---|---|---|---|
| `BluetoothPrinterTransport` | `"bluetooth"` | `partial class : IThermalPrinterTransport`. Implementa el contrato de transport (Android; iOS lanza). | `BluetoothPrinterTransport.cs#L17`, `#L35` |
| `MotorDslBluetoothServiceCollectionExtensions.AddBluetoothPrinterTransport(this IServiceCollection)` | — | Registra el transport con `AddSingleton<IThermalPrinterTransport, BluetoothPrinterTransport>`. | `MotorDslBluetoothServiceCollectionExtensions.cs#L8-L12` |

`BluetoothPrinterTransport` no agrega miembros públicos propios más allá del contrato
`IThermalPrinterTransport` (`Kind`, `IsConnected`, `CurrentDevice`, `Capabilities`, `DiscoverAsync`,
`ConnectAsync`, `DisconnectAsync`, `WriteBytesAsync`, `ProvisionLogoAsync`, `IsLogoProvisionedAsync`,
`ClearLogoAsync`). Las firmas exactas están en la
[API de Abstractions](../MotorDsl.Printing.Abstractions/api-reference.md#11-ithermalprintertransport-firma-exacta).

### 1.1 Comportamiento específico del transport (Android)

| Método | Comportamiento observable | Fuente |
|---|---|---|
| `DiscoverAsync` | Solo dispositivos **emparejados** (`BondedDevices`). Exige `_bluetoothAdapter != null`, BT habilitado y permiso `BLUETOOTH_CONNECT` en API 31+ (`SdkInt >= S`); `Java.Lang.SecurityException` → lista vacía. Cada `PrinterDevice` sale con `Kind="bluetooth"`, `IsPaired=true`. | `BluetoothPrinterTransport.cs#L52-L96` |
| `ConnectAsync` | `InvalidateConnection()` previo; `CreateRfcommSocketToServiceRecord(UUID SPP)`; `Connect()` en `Task.Run`; captura `InputStreamInvoker.BaseInputStream` para `Available()`; detección de capacidades best-effort (`catch → Unknown()`). Error → `Exception("Error al conectar: …")`. | `BluetoothPrinterTransport.cs#L98-L143` |
| `WriteBytesAsync` | Fast-fail hardware (si `StatusFeedback==Supported`) → `InitDelayMs` → chunking 256 con gating/pacing → `FinalDelayMs`. `IOException` (System.IO **o** Java.IO) → `InvalidateConnection()` + rethrow sin envolver. | `BluetoothPrinterTransport.cs#L179-L257` |
| `DisconnectAsync` | Flush + dispose del output stream y del socket; `IsConnected=false`. | `BluetoothPrinterTransport.cs#L145-L177` |
| `ProvisionLogoAsync` | Parsea el `GS v 0` de entrada y re-emite como DEFINE NV: `GS ( L` fn=67 + verificación fn=64 → `NvLogoResult(true,"gsl",…)`; fallback `FS q` → Success con `Kind="fs"` y confirmación limitada. | `…Nv.cs#L23-L102` |
| `IsLogoProvisionedAsync` | Consultable solo vía `GS ( L` fn=64; con kind `"fs"` → `false` best-effort. | `…Nv.cs#L108-L127` |
| `ClearLogoAsync` | gsl → `GS ( L` fn=66 delete; fs → redefine raster mínimo vacío. | `…Nv.cs` |

## 2. Constantes operativas (v1.0.13)

| Constante | Valor | Significado | Fuente |
|---|---|---|---|
| `CHUNK_SIZE` | **256** | Bytes por bloque de escritura (write normal y heavy NV); tamaño fijo, no por contenido. Comentario: "puede bajarse a 128 para impresoras más sensibles". | `BluetoothPrinterTransport.cs#L188`, `…Nv.cs#L82` |
| UUID SPP | `00001101-0000-1000-8000-00805F9B34FB` | Service record RFCOMM estándar de Serial Port Profile. | `BluetoothPrinterTransport.cs#L110` |
| `POLL_EVERY_N_CHUNKS` | 1 | Consultar status antes de CADA bloque. | `…Detection.cs#L16-L18` |
| `MAX_READY_POLLS` | 10 | Reintentos esperando `Ready` antes de escribir igual (no deadlock). | `…Detection.cs#L19-L20` |
| `READY_POLL_DELAY_MS` | 50 | Delay entre polls mientras reporta `Busy`. | `…Detection.cs#L21-L22` |
| `STATUS_TIMEOUT_MS` | 350 | Timeout de cada consulta de status: el envío nunca cuelga por polling. | `…Detection.cs#L23-L24` |
| Pacing fallback | `max(profile.ByteDelayMs, 1)` ms | Una vez por bloque (no por byte). | `BluetoothPrinterTransport.cs#L190-L192` |
| Pacing heavy NV | 1 ms/bloque fijo | `WriteHeavyAsync`, sin status gating ni perfil. | `…Nv.cs#L79-L90` |

## 3. Comandos ESC/POS que maneja el transport

Builders/sondeos **privados**; **no** usan `EscPosCommands` de `MotorDsl.Rendering`
(`…Nv.cs#L129`).

| Comando | Bytes | Uso | Fuente |
|---|---|---|---|
| `DLE EOT n=1` | `10 04 01` | Sondeo de feedback (fase 2, ×3 con 400 ms) y status por bloque (fase 3): online/offline. | `…Detection.cs#L55,#L128` |
| `DLE EOT n=2` | `10 04 02` | Fast-fail hardware: tapa abierta bit2 `0x04`, paper-end stop bit5 `0x20`. | `…Detection.cs#L166-L174` |
| `DLE EOT n=4` | `10 04 04` | Fast-fail hardware: sensor de papel — paper end bits 5,6 (`0x60`). | `…Detection.cs#L159-L164` |
| `GS ( L` fn=48 | `1D 28 4C 02 00 30 30` | Query **no intrusiva**: capacidad restante del área NV graphics (sondeo NV, fase 2). Solo lectura. | `…Detection.cs#L76-L81` |
| `GS ( L` fn=64 | `1D 28 4C 02 00 30 40` | Query de keycodes NV definidos (verificación post-define, `IsLogoProvisionedAsync`). | `…Nv.cs#L108-L127` |
| `GS ( L` fn=67 | `1D 28 4C pL pH 30 43 30 kc1 kc2 01 xL xH yL yH 31 [bits]` | DEFINE NV graphics raster por keycode (`xL xH` = ancho en **dots**). | `…Nv.cs#L131-L159` |
| `GS ( L` fn=66 | `1D 28 4C 04 00 30 42 kc1 kc2` | DELETE del NV graphics del keycode. | `…Nv.cs#L161-L170` |
| `GS I 67` | `1D 49 43` | Transmit printer ID (model name) → `ModelId` best-effort. | `…Detection.cs#L98-L113` |
| `FS q` | `1C 71 01 xL xH yL yH [bits]` | Define NV bit image clásica #1 (fallback; `xL xH` = **bytes por fila**; layout por impresora, sin garantía). | `…Nv.cs#L172-L188` |
| `GS v 0` | `1D 76 30 m xL xH yL yH [bits]` | **No se emite**: se **parsea** como input de `ProvisionLogoAsync` (mismo formato inline de la app). | `…Capabilities.cs#L82-L101` |

**Semántica del status `DLE EOT n=1`**: bits fijos `bit0=0, bit1=1, bit4=1, bit7=0` (máscara
`0b1001_0011 == 0b0001_0010`, sanity check anti-ruido/eco); `bit3 (0x08)` = offline → `Busy`
(`…Capabilities.cs#L24-L60`).

## 4. Tipos internos relevantes (no públicos)

| Tipo | Rol | Fuente |
|---|---|---|
| `enum PrinterStatus { Ready, Busy, Unknown }` | Resultado de un sondeo de status. | `…Capabilities.cs#L9-L14` |
| `ChunkBuffer(data, size)` | Chunker puro → `ArraySegment<byte>` contiguos sin copiar; reensamblado exacto. | `…Chunking.cs#L17-L27` |
| `ParseGsV0` | Parsea header `1D 76 30 m xL xH yL yH` → `(widthBytes, heightDots, bits)`. | `…Capabilities.cs#L82-L101` |
| `NextPacingDecision` | Latch de degradación: un `Unknown` degrada a pacing fijo por el resto del envío. | `…Capabilities.cs#L62-L78` |

---

## 🤖 Para agentes

- **Superficie pública real**: solo `BluetoothPrinterTransport` + `AddBluetoothPrinterTransport`. Todo lo ESC/POS es privado — no lo llames directamente ni asumas que hay un `EscPosCommands` compartido aquí.
- **`Kind == "bluetooth"`** (literal, minúsculas). El servicio enruta por este string (`OrdinalIgnoreCase`).
- **Solo Android imprime**: en iOS los métodos de I/O lanzan `PlatformNotSupportedException`; en otras plataformas son no-op/`false`. No generes código que asuma impresión BT en iOS.
- **Discover = solo emparejados**: `BondedDevices`, no discovery activo. Si la impresora no está emparejada en Ajustes de Android, no aparece.
- **No agregues retry aquí**: ante `IOException` el transport invalida y relanza **sin envolver**; el retry/reconexión es del `ThermalPrinterService`.
- **Hardware ≠ IOException**: papel/tapa lanzan `PrinterHardwareException` (clasificada `Hardware` → no reintenta). Un `IOException` sí dispara reconexión.
- **`CHUNK_SIZE = 256`** es fijo por tamaño (no por LF): el bitmap contiene `0x0A` de datos; nunca partas por salto de línea.
- **NV FS es "confirmación limitada"**: `NvLogoResult(true, "fs", …)` NO garantiza el logo; verificá con impresión de prueba. Solo `"gsl"` se verifica por query de keycodes.
