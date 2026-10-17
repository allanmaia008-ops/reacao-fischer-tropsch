# FT-024 — busca de teses e dissertações

## Objetivo e critério de triagem

A busca foi direcionada a teses e dissertações com resultados experimentais ou
modelagem de Fischer–Tropsch sobre catalisadores de cobalto, priorizando Co–Ce,
suportes de sílica, condições LTFT e tabelas de conversão ou seletividade. Foram
consultados repositórios institucionais e a BDTD/IBICT em 16/10/2026.

Nenhum trabalho localizado reproduz simultaneamente a formulação
`80%Co/20%Ce/15wt%SiO2`, coprecipitação, pressão atmosférica, 200–260 °C e H2/CO de
1,0 e 1,5. Portanto, os trabalhos abaixo são fontes comparativas e não abrem a porta
de validação externa da FT-024.

## Trabalhos prioritários para extração de dados

| Prioridade | Trabalho | Escopo experimental | Uso possível | Compatibilidade FT-024 |
|---|---|---|---|---|
| alta | Menezes, V. M. R. (2018), UFC, dissertação, *Avaliação do desempenho de catalisadores de cobalto na síntese de Fischer-Tropsch* | Co/SBA-15 e Co/Ru/MCM-41; 200–270 °C; 20–30 atm; H2/CO 1 e 2; cinco combinações de pressão e temperatura | comparação de conversão e seletividade C2–C4, C5+ e C10+ em LTFT | temperatura e H2/CO parcialmente compatíveis; suporte, promotor e pressão incompatíveis |
| alta | Shiba, N. C. (2021), UNISA, tese, *The role of cobalt species in Fischer Tropsch synthesis: effects of support characteristics and reducing conditions* | Co/SiO2, Co/TiO2, Co/Al2O3 e Co–Ru; diferentes atmosferas e temperaturas de ativação; FT e WGS | avaliar efeito da ativação, fases Co0/CoO/Co2C, suporte e promoção por Ru | Co/SiO2 e LTFT relevantes; sem Ce e com protocolo diferente |
| alta | Mathe, S. (2021), University of Cape Town, dissertação, *Manganese promotion of a Co/SiO2 Fischer-Tropsch catalyst* | 22 wt% Co/SiO2, dopagem com Mn; leito fixo a 220 °C, 20 barg e H2/CO = 2 | referência independente para conversão/seletividade e efeito de promotor em Co/SiO2 | temperatura compatível; sem Ce, pressão e preparação incompatíveis |
| alta | Chikati, R. (2023), University of the Witwatersrand, tese, *Fischer–Tropsch synthesis: application of clinoptilolite as catalyst support* | 10 wt% Co; leito fixo a 220 °C e 10,85 bar; conversão e seletividades publicadas para várias granulometrias | conjunto independente LTFT para testar métricas e comportamento de cortes | temperatura compatível; suporte, composição e pressão incompatíveis |
| média | Rodrigues, J. J. (2015), UFCG, tese, *Desenvolvimento dos catalisadores Co/SBA-15 e Ru/Co/SBA-15...* | Co/SBA-15 e 20%Co/0,5%Ru/SBA-15 em reator de lama; seletividade C5+ e CH4 | comparação de sílica mesoporosa, Ru e frações pesadas | sem Ce e com suporte/protocolo diferentes |
| média | Smarzaro, J. L. (2022), UFRJ/COPPE, tese, *Nanopartículas de cobalto encapsuladas como catalisador na síntese de Fischer-Tropsch* | nanopartículas de cobalto encapsuladas em sílica e carbono | efeitos de encapsulamento, estabilidade e interação Co–SiO2 | sem Ce e arquitetura distinta |
| média | Ribeiro, A. T. S. (2016), UFPE, dissertação, *Catalisadores de Fischer-Tropsch modificados mediante tratamento ácido e adição de composto quelante* | catalisadores de cobalto modificados; comparação de catalisador estruturado e em pó | efeitos de preparação sobre conversão, CH4 e C5+ | família de Co relevante; composição distinta |
| média | Macheli, L. (2014), University of Cape Town, dissertação, *Silica modified Co3O4 nanocubes as a model system for metal-support interaction in Co/SiO2 catalyst* | nanocubos de Co3O4 modificados com TEOS; caracterização e teste FT | interação Co–SiO2, redução e estabilidade; atividade aumentada no sistema-modelo | sem Ce e material-modelo distinto |
| baixa/modelagem | Barros Junior, A. F. (2013), UFC, tese, *Estimação de parâmetros, modelagem e simulação da síntese de Fischer-Tropsch em reator tubular de leito fixo com catalisador de cobalto* | estimação cinética, balanços de massa e calor em reator tubular | comparação metodológica com o módulo cinético e o modelo de reator | não constitui validação experimental do catalisador FT-024 |
| baixa/modelagem | tese UNICAMP, *Modelagem e simulação de um reator multitubular em leito fixo com cinética Fischer Tropsch e catalisador de cobalto* | modelagem em Fortran/CFX baseada em reator Arge Sasol | referência de arquitetura para futura modelagem de reator | escala e finalidade diferentes; sem dados do catalisador-alvo |

