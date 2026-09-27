# Escopo científico dos regimes LTFT e HTFT

## Finalidade

Define como a plataforma roteará casos de baixa e alta temperatura. Não
prescreve condições experimentais nem substitui avaliação de segurança ou
modelo calibrado.

## Envelope inicial

| Rótulo | Temperatura de referência | Comportamento |
|---|---:|---|
| LTFT | 180–260 °C | habilita contrato e motores LTFT |
| Transição | >260 e <280 °C | exige classificação explícita e justificativa |
| HTFT | 280–350 °C | habilita contrato HTFT, inicialmente bloqueado |
| Fora | <180 ou >350 °C | requer estudo específico e aprovação |

É uma convenção configurável. O regime efetivo também depende de catalisador,
fase, reator, composição, conversão e tempo de residência. Alterar o envelope
exige nova versão e regressão.

## Regras de separação

- parâmetros, modelos e validações pertencem a um regime;
- transição não entra automaticamente em calibração;
- modelos LTFT não são extrapolados para HTFT;
- ASF não modela atividade, conversão ou seletividade real completa;
- Co, Fe, carbetos e promotores são representados explicitamente;
- recomendação HTFT fica bloqueada até H0–H4.

## Saída mínima

**LTFT:** faixas Cn; parafinas/olefinas/oxigenados; conversões CO/H2; CO2/água;
balanços C/H/O; ASF versus medição; estabilidade e desativação.

**HTFT:** todos os itens LTFT; O/P por Cn; isômeros, aromáticos e não
identificados; WGS, metanação, Boudouard, craqueamento e readsorção; coque,
transformação de fase e gradiente térmico.

## Referências de escopo

- U.S. DOE/NETL, *Analysis of Natural Gas-to-Liquid Transportation Fuels via
  Fischer–Tropsch*: escolha do regime pelo produto/alimentação e distinção Co/Fe.
- U.S. DOE/NETL, *High Temperature Fe-Based Fischer–Tropsch*: HTFT centrada em
  Fe, olefinas, WGS, carbono e reações secundárias.
- U.S. DOE/NETL, *Guidelines/Handbook for the Design of Modular Gasification
  Systems*: diferença entre linhas de produto LTFT e HTFT.

Essas fontes orientam o escopo. Dados para modelos exigirão página/tabela,
unidade, licença, compatibilidade e revisão individual.
