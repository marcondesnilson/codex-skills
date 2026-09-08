---
name: laravel-doc-agent
description: Aplicar padrões obrigatórios e incrementais de Laravel, documentação, SonarQube e SSE com Redis Streams. Use sempre que esta skill for citada no AGENTS.md aplicável ou quando a tarefa envolver código, configuração, testes ou arquitetura Laravel.
---

# CONTEXTO

Skill de apoio para mudanças em projetos Laravel.

# OBRIGATORIEDADE E ESCOPO

- Se esta skill estiver citada no `AGENTS.md` aplicável, seguir suas instruções em toda tarefa Laravel dentro desse escopo.
- Não substituir, flexibilizar ou ignorar estas regras por preferência própria. Em caso de conflito, seguir instruções de maior prioridade e informar o conflito.
- Em Laravel existente, aplicar os padrões somente ao fluxo, código, configuração, testes, documentação e contratos diretamente tocados pela tarefa.
- Inspecionar apenas rotas, classes, dependências e documentação necessárias para entender e validar a mudança. Não procurar problemas nem auditar módulos não relacionados.
- Corrigir legado gradualmente: adequar a parte alterada e preservar o restante, salvo dependência direta indispensável para a mudança funcionar.
- Não ampliar o pedido para refatorar controllers, models, rotas, autenticação, auditoria, tratamento de erros ou healthchecks fora do fluxo afetado.
- Em projeto Laravel novo, aplicar os padrões desde a base no escopo solicitado.

# INTEGRAÇÃO COM O GLOBAL E FRONTEND

Consultar `global-doc-agent` pelo catálogo disponível e suas referências pertinentes. Global define requisitos;
esta skill define implementação Laravel. Não reiniciar leituras já realizadas nem duplicar a política global.
Se houver Blade ou outra UI afetada, consultar também `frontend-doc-agent`. API pura não exige tela Sobre,
termos públicos ou módulo frontend: disponibilizar versão e informações necessárias pelo contrato/canal adequado.
A página operacional de status, quando necessária, é exceção mínima ao backend-only, não autorização para adotar
uma stack frontend. Componentes web eventualmente tocados continuam seguindo a skill frontend.

Ao implementar identificação de versão, usar a fonte de release existente por configuração Laravel e serialização
apropriada; expor somente metadados permitidos ao destinatário. Não criar endpoint novo se o contrato atual resolver.
Padrões de IDs, auth, payload e rotas abaixo são defaults na ausência de decisão local compatível; não migrar contratos
existentes apenas para padronizar. JWT exige pacote existente/selecionado compatível: não presumir comando/guard instalado.

# ORDEM

1. Ler documentação local relevante do projeto Laravel, se existir
2. Confirmar versão e stack (Laravel, PHP, banco, filas)
3. Implementar mudança mantendo padrão existente
4. Validar com testes/lint/comandos do projeto
5. Atualizar documentação afetada

# PADROES LARAVEL

- Preferir regras já adotadas no projeto antes de introduzir novas convenções
- Manter linhas com no máximo 120 caracteres para evitar apontamentos recorrentes do Sonar
- Manter controllers enxutos; regra de negocio em services, actions ou use cases
- Usar recursos nativos do Laravel antes de criar solucoes manuais paralelas
- Validacao deve ficar em Form Requests quando houver entrada HTTP com regras relevantes
- Autorizacao deve ficar em Policies, Gates ou middleware, conforme o padrao do projeto
- Serializacao de resposta deve usar API Resources, DTOs ou presenters quando houver contrato de API
- Queries complexas devem ficar em escopos, query builders dedicados, repositorios ou classes de consulta
- Evitar logica de infraestrutura misturada com regra de negocio
- Usar o ecossistema Laravel completo sempre que possivel, em vez de concentrar tudo em controllers ou services

# ROTAS E FILTROS (OBRIGATORIO)

- Antes de criar rota nova, revisar `routes/*.php` e confirmar se ja existe endpoint com o mesmo recurso,
  listagem, consulta ou intencao funcional
- Nao criar varias rotas para o mesmo objetivo apenas mudando criterio de busca, status, periodo, ordenacao,
  agrupamento, tipo ou visao da mesma colecao
- Para listagens e consultas, priorizar filtros por query string no endpoint canônico, como
  `GET /orders?status=pending&from=2026-01-01&to=2026-01-31`
- Validar filtros em Form Request dedicado e aplicar a consulta em scopes, query builders, repositories ou classes
  `app/Queries`, mantendo o controller apenas como orquestrador HTTP
