# Plano de construção e implantação — Reação Fischer–Tropsch

## 1. Objetivo e fronteira científica

Construir uma plataforma própria para planejar, registrar e comparar estudos da
reação Fischer–Tropsch a partir do produto desejado. A primeira linha de produto
é **LTFT**; a linha **HTFT** será preparada em contratos e arquitetura antes de
receber modelos ou recomendações.

O projeto não é uma evolução do CataILab. O legado é somente referência
histórica. Código, dados, identidade, execução e validação são independentes.

A plataforma separa: entrada; evidência rastreável; hipótese; orientação ASF ou
proxy; modelo calibrado; DFT executado; e recomendação experimental aprovada.

## 2. Dois regimes, dois domínios

LTFT e HTFT não serão tratados como uma simples troca de temperatura. Cada
regime terá contrato, dados, validação, modelos, métricas e relatório próprios.

| Aspecto | Linha LTFT | Linha HTFT preparada |
|---|---|---|
| Objetivo inicial | destilados médios, parafinas e ceras | olefinas leves, gasolina e coprodutos |
| Famílias iniciais | Co e Fe, comparadas separadamente | Fe e Fe promovido; demais exigem evidência |
| Reações paralelas | WGS registrada, especialmente para Fe | WGS, Boudouard, metanação e secundárias obrigatórias |
| Produtos mínimos | parafinas, olefinas, oxigenados e faixas Cn | resolução reforçada de olefinas/isômeros |
| Riscos centrais | água, desativação, transferência de massa/calor | coque, carbetos, hot spots e reações secundárias |
| Estado | núcleo funcional, sem cinética calibrada | arquitetura a construir; recomendações bloqueadas |

As faixas operacionais não serão universais. O envelope inicial de roteamento é
`LTFT = 180–260 °C`, `transição = >260–<280 °C` e `HTFT = 280–350 °C`.
São rótulos configuráveis, com fonte e versão, não limites físico-químicos.
Casos na transição exigirão classificação explícita do usuário.

Detalhes: [docs/ESCOPO_LTFT_HTFT.md](docs/ESCOPO_LTFT_HTFT.md).

## 3. Estado real

| Componente | LTFT | HTFT | Evidência/condição |
|---|---|---|---|
| Interface Streamlit pública | CONCLUÍDO | BLOQUEADO | versão atual é somente LTFT |
| Produto-alvo antes do catalisador | CONCLUÍDO | PLANEJADO | reaproveitar conceito, não parâmetros |
| Contrato de caso | CONCLUÍDO v1 | PLANEJADO v2 | v2 adicionará `ft_regime` |
| ASF em base de carbono | CONCLUÍDO | PLANEJADO | validade deve ser avaliada por regime |
| Worker e JSON auditável | CONCLUÍDO | PLANEJADO | falta roteador de regime |
| Evidência rastreável | EM CURSO | BLOQUEADO | HTFT requer corpus próprio |
| Balanços C/H/O | PLANEJADO | PLANEJADO | pré-requisito para calibração |
| Cinética calibrada | BLOQUEADO | BLOQUEADO | faltam dados aprovados e domínio |
| Ranking de catalisadores | BLOQUEADO | BLOQUEADO | faltam critérios e validação externa |
| DFT/adsorção | PLANEJADO | PLANEJADO | protocolos separados por fase/superfície |
| Protótipo publicado | CONCLUÍDO | não aplicável | não equivale a produção validada |
| Produção observável | BLOQUEADO | BLOQUEADO | faltam autenticação, backup e rollback |

## 4. Arquitetura-alvo

```text
produto desejado
  -> classificador (LTFT | transição | HTFT)
  -> contrato específico
  -> evidências compatíveis
  -> motor do regime
       LTFT: ASF + validação + futuros modelos LTFT
       HTFT: ASF limitada + olefinas/WGS/secundárias + futuros modelos HTFT
  -> domínio, sensibilidade e incerteza
  -> relatório auditável
  -> recomendação bloqueada ou liberada por porta científica
```

- núcleo comum somente para unidades, proveniência, balanços e auditoria;
- adaptadores `ltft` e `htft`, sem condicionais dispersas;
- parâmetros calibrados em um regime são proibidos no outro;
- contratos e resultados são versionados, sem reinterpretar o v1;
- cada execução registra versões de dados, modelo, código e configuração;
- HTFT mantém `recommendation_blocked=true` até validação própria.

