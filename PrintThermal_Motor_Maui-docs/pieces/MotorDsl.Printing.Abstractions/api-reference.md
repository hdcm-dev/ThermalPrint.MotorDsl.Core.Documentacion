---
doc_id: MotorDsl.Printing.Abstractions-api-reference
doc_type: api-reference
title: MotorDsl.Printing.Abstractions — referencia de API
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

# API — MotorDsl.Printing.Abstractions

> Superficie pública de la pieza (namespace `MotorDsl.Printing`) en **v1.0.13 @83677eb**. Los
> `#Lx-Ly` valen para esa revisión. Ver también [README](./README.md) y
> [guía de extensión](./extension-guide.md).

## 1. Contratos

| Interfaz | Responsabilidad | Miembros clave | Archivo |
|---|---|---|---|
| `IThermalPrinterTransport` | Capa física de UN medio de transporte; solo mueve bytes y detecta capacidades. | `Kind`, `IsConnected`, `CurrentDevice`, `Capabilities` (default `null`), `DiscoverAsync`, `ConnectAsync(deviceId)`, `DisconnectAsync`, `WriteBytesAsync(data, profile)`, `ProvisionLogoAsync` / `IsLogoProvisionedAsync` / `ClearLogoAsync` (defaults no-op) | `Contracts/IThermalPrinterTransport.cs#L5-L29` |
| `IThermalPrinterService` | Fachada/orquestador: ciclo de vida, retry, eventos, historial de fallos. `INotifyPropertyChanged`. | `IsConnected`, `CurrentDevice`, `ConnectionState`, `LastError`, `CurrentCapabilities`, `RecentFailures`, `ClearFailures()`, eventos `ErrorOccurred`/`DevicesDiscovered`, `DiscoverDevicesAsync`, `ConnectAsync`, `DisconnectAsync`, `ReconnectAsync`, `SendBytesAsync`, `ProvisionLogoAsync`/`IsLogoProvisionedAsync`/`ClearLogoAsync` | `Contracts/IThermalPrinterService.cs#L6-L37` |
| `IDiagnosticsReportProvider` | Captura y serializa el snapshot de diagnóstico. | `Build(notes?, includePii=false)`, `ToJson(report)`, `ToPlainText(report)`, `ToDslJson(report, paperWidthChars=32)` | `Contracts/IDiagnosticsReportProvider.cs#L7-L26` |

### 1.1 `IThermalPrinterTransport` (firma exacta)

```csharp
public interface IThermalPrinterTransport
{
    string Kind { get; }                    // "bluetooth", "usb", ...
    bool IsConnected { get; }
    PrinterDevice? CurrentDevice { get; }

    // null hasta conectar/detectar; los transports no aplicables (iOS, fakes) devuelven null.
    PrinterCapabilities? Capabilities => null;

    Task<IReadOnlyList<PrinterDevice>> DiscoverAsync(CancellationToken ct = default);
    Task<bool> ConnectAsync(string deviceId, CancellationToken ct = default);
    Task DisconnectAsync();
    Task WriteBytesAsync(byte[] data, PrinterProfile profile, CancellationToken ct = default);

    // Aprovisionamiento NV. gsV0Bytes = mismo formato GS v 0 inline que produce la app.
    // Defaults no-op para transports no aplicables.
    Task<NvLogoResult> ProvisionLogoAsync(byte[] gsV0Bytes, int keycode, CancellationToken ct = default)
        => Task.FromResult(new NvLogoResult(false, null, "transport no soporta NV"));
    Task<bool> IsLogoProvisionedAsync(int keycode, CancellationToken ct = default)
        => Task.FromResult(false);
    Task ClearLogoAsync(int keycode, CancellationToken ct = default)
        => Task.CompletedTask;
}
```
Procedencia: `src/MotorDsl.Printing.Abstractions/Contracts/IThermalPrinterTransport.cs#L5-L29`.

## 2. `ThermalPrinterService` — API del orquestador

Implementa `IThermalPrinterService`. Archivo: `Services/ThermalPrinterService.cs` (282 líneas).

