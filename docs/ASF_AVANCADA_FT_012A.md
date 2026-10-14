# ASF avançada — FT-012A

## Modelos implementados

- `single`: reproduz exatamente a ASF de alpha único já existente;
- `dual_mixture`: combinação convexa de duas distribuições ASF completas, com
  `mixture_fraction` explícita;
- `segmented`: ramo leve com `alpha_1` e ramo pesado ancorado no carbono de
  transição, normalizado analiticamente até C infinito.

Os fatores opcionais de metano e C2 são aplicados separadamente e a
distribuição é renormalizada. Eles não são reinterpretados como probabilidades
de crescimento.

## Garantias matemáticas

- fechamento incluindo a cauda infinita;
- frações físicas independentes de `max_carbon`, que controla apenas a janela
  materializada;
- cauda calculada analiticamente, sem truncamento silencioso;
- compatibilidade exata do modelo `single` com `asf.py`;
- validação condicional de parâmetros por tipo de modelo.

## Execução

```powershell
py tools\calculate_advanced_asf.py `
  --input examples\asf_avancada_dual_sintetica.json `
  --output outputs\asf_avancada_dual_sintetica.json `
  --max-carbon 40
```

O exemplo é sintético. Os parâmetros não foram ajustados a experimentos e não
devem orientar catalisador ou condições operacionais.

## Limite

A FT-012A disponibiliza modelos matemáticos; ajuste, seleção e alegação de
superioridade pertencem à FT-017A e exigem dados aprovados.
