---
doc_id: MotorDsl.Extensions-api-reference
doc_type: api-reference
title: MotorDsl.Extensions — Referencia de API
version: 1.0.0
status: draft
origin: reverse-engineered
confidence: high
owner: equipo-motordsl
last_review: 2026-07-14
audience: [dev, agentes-automaticos]
classification: uso-interno
source_ref: "v1.0.13 @83677eb"
---

# MotorDsl.Extensions — Referencia de API

> Superficie pública del paquete `MotorDsl.Extensions`. Firmas verificadas contra
> **v1.0.13 @83677eb**.

## Superficie pública

### `MotorDslServiceCollectionExtensions` (static)

| Miembro | Firma | Propósito | Archivo |
|---|---|---|---|
| `AddMotorDslEngine` | `public static MotorDslBuilder AddMotorDslEngine(this IServiceCollection services)` | Registra el pipeline completo (singletons) y devuelve el builder fluent | `src/MotorDsl.Extensions/MotorDslServiceCollectionExtensions.cs#L14 @83677eb` |

### `MotorDslBuilder`

| Miembro | Firma | Propósito | Archivo |
|---|---|---|---|
| `Services` | `public IServiceCollection Services { get; }` | Escape hatch para registros manuales | `src/MotorDsl.Extensions/MotorDslBuilder.cs#L13 @83677eb` |
| ctor | `internal MotorDslBuilder(IServiceCollection services)` | Solo construible desde `AddMotorDslEngine` | `MotorDslBuilder.cs#L15 @83677eb` |
| `AddTemplates` | `public MotorDslBuilder AddTemplates(Action<InMemoryTemplateProvider> configure)` | Registra `ITemplateProvider` in-memory poblado por callback | `MotorDslBuilder.cs#L20 @83677eb` |
| `AddProfiles` | `public MotorDslBuilder AddProfiles(Action<InMemoryDeviceProfileProvider> configure)` | Registra `IDeviceProfileProvider` in-memory poblado por callback | `MotorDslBuilder.cs#L28 @83677eb` |
| `AddRenderer<TRenderer>` | `public MotorDslBuilder AddRenderer<TRenderer>() where TRenderer : class, IRenderer` | Registra un `IRenderer` custom singleton | `MotorDslBuilder.cs#L36 @83677eb` |

## Snippet — `AddMotorDslEngine` (registro completo)

```csharp
public static MotorDslBuilder AddMotorDslEngine(this IServiceCollection services)
{
    services.AddSingleton<IDslParser, DslParser>();
    services.AddSingleton<IEvaluator, Evaluator>();
    services.AddSingleton<ILayoutEngine, LayoutEngine>();
    services.AddSingleton<IRendererRegistry>(sp =>
    {
        var registry = new RendererRegistry();
        registry.Register(new TextRenderer());
        registry.Register(new EscPosRenderer());
        foreach (var renderer in sp.GetServices<IRenderer>())
            registry.Register(renderer);
        return registry;
    });
    services.AddSingleton<IDataValidator, DataValidator>();
    services.AddSingleton<ITemplateValidator, TemplateValidator>();
    services.AddSingleton<IProfileValidator, ProfileValidator>();
    services.AddSingleton<IDocumentEngine, DocumentEngine>();
    return new MotorDslBuilder(services);
}
```

Procedencia: `src/MotorDsl.Extensions/MotorDslServiceCollectionExtensions.cs#L14-L33 @83677eb`.

## Snippet — `MotorDslBuilder` (métodos fluent)

```csharp
public MotorDslBuilder AddTemplates(Action<InMemoryTemplateProvider> configure)
{
    var provider = new InMemoryTemplateProvider();
    configure(provider);
    Services.AddSingleton<ITemplateProvider>(provider);
    return this;
}

public MotorDslBuilder AddRenderer<TRenderer>() where TRenderer : class, IRenderer
{
    Services.AddSingleton<IRenderer, TRenderer>();
    return this;
}
```

Procedencia: `src/MotorDsl.Extensions/MotorDslBuilder.cs#L20-L40 @83677eb` (`AddProfiles` es análogo
a `AddTemplates` con `InMemoryDeviceProfileProvider` / `IDeviceProfileProvider`).

## Snippet — bootstrap real en tests

```csharp
var services = new ServiceCollection();
var builder = services.AddMotorDslEngine();
builder.AddRenderer<FakeRenderer>();

var sp = services.BuildServiceProvider();
var registry = sp.GetRequiredService<IRendererRegistry>();
Assert.NotNull(registry.GetRenderer("fake"));
```

Procedencia: `src/MotorDsl.Tests/Sprint08CoreTests.cs#L76-L83 @83677eb`.

## 🤖 Para agentes

- **Único punto de entrada**: `AddMotorDslEngine()` (extension sobre `IServiceCollection`). Devuelve
  `MotorDslBuilder`, no `IServiceCollection` — encadena `AddTemplates`/`AddProfiles`/`AddRenderer<T>`
  sobre él, o usa `.Services` para volver al `IServiceCollection`.
- **Todo se registra como singleton** (`MotorDslServiceCollectionExtensions.cs#L16-L31 @83677eb`).
- **El registry es una factory**: los `IRenderer` registrados por DI (incl. `AddRenderer<T>`) se
  añaden **después** de `TextRenderer`/`EscPosRenderer` base y **reemplazan** al base si comparten
  `Target`. Así se inyecta un ESC/POS con `IBitmapRasterizer` real.
- **No hay `AddData(...)`**: pese a existir `InMemoryDataProvider`, no hay método fluent para
  `IDataProvider`; regístralo vía `builder.Services` (`MotorDslBuilder.cs#L20-L40 @83677eb`).
- **`AddTemplates`/`AddProfiles` registran una instancia nueva en cada llamada**: llamadas repetidas
  dejan varios `ITemplateProvider`/`IDeviceProfileProvider` en el contenedor; la resolución simple
  toma el último (`MotorDslBuilder.cs#L20-L34 @83677eb`).
- **El `EscPosRenderer` base de la factory no recibe `IBitmapRasterizer`**: para bitmaps reales,
  registra un renderer propio (p. ej. con `AddRenderer<>`) que reemplace al base
  (`MotorDslServiceCollectionExtensions.cs#L23 @83677eb`; ver pieza `MotorDsl.Rendering`).
- **Providers no registrados por defecto**: `ITemplateProvider`, `IDeviceProfileProvider`,
  `IDataProvider`, `IPrintErrorHandler`, `IBitmapRasterizer`. Resuélvelos antes de usarlos.
- **Enlaces**: registro por target → [ia-db 03 §5](../../../ia-db/indexes/03_renderizado-base.md);
  términos → [`GLOSSARY.md`](../../GLOSSARY.md).
