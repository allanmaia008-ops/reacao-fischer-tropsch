# Aceite FT-038 — adaptador de engine DFT

## Resultado

A FT-038 está **CONCLUÍDA COMO INFRAESTRUTURA** para VASP. O adaptador usa
`pymatgen` para converter os contratos FT-035 e FT-036 em `POSCAR`, `INCAR` e
`KPOINTS`, acompanhados por manifesto versionado e hashes SHA-256.

Isso prepara entradas; não executa VASP e não constitui resultado científico.
O exemplo incluído é sintético e mantém `recommendation_blocked = true`.

## Controles implementados

- validação dos contratos de estrutura e superfície antes da geração;
- suporte explícito e restrito ao engine `vasp` nesta versão;
- rejeição de funcional e família de pseudopotencial não atribuídos;
- mapeamento auditável de cutoff, malha k, spin, tolerâncias e D3/D3(BJ);
- arquivos determinísticos para a mesma entrada e mesma versão do gerador;
- impressão digital separada do contrato-fonte e do método eletrônico;
- manifesto com versão do adaptador, versão do `pymatgen` e hashes dos arquivos;
- recusa de sobrescrita de um bundle existente;
- `POTCAR` deliberadamente ausente e registrado como pendência externa, pois o
  arquivo é licenciado e seus potenciais reais devem ser auditados no ambiente
  de execução.

## Execução

Instale a dependência opcional com `pip install -e .[dft]` e gere um bundle:

```powershell
$env:PYTHONPATH = "src"
py tools/generate_dft_input.py `
  examples/dft_structure_synthetic_v1.json `
  examples/dft_surface_vasp_synthetic_v1.json `
  output/ft038-synthetic-001 `
  --input-set-id ft038-synthetic-001
```

## Limites e próxima atividade

Antes de uma execução real, um responsável deve anexar e verificar o `POTCAR`,
confirmar licença, família e hashes e revisar todos os parâmetros. A FT-039 deve
implementar o parser de saída, distinguindo convergência eletrônica, convergência
iônica, término normal e erros; ela não pode inferir sucesso apenas pela presença
de um arquivo de saída.
