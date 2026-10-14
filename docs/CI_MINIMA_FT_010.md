# CI mínima — FT-010

## Objetivo

Executar, em cada `push` para `main` e em cada `pull_request`, a validação
estrutural dos JSON Schemas, seus exemplos versionados e a suíte automatizada.

## Porta implementada

O workflow `.github/workflows/quality.yml` instala o projeto em Python 3.12 e
executa, em etapas separadas:

```powershell
py tools\validate_schemas.py
py -m pytest -q
```

`tools/validate_schemas.py` verifica:

- sintaxe JSON e conformidade com JSON Schema Draft 2020-12;
- presença e unicidade de `$id`;
- exemplos positivos dos contratos de caso v1/v2 e catalisador v1.

`caso_invalido.json` permanece coberto pelos testes de domínio: ele é
estruturalmente aceito pelo contrato v1, mas deve ser recusado pelas regras
científicas aplicáveis. A CI não mistura essas duas camadas de validação.

Qualquer inconsistência encerra o processo com código diferente de zero. A CI
usa somente permissão de leitura do conteúdo e cancela execuções antigas da
mesma referência quando uma mudança mais recente é enviada.

## Limite do aceite

CI aprovada confirma consistência automatizada do repositório. Ela não equivale
a validação científica dos modelos, homologação operacional nem confirmação de
deploy público.
