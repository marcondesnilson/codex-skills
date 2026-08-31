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

O `laravel-doc-agent` documenta padrões obrigatórios para evitar controllers gigantes:
controllers devem apenas orquestrar HTTP, enquanto regra de negócio, validação, autorização, queries,
serialização e integrações devem ficar em services/actions/use cases e recursos próprios do Laravel.
Também deixa explícito que mudanças Laravel devem usar o ecossistema do framework sempre que possível:
Form Requests, Policies, API Resources, Jobs, queues, Events, Listeners, Observers, Notifications,
Commands, Schedule, Service Providers, casts, scopes e demais primitivas nativas adequadas ao fluxo.
Para APIs, também orienta a evitar rotas redundantes: variações de listagem, busca, status, período,
ordenação ou tipo devem virar filtros validados no endpoint canônico antes de se criar uma nova rota.

O `commit-projects` é uma skill operacional de invocação explícita. Use `$commit-projects` quando quiser revisar o
diff completo, reconciliar a documentação, aplicar SemVer e criar um commit local. Apenas instalar ou citar essa
skill na documentação não autoriza commits, e ela nunca executa push sem um pedido separado e explícito.

## Instalação (URL raw)

mkdir -p .codex/skills/global-doc-agent
curl -o .codex/skills/global-doc-agent/SKILL.md \
https://raw.githubusercontent.com/marcondesnilson/codex-skills/main/skills/global-doc-agent/SKILL.md

mkdir -p .codex/skills/laravel-doc-agent
curl -o .codex/skills/laravel-doc-agent/SKILL.md \
https://raw.githubusercontent.com/marcondesnilson/codex-skills/main/skills/laravel-doc-agent/SKILL.md

mkdir -p .codex/skills/frontend-doc-agent
curl -o .codex/skills/frontend-doc-agent/SKILL.md \
https://raw.githubusercontent.com/marcondesnilson/codex-skills/main/skills/frontend-doc-agent/SKILL.md

mkdir -p .codex/skills/commit-projects
curl -o .codex/skills/commit-projects/SKILL.md \
https://raw.githubusercontent.com/marcondesnilson/codex-skills/main/skills/commit-projects/SKILL.md

## Instalação pelo chat

/skills add https://github.com/marcondesnilson/codex-skills/blob/main/skills/global-doc-agent/SKILL.md
/skills add https://github.com/marcondesnilson/codex-skills/blob/main/skills/laravel-doc-agent/SKILL.md
/skills add https://github.com/marcondesnilson/codex-skills/blob/main/skills/frontend-doc-agent/SKILL.md
/skills add https://github.com/marcondesnilson/codex-skills/blob/main/skills/commit-projects/SKILL.md
