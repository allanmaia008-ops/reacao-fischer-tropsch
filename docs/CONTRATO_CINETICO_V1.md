# Contrato cinético Fischer–Tropsch v1

## Finalidade

O contrato define o que deve acompanhar qualquer equação de taxa antes de sua
integração ao futuro modelo de reator. Ele não fornece uma cinética padrão e não
autoriza estimar conversão apenas com temperatura, pressão ou identidade do metal.

## Campos obrigatórios

- `model_id`, `model_version` e `rate_expression` identificam o modelo;
- `variables` registra variáveis e unidades, incluindo temperatura e pressões
  parciais de H2 e CO;
- `parameters` e `parameter_units` mantêm valor e dimensão de cada parâmetro;
- `applicability_domain` declara regime FT, intervalos de temperatura e pressão
  e família catalítica coberta;
- `source_ids` aponta para publicações ou conjuntos de evidência rastreáveis;
- `uncertainty_method` declara como a incerteza foi obtida;
- `validation_dataset_ids` registra dados independentes de validação;
- `calibration_status` distingue `draft`, `calibrated` e `validated`.

O arquivo normativo é `schemas/ft-kinetic-model-v1.schema.json`. A validação
semântica complementar fica em `src/plataforma_ltft/kinetics.py`.

## Porta para cálculo de taxa

`valid_for_rate_calculation` só pode ser verdadeiro quando o contrato está
completo, o estado é `validated` e há conjunto de validação identificado. Um
contrato `draft` pode ser cadastrado e auditado, mas permanece bloqueado para
cálculo. Parâmetros ausentes não devem ser preenchidos por valores arbitrários.

## Domínio e extrapolação

O consumidor deve verificar todas as dimensões do domínio, não apenas a faixa de
temperatura. Uso fora da família catalítica, composição, pressão ou domínio do
conjunto calibrado é extrapolação e exige nova avaliação científica.
