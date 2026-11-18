---
name: qa-projects
description: Executar Quality Gate de um ou vários projetos, incluindo aplicação real, revisão de UX e Visual QA quando houver interface, testes e regressões, correção segura e resultado baseado em evidências. Use para QA profundo ou $qa-projects com current escolhido a cada execução sem --env e suporte a --env=current ou --env=isolated; não faz commit, release ou deploy.
---

# QA projects

Executar QA depois da implementação e antes de `$commit-projects`. O objetivo é encontrar motivos reais pelos quais o código não deveria ser enviado, corrigir problemas seguros no escopo e aprovar somente com evidências suficientes. Build, lint, testes existentes, resposta HTTP bem-sucedida ou inicialização isoladamente não demonstram correção funcional. QA inclui execução real do produto, validação funcional, visual, UX, acessibilidade e regressão sempre que houver interface e ferramentas disponíveis.

## Invocação e escolha do ambiente

Esta é uma skill global instalada no ambiente Codex, no mesmo formato `skills/<nome>/SKILL.md` de
`commit-projects`. Os argumentos abaixo são instruções da invocação da skill no chat, não um executável de shell.
Aplicar ao workspace atual ou ao escopo explicitamente solicitado, independentemente da stack.
Ler/citar esta skill para editar suas instruções não inicia QA do projeto.

| Invocação | Comportamento |
| --- | --- |
| `$qa-projects` | Perguntar qual ambiente usar nesta execução, antes de qualquer teste com banco/estado. |
| `$qa-projects --env=current` | Usar o desenvolvimento configurado, sem perguntar qual ambiente utilizar. |
| `$qa-projects --env=isolated` | Preparar QA independente e descartável, sem perguntar qual ambiente utilizar. |

Sem `--env`, perguntar **em toda nova execução**, mesmo que uma execução anterior tenha escolhido um modo:

> Qual ambiente deseja usar nesta execução do QA?
> 1. AMBIENTE ATUAL (`current`): desenvolvimento e banco já configurados, preservando os dados existentes.
> 2. AMBIENTE ISOLADO (`isolated`): ambiente próprio e descartável para QA.

Usar a ferramenta de pergunta disponível ou uma pergunta direta quando necessário. Não selecionar por histórico,
memória, preferência inferida, resposta ausente ou timeout. Enquanto aguarda, pode ler documentação, revisar o diff,
montar o plano e executar checks comprovadamente sem acesso a banco/estado de aplicação. Não iniciar containers,
seeds, migrations, workers, testes com persistência ou fluxos autenticados antes da escolha.
Uma resposta vale para a execução em andamento, inclusive retomada após login manual; uma nova invocação sem `--env`
exige nova pergunta. Argumento desconhecido, vazio ou conflitante exige esclarecimento antes dos testes com estado.
Não trocar de modo silenciosamente ao encontrar dificuldade; continuar checks independentes e solicitar mudança de
modo apenas quando necessária. Informar o modo selecionado no progresso e no relatório.

### `current`: desenvolvimento existente

Usar backend, frontend, banco e serviços de desenvolvimento já configurados. A escolha autoriza os testes normais
com persistência; a mera existência de dados não é motivo para bloquear QA nem exigir banco descartável.
Confirmar os destinos efetivos por documentação/configuração sem expor segredos. Não tratar um destino como produção
somente por ser remoto ou usar Docker. Se houver evidência de produção ou destino contraditório/indeterminado,
parar operações com estado nesse destino e pedir esclarecimento; `current` nunca autoriza produção.

- Preferir os fluxos normais: frontend → API → aplicação → banco, API → service/model/repository → banco ou CLI
  oficial. Testar criação, leitura, edição, exclusão, permissões e relacionamentos com registros próprios de QA.
- Identificar os dados criados nesta execução por IDs e/ou marcador único. Editar/excluir preferencialmente esses
  registros. Preservar dados preexistentes; não alterar dados existentes sem necessidade, indiscriminadamente ou
  apenas para fazer assertions passarem. Consultas somente de leitura podem confirmar persistência/integridade.
- Não manipular arbitrariamente o banco via SQL para forçar o cenário ou obter PASS. Se um cenário depender de
  preparação destrutiva, propor executá-lo em isolated; não reescrever o teste para esconder a falta de evidência.
- Proibidos: `DROP DATABASE`, limpeza total, truncate global, `migrate:fresh`, reset destrutivo, apagar tabelas,
  recriar banco, SQL destrutivo arbitrário e remoção indiscriminada de dados preexistentes.
