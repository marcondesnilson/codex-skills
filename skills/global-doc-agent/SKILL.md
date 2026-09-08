---
name: global-doc-agent
description: Coordenar governança transversal, documentação, segurança e qualidade incremental em projetos e monorepos. Use quando citada no AGENTS.md ou ao implementar ou revisar mudanças que exijam consistência entre código, contratos, operação e documentação; consulte especialistas para implementação por stack.
---

# Global: governança transversal

Definir **o que** o projeto precisa considerar ou possuir. Skills especializadas definem **como** implementar na
tecnologia existente. Esta skill coordena leitura, decisões e validação; não é um runtime de agentes nem executa
outras skills automaticamente. Instalar a pasta completa, incluindo `references/`.

## Princípios obrigatórios

- Quando citada no `AGENTS.md` aplicável, cumprir esta skill em toda tarefa desse escopo.
- Antes de editar, consultar documentação e confirmar o contrato no código, configuração e comportamento disponíveis.
- Em projeto existente, atuar somente no fluxo tocado e dependências/contratos diretamente necessários. Não auditar,
  refatorar, modernizar ou corrigir legado não relacionado. Dívida incidental fica intacta, salvo impedimento real.
- Em projeto novo, aplicar os requisitos pertinentes desde a base dentro do pedido. Padronização não autoriza reescrita.
- Antes de adicionar pacote, arquitetura ou padrão, verificar stack, recursos nativos e convenções existentes;
  preferir consistência e exigir benefício concreto. Refatoração ampla exige justificativa e escopo autorizado.
- Nunca expor segredos em código, logs, documentação ou cliente. Separar informação de usuário de diagnóstico interno.
- Código criado/alterado segue Clean as You Code: sem introduzir ou agravar bugs, vulnerabilidades, smells, complexidade
  ou duplicação evitáveis. Respeitar Quality Profile/Gate reais; nunca mascarar achados com `NOSONAR`, supressões,
  exclusões artificiais ou redução de exigências. Não afirmar aprovação de validação não executada.
- Cumprir obrigações reais de privacidade e licenciamento; não inventar conformidade jurídica nem exigir divulgação pública
  de informação que pode ser entregue por canal restrito. Não coletar dados só para preencher um padrão.
- Validar o resultado proporcionalmente ao risco e atualizar documentação afetada. Não concluir com falha conhecida
  introduzida pela tarefa ou requisito essencial não atendido.

## Classes de regra e hierarquia

- **Obrigatório sempre:** princípios acima, determinar escopo, avaliar impactos e relatar evidências/limitações reais.
- **Obrigatório quando aplicável:** cumprir quando o gatilho existir no fluxo afetado. Uma vez aplicável, não é opcional.
- **Recomendado:** adotar quando houver benefício para o produto; não bloqueia sozinho a entrega.

Classificar por evidência. Não produzir uma matriz extensa para toda tarefa; justificar não aplicabilidade apenas quando
não for óbvia ou quando dispensar um requisito esperado. Lacunas de produto fora do pedido não autorizam implantá-las.

A hierarquia real de instruções do ambiente prevalece: esta skill não eleva arquivos locais acima de instruções de
sistema/desenvolvedor ou do pedido explícito. Dentro das regras do projeto:

1. Respeitar requisitos explícitos, `AGENTS.md` aplicável e restrições de segurança, integridade e privacidade.
2. Preservar contratos, arquitetura e convenções locais documentadas e confirmadas no fluxo real.
3. Aplicar requisitos globais; especializações detalham a implementação e não dispensam o requisito transversal.
4. Usar padrões da stack onde não houver decisão local; recomendações opcionais ficam por último.

Não usar costume inseguro como justificativa de compatibilidade. Diante de conflito, seguir a instrução de maior
prioridade, informar o impacto e resolver no menor escopo. Pedir decisão somente se faltar informação/autoridade
indispensável; continuar o trabalho independente. Documentação divergente deve ser corrigida com base em evidência.

## Fluxo obrigatório

1. Ler `documentation/index.md` da raiz do workspace, se existir; identificar apenas os projetos afetados;
   ler `<projeto>/documentation/index.md` e notas relevantes, se existirem. Usar README ou equivalente na ausência.
2. Confirmar stack por manifests e estrutura: `artisan` + `composer.json`/dependências para Laravel,
   `pubspec.yaml`/SDK Flutter para Flutter, `package.json`/dependências e fontes para Node, React ou Vue.
   Não inferir pelo nome da pasta nem pela presença isolada de um arquivo.
