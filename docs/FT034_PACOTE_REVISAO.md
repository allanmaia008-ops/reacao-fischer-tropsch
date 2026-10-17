# FT-034 — pacote de validação e revisão independente

## Estado verificável

O benchmark HTFT quantitativo v1 foi congelado e avaliado contra quatro linhas
holdout que não participaram da calibração. A avaliação quantitativa foi
**reprovada**. O bloqueio é um resultado científico, não uma falha de software.

| Resposta | MAE | RMSE | Critério | Resultado |
|---|---:|---:|---:|---|
| conversão de CO (p.p.) | 28,00 | 32,56 | MAE ≤ 10 | reprovado |
| CH4 (p.p. C) | 4,25 | 4,66 | MAE ≤ 5 | aprovado |
| olefinas C2–C4 (p.p. C) | 6,75 | 6,91 | MAE ≤ 5 | reprovado |
| razão olefina/parafina | 0,0825 | 0,1167 | MAE ≤ 0,15 | aprovado |

A conversão apresenta viés de −28 pontos percentuais. O benchmark de
persistência a 300 °C não representa o aumento de atividade a 320 °C e não pode
ser usado para recomendar condições.

## Dados e separação

- Fonte primária: Ahmed et al., *ACS Omega* 2021, DOI
  [10.1021/acsomega.1c04476](https://doi.org/10.1021/acsomega.1c04476).
- Calibração: quatro catalisadores da Tabela 4, 300 °C.
- Holdout: os mesmos quatro catalisadores da Tabela 5, 320 °C.
- Condições comuns: FBR, 20 bar, H2/CO = 1 e 4,2 L gcat−1 h−1.
- Qualificação de independência: o holdout não foi usado na calibração, mas é
  do mesmo artigo e laboratório; não constitui validação multilaboratorial.

## Incerteza e resíduos

Foram calculados MAE, MSE, RMSE, viés, resíduos linha a linha e intervalo de
95% do MAE por bootstrap não paramétrico determinístico com 10.000
reamostragens. A incerteza instrumental não foi reportada nas tabelas e não foi
inventada.

## Parecer independente solicitado

Um revisor sem participação na implementação deve conferir:

1. transcrição das Tabelas 4 e 5 e bases de seletividade;
2. separação calibração/holdout e sua limitação de mesmo estudo;
3. congelamento e hash do modelo;
4. critérios, métricas, resíduos e bootstrap;
5. conclusão de reprovação quantitativa e manutenção do bloqueio.

O parecer deve registrar `reviewer_id`, vínculo, declaração de independência,
data, decisão e justificativa. Até esse registro existir, o status formal é
**AVALIAÇÃO EXECUTADA / MODELO REPROVADO / REVISÃO INDEPENDENTE PENDENTE**.

## Teses e dissertações rastreadas

Foi criado o catálogo `data/htft/ft034_theses_dissertations_catalog.csv`. Duas
fontes USP contêm resultados HTFT relevantes e foram mantidas como evidência
contextual até a extração auditada das tabelas completas:

- Garona (2024), DOI 10.11606/T.3.2024.tde-10022025-090119;
- Silva (2023), DOI 10.11606/D.3.2023.tde-07022024-115619.

A tese de Du Toit (2002) foi registrada para futura auditoria dos capítulos e
equações. A tese de Van Berge (1994) foi excluída da FT-034 por estudar produção
de ceras em condições LTFT. Valores de resumo não foram usados para recalibrar
ou validar o modelo, pois não trazem todos os campos necessários para uma
comparação quantitativa compatível.
