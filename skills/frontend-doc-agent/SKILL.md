---
name: frontend-doc-agent
description: Aplicar padrões obrigatórios e incrementais de frontend, documentação e SonarQube. Use sempre que esta skill for citada no AGENTS.md aplicável ou quando a tarefa envolver código de interface, experiência visual ou frontend.
---

# CONTEXTO

Skill de apoio para mudancas de frontend em qualquer linguagem, framework ou plataforma.

# OBRIGATORIEDADE E ESCOPO

- Se esta skill estiver citada no `AGENTS.md` aplicável, seguir suas instruções em toda tarefa de frontend dentro desse escopo.
- Não substituir, flexibilizar ou ignorar estas regras por preferência própria. Em caso de conflito, seguir instruções de maior prioridade e informar o conflito.
- Em frontend existente, aplicar os padrões somente aos componentes, estilos, estado, testes, documentação e contratos diretamente tocados pela tarefa.
- Inspecionar apenas o contexto necessário para entender e validar o fluxo afetado. Não procurar problemas nem modernizar telas, componentes, rotas ou módulos não relacionados.
- Corrigir legado gradualmente: adequar a parte alterada e preservar o restante, salvo dependência direta indispensável para a mudança funcionar.
- Não ampliar o pedido para uma refatoração, migração visual, adoção de biblioteca, i18n global ou revisão de acessibilidade do projeto inteiro.
- Em frontend novo, aplicar os padrões desde a base no escopo solicitado.

# ORDEM

1. Ler documentacao local relevante do frontend, se existir
2. Identificar padrao de componentes/estado/estilo vigente
3. Implementar sem quebrar contratos de UI/API
4. Validar build, lint e testes do modulo afetado
5. Atualizar documentacao local

# PADROES FRONTEND

- Priorizar organizacao por feature quando o projeto ja seguir esse modelo
- Evitar componentes gigantes; extrair partes com responsabilidade clara
- Manter separacao entre apresentacao, estado e acesso a API
- Reutilizar componentes e tokens existentes antes de criar novos
- Usar um unico Tailwind por projeto; separar apenas os tokens de cor para temas light e dark
- Em frontend novo, oferecer temas light e dark. Em projeto existente, respeitar e completar ambos os temas somente nos componentes e fluxos visuais tocados, sem iniciar migração global fora do pedido

# I18N

Quando o projeto tiver suporte a internacionalizacao, gerenciar arquivos de idioma, chaves de traducao e configuracao i18n seguindo o padrao vigente do framework ou biblioteca em uso.

## Configuracao

- Identificar a biblioteca, framework ou mecanismo de i18n ja adotado pelo projeto antes de alterar configuracao.
- Manter idiomas suportados, idioma padrao, estrategia de URL e deteccao de idioma consistentes com a decisao do produto.
- Garantir que o caminho configurado para arquivos de idioma corresponda ao local real dos arquivos no projeto.
- Evitar trocar biblioteca, formato de arquivo ou estrategia de roteamento sem necessidade explicita.

## Estrutura Dos Arquivos De Idioma

Organizar chaves por dominio de feature, usando uma estrutura aninhada equivalente ao formato adotado pelo projeto:

```
{
    "featureName": {
        "sectionName": {
            "title": "Translated Title",
            "searchPlaceholder": "Search...",
            "filters": {
                "all": "All",
                "active": "Active"
            }
        }
    }
}
```

## Uso

- Usar o helper, hook, diretiva, filtro, funcao ou componente de traducao ja adotado pelo projeto.
- Referenciar textos por chaves estaveis, por exemplo `featureName.sectionName.title`.
- Evitar concatenar frases traduzidas em partes quando a ordem gramatical puder variar entre idiomas.
- Usar interpolacao, pluralizacao e formatacao de datas, numeros e moedas pelos recursos de i18n disponiveis.

## Regras De I18N

- Organizar chaves por dominio de feature em objetos aninhados.
- Todo texto visivel ao usuario deve usar o mecanismo de traducao do projeto; evitar strings hardcoded em templates, componentes, views e mensagens de validacao.
- Manter todos os arquivos de idioma sincronizados com as mesmas chaves.
- Nao alterar prefixos de rota, cookies, persistencia ou deteccao de idioma sem confirmar o comportamento esperado do projeto.
- Preservar nomes de chaves existentes quando ja houver uso em producao, a menos que a refatoracao atualize todas as referencias.

## Workflow De I18N

1. Ler a configuracao e os arquivos de idioma existentes.
2. Adicionar ou atualizar chaves em todos os arquivos de idioma simultaneamente.
3. Verificar que as chaves batem entre todos os idiomas.
4. Usar busca textual limitada aos arquivos e ao fluxo afetado para encontrar strings hardcoded que deveriam usar i18n.

# UX, ACESSIBILIDADE E PERFORMANCE

- Preservar navegacao por teclado e semantica HTML
- Revisar estados de loading, erro e vazio
- Evitar renderizacoes desnecessarias e bundles maiores sem necessidade
- Garantir responsividade minima desktop/mobile

# QUALIDADE

- Validar tipagem e contratos de dados
- Atualizar testes de componentes/paginas quando comportamento mudar
- Evitar regressao visual em fluxos criticos

# SONARQUBE E CLEAN AS YOU CODE

Todo código frontend criado ou alterado deve respeitar o Quality Profile e o Quality Gate SonarQube ativos no projeto:

- Ler somente a configuração SonarQube do frontend afetado e seus comandos de análise, quando existirem.
- Não introduzir novos bugs, vulnerabilidades, code smells, Security Hotspots sem revisão ou duplicação no New Code.
- Antes de criar componente, hook, utilitário, regra de validação, transformação de dados ou estilo repetido, verificar os equivalentes do módulo afetado e os compartilhados diretamente usados por ele.
- Reutilizar quando comportamento e contrato forem realmente iguais. Não criar abstração genérica apenas para reduzir uma ocorrência métrica de duplicação.
- Evitar duplicar blocos de JSX/templates, chamadas de API, tratamento de estados, validações, mapeamentos e regras de estilo dentro do fluxo alterado.
- Manter componentes e funções coesos, reduzir complexidade cognitiva, retornos ambíguos, condicionais aninhadas, efeitos colaterais ocultos e código morto.
- Não inserir HTML inseguro, `eval`, URLs não validadas, segredos no bundle, tokens em logs ou armazenamento inseguro. Sanitizar conteúdo externo e preservar as proteções do framework contra XSS e injeção.
- Atualizar testes do comportamento alterado e a cobertura do New Code conforme o Quality Gate do projeto; não criar testes que apenas executem linhas sem validar resultado observável.
- Não silenciar achados com `NOSONAR`, comentários de supressão, exclusões ou desativação de regras. Falso positivo exige evidência e justificativa conforme o processo do projeto.
- Executar lint, tipagem, testes e análise Sonar local já configurada e segura para o módulo afetado. Se o scan depender da CI ou de credenciais, não improvisar nem expor segredos; informar a validação pendente.

Em frontend existente, corrigir os achados relacionados ao New Code e às linhas tocadas. Não procurar nem corrigir telas ou módulos não relacionados para limpar o Overall Code.

# DOCUMENTACAO

Se houver alteracao funcional no escopo tocado:
- atualizar docs do frontend
- atualizar index da documentacao local
- registrar decisoes de UI relevantes para o time
