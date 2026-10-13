# Modelo de reator LTFT v1

## Estado atual

A infraestrutura do primeiro modelo de reator está implementada, mas a simulação
permanece bloqueada. O módulo registra alimentação molar, tipo e geometria do
reator, base GHSV ou WHSV, condições e os modelos físicos adotados. Ele calcula
somente o inventário da entrada, sem inferir extensão de reação ou saída.

## Tipos inicialmente previstos

- `fixed_bed_pfr`: leito fixo tratado futuramente como reator tubular;
- `slurry_cstr`: reator de lama tratado futuramente como mistura perfeita.

Cada implementação deve declarar tratamento de energia, queda de pressão,
transferência de massa, WGS e desativação, inclusive quando um fenômeno for
justificadamente não aplicável.

## Porta para simulação

A simulação só será liberada quando o contrato do reator estiver completo, a
cinética possuir estado `validated` e o pacote termodinâmico estiver validado.
Até lá, conversão, produtividade, extensão WGS e vazões de saída permanecem
indisponíveis. Isso evita transformar um integrador de EDO em falsa evidência.
