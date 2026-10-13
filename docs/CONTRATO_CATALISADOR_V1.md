# Contrato de catalisador v1

## Finalidade

O contrato `ft-catalyst-v1` descreve um **lote identificável** de catalisador e
separa composição nominal, preparação, ativação, caracterização, fase ativa e
proveniência. Ele não atribui desempenho catalítico e não transforma uma fase
inferida ou hipotética em fase medida.

## Identidade e composição

Cada registro exige `catalyst_id`, `batch_id`, nome, família ativa, composição
nominal, precursor, suporte e carga mássica. As famílias iniciais são `Co`, `Fe`
e `Co-Fe`. Um sistema `Co-Fe` é exploratório e exige hipótese científica
explícita.

Promotores são registros separados, com nome, carga e precursor opcional. A
soma das cargas de metal ativo e promotores não pode superar 100% em massa, mas
essa verificação não substitui um balanço completo de preparação.

## Preparação e ativação

O método e ao menos uma etapa de preparação são obrigatórios. Cada etapa possui
nome, descrição e, quando disponíveis, temperatura, duração e atmosfera. A
ativação registra gás, temperatura e duração.

O contrato registra o procedimento informado. Ele não verifica sozinho se o
protocolo é seguro ou suficiente para formar a fase desejada.

## Fase ativa e caracterização

`active_phase.status` distingue:

- `medida`: exige pelo menos um identificador de evidência;
- `inferida`: interpretação baseada em evidência, sem equivaler a medição direta;
- `hipotetica`: hipótese a confirmar.

Caracterizações são referenciadas por identificadores de evidência, preservando
a separação entre o cadastro do lote e os arquivos/resultados analíticos.

## Proveniência

Todo lote registra tipo e referência da fonte, licença/condição de uso, curador
e data. Registros legados continuam identificados como legado e não são
promovidos automaticamente a evidência aprovada.

## Implementação e exemplos

- schema: `schemas/ft-catalyst-v1.schema.json`;
- regras cruzadas: `src/plataforma_ltft/catalyst.py`;
- exemplos: `examples/catalisador_co_v1.json`,
  `examples/catalisador_fe_v1.json` e
  `examples/catalisador_co_fe_exploratorio_v1.json`;
- testes: `tests/test_catalyst.py` e `tests/test_schemas.py`.

Os exemplos são demonstrativos e não constituem receitas experimentais,
recomendação de catalisador ou evidência de desempenho.
