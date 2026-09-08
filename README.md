# Codex Skills

Repositório público de skills reutilizáveis para projetos com Codex.

## Skills disponíveis

- global-doc-agent
- laravel-doc-agent
- frontend-doc-agent
- commit-projects

## Uso obrigatório no projeto

Instalar a skill não garante que ela será aplicada em todas as tarefas. Para torná-la obrigatória no projeto,
cite-a no `AGENTS.md` que governa os arquivos envolvidos. Use um bootstrap explícito:

```md
# Skills obrigatórias

- Sempre use `global-doc-agent` antes de alterar este projeto.
- Use também `laravel-doc-agent` em qualquer tarefa que toque código, configuração, testes ou documentação Laravel.
- Use também `frontend-doc-agent` em qualquer tarefa que toque frontend, interface ou experiência visual.
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
tar -czf /tmp/codex-skills-2.0.0.tar.gz skills
```

Esse comando empacota o checkout presente, inclusive alterações ainda não publicadas; o nome não comprova release.
Para instalar, usar um mecanismo disponível no ambiente que aceite a pasta completa ou copiar a pasta da skill para
o diretório de skills configurado nesse ambiente. Comparar destino existente antes de atualizar para preservar
customizações locais. Conferir que `references/` foi transferido e que os links locais resolvem.

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