- Inspecionar também setup/teardown, traits, fixtures, scripts e hooks dos testes. `RefreshDatabase`, reset automático,
  flush de Redis/cache e limpeza de filas podem destruir estado mesmo dentro de uma suíte chamada “test”. Só rodar
  se o destino efetivo for comprovadamente descartável e separado do banco/estado de desenvolvimento. Não apontar
  uma suíte destrutiva ao banco current. Uma base de teste separada já configurada pelo projeto pode ser usada pela
  suíte, registrando esse destino; os testes dos fluxos reais continuam no desenvolvimento escolhido.
- Migrations forward no desenvolvimento somente quando necessárias, documentadas e revisadas como não destrutivas.
  Migration destrutiva, rollback ou seed que sobrescreva dados exige ambiente isolado. Não presumir que backup ou
  transação torna seguro um comando destrutivo em current.
- Ao final remover somente os registros próprios de QA quando seguro, preferencialmente pelos mesmos fluxos da
  aplicação. Se a limpeza arriscar relacionamentos/dados preexistentes, preservar e reportar IDs e pendências sem PII.

### `isolated`: ambiente próprio de QA

Criar/preparar recursos independentes, identificados por nome/prefixo de QA e identificador único da execução.
Usar mecanismos naturais da stack: configuração de testes, banco dedicado, schemas quando realmente isolados,
containers/Compose de QA, factories e seeds apropriados. A escolha autoriza preparar e destruir esses recursos
exclusivos; não exigir confirmação adicional para cada preparação reversível já abrangida pelo modo.

Pode criar banco, aplicar migrations, executar seeds/factories, gerar usuários, organizações/tenants, permissões e
outros dados fake, limpar/recriar esse banco e testar rollback. Antes de qualquer destruição, comprovar que o recurso
pertence exclusivamente ao QA; um nome contendo “test” não basta. Preferir dados sintéticos, sem copiar dados reais.

Isolar também Redis, cache, filas, storage, buckets e consumidores. Não conectar workers de QA às filas reais,
montar volumes de dados de desenvolvimento/produção nem permitir que um Agent de QA controle um Docker/Swarm real.
Usar ambientes sandbox/mocks já suportados para integrações externas. Não alterar `.env`, URLs, credenciais, portas
ou defaults normais do projeto quando overrides temporários/process-local forem suficientes.

### Preparação de infraestrutura e Docker

Descobrir serviços e suas dependências nos manifests, Compose, scripts, CI e documentação. Docker, Redis, workers ou
múltiplos serviços não são por si só impedimentos: tentar construir imagens, iniciar os componentes necessários,
aguardar prontidão/health checks e verificar logs e comunicação antes de declarar BLOCKED.

Inventariar serviços, processos, portas, redes e volumes preexistentes antes de iniciar recursos. Em current,
reutilizar serviços de desenvolvimento saudáveis e iniciar somente o necessário conforme o fluxo documentado;
não recriar, parar ou reiniciar serviços preexistentes indiscriminadamente. Em isolated, usar nomes/projeto Compose,
redes, volumes e portas próprios. Um `--project-name` diferente sozinho não isola volumes external, bind mounts,
URLs, container_name fixos ou filas: revisar a configuração efetiva, init containers e comandos de startup.

Confirmar que migrations/seeds automáticos e workers respeitam o modo selecionado antes de executar `up` ou
comandos equivalentes. Nunca executar `down -v`, prune global, flush compartilhado ou limpeza ampla. Se houver falha,
diagnosticar e tentar a correção local segura baseada no projeto; documentar o impedimento concreto se faltar
ferramenta, acesso ou configuração essencial. Não reconfigurar infraestrutura de produção.

### Autenticação e retomada

Para UI/E2E autenticado, procurar primeiro uma credencial explicitamente documentada como desenvolvimento/QA para
testes automatizados. Usá-la somente no destino correspondente. Não vasculhar armazenamento de senhas, sessões de
outros sites ou dados reais para descobrir credenciais; não exibir senha, token ou sessão em relatório/logs.

Em current, sem credencial apropriada documentada:

1. Preparar/iniciar backend/API, frontend e dependências permitidas.
2. Abrir a tela de login quando as ferramentas permitirem.
3. Pausar o fluxo autenticado e solicitar login manual do usuário, sem pedir senha no chat:
   “Ambiente de QA pronto. Estou aguardando você realizar o login manualmente. Avise quando concluir para eu continuar.”
4. Manter os recursos necessários e a aba/sessão disponíveis para retomada; registrar URL e checks pendentes sem
   segredos. Continuar somente verificações independentes que não afetem a sessão.
5. Após a confirmação, verificar que a sessão autenticada está disponível e continuar a partir dela. Não presumir
   que login no navegador forneça um token reutilizável para ferramentas API; respeitar o mecanismo disponível.

