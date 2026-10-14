# Planejamento mestre — Plataforma Reação Fischer–Tropsch

## 1. Visão do produto

Criar uma plataforma científica independente para apoiar o planejamento e a
análise de estudos Fischer–Tropsch, começando pelo hidrocarboneto ou corte de
produto desejado e conectando, de modo rastreável:

1. objetivo de produto;
2. regime LTFT ou HTFT;
3. alimentação e restrições experimentais;
4. família catalítica, suporte, promotores e preparação;
5. distribuição de produtos e balanços;
6. evidências, modelos e incertezas;
7. planejamento experimental;
8. cálculos atomísticos opcionais;
9. relatório auditável da decisão.

A plataforma não deve apresentar uma heurística, resultado ASF, estrutura
inferida, arquivo de entrada DFT ou saída de IA como evidência experimental ou
recomendação validada.

## 2. Objetivos

### Objetivo principal

Reduzir o espaço de busca experimental de forma transparente, sem ultrapassar o
domínio de validade dos dados e modelos disponíveis.

### Objetivos específicos

- permitir escolher produto individual (`C1`–`C60`) ou corte de produto;
- distinguir LTFT, HTFT, transição e casos fora do envelope aprovado;
- organizar catalisadores de Co, Fe e sistemas exploratórios sem misturá-los;
- calcular ASF como referência matemática, com limitações visíveis;
- validar unidades, balanços C/H/O e qualidade analítica;
- comparar apenas experimentos cientificamente compatíveis;
- quantificar incerteza, extrapolação e domínio de aplicabilidade;
- preparar planos experimentais revisáveis;
- integrar DFT somente com estruturas e protocolos completos;
- gerar resultados reproduzíveis e auditáveis.

## 3. Usuários e responsabilidades

| Perfil | Necessidade | Responsabilidade mínima |
|---|---|---|
| Pesquisador | planejar e comparar casos | revisar premissas e evidências |
| Operador de laboratório | preparar ensaio | informar limites e dados reais do equipamento |
| Curador de dados | incorporar literatura/experimentos | registrar origem, licença, unidades e revisão |
| Especialista científico | validar modelos e recomendações | aprovar domínio, métricas e critérios |
| Administrador | operar a plataforma | acesso, backup, auditoria e incidentes |
| Desenvolvedor | implementar e testar | preservar contratos e rastreabilidade |

Nenhum perfil individual deve poder transformar automaticamente uma hipótese em
evidência aprovada.

## 4. Escopo funcional

### 4.1 Seleção orientada pelo produto

O fluxo começa com:

- produto individual, por exemplo CH4, C2H4 ou um `Cn`;
- corte, por exemplo C2–C4, gasolina, destilados médios ou ceras;
- base da seletividade: carbono, mol ou massa;
- prioridade: rendimento, seletividade, produtividade, estabilidade, custo ou
  combinação explicitamente ponderada;
- pureza/corte desejado e necessidade de upgrading.

O sistema deve explicar quando um produto puro não é representável pela ASF.

### 4.2 Regimes da reação

Cada caso declara um regime. Os envelopes serão versionados e configuráveis.

| Regime inicial de roteamento | Temperatura de referência | Estado inicial |
|---|---:|---|
| LTFT | 180–260 °C | primeira linha de implementação |
| Transição | >260 e <280 °C | exige justificativa e revisão |
| HTFT | 280–350 °C | linha própria, inicialmente bloqueada |
| Fora do envelope | <180 ou >350 °C | estudo específico obrigatório |

Essas faixas são regras de roteamento, não fronteiras físico-químicas universais.
Catalisador, fase, reator, composição, conversão e tempo de residência também
devem ser considerados.

### 4.3 Linha LTFT

Prioridades:

- destilados médios, parafinas e ceras;
- Co e Fe tratados como famílias distintas;
- efeito de pressão, H2/CO, GHSV/WHSV e temperatura;
- água, WGS, desativação, sinterização e transformação de fase;
- desvios da ASF em C1/C2 e cauda pesada;
- transferência de massa e calor;
- estabilidade ao longo do tempo.

### 4.4 Linha HTFT

Prioridades:

