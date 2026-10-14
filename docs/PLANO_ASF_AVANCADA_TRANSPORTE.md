# Plano de ASF avançada, contrato experimental v2 e transporte

## Decisão

As melhorias foram aprovadas para o planejamento em 2026-10-13. A ASF de
alpha único permanece como referência matemática. Modelos avançados serão
alternativas comparadas contra essa referência, nunca substituições presumidas.

Valores numéricos apresentados em exemplos externos não são condições
experimentais aprovadas e não serão promovidos a defaults da plataforma.

## FT-012A — ASF avançada

**Objetivo:** representar desvios da ASF ideal sem impor uma interpretação
mecanicista não demonstrada.

**Implementação planejada:**

- contrato versionado para ASF simples, mistura de duas ASF e modelo segmentado;
- parâmetros `alpha_1`, `alpha_2`, fração de mistura e, quando aplicável, ponto
  de transição explicitamente declarado;
- correções opcionais de C1 e C2 separadas dos parâmetros de crescimento;
- normalização independente do limite de visualização;
- cauda infinita calculada analiticamente;
- testes de fechamento, continuidade aplicável, limites e identificabilidade;
- proveniência, método de ajuste, covariância e domínio registrados.

**Aceite:** resultados reproduzíveis; soma total igual a 1 dentro da tolerância;
alterar `max_n` não altera as frações físicas; nenhuma variante é chamada de
superior sem comparação com dados aprovados.

## FT-013A — Contrato experimental v2

**Objetivo:** ampliar o caso planejado para avaliação de reprodutibilidade e de
transporte.

**Campos planejados:**

- diluente sólido, razão mássica e granulometria;
- tamanho e distribuição das partículas do catalisador;
- diâmetro interno, comprimento útil e porosidade do leito;
- taxa de aquecimento, vazão, composição e pressão de ativação;
- detectores, faixas por espécie, calibração, limites de detecção/quantificação;
- método e recuperação da fração pesada;
- fonte e estado de evidência de cada valor crítico.

**Aceite:** migração explícita do contrato atual; exemplos positivos e
negativos; campos ausentes permanecem ausentes, sem valores arbitrários; o caso
continua rotulado como planejamento até confirmação da execução.

## FT-013B — Diagnóstico de transporte

**Objetivo:** avaliar se uma medição pode sustentar interpretação cinética.

**Implementação planejada:**

- critérios de Weisz–Prater, Mears de massa e Mears térmico;
- entradas, unidades, equações, limites e fontes versionados;
- estados `passed`, `failed` e `not_assessable_missing_inputs`;
- cálculo proibido quando taxa observada, dimensão de partícula, propriedades
  de transporte ou demais entradas exigidas estiverem ausentes;
- análise de sensibilidade às propriedades estimadas;
- separação entre verificação calculada e declaração do operador.

**Aceite:** casos de referência independentes, testes de unidade/dimensão e
mensagens que não confundam ausência de dados com ausência de limitação.

## FT-017A — Ajuste e seleção do modelo ASF

**Objetivo:** comparar ASF simples e variantes avançadas na mesma base e dentro
do domínio de dados aprovado.

**Implementação planejada:**

- ajuste reproduzível com separação entre calibração e avaliação;
- MAE, RMSE, qui-quadrado, AIC/BIC e resíduos por número de carbono/corte;
- incerteza dos parâmetros, covariância e diagnóstico de identificabilidade;
- análise específica de C1, C2 e cauda pesada;
- relatório de seleção que possa concluir “evidência insuficiente”;
- interface comparativa sem destacar Dual-alpha como superior por padrão.

**Dependências:** FT-012A, FT-017 e ao menos um conjunto aprovado por FT-021.

**Aceite:** modelo escolhido por critérios registrados e revisão humana; teste
fora do ajuste quando houver dados suficientes; recomendação experimental
permanece bloqueada.
