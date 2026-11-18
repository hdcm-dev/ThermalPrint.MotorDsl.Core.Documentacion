# Reevaluación: publicación de MotorDsl 1.0.18 y dependencia de la app #62 (2026-11-17)

Pedido del PO: «reevalúa esto y proponeme una solución, no debiste haber caído en esto». Se revisan los puntos (2) y (4) del informe de conformación:

- (2) «Para publicar 1.0.18 con MotorDsl.Pax hace falta tu OK para crear el tag `v1.0.18`.»
- (4) «App #62 (PAX) espera a que MotorDsl.Pax esté publicado y a que #61 entre en `main`.»

Etapa de sólo lectura. No se tocaron repos, tags, runners ni secretos. Credencial: `fernandofilipuzzi-utn` por `git credential fill`, usada con `curl -K` y un archivo 0600 que se borró al terminar.

## 1. Hechos con evidencia

### 1.1 Cómo publica `cd-nuget.yml`

- Corre con `push` de tags `v*`, con `push` a `main` y con `workflow_dispatch` (`cd-nuget.yml:12-20`).
- Versión: un tag da `ref_name` sin la `v`; un dispatch da `inputs.version`; un push a `main` da `0.0.0-preview.<run_number>` (`:38-46`).
- El paso de publicación tiene `if: startsWith(github.ref, 'refs/tags/v') || github.event_name == 'workflow_dispatch'` (`:190`). Su clave es `secrets.NUGET_API_KEY` (`:195`).
- En la cabeza `1eb9000` de #13, `MotorDsl.Pax` va en `pack-platform` (macos-15) con `-p:PaxNeptune=false`, el conteo es 9 y se publica último. El comentario agregado dice que «MotorDsl.Pax sale SIN el binding NeptuneLite … el modo Real cae en Connection» (`git diff origin/main...1eb9000 -- .github/workflows/cd-nuget.yml`).

### 1.2 Cómo se publicaron las 1.0.x (API de Actions y registro de nuget.org)

| Tag | Corrida de `cd-nuget` | Resultado | Publicado en nuget.org (`motordsl.core`) |
|---|---|---|---|
| v1.0.14 | 31261932165 (tag) / 31263655797 (dispatch) | failure / **success** | 2026-08-08T15:09:02, por el dispatch |
| v1.0.15 | 32929872587 (tag, 04:20:51Z) | failure | 2026-08-26T04:20:34, **antes** del tag |
| v1.0.16 | 33021650595 (tag, 22:59:53Z) | failure en «Publish to NuGet.org»: `403 (The specified API key is invalid, has expired, or does not have permission…)` | 2026-08-26T22:59:40, **antes** del tag |
| v1.0.17 | 33124506560 (tag, 22:57:36Z) | failure en «Verificar que estén los 8»: «hay 16» (el `_work` arrastraba las `0.0.0-preview.42`) | 2026-08-27T22:57:19, **antes** del tag |

- Desde la 1.0.4, todas las corridas por tag fallan. Sólo publicaron por CI la v1.0.2, la v1.0.3 y el dispatch de la 1.0.14.
- Las 1.0.15, 1.0.16 y 1.0.17 llegaron a nuget.org entre 12 y 17 s antes de que existiera su tag. Eso coincide con `scripts/nuget/publish-motordsl-nuget.bat`, que publica desde la máquina del PO con `MOTORDSL_NUGET_API_KEY` y después crea y pushea el tag (`docs/09_devops/estrategia-versionado_v1.0.md:87-88`; `guia-publicacion-nuget_v1.0.md:202`).
- Secreto `NUGET_API_KEY`: `created_at` 2026-04-02, `updated_at` **2026-08-08T15:00:30Z** (`GET /repos/.../actions/secrets`). No cambió después del 403 del 2026-08-26.
  - **Inferido, no verificado:** un tag `v1.0.18` fallaría hoy en el mismo 403.
  - Además, `MotorDsl.Pax` es un ID nuevo en nuget.org, así que la clave necesita permiso para empujar paquetes nuevos que entren en su patrón.