- olefinas leves, gasolina e coprodutos definidos pelo caso de uso;
- Fe e Fe promovido como escopo inicial;
- fase óxido/carbeto/carbono e sua evolução;
- razão olefina/parafina por número de carbono;
- WGS, Boudouard, metanação, readsorção e craqueamento;
- coque/carbono, regeneração e desativação;
- gradientes térmicos e hot spots;
- aromáticos, oxigenados, isômeros e espécies não identificadas.

Nenhum parâmetro calibrado em LTFT poderá ser reutilizado em HTFT sem nova
validação.

### 4.5 Cadastro do catalisador

Campos mínimos:

- composição nominal e lote;
- família ativa;
- precursor;
- suporte, área, porosidade e tratamento;
- promotores e cargas;
- método de preparação;
- secagem, calcinação, redução/ativação;
- tamanho de partícula, dispersão e propriedades medidas;
- fase ativa: medida, inferida ou hipotética;
- métodos de caracterização e arquivos correspondentes;
- histórico de uso, regeneração e armazenamento.

### 4.6 Caso experimental

Campos mínimos:

- tipo e dimensões do reator;
- massa de catalisador, volume do leito e diluente;
- composição completa da alimentação, inertes e contaminantes;
- vazão, GHSV/WHSV, pressão e queda de pressão;
- temperaturas de entrada, leito e máxima;
- protocolo de partida, ativação e parada;
- tempo em operação e janela de estado estacionário;
- conversões de CO e H2;
- CO2, água e distribuição de produtos;
- base analítica, GC, calibração e fatores de resposta;
- replicatas, incertezas e fechamento C/H/O;
- eventos operacionais e observações.

### 4.7 Evidências

Cada evidência possuirá:

- identificador e versão;
- DOI/URL/origem experimental;
- licença e condição de uso;
- método de extração;
- tabela, página ou arquivo de origem;
- unidades originais e canônicas;
- condições e catalisador associados;
- incerteza e replicatas;
- status: `metadado`, `extraído`, `verificado`, `aprovado` ou `rejeitado`;
- responsável e data da revisão;
- motivo de inclusão/exclusão;
- hash do artefato quando aplicável.

Dados sem licença ou rastreabilidade podem ser preservados localmente para
auditoria, mas não entram automaticamente no repositório público ou calibração.

### 4.8 Modelos científicos

Camadas previstas:

1. validação física e dimensional;
2. ASF ideal;
3. comparação ASF versus dados;
4. correções ou múltiplos `alpha`, se validados;
5. modelos cinéticos publicados e reimplementados;
6. modelos empíricos/ML com validação externa;
7. otimização multiobjetivo e planejamento experimental.

Todo modelo registra equação/artefato, parâmetros, unidades, conjunto de ajuste,
conjunto de teste, domínio, incerteza, versão e limitações.

### 4.9 Planejamento experimental

A plataforma poderá propor faixas candidatas quando houver evidência suficiente.
O plano deve conter:

- hipótese e objetivo;
- variáveis, faixas e restrições;
- respostas medidas;
- controles, brancos e replicatas;
- sequência e randomização;
- critérios de estado estacionário;
- critérios de parada e segurança fornecidos pelo laboratório;
- análise estatística prevista;
- campos de aceite/rejeição pelo especialista.

No MVP, a plataforma não controla equipamentos.

### 4.10 DFT e ciência de materiais

O módulo DFT será opcional e separado da evidência experimental. Exigirá:

- estrutura completa e validada;
- fase, faceta, terminação, slab, vácuo e cobertura;
- adsorbato, sítio e configuração inicial;
- spin, carga, funcional, dispersão, pseudopotencial/base, cutoff e pontos k;
- superfície limpa, adsorbato isolado e sistema adsorvido comparáveis;
- protocolo e engine versionados;
- teste de convergência e resultado executado;
- proveniência dos arquivos e recursos computacionais.

Energia de adsorção será tratada como propriedade calculada, não como prova de
atividade, seletividade ou estabilidade experimental.

## 5. Fora do escopo inicial

- controle direto de reator ou instrumentos;
- recomendação autônoma de condição segura;
- previsão de conversão sem cinética calibrada;
- geração de estrutura cristalina “confirmada” apenas por fórmula;
- ranking universal de catalisadores;
- mistura de dados LTFT e HTFT sem validação;
- publicação automática de dados restritos;
- substituição da revisão científica humana.

