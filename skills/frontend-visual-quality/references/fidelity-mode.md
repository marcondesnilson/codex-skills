# Modo fidelidade

Use somente quando o usuário identificar uma referência visual como alvo a reproduzir. Registre a origem/identificador da referência e a rota da aplicação comparada. Sem referência-alvo identificada, use o modo criação.

Compare condições equivalentes: conteúdo, viewport, tema e estado da interface. Em screenshots de navegador, registre o viewport CSS e as dimensões em pixels da imagem separadamente quando o fator de escala do dispositivo puder fazê-los divergir. Associe cada captura de referência à captura de resultado correspondente. O helper rejeita pares de fidelidade com rota, viewport, tema, estado ou `content_id` diferentes.

Reproduza o alvo identificado dentro do escopo pedido; não o reinterprete livremente. Adapte somente quando o alvo conflitar com comportamento necessário, acessibilidade, restrição da plataforma ou contrato explícito do projeto. Registre cada adaptação e sua justificativa. Se uma largura, tema, conteúdo ou estado não tiver referência, identifique o resultado como adaptação e não o declare como reprodução validada.

Inspeção visual pode apontar diferenças aparentes, mas não comprova equivalência pixel a pixel. Não alegue equivalência nesse nível sem método de medição apropriado e resultados registrados. Mantenha validação funcional separada da comparação com a referência.