- Criar rota separada somente quando houver recurso diferente, acao de dominio diferente, mudanca real de metodo HTTP,
  contrato de payload incompatível ou necessidade clara de autorizacao/middleware distintos
- Quando houver duvida entre nova rota e filtro, escolher filtro primeiro e documentar os parametros aceitos no contrato
  da API
- Evitar endpoints redundantes como `/users/active`, `/users/inactive`, `/users/by-role/{role}` quando
  `GET /users?status=active&role=admin` resolver o mesmo contrato com clareza

# ARQUITETURA DE APLICACAO (OBRIGATORIO)

Controllers nao devem concentrar regra de negocio. Eles devem apenas:
- receber a request
- acionar validacao/autorizacao
- chamar service, action ou use case
- transformar o resultado em response/resource
- tratar excecoes de borda HTTP quando necessario

Regra pratica para controllers:
- ideal: ate 150 linhas por controller
- aceitavel: ate 300 linhas quando houver muitos endpoints simples e coesos
- acima de 300 linhas: revisar e extrair responsabilidades antes de adicionar novas funcionalidades
- acima de 500 linhas: tratar como debito tecnico e propor refatoracao obrigatoria
- milhares de linhas em controller nao sao aceitaveis, exceto arquivo legado com justificativa documentada

Ao criar ou alterar funcionalidades Laravel:
- criar service/action/use case para cada fluxo de negocio relevante
- manter transacoes, integracoes externas e orquestracao de dominio fora do controller
- mover validacao para `app/Http/Requests`
- mover formatacao de saida para `app/Http/Resources` ou camada equivalente
- mover regras de permissao para `app/Policies`, Gates ou middleware
- mover efeitos assíncronos para Jobs, Events e Listeners quando fizer sentido
- mover regras reutilizaveis de modelo para casts, accessors/mutators, observers ou domain services
- documentar no projeto a organizacao adotada para services/actions/use cases

# USO DO ECOSSISTEMA LARAVEL (OBRIGATORIO)

Ao implementar ou refatorar funcionalidades Laravel, escolher primeiro os recursos nativos do framework que melhor
representam cada responsabilidade:
- Form Requests para validacao e preparacao de entrada HTTP
- Policies, Gates e middleware para autorizacao e protecao de rotas
- API Resources, DTOs ou presenters para contratos de resposta
- Jobs e queues para trabalho assíncrono, pesado, retryable ou dependente de integracoes externas
- Events e Listeners para efeitos colaterais desacoplados do fluxo principal
- Observers para reacoes a eventos de modelo, quando a regra for diretamente ligada ao ciclo de vida da entidade
- Notifications, Mailables e Broadcasts para comunicacao, alertas e atualizacoes em tempo real
- Commands, Schedule e queue workers para rotinas operacionais e processamento recorrente
- Casts, accessors, mutators, scopes, query builders e Collections para comportamento proprio de modelo ou consulta
- Service Providers, config files e bindings do container para configuracao, integracao e inversao de dependencia

Nao criar implementacoes manuais paralelas quando Laravel ja oferecer uma primitiva adequada. Services, actions e use
cases devem orquestrar regras de aplicacao, mas devem delegar validacao, autorizacao, serializacao, eventos,
observacao de modelos, notificacoes, jobs e tarefas agendadas para os recursos nativos correspondentes.

Estruturas recomendadas, adaptando ao padrao existente:
- `app/Services/<Dominio>/<Nome>Service.php` para servicos de dominio ou aplicacao
- `app/Actions/<Dominio>/<Verbo><Entidade>Action.php` para casos de uso pontuais
- `app/UseCases/<Dominio>/<Nome>UseCase.php` quando o projeto ja adotar nomenclatura de use cases
- `app/Queries/<Dominio>/<Nome>Query.php` para consultas complexas e filtros reutilizaveis
- `app/Data` ou `app/DTO` para objetos de transporte quando o projeto ja usar DTOs

Antes de mexer em controller grande:
- mapear responsabilidades existentes
- extrair primeiro validacao, autorizacao, queries, formatacao e integracoes externas
- preservar contratos HTTP e payloads existentes
- cobrir o fluxo com testes feature antes ou junto da refatoracao
- registrar a decisao na documentacao local do projeto

# REGRAS BACKEND (TOKEN-SAVER)