## 6. Arquitetura de produto

Componentes:

- interface web;
- API versionada;
- serviço de contratos e unidades;
- catálogo de materiais/catalisadores;
- catálogo de evidências;
- motor LTFT;
- motor HTFT;
- motor de balanços e qualidade;
- orquestrador de execuções;
- worker assíncrono;
- armazenamento relacional e de artefatos;
- gerador de relatórios/notebooks;
- módulo DFT separado;
- autenticação, autorização e auditoria;
- observabilidade e administração.

Detalhes em [docs/ARQUITETURA_ALVO.md](docs/ARQUITETURA_ALVO.md).

## 7. Dados e contratos

### Entidades principais

- `User`, `Organization`, `Project`;
- `ProductTarget`, `FTCase`, `OperatingEnvelope`;
- `Catalyst`, `CatalystBatch`, `Preparation`, `Characterization`;
- `Experiment`, `AnalyticalMethod`, `Measurement`;
- `EvidenceSource`, `EvidenceRecord`, `Review`;
- `Model`, `ModelVersion`, `ApplicabilityDomain`;
- `Run`, `Artifact`, `Report`, `Decision`;
- `Structure`, `Surface`, `Adsorbate`, `DFTProtocol`, `DFTRun`.

### Regras

- IDs imutáveis e versões explícitas;
- unidades canônicas sem apagar unidades originais;
- campos obrigatórios condicionados ao regime;
- migrações explícitas de schema;
- exclusão lógica para dados científicos;
- trilha de auditoria de todas as mudanças relevantes;
- separação entre dados públicos, privados e restritos;
- exportação legível por máquina.

## 8. Qualidade científica

### Portas mínimas

| Porta | Critério |
|---|---|
| Q0 — cadastro | campos, unidades e proveniência válidos |
| Q1 — experimento | método, condições, estado estacionário e balanços adequados |
| Q2 — comparação | casos compatíveis e normalização documentada |
| Q3 — calibração | corpus aprovado, divisão de dados e métrica definida |
| Q4 — validação | teste externo e incerteza aceitáveis |
| Q5 — orientação | domínio verificado e limitações exibidas |
| Q6 — recomendação | revisão e aprovação humana registradas |

### Testes científicos

- conservação e fechamento de balanços;
- dimensionalidade e conversões de unidades;
- limites físicos e regras condicionais;
- casos sintéticos com resultados conhecidos;
- regressão contra versões aprovadas;
- sensibilidade e propagação de incerteza;
- extrapolação e domínio de aplicabilidade;
- prevenção de vazamento entre treino e teste;
- validação externa por catalisador/lote/grupo experimental;
- não regressão LTFT ao introduzir HTFT.

## 9. Segurança, ética e governança

- autenticação e perfis com menor privilégio;
- segregação por organização/projeto;
- criptografia em trânsito e em repouso;
- segredos fora do código, notebooks e logs;
- logs sem credenciais ou dados desnecessários;
- política de retenção e descarte;
- backups testados e restauração periódica;
- licenças e autoria preservadas;
- registro de alterações de modelos e dados;
- aviso permanente de escopo e limitações;
- revisão de riscos antes de qualquer integração com laboratório.

## 10. Experiência do usuário

Fluxo principal:

1. criar projeto;
2. escolher produto desejado;
3. escolher/declarar regime;
4. informar alimentação, reator e restrições;
5. cadastrar ou selecionar catalisador;
6. verificar completude e qualidade;
7. selecionar evidências aplicáveis;
8. executar orientação/modelo permitido;
9. revisar incerteza, domínio e bloqueios;
10. preparar plano experimental;
11. aprovar ou rejeitar;
12. exportar relatório e artefatos.

Cada valor exibirá um selo: `entrada`, `evidência`, `hipótese`, `heurística`,
`modelo`, `DFT` ou `experimento`.

## 11. Estratégia de implementação

### Fase UX — modernização prioritária da plataforma

Esta fase passa a ser executada **antes da retomada das melhorias científicas e
operacionais ainda planejadas**. Ela reorganiza a experiência sem alterar as
regras científicas, contratos, bloqueios ou o worker já validados.

Ordem de execução:

1. `FT-049` — **concluída**: navegação lateral pelo fluxo produto → regime →
   catalisador → condições → resultados → evidências, com progresso, pendências
   e estado persistente da sessão;
