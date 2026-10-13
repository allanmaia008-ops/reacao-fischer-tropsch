# Notebooks da plataforma Fischer–Tropsch

Os notebooks são interfaces de exploração e validação. A lógica científica e
as regras de domínio permanecem em `src/plataforma_ltft/`, que também é usada
pelo worker e pela aplicação Streamlit.

## Ordem recomendada

1. `01_produto_asf.ipynb`: escolha do produto e distribuição ASF qualitativa;
2. `02_contrato_catalisador.ipynb`: contrato e validação do catalisador;
3. `03_unidades_canonicas.ipynb`: normalização de condições experimentais;
4. `04_auditoria_evidencias.ipynb`: inventário e limites das evidências;
5. `05_caso_experimental_ltft.ipynb`: montagem e execução de um caso LTFT;
6. `06_preparacao_htft.ipynb`: estrutura inicial de HTFT, ainda bloqueada para
   recomendação experimental.

Cada arquivo pode ser executado e corrigido isoladamente. Alterações em
equações, contratos ou validações devem ser feitas primeiro no pacote Python;
os notebooks não devem conter cópias dessas funções.

## Regeneração e verificação

```powershell
py tools\generate_notebook.py
py tools\validate_notebooks.py
py -m unittest discover -s tests -v
```

O notebook histórico `fluxo_ltft.ipynb` é preservado somente como referência e
não compõe a sequência modular oficial.
