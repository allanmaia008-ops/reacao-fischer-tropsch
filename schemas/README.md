# Esquemas v1 e v2

- `ltft-case-v1.schema.json`: entrada científica e experimental.
- `ltft-evidence-v1.schema.json`: envelope de uma evidência rastreável.
- `ltft-result-v1.schema.json`: saída do worker.
- `ft-case-v2.schema.json`: caso com regime LTFT, transição ou HTFT.
- `ft-result-v2.schema.json`: resultado com bloqueio científico explícito.

As unidades fazem parte dos nomes dos campos (`_c`, `_bar`, `_mol_s`, `_h_1`,
`_g`, `_ml`, `_wt_pct`). O JSON Schema valida forma e limites simples; as regras
cruzadas — soma da alimentação, consistência H2/CO, pares GHSV/volume e WHSV/massa,
promotor/carga — são aplicadas por `validate_case`.

Versão atual do caso: `2.0.0`. Casos LTFT v1 continuam aceitos pelo worker por
migração explícita e determinística; transição e HTFT exigem o contrato v2.
