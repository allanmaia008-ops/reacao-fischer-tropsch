# Reação Fischer–Tropsch

Projeto novo e independente para triagem científica Fischer–Tropsch em baixa temperatura.
Este diretório é o produto em construção. `../CataILab_LTFT/` é somente uma referência
histórica de requisitos, fluxos e limitações; não é dependência, base de código ou
runtime desta plataforma.

Estado atual: núcleo mínimo executável com interface Streamlit, domínio, ASF,
worker JSON, notebook e evidência versionada. Ainda não existe motor de ranking,
modelo cinético calibrado, integração DFT ou recomendação final.

A página inicial apresenta a proposta, as ações principais e o estado científico
de LTFT, HTFT e recomendações. A partir dela, a interface usa um fluxo guiado em
seis etapas — produto, regime, catalisador, condições, resultados e evidências —
com progresso, pendências e estado persistente durante a sessão. Esse progresso
representa preenchimento da interface e não substitui validação científica.

O sistema visual usa componentes responsivos, foco de teclado visível e suporte
a preferência de movimento reduzido. Os campos são agrupados por contexto, têm
unidades e ajuda próximas e exibem pendências antes da confirmação.

O painel de resultados apresenta a curva ASF em base de carbono de C1 a C60,
destaca a faixa-alvo e fecha a distribuição com a cauda analítica C61+ até C∞.
Também separa as condições usadas, a prontidão científica e os bloqueios. As
faixas de Cn não são tratadas automaticamente como produtos comerciais.

Os resultados recebem categorias rastreáveis de maturidade e podem ser
comparados em dois ou três cenários de α. Essa comparação é uma sensibilidade
matemática e mantém a recomendação experimental bloqueada.

## Interface web

```powershell
py -m streamlit run app.py
```

O arquivo principal de publicação no Streamlit Community Cloud é `app.py`. O
rótulo público da aplicação é **Projeto Fischer–Tropsch**.

### Publicação no Streamlit Community Cloud

1. Conecte a conta GitHub no Streamlit Community Cloud.
2. Selecione o repositório `allanmaia008-ops/reacao-fischer-tropsch`.
3. Use a branch `main` e o arquivo principal `app.py`.
4. Esta versão não requer secrets.

O contrato científico atual é o v2. Consulte [docs/CONTRATO_V2.md](docs/CONTRATO_V2.md),
o contrato v1 preservado para compatibilidade e os JSON Schemas em
[schemas/](schemas/README.md).

O contrato para futuros modelos cinéticos está definido em
[docs/CONTRATO_CINETICO_V1.md](docs/CONTRATO_CINETICO_V1.md). Nenhuma equação é
executada enquanto o contrato não estiver completo e validado.

A infraestrutura do primeiro modelo de reator LTFT e o contrato termodinâmico
estão documentados em [docs/MODELO_REATOR_LTFT_V1.md](docs/MODELO_REATOR_LTFT_V1.md)
e [docs/CONTRATO_TERMODINAMICO_V1.md](docs/CONTRATO_TERMODINAMICO_V1.md).
Ambos estão em estado parcial: validam a preparação e preservam os bloqueios,
mas não calculam conversão, produtividade ou equilíbrio de fases antes da
seleção, calibração e comparação dos modelos com dados rastreáveis.

## Princípios

- Distinguir composição, estrutura conhecida, hipótese estrutural, proxy, DFT e experimento.
- Manter fase ativa, suporte, carga e condições operacionais como campos distintos.
- Tratar Co e Fe como famílias catalíticas distintas; Co–Fe requer hipótese explícita.
- Bloquear recomendação quando faltarem dados críticos; não inventar parâmetros cinéticos.
- Registrar origem, método, unidades e incerteza de cada evidência.
- Não usar o escore ou os priors heurísticos do CataILab como previsão validada.

## Seleção do hidrocarboneto-alvo

O caso deve informar `desired_product`. São aceitos `CH4`, `C2-C4`, `C5-C11`,
`C12-C20`, `C21+`, `C5+` e hidrocarbonetos individuais de `C1` a `C60`.
Também são reconhecidos os atalhos `metano`, `gasolina`, `diesel` e `ceras`.

A seleção gera:

- orientação matemática de `alpha` pela distribuição ASF;
- perguntas para comparar famílias Co e Fe;
- direção qualitativa para temperatura, pressão e H2/CO;
- lista dos ensaios e dados necessários antes de uma recomendação final.

Ela não promete produto puro, não calcula conversão e não escolhe automaticamente
um catalisador ou condição experimental sem calibração específica.

O planejamento pode começar somente pelo produto, antes de escolher catalisador:

```powershell
$env:PYTHONPATH = "$PWD\src"
py -m plataforma_ltft.worker --config examples\planejar_produto.json --output outputs\planejamento_produto
```

## Testes

No diretório do projeto:

```powershell
py -m unittest discover -s tests -v
```

Validação explícita dos contratos JSON usada pela CI:

```powershell
py tools\validate_schemas.py
```

Consulte [docs/CI_MINIMA_FT_010.md](docs/CI_MINIMA_FT_010.md) para os gatilhos,
portas e limites do aceite da FT-010.

## Execução pelo worker

```powershell
$env:PYTHONPATH = "$PWD\src"
py -m plataforma_ltft.worker --config examples\caso_co.json --output outputs\caso_co
```

O arquivo `resultado_ft.json` contém distribuição ASF condicional ao `alpha`
informado. Ele não produz conversão, produtividade ou extensão WGS.

