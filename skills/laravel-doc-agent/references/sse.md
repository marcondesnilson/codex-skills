# SSE em Laravel com Redis Streams

Leia esta referência ao criar ou alterar qualquer endpoint, produtor ou consumidor Server-Sent Events em Laravel.

## Decisão arquitetural

Use este fluxo como padrão:

```text
transação do domínio
  -> commit no banco
  -> Eloquent Observer após commit
  -> StreamPublisher
  -> Redis Stream (XADD)
  -> endpoint GET /streams/<fluxo> (XREAD)
  -> cliente SSE
```

O Redis é a fonte do transporte em tempo real. O banco continua sendo a fonte do estado de negócio, mas não deve ser
consultado pelo loop SSE. O evento deve ser produzido com os dados já disponíveis no modelo ou no caso de uso.

Redis Pub/Sub puro não é o padrão porque perde mensagens durante desconexões. Redis Streams mantém um log limitado,
fornece IDs ordenados e permite retomar a leitura com `Last-Event-ID`.

## Namespace de rotas

Centralize todo SSE sob o prefixo plural `/streams`, respeitando o prefixo base existente:

- backend sem prefixo: `/streams/notifications`;
- API versionada: `/v1/streams/notifications`;
- recurso específico: `/streams/orders/{order}`.

Use uma rota `GET` explícita para cada contrato. Não use `/stream*`, rotas espalhadas como `/orders/live` ou um
catch-all público `/streams/{channel}`. A rota explícita mantém controller, Policy, middleware, rate limit e chave
Redis sob controle.

Exemplo:

```php
Route::prefix('streams')
    ->name('streams.')
    ->middleware(['auth:api', 'throttle:streams'])
    ->group(function (): void {
        Route::get('/notifications', NotificationStreamController::class)
            ->name('notifications');

        Route::get('/orders/{order}', OrderStreamController::class)
            ->can('view', 'order')
            ->name('orders.show');
    });
```

Adapte o guard ao projeto. Não altere o prefixo público ou a estratégia de autenticação existente apenas para seguir
o exemplo.

## Responsabilidades Laravel

Organize a implementação em responsabilidades pequenas:

- `app/Observers`: detecta mudanças persistidas relevantes;
- `app/Contracts/Streams/StreamPublisher.php`: contrato de publicação;
- `app/Services/Streams/RedisStreamPublisher.php`: executa `XADD` e aplica retenção;
- `app/Services/Streams/RedisStreamReader.php`: valida cursor e executa `XREAD`;
- `app/Http/Controllers/Streams`: autentica, autoriza e devolve a resposta SSE;
- `config/streams.php`: prefixos de chave, retenção, block timeout, heartbeat, retry e duração máxima;
- testes unitários e feature para produtor, reader e resposta HTTP.

Não coloque serialização, montagem de chave Redis, repetição de leitura ou regras de autorização dentro do Observer ou
controller.

## Observer e publicação após commit

Todo evento SSE provocado pelo ciclo de vida de um model Eloquent deve partir de um Observer. O Observer deve implementar
`ShouldHandleEventsAfterCommit` para não publicar alterações que possam sofrer rollback.

```php
use App\Contracts\Streams\StreamPublisher;
use App\Models\Order;
use Illuminate\Contracts\Events\ShouldHandleEventsAfterCommit;

final class OrderObserver implements ShouldHandleEventsAfterCommit
{
    public function __construct(
        private readonly StreamPublisher $publisher,
    ) {}

    public function updated(Order $order): void
    {
        $this->publisher->publish(
            tenantId: (string) $order->tenant_id,
            topic: 'orders',
            event: 'orders.updated',
            payload: [
                'resource_id' => (string) $order->getKey(),
                'status' => $order->status,
                'updated_at' => $order->updated_at?->toISOString(),
            ],
        );
    }
}
```

Regras do Observer:

- publicar somente eventos relevantes para clientes;
- usar atributos já carregados no model e `getChanges()` quando adequado;
- não executar `refresh()`, `load()`, queries, agregações ou serialização de relacionamentos;
- não publicar antes do commit;
- delegar chave, envelope, JSON, retenção e Redis ao publisher;
- nunca enviar atributos ocultos, credenciais, tokens ou dados pessoais desnecessários.

