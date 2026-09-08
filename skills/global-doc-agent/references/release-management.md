# Versão, compatibilidade e release

Consultar em release solicitada, funcionalidade relevante, contrato externo, migration ou compatibilidade alterada.
Avaliar impacto não autoriza publicar, implantar ou criar commit.

## Versão e fonte de verdade

- Padrão: Semantic Versioning `MAJOR.MINOR.PATCH`, salvo motivo documentado em contrário.
- MAJOR: breaking change confirmada em contrato/comportamento; MINOR: funcionalidade compatível; PATCH: correção
  compatível. Classificar pelo contrato publicado do produto, inclusive quando o produto é documentação/skill.
- Definir o contrato considerado: API, formato de arquivo, comportamento ou integração. Identificar explicitamente
  consumidores afetados; quantidade de arquivos não determina a versão.
- Separar versão e build nas plataformas que usam build number. Não incrementar build como substituto de SemVer.
- Confirmar fonte existente em VERSION, manifests, pipeline ou equivalente antes de alterar. Evitar múltiplas fontes
  divergentes; apresentar a versão realmente implantada, não a última versão disponível no servidor de atualizações.
- Ajustar versão no momento previsto pelo fluxo do projeto/release solicitada, não em cada pequena edição. Não criar
  VERSION ou alterar manifests automaticamente apenas porque esta referência foi consultada.

## Changelogs e documentação de release

Recomendado manter histórico; obrigatório atualizar os registros exigidos pelo projeto ou necessários para comunicar
mudança relevante/compatibilidade. Aproveitar localização existente, sem criar vários arquivos que repetem o mesmo texto.

- Usuário: efeitos compreensíveis, como novo relatório, pesquisa mais rápida ou correção de login.
- Técnico: migrations, APIs, dependências, refatorações, breaking changes e instruções à equipe.
- Release registra versão, data confirmada, resumo e campos pertinentes: funcionalidades, melhorias, correções,
  breaking changes, migrations, implantação e riscos conhecidos. Omitir campos vazios; não inventar data de publicação.
- Não expor detalhes internos, vulnerabilidades ou topologia em notas ao usuário. Entregar detalhe técnico a destinatários
  autorizados; B2B pode usar portal ou documentação entregue, sem página pública.
- Novidades pós-update seguem [governança do produto](application-governance.md), sem modal obrigatório por patch.

## Compatibilidade e migrações

Antes de alterar APIs, schemas, banco, eventos ou integrações, avaliar consumidores externos e aplicativos antigos.
Preservar compatibilidade, documentar depreciação/transição e identificar breaking changes antes de implantar.

Quando houver migration, avaliar volume, tempo, locks, dados existentes, coexistência de versões, ordem de deploy,
rollback ou estratégia de recuperação e deploy gradual quando necessário. Mudança destrutiva exige preservação de dados
ou recuperação demonstrável no contexto da operação; não presumir que rollback de código reverte transformação de dados.
Usar testes e ambiente representativos proporcionais ao risco. Detalhes técnicos pertencem à skill da stack/banco.
Não exigir migration em CSS, documentação ou qualquer alteração sem impacto de banco.

## Integração com commit-projects

`commit-projects` mantém o procedimento operacional: diff completo, reconciliação documental, classificação independente,
VERSION, validação, staging e commit local. Consultar essa skill disponível no catálogo quando o fluxo for solicitado.
Preservar sua exigência de invocação explícita; nunca iniciar commits por referência indireta. Push exige pedido separado.
Em preparação sem commit, explicar versão proposta e motivos; no commit posterior, reavaliar o diff completo contra HEAD
conforme a skill, sem aplicar um segundo incremento sobre o valor já preparado.
