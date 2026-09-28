# Contrato científico Fischer–Tropsch v2

## Classificação de regime

O contrato v2 exige `ft_regime` e `regime_envelope_version`:

| Temperatura | Classificação do envelope 1.0.0 |
|---:|---|
| 180–260 °C, inclusive | `LTFT` |
| maior que 260 e menor que 280 °C | `transicao` |
| 280–350 °C, inclusive | `HTFT` |

O envelope serve para roteamento da plataforma; não é um limite físico
universal. A faixa de transição exige `regime_justification`. Valores fora do
envelope são rejeitados até existir estudo e versão específicos.

## Compatibilidade

- casos v1 entre 180 e 260 °C podem ser migrados deterministicamente para LTFT;
- v1 fora de LTFT não é reinterpretado: exige revisão e contrato v2;
- HTFT aceita inicialmente a família Fe; expansão requer evidência e nova decisão;
- parâmetros LTFT não podem ser usados em HTFT;
- toda saída mantém `recommendation_blocked: true` enquanto não houver validação.

## Arquivos

- `schemas/ft-case-v2.schema.json` — entrada v2;
- `schemas/ft-result-v2.schema.json` — saída e bloqueio científico;
- `examples/caso_htft_v2.json` — exemplo HTFT de preparação;
- `examples/caso_transicao_v2.json` — exemplo com justificativa;
- `docs/CONTRATO_V1.md` — contrato legado preservado.
