# Contrato científico LTFT v1

## Níveis de prontidão

- `valid_for_screening`: composição, família/fase, suporte, carga, temperatura,
  pressão, H2/CO e produto-alvo estão completos e consistentes.
- `valid_for_experimental_plan`: além da triagem, registra precursor, ativação,
  reator, composição/vazão da alimentação, tempo em operação e uma base de
  velocidade espacial (`GHSV + volume do leito` ou `WHSV + massa de catalisador`).
- `valid_for_rate_calculation`: permanece falso até existirem equação de taxa,
  parâmetros, unidades, incertezas, conversão medida e balanço de carbono.

## Unidades canônicas

| Sufixo | Unidade |
|---|---|
| `_wt_pct` | porcentagem em massa |
| `_c` | grau Celsius |
| `_bar` | bar absoluto |
| `_mol_fraction` | fração molar, soma 1,0 |
| `_mol_s` | mol por segundo |
| `_h_1` | inverso de hora |
| `_g` | grama |
| `_ml` | mililitro |
| `_h` | hora |

## Regras condicionais

- promotor e carga do promotor são informados juntos;
- GHSV exige volume do leito e vice-versa;
- WHSV exige massa do catalisador e vice-versa;
- a alimentação contém H2 e CO e suas frações somam 1,0;
- a razão H2/CO declarada deve coincidir com a alimentação dentro de 2%;
- cargas de metal ativo e promotor não podem superar juntas 100% em massa;
- versões incompatíveis são rejeitadas.

O contrato valida completude e consistência. Ele não comprova que uma condição é
segura, ótima ou experimentalmente adequada.