Quando o caso contém todos os campos experimentais, o resultado também inclui
um resumo agrupado e uma impressão digital determinística. Isso comprova a
reprodutibilidade das entradas, não a execução do experimento. Consulte
[docs/ACEITE_FT_013.md](docs/ACEITE_FT_013.md).

O worker migra casos LTFT v1 para o contrato v2 de forma explícita. Casos de
transição e HTFT exigem `schema_version: 2.0.0`, regime declarado e envelope
versionado. Consulte [docs/CONTRATO_V2.md](docs/CONTRATO_V2.md).

## Notebooks modulares

```powershell
py tools\generate_notebook.py
```

O gerador mantém seis notebooks independentes em `notebooks/`, todos importando
o pacote oficial `plataforma_ltft` em vez de duplicar regras científicas:

1. `01_produto_asf.ipynb` — produto-alvo e orientação ASF;
2. `02_contrato_catalisador.ipynb` — cadastro e validação do catalisador;
3. `03_unidades_canonicas.ipynb` — conversões e rastreabilidade de unidades;
4. `04_auditoria_evidencias.ipynb` — auditoria não destrutiva de evidências;
5. `05_caso_experimental_ltft.ipynb` — caso completo e triagem LTFT;
6. `06_preparacao_htft.ipynb` — contrato HTFT com recomendação bloqueada.

`fluxo_ltft.ipynb` permanece como demonstração histórica simples. A manutenção
deve ocorrer primeiro nos módulos de `src/plataforma_ltft/`; depois, execute o
gerador para atualizar os notebooks.

Validação rápida dos seis fluxos, sem depender de um kernel Jupyter instalado:

```powershell
py tools\validate_notebooks.py
```

Essa validação executa as células de código em ordem e complementa os testes
estruturais de `tests/test_notebooks.py`. Para exploração interativa, abra cada
arquivo em Jupyter ou VS Code e selecione um ambiente com o pacote instalado.

## Evidência e resultados históricos

- `data/evidence/`: CSVs de evidência importados com sua condição de uso.
- `reference_results/legacy_catailab/`: resultados históricos preservados somente
  para comparação e auditoria. Eles não foram gerados pela nova plataforma.

Os CSVs com licença ainda não verificada e os resultados históricos são mantidos
somente no ambiente local e não integram o repositório público.

Auditoria dos CSVs:

```powershell
py tools\audit_evidence.py --case examples\caso_experimental_completo.json --output outputs\evidence_audit.json
```

Consulte [docs/VALIDACAO_EVIDENCIAS.md](docs/VALIDACAO_EVIDENCIAS.md).

## Balanços elementares

Os balanços C/H/O usam correntes molares declaradas, composição atômica por
espécie, base de medição e tolerância configurável:

```powershell
py tools\calculate_elemental_balance.py --input examples\balanco_elementar_demonstracao.json --output outputs\balanco_elementar_demonstracao.json
```

O exemplo é sintético e valida o cálculo, não um resultado experimental.
Consulte [docs/BALANCOS_ELEMENTARES_FT_014_015.md](docs/BALANCOS_ELEMENTARES_FT_014_015.md).

## Comparação ASF versus medição

A FT-017 possui uma infraestrutura inicial para alinhar a base de carbono,
calcular resíduos e incorporar incertezas sem promover dados não aprovados:

```powershell
py tools\compare_asf_measurement.py --input examples\comparacao_asf_medicao_sintetica.json --output outputs\comparacao_asf_medicao_sintetica.json
```

O exemplo é sintético e mantém a validação de modelo bloqueada. Consulte
[docs/COMPARACAO_ASF_MEDICAO_FT_017.md](docs/COMPARACAO_ASF_MEDICAO_FT_017.md).

As extensões aprovadas para ASF avançada, contrato experimental v2,
diagnósticos de transporte e seleção de modelo estão em
[docs/PLANO_ASF_AVANCADA_TRANSPORTE.md](docs/PLANO_ASF_AVANCADA_TRANSPORTE.md).

Implementações concluídas:

- [ASF avançada FT-012A](docs/ASF_AVANCADA_FT_012A.md);
- [contrato experimental v2 FT-013A](docs/CONTRATO_EXPERIMENTAL_V2_FT_013A.md).

Ver [PLANEJAMENTO.md](PLANEJAMENTO.md) para a sequência LTFT/HTFT, as portas de
validação e as decisões pendentes. A separação científica dos regimes está em
[docs/ESCOPO_LTFT_HTFT.md](docs/ESCOPO_LTFT_HTFT.md).

## Planejamento consolidado

- [Planejamento mestre da plataforma](PLANEJAMENTO_MESTRE.md)
- [Plano de implementação LTFT/HTFT](PLANEJAMENTO.md)
- [Arquitetura-alvo](docs/ARQUITETURA_ALVO.md)
- [Backlog inicial priorizado](docs/BACKLOG_INICIAL.md)
- [Charter científico e aceite da FT-001](docs/CHARTER_FT_001.md)
- [Catálogo de unidades canônicas](docs/UNIDADES_CANONICAS.md)
- [Contrato de catalisador v1](docs/CONTRATO_CATALISADOR_V1.md)
- [Planilha de atividades e status](docs/Planilha_Atividades_Plataforma_Fischer_Tropsch.xlsx)
- [Escopo científico LTFT/HTFT](docs/ESCOPO_LTFT_HTFT.md)

O planejamento mestre amplia o roteiro existente sem substituir os contratos,
testes, módulos LTFT/HTFT ou as restrições científicas já implementadas.
