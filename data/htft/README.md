# Corpus HTFT separado

Nenhum CSV LTFT é reutilizado automaticamente. O primeiro dataset aprovado para
uso interno contextual é `htft_liu_2019_light_olefins.csv`; sua proveniência e
restrições constam em `manifest.json`. Ele sustenta comparação contextual e teste
do contrato, sem calibração automática, ranking ou recomendação.

Novas entradas devem registrar origem, licença, condições, catalisador/fase,
base analítica, oxigenados, coque e reações secundárias antes da revisão.

## Validação FT-034

`htft_ahmed_2021_temperature_holdout.csv` mantém calibração (300 °C) e holdout
(320 °C) separados para os mesmos quatro catalisadores. `validation_manifest.json`
registra licença, hash, compatibilidade e a limitação de mesmo estudo. Os
artefatos em `validation/` congelam o benchmark, apresentam métricas e resíduos
e mantêm o pedido de revisão independente. O modelo v1 falhou nos critérios de
conversão e seletividade a olefinas C2–C4 e não pode recomendar condições.

`ft034_theses_dissertations_catalog.csv` registra teses e dissertações sem
promover valores de resumo a dados de validação antes da extração completa.
