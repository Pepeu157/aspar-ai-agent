# Camada de IA

Atualmente o backend utiliza `LocalRulesProvider`, análise determinística local. Não é um modelo de IA, não faz chamadas externas e não gera minuta. A interface `AIProvider` permite futura substituição por uma implementação aprovada, sem acoplar domínio ao fornecedor. Qualquer modelo real depende de avaliação de segurança, privacidade, qualidade e autorização institucional.
