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
- Manter linhas com no máximo 120 caracteres para evitar apontamentos recorrentes do Sonar
- Manter controllers enxutos; regra de negocio em services, actions ou use cases
- Usar recursos nativos do Laravel antes de criar solucoes manuais paralelas
- Validacao deve ficar em Form Requests quando houver entrada HTTP com regras relevantes
- Autorizacao deve ficar em Policies, Gates ou middleware, conforme o padrao do projeto
- Serializacao de resposta deve usar API Resources, DTOs ou presenters quando houver contrato de API
- Queries complexas devem ficar em escopos, query builders dedicados, repositorios ou classes de consulta
- Evitar logica de infraestrutura misturada com regra de negocio

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

- Todo backend Laravel deve expor endpoints publicos de monitoramento: `GET /health/live`, `GET /health/ready`
  e `GET /status`
- Manter `GET /health` como alias simples de liveness quando houver necessidade de compatibilidade
- `GET /health/live` deve ser minimo, rapido e nao consultar banco, Redis, filas ou servicos externos
- `GET /health/live` deve retornar `200` com payload `{"status":"ok"}` quando a aplicacao estiver viva
- `GET /health/ready` deve verificar se a aplicacao esta pronta para receber trafego
- Readiness deve usar checks modulares, tolerantes a falhas e com indicacao de criticidade
- Checks recomendados: `database`, `redis`, `queue`, `workers`, `disk` e APIs externas criticas do projeto
- Readiness deve retornar `200` com `status: ok` quando todos os checks criticos estiverem saudaveis
- Readiness deve retornar `200` com `status: degraded` quando apenas checks nao criticos falharem
- Readiness deve retornar `503` com `status: error` quando qualquer check critico falhar
- Payload de readiness deve incluir `status`, `uptime`, `timestamp` e objeto `checks`
- Cada check deve informar `status`, `latency_ms`, `critical` e detalhes seguros quando necessario
- `GET /status` deve ser uma pagina HTML para humanos consumindo `/health/ready`
- A pagina `/status` deve exibir status geral, API, uptime, ultima verificacao, servicos e latencia
- A pagina `/status` pode usar tema escuro e atualizacao automatica curta, como 5 segundos
- Docker/Swarm/Kubernetes devem usar `/health/live` no healthcheck/liveness do container
- Nao usar `/health/ready` como healthcheck de container; readiness deve orientar roteamento/trafego
- Organizar checks em `app/Support/Health/Checks` seguindo uma interface `HealthCheckInterface`
- Centralizar execucao e agregacao dos checks em service dedicado, como `App\Support\Health\ReadinessService`
- Para adicionar checks, criar classe em `app/Support/Health/Checks`, implementar `name()` e `run()`
- Documentar endpoints, payloads, checks, criticidade e exemplos de configuracao Docker/Swarm
- Cobrir liveness e readiness com testes feature, incluindo falha critica, falha nao critica e sucesso

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

- Todo projeto Laravel criado ou alterado deve ter auditoria base com `owen-it/laravel-auditing`
- Adicionar/configurar `config/audit.php` com auditoria controlada por `AUDITING_ENABLED` e default `true`
- Usar resolver de usuario considerando guards em ordem `api`, `web`
- Auditar eventos `created`, `updated`, `deleted` e `restored`
- Excluir globalmente campos sensiveis como `password`, `remember_token`, tokens, secrets e credenciais
- Usar driver `database` com tabela `audits`
- Registrar o IP publico real do usuario, nao o IP interno do servidor ou proxy
- Em ambientes com proxy/CDN/load balancer, confiar em headers como `CF-Connecting-IP`, `True-Client-IP`
  e `X-Forwarded-For` somente quando a origem da requisicao for confiavel
- Em producao publica, preferir lista explicita de IPs/CIDRs dos proxies reais por variavel de ambiente
- Quando usar `X-Forwarded-For`, extrair e validar corretamente o primeiro IP publico valido da lista
- Se a origem da requisicao nao for confiavel, usar apenas `REMOTE_ADDR`
- Criar migration da tabela `audits` compativel com o padrao de IDs do projeto
- Quando o projeto usar ULID, definir `user_id` e `auditable_id` como `char(26)`
- Modelos persistentes de dominio devem implementar `OwenIt\Auditing\Contracts\Auditable` e usar o trait
  `OwenIt\Auditing\Auditable`, exceto quando houver justificativa explicita
- Para telas administrativas ou historico de entidades, expor endpoints autenticados de historico quando fizer sentido
- Documentar a implantacao da auditoria, variaveis de ambiente, modelos auditados e exemplos de retorno

# TRATAMENTO DE ERROS (OBRIGATORIO)

- Em backend Laravel, toda rota, controller, service, action, job, listener e classe de regra de negocio deve ter
  tratamento explicito de erro com `try/catch`
- Sempre preferir `catch (Throwable $e)` para capturar erros e excecoes de forma abrangente
- Ao capturar erro: registrar com contexto relevante (ex.: id do recurso, usuario, payload filtrado) e retornar
  resposta consistente
- Nao engolir erro silenciosamente; sempre logar e padronizar retorno HTTP/DTO de erro
- Se necessario, relancar com contexto adicional apos log

Exemplo base:

```php
<?php

use Throwable;
use Illuminate\Support\Facades\Log;

try {
    // regra de negocio / chamada externa / persistencia
} catch (Throwable $e) {
    Log::error('Falha ao processar operacao X', [
        'error' => $e->getMessage(),
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

# DOCUMENTACAO

Se houver alteracao funcional:
- atualizar docs do projeto
- atualizar index da documentacao local
- manter exemplos de uso e contratos atualizados
