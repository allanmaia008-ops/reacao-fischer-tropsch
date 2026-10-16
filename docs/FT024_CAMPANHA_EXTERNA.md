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
