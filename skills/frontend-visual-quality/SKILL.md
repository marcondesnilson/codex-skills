---
name: frontend-visual-quality
description: Orientar criação, redesign e refinamento visual de interfaces web, desktop e aplicativos com inspeção real; use quando a tarefa alterar apresentação ou interação.
---

# Objetivo e limites

Use esta skill quando a tarefa alterar apresentação ou interação. Respeite as instruções superiores e o escopo do usuário. A autorização para redesign vale somente até onde o usuário pediu. Correção exclusivamente funcional ou tarefa sem mudança de interface não exige auditoria visual completa.

Esta skill fornece instruções ao Codex. Use o navegador, a janela nativa, o emulador ou o dispositivo disponível para capturar e inspecionar a aplicação real. O helper em `scripts/visual_review.py` oferece operações locais de aceite e, somente com autorização específica por tarefa, envia à Responses API ou à Images API arquivos locais explicitamente selecionados. O Codex implementa a mudança, compara os achados com a aplicação, decide correções e relata o resultado. O helper não controla navegador, não executa comandos recebidos do revisor, não aplica código e não aprova a tarefa.

# Fluxo

1. Delimite a rota, os componentes, estados, escopo de usuário e critérios de aceite. Leia as instruções pertinentes do projeto e o design system existente. Em `$qa-projects`, declare um plano antes dos checks e preserve a escolha `current`/`isolated` dessa skill.
2. Escolha o modo **criação** ou **fidelidade**; leia a [referência de criação](references/creation-mode.md) ou a [referência de fidelidade](references/fidelity-mode.md).
3. Crie a pasta de evidências da tarefa e, quando houver prévia executável e ferramenta adequada à plataforma, capture o estado inicial real da aplicação. Registre rota, viewport, tema, estado, ferramenta e hash da captura. Não invente screenshots.
4. Implemente somente o escopo solicitado. Execute as verificações funcionais pertinentes.
5. Inspecione a renderização real com Chrome DevTools MCP ou outra ferramenta adequada disponível. Playwright não é obrigatório e não deve ser instalado apenas para cumprir este fluxo. Inspecione seções e interações pertinentes; o primeiro viewport não valida sozinho uma página longa.
6. Separe `review_required` de `api_execution_authorized`. Se o plano declarar impacto em apresentação ou interação, a revisão visual externa é requisito de aceite; falta de serviço, autorização ou evidência resulta em `BLOCKED`, salvo falha confirmada (`FAIL`). Uma API key não autoriza a chamada. Só execute uma operação API com autorização por tarefa e permissão explícita de execução; caso contrário, registre-a como não executada e não aprove o gate visual obrigatório.
7. Compare os achados do revisor com a interface real e os critérios de aceite. Corrija problemas confirmados dentro do escopo. Repita a inspeção após mudanças relevantes; pare quando os critérios forem atendidos ou houver limite/bloqueio documentado. Registre cada ciclo visual sem API com `record-cycle`; uma revisão API ao vivo registra automaticamente o próprio ciclo. Não repita revisão por API com evidências iguais nem continue sem progresso demonstrável.
8. Mantenha uma pasta privada de evidências por tarefa. Separe o resultado funcional, a inspeção visual real, a resposta consultiva e a conclusão geral. Declare telas, estados ou dispositivos não inspecionados e pendências.

# Critérios de conclusão

- O escopo e os critérios de aceite estão registrados.
- As regras do modo escolhido foram seguidas; adaptações e condições não validadas estão identificadas.
- As verificações funcionais e inspeções reais da interface são relatadas separadamente, com rota, viewport, tema, estado, ferramenta e hashes das evidências.
- A revisão por API consta como **não executada**, **falhou/não aprovada** ou **achados consultivos avaliados pelo Codex**. Lista vazia de achados nunca aprova a tarefa.
- A conclusão geral reflete somente evidências inspecionadas. Atingir o limite de ciclos não significa sucesso; não alegue equivalência pixel a pixel sem medição apropriada.
- Em QA integrado, cada critério visual aponta para tela, região, estado, plataforma e IDs de capturas obrigatórias; uma captura ausente, obsoleta ou sem proveniência não pode ser aceita.
- Relacione a evidência ao build servido, não apenas ao Git `HEAD`. Mudança de versão/build/configuração/direção/assets invalida checks e capturas que não correspondam ao fingerprint corrente.
- O resultado agregado do gate é derivado da mesma evidência em state, manifest e report, na ordem `FAIL` > `BLOCKED` > `PASS WITH WARNINGS` > `PASS`.

## Arquivos de apoio

- [Modo criação](references/creation-mode.md): direção visual e decisões antes da implementação.
- [Modo fidelidade](references/fidelity-mode.md): alvo visual e regras de comparação/adaptação.
- [Revisão por API](references/api-review.md): autorização, privacidade, limites, preços e comandos do helper.
- [Contrato da API](references/api-contract.md) e [schemas JSON](schemas/): formato da revisão e autorização.
- [Acceptance gate](references/acceptance-gate.md): plano prévio, build servido, evidência vinculada e conclusão derivada.
- [Media Kit e direção](references/media-kit-and-direction.md): origem, classificação, conflitos e adoção de direção.
- [Operações API](references/operations.md): autorização v2, limites, custos, dry-run e trilha comum.
