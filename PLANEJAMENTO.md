# Plano de implementação e implantação — Reação Fischer–Tropsch

## 1. Objetivo e fronteira

Construir uma plataforma própria para orientar estudos Fischer–Tropsch em baixa
temperatura a partir do hidrocarboneto desejado, das condições operacionais, do
catalisador e da evidência disponível.

O projeto não é uma evolução do CataILab. O diretório `../CataILab_LTFT/` e os
arquivos em `reference_results/legacy_catailab/` são referências históricas, não
dependências de código, dados calibrados ou runtime da nova plataforma.

A plataforma deve sempre distinguir:

1. composição proposta;
2. estrutura atômica conhecida;
3. hipótese estrutural;
4. proxy ou orientação heurística;
5. cálculo DFT;
6. resultado experimental.

## 2. Estado atual

Legenda: `CONCLUÍDO`, `EM CURSO`, `PLANEJADO`, `BLOQUEADO`.

| Componente | Estado | Evidência atual |
|---|---|---|
| Pacote Python independente | CONCLUÍDO | `src/plataforma_ltft/` |
| Contrato e validação das entradas | CONCLUÍDO | `domain.py` e testes |
| Seleção do hidrocarboneto-alvo | CONCLUÍDO | faixas e C1–C60 |
| Distribuição ASF em base de carbono | CONCLUÍDO | fechamento testado |
| Worker local por JSON | CONCLUÍDO | execução ponta a ponta |
| Notebook próprio | CONCLUÍDO | gerador e notebook compilável |
| Evidência histórica segregada | CONCLUÍDO | `data/evidence/` |
| Orientação quantitativa de condições | BLOQUEADO | faltam modelos calibrados |
| Ranking de catalisadores | BLOQUEADO | faltam critérios e dados aprovados |
| Interface de usuário | PLANEJADO | arquitetura ainda não aprovada |
| DFT/adsorção | PLANEJADO | protocolo e estruturas ainda ausentes |
| Implantação pública | BLOQUEADO | depende dos marcos G1–G7 |

## 3. Trilhas de trabalho

### Trilha A — produto científico

- Definir produto-alvo, base da seletividade e função-objetivo.
- Separar famílias Co, Fe e Co–Fe exploratória.
- Qualificar evidências por origem, condição, unidade, incerteza e aplicabilidade.
- Implementar modelos somente quando houver equação, parâmetros, unidades e
  conjunto de validação compatível.
- Manter recomendações bloqueadas quando faltarem entradas críticas.

### Trilha B — engenharia da plataforma

- Evoluir contratos e esquemas versionados.
- Implementar serviços de materiais, evidência, triagem e exportação.
- Criar persistência, fila de workers e rastreabilidade das execuções.
- Construir interface própria após estabilizar os contratos.
- Automatizar testes unitários, integração, regressão científica e segurança.

### Trilha C — implantação operacional

- Definir ambientes de desenvolvimento, homologação e produção.
- Configurar autenticação, autorização, segredos, logs e backups.
- Publicar primeiro em homologação com dados não sensíveis.
- Executar aceite científico e operacional.
- Promover uma versão imutável para produção e manter plano de reversão.

## 4. Fases e portas de decisão

### Fase 0 — governança do projeto

**Estado:** EM CURSO

Entregáveis:

- nome e identidade próprios;
- responsáveis por produto, ciência, dados e operação;
- catálogo de decisões e critérios de mudança;
- política de licença, autoria, privacidade e uso dos dados.

**Porta G0:** escopo, responsáveis e política de dados aprovados.

### Fase 1 — contrato científico mínimo

**Estado:** CONCLUÍDO (G1 atingida em 2026-09-25)

Entregáveis existentes:

- seleção do produto antes do catalisador;
- contrato para composição, família ativa, fase, suporte, carga e condições;
- ASF condicional ao `alpha` informado;
- bloqueio de cinética e recomendação não sustentadas.

Entregáveis adicionais concluídos:

- promotor, precursor, ativação, alimentação, vazão, GHSV/WHSV, leito e tempo;
- unidades canônicas e regras condicionais;
- esquemas v1 para caso, evidência e resultado;
- exemplos completo e inválido e testes de limites.

**Porta G1:** esquema versionado, exemplos válidos/inválidos e testes de unidades.

### Fase 2 — curadoria e qualificação da evidência

**Estado:** EM CURSO

Concluído em 2026-09-27:

- esquemas específicos dos três CSVs;
- validação de cabeçalhos, tipos, ausências, duplicatas e limites;
- fechamento das seletividades de hidrocarbonetos;
- manifesto, hashes e compatibilidade contextual com o caso LTFT;
- relatório JSON reproduzível que impede calibração e ranking automáticos.

Entregáveis:

- manifesto por fonte e licença;
- leitura e validação do esquema dos três CSVs existentes;
- vínculo de cada observação à composição, preparação e condições;
- estados `metadado`, `leitura integral`, `extraído`, `verificado` e `aprovado`;
- relatório de lacunas para cinética, conversão e seletividade.

Os resultados históricos continuam fora do conjunto de calibração até reprodução
e aprovação explícitas.

**Porta G2:** conjunto de evidências rastreável, validado e aprovado para um caso de uso.

