# Esquemas v1 e v2

- `ltft-case-v1.schema.json`: entrada científica e experimental.
- `ltft-evidence-v1.schema.json`: envelope de uma evidência rastreável.
- `ltft-result-v1.schema.json`: saída do worker.
- `ft-case-v2.schema.json`: caso com regime LTFT, transição ou HTFT.
- `ft-result-v2.schema.json`: resultado com bloqueio científico explícito.
- `ft-catalyst-v1.schema.json`: lote, preparação, ativação, fase e proveniência do catalisador.
- `ft-kinetic-model-v1.schema.json`: equação cinética, parâmetros, unidades,
  domínio, fontes, incerteza e estado de calibração/validação.
- `ft-reactor-v1.schema.json`: alimentação, geometria, base espacial e modelos
  físicos exigidos pelo primeiro reator LTFT.
- `ft-thermodynamics-v1.schema.json`: pacote, EOS, mistura, pseudocomponentes,
  VLE, cobertura de fases, domínio e validação termodinâmica.
- `ft-elemental-balance-v1.schema.json`: correntes molares, composição atômica,
  base de medição, fontes e tolerância para balanços C/H/O.
- `ft-asf-measurement-v1.schema.json`: distribuição medida, base analítica,
  incerteza, proveniência e estado de aprovação para comparação com ASF.
- `ft-advanced-asf-v1.schema.json`: ASF simples, mistura de duas ASF ou modelo
  segmentado, com correções C1/C2 explicitamente separadas.
- `ft-experimental-protocol-v2.schema.json`: extensão experimental com leito,
  partículas, diluição, ativação completa, analytics e fontes por campo.
- `ft-transport-diagnostics-v1.schema.json`: entradas SI, proveniência,
  incerteza e limites versionados para Weisz–Prater e Mears.

As unidades fazem parte dos nomes dos campos (`_c`, `_bar`, `_mol_s`, `_h_1`,
`_g`, `_ml`, `_wt_pct`). O JSON Schema valida forma e limites simples; as regras
cruzadas — soma da alimentação, consistência H2/CO, pares GHSV/volume e WHSV/massa,
promotor/carga — são aplicadas por `validate_case`.

Versão atual do caso: `2.0.0`. Casos LTFT v1 continuam aceitos pelo worker por
migração explícita e determinística; transição e HTFT exigem o contrato v2.
