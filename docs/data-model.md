# Modelo de dados inicial

Os modelos Pydantic em `backend/app/domain/models.py` cobrem as entidades:

- **RequestRecord:** UUID, mensagem de entrada, classificação, status, análise, revisões humanas, eventos e timestamps.
- **AIAnalysis:** origem/versão da análise, classificação, campos extraídos, avisos e data.
- **ExtractedFields:** remetente, e-mail, instituição, assunto, solicitação, data/hora sugeridas, participantes, contexto, termos técnicos e resposta sugerida. Ausências escalares são `null`; listas não identificadas são vazias. Minuta permanece nula nesta fundação.
- **HumanReview:** ator, ação, comentários e timestamp; estrutura de domínio, sem endpoint de aprovação nesta etapa.
- **AuditEvent:** evento, ator, referência, detalhes e timestamp.

Entrada não pode ser vazia e é limitada a 20.000 caracteres. E-mail, data ISO e horário são validados. O repositório atual é em memória, sem persistência durável.
