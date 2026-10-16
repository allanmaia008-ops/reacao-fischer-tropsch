# Revisão FT-024 e FT-027 — 2026-10-16

## FT-024: modelo exploratório implementado; validação externa pendente

Os quatro CSVs anteriores foram lidos: proveniência de equações, seletividade de
Mello, propriedades de suportes e seletividades externas parciais. Nenhum contém
uma série de taxas com condições suficientes para ajustar a cinética. A única CTY
preenchida não identifica dependência com temperatura e pressões.

Foi extraída a Tabela 1 de Mansouri et al. (2013), DOI
[10.1186/2228-5547-4-1](https://link.springer.com/article/10.1186/2228-5547-4-1/tables/1).
CSV interno: `data/evidence/ltft_mansouri_2013_kinetics.csv`.
São 22 experimentos publicados de Co–Ce/SiO2; 14 entre 200 e 260 °C.
Cada linha preserva valores publicados, unidade, DOI, tabela, elegibilidade e
checagem de taxa versus alimentação de CO por massa × conversão.
A tolerância absoluta de 0,0002 mmol/(g cat min) é uma regra de auditoria de
arredondamento, não incerteza experimental. A linha 10 falha: 0,0512 publicado
versus 0,0551257 calculado. O valor original não foi corrigido e fica sinalizado.
Essa linha já está fora do intervalo LTFT.

Modelo empírico implementado em `literature_kinetics.py`:
`ln(r) = b0 + b1*1000*(1/493.15 - 1/T_K) + b2*I(composição B)`.
O ajuste não reproduz o modelo mecanístico dos autores. As pressões são acopladas
em somente duas composições; portanto não se estimam ordens independentes de H2/CO.
Usa-se exclusivamente o catalisador do estudo, temperatura coberta pelo treino e
os pares de pressões parciais (0,333; 0,333) e (0,400; 0,267) bar.
Não transferir para pressões industriais, outros catalisadores ou composições.

Divisão pré-definida: 10 observações para treino; as quatro observações de 220/240 °C
para avaliação. MAE: 0,013757; RMSE: 0,015509 mmol CO/(g cat min).
Coeficientes: [-2,974305; 1,689192; -0,192066]. Intervalos preditivos de 95%
usam resíduos normais homocedásticos em log e distribuição t; não são incertezas
de medição. A dispersão é relevante e não existe critério de aceitação científica
aprovado. O ajuste permanece exploratório e `recommendation_blocked=true`.
Avaliação em pontos reservados do mesmo estudo não é validação externa.

Reprodução: instalar `pip install -e ".[kinetics]"` e executar
`python tools/run_ft024_literature.py --refresh`. Sem `--refresh`, reutiliza a cópia
local. O relatório `outputs/ft024_literature/report.json` contém hashes da fonte e
CSV, partição, covariância, previsões e intervalos. CSV e cópia HTML permanecem
locais, conforme a política existente do projeto. Não se alteraram aprovações dos
datasets antigos. A nova extração autoriza análise exploratória neste pedido,
mas não constitui revisão independente nem validação experimental do projeto.

Busca adicional identificou DOI 10.1021/acscatal.7b02758 (Co/SiO2 com promotor Pt)
e 10.5281/zenodo.8241527 (microcinética computacional). Não foram combinados com
Co–Ce/SiO2: catalisadores distintos e simulação não fornecem validação experimental
externa compatível.

Também foi extraída a Tabela 3 de Akbarzadeh et al. (2024), DOI
[10.1038/s41598-024-64382-0](https://www.nature.com/articles/s41598-024-64382-0/tables/3),
no CSV interno `ltft_akbarzadeh_2024_external_candidate.csv`: 15 experimentos com
temperatura, pressões parciais, conversão, taxa média e incerteza publicada. A porta
automática recusou validação antes de calcular métricas: o catalisador Co–Mn/SiO2 e
as pressões não pertencem ao domínio Co–Ce/SiO2 do modelo. O CSV permanece útil
para um futuro modelo específico de Co–Mn; não valida o atual. Continua necessária
uma campanha independente do mesmo sistema catalítico e domínio operacional.

## FT-027: preparação documental; execução de laboratório pendente

O benchmark acima é retrospectivo com literatura. Nenhum ensaio do projeto foi
executado nesta entrega. O registro `examples/ft027_pilot_pending.json` preserva
data, protocolo, método, dados brutos e revisão como ausentes.

Sequência necessária para o piloto:

1. Responsável do laboratório define catalisador/lote, equipamento disponível e
   resposta-alvo; registra isso no contrato experimental v2 existente.
2. Completar alimentação, geometria, ativação, método analítico e calibração dos
   instrumentos. Executar os diagnósticos de transporte existentes com dados reais.
3. Fixar previamente critérios de fechamento, estabilidade, replicatas, erro
   admissível e método de comparação. Escolher o modelo apenas se compatível com
   o catalisador e o domínio efetivamente ensaiados.
4. Aprovar protocolo e condições de execução pela equipe responsável, executar
   o ensaio e preservar arquivos instrumentais e condições efetivamente medidas.
5. Comparar previsão e observação na mesma base/unidade, emitir relatório,
   calcular SHA-256 dos dados e registrar revisão e desvios.

O validador agora exige origem `project_experiment`, data não futura, confirmação,
SHA-256 válido, atestado de conferência dos dados, revisor e relatório comparativo.
Sua validação é de metadados/atestados: não acessa URI nem autentica a execução.
Uma publicação não pode se tornar piloto próprio mudando apenas a confirmação.
Para encerrar FT-027 faltam equipamento/equipe executora e arquivos reais do ensaio;
não existe integração de controle de reator que permita executar o piloto aqui.
