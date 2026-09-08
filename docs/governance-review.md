# Revisão da governança das skills — 2026-09-08

Registro da evolução de 1.2.0 para 2.0.0; versionamento local não representa release publicada.
A fonte normativa é o [Global](../skills/global-doc-agent/SKILL.md) e suas referências.

## Antes e depois

Antes: quatro SKILL.md, com política transversal extensa no Global e uma referência SSE no Laravel.
Depois: as mesmas quatro skills; Global com ponto de entrada e nove referências condicionais; especialistas com
ajustes de integração; README com instalação completa; VERSION preparado como 2.0.0 sem quebra de linha.

Criados: `skills/global-doc-agent/references/{application-governance,final-checklist,licensing,observability,
privacy-and-legal,quality-gates,release-management,security-baseline,tracking-and-audit}.md` e este relatório.
Alterados: README.md, VERSION e os quatro SKILL.md. A referência SSE permanece sem alteração.

## Preservações e decisões

| Regra/contrato anterior | Destino ou resolução |
| --- | --- |
| Documentação antes de código e confirmação pela estrutura real | Fluxo Global, com README/equivalente se não existir índice |
| Escopo incremental e isolamento por projeto | Princípios Global e especialistas; docs compartilhadas só na raiz |
| Clean as You Code, categorias e Gate real | quality-gates.md; proibição de mascaramento permanece no ponto de entrada |
| Referências de cobertura 80% e duplicação inferior a 3% | Preservadas, subordinadas ao Gate real, sem instalar scanner obrigatório |
| Checklist de 15 perguntas de qualidade | Critérios preservados e agrupados no checklist contextual; detalhes na referência de qualidade |
| Tamanho de arquivos 300/500/800 e exceções | Preservado em qualidade, sem dividir arquivos por métrica isolada |
| UID de visitante/sessão/evento, deduplicação, proxies confiáveis | tracking-and-audit.md; coleta condicionada à finalidade e privacidade |
| Health mínimo, liveness independente, readiness e estados | observability.md; canais operacionais, sem exigir servidor em app local/mobile |
| Light/dark, componentes/tokens, i18n sincronizado | Mantidos no frontend; Tailwind somente quando adotado e HTML somente em web |
| Laravel Form Requests, Policies, Resources, controllers e ecossistema | Mantidos no especialista; defaults respeitam contratos locais |
| SSE /streams, Observer após commit, Redis Streams, sem polling | Preservado integralmente, inclusive referência e testes existentes |
| Commit explícito, diff completo, SemVer por repo, HEAD como base, sem push | Fluxo preservado; integração breve com release/privacidade/licenças |

Conflitos resolvidos:

- Detalhes de readiness/status públicos contrariavam a separação de informação interna: liveness mínimo pode ser
  público; detalhes ficam em canal operacional autorizado. Status humano continua disponível quando necessário.
- Backend-only e página HTML obrigatória de status: a página operacional é exceção mínima e contextual, sem criar
  stack frontend ou área Sobre para API pura.
- Tracking automático e auditoria em todo modelo contrariavam proporcionalidade: avaliação continua obrigatória,
  implementação depende de finalidade/risco; owen-it continua padrão quando auditoria for necessária.
- Primeiro IP público de X-Forwarded-For sem validar a cadeia poderia aceitar dado forjado: usar resolução por proxies
  confiáveis. Exemplo Laravel deixou de registrar mensagem bruta de exceção, que poderia carregar conteúdo sensível.
- Atualizar índice a cada mudança sem impacto criava ruído: manter coerência, editando links/navegação/resumo afetados.
- Hierarquia sugerida não poderia substituir a hierarquia real do ambiente: explicitar prioridade real e usar Global
  para requisitos, especialista para implementação, preservando decisões locais compatíveis.
- Instalação de arquivo isolado omitia referências: distribuição passa a ser pasta completa, sem comandos de chat
  presumidos ou sincronização automática. Essa quebra de distribuição justifica MAJOR, além do controle de diagnósticos.

## Simulação documental dos cenários A–J

Método: seguir os gatilhos do novo ponto de entrada e as instruções dos especialistas para cada pedido abaixo,
verificando decisões obrigatórias e possíveis exigências irrelevantes. É revisão mental/documental, sem executar
aplicações externas, agentes consumidores ou provar comportamento futuro do modelo.

