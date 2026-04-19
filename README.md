# Codex Skills

Repositório público de skills reutilizáveis para projetos com Codex.

## Skills disponíveis

- global-doc-agent
- laravel-doc-agent
- frontend-doc-agent

## Uso no projeto (recomendado)

No `AGENTS.md` do repositório, mantenha apenas bootstrap curto chamando as skills:

- sempre aplicar `global-doc-agent`
- aplicar `laravel-doc-agent` quando a mudança for no backend Laravel
- aplicar `frontend-doc-agent` quando a mudança for no frontend

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

## Instalação pelo chat

/skills add https://github.com/marcondesnilson/codex-skills/blob/main/skills/global-doc-agent/SKILL.md
/skills add https://github.com/marcondesnilson/codex-skills/blob/main/skills/laravel-doc-agent/SKILL.md
/skills add https://github.com/marcondesnilson/codex-skills/blob/main/skills/frontend-doc-agent/SKILL.md
