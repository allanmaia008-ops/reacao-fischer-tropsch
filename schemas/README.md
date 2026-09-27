# Esquemas v1

- `ltft-case-v1.schema.json`: entrada científica e experimental.
- `ltft-evidence-v1.schema.json`: envelope de uma evidência rastreável.
- `ltft-result-v1.schema.json`: saída do worker.

As unidades fazem parte dos nomes dos campos (`_c`, `_bar`, `_mol_s`, `_h_1`,
`_g`, `_ml`, `_wt_pct`). O JSON Schema valida forma e limites simples; as regras
cruzadas — soma da alimentação, consistência H2/CO, pares GHSV/volume e WHSV/massa,
promotor/carga — são aplicadas por `validate_case`.

Versão atual: `1.0.0`. Alterações incompatíveis exigem nova versão principal e
migração explícita; arquivos antigos não devem ser reinterpretados silenciosamente.