- IDs: usar ULID como padrao; persistir em minusculo no banco
- Rotas: quando Laravel for apenas backend, nao usar prefixo `/api`
- Escopo backend-only: nao criar/manter pastas, plugins, pacotes ou assets de frontend

# HEALTHCHECK E STATUS (OBRIGATORIO)

- Todo backend Laravel novo deve fornecer `GET /health/live`, `GET /health/ready` e status operacional quando útil.
  Liveness pode ser público com payload mínimo; readiness detalhada e `GET /status` exigem rede/identidade autorizada.
  Se houver status público, apresentar somente disponibilidade agregada, sem serviços internos ou detalhes de infraestrutura
- Em backend existente, aplicar esta seção somente quando a tarefa criar ou alterar health/status, monitoramento,
  deploy ou infraestrutura dependente desses endpoints
- Manter `GET /health` como alias simples de liveness quando houver necessidade de compatibilidade
- `GET /health/live` deve ser minimo, rapido e nao consultar banco, Redis, filas ou servicos externos
- `GET /health/live` deve retornar `200` com payload `{"status":"ok"}` quando a aplicacao estiver viva
- `GET /health/ready` deve verificar se a aplicacao esta pronta para receber trafego
- Readiness deve usar checks modulares, tolerantes a falhas e com indicacao de criticidade
- Checks recomendados: `database`, `redis`, `queue`, `workers`, `disk` e APIs externas criticas do projeto
- Readiness deve retornar `200` com `status: ok` quando todos os checks criticos estiverem saudaveis
- Readiness deve retornar `200` com `status: degraded` quando apenas checks nao criticos falharem
- Readiness deve retornar `503` com `status: error` quando qualquer check critico falhar
- No canal operacional autorizado, payload de readiness deve incluir `status`, `uptime`, `timestamp` e objeto `checks`
- Nesse canal, cada check deve informar `status`, `latency_ms`, `critical` e detalhes seguros quando necessario
- Quando necessário, `GET /status` deve ser uma pagina HTML operacional consumindo `/health/ready` com o mesmo controle de acesso
- A pagina operacional autorizada `/status` deve exibir status geral, API, uptime, ultima verificacao, servicos e latencia
- A pagina `/status` pode usar tema escuro e atualizacao automatica curta, como 5 segundos
- Docker/Swarm/Kubernetes devem usar `/health/live` no healthcheck/liveness do container
- Nao usar `/health/ready` como healthcheck de container; readiness deve orientar roteamento/trafego
- Organizar checks em `app/Support/Health/Checks` seguindo uma interface `HealthCheckInterface`
- Centralizar execucao e agregacao dos checks em service dedicado, como `App\Support\Health\ReadinessService`
- Para adicionar checks, criar classe em `app/Support/Health/Checks`, implementar `name()` e `run()`
- Documentar endpoints, payloads, checks, criticidade e exemplos de configuracao Docker/Swarm
- Cobrir liveness e readiness com testes feature, incluindo falha critica, falha nao critica, sucesso e
  acesso negado/ausência de detalhes internos para destinatários não autorizados

# DADOS E SEGURANCA

- Nao expor segredos
- Revisar impacto em migrations e compatibilidade de deploy
- Garantir validacao e autorizacao para endpoints alterados
- Atualizar variaveis de ambiente quando necessario

# AUTENTICACAO JWT E SEGURANCA DE API

- Para seguranca de login em APIs Laravel puras, usar JWT como padrao de autenticacao stateless
- Em backend-only, manter rotas sem prefixo `/api` quando este for o padrao do projeto
- Gerar segredo JWT com `php artisan jwt:secret` e manter a chave apenas em variaveis de ambiente
- Configurar guard de API com driver `jwt`
- Proteger rotas autenticadas com middleware `auth:api`
- Enviar token apenas no header `Authorization: Bearer <token>`
- Login deve validar email/senha, autenticar credenciais e retornar token no formato padronizado da API
- Refresh deve renovar a sessao conforme TTL/refresh TTL configurados
- Logout deve invalidar o token, usando blacklist quando o pacote JWT oferecer suporte
- Token expirado, invalido ou ausente deve retornar `401` com resposta padronizada
- Nao retornar stack trace, classe de exception, mensagem interna ou detalhes de infraestrutura em erros de auth
- Respostas da API devem seguir formato consistente: `success`, `data` e `error`
- Erros de autenticacao devem usar mensagem generica, como `Nao autorizado`
- Aplicar rate limit especifico em login para reduzir brute force, como middleware `throttle:login`
- Configurar TTL curto para access token e renovacao controlada por refresh
- Usuario autenticavel deve implementar `JWTSubject` quando o pacote utilizado exigir
- Payload JWT nao deve conter dados sensiveis, permissoes amplas demais ou informacoes mutaveis desnecessarias
- Nunca persistir JWT em armazenamento inseguro no cliente; preferir fluxo via header `Authorization`
- Exigir HTTPS em producao para qualquer rota que trafegue JWT
- Permitir HTTP apenas em desenvolvimento local por configuracao explicita de ambiente
- Sanitizar e validar inputs de login com Form Request quando aplicavel
- Cobrir login, refresh, logout, token ausente, token invalido e token expirado com testes feature

