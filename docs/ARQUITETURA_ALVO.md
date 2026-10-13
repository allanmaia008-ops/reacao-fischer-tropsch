# Arquitetura-alvo

## Princípios

- domínio científico isolado da interface;
- LTFT e HTFT como módulos diferentes;
- contratos e APIs versionados;
- execução determinística e idempotente;
- rastreabilidade de dados, código, configuração e artefatos;
- serviços simples antes de microserviços;
- processamento pesado fora do processo web;
- segurança e auditoria por padrão.

## Organização sugerida

```text
apps/
  web/                    interface do usuário
services/
  api/                    API versionada
  worker/                 execuções assíncronas
packages/
  contracts/              schemas, unidades e migrações
  domain/                 entidades e regras comuns
  evidence/               ingestão, proveniência e revisão
  balances/               balanços C/H/O e qualidade
  ltft/                   ASF e modelos LTFT
  htft/                   métricas e modelos HTFT
  planning/               DOE e planos experimentais
  dft/                    estruturas, protocolos e parsers
  reporting/              JSON, CSV, notebook e relatório
data/
  fixtures/               dados sintéticos para testes
docs/
  decisions/              registros de decisão
  protocols/              protocolos científicos
tests/
  unit/
  integration/
  scientific/
  end_to_end/
infra/
  environments/           dev, homologação e produção
```

## Fluxo de execução

```text
Interface -> API -> validação do contrato -> criação de Run
                                      -> fila -> worker do regime
                                      -> artefatos e métricas
                                      -> relatório e trilha de auditoria
```

## Persistência

- PostgreSQL para entidades, versões, estados e auditoria;
- armazenamento de objetos para arquivos, relatórios, notebooks e resultados;
- fila para execuções demoradas;
- cache apenas para dados reconstruíveis;
- hashes para artefatos científicos relevantes;
- backups versionados e restauração testada.

## Estados de uma execução

`created -> validated -> queued -> running -> succeeded|failed|blocked|cancelled`

`blocked` representa uma porta científica ou entrada ausente, não erro técnico.

## API mínima

- `/projects`
- `/product-targets`
- `/cases`
- `/catalysts`
- `/evidence`
- `/experiments`
- `/models`
- `/runs`
- `/reports`
- `/dft`

Cada resposta inclui versão do schema e identificadores das dependências usadas.

## Observabilidade

- logs estruturados com `project_id`, `case_id`, `run_id` e versão;
- métricas de fila, duração, falhas e bloqueios;
- alertas de indisponibilidade, erro e atraso;
- registro separado de eventos científicos e eventos técnicos;
- sem segredos ou dados desnecessários em logs.

## Evolução recomendada

1. monólito modular com worker separado;
2. API e contratos estáveis;
3. persistência e autenticação;
4. separação de serviços somente quando carga ou equipe justificar;
5. DFT e computação externa por adaptadores.