Se uma alteração de domínio não passar por Eloquent, o caso de uso deve chamar o mesmo `StreamPublisher` após o sucesso.
Não force um Observer artificial nem grave novamente no banco apenas para produzir SSE.

## Redis Streams

O publisher deve usar `XADD` com ID automático `*` e retenção limitada, preferencialmente `MAXLEN ~ <limite>`. Configure
o limite por volume e janela de reconexão; não permita crescimento ilimitado.

Convenção de chave multitenant:

```text
sse:{<tenant-id>}:<topic>
```

As chaves devem ser montadas por código a partir de tenant e tópico autorizados. Nunca aceite a chave Redis ou o tópico
diretamente da URL sem allowlist. Para streams por recurso, derive o tópico no servidor, como
`orders:<order-public-id>`, depois de autorizar o model correspondente.

Use o ID devolvido pelo `XADD` como `id` do evento SSE. O reader usa `XREAD COUNT <n> BLOCK <ms> STREAMS <key> <cursor>`.

- Primeira conexão sem cursor: use `$` para receber apenas eventos posteriores à conexão.
- Reconexão: use o `Last-Event-ID` válido recebido do cliente.
- Após cada lote: avance o cursor para o último ID efetivamente entregue.
- Use `BLOCK` com timeout finito, nunca bloqueio infinito, para emitir heartbeat e verificar desconexão.
- Defina `COUNT` para limitar memória e tempo gasto em cada lote.
- Se o cursor já tiver sido removido pela retenção, envie `stream.reset` e encerre ou solicite sincronização REST.

Não use consumer groups para conexões SSE comuns: cada cliente deve receber sua própria cópia dos eventos. Consumer groups
são adequados a workers que dividem trabalho, não a fan-out para clientes.

## Contrato de evento

Cada evento deve seguir o formato SSE e terminar com uma linha vazia:

```text
id: 1725123456789-0
event: orders.updated
retry: 3000
data: {"schema_version":1,"resource_id":"01...","occurred_at":"2026-08-31T14:00:00Z"}

```

Padronize:

- `id`: ID do Redis Stream;
- `event`: nome estável em minúsculas no formato `<dominio>.<ação>`;
- `data`: JSON UTF-8 válido e compacto;
- `retry`: milissegundos antes da tentativa automática de reconexão;
- `schema_version`: inteiro para evolução compatível do payload;
- `occurred_at`: timestamp UTC em ISO 8601;
- `resource_id`: identificador público quando o evento representar um recurso.

O payload não deve transportar uma coleção ou snapshot grande. Envie os campos mínimos úteis ou um evento de invalidação
para que o cliente atualize o estado pelo endpoint REST canônico. Nunca coloque segredo, token, stack trace ou dado de outro
tenant.

Mudança incompatível no payload exige novo nome de evento ou nova versão de schema com período de compatibilidade.

## Resposta e ciclo da conexão

Confirme a versão do Laravel. Use `response()->eventStream()` quando a versão instalada oferecer o recurso; em versões
anteriores, use `response()->stream()` ou `StreamedResponse` preservando exatamente o protocolo SSE.

Headers mínimos:

```text
Content-Type: text/event-stream
Cache-Control: no-cache, no-transform
X-Accel-Buffering: no
```

Também:

- desabilite buffering e compressão que acumulem chunks;
- envie `: heartbeat\n\n` em intervalo configurável, normalmente entre 15 e 30 segundos;
- faça flush depois de cada evento e heartbeat;
- verifique desconexão do cliente entre leituras;
- encerre a resposta após duração máxima configurável para reciclar workers;
- deixe o cliente reconectar usando `retry` e `Last-Event-ID`;
- não mantenha transação de banco aberta durante a conexão.

Não envie `Connection: keep-alive` de forma fixa quando HTTP/2 ou o proxy gerenciar a conexão. Configure timeouts do proxy,
load balancer e runtime acima do heartbeat e de forma coerente com a duração máxima da resposta.

## Reconexão e recuperação

