# Dados externos, GNN e alternativa neural para FT

## Decisão com o corpus atual

O benchmark HTFT v14 tem 54 linhas completas no perfil operacional (8 fontes) e 36 no perfil com GHSV/TOS (5 fontes). A junção exata dentro do v14 segue em 0/54: o catálogo de descritores é de estudos distintos. A auditoria source-scoped corrigida, por outro lado, liga os 12 registros do catálogo aos ensaios dos próprios estudos Liu 2021 e Xie 2016 por dataset, catalisador e DOI; isso gera um corpus descriptor-rich separado, não uma extensão da coorte v14. Não foram localizadas estruturas atômicas rastreáveis para treinar GNN. Por isso:

- a seleção por alvo exibida no app é somente o menor MAE retrospectivo por alvo/perfil; não promove modelo, não gera previsão e não libera recomendação;
- não treinar uma GNN de processo nem uma MLP com esses poucos grupos de artigos: a unidade de generalização é a fonte independente, não cada linha tabular, e o risco de sobreajuste é alto;
- não combinar dados computacionais de adsorção com rótulos experimentais de conversão/seletividade como se fossem a mesma variável.

O join reprodutível está implementado em `src/plataforma_ltft/htft_descriptor_join.py`. No ambiente de pesquisa, `py -3 tools/audit_htft_descriptor_join.py` regenerou o CSV aumentado e o relatório JSON de cobertura. Os CSVs extraídos dos artigos não são incluídos no deploy público por escopo/licença; o código nunca inventa correspondências nem preenche descritores ausentes.

## Fontes online a priorizar

