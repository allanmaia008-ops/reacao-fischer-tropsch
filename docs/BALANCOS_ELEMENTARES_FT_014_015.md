# Balanços elementares — FT-014 e FT-015

## Objetivo

Verificar o fechamento molar de carbono, hidrogênio e oxigênio entre correntes
de entrada e saída declaradas, com base de medição, espécies, fontes e tolerância
explicitamente registradas.

## Contrato

O contrato `ft-elemental-balance-v1` recebe:

- vazões molares por espécie na entrada e na saída, em `mol/s`;
- composição atômica C/H/O de cada espécie;
- base de medição de cada corrente: `wet_total`, `dry_gas` ou
  `hydrocarbon_only`;
- tolerância percentual configurável;
- incertezas-padrão opcionais das vazões molares de cada espécie;
- identificadores das medições ou do conjunto de demonstração.

Entrada e saída devem usar a mesma base. Espécies sem composição atômica são
rejeitadas, evitando que carbono ou heteroátomos desapareçam silenciosamente.

## Cálculo

Para cada elemento `E`:

```text
F_E = soma(F_i × número de átomos E na espécie i)
fechamento (%) = F_E,saída / F_E,entrada × 100
desvio absoluto (%) = |F_E,saída − F_E,entrada| / F_E,entrada × 100
```

As incertezas das vazões são propagadas por soma em quadratura para cada fluxo
atômico e para o residual. A incerteza do fechamento usa a propagação de uma
razão para grandezas independentes. Correlações entre medições não são
inferidas; quando forem relevantes, devem ser fornecidas por um modelo
analítico posterior.

O balanço é aceito quando o desvio é menor ou igual à tolerância. C pode ser
avaliado em bases seca ou de hidrocarbonetos quando as duas correntes usam a
mesma base e todas as espécies carbonadas foram incluídas. H e O recebem
`not_assessable_on_dry_basis` fora de `wet_total`, porque excluir água torna o
fechamento total desses elementos incompleto.

## Execução reproduzível

```powershell
py tools\calculate_elemental_balance.py `
  --input examples\balanco_elementar_demonstracao.json `
  --output outputs\balanco_elementar_demonstracao.json
```

O exemplo é sintético e existe para verificar o cálculo; não é evidência
experimental. O relatório não calcula conversão, cinética ou seletividade e não
aprova a qualidade do método analítico.

## Aceite

- FT-014: fechamento de carbono, residual, desvio e tolerância configurável;
- FT-015: fechamento de H/O, espécies e bases documentadas, com bloqueio em
  base seca;
- contrato JSON, exemplo, ferramenta de linha de comando e testes positivos e
  negativos incluídos;
- resultado reproduzível e sem preenchimento de correntes ausentes.
