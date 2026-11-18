# Contrato da revisão visual

A saída é consultiva, não é decisão de aceite, plano executável, instrução para implementar nem substituto da inspeção
da aplicação real. O helper valida schema e referências antes de registrar uma resposta. O Codex compara o conteúdo com
a interface e os critérios declarados.

## Cobertura e capturas

`criteria.json` relaciona cada critério a uma ou mais entradas de cobertura. Cada entrada identifica tela/rota, região,
estado, plataforma e IDs de capturas obrigatórias. A captura registra, no mínimo, ID, papel, rota, viewport, tema,
estado, content ID, ferramenta, plataforma, ambiente, dispositivo/janela, escala e fingerprint do build servido.

```json
{
  "criteria": [{
    "id": "hero-hierarchy",
    "description": "O título e a ação principal têm hierarquia clara.",
    "coverage": [{
      "id": "hero-desktop-default",
      "screen": "/",
      "region": "hero",
      "state": "default",
      "platform": "web",
      "required_capture_ids": ["result-home-desktop"]
    }]
  }]
}
```

O modo criação aceita capturas `result`. O modo fidelidade exige um par `reference`/`result` em cada `pair_id`, com a
referência identificada como alvo selecionado pelo usuário e mesmo caminho, viewport, tema, estado e content ID. A
imagem precisa ser um arquivo PNG/JPEG local comum, com ID único; URLs são rejeitadas. A pasta privada registra SHA-256,
dimensões, bytes e metadados de ambiente/build. Capturas exigidas devem pertencer à plataforma e ao estado declarados.

## Resposta estruturada

O objeto contém modo, resultado para cada par critério/cobertura, achados e limitações. Cada linha de critério/cobertura
usa `evaluated` ou `not_evaluable`, descreve evidência observável e lista os IDs das capturas usadas. Uma linha avaliada
precisa citar todas as capturas obrigatórias para sua cobertura. Um finding cita ID de screenshot conhecido, região,
evidência observável, gravidade (`critical`, `high`, `medium`, `low`, `info`) e recomendação. `not_evaluable` impede a
cobertura visual completa. Lista de achados vazia nunca aprova a tarefa.

O helper rejeita recusa, saída incompleta, erro HTTP, JSON inválido, falta/duplicação de linhas, IDs desconhecidos,
saída sem evidência e schema inválido. Ele grava apenas o resultado normalizado, não o corpo bruto nem cabeçalhos de
autorização.

## Fingerprints e rastreabilidade

O `visual_fingerprint` cobre bytes e metadados de todas as capturas. O `context_sha256` cobre direção adotada e findings
anteriores. O fingerprint de evidência combina estes dados com critérios, brief, modo e tipo da revisão. Reutilizar o
mesmo fingerprint visual não vira nova revisão paga só porque o contexto textual mudou. A tentativa registra build,
schema/contrato, request/response IDs quando fornecidos, modelo e tier solicitado/retornado, tempo, usage, rate card,
estimativa e settlement.

O gate visual integrado só aceita evidência ligada ao fingerprint do build corrente e cobertura completa. Screenshots
de outro build, plataforma, viewport, escala ou estado são stale para esse aceite. A aprovação final é derivada pelo
Codex em evidência separada; a resposta da API nunca decide o resultado do QA.