| Cenário/pedido representativo | Roteamento e resultado da simulação | Obrigações irrelevantes evitadas |
| --- | --- | --- |
| A — Laravel com Blade: adicionar relatório | Global + qualidade/segurança/UX/release; Laravel para autorização/consulta; frontend para componentes, estados e renderização | Não trocar arquitetura, temas ou biblioteca; migration só se dados exigirem |
| B — Laravel API: corrigir validação de entrada | Global + qualidade/segurança; Laravel Form Request e teste feature de válido/inválido | Não criar Sobre, frontend, status ou páginas jurídicas por corrigir endpoint |
| C — Flutter + Laravel: exibir versão e reportar erro | Global + governança/privacidade conforme os dados; frontend para UX; especialista Flutter se disponível, senão padrões reais; Laravel só se contrato backend mudar | Não inventar skill Flutter, impor HTML/Tailwind ou criar health endpoint no dispositivo |
| D — Web independente: nova tela Sobre | Global + governança/qualidade; frontend para navegação, metadados, temas, i18n, acesso e renderização | Não chamar Laravel nem divulgar inventário técnico; links legais só quando necessários |
| E — Pequeno bug: corrigir cálculo | Global + qualidade; especialista existente; avaliar regressão observável e impactos documentais | Não instalar analytics, auditoria, scanner ou criar release/modal por edição |
| F — Funcionalidade importante: novo fluxo de aprovação | Global + segurança/qualidade/governança/release; avaliar auditoria, dados e contratos; especialistas implementam; notas e versão no fluxo de release | Não exigir todas as categorias de teste; Novidades continua recomendação |
| G — Nova dependência: biblioteca de exportação | Global + segurança/licenciamento/qualidade; verificar recursos nativos, manutenção, versão, transitivas, licença e distribuição; especialista integra | Não assumir que MIT dispensa notices nem que toda biblioteca exige tela pública |
| H — Novos dados pessoais: cadastro coleta informação adicional | Global + privacidade/segurança/qualidade; mapear finalidade, responsável, retenção e destinatários; adequar controles e política real | Não inventar base legal, responsável, consentimento universal ou garantia de LGPD |
| I — Release com migration: alterar campo usado por app antigo | Global + release/qualidade/segurança/operação; Laravel para migration; avaliar volume, lock, coexistência, recuperação, notas técnicas e consumidores | Não presumir rollback de código suficiente nem executar deploy/commit por referência |
| J — Visual: ajustar espaçamento de botão | Global + governança/qualidade no trecho; frontend para layout, temas e acessibilidade afetada; validar renderização | Não exigir migration, nova dependência, página legal, changelog vazio ou testes que só reproduzem CSS |

Resultado: o roteamento permite cumprir cada cenário mantendo o escopo. Em projetos novos, os requisitos de base são
avaliados; em existentes, sua ausência fora do fluxo não amplia a tarefa. Requisito crítico aplicável sem evidência
permanece pendente e impede afirmar prontidão para produção.

## Fora do Global e evolução futura

Ficam nos especialistas: PHP/Dart/JS, componentes, bibliotecas específicas, autenticação Laravel, comandos de build,
migrations da stack, SSE, instrumentação concreta e procedimento de commits. Global não redige parecer jurídico,
não inventa ferramentas, não instala especialistas e não transforma checklist em automação de deploy.

Próximas skills possíveis, mediante necessidade concreta: flutter-doc-agent, react-doc-agent, vue-doc-agent,
devops-agent, database-agent, security-agent e testing-agent. Não foram criadas nesta revisão.

## Validações executadas

- `quick_validate.py` aprovado para as quatro skills: frontmatter e estrutura básica.
- 26 links Markdown locais resolvidos nos 16 documentos Markdown do repositório.
- Empacotamento com `tar` em diretório temporário: os 14 arquivos das skills presentes, incluindo todas as referências.
- Referência SSE comparada byte a byte com HEAD: intacta. Fluxo original de commit também idêntico ao remover apenas
  a nova seção de integração da comparação.
- VERSION confirmado como cinco bytes `2.0.0`, hexadecimal `322e302e30`, sem newline.
- `git diff --check` sem problemas; revisão documental dos dez cenários descrita acima.
- Sem suíte de aplicação, build ou SonarQube configurados neste repositório; não houve validação de Quality Gate
  nem execução em aplicações consumidoras. Validadores estruturais não provam comportamento futuro do agente.
- Na revisão inicial, nenhum commit, push ou instalação externa foi realizado. Em seguida, o usuário autorizou
  explicitamente `commit-projects`: o diff completo foi revisado para um commit local, mantendo `2.0.0` a partir de
  `HEAD:VERSION` igual a `1.2.0`, sem incremento duplicado. Push e instalação externa não fazem parte dessa autorização.
