# Validação das evidências CSV

## Execução

```powershell
py tools\audit_evidence.py `
  --case examples\caso_experimental_completo.json `
  --output outputs\evidence_audit.json
```

## Verificações implementadas

- nome, presença e ordem das colunas;
- chave duplicada;
- campos obrigatórios e ausências por coluna;
- tipos numéricos, valores negativos e percentuais acima de 100%;
- fechamento das seletividades C1 + C2–C4 + C5–C12 + C13+ em 100%;
- estados permitidos das equações cinéticas;
- hash SHA-256 de cada arquivo;
- entrada correspondente no manifesto;
- URL/DOI, licença e leitura integral;
- compatibilidade contextual com um caso LTFT.

## Resultado de 2026-09-27

- três conjuntos estruturalmente válidos;
- zero erros;
- nove alertas: URL/DOI, licença e leitura integral ausentes para os três conjuntos;
- cinco linhas de seletividade fecham em 100%;
- CTY está ausente em quatro das cinco linhas, preservado como ausência e não zero;
- nenhum conjunto aprovado para calibração, ranking ou recomendação automática;
- Porta G2 ainda não atingida.

O relatório canônico é `outputs/evidence_audit.json`. Os arquivos CSV originais
não são modificados durante a auditoria.

