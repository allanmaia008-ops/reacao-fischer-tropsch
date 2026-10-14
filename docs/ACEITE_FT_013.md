# Aceite da FT-013 — caso experimental completo

## Objetivo

Representar de forma reproduzível um caso LTFT com catalisador e ativação,
reator, alimentação, velocidade espacial, condições operacionais e produto-alvo.

## Entregas

- `examples/caso_experimental_completo.json`: exemplo completo no contrato v1,
  migrado explicitamente para v2 pelo worker;
- `experimental_case_summary`: visão agrupada das entradas, estado de prontidão,
  impressão digital SHA-256 determinística e saídas experimentais ausentes;
- resultado do worker contém `experimental_case`, permitindo auditar exatamente
  quais entradas foram usadas;
- notebook 05 continua exercitando migração, validação e ASF condicional;
- testes cobrem completude, grupos, reprodutibilidade e ausência de resultados
  medidos inventados.

## Critério atendido

O caso registra:

- catalisador, hipótese de fase, suporte, promotor, precursor e ativação;
- tipo de reator;
- temperaturas de entrada e saída do leito para registrar o gradiente observado;
- H2/CO, composição e vazão molar da alimentação;
- GHSV com volume do leito, ou alternativamente WHSV com massa;
- temperatura, pressão, tempo em operação e produto-alvo.
- método analítico, número de replicatas e critério de estado estacionário.

## Limite científico

O exemplo é ilustrativo e recebe o estado
`planned_case_not_experimental_evidence`. A completude libera somente a porta de
planejamento. Conversão, produtividade, seletividade medida, cinética e
adequação de segurança permanecem ausentes ou bloqueadas. A execução em
laboratório exige protocolo real, revisão humana e aprovação de segurança.
