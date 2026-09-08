# Observabilidade e operação

Consultar em produto novo operado ou mudanças de logs, métricas, erros, suporte, monitoramento, deploy e infraestrutura.
Obrigatório quando aplicável ao risco operacional; não instalar ferramentas ou instrumentar outros módulos sem necessidade.

- Usar logs estruturados e identificadores de correlação quando houver múltiplos componentes ou investigação de erros.
- Definir níveis, volume, amostragem, retenção e acesso; evitar logs repetitivos, dados pessoais, tokens, credenciais
  e payloads confidenciais. Sanitizar também mensagens de exceções e URLs.
- Selecionar métricas, monitoramento e alertas para falhas e objetivos operacionais reais; indicar responsável e ação
  esperada de cada alerta. Não criar dashboards ou alertas sem finalidade.
- Rastreabilidade distribuída é recomendada quando a correlação entre serviços justificar seu custo.
- Diagnóstico enviado pelo usuário segue [governança do produto](application-governance.md); auditoria segue
  [trilhas de auditoria](tracking-and-audit.md).

## Healthcheck e status

Todo serviço novo operado deve ter documentação e implementação mínima de health/status compatível com a plataforma.
Bibliotecas e aplicativos locais/mobile não precisam hospedar endpoints: avaliar sinais de funcionamento pertinentes.
Em projeto existente, aplicar estas regras somente quando a tarefa criar ou alterar health/status, monitoramento, deploy ou infraestrutura que
dependa desses sinais. Uma mudança sem relação com esse fluxo não autoriza procurar ou implantar healthchecks.

Regras gerais:
- expor um endpoint, rota, comando ou arquivo de liveness acessível ao monitor autorizado para monitoramento automatizado
- expor status humano quando fizer sentido para operação, suporte ou validação de deploy
- separar liveness de readiness quando a stack permitir
- liveness deve ser rápido e não depender de banco, APIs externas, filas ou serviços terceiros
- readiness deve validar dependências reais necessárias para receber tráfego
- readiness deve diferenciar estado saudável, degradado e erro quando houver checks não críticos
- documentar payloads, status HTTP, periodicidade, dependências verificadas e exemplos de uso
- documentar como o healthcheck deve ser usado em Docker, Swarm, Kubernetes, CDN ou hospedagem estática
- cobrir health/status com testes, smoke tests ou validação de build quando aplicável

Diretrizes por tipo de projeto:
- backend/API: usar os contratos de monitoramento da skill especializada e do projeto
- frontend SPA/SSR: expor health estático ou rota adequada validando build, versão e configuração essencial sem divulgar valores internos
- frontend que consome API: status humano deve indicar conectividade com backend quando seguro e relevante
- worker/CLI: disponibilizar comando, endpoint interno ou arquivo de status compatível com a infraestrutura
- monorepo: cada projeto deve ter health próprio, e agregadores devem apenas consolidar estados existentes

## Exposição

Existir não significa ser público na Internet. Liveness público, quando necessário, retorna apenas sinal mínimo seguro.
Readiness detalhada e status operacional devem ficar restritos à rede/identidade autorizada. Se houver status público,
exibir apenas disponibilidade e informações úteis ao público, sem topologia, versões de componentes, IPs ou erros internos.
Testar também acesso indevido aos diagnósticos, além dos estados saudável, degradado e erro.
