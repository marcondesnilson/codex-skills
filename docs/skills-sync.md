# Sincronização centralizada das skills

O repositório `codex-skills` é a fonte canônica. O script `scripts/sync-skills.py`
sincroniza **pastas completas** (inclusive `references/`) para um catálogo local
de skills do Codex, sem alterar repositórios consumidores nem `AGENTS.md`.

## Uso (Linux/macOS)

Execute no checkout deste repositório:

```bash
# Inspecionar alterações (não grava nada)
python3 scripts/sync-skills.py --destination ~/.codex/skills

# Aplicar somente alterações seguras
python3 scripts/sync-skills.py --destination ~/.codex/skills --apply
```

Para testar com um checkout local, sem rede:

```bash
python3 scripts/sync-skills.py --source . --destination /tmp/codex-skills-test --apply
```

O primeiro uso **não sobrescreve arquivos já existentes**: são classificados
como conflitos, a menos que tenham conteúdo idêntico. Arquivos gerenciados
recebem atualizações futuras apenas quando o hash local ainda corresponde ao
manifesto `.codex-skills-sync.json`. Alterações locais são preservadas;
nenhum arquivo é removido automaticamente. Se uma instalação existente divergir,
compare e faça backup/reconciliação antes de adotar o sincronizador.

## Atualização automática opcional

Depois de testar manualmente, é possível executar periodicamente via cron
ou systemd user timer. Exemplo de cron diário, após instalar o script em um
checkout local confiável:

```cron
0 9 * * * /usr/bin/python3 /caminho/codex-skills/scripts/sync-skills.py --destination /home/USUARIO/.codex/skills --apply
```

Adapte os caminhos e horários. Não há cron ou timer instalado automaticamente.
Para maior previsibilidade, fixe uma tag usando `--ref` em vez de `main`.
Mudanças do upstream passam a ser aplicadas na próxima execução agendada,
desde que não existam conflitos locais. Faça revisão das versões antes de
habilitar atualização automática de instruções confiadas a agentes.

O sincronizador não modifica o código dos projetos, não faz deploy, não altera
`AGENTS.md` e não garante que uma sessão Codex já aberta recarregue skills.
Cada projeto deve declarar as skills no seu `AGENTS.md` aplicável.