Nunca pedir, descobrir, alterar ou resetar a senha do usuário, criar bypass ou desabilitar autenticação. Não criar
uma nova conta em current para contornar a etapa manual na ausência de credencial QA documentada.
Em isolated, preferir criar automaticamente usuário/tenant/organização/permissões fake por seed/factory ou fluxo
normal da aplicação, exclusivamente nesse ambiente; isso não autoriza modificar credenciais de contas existentes.
Se autenticação manual ainda for necessária, seguir a mesma pausa. Sem ferramenta de navegador, informar a URL e
as limitações reais para reaproveitar a sessão, sem prometer acesso automático.

Se extensão/browser/ferramenta bloquear automação, informar o bloqueio e solicitar a intervenção necessária,
preservando a sessão quando seguro. Uma pausa recuperável não encerra o QA: retomar após a confirmação do usuário.
Enquanto aguardando, não emitir PASS nem destruir o ambiente necessário ao login/diagnóstico. Se for necessário
encerrar com a validação incompleta, relatar BLOCKED com o requisito exato pendente.

## Limites e segurança

- Esta skill não executa commit, push, tag, merge, release, deploy, staging ou bump de versão e não invoca `$commit-projects`. A menção à próxima etapa não autoriza executá-la.
- Preservar alterações do usuário, inclusive a separação entre index e worktree. Não usar reset, clean, stash ou restauração destrutiva para facilitar testes.
- Revisar o diff inteiro e seus consumidores; limitar correções automáticas aos problemas causados ou agravados pelas mudanças atuais e à cobertura/documentação correspondente. Reportar problemas preexistentes sem refatorações arbitrárias.
- Em um pedido explícito de QA do produto, corrigir também defeitos objetivos, localizados e seguros nos fluxos de interface efetivamente exercitados, mesmo quando já existiam antes do diff, se a correção estiver dentro da tarefa e não alterar regra de negócio/contrato inesperadamente. Para os demais problemas preexistentes, registrar evidência e severidade sem ampliar o escopo.
- Nunca destruir dados preexistentes arbitrariamente, executar migrations/rollback em produção, derrubar infraestrutura compartilhada ou alterar serviços de produção. Antes de executar scripts, inspecionar efeitos, hooks e destinos; um nome como `test` ou `dev` não comprova isolamento.
- Respeitar o modo escolhido: desenvolvimento configurado e dados preservados em current; recursos exclusivos e descartáveis em isolated. Confirmar destinos efetivos sem imprimir credenciais. Não enviar e-mails, mensagens, pagamentos ou outras ações externas reais como smoke test; usar sandbox/mocks existentes ou reportar bloqueio.
- Não instalar ferramentas globalmente, atualizar dependências arbitrariamente nem criar infraestrutura permanente para obter PASS. Preparação local reversível deve seguir lockfiles, documentação e autorização existente.
- Não remover testes, aplicar skip/ignore, enfraquecer assertions, desativar lint/regras, reduzir cobertura, esconder warnings ou mascarar falhas com configurações/supressões.
- Segredos encontrados devem ser relatados por localização e tipo, nunca pelo valor. Não gravar tokens, dados pessoais ou respostas sensíveis no relatório.

## 1. Entender o escopo antes de testar

Ler os `AGENTS.md` aplicáveis, da raiz até as subpastas afetadas, README, documentação técnica, `documentation/index.md`/MOCs quando presentes e instruções de desenvolvimento/teste. Respeitar skills exigidas pelo projeto. Descoberta somente de leitura é permitida para localizar essas instruções; ler antes de executar scripts/testes ou editar.

Usar o diretório solicitado ou o workspace atual como escopo. Identificar o repositório que o contém e repositórios independentes/submódulos dentro do escopo; não explorar irmãos alheios quando o workspace está dentro de um repositório. Deduplicar caminhos canônicos. Não confundir subpastas comuns com repositórios independentes, nem componentes de um monorepo com repos separados. Descobrir componentes em qualquer profundidade pertinente, sem depender de nomes como `api`, `web` ou `apps`.

Buscar manifests, workspaces, arquivos de configuração e CI reais: por exemplo `package.json`, `composer.json`, `pubspec.yaml`, `go.mod`, `Cargo.toml`, `pyproject.toml`, `requirements.txt`, `pom.xml`, `build.gradle`, `Gemfile`, Dockerfiles, arquivos Compose, Makefile, Taskfile e justfile. A lista não é exaustiva. Evitar buscas recursivas em dependências vendorizadas, caches e saídas geradas, sem ignorar arquivos desses tipos que estejam no diff. Não assumir linguagem ou framework previamente.

Para cada repositório, inventariar:

```sh
git status --short --untracked-files=all
git diff --stat
git diff --name-status --find-renames
git diff
git diff --cached --stat
git diff --cached --name-status --find-renames
git diff --cached
```