3. Delimitar comportamento solicitado, contratos diretos, risco e impactos em UI, dados, dependências e operação.
   Consultar as referências acionadas abaixo antes de implementar; em correção pequena, carregar só as pertinentes.
4. Ler as skills especializadas disponíveis e aplicar a implementação ao padrão existente. Não reiniciar este fluxo
   por referências recíprocas: ler cada instrução uma vez e combinar responsabilidades.
5. Implementar incrementalmente; validar apenas projetos afetados com ferramentas existentes; corrigir falhas da mudança.
6. Atualizar docs quando mudar comportamento, configuração, arquitetura, API, deploy, requisitos, operação ou processo.
   Manter índice/MOC coerente; editá-lo quando navegação, links ou resumo forem afetados, sem alterações cosméticas.
7. Aplicar [checklist final](references/final-checklist.md), comunicar resultado, evidências e pendências pertinentes.
   Avaliar versão/release quando houver gatilho; não fazer commit, push, instalação externa ou deploy por inferência.

Em múltiplos projetos, tratar implementação, validação e versão independentemente. Documentação específica fica no projeto;
raiz guarda governança e contratos realmente compartilhados. Não inspecionar projetos irmãos sem relação com a mudança.

## Referências: consultar pelo gatilho

Os detalhes são obrigatórios nos respectivos escopos; não carregar todas as referências em toda tarefa.

| Gatilho no escopo | Referência e decisão |
| --- | --- |
| Código criado/alterado ou revisão de diff | [Qualidade](references/quality-gates.md): categorias Sonar, testes e evidência |
| Entrada externa, auth, dados, configuração, dependência ou fronteira de confiança | [Segurança](references/security-baseline.md): controles pertinentes |
| Produto novo, UI, Sobre, versão exibida, suporte, erro ou novidades | [Governança do produto](references/application-governance.md): informação e experiência do usuário |
| Dependência/asset novo, atualizado, removido ou distribuição alterada | [Licenciamento](references/licensing.md): inventário e obrigações reais |
| Dados pessoais, tracking, fornecedor de dados ou contexto contratual alterado; produto novo | [Privacidade e termos](references/privacy-and-legal.md): necessidade e conteúdo factual |
| Sessão, visitas, analytics ou operação auditável; produto novo | [Tracking e auditoria](references/tracking-and-audit.md): avaliar necessidade e coletar minimamente |
| Logs, erros operacionais, monitoramento, infraestrutura/deploy; serviço novo | [Observabilidade](references/observability.md): sinais, health e acesso |
| Release solicitada, funcionalidade relevante, contrato, migration ou compatibilidade alterada | [Releases](references/release-management.md): SemVer, changelogs e implantação |
| Conclusão de qualquer tarefa | [Checklist final](references/final-checklist.md): selecionar itens e verificar Definition of Done |

## Integração com especialistas

- `frontend-doc-agent`: consultar ao tocar interface, inclusive Blade e mobile conforme o escopo dessa skill.
  Global exige UX, acessibilidade, estados, responsividade web e informação segura; frontend define componentes,
  tokens, temas, i18n e validação visual, preservando padrões existentes.
- `laravel-doc-agent`: consultar em código, configuração, testes e arquitetura Laravel; a especialização mantém
  Form Requests, Policies, Resources, controllers, auditoria, health e SSE. API pura não exige tela Sobre ou frontend.
- `commit-projects`: consultar suas regras de versão/revisão quando pertinente, mas executar o fluxo de commits somente
  por pedido explícito. Ler ou citar a skill não concede autorização; push exige pedido separado.
- Outras stacks: consultar skill pertinente somente se disponível. Flutter, React, Vue, DevOps, banco, segurança e testes
  podem ganhar especialistas futuros; não presumir que já existem nem criar automaticamente.
- Sem especialista disponível, usar documentação e mecanismos reais do projeto, mantendo os requisitos globais;
  informar uma falta apenas se limitar a implementação. Não simular chamada de ferramenta ou delegação inexistente.

Consultar outra skill significa ler e aplicar suas instruções pelos recursos disponíveis no ambiente. Isso não implica
criar subagentes. Referências internas são relativas à pasta da skill; especialistas são resolvidos pelo catálogo instalado.
