

# Tool-Prompt — Prompt Integrador de documentación final

> **Invocación**:
> - `Lee y ejecuta /DEV/ThermalPrint.MotorDsl.Core.Documentacion/PROMPTs/02-Crear-Analisis-IOs/Crear-Analisis-IOs.md`
> Overview: Crear un unico documento final

---
## Contexto

  Leer `/DEV/ThermalPrint.MotorDsl.Core.Documentacion/ia-db/README.md`, es una librería para integración de impresoras Térmicas e impresión de documentos DSL en maui.

  Actualmente el desarrollo se encuentra planteado para Android, dicha libreria se distribuye bajo librerias nuget.

---

## Objetivos

  Añadir soporte para dispositivos IOs.

---

## Solicitudes

  1- Generar un plan de evaluación el desarrollo actual generando y ordenando el plan en subtareas con asignación de subagentes para cada subtarea bajo la especialdiad que le corresponda a cada subagente. Luego plantear alternativas para dar soporte a dipositivos IOs. Por cada alternativa se deberá considerar como quedaría la estructura final de la solución, que cambios e implicancias se darían. Me queda la duda cuando instalo el nuget, luego cuando compilo para el target android y ios que tome el nuget que corresponda a la plataforma objetivo para compilar.

  2- Generar el informe en:
  `/DEV/ThermalPrint.MotorDsl.Core.Documentacion/Analisis/03-Analisis-IOs/Nuget-Multiplaforma.md`


---

## Reglas

  - El documento markdown debe tener estar organizado en secciones jerarquizadas, y tener una tabla de contenidos, idear ejemplos prácticos concretos con explicaciones y analisis oridentados al maquetado de la solución tanto web como de datos, definiciones y glosario detallado, graficos mermaid.

 - No inventar información.

 - Toda afirmación deberá estar respaldada por evidencias verificables.

 - No modificar el código, no hacer push, ni commit, ni PR

---

# Framework

## Profiles

  Aplicar: 

  - `/IA/IA.Prompts/PromptFramework/Profiles/Study-Guide-Documentation.md`

