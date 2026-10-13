# Charter científico da plataforma — FT-001

**Projeto:** Reação Fischer–Tropsch  
**Versão:** 1.0  
**Data da decisão:** 12 de outubro de 2026  
**Responsável pelo projeto:** Allan Maia  
**Decisão:** escopo e exclusões aprovados para a FT-001

## 1. Finalidade

Construir uma plataforma científica própria e independente para planejar,
registrar, executar e comparar estudos da reação Fischer–Tropsch. O fluxo parte
do hidrocarboneto ou corte desejado e mantém rastreáveis as condições, o
catalisador, as evidências, os modelos, as incertezas e a revisão humana.

A plataforma reduz o espaço de busca experimental. Ela não substitui a decisão
do especialista, a avaliação de segurança do laboratório nem a validação
experimental.

## 2. Identidade e independência

- o produto se chama **Reação Fischer–Tropsch**;
- o repositório e o runtime são próprios da plataforma;
- o CataILab é somente referência histórica de requisitos, fluxos e limitações;
- código, dados, modelos, resultados e validações do CataILab não constituem
  dependência nem evidência da nova plataforma;
- artefatos históricos preservados devem permanecer identificados como legado e
  fora da cadeia de resultados da plataforma.

## 3. Escopo aprovado

### 3.1 Núcleo comum

- seleção de produto individual entre C1 e C60 ou de corte de hidrocarbonetos;
- classificação explícita do regime como LTFT, transição, HTFT ou fora do
  envelope;
- contratos versionados para casos, catalisadores, evidências e resultados;
- unidades canônicas sem eliminar as unidades originais;
- proveniência, incerteza, revisão e estado de aprovação das evidências;
- validações físicas, dimensionais, de completude e, quando implementadas, de
  balanços C/H/O;
- execução reproduzível, exportação legível por máquina e relatório auditável;
- planejamento experimental sujeito a revisão humana;
- DFT como módulo opcional, separado da evidência experimental.

### 3.2 LTFT

- envelope inicial de roteamento entre 180 e 260 °C;
- famílias de Co e Fe tratadas separadamente;
- foco inicial em destilados médios, parafinas e ceras;
- ASF usada como referência matemática, nunca como prova de conversão,
  produtividade ou seletividade experimental completa;
- registro de água, WGS, desativação e limitações de transferência de massa e
  calor quando os dados estiverem disponíveis.

### 3.3 HTFT

- envelope inicial de roteamento entre 280 e 350 °C;
- linha própria, inicialmente descritiva e com recomendação bloqueada;
- foco inicial em Fe e Fe promovido, olefinas leves, gasolina e coprodutos;
- contratos, dados, parâmetros, modelos, métricas e validação separados de LTFT;
- representação de WGS, Boudouard, metanação, readsorção, craqueamento, coque,
  evolução de fase e gradientes térmicos quando suportada por evidências.

### 3.4 Transição e casos fora do envelope

- temperaturas acima de 260 e abaixo de 280 °C exigem classificação e
  justificativa explícitas;
- temperaturas abaixo de 180 ou acima de 350 °C exigem estudo específico;
- os envelopes são regras versionadas de roteamento, não fronteiras
  físico-químicas universais.

## 4. Fronteiras de evidência

Toda saída deve ser identificada como uma das seguintes categorias: entrada,
evidência, hipótese, heurística, modelo, DFT ou experimento.

- ASF e regras qualitativas são orientação matemática ou heurística;
- resultados importados não são evidência aprovada sem origem, licença,
  compatibilidade e revisão;
- estrutura inferida ou arquivo de entrada DFT não equivale a cálculo executado;
- energia de adsorção não comprova atividade, seletividade ou estabilidade;
- recomendação quantitativa exige domínio de aplicabilidade, incerteza,
  validação externa e aprovação humana;
- parâmetros e validações não atravessam LTFT e HTFT automaticamente.

## 5. Exclusões aprovadas para o escopo inicial

- controle direto de reator, instrumentos ou sistemas de segurança;
- recomendação autônoma de condição segura;
- previsão de conversão sem cinética calibrada e validada;
- promessa de produto puro com base apenas em ASF;
- ranking universal ou escolha automática de catalisadores;
- geração de estrutura cristalina confirmada somente por fórmula;
- uso cruzado de dados ou parâmetros LTFT/HTFT sem validação específica;
- publicação automática de dados restritos ou sem licença verificada;
- transformação automática de hipótese ou resultado legado em evidência;
- substituição da revisão científica, operacional ou de segurança humana.

## 6. Responsabilidades de decisão

| Decisão | Responsável pela proposta | Aprovação necessária |
|---|---|---|
| alterar escopo ou exclusões | responsável do projeto | responsável do projeto e registro versionado |
| alterar envelope de regime | desenvolvedor ou especialista científico | especialista científico e testes de regressão |
| aprovar evidência | curador de dados | especialista científico |
| liberar modelo quantitativo | desenvolvedor/modelador | validação externa e especialista científico |
| liberar plano experimental | pesquisador | especialista científico e responsável do laboratório |
| integrar equipamento | equipe técnica | revisão científica, operacional e de segurança |

Na ausência de um ocupante formal para um papel, a decisão correspondente
permanece bloqueada. O responsável do projeto não substitui automaticamente o
especialista científico ou o responsável de segurança.

## 7. Critérios de mudança

Qualquer alteração material deste charter exige:

1. nova versão do documento;
2. motivo e impacto registrados;
3. identificação das portas científicas afetadas;
4. revisão dos contratos, testes e documentos dependentes;
5. nova aprovação explícita.

## 8. Registro de aceite

A solicitação do responsável do projeto para finalizar a FT-001, em 12 de
outubro de 2026, constitui aprovação do escopo e das exclusões descritos nesta
versão. Assim, a **FT-001 está concluída**.

Este aceite não aprova toda a porta G0. Licença do projeto, política completa de
dados/autoria/segurança e designações formais adicionais continuam sendo
entregas independentes antes de declarar G0 concluída.

## 9. Documentos normativos relacionados

- [Planejamento mestre](../PLANEJAMENTO_MESTRE.md)
- [Plano de implementação LTFT/HTFT](../PLANEJAMENTO.md)
- [Escopo científico LTFT/HTFT](ESCOPO_LTFT_HTFT.md)
- [Arquitetura-alvo](ARQUITETURA_ALVO.md)
- [Backlog inicial](BACKLOG_INICIAL.md)

