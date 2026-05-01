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

# 🩺 HEALTHCHECK E STATUS

Todo projeto criado ou alterado deve ter documentação e implementação mínima de health/status.

Regras gerais:
- expor um endpoint, rota ou arquivo público de liveness para monitoramento automatizado
- expor status humano quando fizer sentido para operação, suporte ou validação de deploy
- separar liveness de readiness quando a stack permitir
- liveness deve ser rápido e não depender de banco, APIs externas, filas ou serviços terceiros
- readiness deve validar dependências reais necessárias para receber tráfego
- readiness deve diferenciar estado saudável, degradado e erro quando houver checks não críticos
- documentar payloads, status HTTP, periodicidade, dependências verificadas e exemplos de uso
- documentar como o healthcheck deve ser usado em Docker, Swarm, Kubernetes, CDN ou hospedagem estática
- cobrir health/status com testes, smoke tests ou validação de build quando aplicável

Diretrizes por tipo de projeto:
- backend/API: usar endpoints como `/health/live`, `/health/ready`, `/health` e `/status`
- frontend SPA/SSR: expor health estático ou rota pública validando build, versão e configuração essencial
- frontend que consome API: status humano deve indicar conectividade com backend quando seguro e relevante
- worker/CLI: disponibilizar comando, endpoint interno ou arquivo de status compatível com a infraestrutura
- monorepo: cada projeto deve ter health próprio, e agregadores devem apenas consolidar estados existentes

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
