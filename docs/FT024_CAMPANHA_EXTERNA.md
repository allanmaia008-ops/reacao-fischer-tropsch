# FT-024 — campanha externa independente FT024-EXT-001

## Estado

A matriz prospectiva contém 100 corridas randomizadas, 50 condições únicas e dois
lotes de catalisador a serem preparados independentemente. Ela é um protocolo de
execução e captura; não contém resultados experimentais.

O catalisador-alvo é `80%Co/20%Ce/15wt%SiO2`, preparado por coprecipitação. O
domínio permanece restrito a pressão atmosférica, 200–260 °C e às duas composições
de alimentação admitidas pelo modelo. As condições reproduzem o domínio publicado
por Mansouri et al. (2013), sem reutilizar suas respostas como validação externa.

## Desenho

- 25 temperaturas entre 200 e 260 °C;
- duas razões H2/CO: 1,0 e 1,5;
- dois lotes independentes do catalisador, totalizando 100 corridas;
- ordem aleatória reprodutível, semente `24024`;
- massa nominal de catalisador de 1,0 g, GHSV nominal de 3.950 h-1 e coleta após
  12 h de estabilização, sujeitos à revisão de segurança e capacidade do laboratório;
- campos separados para resultados, incerteza, operador, data, arquivos brutos,
  SHA-256, exclusão e parecer independente.

## Governança e segurança

A execução requer instalação habilitada para CO/H2, análise de risco, revisão do
responsável técnico, calibração analítica, verificação de transferência de massa e
calor e retenção dos cromatogramas. A plataforma não controla o reator nem autoriza
uma operação de laboratório.

Uma corrida só muda para `validation_eligible=true` depois de executada, rastreada e
aprovada. A validação do modelo exige pelo menos 20 condições compatíveis e aprovação
de todos os critérios pré-registrados de MAE, MSE/RMSE, viés, resíduos,
heterocedasticidade, cobertura preditiva e incerteza.

## Pendência objetiva

O desenho da campanha está completo. A pendência científica só será resolvida após
execução por laboratório independente e entrega dos dados brutos. Marcar a FT-024
como validada antes disso equivaleria a fabricar evidência experimental.

## Fonte primária do domínio

Mansouri, M.; Atashi, H.; Mirzaei, A. A.; Jangi, R. *Kinetics of the
Fischer–Tropsch synthesis on silica-supported cobalt-cerium catalyst*.
International Journal of Industrial Chemistry 4, 1 (2013).
https://doi.org/10.1186/2228-5547-4-1.

## Auditoria de literatura posterior

A busca por execução prévia da matriz não encontrou uma campanha independente que
reúna a mesma composição, coprecipitação e domínio LTFT. Os artigos adicionais e sua
classificação de compatibilidade foram incorporados a
`FT024_REFERENCIAS_E_CRITERIOS.md`. Eles sustentam a família catalítica e o desenho
experimental, mas não substituem a execução de FT024-EXT-001.

### Resultado do acesso CAFe — 2026-10-16

O texto integral de Mirzaei et al. (2007), obtido pela assinatura institucional da
UFRN, confirma a formulação e o preparo do catalisador-alvo: 80%Co/20%Ce, 15% em massa
de SiO2, coprecipitação, envelhecimento por 2 h, sem promotor e calcinação a 600 °C
por 6 h. O trabalho utilizou 1,0 g de catalisador em leito fixo, pressão atmosférica,
H2/CO entre 1 e 4, GHSV entre 4050 e 5400 h-1 e temperaturas de 300–500 °C.

Esses dados fortalecem o protocolo de preparação, mas não encerram a campanha:
trata-se de HTFT, fora do domínio 200–260 °C, e o estudo compartilha autoria/linhagem
institucional com a fonte de calibração. Logo, não é um conjunto externo independente
apto a validar o modelo LTFT.

Uma busca complementar com acesso CAFe localizou Ernst et al. (1999) no domínio
LTFT (493 K, 2 MPa e H2/CO = 2), além de Bruce et al. (1993), Dai et al. (2006) e
Arsalanfar et al. (2012). O primeiro é independente, mas emprega 25 wt% Co,
4,5–38,2 wt% Ce e outra preparação; os demais alteram suporte, promotor, método ou
independência científica. Assim, ampliam a base contextual, mas não substituem as
corridas externas com a formulação e o domínio de FT024-EXT-001.

Teses e dissertações também foram triadas. Elas fornecem campanhas LTFT independentes
com Co/SiO2, Co/SBA-15 e outros suportes, mas nenhuma reproduz simultaneamente a
formulação, a coprecipitação e a pressão atmosférica exigidas. A lista auditável está
em `docs/FT024_TESES_DISSERTACOES.md`.
