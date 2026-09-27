# Reação Fischer–Tropsch

Projeto novo e independente para triagem científica Fischer–Tropsch em baixa temperatura.
Este diretório é o produto em construção. `../CataILab_LTFT/` é somente uma referência
histórica de requisitos, fluxos e limitações; não é dependência, base de código ou
runtime desta plataforma.

Estado atual: núcleo mínimo executável com interface Streamlit, domínio, ASF,
worker JSON, notebook e evidência versionada. Ainda não existe motor de ranking,
modelo cinético calibrado, integração DFT ou recomendação final.

## Interface web

```powershell
py -m streamlit run app.py
```

O arquivo principal de publicação no Streamlit Community Cloud é `app.py`.

### Publicação no Streamlit Community Cloud

1. Conecte a conta GitHub no Streamlit Community Cloud.
2. Selecione o repositório `allanmaia008-ops/reacao-fischer-tropsch`.
3. Use a branch `main` e o arquivo principal `app.py`.
4. Esta versão não requer secrets.

O contrato científico atual é o v1. Consulte [docs/CONTRATO_V1.md](docs/CONTRATO_V1.md)
e os JSON Schemas em [schemas/](schemas/README.md).

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

## Execução pelo worker

```powershell
$env:PYTHONPATH = "$PWD\src"
py -m plataforma_ltft.worker --config examples\caso_co.json --output outputs\caso_co
```

O arquivo `resultado_ltft.json` contém distribuição ASF condicional ao `alpha`
informado. Ele não produz conversão, produtividade ou extensão WGS.

## Notebook

```powershell
py tools\generate_notebook.py
```

O notebook gerado fica em `notebooks/fluxo_ltft.ipynb` e usa somente o pacote
`plataforma_ltft`.

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

Ver [PLANEJAMENTO.md](PLANEJAMENTO.md) para a sequência LTFT/HTFT, as portas de
validação e as decisões pendentes. A separação científica dos regimes está em
[docs/ESCOPO_LTFT_HTFT.md](docs/ESCOPO_LTFT_HTFT.md).
