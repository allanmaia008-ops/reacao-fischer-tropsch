# FT-024 — referências, banco experimental e critérios de validação

## Resultado da busca

O banco consolidado contém **374 medições publicadas associadas a 52 condições experimentais únicas**. Ele supera o requisito de 100 dados como número de medições, mas não deve ser descrito como 374 experimentos independentes.

- 44 medições provêm de 22 ensaios do catalisador exato do modelo, `80%Co/20%Ce/15wt%SiO2`, preparados por coprecipitação.
- 330 medições provêm de 30 ensaios Fe–Co–Ce com diferentes proporções, publicados em material suplementar aberto.
- Nenhuma linha é atualmente elegível como validação externa direta: o primeiro conjunto pertence ao estudo usado na calibração; o segundo muda composição, suporte e faixa térmica.
- Valores ausentes ou incertezas não publicadas permanecem declarados como `not_reported`. Não foram interpolados pontos de figuras.

O banco está em `data/evidence/ft024_cobalt_cerium_measurements.csv`; o manifesto registra contagens, SHA-256 e bloqueio científico.

## Critérios de aceitação propostos

Estes limiares são critérios de governança do projeto, não consensos universais da literatura. Devem ser congelados antes da avaliação externa.

| Dimensão | Critério FT-024 |
|---|---|
| Independência | conjunto não utilizado em seleção, ajuste ou escolha da forma do modelo |
| Compatibilidade | mesmo catalisador `80%Co/20%Ce/15wt%SiO2`, método de preparação compatível e entradas dentro do domínio declarado |
| Tamanho | pelo menos 20 condições externas únicas; o objetivo operacional de 100 deve contar condições, não respostas correlacionadas |
| MAE | MAE normalizado pela média observada ≤ 15% |
| MSE/RMSE | MSE sempre reportado na unidade ao quadrado; RMSE normalizado pela média observada ≤ 20% |
| Viés | valor absoluto do resíduo médio ≤ 5% da média observada |
| Resíduos extremos | no máximo 1% com resíduo padronizado absoluto > 3 |
| Tendência residual | correlação de Spearman absoluta entre resíduo e cada variável/fitted < 0,30 |
| Heterocedasticidade | teste pré-especificado sem evidência a 5%; se falhar, usar modelo de variância/ponderação e revalidar |
| Incerteza preditiva | cobertura do intervalo preditivo nominal de 95% entre 90% e 99% |
| Reamostragem | intervalo de confiança de 95% por bootstrap agrupado por estudo e lote, mínimo de 2.000 reamostragens |
| Incerteza de medição | propagar valores publicados; quando ausentes, executar análise de cenários e não tratá-los como zero |
| Revisão | relatório, partição, código, resíduos e exceções revisados por pessoa independente |

A porta só abre se todos os critérios passarem. MAE, MSE e RMSE devem ser calculados na variável original de resposta; transformações logarítmicas podem ter diagnóstico adicional, mas não substituem as métricas na unidade física.

## Referências bibliográficas

1. Mansouri, M.; Atashi, H.; Mirzaei, A. A.; Jangi, R. *Kinetics of the Fischer–Tropsch synthesis on silica-supported cobalt-cerium catalyst*. International Journal of Industrial Chemistry 4, 1 (2013). https://doi.org/10.1186/2228-5547-4-1. Fonte dos 22 ensaios Co–Ce/SiO2 e da formulação do catalisador.
2. Taherzadeh Lari, T.; Mirzaei, A. A.; Atashi, H. *Effects of Co/Ce molar ratio and operating temperature on nanocatalyst performance in the Fischer–Tropsch synthesis*. RSC Advances 7 (2017). https://doi.org/10.1039/C7RA05490D. Tabelas suplementares S4–S8 fornecem 30 ensaios e 330 respostas Fe–Co–Ce; uso contextual, não validação direta.
3. Beigbabaei, A. et al. *Selective Formation of Light Olefins from CO+H2 Over Silica Supported Co/CeO2 Prepared by Fusion Method: Preparation, Characterization and Operational Conditions Effects*. The Open Catalysis Journal 3, 62–69 (2010). Artigo lido; resultados principais são gráficos, portanto não foram digitalizados automaticamente.
4. Mirzaei, A. A.; Arsalanfar, M.; Beigbabaei, A.; Eslamimanesh, V. *Preparation and operating conditions for cobalt cerium oxide catalysts used in the conversion of synthesis gas into light olefins*. Journal of the Iranian Chemical Society 4, 347–363 (2007). https://doi.org/10.1007/BF03245986. Referência de formulação e condições; dados numéricos completos ainda exigem revisão do texto integral.
5. Ernst, B.; Hilaire, L.; Kiennemann, A. *Effects of highly dispersed ceria addition on reducibility, activity and hydrocarbon chain growth of a Co/SiO2 Fischer–Tropsch catalyst*. Catalysis Today 50, 413–427 (1999). https://doi.org/10.1016/S0920-5861(98)00519-7. Catalisadores 25%Co–CeO2/SiO2; composição diferente da usada pelo modelo.
6. Spadaro, L.; Arena, F.; López Granados, M.; Ojeda, M.; Fierro, J. L. G.; Frusteri, F. *Metal–support interactions and reactivity of Co/CeO2 catalysts in the Fischer–Tropsch synthesis reaction*. Journal of Catalysis 234, 451–462 (2005). https://doi.org/10.1016/j.jcat.2005.07.006. Co/CeO2 sem SiO2; evidência mecanística contextual.

## Pendência que permanece

O requisito numérico de 100 medições foi atendido. A validação externa do modelo, porém, continua bloqueada porque ainda não foi localizado um conjunto independente com ao menos 20 — idealmente 100 — condições únicas do mesmo catalisador, preparação e domínio operacional. O acesso CAFe informado pelo usuário não pôde ser automatizado porque o controle local do navegador está desativado nesta sessão.