- La falla del conteo 16 no se repetiría: desde el 2026-11-03 los runners borran `/_work/*` antes de cada arranque (registro interno de los runners).
- Los tags `v1.0.15`, `v1.0.16` y `v1.0.17` son anotados: tagger `fernandofilipuzzi-utn` y mensaje «Release 1.0.x». La credencial es la misma que usan los agentes, así que el tagger no prueba quién los creó. Lo que sí está medido es el orden: primero el push a nuget.org y después el tag.
- `motordsl.pax` en nuget.org: HTTP 404. `motordsl.core`, `.maui` y `.bluetooth` terminan en 1.0.17.

### 1.3 Los scripts de publicación no conocen MotorDsl.Pax

En `1eb9000`, ni `scripts/nuget/publish-motordsl-nuget.bat` (líneas 32-39 y 55: ocho paquetes) ni `scripts/nuget/tag-next-version.sh` (líneas 26-35, `PAQUETES=(` con ocho) mencionan Pax. `git grep -i pax 1eb9000 -- scripts/nuget docs/09_devops` no devuelve nada.

Consecuencia: si el PO publica como en la 1.0.15–1.0.17, con el `.bat` local, salen ocho paquetes 1.0.18 **sin** MotorDsl.Pax. Es un hueco de U3: el Núcleo 07 CA-07.1 pide «workflow empaqueta 9 y publica».

### 1.4 Delegación y autorización

