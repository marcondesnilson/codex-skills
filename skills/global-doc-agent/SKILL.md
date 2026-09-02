---
name: global-doc-agent
description: Aplicar documentação obrigatória, escopo incremental e qualidade SonarQube em projetos e monorepos. Use sempre que esta skill for citada no AGENTS.md do projeto ou quando a tarefa exigir consistência entre código, documentação e análise estática.
---

# 🧠 CONTEXTO

Esta skill aplica um padrão orientado por documentação obrigatória, com suporte a múltiplos projetos independentes dentro do mesmo repositório.

# ⚠️ OBRIGATORIEDADE E ESCOPO

- Se esta skill estiver citada no `AGENTS.md` aplicável ao arquivo ou projeto, suas instruções são obrigatórias em toda tarefa dentro desse escopo.
- Não substituir, flexibilizar ou ignorar estas regras por preferência própria. Em caso de conflito, seguir instruções de maior prioridade e informar o conflito.
- Em projeto existente, aplicar estas regras somente ao código, configuração, testes e documentação que a tarefa criar ou alterar, incluindo dependências e contratos diretamente necessários à mudança.
- Não auditar, varrer, refatorar ou corrigir outras áreas apenas para adequar código legado a esta skill.
- Não incluir correções oportunistas fora do pedido. Dívida antiga encontrada incidentalmente deve permanecer intacta, salvo quando impedir a mudança solicitada.
- Melhorias estruturais em projetos existentes são incrementais: ao tocar um fluxo legado, adequar a parte modificada sem exigir a modernização completa do arquivo, módulo ou projeto.
- Em projeto novo, aplicar as regras desde a base no escopo solicitado.

# 🧭 ORDEM OBRIGATÓRIA

Sempre seguir:

1. Verificar `/documentation/index.md`, se existir
2. Identificar o projeto afetado
3. Verificar `/<projeto>/documentation/index.md`, se existir
4. Ler documentação relevante
5. Validar com estrutura real

Nunca modificar código antes disso.

# 📚 PRIORIDADE

1. Instruções aplicáveis e documentação do projeto
2. Documentação global
3. Estrutura real para confirmar a implementação

Não confiar apenas na documentação quando código, configuração ou comportamento executável puderem confirmar o contrato. Se houver divergência, limitar a investigação ao fluxo afetado e atualizar a documentação correspondente.

# 🧩 MÚLTIPLOS PROJETOS

- Identificar somente o projeto ou os projetos afetados pela tarefa
- Tratar de forma independente
- Não assumir stack
- Não inspecionar outros projetos do monorepo sem relação direta com a mudança

# 🔄 DOCUMENTAÇÃO

Se alterar comportamento:

- atualizar documentação correta
- atualizar index.md
- manter consistência

# 🧪 VALIDAÇÃO

- validar apenas projeto afetado
- usar testes/build/lint se existirem

# Qualidade de Código e SonarQube

## Política obrigatória

Todo código criado, modificado, corrigido ou refatorado, em qualquer tecnologia, deve seguir Clean as You Code. Tratar
como New Code o código adicionado ou modificado pela tarefa, o fluxo diretamente afetado e as dependências diretas
necessárias. O código tocado deve ficar tão sustentável quanto estava ou melhor e não pode introduzir nem agravar
deliberadamente problemas normalmente detectados pelo SonarQube.

Em projeto existente, não realizar auditoria, limpeza ou refatoração geral para corrigir o Overall Code. Problemas legados
não relacionados permanecem fora do escopo. Quando um problema existente estiver no trecho que precisa ser alterado,
avaliar a correção conjunta se ela for necessária para manter o New Code limpo e não ampliar indevidamente a tarefa.

Antes de concluir uma alteração de código, revisar as categorias abaixo.

## 1. Bugs e confiabilidade

- Analisar os principais caminhos possíveis de execução, incluindo sucesso, ausência de dados, falhas e limites relevantes.
- Não introduzir acessos inseguros a valores `null`/`undefined`, índices ou propriedades inexistentes, tipos inconsistentes,
  condições incorretas, retornos incompatíveis, código inalcançável ou erros previsíveis de runtime.
