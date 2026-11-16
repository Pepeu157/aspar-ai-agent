# ASPAR AI Agent

Base local de aplicação para apoiar o tratamento de solicitações de audiências, sempre com revisão humana. Nesta etapa não há acesso ao Microsoft 365, integrações externas ou envio de e-mails.

## O que existe nesta fundação

- API FastAPI para criar, listar e consultar solicitações;
- análise determinística local, conservadora e sem provedor de modelo;
- extração somente de informações explicitamente identificadas;
- campos ausentes ou incertos como `null` e listas vazias;
- armazenamento volátil em memória;
- frontend React/TypeScript que consulta a API e não mostra registros de demonstração;
- testes automatizados para validação e cenários de escopo.

## Limitações

As regras locais não são um modelo de IA e não oferecem interpretação semântica ampla. Não geram uma minuta. O armazenamento em memória é perdido ao encerrar o processo e não é apropriado para produção. Utilize exclusivamente mensagens sintéticas. Nenhum dado institucional ou pessoal real deve ser adicionado.

## Estrutura

```text
.
├── backend/app/{api,core,domain,repositories,services}/
├── backend/tests/
├── frontend/src/
├── docs/
├── ai/
└── integrations/
```

## Execução

Veja [`docs/development.md`](docs/development.md) para comandos PowerShell (Windows) e Linux/macOS. API local em `http://127.0.0.1:8000`; OpenAPI em `/docs`; frontend em `http://localhost:5173`.

## Endpoints

- `GET /health`
- `POST /api/v1/requests` com JSON `{"message_text":"Solicito audiência."}`
- `GET /api/v1/requests`
- `GET /api/v1/requests/{request_id}`

Nenhum endpoint envia e-mail nem acessa caixa postal.

## Próximas decisões

Persistência durável, identidade e autenticação, fluxo completo de revisão/aprovação, política de retenção e eventual modelo de IA dependem de análise e autorização institucional. Microsoft Graph/Outlook, Power Automate, SharePoint e Dataverse continuam opcionais e desativados.
