# Aceite FT-022 e FT-023

As duas atividades foram implementadas em `src/plataforma_ltft/applicability.py`.

- FT-022 compara família catalítica, regime térmico, pressão, razão H₂/CO e estado de aprovação do corpus.
- FT-023 emite alertas para temperatura fora de LTFT, família fora do contexto, pressão ou razão H₂/CO fora das faixas declaradas.
- Toda saída mantém `recommendation_blocked=true`.
- Compatibilidade contextual não é tratada como transferência quantitativa.

Os testes cobrem o bloqueio pelo corpus ainda não aprovado e a detecção de um caso HTFT fora do domínio LTFT.