## Referências e endereços institucionais

1. Menezes, V. M. R. *Avaliação do desempenho de catalisadores de cobalto na síntese de Fischer-Tropsch*. Dissertação, Universidade Federal do Ceará, 2018. https://repositorio.ufc.br/handle/riufc/31542.
2. Shiba, N. C. *The role of cobalt species in Fischer Tropsch synthesis: effects of support characteristics and reducing conditions*. Thesis, University of South Africa, 2021. https://hdl.handle.net/10500/28804.
3. Mathe, S. *Manganese promotion of a Co/SiO2 Fischer-Tropsch catalyst*. Master thesis, University of Cape Town, 2021. http://hdl.handle.net/11427/35863.
4. Chikati, R. *Fischer–Tropsch synthesis: application of clinoptilolite (natural zeolite) as catalyst support*. PhD thesis, University of the Witwatersrand, 2023. https://hdl.handle.net/10539/37372.
5. Rodrigues, J. J. *Desenvolvimento dos catalisadores Co/SBA-15 e Ru/Co/SBA-15 a partir das fontes de sílica tetraetilortosilicato e cinzas da casca de arroz destinados à reação de Fischer-Tropsch*. Tese, Universidade Federal de Campina Grande, 2015. https://dspace.sti.ufcg.edu.br/handle/riufcg/317.
6. Smarzaro, J. L. *Nanopartículas de cobalto encapsuladas como catalisador na síntese de Fischer-Tropsch*. Tese, COPPE/Universidade Federal do Rio de Janeiro, 2022. Registro BDTD: https://bdtd.ibict.br/vufind/Record/UFRJ_16837840926cfd85d46619b991556778.
7. Ribeiro, A. T. S. *Catalisadores de Fischer-Tropsch modificados mediante tratamento ácido e adição de composto quelante*. Dissertação, Universidade Federal de Pernambuco, 2016. https://repositorio.ufpe.br/handle/123456789/25099.
8. Macheli, L. *Silica modified Co3O4 nanocubes as a model system for metal-support interaction in Co/SiO2 catalyst for Fischer-Tropsch synthesis*. Master thesis, University of Cape Town, 2014. Repositório UCT: https://open.uct.ac.za/items/58fe53ab-267b-431a-a2a8-89ac1e5c752b.
9. Barros Junior, A. F. *Estimação de parâmetros, modelagem e simulação da síntese de Fischer-Tropsch em reator tubular de leito fixo com catalisador de cobalto*. Tese, Universidade Federal do Ceará, 2013. https://repositorio.ufc.br/handle/riufc/4835.

## Decisão para o banco experimental

Antes de incorporar números, os PDFs prioritários devem ser examinados para localizar
tabelas, identificar unidade, base de seletividade, balanço de carbono, replicatas e
incerteza. Dados apresentados apenas em gráficos deverão receber método de digitalização,
resolução e incerteza explícitos. Nenhum valor deve ser inferido do resumo.

Os dados extraídos dessas teses devem receber `external_validation_eligible=false` para
o modelo FT-024 enquanto composição, preparação, pressão ou suporte forem incompatíveis.
Eles podem formar um conjunto separado de validação de tendência e teste de
transferibilidade, sem serem misturados às medições do catalisador exato.