| Miembro | Firma | Comportamiento | Fuente |
|---|---|---|---|
| ctor | `ThermalPrinterService(IEnumerable<IThermalPrinterTransport> transports, IPrintErrorHandler errorHandler)` | Lanza `InvalidOperationException` si **no** hay ningún transport registrado. | `#L83-L91` |
| `DiscoverDevicesAsync` | `Task<IReadOnlyList<PrinterDevice>> DiscoverDevicesAsync(string? kind = null, CancellationToken ct = default)` | Estado `Scanning`; itera todos los transports (filtro opcional por `Kind`, `OrdinalIgnoreCase`); el error de un transport no aborta a los demás; dispara `DevicesDiscovered`; restaura `Connected`/`Disconnected`. | `#L93-L131` |
| `ConnectAsync` | `Task<bool> ConnectAsync(PrinterDevice device, CancellationToken ct = default)` | Enruta por `device.Kind`; sin transport → `Failed` + `PrintError` de tipo `Protocol`. Éxito → guarda `_activeTransport`, `Connected`. | `#L133-L172` |
| `DisconnectAsync` | `Task DisconnectAsync()` | Cierra el transport activo (errores → `LastError`+evento), limpia estado, `Disconnected`. | `#L174-L191` |
| `ReconnectAsync` | `Task<bool> ReconnectAsync(CancellationToken ct = default)` | `null` device → `false`; estado `Reconnecting`; reusa `ConnectAsync(CurrentDevice)`. | `#L193-L199` |
| `SendBytesAsync` | `Task SendBytesAsync(byte[] data, PrinterProfile? profile = null, PrintRetryOptions? retry = null, CancellationToken ct = default)` | Defaults `profile = Thermal58mm`, `retry = new PrintRetryOptions()`. Loop de retry con backoff + reconexión silenciosa; fallo definitivo → `RecordFailure` + relanza. Sin transport activo → `InvalidOperationException`. | `#L201-L236` |
| `ProvisionLogoAsync` | `Task<NvLogoResult> ProvisionLogoAsync(byte[] gsV0Bytes, int keycode, CancellationToken ct = default)` | Delega en el transport activo; sin conexión → `NvLogoResult(false, null, "no conectado")`. | `#L65-L71` |
| `IsLogoProvisionedAsync` / `ClearLogoAsync` | (delegación) | Delegan en `_activeTransport`; sin transport → `false` / `Task.CompletedTask`. | `#L73-L77` |
| `CurrentCapabilities` | `PrinterCapabilities?` (get) | Delega en `_activeTransport?.Capabilities`. | `#L53` |
| `RecentFailures` / `ClearFailures` | `IReadOnlyList<PrintFailureEntry>` / `void` | Snapshot thread-safe del ring buffer / limpieza. | `#L55-L63` |
| `RecordFailure` | `internal void RecordFailure(PrintFailureEntry entry)` | Ring buffer `MAX_FAILURES = 20`; descarta el más viejo. `internal` (visible a `MotorDsl.Tests`). | `#L246-L256` |

### 2.1 Retry — parámetros efectivos

| Parámetro | Default | Origen |
|---|---|---|
| `PrintRetryOptions.MaxRetries` | 3 | `MotorDsl.Core/Models/PrintError.cs#L60-L64` |
| `PrintRetryOptions.InitialDelayMs` | 500 | `MotorDsl.Core/Models/PrintError.cs#L60-L64` |
| Backoff | `InitialDelayMs * 2^(intento-1)` (500 → 1000 → 2000 ms) | `Services/ThermalPrinterService.cs#L230` |
| Clasificación retry/abort | `Connection`/`Timeout`/`Unknown` → retry; `Hardware`/`Protocol` → abort | `MotorDsl.Core/Printing/DefaultPrintErrorHandler.cs#L16-L28` |

## 3. Modelos (namespace `MotorDsl.Printing`)