- Não ignorar exceções, falhas de recursos, concorrência aplicável, efeitos colaterais inesperados ou liberação necessária
  de arquivos, conexões, locks, listeners, timers e outros recursos.
- Preservar contratos e estados consistentes nos diferentes caminhos do fluxo alterado.

## 2. Vulnerabilidades e segurança

- Considerar toda entrada externa não confiável até que seja validada, normalizada e autorizada conforme o contexto.
- Verificar, quando aplicável, SQL Injection, XSS, Command Injection, Path Traversal, SSRF, CSRF, Mass Assignment,
  Broken Access Control, autenticação, autorização, uploads, manipulação de arquivos e URLs externas.
- Proteger secrets, tokens, senhas, credenciais e dados sensíveis em código, configuração, resposta, armazenamento e logs.
- Não usar criptografia insegura nem inventar mecanismos criptográficos próprios.
- Nunca considerar validação, ocultação de controles ou outra proteção da interface suficiente para autorização; a decisão
  deve ser aplicada na fronteira confiável do sistema.

## 3. Code Smells e manutenibilidade

- Evitar métodos e classes grandes, responsabilidades excessivas, parâmetros demais, condicionais complexas,
  aninhamento excessivo, dependências desnecessárias e abstrações sem benefício real.
- Remover, quando forem consequência direta da alteração, imports e variáveis não utilizados, métodos ou funções que se
  tornaram obsoletos, branches impossíveis, código comentado e demais códigos mortos.
- Não fazer limpeza indiscriminada em arquivos ou módulos não relacionados.
- Priorizar legibilidade, nomes claros, baixo acoplamento, alta coesão, responsabilidade bem definida e a solução mais
  simples que preserve corretamente o contrato.
- Comentários devem explicar contexto ou decisão não evidente, não repetir literalmente o código.

## 4. Complexidade cognitiva e ciclomática

- Controlar principalmente a Complexidade Cognitiva de funções que acumulem `if`, `else`, `switch`, `match`, loops,
  `try/catch`, callbacks ou muitos níveis de aninhamento.
- Avaliar guard clauses, early returns, extração de métodos e separação em services, actions, strategies ou utilities
  quando isso reduzir responsabilidades e melhorar de fato a compreensão.
- Não criar abstrações artificiais nem fragmentar um fluxo claro apenas para reduzir uma métrica.

## 5. Duplicação

- Antes de copiar lógica existente, verificar o módulo afetado e suas dependências diretas e decidir se o comportamento
  realmente deve ser reutilizado.
- Usar a abstração apropriada à tecnologia, como funções, métodos, services, actions, components, hooks, helpers,
  utilities, traits ou objetos de domínio, somente quando houver equivalência real de responsabilidade e contrato.
- Não criar abstrações prematuras para pequenas coincidências.
- Buscar duplicação inferior a 3% no New Code como referência comum somente quando não houver limite específico no
  Quality Gate do projeto.

## 6. Security Hotspots

Código relacionado a autenticação, autorização, criptografia, tokens, uploads, arquivos, comandos, URLs ou comunicação
HTTP externa, banco de dados, permissões ou dados sensíveis exige revisão de segurança explícita antes da conclusão.
Analisar a origem da entrada, os limites de confiança, a exposição e a mitigação; não classificar um hotspot como seguro
nem aplicar correção mecânica sem entender o contexto real.

## 7. Testes e cobertura

- Código com comportamento relevante deve possuir testes quando o projeto tiver infraestrutura adequada.
- Priorizar regras de negócio, validações, cálculos, autorização, permissões, services, APIs, casos de uso, caminhos de
  erro, correções de bugs e comportamentos críticos.
- Ao corrigir um bug, avaliar sempre um teste de regressão que falhe sem a correção e valide resultado observável.
- Buscar cobertura de pelo menos 80% no New Code como referência comum somente quando não houver exigência específica no
  Quality Gate do projeto.