O navegador reconecta automaticamente `EventSource` e envia `Last-Event-ID` quando o servidor forneceu `id`. O servidor
deve validar sintaxe, tenant, tópico e retenção antes de usar o cursor.

Fluxo esperado:

1. Autorizar usuário, tenant e recurso.
2. Ler e validar `Last-Event-ID`.
3. Sem cursor, iniciar em `$`.
4. Com cursor disponível, reproduzir eventos posteriores via `XREAD`.
5. Com cursor expirado, enviar `stream.reset` com motivo seguro.
6. O cliente executa sincronização REST e abre nova conexão sem cursor antigo.
7. Aplicar backoff com jitter no cliente se ele não usar o retry automático do `EventSource`.

O cliente deve deduplicar pelo `id`, tolerar eventos repetidos e fechar a conexão em logout, troca de tenant, perda de
permissão, mudança de tela quando o fluxo não for mais necessário ou indisponibilidade de rede.

Exemplo mínimo para sessão web no mesmo origin:

```js
const source = new EventSource('/streams/notifications', {
    withCredentials: true,
});

source.addEventListener('orders.updated', (message) => {
    const event = JSON.parse(message.data);

    updateOrder(event.resource_id);
});

source.addEventListener('stream.reset', async () => {
    await synchronizeState();
    source.close();
});

source.onerror = () => {
    // EventSource reconecta automaticamente usando retry e Last-Event-ID.
};
```

Não crie um timer paralelo de reconexão quando usar o comportamento automático do `EventSource`. Clientes baseados em
`fetch` devem implementar backoff exponencial com jitter, preservar o último ID confirmado e impedir conexões duplicadas.

## Autenticação, autorização e CORS

Autorize antes de iniciar a resposta; após o primeiro byte não é possível trocar de forma confiável para uma resposta JSON
de erro.

- Use sessão/cookie seguro e `EventSource` no mesmo origin quando esse for o padrão web.
- O `EventSource` nativo não permite definir livremente o header `Authorization`.
- Quando o projeto exigir Bearer JWT, use cliente SSE baseado em `fetch` ou o mecanismo oficial da stack que aceite headers.
- Não coloque JWT ou token de longa duração na query string.
- Se URL assinada for indispensável, use token dedicado, de uso restrito e expiração curta; não reutilize access token.
- Em cross-origin, configure allowlist CORS explícita e credenciais somente para origens confiáveis.
- Resolva tenant no servidor; nunca confie apenas no tenant informado pela URL.
- Revalide permissões a cada reconexão e limite conexões simultâneas por usuário, tenant e IP.

## Banco, desempenho e capacidade

Meta obrigatória: zero consultas ao banco dentro do loop SSE depois da autenticação/autorização inicial.

- Não faça polling de tabela, `exists()`, `find()`, `refresh()` ou contagem periódica.
- Não carregue model ou relacionamento para cada mensagem.
- Não use banco como fila, cursor ou heartbeat.
- Cacheie metadados de autorização no mecanismo já adotado quando seguro, sem enfraquecer revogação.
- Use conexão Redis dedicada a leituras bloqueantes; não retenha a conexão usada pelo cache geral.
- Configure timeout, limite de conexões, memória, retenção e métricas do Redis.

Cada SSE mantém uma requisição aberta. Calcule capacidade de PHP-FPM/Octane, servidor web e load balancer para o número de
clientes simultâneos. Em escala incompatível com workers PHP bloqueados, use Octane ou um gateway SSE dedicado que continue
consumindo o mesmo contrato Redis; não aumente workers sem medir memória e conexões.

## Falhas e garantia de entrega

Publicação após commit no banco e escrita no Redis não formam uma transação atômica. O padrão sem outbox oferece entrega
best effort com replay enquanto o evento existir no Redis.

- Defina timeout curto e retry limitado para publicação.
- Se usar Job de publicação, use fila Redis e payload idempotente; não use fila de banco para este fluxo.
- Registre falhas sem payload sensível e monitore taxa de publicação, conexões, lag, resets e desconexões.
- Se perda de evento for inaceitável, documente a exigência e proponha transactional outbox. Essa exceção usa banco e
  precisa de decisão explícita de arquitetura, retenção e limpeza.
