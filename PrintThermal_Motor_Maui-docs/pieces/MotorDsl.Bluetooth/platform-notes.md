---
doc_id: MotorDsl.Bluetooth-platform-notes
doc_type: platform-notes
title: MotorDsl.Bluetooth — notas de plataforma
version: 1.0.0
status: draft
origin: reverse-engineered
confidence: high
owner: equipo-motordsl
last_review: 2026-07-15
audience: [dev, arquitectura, qa, agentes-automaticos]
classification: uso-interno
source_ref: v1.0.13 @83677eb
---

# Notas de plataforma — MotorDsl.Bluetooth

> Soporte por plataforma, mínimos de OS, permisos y flags de build del transport Bluetooth Classic
> SPP en **v1.0.13 @83677eb**. Ver [README](./README.md) y [API](./api-reference.md).

## 1. Matriz de soporte

| Plataforma | `#if` | Discover / Connect / Disconnect / Write | `Capabilities` | Fuente |
|---|---|---|---|---|
| **Android** | `#if ANDROID` | Soportado (RFCOMM SPP sobre dispositivos emparejados). | `_capabilities` (detectadas al conectar) | `BluetoothPrinterTransport.cs#L56-L96,#L100-L143,#L181-L250`, `#L40` |
| **iOS** | `#elif IOS` | **Lanza** `PlatformNotSupportedException` en los 4 métodos de I/O. | `null` | `BluetoothPrinterTransport.cs#L92-L93,#L136-L138,#L171-L173,#L251-L253`, `#L42` |
| **Otras** | `#else` | `ConnectAsync` → `false`; `WriteBytesAsync` no-op; discover devuelve lista vacía. | `null` | `BluetoothPrinterTransport.cs#L139-L141,#L254-L256` |

### 1.1 Mensaje de iOS (literal)

```
iOS no soporta Bluetooth Classic SPP. Usar BLE o impresion por red.
```
Emitido por `PlatformNotSupportedException` en `DiscoverAsync`, `ConnectAsync`, `DisconnectAsync` y
`WriteBytesAsync`. Procedencia: `BluetoothPrinterTransport.cs#L93,#L138,#L173,#L253`.

> **Nota de diseño (verificada)**: los TFMs incluyen `net10.0-ios` aunque iOS no imprima. La rama
> iOS existe para que el paquete **compile y se referencie** desde apps multiplataforma sin
> `#if` en el llamador; la app decide en runtime (o por capacidades) no usar BT en iOS. La
> alternativa recomendada en el mensaje es **BLE o impresión por red**.

## 2. Mínimos de OS

| Componente | Android | iOS | Fuente |
|---|---|---|---|
| `MotorDsl.Bluetooth` (esta pieza) | **24.0** | 15.0 | `src/MotorDsl.Bluetooth/MotorDsl.Bluetooth.csproj#L10-L11` |
| `MotorDsl.Maui` (UI del stack) | **25.0** | 15.0 | `src/MotorDsl.Maui/MotorDsl.Maui.csproj#L11-L12` |

### 2.1 Piso efectivo de OS

Una app MAUI que consuma **ambas** piezas queda limitada por el **máximo** de los mínimos: aunque
`MotorDsl.Bluetooth` compila desde Android **24.0**, `MotorDsl.Maui` exige **25.0**, así que el
**piso efectivo de la app es Android 25.0**.

| Escenario de consumo | Piso Android efectivo |
|---|---|
| Solo `MotorDsl.Bluetooth` (sin UI MAUI del stack) | 24.0 |
| `MotorDsl.Bluetooth` + `MotorDsl.Maui` (stack completo) | **25.0** |

Fuentes: `MotorDsl.Bluetooth.csproj#L11` (24.0) y `MotorDsl.Maui.csproj#L12` (25.0).

## 3. Permisos Android

| Permiso | ¿Verificado en el código de esta pieza? | Cuándo / para qué |
|---|---|---|
| `BLUETOOTH_CONNECT` | ✅ **Sí**: chequeado en runtime en `DiscoverAsync` cuando `SdkInt >= S` (API 31+); si no está `Granted`, lanza `Exception("Permiso BLUETOOTH_CONNECT no otorgado…")`. | Conectar y enumerar dispositivos emparejados en Android 12+. |
| `BLUETOOTH_SCAN` | ⚠️ **No verificado en esta pieza** (no referenciado en el código ni hay `AndroidManifest.xml` en el proyecto). Requerido por la plataforma para descubrimiento BT en Android 12+ (API 31+). | Descubrimiento activo de dispositivos (API 31+). Lo declara el manifest de la **app host**. |
| `ACCESS_FINE_LOCATION` | ⚠️ **No verificado en esta pieza** (ídem). Requerido por la plataforma para scan BT en Android ≤ 11 (API < 31). | Descubrimiento BT en Android 11 e inferiores. Lo declara el manifest de la **app host**. |

Procedencia del chequeo verificado: `BluetoothPrinterTransport.cs#L63-L71`.

> **Importante (trazabilidad)**: `MotorDsl.Bluetooth` **no** incluye un `AndroidManifest.xml`
> propio (búsqueda sin resultados en `src/MotorDsl.Bluetooth/`). La declaración de
> `uses-permission` es responsabilidad del **manifest de la aplicación host**. El único permiso que
> la pieza valida en runtime es `BLUETOOTH_CONNECT`; `BLUETOOTH_SCAN` y `ACCESS_FINE_LOCATION` se
> listan por requisito de la plataforma Android, no por evidencia en el código de esta pieza
> («No verificado» a nivel de pieza).
>
> Recordatorio operativo del transport: `DiscoverAsync` solo enumera dispositivos **emparejados**
> (`BondedDevices`), no hace discovery activo — por eso el chequeo explícito es de
> `BLUETOOTH_CONNECT` y no de `BLUETOOTH_SCAN` (`BluetoothPrinterTransport.cs#L76-L86`).

## 4. Flags de build (Android)

| Flag | Valor | Motivo | Fuente |
|---|---|---|---|
| `AndroidLdFlags` | `-Wl,-z,max-page-size=16384` | Alinea las librerías nativas a **páginas de 16 KB**, requisito de compatibilidad de dispositivos/Android recientes que usan page size de 16 KB. | `MotorDsl.Bluetooth.csproj#L28-L30` |

> El bloque `TargetPlatformVersion 35.0` está **comentado** en el csproj (no activo en v1.0.13):
> `MotorDsl.Bluetooth.csproj#L23-L27`.

## 5. Resumen operativo

| Pregunta | Respuesta corta |
|---|---|
| ¿Imprime en iOS? | No. Lanza `PlatformNotSupportedException`; usar BLE o impresión por red. |
| ¿Descubre no emparejados? | No. Solo `BondedDevices` (emparejados en Ajustes de Android). |
| ¿Piso de Android del stack completo? | 25.0 (impuesto por `MotorDsl.Maui`; la pieza BT sola es 24.0). |
| ¿Qué permiso valida el código? | `BLUETOOTH_CONNECT` (API 31+). El resto los declara la app host. |
| ¿Flag de build especial? | `AndroidLdFlags` para páginas de 16 KB. |

## Enlaces

- [README de la pieza](./README.md) · [Referencia de API](./api-reference.md).
- Contrato: [`MotorDsl.Printing.Abstractions`](../MotorDsl.Printing.Abstractions/README.md).
- [Índice ia-db 04](../../../ia-db/indexes/04_impresion-transports.md) · [Glosario](../../GLOSSARY.md).