- Não criar testes artificiais que apenas executem linhas ou burlem medição sem comprovar comportamento.

## 8. Dívida técnica

Não introduzir deliberadamente `TODO` sem contexto e critério de resolução, `FIXME` sem justificativa, código comentado,
workaround tratado como solução permanente, duplicação por rapidez, bypass de validação ou autorização, nem exceção
silenciosa. Se uma limitação inevitável permanecer no escopo, documentar causa, impacto e condição objetiva de resolução
conforme o padrão do projeto.

## Tratamento de erros

- Nunca esconder erro com `catch` vazio ou equivalente.
- Conforme a responsabilidade da camada, tratar, propagar, registrar com contexto seguro, converter em erro de domínio ou
  transformar em resposta apropriada.
- Capturar apenas quando houver ação útil; preservar a causa ao relançar ou converter o erro.
- Logs não podem expor secrets nem dados sensíveis desnecessários.

## Quality Profile, Quality Gate e validação

- Identificar no projeto afetado a configuração existente do SonarQube, como `sonar-project.properties`, workflow de CI,
  Quality Profile, Quality Gate, exclusões, definição de New Code e comandos já adotados.
- O Quality Profile e o Quality Gate reais do projeto têm prioridade sobre as referências de cobertura e duplicação desta
  skill. Não presumir que todos os projetos usam os mesmos limites.
- Não adicionar `NOSONAR` ou supressões apenas para esconder problemas, desabilitar regras, excluir arquivos sem
  justificativa técnica real, reduzir cobertura exigida nem alterar o Quality Gate para fazer código ruim passar. Corrigir
  a causa. Falso positivo comprovado deve seguir o processo do projeto e possuir justificativa técnica rastreável.
- Quando houver scanner local já configurado e sua execução for segura no fluxo existente, executar a análise do projeto
  afetado. Não inventar configuração. Se o scan depender da CI ou de credenciais, executar as validações locais cabíveis,
  proteger tokens e informar claramente que o Quality Gate não foi confirmado.
- Se a CI ou o SonarQube reportar problema introduzido pela tarefa, corrigir a causa e repetir a validação relevante antes
  de concluir. Registrar achados legados fora do New Code somente como limite, sem corrigi-los sem pedido explícito.

## Checklist obrigatório antes de finalizar alteração de código

Responder mentalmente e corrigir qualquer problema encontrado antes de concluir:

1. Introduzi algum bug provável?
2. Introduzi vulnerabilidade?
3. A autorização está correta?
4. Entradas externas estão validadas?
5. Criei duplicação relevante?
6. Aumentei complexidade sem necessidade?
7. Existe código morto?
8. Existem imports ou variáveis sem uso?
9. Existem exceções silenciosas?
10. Há secrets ou dados sensíveis?
11. Alguma regra de negócio precisa de teste?
12. Corrigi um bug que deveria possuir teste de regressão?
13. Existe provável violação de SonarQube no código que alterei?
14. Estou mascarando algum problema em vez de corrigir sua causa?
15. O código tocado ficou pelo menos tão sustentável quanto estava?

# 🔐 SEGURANÇA

- nunca expor segredos
- documentar variáveis de ambiente

# 🧾 SESSÃO, VISITAS E AÇÕES

Todo projeto novo com interface, API pública, autenticação ou fluxo de usuário deve prever registro de sessões,
visitas e ações de forma proporcional ao produto e à legislação aplicável. Em projeto existente, estas regras se
aplicam apenas quando a tarefa tocar no fluxo de sessão, visitas, ações, analytics ou em seu contrato direto.

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

Todo projeto novo deve ter documentação e implementação mínima de health/status. Em projeto existente, aplicar
estas regras somente quando a tarefa criar ou alterar health/status, monitoramento, deploy ou infraestrutura que
dependa desses sinais. Uma mudança sem relação com esse fluxo não autoriza procurar ou implantar healthchecks.

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
