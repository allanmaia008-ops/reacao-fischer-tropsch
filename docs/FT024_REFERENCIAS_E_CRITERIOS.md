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
4. Mirzaei, A. A.; Galavy, M.; Beigbabaei, A.; Eslamimanesh, V. *Preparation and operating conditions for cobalt cerium oxide catalysts used in the conversion of synthesis gas into light olefins*. Journal of the Iranian Chemical Society 4, 347–363 (2007). https://doi.org/10.1007/BF03245986. Texto integral revisado via acesso CAFe/UFRN em 16/10/2026. Confirma a formulação `80%Co/20%Ce/15wt%SiO2`, coprecipitação, envelhecimento por 2 h, ausência de promotor e calcinação a 600 °C por 6 h. Os ensaios catalíticos são HTFT, entre 300 e 500 °C, e os resultados de conversão/seletividade são apresentados principalmente em gráficos; não são validação LTFT independente.
5. Ernst, B.; Hilaire, L.; Kiennemann, A. *Effects of highly dispersed ceria addition on reducibility, activity and hydrocarbon chain growth of a Co/SiO2 Fischer–Tropsch catalyst*. Catalysis Today 50, 413–427 (1999). https://doi.org/10.1016/S0920-5861(98)00519-7. Acesso institucional confirmado via CAFe/UFRN. Campanha independente em 493 K, 2 MPa e H2/CO = 2, com 25 wt% Co e 4,5–38,2 wt% Ce. É evidência LTFT relevante, porém a composição, a pressão e a preparação diferem do modelo; o artigo reporta α = 0,82–0,87 para os catalisadores com céria e 0,92 para o catalisador sem promotor.
6. Spadaro, L.; Arena, F.; López Granados, M.; Ojeda, M.; Fierro, J. L. G.; Frusteri, F. *Metal–support interactions and reactivity of Co/CeO2 catalysts in the Fischer–Tropsch synthesis reaction*. Journal of Catalysis 234, 451–462 (2005). https://doi.org/10.1016/j.jcat.2005.07.006. Co/CeO2 sem SiO2; evidência mecanística contextual.
7. Mirzaei, A. A.; Arsalanfar, M.; Eslamimanesh, V. *SEM and BET methods for investigating the structure and morphology of Co–Ce catalysts for production of light olefins*. Australian Journal of Chemistry 61, 144–152 (2008). https://doi.org/10.1071/CH07130. Confirma a seleção de 80%Co/20%Ce/15%SiO2 coprecipitado, envelhecido por 2 h e calcinado a 600 °C; não fornece a campanha cinética LTFT independente requerida.
8. Dai, X.; Yu, C.; Li, R.; Shi, H.; Shen, S. *Role of CeO2 promoter in Co/SiO2 catalyst for Fischer–Tropsch synthesis*. Chinese Journal of Catalysis 27, 904–910 (2006). https://doi.org/10.1016/S1872-2067(06)60047-8. Acesso institucional confirmado via CAFe/UFRN. Evidência experimental independente de que uma pequena adição de CeO2 aumenta dispersão de Co, concentração de espécies superficiais –CH2–, probabilidade de crescimento e seletividade C5+. A preparação por impregnação ao ponto de umidade e a formulação diferem do catalisador FT-024.
9. Bruce, L. A.; Hoang, M.; Hughes, A. E.; Turney, T. W. *Ruthenium promotion of Fischer–Tropsch synthesis over coprecipitated cobalt/ceria catalysts*. Applied Catalysis A: General 100, 51–67 (1993). https://doi.org/10.1016/0926-860X(93)80115-7. Acesso institucional confirmado via CAFe/UFRN. Campanha independente de Co/Ce coprecipitado: 0,3 wt% Ru triplicou a atividade, sem perda declarada de seletividade, e a atividade permaneceu quase constante por até 100 h com conversão de CO superior a 40%. Não usa o mesmo suporte e inclui promoção por Ru.
10. Arsalanfar, M.; Mirzaei, A. A.; Bozorgzadeh, H. R.; Atashi, H.; Shahriari, S.; Pourdolat, A. *Structural characteristics of supported cobalt–cerium oxide catalysts used in Fischer–Tropsch synthesis*. Journal of Natural Gas Science and Engineering 9, 119–129 (2012). https://doi.org/10.1016/j.jngse.2012.05.015. Texto disponibilizado pela assinatura CAFe/UFRN. Compara razão Co/Ce, envelhecimento, calcinação, suportes e promotores por XRD, SEM, TPR, BET, TGA e DSC. Compartilha autores e protocolo com Mirzaei et al. (2007), sendo evidência de caracterização, não uma validação externa independente da matriz FT024-EXT-001.
11. He, L.; Teng, B.; Zhang, Y.; Fan, M. *Development of composited rare-earth promoted cobalt-based Fischer–Tropsch synthesis catalysts with high activity and selectivity*. Applied Catalysis A: General 505, 276–283 (2015). https://doi.org/10.1016/j.apcata.2015.07.041. Campanha em leito fixo com Co suportado em sílica e promotores La/Ce; composição diferente da formulação FT-024.
12. Suzuki, T.; Tajima, S. *Enhancement of Fischer–Tropsch Reaction on Silica Supported Cobalt Catalyst*. Transactions of the Materials Research Society of Japan 35, 635–638 (2010). https://doi.org/10.14723/tmrsj.35.635. Compara promotores de terras raras em Co/SiO2, incluindo céria, mas não informa a razão 80:20 nem a preparação-alvo.
13. Zohdi-Fasaei, H.; Atashi, H.; Farshchi Tabrizi, F.; Mirzaei, A. A. *Modeling and optimization of Fischer–Tropsch synthesis over Co–Mn–Ce/SiO2 catalyst using hybrid RSM/LHHW approaches*. Energy 128, 496–508 (2017). https://doi.org/10.1016/j.energy.2017.03.122. Possui planejamento e modelagem experimental, porém adiciona Mn e não valida o catalisador binário Co–Ce.

