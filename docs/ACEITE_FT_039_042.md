# Entregas FT-039 a FT-042

Atualizado em 2026-10-20. Os testes usam fixtures sintéticas; nenhuma corrida
DFT, implantação web ou instância operacional de banco foi executada.

## FT-039 — parser de saída DFT

**Concluída como infraestrutura de parsing VASP.** O módulo dft_parser.py lê
OUTCAR, registra SHA-256 do conteúdo, última energia TOTEN, blocos de força e
contagem de átomos comparada com NIONS, convergência eletrônica, teste explícito
da força final contra um limiar informado, término normal e mensagens de erro.
O marcador de parada iônica do VASP é registrado, mas não substitui o teste de
força. Sem limiar declarado, a convergência iônica fica desconhecida e o estado
não pode ser succeeded. Estados possíveis são succeeded,
failed, incomplete, unconverged e synthetic_test.

O estado succeeded exige sinais explícitos de término normal, convergência
eletrônica e iônica, e energia disponível. Saída incompleta não é promovida a
sucesso. recommendation_blocked permanece sempre verdadeiro. O contrato está
em ft-dft-parsed-result-v1.schema.json; o comando é
py tools/parse_dft_output.py OUTCAR --output resultado.json
--force-threshold 0.03.

**Limite:** parser e fixtures estão verificados, mas um OUTCAR real do conjunto
ScienceDB ainda precisa ser obtido e comparado contra a tabela/publicação e os
inputs correspondentes. O parser não substitui avaliação de convergência,
consistência de pseudopotenciais nem revisão científica.

## FT-040 — relatório de cálculo DFT

**Concluída como infraestrutura de relatório auditável.** O módulo
dft_reporting.py gera um relatório JSON e Markdown a partir do resultado
parseado, contrato estrutural, protocolo, manifesto de entradas e citação.
Registra método, superfície, cobertura, critérios, hashes, estado de execução
e limitações. Recusa entradas sem bloqueio científico e recusa sobrescrita dos
arquivos. Contrato em ft-dft-report-v1.schema.json; comando em
py tools/build_dft_report.py --help.

O relatório não produz interpretação catalítica, taxa, desempenho experimental
ou recomendação operacional. A revisão humana independente continua obrigatória.

## FT-041 — banco e migrações

**Parcial — piloto local SQLite implementado.** database.py implementa
migrações numeradas, projetos, execuções, eventos de auditoria, serialização
JSON e cópias/recuperação verificadas com PRAGMA integrity_check. Os testes
usam diretórios temporários e recusam sobrescrever destino existente.

**Pendências:** integrar o repositório ao worker/aplicação; definir provedor
PostgreSQL para implantação; configurar backups automatizados fora da máquina,
retenção, criptografia e ensaio operacional de recuperação. Os testes locais
não equivalem a backup de produção.

## FT-042 — autenticação e perfis

**Parcial — primitivas de autenticação/autorização implementadas.** auth.py
oferece criação controlada do primeiro administrador, senhas derivadas com
scrypt, tokens aleatórios de sessão guardados somente como SHA-256, expiração,
revogação, perfis admin/pesquisador/leitor e permissões por projeto. Testes
cobrem criação administrativa, isolamento, menor privilégio, falhas de login
e revogação.

**Pendências de produção:** integração obrigatória em todas as rotas da UI/API,
gestão segura do token/cookie, HTTPS, proteção CSRF, limitação de tentativas,
recuperação/desativação de conta, política institucional de identidade,
revisão de segurança e teste ponta a ponta. Não habilitar o sistema em Streamlit
público até concluir essas portas.

## Verificações

- 20 novos testes de parser, relatório, banco e autenticação.
- Schemas v1 de parser e relatório e exemplos sintéticos adicionados à validação.
- Os exemplos não são evidência científica e mantêm recommendation_blocked=true.
