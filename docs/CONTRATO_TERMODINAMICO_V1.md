# Contrato termodinâmico Fischer–Tropsch v1

## Finalidade

O contrato prepara a seleção e comparação de propriedades antes de integrar
Cantera, Thermo ou outra biblioteca. Ele registra fornecedor e versão, equação
de estado, regra de mistura, mapeamento de componentes, pseudocomponentes, VLE,
faixa de aplicação, fontes, dados de validação e métricas de erro.

## Cobertura mínima

O pacote deve cobrir gás de síntese, água, hidrocarbonetos leves, líquidos e
ceras. A representação de C21+ precisa declarar como os pseudocomponentes são
construídos; uma cauda ASF não substitui propriedades termodinâmicas.

## Porta de validação

O estado `draft` permite cadastro. `compared` exige conjuntos de dados
identificados. `validated` exige também métricas quantitativas de erro dentro
das faixas de temperatura e pressão declaradas. Nenhum pacote é selecionado por
padrão nesta versão, pois ainda faltam os dados comparativos aprovados.