## Resultado da busca de equivalência da campanha externa

A triagem específica procurou trabalhos que reunissem simultaneamente: composição
`80%Co/20%Ce/15wt%SiO2`, coprecipitação, pressão atmosférica, 200–260 °C, H2/CO de
1,0 e 1,5 e resultados numéricos de taxa. Nenhuma publicação independente localizada
atendeu a todos esses critérios.

Beigbabaei et al. (2010) empregou a mesma composição nominal, mas por fusão e em
300–450 °C. Mirzaei et al. (2007) e Mirzaei et al. (2008) estudaram a formulação
coprecipitada, mas concentraram a avaliação de desempenho em temperaturas mais altas
e não constituem uma repetição externa da matriz cinética de Mansouri et al. (2013).
Os estudos de Dai, Bruce e Arsalanfar são independentes, porém alteram composição,
suporte, promotor ou método de preparação. Por isso, todos permanecem como evidência
contextual e nenhuma linha recebeu `external_validation_eligible=true`.

### Auditoria no Portal de Periódicos CAPES — 2026-10-16

A busca por `cobalt cerium silica Fischer Tropsch` retornou quatro artigos, incluindo
Ernst et al. (1999), He et al. (2015) e Suzuki e Tajima (2010). A busca pelo título
exato de Mirzaei et al. (2007) confirmou o registro revisado por pares, DOI,
autoria, periódico, volume e páginas. Após a renovação da sessão CAFe, a página da
Springer reconheceu o acesso institucional da Universidade Federal do Rio Grande do
Norte e permitiu obter o texto integral.

O artigo confirma o seguinte protocolo: reator tubular de leito fixo em aço
inoxidável, diâmetro interno de 3 mm, 1,0 g de catalisador, pressão atmosférica,
pré-redução *in situ* a 300 °C por 8 h em H2/N2 (30 mL/min de cada gás), ensaios entre
300 e 500 °C, H2/CO entre 1 e 4 e GHSV entre 4050 e 5400 h-1. Para o catalisador
selecionado, a condição reportada como ótima para olefinas leves foi 450 °C,
H2/CO = 2 e GHSV = 4500 h-1. As Tabelas 1–3 fornecem áreas BET para séries de razão
Co/Ce, tempo de envelhecimento e presença de SiO2; já conversão de CO e seletividades
são exibidas em gráficos e não foram transformadas em números sem uma digitalização
com incerteza explícita.

Apesar da coincidência da formulação, o artigo pertence ao domínio HTFT e compartilha
autoria e linhagem institucional com a fonte de Mansouri et al. (2013). Portanto, ele
é evidência primária útil para preparação e triagem do catalisador, mas não satisfaz
nem a independência nem o domínio LTFT exigidos por FT024-EXT-001.

Uma segunda rodada pelo acesso CAFe confirmou acesso institucional aos textos de
Arsalanfar et al. (2012), Bruce et al. (1993), Ernst et al. (1999) e Dai et al.
(2006). Ernst et al. é o candidato independente mais próximo do domínio LTFT:
493 K (219,85 °C), 2 MPa e H2/CO = 2, mas altera simultaneamente composição,
pressão e método de preparação. Bruce et al. fornece estabilidade por até 100 h,
porém não usa SiO2 e inclui Ru. Dai et al. usa impregnação e uma pequena carga de
céria, enquanto Arsalanfar et al. pertence à mesma linhagem dos estudos usados para
selecionar a formulação. Nenhum desses quatro estudos abriu a porta de validação
externa do catalisador exato no domínio atmosférico de FT024-EXT-001.

Para Ernst et al. (1999), o registro CAPES confirmou 25 wt% de Co, 4,5–38,2 wt% de
Ce, 493 K, 2 MPa e H2/CO = 2, com preparação sol-gel/coprecipitação distinta. Assim,
o estudo é independente e contém uma condição LTFT, mas é incompatível em carga,
pressão, composição e preparação.

## Pendência que permanece

O requisito numérico de 100 medições foi atendido. A validação externa do modelo,
porém, continua bloqueada porque ainda não foi localizado um conjunto independente
com ao menos 20 — idealmente 100 — condições únicas do mesmo catalisador, preparação
e domínio operacional LTFT. O acesso CAFe ao texto integral de Mirzaei et al. (2007)
resolveu a pendência documental desse artigo, mas confirmou que ele não substitui a
execução independente de FT024-EXT-001.