| Modelo | Definición | Notas | Fuente |
|---|---|---|---|
| `PrinterDevice` | `record (string Id, string Name, string Kind, bool IsPaired = false)` | `ToString()` = `"Name (Id)"`. | `Models/PrinterDevice.cs#L3-L6` |
| `PrinterProfile` | `class` con delays de pacing (`Name`, `LineDelayMs=150`, `ByteDelayMs=5`, `InitDelayMs=100`, `FinalDelayMs=500`, `QrDelayMs=300`, `ImageDelayMs=500`, `CutDelayMs=500`, `InitCommandDelayMs=300`) | Presets estáticos: `Thermal58mm`, `Real58HB6` (58HB6-6101, basado en self-test). | `Models/PrinterProfile.cs#L3-L37` |
| `PrinterCapabilities` | `record (CapabilitySupport StatusFeedback, CapabilitySupport NvGraphics, string? NvGraphicsKind, string? ModelId)` | Inmutable, detectado al conectar. Factory `Unknown()` = todo Unknown/null. `NvGraphicsKind` ∈ `"gsl"`\|`"fs"`\|null. | `Models/PrinterCapabilities.cs#L7-L16` |
| `CapabilitySupport` | `enum { Unknown, NotDetected, Supported }` | Tri-estado deliberado, nunca bool. | `Models/CapabilitySupport.cs#L7-L17` |
| `PrinterConnectionState` | `enum { Disconnected, Scanning, Connecting, Connected, Reconnecting, Failed }` | — | `Models/PrinterConnectionState.cs#L3-L11` |
| `PrintStrategySelector` | `static string RecommendTarget(PrinterCapabilities? caps, bool docNeedsGraphics)` | Helper puro; `escpos` si `NvGraphics==Supported`, si no `escpos-bitmap`. `docNeedsGraphics` hoy se ignora (reservado). | `Models/PrintStrategySelector.cs#L14-L20` |
| `PrintFailureEntry` | `record (DateTimeOffset Timestamp, string DeviceId, string DeviceName, string DeviceKind, PrinterCapabilities Capabilities, string ErrorType, string ErrorMessage, int Attempts, int BytesLength, string? RenderTarget)` | Identidad **cruda** (masking al reportar); **nunca** payload, solo `BytesLength`. | `Models/PrintFailureEntry.cs#L8-L18` |
| `NvLogoResult` | `record (bool Success, string? Kind, string? Message)` | Honestidad FS: `Success` con `Kind="fs"` lleva `Message` de advertencia (confirmación limitada). | `Models/NvLogoResult.cs#L9` |
| `DiagnosticsReport` | `record` raíz (`Libraries`, `App`, `Device`, `Printer?`, `Permissions?`, `CapturedAt`, `Notes=null`, `Failures=null`) | Sub-records `LibraryInfo`, `AppInfoSnapshot`, `DeviceInfoSnapshot`, `PrinterInfoSnapshot`, `PermissionsSnapshot`. `Failures` opcional para no romper llamadores. | `Models/DiagnosticsReport.cs#L61-L71` |
| `DiagnosticsBuilder` | Helpers **puros** estáticos (testeables sin MAUI) | `MaskMac(id)`, `CapabilitiesToDictionary`, `BuildPrinterSnapshot(service, includePii)`, `BuildFailures(service, includePii)`. Claves dict: `supports_status_feedback`, `supports_nv_graphics`, `nv_graphics_kind`, `model_id`. | `Models/DiagnosticsBuilder.cs#L10-L105` |

### 3.1 `PrinterProfile` — presets

```csharp
public static PrinterProfile Thermal58mm => new()
{
    Name = "thermal_58mm",
    LineDelayMs = 150, ByteDelayMs = 5, InitDelayMs = 100, FinalDelayMs = 500
};

// Perfil real: 58HB6-6101 (basado en self-test)
public static PrinterProfile Real58HB6 => new()
{
    Name = "58HB6-6101",
    LineDelayMs = 150, ByteDelayMs = 5, InitDelayMs = 100, FinalDelayMs = 500,
    QrDelayMs = 300, ImageDelayMs = 500, CutDelayMs = 500, InitCommandDelayMs = 300
};
```
Procedencia: `src/MotorDsl.Printing.Abstractions/Models/PrinterProfile.cs#L15-L36`.

