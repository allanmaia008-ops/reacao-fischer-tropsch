# Aceite das atividades FT-016 e FT-018

## FT-016 — auditor de evidência

Implementado em `src/plataforma_ltft/evidence_validation.py`.

- valida os três CSVs versionados contra cabeçalhos e campos obrigatórios;
- detecta valores não numéricos, negativos, percentuais acima de 100%, duplicidades e fechamento de seletividade;
- registra SHA-256, métricas, origem/licença e leitura integral declaradas no manifesto;
- classifica cada conjunto como `invalid` ou `structurally_valid_not_approved`;
- mantém `approved_for_model_use_count=0`, `g2_ready=false` e impede calibração/ranking automático;
- avalia compatibilidade somente como `context_only` ou `provenance_only`.

O aceite não transforma os CSVs em evidência aprovada: a licença, a leitura integral e a revisão científica continuam portas explícitas.

O responsável aprovou os três datasets para uso interno contextual. Essa aprovação não libera calibração automática, alteração de ranking ou recomendação de condições.

## FT-018 — interface LTFT

Implementado em `app.py` e `src/plataforma_ltft/ui_workflow.py`.

O fluxo público versionado é:

1. produto ou faixa de carbono;
2. regime LTFT/HTFT/transição;
3. catalisador e hipótese de fase;
4. condições de operação e α informado;
5. distribuição ASF e maturidade do resultado;
6. evidências, pendências e limites.

Cada etapa pode ser invalidada junto com as etapas dependentes. A interface deixa explícito que a saída ASF é matemática e condicional a α; não há conversão, produtividade ou recomendação experimental automática.

## Verificação

- `py -m pytest -q`: suíte existente cobrindo auditoria e navegação;
- validação pública do Streamlit: fluxo completo até Resultados, ASF para C12–C20 e controles de exportação visíveis;
- console do navegador sem erros na versão publicada.
