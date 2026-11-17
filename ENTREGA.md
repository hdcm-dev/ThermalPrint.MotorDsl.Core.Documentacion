# Entrega de cambios a este repositorio

Cómo llega un cambio a `main` del repositorio de documentación de MotorDsl (`PrintThermal_Motor_Maui.Documentacion`).

## 1. Delegación del merge

Los cambios entran por pull request con commit de merge (nunca `squash` ni `rebase`), y el agente que conduce la unidad lo fusiona él mismo siguiendo `Knowledge-Conformacion-Pull-Request-Automatico` (IA.Knowledge.Base), con la guarda G1–G4.

| Campo | Valor | Origen |
|---|---|---|
| Estado | Merge delegado al agente | Asentado el 2026-11-17 en la unidad que regenera la ia-db sobre `0f8413d` |
| Fecha | 2026-10-25 | Regla del PO para todos los PR del espacio de trabajo; asentada aquí el 2026-11-17 |
| Decidió | Fernando Filipuzzi, Product Owner | 2026-10-25: «siempre para conformar los pr sigue `IA/IA.Knowledge.Base/Knowledges/Knowledge-Conformacion-Pull-Request-Automatico.md`»; 2026-11-17, en `PROMPTs/Indexado/Crear-Indexado.md`: «Al finalizar actualizar, changelog, stage, commits y push siguiendo este conocimiento `/IA/IA.Knowledge.Base/Knowledges/Knowledge-Conformacion-Pull-Request-Automatico.md`» |
| Responsable | El agente que conduce la unidad: abre el PR, corre la guarda, fusiona y borra la rama | `Knowledge-Conformacion-Pull-Request-Automatico` §2 (actor A) |
| Techo | 30 minutos | Mismo valor que las delegaciones de IA.CDD y Research.IA-DeviceManager.Core |
| Intervalo | 20 segundos | Ídem |
| Control G3 | Workflow `Verificar` (`.github/workflows/verificar.yml`), corre `scripts/verificar_ia_db.py` en cada PR | Nace con esta unidad: sin CI no hay G3 |

**Excepción y revocación.** La delegación es revocable por unidad: un cuestionamiento particular del PO sobre una unidad, o una reserva (decisión que no es del agente, criterio que no se cumple, efecto no medido), la vuelve manual y el agente entrega el enlace sin fusionar.

## 2. Guardas

| Guarda | Qué pide |
|---|---|
| G1 | La cabeza del PR es el SHA auditado |
| G2 | `mergeable == true` y `mergeable_state == clean` |
| G3 | Al menos una corrida de `Verificar` para ese SHA, todas en éxito |
| G4 | Ninguna reserva declarada |

## 3. Verificador

```bash
python3 scripts/verificar_ia_db.py
```

Mira los enlaces internos de `ia-db/` y que la tabla de §1 tenga valor y origen en sus campos. **No mira** los enlaces al repositorio de código (no se clona en CI), ni si lo que dice cada índice es cierto: eso lo verifica la regeneración contra el código.
