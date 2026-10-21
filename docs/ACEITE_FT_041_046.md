# Aceite FT-041 a FT-046 — piloto operacional

Atualizado em 2026-10-20. Escopo validado em SQLite local e testes automatizados;
isso não homologa a implantação pública nem certifica validade científica.

## FT-041 — persistência

Mantido o piloto SQLite versionado. Migrações 003–004 adicionam fila idempotente,
lease, resultados JSON e campos de encadeamento dos eventos. O worker persiste
resultados e a trilha junto ao estado. Backup/restore local permanece testado,
mas PostgreSQL, backups externos cifrados/retidos e exercício operacional ainda
faltam. **Status: parcial.**

## FT-042 — identidade e autorização

O núcleo de autenticação conserva scrypt, token de sessão persistido somente
como SHA-256, expiração/revogação e papéis globais/por projeto. Bootstrap de
admin, criação de usuário, alteração de associação e emissão/revogação de sessão
geram eventos sem gravar senha, token ou nome de usuário na auditoria. Não está
integrado à UI/API e não deve ser ativado no Streamlit público. HTTPS, cookies
seguros, CSRF, rate limit, recuperação de conta e revisão institucional pendem.
**Status: parcial.**

## FT-043 — fila e worker

`Database.enqueue_run` deduplica por chave de idempotência; `claim_job` usa
transação imediata e lease recuperável; falhas recebem até o número configurado
de tentativas com espera exponencial limitada; `cancel_job` cancela execução
pendente/em curso. `run_queued_once` executa a configuração pelo worker
determinístico e persiste resultado/artefato local. Cobertos sucesso, falha,
retry, cancelamento, chave repetida e proveniência. **Status: parcial** porque
SQLite e execução local não substituem broker distribuído, concorrência em
multi-host ou supervisor de processo.

## FT-044 — trilha de auditoria

Eventos são ordenados e encadeados por SHA-256; `verify_audit_chain` detecta
alteração/exclusão/inserção que quebre o encadeamento. Eventos incluem projeto,
execução, fila, resultado e ações de administração/autenticação; resultado
registra hash, não o payload duplicado. **Status: parcial:** o hash-chain local
não é armazenamento imutável; administrador com acesso ao banco pode reescrever
a cadeia. Faltam exportação/âncora externa, política de retenção e auditoria
independente da cobertura de eventos.

## FT-045 — homologação

`run_homologation_preflight.py` executa smoke tests operacionais e valida schemas,
produz relatório técnico e recusa sobrescrever o arquivo de relatório. O
contrato `build_preflight_report` mantém separadas portas para dados aprovados,
ambiente isolado, revisão de segurança, simulado de recuperação e sign-off.
**Status: parcial:** relatório verde significa somente preflight técnico; as
portas exigem evidências reais e aceite humano, ausentes neste ambiente.

## FT-046 — observabilidade

`observability.py` emite logs JSON com contexto de execução em allowlist, sem
payload científico, credenciais ou tokens. `metrics_snapshot` retorna contadores
locais e resumo de estado/integridade do SQLite; `tools/platform_health.py`
expõe o snapshot para diagnóstico manual. **Status: parcial:** contadores são
em memória e não há backend durável, alertas, SLO nem monitoramento contínuo.

## Verificação e próximo passo

- Testes direcionados: `tests.test_database`, `tests.test_auth`, `tests.test_worker`,
  `tests.test_worker_queue`, `tests.test_observability` e `tests.test_homologation`.
- Validação de schemas mantida pelo comando `py tools/validate_schemas.py`.
- Preflight: `py tools/run_homologation_preflight.py`; resultado esperado não
  equivale a homologação. Worker: `py tools/run_queue_worker.py --help`.
- Não executar contra dados reais/publicação antes de concluir FT-047/048 e
  validar a configuração de identidade/segredos, persistência, backup e revisão
  científica aplicável.
