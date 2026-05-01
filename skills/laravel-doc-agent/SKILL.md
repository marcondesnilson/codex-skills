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
- Para seguranca de login em APIs Laravel, usar JWT como padrao de autenticacao stateless
- Implementar login, refresh e logout com invalidacao/rotacao de tokens quando o pacote escolhido suportar
- Configurar expiracao curta para access token e expiracao controlada para refresh token
- Armazenar segredo JWT apenas em variaveis de ambiente; nunca versionar chaves ou tokens
- Proteger rotas autenticadas com middleware/guard JWT e cobrir fluxos de login com testes feature

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

- Em backend Laravel, toda rota, controller, service, action, job, listener e classe de regra de negocio deve ter tratamento explicito de erro com `try/catch`
- Sempre preferir `catch (Throwable $e)` para capturar erros e excecoes de forma abrangente
- Ao capturar erro: registrar com contexto relevante (ex.: id do recurso, usuario, payload filtrado) e retornar resposta consistente
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