- Se Redis falhar antes de iniciar o stream, retorne `503` seguro. Se falhar depois do início, emita evento de erro quando
  possível, encerre e deixe o cliente reconectar.

## Configuração

Centralize parâmetros em `config/streams.php` e variáveis de ambiente equivalentes:

- `SSE_REDIS_CONNECTION`: conexão Redis exclusiva;
- `SSE_KEY_PREFIX`: prefixo seguro das chaves;
- `SSE_STREAM_MAXLEN`: retenção máxima aproximada por stream;
- `SSE_BATCH_SIZE`: tamanho máximo do lote;
- `SSE_XREAD_BLOCK_MS`: timeout finito de `XREAD BLOCK`;
- `SSE_HEARTBEAT_SECONDS`: intervalo de heartbeat;
- `SSE_CONNECTION_MAX_SECONDS`: duração máxima da resposta;
- `SSE_RETRY_MS`: retry sugerido ao cliente;
- limites simultâneos por usuário, tenant e IP com nomes coerentes ao projeto.

Não leia `env()` fora de arquivos de configuração. Não use valores sem limite em produção.

## Operação e smoke test

- Configure proxy e CDN para não armazenar nem transformar `text/event-stream`.
- Desative buffering na rota e mantenha timeouts maiores que o heartbeat.
- Inclua Redis e capacidade de conexão SSE na readiness quando forem críticos para receber tráfego.
- Meça conexões ativas, duração, eventos publicados/entregues, bytes, lag, retries, resets e erros Redis.
- Faça deploy drenando conexões antigas; clientes devem reconectar na nova instância pelo cursor.

Teste manualmente sem colocar token na URL ou no histórico do terminal:

```sh
curl -N \
  -H 'Accept: text/event-stream' \
  -H 'Last-Event-ID: <redis-stream-id>' \
  --cookie '<cookie-de-sessao-seguro>' \
  https://app.example.com/streams/notifications
```

Use conta e tenant de teste. Remova o header `Last-Event-ID` para validar a primeira conexão e repita com um ID conhecido
para validar replay. Confirme que cada chunk chega antes do encerramento e que o proxy não agrupa eventos.

## Testes obrigatórios

Cubra no mínimo:

- todas as rotas SSE sob `/streams` e nenhuma nova rota SSE fora do namespace;
- método `GET`, middleware, autenticação, Policy e isolamento entre tenants;
- Observer publicado somente após commit e sem publicação após rollback;
- Observer sem consultas adicionais ao banco;
- `XADD` com chave, envelope e retenção corretos;
- `XREAD` a partir de `$` e de `Last-Event-ID`;
- replay sem lacuna dentro da retenção e deduplicação por ID;
- cursor expirado produzindo `stream.reset`;
- headers, `id`, `event`, `data`, `retry`, heartbeat e flush;
- zero consultas ao banco dentro do loop depois da autorização;
- encerramento por desconexão e duração máxima;
- Redis indisponível antes e depois do início da resposta;
- payload sem secrets, dados ocultos ou vazamento entre tenants.

Use fakes somente nos testes unitários do publisher/Observer. Mantenha pelo menos um teste de integração com Redis real ou
container para provar `XADD`, `XREAD`, bloqueio, cursor e retenção.

## Documentação obrigatória do projeto consumidor

Ao implementar SSE, documente no projeto:

- matriz de endpoints, middleware, autenticação e autorização;
- catálogo de eventos e versões de payload;
- sequência Observer -> publisher -> Redis -> endpoint -> cliente;
- nomes de chaves sem expor identificadores ou secrets reais;
- retenção, replay, `Last-Event-ID`, `stream.reset`, retry e heartbeat;
- comportamento do cliente em conexão, reconexão, logout e troca de tenant;
- configuração de Redis, proxy, CORS, timeouts e limites de conexão;
- objetivo de zero queries no loop e como ele foi validado;
- métricas, alertas, falhas conhecidas e garantia de entrega;
- comandos de teste e smoke test com `curl -N` usando credenciais seguras.

Atualize o índice/MOC de documentação e mantenha exemplos alinhados às rotas e eventos executáveis.
