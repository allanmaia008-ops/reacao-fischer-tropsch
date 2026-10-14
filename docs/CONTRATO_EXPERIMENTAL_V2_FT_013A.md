# Contrato experimental v2 — FT-013A

## Objetivo

Estender o caso Fischer–Tropsch existente com as informações necessárias para
reprodutibilidade, revisão experimental e futuros diagnósticos de transporte.

O contrato é separado de `ft-case-v2`: o primeiro continua responsável pelo
caso científico e pelo regime; `ft-experimental-protocol-v2` registra detalhes
do aparato, ativação e análise.

## Blocos adicionais

### Reator e leito

- diâmetro interno e comprimento aquecido;
- porosidade do leito;
- tamanho das partículas de catalisador e diluente;
- massa de catalisador, diluente e razão mássica de diluição.

### Ativação

- composição e vazão do gás;
- temperatura, taxa de aquecimento, patamar e pressão.

### Análise

- detectores e faixas por espécie;
- protocolo de calibração;
- limites de detecção e quantificação;
- método e recuperação da fração pesada.

Cada campo preenchido exige uma entrada em `field_sources`. O contrato mantém
`recommendation_blocked=true`.

## Migração

```powershell
py tools\migrate_experimental_protocol.py `
  --input examples\caso_experimental_completo.json `
  --output outputs\protocolo_experimental_v2_migrado.json `
  --protocol-id FT-013A-DEMO `
  --source-id synthetic-migration-not-evidence
```

A migração preserva o caso de origem e inicializa todos os campos novos como
`null`. Nenhuma dimensão, condição de ativação ou capacidade analítica é
inventada.

## Prontidão

- `structurally_valid`: contrato e valores fornecidos são coerentes;
- `ready_for_transport_assessment`: todos os campos novos estão presentes e
  rastreados;
- `ready_for_experimental_execution_review`: o protocolo planejado pode seguir
  para revisão humana, não para execução autônoma.

Os exemplos completos são explicitamente sintéticos e existem apenas para
testes do software.
