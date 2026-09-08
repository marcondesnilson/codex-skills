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

# INTEGRAÇÃO COM O GLOBAL

Consultar `global-doc-agent` pelo catálogo disponível antes de implementar e ler suas referências acionadas pela tarefa.
O Global define requisitos transversais; esta skill implementa componentes, estado, estilo, temas, i18n e validação visual.
Não duplicar documentos de governança nem reiniciar leituras já realizadas. Se uma skill de plataforma estiver disponível,
combiná-la com estes padrões: mobile usa semântica e acessibilidade nativas, sem impor HTML, Tailwind ou APIs de navegador.

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
- Quando o projeto usar Tailwind, usar uma única instalação/configuração base; separar apenas os tokens de cor para temas light e dark. Não adotar Tailwind onde a stack já usa outra solução
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

- Implementar os requisitos de UX do Global nos componentes afetados: labels associados, semântica HTML ou nativa,
  teclado/foco quando aplicáveis, contraste, erro identificável e informação que não dependa apenas de cor
- Modelar loading, vazio, erro, sucesso, sem permissão, sessão expirada e offline conforme o fluxo; preservar dados
  editados e oferecer ação de recuperação quando possível, sem tratar erro HTTP como ausência de rede
- Validar interação e renderização relevantes, incluindo tecnologia assistiva quando pertinente; não depender só do build
- Evitar renderizacoes desnecessarias e bundles maiores sem necessidade
- Em web, conferir responsividade desktop/mobile e tamanhos intermediários relevantes, overflow e espaço útil dos componentes
- Ao implementar Sobre, suporte, licenças ou novidades, reutilizar navegação/componentes existentes e consumir metadados
  de versão confiáveis. Aplicar a separação de informação pública/interna do Global e preservar temas/i18n do projeto

# QUALIDADE

- Validar tipagem e contratos de dados
- Atualizar testes de componentes/paginas pertinentes quando comportamento relevante mudar e houver infraestrutura;
  não criar testes artificiais para alterações visuais triviais
- Evitar regressao visual em fluxos criticos

# QUALIDADE FRONTEND E SONARQUBE

Aplicar integralmente a política de qualidade e o checklist do `global-doc-agent`. Esta seção apenas especializa o New Code
de interface e deve preservar a tecnologia, a arquitetura e as bibliotecas já adotadas:

- Evitar componentes excessivamente grandes, responsabilidades misturadas e duplicação de JSX/templates, chamadas de
  API, validações, mapeamentos, estados e estilos. Extrair somente unidades com responsabilidade e contrato claros.
- Evitar estados redundantes e derivados armazenados sem necessidade, effects desnecessários e efeitos colaterais ocultos.
- Tratar promises e erros explicitamente; não deixar rejeições sem tratamento nem usar `catch` vazio.
- Tratar dados da API e qualquer HTML externo como não confiáveis. Preservar escaping do framework, sanitizar quando HTML
  dinâmico for indispensável e evitar `eval`, URLs não validadas e APIs inseguras de injeção de HTML.
- Nunca colocar secrets no bundle, em variáveis públicas, source maps, logs ou armazenamento inseguro do cliente.
- Modelar loading, erro e empty state quando aplicáveis ao fluxo, sem deixar estado inconsistente após falhas ou retries.
- Fazer cleanup de listeners, subscriptions, observers, timers e requisições canceláveis quando seu ciclo de vida exigir,
  evitando memory leaks e atualizações após desmontagem.
- Manter TypeScript consistente com os contratos reais da API, tratar nulabilidade e evitar `any` desnecessário. Não usar
  assertions ou casts apenas para esconder incompatibilidade de tipo.
- Remover imports, variáveis, props, handlers e branches sem uso que resultem da alteração.
- Preservar semântica HTML, teclado, foco, rótulos e acessibilidade aplicáveis aos componentes tocados.
- Testar comportamento observável, contratos da API, estados assíncronos e correções de regressão relevantes.
- Executar lint, tipagem, testes, build e Sonar já configurados para o módulo afetado. Não inventar configuração nem afirmar
  que o Quality Gate passou quando o scan não foi executado.
- Não introduzir biblioteca, framework, gerenciador de estado ou arquitetura nova sem necessidade demonstrada pela tarefa.

Em frontend existente, limitar a inspeção e as correções ao New Code, às linhas tocadas e aos contratos diretos. Não limpar
ou modernizar outras telas apenas por haver dívida no Overall Code.

# DOCUMENTACAO

Se a mudança afetar comportamento, configuração, contratos, decisões de UI ou processo no escopo tocado:
- atualizar docs do frontend
- manter index/MOC da documentacao local coerente, editando quando links, navegação ou resumo mudarem
- registrar decisoes de UI relevantes para o time