- Conocimiento `Knowledge-Conformacion-Pull-Request-Automatico.md:39`: «Etiquetar, publicar o desplegar después del merge» queda afuera y le corresponde a «quien tiene a cargo, en el destino, la entrega y el despliegue». «Conforma los prs» **no** autoriza publicar.
- El `ENTREGA.md` de la librería que dice «Etiquetar y publicar no está delegado al agente» lo escribió el agente en esta feature (`0b86cbe`, PR #15). No cita una frase del PO para esa línea: repite el §0 del conocimiento.
- Sí está en el alcance aprobado:
  - el prompt: «llevarlo a la app» (`Agregar-PAX-A910s.md:7`) y «la integración en `cd-nuget.yml`» (`:59`);
  - Núcleo 07: CA-07.1 «empaqueta 9 y publica» y CA-07.3 «la app restaura la versión nueva».
- La publicación es externa e irreversible: en nuget.org una versión no se reemplaza, sólo se deslista. Por [[no-preguntas-menores-mesa-y-pr-propios]], es de las cosas que justifican interrumpir al PO.
- **Reserva de licencia, sin resolver** (`Implementacion/U2.md:24`): el material PAX no trae licencia ni términos de redistribución. «Publicar `MotorDsl.Pax` con binding en nuget.org (público) … requiere OK de PAX/PO». U3 la esquivó publicando sin binding (`U3.md:22`). P2, que se respondió por default, aprobaba «9 paquetes con el binding dentro de `MotorDsl.Pax`» (`Plan-Aprobado-Mesa.md:39`). El paquete público iba a salir distinto de lo aprobado y nadie se lo planteó al PO.

### 1.5 Versión

- Versión unificada: los nueve paquetes salen con un único `PACKAGE_VERSION` (`cd-nuget.yml:29-47`). [[nuget-version-unificada]] se cumple por construcción: todos a 1.0.18.
- El criterio de la memoria, «mayor entre la siguiente del feed de cada paquete y la del `.csproj`», da **1.0.18**. Es lo que calcularía `tag-next-version.sh` o el `.bat`, porque los `.csproj` no declaran versión (CHANGELOG:7-9).
- Discrepancia: `estrategia-versionado_v1.0.md:28` (SemVer: MINOR para funcionalidad nueva) y el Núcleo 07 §2, que infiere 1.1.0. La práctica del repo es subir sólo el parche: la 1.0.17 trajo funciones nuevas y un cambio de comportamiento. 1.0.18 sigue la regla del PO y la práctica. 1.1.0 sigue el documento. Se le señala al PO, no se le pregunta.

### 1.6 App: ¿#62 necesita MotorDsl.Pax publicado?

Respuesta: **no.**

- `<app>.csproj:228-247` en la rama de U6 (`bb0a606`):
  - Por omisión usa `MotorDslVersion` 1.0.17 y los siete paquetes de siempre.
  - `UsaMotorDslPax` es true **sólo** con TFM android **e** `Impresora=PAX`. Sólo entonces se suma `<PackageReference Include="MotorDsl.Pax">`, con `1.0.18-pax.local` y el feed `-p:MotorDslPaxFeed`.
- `WhiteLabel.props:99`: `Impresora` vale `BLUETOOTH` por omisión.
- Todo uso de `MotorDsl.Pax` en C# está dentro de `#if ANDROID && IMPRESORA_PAX`:
  - `MauiProgram.cs:18-20`;
  - `Services/Printing/PaxPrinterService.cs:1-146`;
  - `Services/Printing/PrinterErrorCatalog.cs:179-193`.
- CI de la app: `verificar-pr.yml:32` usa `TRIO_PROPS` sin `-p:Impresora`, y `:145-146` compila Debug android con eso, o sea BLUETOOTH. `grep -rn Impresora .github/` no da resultados: **ningún workflow compila un trío PAX**. La CI de #62 nunca restaura MotorDsl.Pax.
- Evidencia local de U6 (`Implementacion/U6.md:21-23`): el build por omisión (BLUETOOTH) termina con EXIT=0, 0 errores y sin `com.pax` en el manifiesto. Los builds PAX Real y PAX Simulado, con el feed local, también dan EXIT=0.
- API: #62 tiene `head` `bb0a6060` y `base` `feature/04-impresora-por-trio`, `mergeable_state` clean y **0 check-runs**. `verificar-pr` sólo corre en PR a `main` o `release/**` (`verificar-pr.yml:10-11`). La única dependencia real es estructural: #62 está apilado sobre #61.
- **Además, esperar el paquete publicado era contraproducente.** El paquete de nuget.org sale con `PaxNeptune=false`, y en modo Real responde `Connection` («Avisá a soporte»). Hacer lo que dice `<app>.csproj:224-226` («al publicar … se fija acá `MotorDslPaxVersion` a esa versión») dejaría el build PAX real **sin impresión**. Hoy ese build funciona con un feed local (fuera del repo), que sí lleva el binding (`U3.md:14-18`).

### 1.7 Dato nuevo sobre (1), que cambia la secuencia

Corrida 44204636651 de `CI - Tests` en #13:

- El job se creó a las 00:03:34Z y lo tomó el runner propio (`[self-hosted, ci-hdcm]`) a las 00:26:06Z. Terminó en **success** a las 00:26:44Z.
- #13 está `clean` (`GET /pulls/13`: open, `1eb9000`, clean).
- El runner no estaba caído: hubo unos 22 min de cola, coherente con la carga del host de CI de 17 sobre 8 núcleos que registró la misma sesión. Concluir que «ningún runner lo tomó» después de unos 4 min de espera fue prematuro.

## 2. Diagnóstico: dónde me equivoqué

1. **La dependencia de (4) la inventé yo.** Ningún documento ni regla del PO ata el merge de #62 a la publicación. El `.csproj` deja el paquete detrás de `Impresora=PAX`, y la CI compila BLUETOOTH. Traté «el paquete no está en nuget.org» como un bloqueo de merge, cuando sólo bloquea el build PAX sin feed local, que ya tiene su camino.
2. **La pregunta de (2) estaba mal formulada e incompleta.** Pedí un «OK al tag» como si fuera el único paso. Con la evidencia, ese tag:
   - **(a)** con alta probabilidad falla en el 403 de `NUGET_API_KEY` (secreto sin renovar desde 2026-08-08; las tres últimas versiones las publicó el `.bat` local);
   - **(b)** publica en nuget.org, público e inmutable, un `MotorDsl.Pax` sin binding que no imprime en el A910S real, sin validación en el equipo y apartándose de P2;
   - **(c)** no lo necesita ningún consumidor hoy.

   La decisión real del PO es otra: **cuándo y por qué canal se distribuye el binding PAX**, que es una cuestión de licencia. Esa decisión no está en el camino crítico mientras el A910S no llegue.
3. Falta en U3: los scripts de publicación (`.bat` y `tag-next-version.sh`) siguen con ocho paquetes.
4. No convoqué a la mini-mesa antes de elevar. [[autonomia-inteligente-objetivo]] pide análisis previo y una propuesta con default, no un pedido de confirmación.

## 3. Soluciones

- **S1. No publicar ahora y destrabar todo lo demás (recomendada).**
  - Se fusiona #13, que está en verde y `clean`, con la delegación G1–G4. El push a `main` corre `cd-nuget` en modo preview y comprueba, sin publicar, que se empaquetan los nueve (Pax en macos-15). Esa es la evidencia parcial de CA-07.1.
  - En la app: #60 → #61 → #62 retargeteado a `main` y conformado con `verificar-pr` (BLUETOOTH). El build PAX sigue con el feed local, que lleva el binding, hasta validar en el equipo.
  - La publicación pasa a hito de la llegada del A910S (D1/D2). Se agrega a la checklist del equipo y al punto de continuación del expediente.
- **S2. Publicar ya la 1.0.18 pública con `MotorDsl.Pax` sin binding.**
  - Requiere renovar `NUGET_API_KEY` (sólo el PO, en su cuenta de nuget.org, con permiso para ID nuevos `MotorDsl.*`) y crear el tag.
  - Publica, de forma inmutable, un paquete que en el equipo real responde `Connection`, y no aporta nada a la app.
- **S3. Canal privado para el paquete con binding.**
  - Publicar MotorDsl.* en el feed privado de GitHub Packages de la organización de la app. La app ya lo consume con `NUGET_TOKEN` para NgPushDispatch.Maui (`verificar-pr.yml:126-139`).
  - Resuelve que el build PAX dependa del feed local y que el material PAX se redistribuya en público.
  - Requiere un workflow nuevo con el SDK PAX como secreto o artefacto privado (la opción que dejó abierta U2 §bloqueo 1) y una decisión sobre la licencia. Conviene hacerlo **después** de validar en el equipo.
- **S4. Cerrar los huecos de U3 en un PR chico de la librería, sin publicar.** Agregar `MotorDsl.Pax` a `tag-next-version.sh` y a `publish-motordsl-nuget.bat`, y anotar en `docs/09_devops` y en el CHANGELOG que el paquete público sale sin binding. Va aparte de S1 y es delegable.

## 4. Secuencia recomendada

1. **Librería:** conformar #13 ya. Guarda G1–G4 sobre `1eb9000`: CI en success y `clean`. Fusionar con merge commit, borrar `feature/04-pax-transporte` y controlar la corrida de `cd-nuget` del push a `main`, que debe empaquetar nueve en preview, sin publicar.
2. **Librería:** abrir y conformar un PR S4 con los scripts de publicación en nueve y la nota de distribución sin binding.
3. **App:** resolver el chequeo del menú de bundles (#63, otro tramo). Después conformar #60 y #61 a `main`, retargetear #62 a `main`, actualizarlo y conformarlo con `verificar-pr` en verde. No cambiar `MotorDslPaxVersion` a una versión pública.
4. **Expediente 0001:** reescribir el punto de continuación 2 y 4. Ni la publicación ni #62 esperan al PO. La publicación queda como hito D2+ con tres requisitos: clave de nuget.org renovada, decisión de licencia y canal (público sin binding, o privado con binding), y versión 1.0.18 según la regla «siguiente del feed».
5. **Cuando el A910S imprima de verdad:** llevar una sola decisión al PO, con default S3, y acompañarla con lo que hace falta de su lado (renovar la clave o el token).

## 5. Qué necesita del PO y cuándo

**Nada ahora.** Los pasos 1 a 4 están cubiertos por la delegación de PR y por el alcance aprobado.

Cuando el A910S valide la impresión real, una sola decisión con default:

- Canal del paquete con binding: el default es el feed privado de la organización de la app (S3). La alternativa es nuget.org público sin binding (S2).
- Si va a nuget.org: renovar `NUGET_API_KEY`, que dio 403 el 2026-08-26 y no se actualizó desde el 2026-08-08. Sólo puede hacerlo él.
- Se le informa, sin preguntarle, que la versión será 1.0.18, salvo que prefiera 1.1.0 por SemVer.
