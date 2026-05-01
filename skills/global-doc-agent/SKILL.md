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

# 🧾 SESSÃO, VISITAS E AÇÕES

Todo projeto com interface, API pública, autenticação ou fluxo de usuário deve prever registro de sessões,
visitas e ações de forma proporcional ao produto e à legislação aplicável.

Objetivos:
- permitir auditoria de ações de usuários autenticados
- permitir análise de visitas e navegação de visitantes anônimos
- formar base segura para métricas, recomendação, suporte, antifraude e investigação operacional
- preservar privacidade, evitar repetição desnecessária de dados e não transformar fingerprint em identidade forte

Regras gerais:
- identificar visitantes anônimos por UID público aleatório, sem expor ID interno de banco
- identificar sessões por UID próprio, separado do visitante e do usuário autenticado
- registrar eventos com UID idempotente para evitar duplicidade em retry, refresh ou duplo disparo
- normalizar IP e user-agent em entidades/referências reutilizáveis quando houver persistência relacional
- logs de sessão, ações e analytics devem referenciar IP/user-agent normalizados quando possível
- registrar domínio, path, URL, origem, tipo de evento, conteúdo relacionado e timestamp quando aplicável
- separar metadados estáveis do visitante de metadados voláteis da sessão
- evitar armazenar metadados repetidos em todo pageview quando colunas próprias resolverem o contrato
- aplicar deduplicação por visitante, sessão, evento, path e conteúdo em janela curta configurável
- ignorar repetição da última página/conteúdo da mesma sessão quando isso inflar contagem artificialmente
- tratar fingerprint apenas como correlação probabilística, nunca como identidade garantida da pessoa
- permitir consentimento/configuração para tracking de visitantes quando exigido pelo produto ou legislação
- documentar retenção, finalidade, campos coletados, opt-out/consentimento e variáveis de ambiente

Captura de IP e user-agent:
- registrar o IP público real do cliente, não apenas o IP de servidores intermediários
- quando houver frontend, BFF, API gateway, CDN ou proxy, preservar a cadeia de IP/user-agent com headers internos
- confiar em headers de IP encaminhado somente quando a origem da requisição for infraestrutura confiável
- validar listas de IPs, descartar valores inválidos e evitar aceitar headers manipuláveis diretamente do cliente
- em ambientes públicos, preferir allowlist explícita de proxies/CDNs/load balancers por variável de ambiente

Diretrizes por tipo de projeto:
- frontend: gerar/manter UID de visitante e sessão, respeitar consentimento e enviar eventos públicos seguros
- backend/API: receber eventos, validar payload, deduplicar, resolver IP/user-agent reais e persistir referências
- área autenticada: registrar ações relevantes com usuário, sessão, IP/user-agent, recurso afetado e resultado
- monorepo: preservar identidade e sessão entre projetos por contrato documentado, sem acoplar bancos indevidamente

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
