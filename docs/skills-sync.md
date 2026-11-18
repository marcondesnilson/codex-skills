# Sincronização centralizada das skills

O repositório `codex-skills` é a fonte canônica. `scripts/sync-skills.py`
sincroniza **pastas completas** de skills, incluindo `references/`, `schemas/`
e `scripts/`. Ele requer `--destination`, preserva diferenças locais, não remove
arquivos, não altera código consumidor nem `AGENTS.md` e não confirma que uma
sessão já aberta descobriu/recarregou uma skill.

Diretórios `__pycache__` e arquivos `.pyc`/`.pyo` são excluídos antes da leitura
de hashes, comparação de destino, contagem de conflitos e cópia. Registros
legados desses caminhos no manifesto permanecem inertes. O filtro do
sincronizador complementa `.gitignore` (`__pycache__/` e `*.py[co]`); ele não
apaga caches existentes nem limpa o manifesto.

## Caminhos e descoberta

Na documentação pública atual consultada em 2026-11-17, os caminhos manuais
documentados para Codex são `.agents/skills/` no projeto e `~/.agents/skills/`
no escopo do usuário. Ambientes podem manter instalações legadas/customizadas,
como `$CODEX_HOME/skills`. Confirme qual caminho é reconhecido pela versão e
runtime que executarão a tarefa; não presuma descoberta só porque a pasta existe.

Uma skill é uma pasta com `SKILL.md` e recursos opcionais. O `AGENTS.md` contém
orientações para o Codex, mas não instala nem registra skills. Depois de copiar,
confirme a skill no catálogo/contexto do ambiente e, se necessário, inicie uma
nova sessão. A seleção automática continua sendo uma decisão do Codex; para um
fluxo determinístico, solicite a skill explicitamente na tarefa.

Fonte sobre os caminhos: [instalação manual de skills do Codex](https://developers.openai.com/api/reference/cli).

## Aplicar a partir de um checkout

Execute no checkout que contém a versão desejada. Sempre informe o destino.

```bash
# Simular; não grava arquivos
python3 scripts/sync-skills.py --source "$PWD" --destination /tmp/codex-skills-check

# Aplicar em um diretório temporário para revisar a cópia completa
python3 scripts/sync-skills.py --source "$PWD" --destination /tmp/codex-skills-check --apply
```

Para validar alterações ainda não publicadas, `--source` deve apontar para
este checkout local. Não clone `main` e trate a cópia como se contivesse mudanças
que ainda não foram publicadas.

Para sincronizar um catálogo Codex já confirmado, escolha explicitamente o
destino apropriado ao ambiente. Exemplos de destinos documentados:

```bash
# Skill do projeto consumidor (execute na raiz do projeto)
python3 /caminho/codex-skills/scripts/sync-skills.py \
  --source /caminho/codex-skills --destination "$PWD/.agents/skills"

# Catálogo do usuário, se esse caminho estiver reconhecido pelo runtime
python3 /caminho/codex-skills/scripts/sync-skills.py \
  --source /caminho/codex-skills --destination "$HOME/.agents/skills"
```

O exemplo não é uma autorização para instalar agora nem substitui a confirmação
do caminho suportado pelo runtime. Não direcione o sincronizador a `~/.agents`,
`~/.codex` ou a outro projeto sem decisão explícita para a tarefa.

O primeiro uso **não sobrescreve arquivos existentes**: arquivos diferentes
são conflitos, a menos que seu conteúdo corresponda ao manifesto
`.codex-skills-sync.json`. Arquivos gerenciados recebem atualizações futuras
somente quando o hash local ainda corresponde ao manifesto. Alterações locais
são preservadas, nenhum arquivo é removido automaticamente. Se o destino
divergir, compare e reconcilie com backup antes de adotar a cópia.

## Revisar uma pasta distribuída

Para `frontend-visual-quality` e `qa-projects`, a distribuição deve conter a
pasta completa, incluindo `references/`, `schemas/`, `scripts/` e `agents/` que
existirem:

```text
frontend-visual-quality/
├── SKILL.md
├── references/
├── schemas/
└── scripts/
qa-projects/
├── SKILL.md
└── agents/
    └── openai.yaml
```

Após a sincronização temporária, compare hashes de todos os arquivos e execute
o CLI e os testes offline dentro da pasta copiada. A suíte usa fixtures e
transporte injetado; não precisa de chave nem rede.

## Atualização agendada

O sincronizador não instala cron nem timers. Um operador pode agendar execuções
somente depois de testar e escolher o destino. Fixe uma referência de release
quando aplicável, revise as mudanças de instruções e acompanhe conflitos antes
de aplicar atualizações futuras. Uma atualização de skills não atualiza o
`AGENTS.md` dos consumidores e não prova que uma sessão ativa recarregou o
catálogo.
