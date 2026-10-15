# Aceite FT-058 e FT-059 — fundações LTFT

## FT-058 — contrato e porta do reator LTFT

O módulo `reactor.py` valida alimentação de CO/H₂, temperatura, pressão, massa/volume ou GHSV/WHSV, geometria, modelos de energia, queda de pressão, transferência de massa, WGS e desativação. O balanço disponível é explicitamente apenas de entrada; não calcula conversão nem produtividade sem cinética validada.

## FT-059 — contrato e porta termodinâmica

O módulo `thermodynamics.py` exige EOS, regra de mistura, mapeamento de componentes, pseudocomponentes, VLE, cobertura das fases de syngas, água, hidrocarbonetos leves/líquidos e ceras, fontes e conjunto de validação. A porta só libera o modelo de processo com status `validated` e métricas quantitativas.

As duas atividades ficam concluídas como contratos e portas de segurança; a simulação quantitativa continua bloqueada até FT-057/FT-063 fornecerem cinética, propriedades e validação externa.