Revisar também conteúdo de arquivos não rastreados, adições, remoções, renomeações, binários e mudanças em gitlinks. Abrir diff dos repositórios filhos quando aplicável; um ponteiro de submódulo não substitui a revisão do conteúdo. Considerar o estado final contra HEAD sem perder diferenças entre staged e unstaged. Em repositório sem HEAD, tratar arquivos presentes como estado inicial sem inventar base histórica. Conflitos não resolvidos bloqueiam o componente afetado.

Sem diff, executar QA do estado atual solicitado e registrar que não há alterações locais para avaliar. Componentes fora de Git podem ser testados, mas a ausência de baseline deve ser explícita.

## 2. Descobrir comandos e arquitetura

Para cada aplicação/componente registrar linguagem, framework, versões, package manager/lockfile, comandos de desenvolvimento, build, teste, lint, formatter check, typecheck, análise estática, integração/E2E e infraestrutura necessária.

Obter comandos de scripts/configurações reais, Makefile/Taskfile/justfile, CI e documentação. A configuração do projeto tem prioridade. Não adivinhar comandos por reconhecer uma extensão. Se não houver wrapper, somente usar comando nativo após confirmar sua interface na ferramenta/documentação e a configuração aplicável; declarar a origem. Não alegar execução de ferramenta ausente.

Confirmar versões, variáveis obrigatórias, serviços, portas, fixtures e configuração de testes. Não imprimir `.env` completo. Verificar hooks de instalação/build/teste e se os comandos disparam deploy, publicação ou conexões externas. Usar containers de desenvolvimento/teste quando forem o ambiente estabelecido.

## 3. Revisar mudanças e construir plano de impacto

Revisar integralmente o diff e os arquivos novos. Para cada mudança identificar comportamento anterior/final, motivo confirmado (não inventar intenção), funcionalidades, consumidores, dependências, contratos/API, banco, autenticação/autorização, UI, integrações, efeitos colaterais e riscos de regressão. Inspecionar código relacionado além dos arquivos alterados.

Antes dos testes criar internamente uma matriz com:

- componente/funcionalidade e risco;
- hipótese de falha e comportamento esperado;
- comando ou procedimento, sua origem e ambiente seguro;
- categoria, evidência esperada e resultado observado;
- motivo para não aplicabilidade ou bloqueio.

Categorias: `STATIC`, `UNIT`, `FEATURE`, `INTEGRATION`, `DATABASE`, `API`, `UI`, `UX`, `VISUAL`, `ACCESSIBILITY`, `FORMS`, `LOADING`, `ERROR`, `EMPTY`, `E2E`, `SECURITY`, `BUILD`, `RUNTIME`, `SMOKE`, `REGRESSION`.

Executar todas as categorias aplicáveis. Ausência de ferramenta não torna uma categoria não aplicável: procurar uma verificação equivalente segura e registrar limitações. Categoria aplicável sem evidência obrigatória fica BLOCKED, nunca silenciosamente PASS. Definir obrigatoriedade pelo impacto antes da execução; não rebaixar um check porque falhou ou ficou indisponível.

## 4. Static QA e testes automatizados

Executar todos os checks disponíveis pertinentes aos componentes: lint, formatter em modo check, typecheck, análise estática, compilação, imports, dependências, configurações e código morto quando houver ferramenta. Analisar warnings individualmente por impacto; não basta registrar seu número. Consultar o Quality Gate configurado quando aplicável, sem inventar SonarQube ou alegar aprovação de scan não executado.

Executar testes unitários, feature, integração, API, widgets/componentes, E2E e regressão existentes e relevantes. Quando viável, começar pelos direcionados, depois os do módulo e então executar a suíte completa dos componentes afetados e consumidores pertinentes. Não limitar a testes dos arquivos do diff. Se a suíte mais ampla não puder rodar, registrar exatamente a parcela omitida, motivo e efeito sobre o gate.

Para cada funcionalidade alterada, criar ou executar pelo menos uma verificação comportamental com resultado esperado explícito. Cobrir happy path, edge case e error path quando aplicáveis. Uma API exige verificar conteúdo/semântica, payload válido/inválido e limite, ausência de autenticação, falta de permissão e recurso inexistente, não apenas HTTP 200. Fluxos críticos exigem comprovação de efeitos/persistência, não apenas ausência de exceção.

Quando houver CRUD alterado, testar CREATE, READ, UPDATE e DELETE aplicáveis, confirmando persistência e resposta na
API/interface pelo modo escolhido. Com tenants, organizações, empresas, roles, grupos ou permissões, testar
explicitamente acesso permitido e negado, inclusive tentativa de ler/editar/excluir recurso de outro tenant. Usar
identidades e dados de QA apropriados; falta de segunda identidade necessária é lacuna explícita, não prova de isolamento.