## 4. Eventos

| Evento | Args | Contenido | Fuente |
|---|---|---|---|
| `ErrorOccurred` | `PrintErrorEventArgs` | `PrintError Error` (envuelve el `PrintError` de `MotorDsl.Core`). | `Events/PrintErrorEventArgs.cs#L5-L9` |
| `DevicesDiscovered` | `DevicesDiscoveredEventArgs` | `IReadOnlyList<PrinterDevice> Devices`. | `Events/DevicesDiscoveredEventArgs.cs#L3-L7` |
| `PropertyChanged` | `PropertyChangedEventArgs` | Vía `INotifyPropertyChanged` (patrón MVVM: `IsConnected`, `CurrentDevice`, `ConnectionState`, `LastError`). | `Services/ThermalPrinterService.cs#L275-L280` |

## 5. Inyección de dependencias

```csharp
public static IServiceCollection AddMotorDslPrinting(this IServiceCollection services)
{
    services.TryAddSingleton<IPrintErrorHandler, DefaultPrintErrorHandler>();
    services.TryAddSingleton<IThermalPrinterService, ThermalPrinterService>();
    return services;
}
```
Procedencia: `src/MotorDsl.Printing.Abstractions/MotorDslPrintingServiceCollectionExtensions.cs#L10-L15`.

- `TryAddSingleton` (no `AddSingleton`): permite al consumer **sobreescribir** registrando su propia
  implementación **antes** de llamar a `AddMotorDslPrinting()`.
- El servicio necesita **al menos un** `IThermalPrinterTransport` en el contenedor (los registra
  cada pieza de transport, p. ej. `AddBluetoothPrinterTransport()`), o el ctor lanza
  `InvalidOperationException`.

## 6. Uso mínimo (extremo a extremo)

```csharp
var svc = provider.GetRequiredService<IThermalPrinterService>();

var devices = await svc.DiscoverDevicesAsync(kind: "bluetooth");
await svc.ConnectAsync(devices[0]);

// Recomendación de estrategia (la decisión final es de la app):
string target = PrintStrategySelector.RecommendTarget(svc.CurrentCapabilities, docNeedsGraphics: true);

// bytes = salida del renderer elegido (escpos | escpos-bitmap)
await svc.SendBytesAsync(bytes, PrinterProfile.Thermal58mm);
```
Procedencia de los métodos: `Contracts/IThermalPrinterService.cs#L26-L30`,
`Models/PrintStrategySelector.cs#L14-L20`.

---

## 🤖 Para agentes

- **Namespace único**: todo el contrato público es `MotorDsl.Printing` (no `MotorDsl.Printing.Abstractions`).
- **No inventes un `IThermalPrinterService.SendAsync(string)`**: el único envío es `SendBytesAsync(byte[], PrinterProfile?, PrintRetryOptions?, CancellationToken)` — la pieza opera **bytes ya renderizados**, no DSL.
- **`SendBytesAsync` no devuelve `RenderResult`**: es `Task`; el éxito es "no lanzó". El fallo definitivo relanza `Exception("Print failed after N attempt(s)…")` tras registrar **una** `PrintFailureEntry`.
- **Capacidades = tri-estado**: nunca trates `CapabilitySupport` como bool. `NotDetected` ≠ "no soporta"; puede ser "estaba ocupada".
- **`RecordFailure` es `internal`** (solo `MotorDsl.Tests`): no forma parte de la API pública; no lo llames desde app.
- **DI**: el servicio se registra con `TryAdd` (sobrescribible); los transports con `AddSingleton` (coexisten varios). No conviertas los transports a `TryAdd`: colapsarías el multi-transport.
- **Nunca loguees el payload**: `PrintFailureEntry` guarda `BytesLength`, no los bytes; el MAC se enmascara al construir el reporte (`DiagnosticsBuilder.MaskMac`), no al registrar.
- **Extensión**: para un medio nuevo implementa `IThermalPrinterTransport` (ver [extension-guide](./extension-guide.md)); **no** modifiques `ThermalPrinterService`.