2. `FT-050` — **concluída**: página inicial com proposta, ações principais e
   estado explícito de LTFT, HTFT e recomendações;
3. `FT-051` — **concluída**: sistema visual próprio com tokens, componentes,
   foco visível, redução de movimento e adaptação para desktop e celular;
4. `FT-052` — **concluída**: entradas reorganizadas em blocos, com unidades,
   ajuda contextual, mensagens próximas ao campo e validação imediata;
5. `FT-053` — **concluída**: painel científico de resultados com curva ASF
   C1–C60, faixa-alvo destacada, base de carbono declarada, fechamento com cauda
   analítica C61+ até C∞, condições utilizadas, prontidão e bloqueios separados;
6. `FT-054` — **concluída**: maturidade representada por categorias textuais e
   visuais rastreáveis — matemático, heurístico, literatura, experimental,
   calibrado ou bloqueado — vinculadas à origem e à limitação;
7. `FT-055` — **concluída**: comparação auditável de dois ou três cenários ASF,
   com entradas, base e bloqueios explícitos, sem apresentá-la como otimização;
8. `FT-056` — **concluída**: responsividade, acessibilidade, fluxo e regressão
   científica testados; CI e critérios separados de publicação documentados.

**Porta UX:** as atividades `FT-049` a `FT-056` devem ser aceitas antes de
retomar `FT-010` e as demais atividades anteriormente planejadas. Correções
críticas de segurança ou integridade científica continuam tendo precedência.

**Saída:** interface moderna e orientada à decisão, mantendo
`recommendation_blocked=true` sempre que as evidências forem insuficientes.

### Fase 0 — fundação e governança

Entregáveis:

- charter, responsáveis e matriz de decisão;
- identidade e licença do projeto;
- taxonomia científica;
- política de dados, autoria e segurança;
- repositório, convenções e CI mínima.

`FT-010` — **concluída**: workflow em cada `push` para `main` e em cada
`pull_request`, com validação explícita dos nove JSON Schemas, sete exemplos
versionados e suíte automatizada. O aceite e seus limites estão em
`docs/CI_MINIMA_FT_010.md`.

**Saída:** G0 aprovado.

### Fase 1 — núcleo comum e contrato v1

- produto-alvo;
- regimes e envelopes versionados;
- unidades e validação;
- contratos JSON;
- worker determinístico;
- relatório mínimo;
- testes positivos, negativos e limites.

**Saída:** casos válidos são executados; recomendações continuam bloqueadas.

### Fase 2 — LTFT mínimo útil

- ASF em base de carbono;
- catalisadores Co/Fe separados;
- `FT-013` **concluída**: caso experimental completo, agrupado e reproduzível,
  com impressão digital determinística e sem inventar resultados medidos;
- balanços C/H/O;
- ingestão e revisão de evidência;
- comparação ASF versus experimento;
- interface web LTFT.

**Saída:** análise LTFT reproduzível, sem cinética inventada.

### Fase 3 — validação LTFT

- corpus licenciável e aprovado;
- critérios de compatibilidade;
- incerteza e domínio;
- modelo quantitativo escolhido após revisão;
- validação externa;
- planejamento experimental piloto.

**Saída:** orientação LTFT limitada ao domínio validado.

### Fase 4 — preparação HTFT

- caso de uso inicial;
- schema e taxonomia HTFT;
- métricas O/P e reações secundárias;
- corpus separado;
- interface em homologação;
- testes de bloqueio cruzado.

**Saída:** diagnóstico HTFT descritivo; recomendação bloqueada.

### Fase 5 — validação HTFT

- balanços e qualidade analítica;
- modelos candidatos;
- validação externa;
- estabilidade, coque, fase e gradientes;
- aceite científico independente.

**Saída:** orientação HTFT somente após aprovação.

### Fase 6 — modelagem de processo e avaliação técnico-econômica

Esta fase começa pelo LTFT e só avança de descrição para predição após o corpus,
os balanços e o modelo quantitativo passarem pelas portas científicas.

- `FT-057` — **concluída**: contrato v1 do modelo cinético com variáveis,
  parâmetros, unidades, domínio, fontes, incerteza e porta de validação;
