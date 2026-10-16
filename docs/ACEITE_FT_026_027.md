# Aceite FT-026 e FT-027

Atualização 2026-10-16: FT-027 exige também origem de experimento do projeto,
data válida, hash, atestado de conferência, revisor e relatório comparativo.
Execução real ainda pendente; ver [evidências](FT024_FT027_EVIDENCIAS.md).

FT-026 agora gera um plano experimental em estado `draft`, com checklist de contrato, transporte, segurança e analytics. A revisão humana é obrigatória e `recommendation_blocked` permanece verdadeiro.

FT-027 agora valida registros de piloto. Um registro só pode ser `measured_record` se possuir identificador, protocolo, data de execução, método analítico, URI dos dados brutos e confirmação explícita de execução. A implementação não cria dados de laboratório.