Criar cobertura apropriada para mudanças importantes descobertas sem testes, seguindo a arquitetura existente. Bugs corrigidos devem ter teste de regressão que falharia antes da correção sempre que viável. Preferir reprodução isolada para demonstrar o antes/depois, preservando worktree/index. Não criar testes que apenas repitam a implementação. Checks manuais podem complementar ou substituir automação quando justificável, mas devem ter passos e observações verificáveis.

## 5. Banco de dados

Quando houver banco/migrations, revisar sintaxe, migração de dados, constraints, índices, foreign keys, nullability, defaults, compatibilidade com código antigo/novo, operações destrutivas, perda de dados, concorrência, N+1 e queries evidentemente problemáticas.

Em current, preservar dados e seguir as restrições de migrations, fixtures e setup/teardown do modo; não executar
reset/rollback/limpeza destrutiva no banco de desenvolvimento. Em isolated, aplicar migrations em banco descartável
compatível com o projeto e usar seeds/factories sintéticos. Verificar instalação nova e atualização do estado anterior
quando o impacto exigir. Testar rollback quando seguro e suportado; ausência deliberada de reversão deve ser avaliada
conforme o contrato da migração. Validar tipos, relacionamentos, persistência e integridade após as operações.
Se uma verificação obrigatória exigir testes destrutivos fora do modo escolhido, solicitar isolated e registrar a
pendência; não executar destruição em current nem tratar falta de evidência como PASS.

## 6. Runtime, smoke e UI

Preparar e iniciar automaticamente os componentes realmente necessários segundo os manifests e as instruções do projeto: containers, API, frontend, banco, Redis, filas/workers, WebSocket/SSE e serviços auxiliares conforme a arquitetura. Iniciar infraestrutura é parte do QA, não motivo isolado para omitir testes. Primeiro identificar e preservar processos, containers, redes, dados e portas que já existiam, conforme `current`/`isolated` e as regras de segurança. Não afetar produção nem executar operações externas reais. Aguardar readiness/health checks com limite razoável, inspecionar logs de startup e verificar a comunicação entre componentes; se não ficar pronto, diagnosticar e tentar uma resolução local segura antes de registrar o bloqueio. Registrar o que foi iniciado e encerrar somente processos/recursos temporários próprios da sessão.

Confirmar prontidão, ausência de crash, logs/exceptions/warnings, respostas HTTP, conexão com serviços e comunicação frontend/backend. Não confundir processo iniciado com aplicação pronta. Para CLI/worker/mobile/biblioteca, executar o binário, serviço ou consumidor real/harness pertinente à arquitetura; um container saudável ou build sem uso funcional não encerra esse QA.

Executar smoke de inicialização, health checks existentes, endpoints críticos, autenticação quando aplicável, funcionalidades modificadas e fluxos relacionados. Testar o comportamento afetado; uma requisição a `/` não é suficiente. Não inventar endpoint `/health` inexistente. A ausência de credenciais/serviço necessário é uma limitação explícita.

### UX QA e uso real

Se houver interface web, app mobile, desktop ou outra UI e ferramentas disponíveis, execute a aplicação e use-a como uma pessoa usuária. Faça navegação real pelos menus e fluxos entre telas; abra listagens/detalhes; use busca, filtros, ordenação e paginação existentes; abra/feche modais; use ações principais e atualize a tela. Adapte testes de criar, ler, editar e excluir aos recursos afetados e existentes, usando apenas dados próprios de QA e as regras de `current`/`isolated`. Não altere ou remova registros preexistentes sem necessidade autorizada. Verifique cancelamento/retorno e confirmação de ações, feedback, persistência, estados de sessão e transições.

Avalie a experiência de uso diário: é claro o que fazer, as ações importantes são fáceis de descobrir, as etapas são previsíveis e proporcionais, a organização e hierarquia ajudam a tarefa, e a interface explica o resultado? Observe formulários, navegação, menus, tabelas, busca, filtros, paginação, confirmações, mensagens e densidade da informação. Pergunte-se: “Um usuário entende o próximo passo?”, “É fácil achar a ação principal?”, “A tarefa é confortável e previsível?” e “A tela confirma o que aconteceu?”. Não converta gosto pessoal em defeito: classifique preferência subjetiva como `SUGGESTION`.

Não aprove a UI só por abrir, ter DOM, não exibir erro JavaScript, retornar HTTP 200 ou passar testes de componente. Demonstre que tarefas relevantes são concluídas no fluxo da aplicação e que as respostas/efeitos aparecem corretamente ao usuário. UI/E2E devem navegar pela aplicação real, frontend e backend integrados sempre que aplicável; requests isolados e testes automatizados complementam essa evidência.

### VISUAL QA

