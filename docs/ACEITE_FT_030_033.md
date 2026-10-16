# Aceite FT-030 a FT-033

## FT-030 — bloqueio cruzado

O roteamento HTFT rejeita temperatura LTFT, família Co, contrato incompleto e
qualquer tentativa de remover `recommendation_blocked`. A porta de evidência
permite apenas comparação contextual quando regime e família são compatíveis;
ela sempre retorna `ltft_model_allowed=false` e
`automatic_calibration_allowed=false`.

## FT-031 — corpus HTFT inicial

O corpus dedicado contém oito registros da Tabela 1 de Liu et al. (2019), DOI
[10.1039/C9SC01210A](https://doi.org/10.1039/C9SC01210A), para catalisadores de
Fe em 350 °C, 1 bar, CO/H2 = 1, GHSV 12 000 mL h-1 gcat-1 e 60 h. Foram
registrados conversão de CO, CO2, CH4, olefinas e parafinas C2–C4, C5+ e O/P.
O auditor verifica cabeçalho, envelope HTFT, fechamento dos hidrocarbonetos,
duplicidade, manifesto e hash. Os oito registros fecham em 100% na base de
carbono dos hidrocarbonetos.

O uso aprovado é interno e contextual. O corpus não pode calibrar modelos,
produzir ranking universal nem recomendar condições. A licença deve ser
confirmada antes de redistribuição externa do CSV.

## FT-032 — balanços HTFT

O contrato `ft-htft-balance-v1` e o módulo `htft_balance.py` calculam fechamento
C/H/O com CO, H2, CO2, água, CH4, hidrocarbonetos agregados, oxigenados, carbono
em coque e fração não identificada. O resultado somente recebe `closed` quando
CO2, água e coque foram medidos, a fração não identificada é zero e os três
elementos ficam dentro da tolerância. Dados ausentes, espécie não suportada,
fluxo negativo ou regime LTFT impedem o fechamento.

A entrega é infraestrutura validada com exemplo sintético. Balanços de um ensaio
real dependerão de fluxos e análises medidos.

## FT-033 — interface HTFT controlada

A seleção HTFT mostra alvo C2–C4, quantidade de registros do corpus, contrato
analítico e bloqueio da recomendação. Na etapa de condições, a interface declara
que ASF é referência matemática e que conversão, O/P, WGS, coque e balanços
dependem de medição. O resultado HTFT repete essa fronteira e não apresenta a
curva como seletividade validada.

As quatro atividades preservam `recommendation_blocked=true`. Elas não concluem
validação quantitativa HTFT, que pertence à FT-034.