# AUDITORIA (OBRIGATORIO)

- Todo projeto Laravel novo deve avaliar operações auditáveis conforme o Global. Quando necessárias, implementar
  auditoria base com `owen-it/laravel-auditing`, salvo solução equivalente já adotada ou justificativa documentada.
  Verificar manutenção, compatibilidade, licença e vulnerabilidades antes de adicionar o pacote
- As regras de configuração abaixo se aplicam ao usar esse pacote; não instalar auditoria para operações triviais
- Em projeto existente, aplicar esta seção somente quando a tarefa criar ou alterar auditoria ou modelos/fluxos cujo
  contrato de auditoria seja diretamente afetado; não instalar o pacote nem revisar outros modelos por uma mudança não relacionada
- Adicionar/configurar `config/audit.php` com auditoria controlada por `AUDITING_ENABLED` e default `true`
- Usar resolver de usuario considerando guards em ordem `api`, `web`
- Auditar eventos `created`, `updated`, `deleted` e `restored`
- Excluir globalmente campos sensiveis como `password`, `remember_token`, tokens, secrets e credenciais
- Usar driver `database` com tabela `audits`
- Registrar o IP publico real do usuario, nao o IP interno do servidor ou proxy
- Em ambientes com proxy/CDN/load balancer, confiar em headers como `CF-Connecting-IP`, `True-Client-IP`
  e `X-Forwarded-For` somente quando a origem da requisicao for confiavel
- Em producao publica, preferir lista explicita de IPs/CIDRs dos proxies reais por variavel de ambiente
- Quando usar `X-Forwarded-For`, resolver a cadeia a partir dos proxies confiáveis com os recursos do framework;
  não aceitar o primeiro IP público sem validar a cadeia, pois pode ter sido inserido pelo cliente
- Se a origem da requisicao nao for confiavel, usar apenas `REMOTE_ADDR`
- Criar migration da tabela `audits` compativel com o padrao de IDs do projeto
- Quando o projeto usar ULID, definir `user_id` e `auditable_id` como `char(26)`
- Modelos persistentes de dominio abrangidos pela finalidade de auditoria devem implementar `OwenIt\Auditing\Contracts\Auditable` e usar o trait
  `OwenIt\Auditing\Auditable`, exceto quando houver justificativa explicita
- Para telas administrativas ou historico de entidades, expor endpoints autenticados de historico quando fizer sentido
- Documentar a implantacao da auditoria, variaveis de ambiente, modelos auditados e exemplos de retorno

# TRATAMENTO DE ERROS (OBRIGATORIO)

- No código Laravel novo ou diretamente alterado, tratar erros de forma explícita nas bordas em que seja necessário
  registrar contexto, recuperar a operação, converter o erro ou padronizar a resposta
- Capturar somente quando houver tratamento útil; usar a exception mais específica possível e, em uma borda que precise
  abranger erros e exceções, preferir `catch (Throwable $e)`
- Ao capturar erro, conforme o contexto: recuperar, converter em erro de domínio ou resposta consistente, registrar com
  dados seguros ou relançar preservando a causa
- Nao engolir erro silenciosamente nem registrar secrets, tokens ou payloads sensíveis

Exemplo base:

```php
<?php

use Throwable;
use Illuminate\Support\Facades\Log;

try {
    // regra de negocio / chamada externa / persistencia
} catch (Throwable $e) {
    Log::error('Falha ao processar operacao X', [
        'error_type' => 'operation_failed',
        'context' => [
            // dados de contexto sem segredo
        ],
    ]);

    throw $e;
}
```

# TESTES

- Executar testes focados no modulo alterado
- Priorizar testes feature para fluxos HTTP e unitarios para regra de negocio
- Evitar alterar suites nao relacionadas sem necessidade

