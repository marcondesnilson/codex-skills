---
name: laravel-doc-agent
description: Aplicar padrões recorrentes para projetos Laravel com foco em documentação, organização por domínio, validação, segurança e consistência entre código e docs.
---

# CONTEXTO

Skill de apoio para mudanças em projetos Laravel.

# ORDEM

1. Ler documentação local do projeto Laravel
2. Confirmar versão e stack (Laravel, PHP, banco, filas)
3. Implementar mudança mantendo padrão existente
4. Validar com testes/lint/comandos do projeto
5. Atualizar documentação afetada

# PADROES LARAVEL

- Preferir regras já adotadas no projeto antes de introduzir novas convenções
- Manter controllers enxutos; regra de negocio em services/actions/use-cases
- Validacao em Form Requests quando aplicavel
- Queries complexas em escopos, repositorios ou classes dedicadas
- Evitar logica de infraestrutura misturada com regra de negocio

# REGRAS BACKEND (TOKEN-SAVER)

- IDs: usar ULID como padrao; persistir em minusculo no banco
- Rotas: quando Laravel for apenas backend, nao usar prefixo `/api`
- Escopo backend-only: nao criar/manter pastas, plugins, pacotes ou assets de frontend

# DADOS E SEGURANCA

- Nao expor segredos
- Revisar impacto em migrations e compatibilidade de deploy
- Garantir validacao e autorizacao para endpoints alterados
- Atualizar variaveis de ambiente quando necessario

# TESTES

- Executar testes focados no modulo alterado
- Priorizar testes feature para fluxos HTTP e unitarios para regra de negocio
- Evitar alterar suites nao relacionadas sem necessidade

# DOCUMENTACAO

Se houver alteracao funcional:
- atualizar docs do projeto
- atualizar index da documentacao local
- manter exemplos de uso e contratos atualizados
