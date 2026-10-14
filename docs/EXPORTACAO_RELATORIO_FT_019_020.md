# Exportação e relatório científico — FT-019 e FT-020

## FT-019 — exportação JSON/CSV

O módulo `reporting.py` transforma um resultado já calculado em quatro arquivos:

- `resultado_ft_v1.json`: resultado completo, incluindo valores nulos e bloqueios;
- `resumo_ft_v1.csv`: uma linha com versão, fingerprint, caso e resultado-alvo;
- `faixas_asf_v1.csv`: tabela longa das faixas ASF;
- `manifesto_exportacao_v1.json`: SHA-256, tipo e tamanho de cada artefato.

A serialização é canônica e não inclui relógio, caminho local ou identificador aleatório. O mesmo resultado produz os mesmos bytes e hashes. CSV usa cabeçalho estável, UTF-8 com BOM e ponto decimal, adequado à leitura por máquina. O contrato do manifesto é `1.0.0`.

## FT-020 — relatório científico

O relatório Markdown inclui:

- versão e SHA-256 do resultado;
- objetivo e escopo;
- premissas operacionais e do modelo;
- resultados ASF e saídas deliberadamente não calculadas;
- fontes anexadas ou declaração explícita de ausência;
- prontidão, campos ausentes, limitações e bloqueio de recomendação.

O relatório não transforma uma simulação em evidência experimental. Sem `source_ids`, registra que nenhuma fonte experimental aprovada está anexada. Conversão e produtividade ausentes aparecem como “não calculada”, nunca como zero.

## Interface e execução independente

A aba **Resultados** oferece downloads do JSON, dos dois CSVs, do relatório e do manifesto. Os mesmos artefatos podem ser gerados sem Streamlit:

```powershell
py -m pip install -e .
py -m plataforma_ltft.worker --config examples\caso_co.json --output outputs\caso_co
py tools\export_result_bundle.py --input outputs\caso_co\resultado_ft.json --output outputs\caso_co\exportacao
py tools\generate_scientific_report.py --input outputs\caso_co\resultado_ft.json --output outputs\caso_co\relatorio_cientifico_ft_v1.md
```

## Critérios de aceite verificados

- repetição da exportação produz bytes idênticos;
- hashes do manifesto conferem com os arquivos;
- JSON preserva nulos e faz round-trip;
- CSV é parseável e contém versão e bloqueio;
- relatório contém premissas, lacunas de evidência e limitações;
- resultado incompleto é rejeitado;
- downloads aparecem apenas depois de existir resultado calculado.
