# Dependências e licenças de terceiros

Consultar ao adicionar, atualizar ou remover dependências/assets, preparar distribuição ou mudar o modelo de entrega.
Obrigatório quando houver terceiros; a obrigação concreta depende da licença e de como o software é usado/distribuído.

1. Identificar componentes diretos e transitivos pertinentes, bibliotecas incorporadas, fontes, ícones e outros assets.
   Usar manifests, lockfiles e os arquivos de licença do artefato efetivamente entregue; manter inventário interno
   rastreável, aproveitando ferramentas existentes. SBOM é recomendado quando porte/cliente justificar.
2. Confirmar licença, titulares, notices e obrigações nos textos oficiais da versão utilizada. MIT, BSD e Apache são
   permissivas, mas não dispensam preservação de avisos/atribuições e demais condições efetivamente aplicáveis.
3. Avaliar compatibilidade com produto e distribuição: uso interno, SaaS, binário, fonte, redistribuição e acesso por rede
   podem produzir obrigações diferentes. Copyleft/restritivas exigem análise específica; não presumir que todo uso
   obriga abrir o produto, nem que SaaS elimina obrigações.
4. Preservar textos, notices, atribuições, ofertas/entrega de fonte ou outros materiais quando exigidos. Escolher mecanismo
   adequado: pacote distribuído, arquivo de notices, documentação entregue, portal ou área de licenças na UI.
   Não presumir que toda dependência exige tela pública.
5. Verificar que os materiais acompanham a distribuição e são acessíveis ao destinatário exigido. Se necessário,
   validar a geração de notices com o build existente e revisar o resultado, inclusive componentes transitivos.

Interface de licenças deve cumprir obrigações sem despejar inventário interno: não publicar versões detalhadas quando
não exigidas, endpoints, infraestrutura, arquitetura, chaves, tokens, credenciais, nomes internos ou configurações.
Não remover texto obrigatório para esconder detalhes técnicos. Manter inventário completo em canal interno apropriado.

Licença ausente, ambígua ou incompatível precisa ser resolvida antes de incorporar/distribuir o componente afetado:
confirmar com responsável, escolher alternativa compatível ou obter autorização/licença adequada. Não fabricar licença,
parecer jurídico ou garantia de conformidade; registrar a pendência concreta sem paralisar trabalho independente.
