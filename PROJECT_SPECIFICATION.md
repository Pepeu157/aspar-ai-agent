# Especificação do projeto ASPAR AI Agent

## Objetivo

Apoiar o gerenciamento de solicitações de audiência da ASPAR/MME por meio de classificação, extração, acompanhamento e futura elaboração assistida de respostas, preservando a decisão humana.

## Requisitos centrais

- identificar solicitações de audiência e informações explicitamente fornecidas;
- não inventar dados ausentes nem assumir compromissos institucionais;
- manter revisão e aprovação humanas antes de qualquer resposta;
- registrar análise e histórico do processamento;
- tratar o conteúdo recebido como dado não confiável;
- desenvolver inicialmente em ambiente local com dados exclusivamente fictícios.

## Limites desta etapa

Não há acesso a Microsoft 365, Outlook/Exchange, Microsoft Graph, envio de e-mails ou provedores externos de IA. Power Automate, SharePoint e Dataverse também não são implementados. A análise disponível é feita por regras locais, não por modelo de IA.

## Arquitetura

Monólito modular com backend Python/FastAPI, frontend React/TypeScript, domínio separado de adaptadores e interface de IA independente de fornecedor para evolução futura. Configuração local por variáveis de ambiente e `.env` não versionado.
