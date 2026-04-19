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

# 📏 TAMANHO DE ARQUIVOS

Não existe um limite técnico universal de linhas por arquivo, mas o agente deve manter os arquivos do projeto coesos, legíveis e fáceis de manter.

Diretriz prática:
- ideal: até 300 linhas por arquivo
- aceitável: até 500 linhas por arquivo
- acima de 500 linhas: revisar se o arquivo deve ser dividido
- acima de 800 linhas: considerar exceção e manter apenas com justificativa clara

O agente deve avaliar quebra quando o arquivo:
- acumula múltiplas responsabilidades
- mistura regra de negócio com infraestrutura, UI ou detalhes auxiliares
- dificulta leitura, testes, revisão ou manutenção

Possíveis extrações:
- componentes
- serviços
- helpers
- hooks
- composables
- casos de uso
- actions
- validadores
- mapeadores
- adaptadores
- módulos internos

Exceções podem incluir:
- arquivos gerados
- migrations
- arquivos agregadores
- configurações
- pontos centrais em que a divisão prejudicaria a clareza

⚠️ O agente não deve dividir arquivos só por atingir um número arbitrário. A prioridade é responsabilidade única, boa organização e facilidade de evolução.

# 🎯 OBJETIVO

- consistência entre código e docs
- manutenção simples
- isolamento por projeto
