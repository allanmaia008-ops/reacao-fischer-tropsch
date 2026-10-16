# Aceite FT-034 a FT-037

## Resultado

As quatro atividades agora têm contratos executáveis, schemas versionados,
exemplos e testes. O estado científico de cada entrega permanece explícito.

| Atividade | Entrega | Estado científico |
|---|---|---|
| FT-034 | porta de validação HTFT com modelo congelado, conjunto externo, métricas, incerteza, resíduos e parecer independente | **PORTA IMPLEMENTADA / BLOQUEADA**: ainda não existe modelo HTFT quantitativo congelado, conjunto externo compatível aprovado nem parecer independente |
| FT-035 | contrato estrutural com célula, sítios, periodicidade, carga, spin, arquivo, hash e proveniência | **CONCLUÍDO COMO CONTRATO**: o exemplo é sintético e não é uma estrutura científica validada |
| FT-036 | protocolo de superfície com índice de Miller, terminação, slab, vácuo, supercélula, camadas fixas, cobertura, método e convergência | **CONCLUÍDO COMO PROTOCOLO**: nenhum slab real foi gerado ou convergido |
| FT-037 | porta de energia de adsorção baseada em superfície limpa, adsorbato isolado e sistema adsorvido | **CONCLUÍDO COMO INFRAESTRUTURA**: o valor do exemplo é sintético e serve apenas ao teste automatizado |

## Regras implementadas

- FT-034 não aceita dataset vazio, compartilhado com a calibração ou sem análise de compatibilidade.
- O parecer precisa ser aprovado por revisor identificado e independente.
- FT-035 exige conteúdo estrutural e SHA-256 do arquivo, além da origem e das transformações.
- FT-036 registra explicitamente a construção do slab e os testes de convergência; campos `false` mantêm as pendências visíveis.
- FT-037 só calcula `E_ads = E_sistema - E_superfície - n E_adsorbato` quando existem exatamente três papéis, todos convergidos e com a mesma impressão digital metodológica.
- Mesmo quando a porta computacional passa, `recommendation_blocked` permanece verdadeiro: energia de adsorção isolada não demonstra atividade, seletividade ou estabilidade catalítica.

## Referências técnicas

- A documentação do ASE descreve a construção de superfícies por índices de Miller, número de camadas, vácuo e posicionamento de adsorbatos: https://wiki.fysik.dtu.dk/ase/ase/build/surface.html
- Um exemplo publicado da convenção de energia usa os três termos superfície+adsorbato, superfície limpa e adsorbato isolado, com parâmetros consistentes: https://doi.org/10.1039/C4RA16308G

## Evidência de aceite

- schemas `ft-htft-validation-v1`, `ft-dft-structure-v1`, `ft-dft-surface-v1` e `ft-dft-adsorption-v1`;
- exemplos sintéticos ou pendentes claramente rotulados;
- testes de bloqueio, proveniência, hash, comparabilidade e cálculo;
- validação centralizada dos 21 schemas e 21 exemplos.

## Próximos passos

FT-034 só poderá mudar para validação concluída após a implementação e o congelamento do modelo HTFT, a seleção de uma campanha externa compatível e o parecer independente. A sequência DFT prossegue na FT-038, com o adaptador de engine, sem transformar os exemplos sintéticos atuais em resultados científicos.
