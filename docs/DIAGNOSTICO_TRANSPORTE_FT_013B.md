# Diagnóstico de transporte — FT-013B

## Escopo

O módulo calcula três testes de triagem adimensionais para uma medição já definida: Weisz–Prater, Mears de transferência externa de massa e Mears térmico. Ele não estima entradas ausentes e não certifica cinética intrínseca.

## Equações e unidades canônicas

- Weisz–Prater: `C_WP = r_obs R_p² / (C_As D_eff)`.
- Mears de massa: `C_MM = n r_obs R_p / (k_c C_Ab)`.
- Mears térmico: `C_MH = |ΔH| r_obs R_p E_a / (h R T²)`.

As entradas usam SI: `r_obs` em mol m⁻³ s⁻¹, `R_p` em m, concentrações em mol m⁻³, difusividade em m² s⁻¹, `k_c` em m s⁻¹, energias em J mol⁻¹, `h` em W m⁻² K⁻¹ e temperatura em K. A taxa e as propriedades precisam usar bases fisicamente consistentes com a geometria e o critério avaliado.

O perfil `conservative-screening-v1` registra os limites operacionais adotados pela plataforma: 0,3 para Weisz–Prater e 0,15 para cada critério de Mears. Esses números são parâmetros versionados de triagem, não constantes universais.

## Estados e bloqueios

- `passed`: valor calculado estritamente abaixo do limite configurado;
- `failed`: valor igual ou superior ao limite;
- `not_assessable_missing_inputs`: cálculo não realizado porque faltam entradas;
- `incomplete`: ao menos um critério não foi avaliado;
- `passed_all_assessed`: os três testes passaram;
- `failed`: ao menos um teste calculado reprovou.

Mesmo com três testes aprovados, `kinetic_interpretation_approved` permanece falso e `recommendation_blocked` permanece verdadeiro. Revisão humana, consistência das bases, qualidade das propriedades e outros diagnósticos continuam necessários.

## Sensibilidade e proveniência

`relative_uncertainty_fraction` aceita incertezas relativas entre 0 e 1 para entradas preenchidas. O relatório propaga extremos independentes e informa se o intervalo cruza o limite. Essa faixa é sensibilidade conservadora, não distribuição de probabilidade.

Cada entrada preenchida exige uma chave correspondente em `field_sources`, e o contrato exige ao menos um `source_id`. O exemplo fornecido é sintético e não constitui evidência experimental.

## Referências metodológicas

- Weisz, P. B.; Prater, C. D. *Interpretation of Measurements in Experimental Catalysis*. Advances in Catalysis 6 (1954), 143–196. DOI: 10.1016/S0360-0564(08)60390-9.
- Mears, D. E. *Tests for Transport Limitations in Experimental Catalytic Reactors*. Industrial & Engineering Chemistry Process Design and Development 10 (1971), 541–547. DOI: 10.1021/i260040a020.
- Mears, D. E. *Diagnostic Criteria for Heat Transport Limitations in Fixed Bed Reactors*. Journal of Catalysis 20 (1971), 127–131. DOI: 10.1016/0021-9517(71)90073-X.

## Execução

```powershell
python tools/calculate_transport_diagnostics.py --input examples/diagnostico_transporte_sintetico.json --output output/diagnostico_transporte.json
```