Inspecione a tela renderizada por screenshot ou visualização direta quando disponível, além de ler DOM/código. Revise alinhamento, espaçamento, margens/padding, corte e legibilidade de texto, overflow, sobreposição, quebras, botões, ícones, dimensões de cards/tabelas/formulários/modais, hierarquia, densidade, contraste e feedback visual. Compare telas/components que realizam a mesma função para detectar inconsistências.

Antes de corrigir visual, descubra design system e documentação: componentes compartilhados, tokens, cores, tipografia, spacing, radius, sombras, componentes de formulário/tabela/modal e guidelines. Reuse padrões existentes; não crie sistema visual paralelo. Defeitos objetivos e locais podem ser corrigidos; redesenho, mudança de identidade, arquitetura ou fluxo de negócio são propostas, não correções automáticas.

### Responsividade, estados e formulários

Quando aplicável, verifique ao menos `MOBILE`, `TABLET` e `DESKTOP`, incluindo desktop largo se viável. Confirme o viewport efetivo. Avalie conforto de uso, menu/sidebar, rolagem de tabelas, alcance das ações, toque, tamanho de fontes e campos, espaço vazio e densidade, além de overflow, conteúdo cortado, botões fora da tela, cards esmagados e modais que excedem o viewport. Existir encaixe geométrico não prova usabilidade responsiva.

Para dados assíncronos, observe loading/skeleton, primeira carga, refresh e atualização, resultado, retry, erro e empty state. Procure layout shift, piscar, spinner infinito, conteúdo perdido, duplo submit e botão sem feedback. Em formulários relevantes, teste obrigatórios vazios, dados válidos/inválidos, limites/tamanho extremo, caracteres especiais, validação, cancelar/salvar, repetição/duplo clique, submit enquanto carrega e erro de API quando for reproduzível com segurança. Confirme que a mensagem indica uma ação compreensível e que valores digitados não se perdem indevidamente.

### Console, rede e logs durante a interação

Durante o uso visual, monitorar console JavaScript, exceções, warnings relevantes e requests/status HTTP; procurar loops, duplicação e chamadas desnecessárias. Em paralelo, revisar logs pertinentes de API/backend, workers e containers. Investigar se uma tela aparentemente bem-sucedida esconde erro. Distinguir erro do produto de ruído comprovadamente originado em extensão/ferramenta; se a origem for incerta, relatar literalmente a incerteza, sem declarar o console limpo ou culpar uma extensão por inferência.

### Acessibilidade

Verificação proporcional nas telas tocadas: navegação por teclado e ordem de foco, foco visível/restauração, semântica e nomes acessíveis, labels dos campos, reconhecimento de ações, feedback e associação de erros, contraste e tamanho de alvos interativos. Use scanners/ferramentas de acessibilidade existentes. Não altere radicalmente o visual por preferência; corrija violações objetivas e locais sem introduzir regressões e valide outra vez.

Para interface nativa, use emulador/dispositivo e controle de UI disponível; para Web, navegador real e viewport efetivo. Executar E2E configurado. Screenshots servem como evidência das telas/estados relevantes, não para registrar por registrar; evite dados pessoais/segredos nas evidências e no relatório. Se uma ferramenta necessária não estiver disponível, tente equivalentes existentes e registre o que impediu validação, sem converter ausência de ferramenta em N/A quando a UI for aplicável.

## 7. Segurança e dependências

Fazer revisão proporcional do código alterado e dos fluxos relacionados: autenticação, autorização por recurso/tenant (IDOR), SQL injection, XSS, CSRF, mass assignment, validação, exposição de dados, permissões, endpoints administrativos e logs sensíveis. Verificar arquivos staged, unstaged e novos que poderão ir ao Git, incluindo `.env`, tokens, senhas, dumps e artefatos. Um scanner sem achados não substitui revisão dos contratos de autorização.

Se dependências mudaram, comparar manifest e lockfile, versões, compatibilidade, necessidade, origem e vulnerabilidades usando ferramentas disponíveis do ecossistema. Audits com rede devem respeitar a confidencialidade do projeto. Separar vulnerabilidade confirmada de indisponibilidade do scanner. Não rodar fixes/upgrades automáticos arbitrários. Lockfile inesperadamente modificado durante preparação deve ser revisado e reportado, sem sobrescrever alterações do usuário.

## 8. Regressão, correções e build final

Perguntar para cada mudança: “O que poderia ter parado de funcionar por causa desta alteração?”. Formular e testar hipóteses sobre consumidores, contratos e funcionalidades existentes relacionadas, incluindo integração entre telas, clientes, API e serviços reais. No produto, pergunte também se o usuário consegue concluir a tarefa e entender o estado, os erros e as consequências da ação.

Repetir: ANALISAR → EXECUTAR → TESTAR → ENCONTRAR PROBLEMA → CORRIGIR → RETESTAR → REGRESSÃO → CONTINUAR.

