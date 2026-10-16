# Aceite FT-024 e FT-025

Atualização 2026-10-16: FT-024 dispõe de modelo exploratório ajustado a dados publicados,
avaliação holdout e intervalos; validação externa continua pendente. Ver
[relatório de evidências](FT024_FT027_EVIDENCIAS.md). O texto abaixo descreve a porta original.

FT-024 implementa a porta `quantitative_readiness`: nenhum cálculo de taxa é liberado sem contrato cinético validado, validação externa e método de incerteza.

FT-025 implementa sensibilidade local one-at-a-time, registrando valor basal, perturbação, resposta, derivada local e se o ponto permanece na faixa declarada.

As duas saídas mantêm `recommendation_blocked=true`. A FT-024 permanece bloqueada até existirem dados cinéticos aprovados; a implementação não infere conversão a partir de temperatura e pressão.
