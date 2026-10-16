---
name: frontend-visual-quality
description: Auditar e refinar a qualidade visual de interfaces web no escopo solicitado, com referências, evidências de navegador e preservação de comportamento. Use em tarefas de criação, redesign ou refinamento visual quando citada no AGENTS.md ou solicitada.
---

# Objetivo

Complementar `frontend-doc-agent` com critérios verificáveis de acabamento visual. Não substituir governança do `global-doc-agent`, testes funcionais ou decisões de produto. Não é um agente autônomo nem depende de um framework específico.

# Escopo e precedência

- Respeitar instruções superiores, `AGENTS.md` aplicável, documentação e design system do projeto.
- Em aplicações existentes, atuar apenas nas telas, componentes e contratos diretamente afetados. Não iniciar redesign global, migração de framework ou adoção de biblioteca por conta própria.
- Preservar comportamento, fluxos, acessibilidade, i18n, estados de interface e contratos de API.
- React, Vue ou outra stack web: identificar a tecnologia real antes de alterar componentes e estilos. Reutilizar tokens, componentes e convenções existentes.
- Se houver referência visual aprovada, tratá-la como direção estética; não copiar HTML gerado sem adaptar à arquitetura existente.
- Sem referência, analisar a tela atual e propor melhorias proporcionais à tarefa; não inventar uma identidade visual corporativa.

# Processo de qualidade visual

1. **Contexto**: identificar tela/fluxo, restrições, componentes existentes, temas e estados relevantes; ler apenas a documentação pertinente.
2. **Referência**: localizar design aprovado, screenshot ou padrões locais. Registrar se não existir referência. Se houver MCP do Stitch disponível e o projeto/tarefa indicar um design específico, consultá-lo; caso contrário, não exigir Stitch.
3. **Diagnóstico**: examinar hierarquia visual, densidade de informação, grid, alinhamento, tipografia, escala, espaços, contraste, estados, consistência e responsividade. Distinguir problema de preferência estética.
4. **Implementação**: ajustar no menor escopo possível; priorizar tokens e componentes compartilhados quando a mudança realmente afetar seus consumidores. Evitar valores arbitrários e overrides repetidos.
5. **Validação funcional**: executar as verificações existentes pertinentes, incluindo lint, tipagem, testes e build quando disponíveis. Não confundir sucesso técnico com qualidade visual.
6. **Inspeção visual**: quando houver navegador automatizável, executar a tela real e capturar evidências em desktop, mobile e largura intermediária pertinente, com tema claro/escuro quando suportados. Incluir estados críticos acessíveis no escopo. Usar Playwright se já disponível; não instalar dependência nova apenas para satisfazer este passo.
7. **Comparação e refinamento**: comparar com referência sob viewport, tema, dados e estado equivalentes; registrar diferenças relevantes e corrigir. Repetir a inspeção das áreas afetadas após correção.
8. **Entrega**: relatar telas verificadas, resoluções, evidências, diferenças remanescentes e verificações não executadas. Nunca afirmar fidelidade visual validada sem inspeção efetiva.

# Critérios de aceitação visual

- Hierarquia clara entre título, contexto, ações principais, conteúdo e elementos secundários.
- Alinhamentos e ritmo de espaçamento coerentes com os tokens e a densidade esperada do produto; sem vazios excessivos ou compactação que prejudique a leitura.
- Tipografia legível e consistente em peso, tamanho, altura de linha e comprimento de texto.
- Tabelas, filtros, formulários, modais e navegação utilizáveis nas larguras pertinentes; sem cortes, sobreposição ou overflow inesperado.
- Contraste, foco visível, navegação por teclado, labels e estados não dependentes apenas de cor preservados.
- Loading, vazio, erro, sucesso e demais estados aplicáveis não quebram o layout.
- Elementos repetidos seguem o mesmo padrão; não criar componentes visualmente divergentes para a mesma função.
- Alterações visuais não quebram interação, roteamento, responsividade ou contratos com a API.

# Integrações opcionais

- **Stitch via MCP**: fonte de design quando disponível e explicitamente relevante. Registrar o design consultado; não presumir acesso.
- **Impeccable**: aplicar suas orientações de crítica/refinamento quando instalado e apropriado; não alegar uso sem realmente consultá-lo.
- **Playwright ou navegador equivalente**: evidência de renderização e interação; screenshots não substituem testes funcionais nem comprovam automaticamente equivalência pixel a pixel.
- Na ausência de ferramentas, executar verificações disponíveis, explicar a limitação e deixar a validação visual como pendência explícita. Não fabricar screenshots, métricas de similaridade ou aprovações.

# Definition of Done

- Escopo e referência identificados, ou ausência de referência registrada.
- Implementação segue a arquitetura existente e preserva contratos.
- Problemas visuais relevantes do escopo corrigidos ou documentados com justificativa.
- Evidências reais de inspeção visual e validação funcional informadas; pendências declaradas.
- Documentação local atualizada somente quando houver decisão ou comportamento relevante alterado.


# CICLO AUTÔNOMO DE FIDELIDADE VISUAL

Quando a tarefa autorizar criação ou redesign, executar o ciclo abaixo **somente no escopo solicitado**, sem checkpoints de aprovação intermediários desnecessários:

1. Identificar o design aprovado e as condições comparáveis (viewport, tema, conteúdo, estado). Se Stitch via MCP estiver disponível e o design indicado, consultar a fonte e seus assets; não exigir Stitch quando não for relevante.
2. Mapear funcionalidades, contratos, acessibilidade e consumidores dos componentes atuais antes de substituí-los.
3. Implementar ou reconstruir a apresentação com liberdade proporcional ao redesign autorizado, preservando comportamento e integrações. Não limitar a mudança a CSS antigo.
4. Executar build, tipagem, lint e testes pertinentes existentes; corrigir falhas introduzidas.
5. Inspecionar a aplicação real com Playwright, navegador equivalente ou ferramenta nativa compatível (por exemplo, testes Flutter em emulador/dispositivo). Capturar evidências reais em resoluções e estados relevantes.
6. Comparar com a referência: hierarquia, grid, densidade, tipografia, cores, imagens, ícones, espaçamentos, bordas, sombras, temas, estados e responsividade.
7. Corrigir diferenças materiais e repetir testes e inspeção até cumprir os critérios ou encontrar bloqueio demonstrável. Não alegar equivalência pixel a pixel sem medição adequada.
8. Entregar resumo dos fluxos, dispositivos/viewports, evidências, testes e limitações. Não inventar resultados ou acesso a ferramentas.

- Impeccable é um recurso opcional de crítica visual quando instalado e relevante, não um requisito universal.
- Não instalar ferramentas ou dependências apenas para simular conformidade; utilizar as disponíveis e declarar impedimentos reais.
- Para componentes compartilhados ou motores multi-tenant, validar os consumidores diretamente afetados e preservar variantes anteriores quando necessário.
- Mudanças em produção, deploy, dados reais, commits e push permanecem sujeitos a autorização explícita.
