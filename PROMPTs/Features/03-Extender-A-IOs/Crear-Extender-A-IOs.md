

# Tool-Prompt — Prompt extender ios libreria nuget

> **Invocación**:
> - `Lee y ejecuta /DEV/ThermalPrint.MotorDsl.Core.Documentacion/PROMPTs/03-Extender-A-IOs/Crear-Extender-A-IOs.md`
> Overview: Prompt extender ios libreria nuget

---

## Contexto

  contexto actual
 
  Leer `/DEV/ThermalPrint.MotorDsl.Core.Documentacion/ia-db/README.md`, es una librería para integración de impresoras Térmicas e impresión de documentos DSL en maui.

   Leer `/DEV/ThermalPrint.MotorDsl.Core.Documentacion/Analisis/03-Analisis-IOs/Nuget-Multiplaforma.md`, es un analisis del desarrollo actual

  Actualmente el desarrollo se encuentra planteado para Android, dicha libreria se distribuye bajo librerias nuget.

---

## Objetivos

  Añadir soporte para dispositivos IOs.

---

## Solicitudes

  1- Generar un plan de evaluación el desarrollo actual generando y ordenando el plan en subtareas con asignación de subagentes para cada subtarea bajo la especialdiad que le corresponda a cada subagente. Luego plantear alternativas para dar soporte a dipositivos IOs. Por cada alternativa se deberá considerar como quedaría la estructura final de la solución, que cambios e implicancias se darían. Me queda la duda cuando instalo el nuget, luego cuando compilo para el target android y ios que tome el nuget que corresponda a la plataforma objetivo para compilar.

  2- Planifica extender las librerias nuget para ios además de la existente desarrollo para android.

  3- Actualizar la documentación involucrada, siguiendo el profile:  `/IA/IA.Prompts/PromptFramework/Profiles/Study-Guide-Documentation.md`

  4- El host actual no tiene sdk instalado, trabajar a traves de un devcontainer para ensamblar y testear. Ajustar los workflow si se necesitan (estos workflow fueron editados para que trabajen con runners locales, el runner ( runs-on: [self-hosted, i7infra-dev]) ahora esta corriendo en el host local, github llama a ese, su configuración esta dada por `/Repos-Docker/Docker.RunnerGitHub/docker/runner-github/runner-github-dev/runner-github-dev/Dockerfile` )

---

## Reglas

 - No inventar información.

 - Toda afirmación deberá estar respaldada por evidencias verificables.

 - avisar cuando haya que cerrar y mezclar el PR.


