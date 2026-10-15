# Comparação ASF versus medição — FT-017

## Estado da atividade

A infraestrutura inicial está implementada. A fonte interna aprovada foi auditada,
mas a FT-017 permanece **parcial** porque seus cortes C5–C12/C13+ não coincidem
com os cortes ASF C5–C11/C12–C20/C21+. A plataforma bloqueia a repartição
arbitrária desses intervalos.

## Escopo implementado

- comparação por número de carbono (`C1` a `C60`) ou por cortes exclusivos;
- única base aceita nesta versão: fração de carbono nos hidrocarbonetos;
- resíduos assinados e absolutos, MAE e RMSE;
- resíduos padronizados e qui-quadrado quando há incerteza por ponto;
- diagnóstico explícito para C1, C2 e cauda `C21+`, quando disponíveis;
- teste de fechamento apenas para a distribuição completa dos cinco cortes;
- estado da evidência e fontes preservados no relatório;
- validação de modelo permitida somente para evidência `approved` sem falha de
  fechamento;
- `recommendation_blocked = true` em todos os casos.

## Execução

```powershell
py tools\compare_asf_measurement.py `
  --input examples\comparacao_asf_medicao_sintetica.json `
  --output outputs\comparacao_asf_medicao_sintetica.json
```

O exemplo é sintético e serve apenas para verificar o código. Ele não pode
calibrar modelos, validar catalisadores ou orientar condições experimentais.

## Pendências para conclusão

1. obter dados experimentais nos mesmos cinco cortes ASF, ou um método publicado
   para desagregar C5–C12 e C13+;
2. confirmar a base de seletividade e converter somente quando houver dados
   suficientes e método documentado;
3. registrar incertezas, limites de detecção e tratamento de espécies não
   identificadas;
4. revisar os resíduos com especialista e definir critérios de aceite externos.

## Expansão aprovada

A etapa FT-017A comparará ASF simples e modelos avançados somente após a
implementação de FT-012A e a aprovação de dados experimentais. A seleção deverá
usar resíduos, incertezas e critérios de informação; Dual-alpha não será tratado
como superior por padrão. Ver `PLANO_ASF_AVANCADA_TRANSPORTE.md`.
