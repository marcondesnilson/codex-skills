# Governança do produto e experiência do usuário

Consultar em produto novo ou mudanças de UI, identificação, Sobre, suporte, mensagens de erro e novidades.
Aplicar ao fluxo tocado; uma correção visual não obriga construir áreas ausentes no restante do produto.

## Identificação e área Sobre

Obrigatório quando houver aplicação distribuída: identificar a versão em execução por fonte confiável de release,
sem valores duplicados que possam divergir. Build é separado da versão; data só quando conhecida e útil.
API, CLI e worker podem informar versão por metadado, comando ou canal operacional adequado, sem criar interface pública.

Em aplicações com UI, prever área compacta equivalente a Sobre/Informações do sistema. Exibir nome e versão;
considerar build, data da versão, fornecedor/desenvolvedor responsável e copyright quando pertinentes.
A área pode agregar links para suporte, privacidade, termos, licenças necessárias e histórico de atualizações,
sem reproduzir tudo numa tela. Não inventar empresa, titularidade, datas ou canais.

## Informação do usuário e informação interna

- Usuário: versão do produto, novidades úteis, documentação de uso, suporte, privacidade, termos e licenças necessárias.
- Interno/técnico: stack, versões de infraestrutura/componentes, banco, IPs, endpoints internos, nomes internos,
  arquitetura, configurações, dependências de segurança, detalhes de vulnerabilidade e diagnósticos.
- Não divulgar o segundo grupo sem necessidade e autorização adequadas. Nem mesmo uma área autenticada de usuário
  comum é automaticamente um canal de diagnóstico administrativo.
- Licenças devem manter atribuições e notices exigidos mesmo quando contenham nomes técnicos; não remover obrigação
  real sob justificativa de sigilo. Consultar [licenciamento](licensing.md).
- B2B/empresarial: informações podem existir na aplicação, portal do cliente, contrato, documentação entregue ou
  central de suporte. Existência e acesso pelo destinatário não significam publicação na Internet.

## Suporte e reportar problema

Obrigatório quando houver atendimento ao usuário/cliente: identificar canal oficial acessível, como e-mail institucional,
formulário, central de ajuda ou portal. Preferir contato institucional; não expor dados pessoais de desenvolvedores.
Se o canal não foi definido, registrar a lacuna sem fabricar endereço funcional.

Recomendado quando útil ao produto: ação Reportar problema. Preparar somente campos permitidos: versão, build,
plataforma, SO, tela/módulo, horário e identificador seguro de erro/correlação. Minimizar detalhamento e validar valores.
Permitir revisar o relatório antes de enviá-lo; anexos e logs precisam de sanitização e envio consciente.
Nunca anexar automaticamente senha, token, cookie, credencial, informação financeira, dado pessoal sensível,
payload confidencial ou segredo. Texto livre e screenshots também podem conter dados privados; não capturá-los
silenciosamente. Definir destinatário, acesso e retenção conforme a política real.

## UX transversal

Obrigatório quando houver UI no escopo; implementar via frontend e especialista de plataforma disponível:

- Tratar loading, vazio, erro, sucesso, sem permissão e sessão expirada nos fluxos que comportam esses estados.
  Tratar offline quando houver dependência de rede/uso offline; não confundir falha de servidor com ausência de rede.
- Erros devem ser claros e acionáveis; detalhes técnicos necessários ficam em logs sanitizados. Não exibir stack trace,
  SQL, senha, token, caminho interno ou infraestrutura. Usar correlação segura quando ajudar o suporte.
- Considerar teclado quando aplicável, foco, labels, semântica, contraste, feedback de erro e tecnologias assistivas.
  Não depender somente de cor. Validar a interação relevante, não apenas a presença de atributos.
- Web: avaliar responsividade em tamanhos representativos do público e conferir a renderização do fluxo afetado.
- Preservar componentes, tokens, convenções, temas e i18n exigidos pelo frontend; não adicionar stack visual por causa
  de uma tela Sobre ou de um checklist.

## Novidades após atualizar

Recomendado para mudanças relevantes: mostrar Novidades da versão com resumo compreensível e link para histórico.
Deve ser fechável, não reaparecer indefinidamente e registrar versão visualizada quando apropriado, respeitando conta,
dispositivo e persistência do produto. Não criar modal por typo, patch trivial ou toda abertura da aplicação.
Separação entre histórico do usuário e técnico está em [releases](release-management.md).
