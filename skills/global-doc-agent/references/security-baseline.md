# Baseline de segurança, dependências e configuração

Consultar ao tocar entradas externas, autenticação, autorização, dados, configuração, dependências ou limites de confiança.
Obrigatório no fluxo afetado, proporcional à exposição; implementação pertence à stack.

- Não versionar segredos, colocá-los em logs, exemplos, fixtures ou enviá-los ao cliente. Variáveis públicas e bundles
  são visíveis. Usar placeholders em exemplos e documentar nomes/finalidade sem valores reais.
- Preferir configuração externa para valores por ambiente. Separar development, testing, staging/homologação e
  production conforme a operação; não exigir quatro ambientes físicos para todo produto.
- Não promover automaticamente debug, credenciais de exemplo, permissões amplas ou configuração insegura de dev
  para produção. Separar credenciais, acessos e dados; não usar dados reais de produção em testes sem proteção adequada.
- Aplicar menor privilégio a usuários, serviços e integrações; validar, normalizar e autorizar entrada externa.
- Autenticar quando o recurso exigir identidade. Autorizar no servidor/fronteira confiável, inclusive objeto e tenant;
  ocultar botão não concede proteção. Respeitar autenticação já adotada sem inventar mecanismos próprios.
- Revisar SQL Injection, XSS, Command Injection, Path Traversal, SSRF, CSRF, Mass Assignment e Broken Access Control
  conforme os vetores alterados, incluindo uploads, arquivos e URLs externas.
- Proteger dados sensíveis em trânsito e armazenamento conforme risco; usar criptografia suportada, nunca caseira.
- Sessões/tokens exigem armazenamento apropriado, expiração, renovação e revogação/logout coerentes com o produto.
- Aplicar rate limiting a login, recuperação, operações caras ou sujeitas a abuso; evitar enumeração de contas/recursos
  por mensagens, respostas ou comportamento indevidamente distintos.
- Em web/HTTP, avaliar headers de segurança, cookies e política de origem conforme a arquitetura; detalhes ficam na stack.
- Erros públicos são seguros e acionáveis; logs preservam contexto necessário sanitizado. Não capturar sem ação útil,
  esconder exceções ou registrar indiscriminadamente mensagem/payload recebido.
- Operações críticas acionam [auditoria](tracking-and-audit.md); dados pessoais acionam [privacidade](privacy-and-legal.md).
- Revisar explicitamente hotspots: origem da entrada, limites de confiança, exposição e mitigação. Não declarar seguro
  por mera ausência de alerta do scanner.

## Dependências

Ao adicionar/atualizar dependência, verificar o que o projeto e a stack já resolvem. Avaliar necessidade, manutenção,
versão suportada, licença, vulnerabilidades conhecidas e custo de atualização. Não adicionar biblioteca para algo trivial
já resolvido nativamente, nem dependência abandonada sem justificativa e plano de manutenção/substituição.

Usar manifests, lockfiles e ferramentas de análise existentes. Verificar avisos nas fontes oficiais atuais quando necessário;
não presumir ausência de vulnerabilidades por desconhecimento. Atualizar dentro da compatibilidade e do escopo, sem
upgrade geral oportunista. Registrar risco relevante, mitigação e condição de resolução se a correção imediata não for viável.
Mudança de dependência ou distribuição exige [revisão de licenciamento](licensing.md).
