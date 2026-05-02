---
name: frontend-doc-agent
description: Aplicar padrões recorrentes para frontend com foco em organização por feature, consistência visual, acessibilidade, performance, i18n e documentação.
---

# CONTEXTO

Skill de apoio para mudancas de frontend em qualquer linguagem, framework ou plataforma.

# ORDEM

1. Ler documentacao local do frontend
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
- Todo projeto frontend deve oferecer temas light e dark para melhor adaptacao ao usuario

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
4. Usar busca textual para encontrar strings hardcoded em componentes que deveriam usar i18n.

# UX, ACESSIBILIDADE E PERFORMANCE

- Preservar navegacao por teclado e semantica HTML
- Revisar estados de loading, erro e vazio
- Evitar renderizacoes desnecessarias e bundles maiores sem necessidade
- Garantir responsividade minima desktop/mobile

# QUALIDADE

- Validar tipagem e contratos de dados
- Atualizar testes de componentes/paginas quando comportamento mudar
- Evitar regressao visual em fluxos criticos

# DOCUMENTACAO

Se houver alteracao funcional:
- atualizar docs do frontend
- atualizar index da documentacao local
- registrar decisoes de UI relevantes para o time
