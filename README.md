# Codex Skills

Repositório público de skills reutilizáveis para projetos com Codex.

## Skills disponíveis

- global-doc-agent
- laravel-doc-agent
- frontend-doc-agent
- frontend-visual-quality (criação, redesign, refinamento e inspeção visual real)
- qa-projects (QA funcional, visual, UX e regressão com current/isolated)
- commit-projects

## Uso obrigatório no projeto

Instalar/copiar uma skill não garante que ela será selecionada ou aplicada. O `AGENTS.md` pode instruir o Codex a usar
uma skill disponível; ele não instala nem registra skills. Para tornar seu uso uma instrução do projeto, cite-a no
`AGENTS.md` que governa os arquivos envolvidos. Use um bootstrap explícito:

```md
# Skills obrigatórias

- Sempre use `global-doc-agent` antes de alterar este projeto.
- Use também `laravel-doc-agent` em qualquer tarefa que toque código, configuração, testes ou documentação Laravel.
- Use também `frontend-doc-agent` em qualquer tarefa que toque frontend, interface ou experiência visual.
- Use `frontend-visual-quality` quando a tarefa altera apresentação ou interação em web, desktop ou aplicativo. Backend sem impacto na interface, documentação e refatorações internas seguem o QA aplicável ao seu escopo.
- As instruções dessas skills são obrigatórias dentro do escopo em que forem citadas.
- Em código existente, aplique-as somente ao fluxo e aos arquivos tocados e às dependências diretas necessárias.
- Não audite, procure problemas, refatore ou corrija áreas não relacionadas; a adequação do legado deve ser gradual.
- Todo código criado ou alterado deve respeitar o Quality Profile e o Quality Gate SonarQube do projeto, sem novos problemas no New Code e sem mascarar achados com supressões.
```

Mantenha esse arquivo no repositório e ajuste o escopo com arquivos `AGENTS.md` mais específicos quando necessário.
Na prática:

- sempre aplicar `global-doc-agent`
- aplicar `laravel-doc-agent` quando a mudança for no backend Laravel
- aplicar `frontend-doc-agent` quando a mudança for no frontend

As três skills distinguem projetos novos de existentes. Em projetos existentes, uma tarefa pequena não autoriza
uma varredura geral: as regras devem ser cumpridas no código tocado e em seus contratos diretos, mantendo dívida
legada não relacionada fora da alteração.

Todas também adotam o modelo Clean as You Code do SonarQube: código novo ou alterado deve passar sem novos bugs,
vulnerabilidades, code smells ou duplicações, com Security Hotspots revisados e cobertura conforme o Quality Gate
configurado no projeto. Achados antigos no Overall Code permanecem fora do escopo até que o fluxo correspondente
seja tocado ou exista um pedido explícito de saneamento.

A hierarquia de qualidade mantém a política tecnológica agnóstica no `global-doc-agent`: confiabilidade, segurança,
manutenibilidade, complexidade, duplicação, Security Hotspots, testes/cobertura, dívida técnica, tratamento de erros,
código morto e o checklist obrigatório de conclusão. `laravel-doc-agent` e `frontend-doc-agent` apenas complementam essa
base com verificações próprias de suas stacks, sem repetir ou substituir a política global. Os limites de cobertura de
80% e duplicação inferior a 3% no New Code são referências quando o projeto não definir valores próprios; o Quality
Profile e o Quality Gate reais sempre prevalecem.

O `laravel-doc-agent` documenta padrões obrigatórios para evitar controllers gigantes:
controllers devem apenas orquestrar HTTP, enquanto regra de negócio, validação, autorização, queries,
serialização e integrações devem ficar em services/actions/use cases e recursos próprios do Laravel.
Também deixa explícito que mudanças Laravel devem usar o ecossistema do framework sempre que possível:
Form Requests, Policies, API Resources, Jobs, queues, Events, Listeners, Observers, Notifications,
Commands, Schedule, Service Providers, casts, scopes e demais primitivas nativas adequadas ao fluxo.
Para APIs, também orienta a evitar rotas redundantes: variações de listagem, busca, status, período,
ordenação ou tipo devem virar filtros validados no endpoint canônico antes de se criar uma nova rota.
Para SSE, centraliza rotas explícitas sob `/streams`, usa Observer após commit e Redis Streams para publicação,
replay e reconexão sem polling no banco. O contrato completo fica na
[referência SSE da skill Laravel](skills/laravel-doc-agent/references/sse.md).

O `commit-projects` é uma skill operacional de invocação explícita. Use `$commit-projects` quando quiser revisar o
diff completo, revisar a qualidade do New Code e dos contratos diretamente afetados, reconciliar a documentação, aplicar
SemVer e criar um commit local. Essa revisão procura problemas evidentes de confiabilidade, segurança, manutenção,
complexidade, duplicação, tratamento de erros e testes somente no escopo tocado; não é uma auditoria geral do repositório.
Apenas instalar ou citar essa skill na documentação não autoriza commits, e ela nunca executa push sem um pedido separado
e explícito.

