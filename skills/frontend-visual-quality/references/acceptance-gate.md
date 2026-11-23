# Acceptance plan and evidence gate

The task plan is declared before execution. It names affected components and required checks. `frontend_impact` and
`api_execution_authorized` are separate facts: a visual impact always adds the required external visual-review check,
while API execution still needs explicit task-scoped authorization and a separate `--authorize-api-execution` flag.
An API key or authorization file alone does not grant permission to make a request.

Create a plan matching [acceptance-plan.schema.json](../schemas/acceptance-plan.schema.json), then initialize a private
task folder:

```sh
python3 scripts/visual_review.py init \
  --task-id <task-id> --project <project> --scope <routes-and-components> \
  --acceptance-plan /private/plan.json --project-root /workspace/project
```

When separate API execution permission has been granted for this task, add both `--authorization-file` and
`--authorize-api-execution`. The plan's frontend decision still requires visual acceptance if true. A frontend task
without API execution authorization remains `BLOCKED` at finalization unless a confirmed failure already makes the
result `FAIL`.

## Served build identity

Record a hash-backed build context with `record-build`. It contains a served version, build ID, source hash, runtime
configuration hash, accepted visual-direction hash, and served asset hash. Each current screenshot records the returned
`build_fingerprint` plus platform, environment, device/window, viewport, scale factor, theme, state, route, tool, and
content ID. A change to the served fingerprint makes prior checks and screenshots stale; record the checks again against
the current build. Git `HEAD` alone does not identify the served app.

## Evidence-linked checks

Declare check IDs before running checks. Store a sanitized, non-empty `.md`, `.txt`, or `.json` evidence file in the
private task folder, then register its SHA-256 and byte count with `record-check`. The helper rejects unknown check IDs,
missing evidence, symlinks, external files, and a warning downgrade of a required check. Evidence is checked again at
finalization; editing it after registration makes it stale.

```sh
python3 scripts/visual_review.py record-check --task-dir <task-dir> \
  --check-id unit-tests --status PASS \
  --evidence <task-dir>/evidence/unit-tests.txt --summary "42 offline tests passed"
python3 scripts/visual_review.py finalize --task-dir <task-dir>
```

The finalizer derives the same conclusion into state, manifest, and report. It does not accept a caller-supplied result.
Precedence is `FAIL` > `BLOCKED` > `PASS WITH WARNINGS` > `PASS`. A missing required test is `BLOCKED`, not a warning.
Only recorded checks and evidence for the same current build count. A consultive model response is not itself an approval;
Codex records the evaluation as an evidence-linked external visual check.

Backend-only plans do not need visual configuration or API authorization. Reading or changing the QA skill does not
create a task, start a product test, or count as product QA.

## Matriz, lotes e reavaliação

Registre a matriz inteira com `record-criteria --task-dir <task-dir> --criteria <matrix.json>`
antes da primeira consulta. Cada lote recebe o subconjunto exato dos critérios e um `--batch-id`.
O agregador mantém a tentativa mais recente por linha no mesmo build, direção e versão da matriz.
Uma tentativa que falhe mantém suas linhas pendentes. Ao consolidar, o check do Codex referencia o último
call ID e fixa os IDs das tentativas que compõem a cobertura. Confirme os achados na aplicação.

A CLI antiga de lote único fixa a matriz na primeira submissão. Uma matriz diferente exige
`record-criteria ... --reason <decisão>`. A revisão preserva a matriz anterior e a justificativa.
A operação pode cobrir menos linhas por lote, mantendo as demais obrigatórias. Uma nova matriz exige ao menos uma consulta atual. Linhas que permaneceram idênticas podem manter
a evidência do mesmo build, direção e brief. Um build diferente exige capturas atuais.

`--review-kind reevaluation` usa a autorização própria. Indique `--reevaluation-reason` para uma
reavaliação sem correção, por exemplo, após mudar critério ou referência. Permaneça no ciclo atual
para reavaliar a mesma captura e use uma matriz modificada ou uma referência distinta. Ciclos novos
representam correções e registram progresso. O limite de API se aplica a cada rodada enviada.

Cada tentativa guarda metadados e hashes de capturas, referências, contexto da consulta e resultado
normalizado. A finalização verifica novamente os arquivos. Tentativas antigas que carecem dos
novos vínculos precisam de evidência atual. Um build só passa com a direção adotada quando
`visual_direction_sha256` representa o SHA-256 do conteúdo canônico. A adoção atualiza a decisão,
e a aplicação precisa efetivamente servir um build com essa direção.

Em apps nativos, use `screen_id` no lugar de rota web, dimensões da janela em `viewport` e metadados
do dispositivo, ambiente, escala, tema, estado e ferramenta. A presença desses campos é evidência
do contrato da captura. A execução real requer a aplicação e a ferramenta apropriada.

O schema valida formato e categorias. O runtime também exige unicidade de IDs entre checks,
uma restrição entre itens distintos que JSON Schema padrão não expressa por campo.

### Resultado corrente e interrupções

`status` expõe `acceptance.valid`, `acceptance.result` e, quando vigente,
`acceptance.conclusion`. Antes de persistir uma mudança que afete o aceite, o helper
publica `pending_revalidation` no relatório e no manifest. A conclusão final volta
a ficar vigente quando state, manifest e relatório concordam. Uma interrupção pode
deixar cópias de uma conclusão anterior nos arquivos internos. Nesse caso, consulte
`status`, que trata a publicação incompleta como pendente. Execute `finalize` para
recalcular a conclusão a partir das evidências.

Capturas PNG/JPEG e assets enviados são decodificados com Pillow após os limites
individuais e agregados. O transporte usa os bytes originais validados. Ausência
do decodificador ou tolerância a truncamento ativa impede a preparação do envio.
