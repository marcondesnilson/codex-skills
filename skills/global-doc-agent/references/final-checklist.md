# Checklist final e Definition of Done contextual

Consultar antes de concluir. Selecionar os itens pelo escopo e risco; não anexar uma lista inteira de N/A à resposta.
Conferir o requisito solicitado e corrigir problemas introduzidos antes da entrega. Um item aplicável pendente não é
aprovado: informar evidência, limitação e impacto. Pendência essencial impede declarar conclusão/prontidão para produção.

## Arquitetura — sempre no escopo

- [ ] O resultado atende efetivamente ao pedido e respeita contratos, arquitetura e convenções existentes.
- [ ] Não houve abstração/dependência desnecessária nem modernização de legado fora do pedido.
- [ ] Código tocado ficou pelo menos tão sustentável quanto estava; complexidade e duplicação foram revisadas.

## Segurança — controles conforme fronteiras tocadas

- [ ] Sem segredos em código, exemplos, cliente, erros ou logs; dados sensíveis minimizados.
- [ ] Entrada externa validada e autorização/autenticação revisadas onde necessárias, inclusive tenant/recurso.
- [ ] Hotspots pertinentes revisados por contexto; não há vulnerabilidade provável nem exceção silenciosa.
- [ ] Configuração de ambiente e exposição de diagnósticos preservam fronteiras de confiança.

## Qualidade — ferramentas e comportamento pertinentes

- [ ] Caminhos de sucesso, falha, ausência de dados e limites relevantes foram avaliados; sem bug provável conhecido.
- [ ] Testes pertinentes executados; necessidade de regressão avaliada para bugs e cobertura proporcional ao risco.
- [ ] Compilação/build, formatter, lint, tipagem e análise estática existentes executados quando pertinentes.
- [ ] Quality Profile/Gate reais respeitados; sem mascarar achados. Execução pendente/inviável informada.
- [ ] Sem debug, código morto, imports/variáveis sem uso resultantes da mudança ou TODO crítico sem registro.

## UX — somente quando houver interface afetada

- [ ] Loading, vazio, erro, sucesso, sem permissão, sessão expirada e offline tratados conforme o fluxo.
- [ ] Mensagens acionáveis, acessibilidade e responsividade pertinentes verificadas; visual validado no escopo.
- [ ] Padrões de componentes, temas e i18n preservados; informação de usuário separada de diagnóstico interno.

## Governança — conforme impacto da mudança

- [ ] Documentação afetada atualizada por mudança real; índices/links coerentes.
- [ ] Versão, build, changelog e release atualizados no momento exigido pelo fluxo.
- [ ] Identificação, Sobre e suporte tratados quando fizerem parte do produto/fluxo solicitado.
- [ ] Licenciamento revisado se dependências/assets/distribuição mudaram; notices obrigatórios preservados.
- [ ] Privacidade/termos reavaliados se tratamento de dados ou contexto contratual mudou.
- [ ] Auditoria, tracking e observabilidade pertinentes preservam finalidade, retenção e acesso.

## Release — somente quando contratos, banco ou operação forem afetados

- [ ] Breaking changes e consumidores antigos identificados; transição documentada quando necessária.
- [ ] Migrations avaliadas quanto a volume, locks, compatibilidade e recuperação.
- [ ] Impacto de deploy, configuração e monitoramento avaliado; riscos conhecidos registrados.

Uma tarefa documental pode concluir com revisão de conteúdo e links; uma correção CSS exige validação visual pertinente,
sem migration; uma mudança crítica de autorização precisa comprovar o comportamento permitido e negado.
Reportar resultado, verificações reais e limitações relevantes. Não confundir checklist mental com evidência executada.