# SERVER-SENT EVENTS (SSE)

Ao criar ou alterar SSE, ler e seguir integralmente [references/sse.md](references/sse.md).

Regras essenciais:

- Centralizar endpoints SSE sob o prefixo plural `/streams`, dentro do prefixo base já adotado pelo projeto.
- Criar rotas `GET` explícitas por fluxo, como `/streams/notifications`; não usar um catch-all público
  `/streams/{channel}` nem espalhar SSE em rotas fora desse namespace.
- Para eventos originados por alterações Eloquent, usar Observer executado após o commit e um publisher dedicado
  que grave no Redis. O Observer não deve abrir o stream HTTP nem executar consultas adicionais.
- Usar Redis Streams com `XADD` e `XREAD` como padrão para permitir cursor, retenção limitada e reconexão por
  `Last-Event-ID`. Não usar polling no banco e não usar Pub/Sub puro quando houver necessidade de replay.
- O loop SSE deve ler apenas do Redis depois da autenticação e autorização iniciais. Nunca consultar banco a cada
  ciclo, heartbeat ou evento.
- Padronizar `id`, `event`, `data` JSON, `retry`, heartbeat, encerramento controlado, autenticação, isolamento de
  tenant, limites de conexão e comportamento quando o cursor tiver expirado.
- Manter payloads pequenos e seguros. Preferir eventos de alteração/invalidação e obter estado completo pelo
  endpoint REST canônico quando necessário.
- Documentar e testar publicação, formato, reconexão, replay, autorização, isolamento, falha do Redis, proxy e
  ausência de consultas ao banco dentro do loop.

# QUALIDADE LARAVEL/PHP E SONARQUBE

Aplicar integralmente a política de qualidade e o checklist do `global-doc-agent`. Esta seção apenas especializa o New Code
Laravel/PHP e não substitui as decisões arquiteturais já adotadas pelo projeto:

- Usar Form Requests para entrada HTTP com validação relevante e Policies, Gates ou middleware para autorização. Não
  considerar validação ou proteção da interface como autorização.
- Usar API Resources, DTOs ou presenters conforme o padrão existente para manter serialização e contratos consistentes.
- Manter controllers focados em HTTP e Blade focado em apresentação; regras de negócio relevantes pertencem a Services,
  Actions ou Use Cases já adotados pelo projeto.
- Usar Jobs/Queues para processamento assíncrono e Events/Listeners quando o desacoplamento representar corretamente o
  fluxo, sem mover trabalho artificialmente apenas para satisfazer uma regra estrutural.
- Usar transactions nas operações que precisam ser atômicas e considerar concorrência, idempotência, retries e efeitos
  externos. Não manter transação aberta além do necessário.
- Definir casts e scopes adequados ao domínio e revisar tipos, atributos ausentes e retornos nullable.
- Evitar N+1; usar eager loading quando os relacionamentos forem realmente consumidos e validar o custo das consultas do
  fluxo alterado.
- Preferir Eloquent ou Query Builder com bindings. SQL bruto e comandos exigem necessidade comprovada, parâmetros seguros
  e revisão explícita contra injeção.
- Proteger Mass Assignment conforme o padrão do projeto com `$fillable`, `$guarded`, DTOs ou atribuição explícita; nunca
  persistir indiscriminadamente toda a entrada da request.
- Não usar `env()` fora de arquivos de configuração e nunca inserir secrets em código, logs, respostas ou fixtures
  versionadas.
- Tratar exceptions conforme a seção específica desta skill, preservando causa e contrato de resposta.
- Remover imports PHP não utilizados e código morto resultante da alteração.
- Cobrir regras de negócio, validação, autorização, APIs, Jobs e correções de bugs com testes focados, incluindo regressão
  quando aplicável.
- Executar os comandos Laravel/PHP de testes, lint, análise estática e Sonar já configurados para o fluxo afetado. Não
  inventar configuração nem afirmar que o Quality Gate passou quando o scan não foi executado.

Em Laravel existente, limitar a inspeção e as correções ao New Code, às linhas tocadas e aos contratos diretos. Não limpar
outros módulos apenas por haver dívida no Overall Code.

# DOCUMENTACAO

Se a mudança afetar comportamento, configuração, arquitetura, API, deploy ou operação no escopo tocado:
- atualizar docs do projeto
- manter index/MOC da documentacao local coerente, editando quando links, navegação ou resumo mudarem
- manter exemplos de uso e contratos atualizados
