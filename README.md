# ASPAR AI Agent

Base local de aplicação para apoiar o tratamento de solicitações de audiências, sempre com revisão humana. Não há acesso ao Microsoft 365, integrações externas ou envio de e-mails.

## Componentes

- API FastAPI para criar, listar e consultar solicitações;
- regras determinísticas locais, sem provedor de modelo;
- extração conservadora com campos ausentes como `null`;
- armazenamento volátil em memória;
- frontend React/TypeScript que consome a API local e não contém registros de demonstração;
- testes automatizados para validação e escopo.

A análise é heurística, não um modelo de IA, e pode classificar incorretamente. A aplicação não gera minuta. Use exclusivamente dados fictícios. Registros são perdidos ao reiniciar o backend; não usar em produção.

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

## Execução local

Consulte [`docs/development.md`](docs/development.md) para PowerShell e Linux/macOS. API: `http://127.0.0.1:8000` (OpenAPI em `/docs`); frontend: `http://localhost:5173`.

## Endpoints

- `GET /health`
- `POST /api/v1/requests` com JSON `{"message_text":"Solicito audiência."}`
- `GET /api/v1/requests`
- `GET /api/v1/requests/{request_id}`

Nenhum endpoint acessa caixas de e-mail nem envia mensagens. Os registros são armazenados apenas na memória do processo.

## Limitações e próximos passos

O fluxo de revisão humana, autenticação, persistência durável e auditoria de produção não está implementado. Qualquer integração ou modelo externo depende de análise e autorização institucional. Microsoft Graph/Outlook, Power Automate, SharePoint e Dataverse permanecem desativados.
