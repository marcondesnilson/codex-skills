# Sessões, visitas, ações e auditoria

Consultar ao criar produto ou alterar sessão, tracking, analytics ou operações auditáveis.

Todo projeto novo com interface, API pública, autenticação ou fluxo de usuário deve avaliar a necessidade de registro
de sessões, visitas e ações. Implementar apenas a coleta justificada pela finalidade, pelo produto e pela legislação;
não instalar analytics ou fingerprint por padrão. As regras de captura abaixo se aplicam aos dados necessários definidos pela finalidade.
Em projeto existente, estas regras se aplicam apenas quando a tarefa tocar no fluxo de sessão, visitas, ações, analytics ou em seu contrato direto.

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
- registrar domínio, path, URL, origem, tipo de evento, conteúdo relacionado e timestamp quando aplicável;
  remover query strings, fragmentos e identificadores sensíveis antes de persistir
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

## Auditoria de negócio

Obrigatório quando a operação exigir rastreabilidade: avaliar alteração de permissões, exclusão, mudança de dados
críticos, aprovação, cancelamento e ações administrativas. Não auditar cada operação trivial por formalidade.

- Registrar ator, ação, alvo, data/hora, contexto mínimo e resultado; distinguir pessoa, serviço e ação anônima.
- Separar auditoria de negócio, logs técnicos e analytics: finalidade, acesso e retenção podem ser diferentes.
- Proteger a trilha contra alteração/exclusão indevida e restringir consulta por autorização e tenant quando houver.
- Não duplicar payloads completos ou segredos em valores anteriores/novos. Definir retenção e descarte compatíveis
  com a finalidade, obrigações reais e [privacidade](privacy-and-legal.md).
- Testar a emissão de eventos críticos, falhas e ausência de campos proibidos; usar a implementação da stack.
