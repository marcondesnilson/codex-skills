# Qualidade e validação

Consultar ao alterar código ou revisar um diff. Obrigatório no escopo tocado; ferramentas somente quando existentes.

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

Aplicar o [baseline de segurança](security-baseline.md) nos vetores tocados: entrada externa, autorização na fronteira
confiável, injeção, arquivos/URLs, secrets e criptografia. Essa referência mantém os controles transversais sem duplicá-los
nesta lista de qualidade. A revisão explícita de Security Hotspots abaixo continua obrigatória quando houver gatilho.

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

## Tamanho e coesão de arquivos

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

## Evidência proporcional e Definition of Done

- Detectar comandos em manifests, scripts e CI do projeto afetado antes de executar build/compilação, lint,
  formatter, análise estática e testes. Aplicar formatter ao escopo pertinente, sem reformatar legado não relacionado.
- Escolher unitários, integração, feature, widget/UI, E2E e regressão pelo risco e pelo contrato alterado;
  não exigir todas as categorias. Mudanças críticas exigem evidência proporcional, inclusive caminhos negativos.
- Sem infraestrutura de testes, validar comportamento por inspeção e execução controlada quando possível;
  registrar a lacuna relevante e não instalar uma suíte inteira por formalidade. Falta de evidência crítica impede
  afirmar prontidão para produção.
- Não deixar debug, código morto resultante da tarefa ou TODO crítico sem causa, impacto e condição de resolução.
- Uma tarefa está concluída quando o requisito funciona, respeita a arquitetura, os impactos pertinentes foram
  avaliados, as validações adequadas foram realizadas e a documentação necessária acompanha a entrega.
- Distinguir validação local de validação de produção. Gate exigido ainda pendente deve ser informado como pendente,
  nunca aprovado por inferência. Falha causada pela mudança deve ser corrigida antes de concluir.
- Aplicar o [checklist final](final-checklist.md) selecionando somente os itens pertinentes.