Corrigir automaticamente quando houver defeito objetivo e a mudança for localizada, reversível, compatível com contratos/design system e dentro do escopo autorizado; isso inclui corrigir defeito visível em fluxo exercitado na tarefa de QA mesmo que preexistente, conforme a regra em Limites e segurança. Classificar bugs como `CRITICAL`, `HIGH`, `MEDIUM` ou `LOW`; melhoria subjetiva sem comportamento objetivamente errado é `SUGGESTION` e deve ser relatada, sem redesenho decidido pelo agente. Não alterar regra de negócio, contrato, identidade, arquitetura, funcionalidade ou layout amplamente sem evidência clara e autorização da tarefa. Quando houver dúvida material sobre comportamento esperado, documentar impacto e perguntar, enquanto prossegue checks independentes. Atualizar documentação exigida pelo projeto para refletir a correção. Depois executar novamente o teste que falhou, o fluxo ponta a ponta, os testes relacionados e regressões; reabrir a interface alterada e validar a renderização sempre que houver ferramenta. Repetir checks estáticos aplicáveis e verificar regressão. Reavaliar impacto e repetir checks invalidados por mudanças posteriores; resultados de código anterior não aprovam o estado final. Não repetir checks já válidos sem motivo novo.

Referência de severidade: `CRITICAL` = risco grave de segurança, perda de dados ou produto inutilizável; `HIGH` = funcionalidade principal quebrada ou regressão importante; `MEDIUM` = problema funcional/UX relevante com alternativa; `LOW` = incômodo pequeno que não impede o uso; `SUGGESTION` = melhoria subjetiva de experiência/consistência sem defeito objetivo. A severidade descreve impacto observado, não preferência estética.

Executar os builds finais aplicáveis de produção usando os comandos/configurações descobertos, sem deploy/publicação. Falha de build é FAIL. Não substituir build de produção por dev server. Se build obrigatório não pode sequer ser executado por ambiente/credencial/ferramenta ausente, é BLOCKED. Configurar placeholders somente quando isso for suportado e não invalidar a verificação.

Parar quando todos os checks aplicáveis estiverem concluídos sem problemas relevantes ou houver impedimento sem solução segura. Não repetir indefinidamente tentativas idênticas. Continuar verificações independentes mesmo se um componente estiver bloqueado; relatar resultados por componente e agregado, incluindo contratos entre projetos.

## 9. Evidências e decisão

Manter registro conciso de comandos/procedimentos, diretório/componente, ambiente, resultado/código de saída, quantidade de testes quando disponível, observações e limitações. Cancelamento/timeout não é sucesso. Reportar testes skipped, suites não executadas e cobertura insuficiente. Distinguir falha preexistente comprovada, regressão atual e falha ambiental; não presumir que é preexistente sem evidência.

Antes do relatório, reinventariar status e ambos os diffs, revisar mudanças feitas pelo QA e artefatos gerados. Não adicionar caches/logs ao Git nem remover arquivos preexistentes. Aplicar a limpeza conforme o modo: remover dados fake próprios quando seguro (em current, preferir fluxos normais),
encerrar processos temporários iniciados exclusivamente pelo QA e remover recursos descartáveis exclusivos de isolated
quando não necessários ao diagnóstico. Preservar dados e serviços preexistentes e evidências/logs úteis sanitizados.
Não encerrar recursos necessários durante espera de login ou intervenção do usuário. Registrar o que foi criado,
removido e mantido, com motivo e pendências de limpeza; nunca remover recursos cuja propriedade seja incerta. Confirmar que as evidências correspondem ao estado final; mudança concorrente relevante exige reavaliação.

Resultados por componente e agregado:

- **PASS**: todos os checks aplicáveis e obrigatórios executados e aprovados, evidências comportamentais/regressão suficientes, nenhum problema relevante pendente.
- **PASS WITH WARNINGS**: mesmos requisitos de validação, com ressalvas comprovadamente não bloqueantes; explicar evidência, impacto e por que não bloqueiam. Não usar para teste obrigatório ausente, vulnerabilidade relevante, build falho ou regressão pendente.
- **FAIL**: defeito relevante confirmado, teste/check obrigatório falhou ou qualquer build aplicável falhou. Falha preexistente não vira warning automaticamente.
- **BLOCKED**: evidência obrigatória não pôde ser obtida por ambiente, credencial, ferramenta, decisão, conflito ou ambiente seguro indisponível, sem falha confirmada que já determine FAIL.

Agregado: FAIL prevalece, seguido de BLOCKED, PASS WITH WARNINGS e PASS. Mesmo com FAIL, listar também bloqueios. Não converter problema relevante em warning para obter aprovação. Aprovação vale para o estado revisado, sem garantir ausência absoluta de bugs.