### Fase 3 — motor de orientação e triagem

**Estado:** fundação ASF CONCLUÍDA; motor completo PLANEJADO

Sequência:

1. produto desejado;
2. orientação ASF e definição da métrica-alvo;
3. seleção comparativa de famílias catalíticas;
4. intervalo experimental permitido pela evidência;
5. análise de sensibilidade e domínio de aplicabilidade;
6. recomendação apenas quando critérios de aceite forem satisfeitos.

Não adotar automaticamente o funil legado `1000 → 100 → 10 → 2`. As cotas e o
ranking devem nascer de objetivos, custos, diversidade e evidência aprovados.

**Porta G3:** resultados reproduzíveis em conjunto de validação, com limitações e
incerteza reportadas.

### Fase 4 — materiais e estruturas

**Estado:** PLANEJADO

Entregáveis:

- entrada por fórmula, elementos, identificador de base ou CIF;
- fórmula/elementos tratados como espaço químico, nunca como estrutura confirmada;
- recuperação e validação de estruturas completas;
- proveniência, simetria, ocupação, carga, spin e estado estrutural;
- hipóteses neurais rotuladas e separadas das estruturas conhecidas.

**Porta G4:** somente estruturas completas e validadas podem seguir para DFT.

### Fase 5 — DFT e adsorção

**Estado:** BLOQUEADO até G4 e aprovação do protocolo

Entregáveis:

- protocolo explícito de superfície, faceta, terminação e adsorbato;
- três energias comparáveis: sistema adsorvido, superfície limpa e adsorbato isolado;
- cálculo de `E_ads = E_superfície+adsorbato − E_superfície − E_adsorbato`;
- configurações de funcional, dispersão, spin, carga, slab, vácuo, cobertura,
  pseudopotenciais/bases, cutoff e pontos k;
- adaptadores independentes para os engines aprovados;
- validação sintática e reconstrução cruzada antes da execução.

**Porta G5:** pacote DFT validado para execução no programa-alvo. Arquivo gerado
não equivale a cálculo executado ou resultado confirmado.

### Fase 6 — interface e experiência do usuário

**Estado:** PLANEJADO após G1–G3

Fluxo proposto:

1. escolher hidrocarboneto/faixa desejada;
2. informar alimentação e restrições experimentais;
3. selecionar ou comparar família catalítica;
4. definir composição, suporte, carga, promotor e ativação;
5. visualizar evidências aplicáveis e lacunas;
6. executar orientação/triagem;
7. revisar hipóteses, incertezas e domínio;
8. exportar relatório auditável;
9. opcionalmente preparar DFT após G4/G5.

A interface deve mostrar diretamente se cada valor é entrada, evidência,
heurística, proxy, DFT ou experimento.

**Porta G6:** teste de usabilidade e aceite científico sem afirmações enganosas.

### Fase 7 — homologação

**Estado:** BLOQUEADO até G3 e G6

Entregáveis:

- ambiente separado de produção;
- banco e armazenamento de artefatos com backups testados;
- autenticação e perfis de acesso;
- logs estruturados, métricas, alertas e trilha de auditoria;
- testes de carga, recuperação, segurança e reprodutibilidade;
- casos de aceite com resultados esperados e tolerâncias.

**Porta G7:** aceite conjunto científico, técnico e operacional.

### Fase 8 — produção e operação

**Estado:** BLOQUEADO até G7

Entregáveis:

- versão imutável e identificada;
- migrações e backups verificados;
- plano de rollback;
- monitoramento e resposta a incidentes;
- política de revalidação quando dados, modelos ou protocolos mudarem;
- documentação e treinamento dos usuários.

**Porta G8:** publicação confirmada, teste de fumaça e observabilidade ativa.

## 5. Próximo ciclo recomendado

O próximo ciclo deve avançar G2, nesta ordem:

1. localizar e registrar URL/DOI e licença de cada fonte;
2. verificar a leitura integral e conferir cada valor contra a tabela original;
3. promover registros conferidos de `extraido` para `verificado`;
4. escolher um único caso de uso para o primeiro aceite científico;
5. só então definir o primeiro método quantitativo além da ASF.

## 6. Critérios globais de pronto

Uma funcionalidade só está concluída quando possui:

- requisito e responsável definidos;
- esquema/contrato versionado;
- código sem dependência do runtime legado;
- testes positivos, negativos e de limites;
- proveniência e unidades;
- documentação de uso e limitações;
- artefato reproduzível;
- aceite científico quando produzir orientação ou resultado científico.

Uma implantação só está concluída quando, além dos itens acima, possui ambiente
identificado, versão implantada, migrações concluídas, backup, rollback, logs,
monitoramento e teste de fumaça registrados.

## 7. Decisões pendentes

1. Nome público e identidade visual.
2. Caso de uso LTFT inicial para aceite.
3. Arquitetura da interface e infraestrutura de implantação.
4. Modelo de autenticação e perfis de usuário.
5. Banco de dados e política de retenção.
6. Fontes experimentais autorizadas para calibração.
7. Métricas e critérios do futuro ranking.
8. Protocolo DFT, engines e recursos computacionais.

Nenhuma dessas decisões será preenchida silenciosamente pelo sistema.
