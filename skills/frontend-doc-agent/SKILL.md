---
name: frontend-doc-agent
description: Aplicar padrões recorrentes para frontend com foco em organização por feature, consistência visual, acessibilidade, performance e documentação.
---

# CONTEXTO

Skill de apoio para mudancas de frontend (React, Vue, Next, Vite ou similar).

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