Quando o projeto define notas de release, o `commit-projects` prepara os textos em português do Brasil após atualizar
o `VERSION`. A nota técnica segue o formato do projeto. Se houver uma nota prevista para o aplicativo e a mudança
afetar usuários, a skill prepara um texto próprio para esse público. As notas aplicáveis entram no mesmo commit da
versão que descrevem. Consulte o [procedimento da skill](skills/commit-projects/SKILL.md#release-governance-integration).

## Arquitetura e carregamento progressivo

O `global-doc-agent` coordena **o que** considerar; especialistas definem **como** implementar. A consulta entre skills
é leitura e aplicação de instruções disponíveis no catálogo do ambiente, não um mecanismo automático de subagentes.
Não existe requisito de instalar especialistas futuros. A ausência de um especialista é suprida pela documentação
real do projeto, com limitações informadas quando relevantes.

```text
skills/
├── global-doc-agent/
│   ├── SKILL.md
│   └── references/
│       ├── application-governance.md
│       ├── final-checklist.md
│       ├── licensing.md
│       ├── observability.md
│       ├── privacy-and-legal.md
│       ├── quality-gates.md
│       ├── release-management.md
│       ├── security-baseline.md
│       └── tracking-and-audit.md
├── frontend-doc-agent/SKILL.md
├── frontend-visual-quality/
│   ├── SKILL.md
│   ├── references/
│   ├── schemas/
│   └── scripts/
├── qa-projects/
│   ├── SKILL.md
│   └── agents/
│       └── openai.yaml
├── laravel-doc-agent/
│   ├── SKILL.md
│   └── references/sse.md
└── commit-projects/SKILL.md
```

O [ponto de entrada Global](skills/global-doc-agent/SKILL.md) contém princípios críticos, hierarquia, fluxo e tabela de
referências com gatilhos. Ler detalhes somente quando acionados: código leva a qualidade; dependência leva a segurança
e licenças; dados pessoais levam a privacidade; release/migration leva a compatibilidade e implantação. O checklist final
é sempre consultado, mas só seus itens pertinentes são aplicados.

Regras são **obrigatórias sempre**, **obrigatórias quando aplicáveis** ou **recomendadas**. Um requisito condicional
não vira opcional quando seu gatilho existe; tampouco autoriza reformar módulos fora do pedido. Sobre, suporte, termos,
licenças e informações de release podem ser oferecidos dentro da aplicação ou por canais empresariais restritos.
Existência não implica publicação na Internet. Nenhum segredo ou diagnóstico interno deve ir para interfaces comuns.

Exemplo: pedido de novo relatório Blade → ler docs e confirmar contratos → Global avalia dados, acesso e release →
Laravel implementa consulta/autorização/serialização → frontend implementa componentes, estados, temas e acessibilidade →
validar comportamento e renderização → atualizar docs/notas pertinentes → checklist contextual. Commit só por pedido.

## Distribuição e instalação completa

Cada skill é uma **pasta distribuível**, não apenas seu `SKILL.md`. Manter os nomes e copiar suas referências junto.
Links internos usam Markdown relativo e não dependem de vault Obsidian; documentação dos projetos consumidores segue
seu padrão local, incluindo MOCs, frontmatter e backlinks quando adotados.

Para preparar um pacote a partir deste checkout, sem instalar ou sobrescrever configurações:

```sh
tar -czf /tmp/codex-skills-2.1.0.tar.gz skills
```

Esse comando empacota o checkout presente, inclusive alterações ainda não publicadas; o nome não comprova release.
Os caminhos documentados atualmente para Codex são `.agents/skills/` no projeto e `~/.agents/skills/` no escopo
do usuário; instalações existentes também podem usar um `CODEX_HOME` ou catálogo legado/customizado. Confirme o caminho
reconhecido pelo runtime que executará a skill. Mantenha `--destination` explícito, compare o destino existente e
preserve customizações locais. Depois de copiar a pasta completa, confirme que a sessão/catálogo reconheceu a skill;
abra uma sessão nova se necessário. Nem a cópia garante seleção automática, nem citar o nome no `AGENTS.md` a instala.

Para sincronizar apenas em um diretório temporário durante o desenvolvimento desta branch:

```sh
python3 scripts/sync-skills.py --source "$PWD" --destination /tmp/codex-skills-check --apply
```

Use o checkout local em `--source` para testar mudanças ainda não publicadas. Não clone `main` para validar alterações
que só existem neste checkout. O sincronizador preserva arquivos divergentes e não remove instalações antigas.

Os exemplos antigos de download raw de um único `SKILL.md` foram retirados: já omitiam `references/sse.md` e agora
omitiriam as políticas modulares do Global. Não assumir que um comando de chat ou instalador transfere referências;
validar a capacidade e o resultado no ambiente utilizado. Este repositório não sincroniza instalações automaticamente.

## Versão e transição para 2.0.0

`VERSION` identifica a distribuição das skills. O histórico usa SemVer (`1.0.0`, `1.1.0`, `1.2.0`) e arquivo sem newline.
A evolução para `2.0.0` altera o contrato distribuído: o Global exige referências e o consumidor que instalava só o
arquivo principal deve passar a instalar a pasta inteira. Diagnósticos detalhados de health/status passam a exigir
acesso operacional autorizado; integrações que dependiam de detalhes públicos precisam se adaptar quando esse fluxo
for atualizado. Não realizar migração geral dos projetos legados por instalar a skill.

Novidades: governança de produto, Sobre/suporte, separação de informação interna, licenciamento, privacidade/termos,
releases, segurança, auditoria e Definition of Done contextual. Tracking passa a exigir finalidade demonstrada;
auditoria Laravel é aplicada a operações justificadas. Temas, i18n, qualidade e contrato SSE são preservados.

A versão identifica esta evolução das skills; seu registro em Git não implica publicação ou instalação externa.
No fluxo de `commit-projects`, a classificação é calculada pelo diff completo contra HEAD, sem incrementar novamente
sobre um número previamente preparado. Nesta evolução, a base `1.2.0` resulta em `2.0.0` por um único incremento MAJOR.
Não há migration de banco neste repositório documental.

A [revisão estrutural e cenários A–J](docs/governance-review.md) registra preservações, conflitos resolvidos e limites da
validação. As referências são normativas; o relatório é evidência desta revisão, não um segundo conjunto de regras.

## Incremento local 2.1.0

Este incremento MINOR adiciona QA funcional/visual com modos `current` e `isolated`, evidência ligada ao build servido,
um gate de aceite visual e operações opcionais para direção, conteúdo e imagens. As chamadas à Responses API usam
`store=false`; chamadas às Images API enviam os campos suportados pelo endpoint. A distribuição também passa a excluir
caches Python do sincronizador. Esta classificação descreve o diff local sobre `2.0.0`; não declara publicação ou release.

## Qualidade visual de frontend

A skill [`frontend-visual-quality`](skills/frontend-visual-quality/SKILL.md) complementa `frontend-doc-agent` quando houver impacto na apresentação ou interação. Correções somente funcionais e tarefas sem mudança de interface não exigem auditoria visual completa. A pasta distribuível contém instruções, referências, schemas e um CLI opcional para revisão pela Responses API; chamadas reais exigem autorização por tarefa e permissão separada de execução. O navegador/MCP captura e inspeciona a aplicação real; a skill orienta o Codex, que avalia achados e implementa correções confirmadas.

Chrome DevTools MCP ou outra ferramenta de navegador adequada pode inspecionar e capturar a renderização real. Nenhuma ferramenta é presumida disponível e nenhuma ausência deve ser coberta por screenshots fictícios. Quando uma tarefa afeta apresentação ou interação, a revisão visual externa é requisito de aceite: sem autorização ou evidência, o resultado é `BLOCKED` salvo falha confirmada (`FAIL`). Chamadas à Responses API enviam somente entradas explicitamente selecionadas, usam `store=false` e exigem autorização e configuração de custo por tarefa; operações da Images API também exigem autorização e enviam apenas campos suportados pelo endpoint. O helper offline não comprova chamada real à API nem qualidade visual de aplicação.

A integração de responsabilidades, fingerprints de build, evidência de aceite e limites está em
[Frontend design QA](docs/frontend-design-qa-integration.md). A skill `qa-projects` preserva a escolha de ambiente em
cada execução (`current`/`isolated`) e não roda somente por ser lida ou editada.


## Fluxo autônomo de implementação visual (qualquer frontend)

Para instruir um projeto consumidor, disponibilize as **pastas completas** das skills e declare no `AGENTS.md` aplicável:

```md
- Use `global-doc-agent` nas tarefas deste projeto.
- Use `frontend-doc-agent` sempre que tocar interface web ou nativa.
- Use `frontend-visual-quality` para alterações de apresentação ou interação em qualquer plataforma.
- Em redesign autorizado, permita reconstruir a camada visual do escopo solicitado; preserve comportamento e contratos.
- Valide a renderização real e as interações com as ferramentas disponíveis; informe limitações sem inventar evidências.
```

O ciclo de fidelidade visual está centralizado nas skills e funciona com Vue, Nuxt, React, Next.js, Blade, Flutter ou outra stack compatível. Stitch/MCP, Impeccable e Playwright são integrações condicionais, não pré-requisitos universais. Em sistemas configuráveis ou multi-tenant, preserve contratos e consumidores existentes; não associe layouts fixos a domínios.

Um `AGENTS.md` orienta o Codex, mas não registra nem instala uma skill. Atualizar este repositório **não atualiza automaticamente** cópias em outros ambientes. Copie/sincronize a pasta completa para um caminho reconhecido, confirme sua descoberta e mantenha o bootstrap no `AGENTS.md` pertinente.

## Sincronização centralizada

Para distribuir atualizações das pastas completas das skills para o catálogo local do Codex, consulte [o guia de sincronização](docs/skills-sync.md). O processo usa dry-run por padrão, preserva modificações locais e permite agendamento opcional após validação. Atualizar o catálogo não altera automaticamente o AGENTS.md dos projetos.
