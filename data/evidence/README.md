# Evidência LTFT importada

Origem material dos arquivos: checkout histórico local, commit de referência
`ef6b053`, copiado em 2026-09-16.

- `ltft_kinetic_equations_provenance.csv`: proveniência e limites de equações.
- `ltft_mello_2017_selectivity.csv`: dados de seletividade atribuídos à referência.
- `ltft_mello_2017_supports.csv`: relações de suportes atribuídas à referência.
- `ft024_contextual_partial_measurements.csv`: 61 medições parciais contextuais,
  mantendo qualificadores de faixa, limite e aproximação.
- `ft024_partial_source_catalog.csv`: catálogo de 17 fontes coletadas e estado de
  extração numérica.
- `ft024_cobalt_cerium_database.xlsx`: planilha consolidada; as abas
  `Evidência parcial` e `Fontes parciais` mantêm os novos dados separados das
  medições de calibração.

Importar estes CSVs não transforma as observações em parâmetros universais nem
autoriza transferência direta para outra composição ou condição. Antes de usá-los
no runtime, a plataforma deverá validar esquema, unidades, referência, licença,
condições experimentais e compatibilidade com o caso analisado.

Enquanto a licença não estiver verificada, os CSVs permanecem fora do repositório
público. Este README e o manifesto registram apenas o estado de governança.

Os CSVs parciais são de uso interno do projeto. Nenhuma linha nova recebeu
`external_validation_eligible=true`; valores provenientes de resumos ou metadados
não substituem a verificação das tabelas no texto integral.
