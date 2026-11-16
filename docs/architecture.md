# Arquitetura

## Forma

Monólito modular local. Separar módulos permite substituir armazenamento e análise sem acoplar as regras do domínio a FastAPI ou a um fornecedor.

## Módulos

- `backend/app/api`: endpoints e conversão de requisições HTTP.
- `backend/app/domain`: estados, validações e modelos de solicitação, análise, revisão e histórico.
- `backend/app/services`: porta `AIProvider` e regra local atual.
- `backend/app/repositories`: persistência substituível; hoje somente memória.
- `backend/app/core`: configuração de ambiente.
- `frontend`: painel web e cliente da API; inicia sem exemplos fictícios.
- `ai`: documentação da fronteira para futura IA.
- `integrations`: documentação das integrações opcionais, inativas.

## Análise local e futura IA

`LocalRulesProvider` é lógica determinística baseada em expressões regulares. Não é um LLM nem faz chamadas de rede. Classifica intenção explícita de solicitar audiência/reunião e se abstém diante de menção ambígua. Datas e horários só são aceitos em campos rotulados de sugestão/proposta e quando uma solicitação é explícita. Outros valores ausentes ficam nulos. A futura implementação de `AIProvider` requer avaliação e autorização; não está neste escopo.

## Segurança

A configuração lê variáveis do processo e `.env` local. O arquivo real `.env` é ignorado pelo Git e não são necessárias chaves. Não conectar contas institucionais ou serviços externos. Usar apenas dados fictícios. Conteúdo de mensagem nunca deve ser interpretado como instrução de sistema. Nenhuma operação de envio está implementada.

## Limitações e riscos

A classificação por regras tem falsos negativos/positivos e deve ser revisada por pessoa responsável. A persistência em memória perde dados ao reiniciar e não oferece controle de acesso ou auditoria durável. O endpoint atual armazena texto em memória; não usar dados reais. A aprovação humana está definida como requisito, mas o fluxo de aprovação ainda precisa ser implementado antes de qualquer implantação.