| Fonte | Tipo de evidência e utilidade | Limite para esta plataforma |
|---|---|---|
| [NOMAD Catalysis App](https://nomad-lab.eu/prod/v1/gui/search/heterogeneouscatalyst) | Repositório/app de dados experimentais estruturados de catálise heterogênea; filtra reações, materiais catalíticos e condições. Melhor primeiro lugar para procurar novos ensaios e metadados experimentais. | A existência da plataforma não garante que haja número ou cobertura suficiente de FT/HTFT. Antes de importar, consultar entradas FT, conferir o esquema, unidade, proveniência, base de seletividade e licença; manter LTFT e HTFT separados. |
| [ACS SI: Motaev et al. (2023), DOI 10.1021/acs.iecr.3c03147](https://pubs.acs.org/doi/10.1021/acs.iecr.3c03147) | O suplemento contém um conjunto declarado de 169 experimentos FT com catalisadores de Co, 16 atributos e seis respostas. Candidato direto para enriquecer/validar um ramo LTFT separado. | Não é HTFT Fe e não deve ser incorporado ao corpus v14. Extrair SI, auditar linha a linha, conciliar definições/bases, duplicatas, estudos e licença antes de uso. |
| [Catalysis-Hub GraphQL](https://www.catalysis-hub.org/graphQLConsole) | Energias de adsorção, energias de reação, barreiras e geometrias/superfícies computacionais DFT; pode apoiar descritores e benchmark atomístico. | Não é base de ensaios de processo FT; rótulos computacionais não substituem conversão, seletividade, GHSV/TOS ou rendimento experimental. |
| [Open Catalyst Project (OC20/OC22)](https://github.com/Open-Catalyst-Project/ocp) | Estruturas e energias/forças DFT em grande escala, úteis para pré-treino de representações geométricas e modelos de energia/força. | Cobertura química e alvos diferentes dos desfechos de processo FT; usar apenas como pré-treino/benchmark estrutural, com licença e split documentados. |

## Plano para tornar uma GNN testável

1. Criar identificadores canônicos de fonte, catalisador e ensaio; normalizar DOI, composição, suporte, promotores, fase, preparação/ativação, tamanho de partícula, BET e condições. Manter cada campo como medido, reportado, inferido ou ausente.
2. Corrigir a proveniência/junção de descritores até cobrir ensaios do corpus. Exigir geometria/superfície rastreável: arquivo, DOI, fase, faceta, terminação, adsorbato e método DFT.
3. Construir grafo superficial/adsorbato para tarefa computacional (energia/barreira) e, em separado, um ramo tabular de processo (T, P, H₂/CO, GHSV/TOS e propriedades catalíticas). Uma arquitetura híbrida só pode transferir informação após uma ponte validada entre domínio atomístico e resposta experimental.
4. Pré-treinar ou comparar com conjuntos DFT públicos; fazer split por publicação e por identidade de catalisador, sem vazamento de geometrias equivalentes. Quantificar erro por fonte/família e calibrar incerteza.
5. Só avaliar desfechos experimentais com campanha externa prospectiva e validação independente; manter `recommendation_blocked=true` até critérios científicos predefinidos passarem.

Uma GNN equivarante (por exemplo, família GemNet/Equiformer) é adequada para geometrias e propriedades atomísticas, mas não resolve por si só o problema de poucos ensaios FT. Reutilizar checkpoints públicos não transforma seus rótulos DFT em dados experimentais FT.

## Alternativa de rede neural

A alternativa natural à GNN é uma rede neural densa tabular (MLP), com uma ou poucas camadas pequenas, regularização L2/early stopping, escala ajustada somente no treino e saída multi-alvo. Ela aceita vetores de operação e descritores sem exigir CIF. Ainda assim, com 5–8 fontes, comparar MLP contra Ridge/GP/árvores por validação nested leave-one-source-out é apenas um piloto; não presumir que uma rede seja superior. Usar o conjunto ACS de Co somente no estudo LTFT correspondente após auditoria e evitar misturar esse teste com HTFT.

Há precedente direto de ANN para FT usando dados sintéticos gerados por um modelo single-event microkinetic, com produção de metano como resposta. Isso apoia ANN como surrogate de simulador mecanístico, mas não prova generalização em dados experimentais heterogêneos. Caso a plataforma futuramente possua um mecanismo cinético validado, a ANN/PINN pode ser avaliada primeiro como acelerador do solver, com erros medidos contra o solver e balanços físicos impostos.

## Referências verificadas

- Motaev, K. et al. “Application of Machine Learning to Fischer–Tropsch Synthesis for Cobalt Catalysts.” *Industrial & Engineering Chemistry Research* 62 (48), 20658–20666 (2023). [DOI](https://doi.org/10.1021/acs.iecr.3c03147). O resumo e a página do artigo descrevem o conjunto de 169 experimentos e o suplemento.
- Schumann, J. et al. “Enabling open and FAIR catalysis data with standardized data structures.” *Nature Catalysis* 9, 225–229 (2026). [DOI](https://doi.org/10.1038/s41929-026-01508-9). Esquema NOMAD para busca/compartilhamento de dados experimentais heterogêneos.
- Winther, K. T. et al. “Catalysis-Hub.org, an open electronic structure database for surface reactions.” *Scientific Data* 6, 75 (2019). [DOI](https://doi.org/10.1038/s41597-019-0081-y). Dados computacionais de adsorção, reação e barreiras em superfícies.
- Chanussot, L. et al. “The Open Catalyst 2020 (OC20) Dataset and Community Challenges.” *ACS Catalysis* 11, 6059–6072 (2021). [DOI](https://doi.org/10.1021/acscatal.0c04525). Dataset DFT de geometrias, energias e forças para catálise de superfície.
- Chakkingal, A. et al. “Machine learning based interpretation of microkinetic data: a Fischer–Tropsch synthesis case study.” *Reaction Chemistry & Engineering* 7, 101–110 (2022). [DOI](https://doi.org/10.1039/D1RE00351H). ANN reproduziu dados gerados por SEMK; não é um conjunto independente de rótulos experimentais.

## Situação

Fontes identificadas, não importadas nesta alteração. O resumo público usado pela interface contém somente MAE agregados e estado dos bloqueios, sem medições, previsões ou resíduos linha a linha. O passo seguro de ingestão é auditar arquivos suplementares/entradas com identificadores, direitos de uso, unidade e definição de alvo; não concatenar os registros diretamente ao conjunto HTFT atual.