## 5. Consolidação LTFT

### LTFT-1 — contrato v2

Adicionar: `ft_regime` e fonte do envelope; gás completo, inertes, contaminantes
e umidade; reator/leito/diluente; temperaturas de entrada, leito e máxima;
pressão, vazão, GHSV/WHSV e tempo; preparo/ativação; base analítica e seletividade;
conversões CO/H2, CO2, água, balanços C/H/O, incerteza, replicatas e estado
estacionário.

**Aceite:** migração v1→v2, exemplos válidos/inválidos e testes de unidades,
limites e regras condicionais.

### LTFT-2 — qualidade experimental e balanços

- validar fechamento C/H/O com tolerância declarada;
- separar seletividade total, hidrocarbonetos, CO2 e oxigenados;
- registrar GC, calibração, fatores de resposta e espécies não identificadas;
- testar H2/CO declarado contra a alimentação real;
- sinalizar limitações de transporte e hot spots;
- exigir estado estacionário e histórico de desativação.

**Aceite:** relatório reproduzível; dados reprovados não entram em calibração.

### LTFT-3 — seletividade e ASF ampliada

- manter ASF ideal como referência matemática;
- comparar medição e ASF por número de carbono;
- medir desvios de C1, C2, olefinas e cauda pesada;
- admitir múltiplos `alpha` ou modelos não-ASF só após validação;
- propagar incerteza para as frações previstas;
- não inferir produto puro a partir de ASF isolada.

**Aceite:** regressão com dados sintéticos conhecidos e conjunto experimental
aprovado que não tenha sido usado no ajuste.

### LTFT-4 — catalisadores e domínio

- separar Co, Fe e Co–Fe exploratório;
- representar suporte, promotor, precursor, carga, dispersão e partícula;
- rotular fase ativa como medida, inferida ou hipotética;
- avaliar água, carbono, sinterização e transformação de fase;
- comparar apenas casos compatíveis e explicar inclusão/exclusão.

**Aceite:** nenhuma recomendação sem cobertura, incerteza, domínio e validação
externa.

### LTFT-5 — planejamento experimental

- gerar faixas candidatas, não ponto ótimo sem calibração;
- respeitar restrições de segurança/equipamento informadas pelo usuário;
- sugerir replicatas, brancos, ativação e pontos de verificação;
- permitir DOE somente no domínio aprovado;
- exportar premissas, controles, respostas e critérios de parada.

**Aceite:** revisão por especialista e piloto documentado; sem controle de
equipamento nesta fase.

## 6. Preparação HTFT

### HTFT-0 — escopo

Escolher um alvo: olefinas leves, gasolina, aromáticos ou outro corte. Não
combinar objetivos incompatíveis em um único escore.

Entregáveis: produto/base de seletividade; envelope de reator/alimentação/família;
espécies e balanços obrigatórios; critérios de sucesso/segurança; corpus HTFT
separado.

**Porta H0:** caso de uso e responsáveis científicos aprovados.

### HTFT-1 — contrato e taxonomia

Incluir Fe, promotores e evolução óxido/carbeto/carbono; olefinas/parafinas por
Cn e razão O/P; isômeros, aromáticos, oxigenados e não identificados; CO2/WGS,
água e balanços; coque e regeneração; gradiente/máximo térmico; transientes,
tempo e desativação por estágio.

**Porta H1:** schema, exemplos e bloqueio cruzado de parâmetros LTFT.

### HTFT-2 — evidência e reações secundárias

- extrair apenas estudos HTFT compatíveis;
- registrar WGS, Boudouard, metanação, craqueamento e readsorção;
- distinguir seletividade primária de produtos após reações secundárias;
- mapear temperatura, pressão, H2/CO, conversão e residência;
- registrar fase e carbono superficial quando medidos.

**Porta H2:** conjunto rastreável, aprovado e suficiente; antes disso, saídas
são descritivas e bloqueadas.

### HTFT-3 — motor mínimo

- ASF apenas como linha de base limitada;
- balanços e métricas de olefinas com incerteza;
- alertas de extrapolação, hot spot, coque e incompatibilidade;
- comparação de modelos fora da amostra;
- rejeição automática de modelos LTFT.

