# Unidades canônicas — catálogo 1.0.0

## Finalidade

O módulo `plataforma_ltft.units` converte entradas compatíveis para as unidades
do contrato científico sem apagar o valor ou a unidade originais. O catálogo é
versionado por `UNIT_CATALOG_VERSION`.

## Catálogo normativo

| Grandeza | Unidade canônica | Unidades de entrada aceitas |
|---|---|---|
| temperatura | `degC` | `degC`, `K`, `degF` e aliases documentados no código |
| pressão absoluta | `bar` | `bar`, `Pa`, `kPa`, `MPa`, `atm` |
| tempo | `h` | `h`, `min`, `s`, `d` |
| vazão molar | `mol/s` | `mol/s`, `mmol/s`, `mol/min`, `mol/h`, `kmol/h` |
| inverso de tempo | `h^-1` | `h^-1`, `min^-1`, `s^-1` |
| massa | `g` | `g`, `mg`, `kg` |
| volume | `mL` | `mL`, `L`, `m3` e equivalentes registrados |
| fração mássica | `wt_pct` | `wt_pct`, fração mássica, `ppm_wt` |
| fração molar | `mol_fraction` | fração molar, `mol_pct`, `ppm_mol` |
| razão adimensional | `ratio` | `ratio` ou unidade `1` |

Os campos do contrato v2 estão associados explicitamente a essas grandezas por
`FIELD_QUANTITIES`. Isso impede, por exemplo, converter massa em volume ou
fração mássica em fração molar.

## Regras científicas

- todas as pressões do contrato são **absolutas**; `barg` não é aceito;
- conversão de vazão volumétrica para molar exige temperatura, pressão e modelo
  de gás, portanto não é feita por este catálogo;
- `GHSV` e `WHSV` compartilham dimensão de inverso de tempo, mas continuam sendo
  variáveis científicas distintas no contrato;
- converter uma unidade não altera base analítica, composição, incerteza nem
  qualidade da evidência;
- o registro canônico preserva `original_value`, `original_unit`, grandeza,
  valor canônico, unidade canônica e versão do catálogo;
- mudanças de definição exigem nova versão e testes de regressão.

## Uso

```python
from plataforma_ltft.units import canonicalize_field

pressure = canonicalize_field("pressure_bar", 2.0, "MPa")
assert pressure.canonical_value == 20.0
assert pressure.canonical_unit == "bar"
assert pressure.original_value == 2.0
assert pressure.original_unit == "MPa"
```

## Validação

Os testes cobrem temperaturas com deslocamento de escala, pressão absoluta,
tempo, inverso de tempo, vazão molar, massa, volume, bases de fração,
rastreabilidade da observação original e rejeição de unidade ou dimensão
incompatível.

