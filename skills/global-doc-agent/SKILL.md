---
name: global-doc-agent
description: Aplicar padrão de documentação obrigatória com múltiplos projetos (monorepo), garantindo leitura de docs antes de alterações e consistência entre código e documentação.
---

# 🧠 CONTEXTO

Esta skill aplica um padrão orientado por documentação obrigatória, com suporte a múltiplos projetos independentes dentro do mesmo repositório.

# 🧭 ORDEM OBRIGATÓRIA

Sempre seguir:

1. Verificar /documentation/index.md
2. Identificar o projeto afetado
3. Verificar /<projeto>/documentation/index.md (se existir)
4. Ler documentação relevante
5. Validar com estrutura real

Nunca modificar código antes disso.

# 📚 PRIORIDADE

1. Documentação do projeto
2. Documentação global
3. Estrutura real

# 🧩 MÚLTIPLOS PROJETOS

- Detectar automaticamente projetos
- Tratar de forma independente
- Não assumir stack

# 🔄 DOCUMENTAÇÃO

Se alterar comportamento:

- atualizar documentação correta
- atualizar index.md
- manter consistência

# 🧪 VALIDAÇÃO

- validar apenas projeto afetado
- usar testes/build/lint se existirem

# 🔐 SEGURANÇA

- nunca expor segredos
- documentar variáveis de ambiente

# 📏 COESÃO

- priorizar responsabilidade única
- evitar arquivos grandes (>500 linhas)
- não dividir sem necessidade

# 🎯 OBJETIVO

- consistência entre código e docs
- manutenção simples
- isolamento por projeto