**Porta H3:** validação fora da amostra, resíduos, incerteza, domínio e revisão
científica independente.

### HTFT-4 — interface controlada

- seletor de regime antes das condições;
- mostrar mudança de contrato ao trocar LTFT↔HTFT;
- selo `experimental` durante homologação;
- impedir recomendação antes de H0–H3;
- testar em homologação antes do endereço público.

**Porta H4:** aceite científico, usabilidade e não regressão LTFT.

## 7. DFT e materiais

- LTFT: superfícies de Co/Fe, água e intermediários de crescimento;
- HTFT: carbetos de Fe, promotores, carbono superficial e olefinas;
- exigir superfície limpa, adsorbato isolado e sistema adsorvido;
- fórmula não substitui estrutura, superfície, cobertura ou spin;
- entrada gerada não equivale a cálculo executado;
- DFT não equivale a desempenho experimental.

**Porta DFT:** estrutura/protocolo validados, convergência, proveniência e revisão.

## 8. Engenharia e operação

Sequência: contratos v2 e roteador; persistência; worker idempotente/fila; API
versionada; interface com proveniência/bloqueios; exportações; autenticação e
auditoria; observabilidade, backup e rollback.

Ambientes: desenvolvimento com dados sintéticos/públicos; homologação com dados
aprovados; produção imutável e monitorada; integração futura de laboratório
separada e sem controle de equipamento no MVP.

O Streamlit atual é protótipo público; não satisfaz sozinho homologação ou
produção científica.

## 9. Portas de liberação

| Porta | Libera | Condição mínima |
|---|---|---|
| G0 | governança | escopo, responsáveis, licenças e política de dados |
| G1 | contrato comum | schemas, unidades, migração e testes |
| L1 | análise LTFT | LTFT-1 a LTFT-3 aceitos |
| L2 | orientação LTFT | LTFT-4 validado externamente |
| L3 | plano experimental | LTFT-5 revisado por especialista |
| H0 | desenvolvimento HTFT | caso de uso aprovado |
| H1 | ingestão HTFT | contrato e taxonomia próprios |
| H2 | calibração HTFT | evidência aprovada e suficiente |
| H3 | orientação HTFT | validação externa e revisão |
| H4 | exposição pública HTFT | homologação e não regressão LTFT |
| D1 | uso de DFT | protocolo, convergência e proveniência |
| O1 | produção | segurança, backup, rollback e observabilidade |

## 10. Próximos ciclos

### Ciclo 1 — consolidar LTFT

1. implementar `ft_regime` e contrato v2 sem quebrar v1;
2. adicionar balanços C/H/O e qualidade analítica;
3. qualificar um conjunto LTFT completo e licenciável;
4. comparar ASF com esse conjunto e quantificar desvios;
5. publicar relatório de validação sem liberar recomendação final.

### Ciclo 2 — preparar HTFT bloqueado

1. aprovar o primeiro produto-alvo HTFT;
2. criar schema e exemplos HTFT;
3. implementar roteador e bloqueio LTFT/HTFT;
4. criar testes de incompatibilidade e não regressão;
5. liberar só formulário e diagnóstico em homologação.

### Ciclo 3 — validar por portas

1. formar corpus HTFT rastreável;
2. validar balanços e métricas de olefinas;
3. comparar modelos fora da amostra;
4. executar aceite científico independente;
5. habilitar HTFT publicamente somente após H4.

## 11. Critério global de pronto

Funcionalidade científica pronta exige requisito, contrato, proveniência,
unidades, incerteza, testes, domínio, artefato reproduzível e aceite científico.
Implantação pronta também exige versão, migração, permissões, backup, rollback,
logs, monitoramento e teste de fumaça. Publicar código ou URL não basta.

## 12. Decisões pendentes

1. caso LTFT para validação externa;
2. tolerâncias de balanço e estado estacionário;
3. produto-alvo inicial HTFT;
4. limites versionados dos regimes;
5. corpus e licenças HTFT;
6. métricas para olefinas e reações secundárias;
7. homologação, persistência e autenticação;
8. protocolo DFT por regime e recursos computacionais.

Nenhuma decisão pendente será inferida silenciosamente.