## Integração com frontend design QA

Esta seção só se aplica quando uma invocação de `$qa-projects` realmente abrange mudança de apresentação ou interação.
Ler, copiar ou editar esta skill e seus agents não inicia QA de um produto.

- Preserve a decisão `current`/`isolated` desta skill. Sem `--env`, pergunte pelo ambiente em cada nova execução antes
  de qualquer teste com estado. A escolha do ambiente não autoriza uma chamada paga à API.
- `frontend-impact` e `api-execution-authorized` são decisões independentes. Se uma mudança afeta apresentação ou
  interação, inclua revisão visual externa como requisito obrigatório do aceite. Se o serviço, autorização ou evidência
  não estiver disponível, registre `BLOCKED`; uma falha confirmada continua sendo `FAIL` e prevalece no agregado.
- Para tarefa somente backend sem impacto visual, não exija configuração visual nem bloqueie os testes funcionais por
  falta de API.
- Use a responsabilidade especializada: `global-doc-agent` governa segurança, privacidade, qualidade e evidências
  transversais; `frontend-doc-agent` implementa componentes, estados, contratos e testes; `frontend-visual-quality`
  orienta direção, captura e observação consultiva; esta skill executa QA real, valida regressões, classifica resultados
  e decide o aceite a partir das evidências.
- Na revisão visual, declare antes as telas, regiões, estados e plataformas cobertos e vincule cada critério às capturas
  requeridas. Registre build servido, origem/configuração/direção/assets por fingerprint, ambiente, dispositivo/janela,
  viewport e escala. Não use `HEAD` sozinho como identidade do build.
- Uma resposta do modelo não aprova o projeto. Compare o conteúdo da direção adotada, os findings completos e a revisão
  com a aplicação real; registre a avaliação do Codex como evidência para a mesma versão/build revisada. Um resultado
  ausente, screenshot incompleto ou stale não pode virar warning para obter PASS.
- Preserve a classificação de sugestões subjetivas versus defeitos confirmados, o limite de correção dentro do escopo,
  a proteção contra regressões, a minimização de dados e os controles `current`/`isolated` das seções anteriores.

O contrato de execução e o agregador de evidências estão documentados na skill distribuível
[`frontend-visual-quality`](../frontend-visual-quality/SKILL.md), especialmente em
[`references/acceptance-gate.md`](../frontend-visual-quality/references/acceptance-gate.md). O helper opcional não inicia
browser, produto, banco ou QA por conta própria.

## 10. Relatório final

Responder no idioma do usuário, de forma curta e objetiva, usando este formato ampliado. Cada check aplicável deve informar `PASS`, `PASS WITH WARNINGS`, `FAIL` ou `BLOCKED` e evidência resumida. Usar `N/A — motivo` somente quando a categoria for realmente inaplicável, não para falta de ferramenta/evidência. Separar componentes quando resultados diferirem. Não apresentar plano como execução. Para cada problema, fornecer severidade, evidência, correção e reteste. Listar sugestões subjetivas separadas dos bugs.

```text
QA PROJECTS
======================================

Environment: CURRENT | ISOLATED
Projetos detectados:
Alterações analisadas:

INFRASTRUCTURE
Environment:
Docker/Services:
Runtime:

CODE QUALITY
Static Analysis:
Lint:
Formatting:
Typecheck:

TESTS
Unit:
Feature:
Integration:
API:
Database:
E2E:
Regression:

APPLICATION
Smoke:
Authentication:
CRUD:
Permissions:
Multitenancy:

USER EXPERIENCE
Visual QA:
UX QA:
Responsive:
Accessibility:
Forms:
Loading States:
Error States:
Empty States:

PRODUCTION READINESS
Security:
Production Build:

======================================
Problemas encontrados:
[SEVERITY] descrição
Evidência:
Correção:
Reteste:

Problemas corrigidos:
Problemas não corrigidos:
Sugestões de UX:
Testes executados:
Testes adicionados:
Pendências:
Warnings:
Limpeza e recursos mantidos:

RESULTADO FINAL:
PASS | PASS WITH WARNINGS | FAIL | BLOCKED
```

Preservar a distinção `current`/`isolated`: imprimir `CURRENT` para modo `current`, `ISOLATED` para modo `isolated`, sem assumir modo quando ainda não escolhido. Escolher um único resultado agregado usando as regras da seção 9. Para `FAIL`/`BLOCKED`, explicar o impedimento e a evidência pendente. `PASS WITH WARNINGS` só cabe quando todos os checks obrigatórios passaram e cada ressalva foi demonstrada não bloqueante. Para `PASS`, finalizar com: “QA aprovado. Projeto apto para $commit-projects.” Para os demais resultados, não dizer que está apto a commitar. Nunca executar o commit como continuação automática.