- `FT-058` — implementar o primeiro modelo de reator LTFT com balanços molares,
  geometria, vazão/GHSV ou WHSV, pressão, calor e massa, queda de pressão e
  desativação quando aplicáveis;
- `FT-059` — selecionar e validar propriedades termodinâmicas, equação de estado,
  regras de mistura, pseudocomponentes e equilíbrio vapor–líquido de água,
  hidrocarbonetos e ceras;
- `FT-060` — integrar balanços de massa e energia do gás de síntese à síntese FT
  e ao upgrading, distinguindo oxigênio coproduzido na eletrólise de oxigênio
  consumido em gaseificação;
- `FT-061` — definir contrato técnico-econômico, fronteira, capacidade, moeda,
  ano-base, vida útil, disponibilidade, preços e cenários;
- `FT-062` — calcular CAPEX, OPEX, consumo e custo de H2/gás de síntese,
  eletricidade, intensidade de carbono e custo mínimo do combustível por
  unidade de massa, volume e energia, com sensibilidade e incerteza;
- `FT-063` — validar o fluxo integrado fora da amostra e documentar balanços,
  resíduos, limites, rastreabilidade e revisão independente.

`solve_ivp`, Cantera, Thermo ou bibliotecas equivalentes são meios de cálculo,
não validação científica. A escolha de biblioteca deverá registrar modelos,
parâmetros, fases, faixa de validade e comparação com dados experimentais.
Conversão e seletividade não poderão ser inferidas apenas de temperatura e
pressão: exigem cinética calibrada, catalisador, alimentação, vazão/tempo de
residência, tipo de reator, transporte, WGS, desativação e domínio aplicável.

**Saída:** simulador de processo rastreável e avaliação econômica por cenários;
`recommendation_blocked=true` permanece enquanto calibração e validação externa
forem insuficientes.

### Fase 7 — DFT

- protocolo por regime/família;
- cadastro estrutural;
- geradores e validadores de entrada;
- orquestração computacional;
- parsing e testes de convergência;
- associação a evidência e modelos.

**Saída:** cálculo rastreável, sem promovê-lo automaticamente a recomendação.

### Fase 8 — plataforma multiusuário

- banco e armazenamento de artefatos;
- autenticação e perfis;
- fila de workers;
- projetos, compartilhamento controlado e auditoria;
- exportações e API;
- administração e observabilidade.

### Fase 9 — homologação e produção

- ambientes separados;
- migrações, backup e recuperação;
- carga, segurança e testes de fumaça;
- aceite científico, técnico e operacional;
- versão imutável e rollback;
- suporte, treinamento e resposta a incidentes.

## 12. Cronograma de referência

O cronograma depende da equipe e da disponibilidade de dados. A referência abaixo
pressupõe uma equipe pequena com participação científica regular.

| Período | Entrega principal |
|---|---|
| Próximo ciclo, semanas 1–4 | Fase UX prioritária (`FT-049` a `FT-056`) |
| Após a Porta UX, semanas 5–6 | CI mínima concluída; retomada das demais pendências de fundação |
| Semanas 7–12 | consolidação do LTFT mínimo útil |
| Semanas 13–18 | corpus, balanços e validação LTFT inicial |
| Semanas 19–24 | planejamento experimental e homologação LTFT |
| Semanas 25–30 | contrato, corpus e interface HTFT bloqueada |
| Semanas 31–38 | validação HTFT inicial |
| Semanas 39–46 | modelagem de reator, termodinâmica e balanço energético |
| Semanas 47–52 | avaliação técnico-econômica e validação integrada |
| Semanas 53–60 | DFT mínimo e integração rastreável |
| Semanas 61–68 | multiusuário, produção e operação |

O avanço é governado pelas portas de qualidade, não apenas pelas datas.

## 13. Equipe mínima sugerida

- 1 responsável de produto/projeto;
- 1 especialista Fischer–Tropsch/LTFT;
- 1 especialista HTFT/Fe quando essa trilha iniciar;
- 1 engenheiro de dados/backend;
- 1 desenvolvedor frontend/full-stack;
- apoio de estatística/ML;
- apoio de engenharia de processos, termodinâmica e economia na Fase 6;
- apoio de DFT quando a Fase 7 iniciar;
- apoio de DevOps/segurança na preparação de produção;
- operadores/analistas do laboratório para aceite.

Funções podem acumular pessoas, mas aprovações científicas e implementação devem
ser revisadas por pessoas distintas sempre que possível.

## 14. Métricas

### Produto e uso

- taxa de casos completos;
- tempo até relatório reproduzível;
- taxa de bloqueios compreendidos pelo usuário;
- número de exportações/reutilizações;
- satisfação por perfil.

### Dados

- percentual com proveniência/licença/unidades completas;
- percentual verificado e aprovado;
- taxa de balanços aceitos;
- cobertura por regime, catalisador e produto;
- duplicatas e conflitos detectados.

### Modelos

- erro e calibração de incerteza fora da amostra;
- cobertura do domínio;
- estabilidade entre versões;
- taxa de extrapolação bloqueada;
- diferença entre orientação e resultado experimental.

### Operação

- disponibilidade e latência;
- falhas por execução;
- tempo de recuperação;
- sucesso de backup/restauração;
- incidentes e vulnerabilidades abertas.

## 15. Riscos e mitigação

| Risco | Impacto | Mitigação |
|---|---|---|
| dados heterogêneos | comparação incorreta | contratos, unidades e compatibilidade |
| poucos dados | sobreajuste | modelos simples, validação externa e bloqueio |
| mistura LTFT/HTFT | extrapolação inválida | módulos e corpus separados |
| ASF interpretada como cinética | afirmação enganosa | rótulo, testes e relatório explícito |
| fase ativa incerta | atribuição causal indevida | estado medido/inferido/hipotético |
| estrutura incompleta para DFT | cálculo inválido | porta estrutural obrigatória |
| vazamento de dados | resultado otimista | divisão por fonte/lote/grupo |
| dados restritos publicados | risco legal | licença, classificação e revisão |
| recomendações inseguras | risco operacional | limites do laboratório e aprovação humana |
| dívida de protótipo | baixa confiabilidade | contratos, CI, migrações e observabilidade |

## 16. Portas de decisão

| Porta | Decisão |
|---|---|
| G0 | governança e escopo aprovados |
| G1 | contrato comum e unidades estáveis |
| L1 | LTFT mínimo cientificamente consistente |
| L2 | evidência LTFT aprovada para calibração |
| L3 | modelo LTFT validado externamente |
| L4 | plano experimental LTFT aceito |
| H0 | caso de uso HTFT aprovado |
| H1 | contrato e corpus HTFT adequados |
| H2 | modelo HTFT validado externamente |
| D1 | estruturas e protocolo DFT aprovados |
| O1 | homologação científica/técnica concluída |
| O2 | produção, backup, rollback e monitoramento ativos |

## 17. Critério de pronto

Uma funcionalidade científica está pronta somente quando possui:

- requisito e responsável;
- contrato versionado;
- unidades e proveniência;
- código revisado;
- testes positivos, negativos, limites e regressão;
- incerteza e domínio quando aplicável;
- documentação e exemplo reproduzível;
- aceite científico.

Uma implantação está pronta somente quando acrescenta:

- ambiente e versão identificados;
- migrações verificadas;
- permissões mínimas;
- backup e restauração testados;
- rollback;
- logs, métricas e alertas;
- teste de fumaça e aceite operacional.

## 18. Próxima atividade recomendada

Concluir as portas científicas de `FT-058` e `FT-059`: selecionar uma hipótese
cinética LTFT com parâmetros e domínio rastreáveis e qualificar dados de
comparação termodinâmica para os pacotes candidatos. A infraestrutura de ambos
foi implementada, mas permanece parcial e bloqueada para previsões. `FT-060`
somente deve começar após essas duas validações.

## 19. Decisões ainda necessárias

1. primeiro produto-alvo e caso LTFT de validação;
2. tolerâncias de balanço C/H/O;
3. critérios de estado estacionário;
4. fontes de dados e licenças permitidas;
5. infraestrutura e identidade de acesso;
6. primeiro caso HTFT;
7. engines e recursos DFT;
8. responsáveis por cada porta de aprovação;
9. modelo cinético, parâmetros e domínio para o primeiro reator LTFT;
10. propriedades de referência e critérios de aceite termodinâmico.

Essas decisões não devem ser preenchidas silenciosamente pelo software.
