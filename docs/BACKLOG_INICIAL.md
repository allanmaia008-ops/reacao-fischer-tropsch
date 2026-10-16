# Backlog inicial priorizado

## P0 — fundação obrigatória

| ID | Entrega | Aceite |
|---|---|---|
| FT-001 | charter e fronteira científica | **CONCLUÍDO** — escopo e exclusões aprovados em [CHARTER_FT_001.md](CHARTER_FT_001.md) |
| FT-002 | taxonomia LTFT/HTFT | regimes e transição versionados |
| FT-003 | unidades canônicas | **CONCLUÍDO** — catálogo 1.0.0 e conversões testados em [UNIDADES_CANONICAS.md](UNIDADES_CANONICAS.md) |
| FT-004 | contrato de caso | schema, exemplos e validação |
| FT-005 | contrato de catalisador | **CONCLUÍDO** — lote, preparação, fase e proveniência em [CONTRATO_CATALISADOR_V1.md](CONTRATO_CATALISADOR_V1.md) |
| FT-006 | contrato de evidência | origem, licença e status de revisão |
| FT-007 | contrato de resultado | bloqueios e versões explícitos |
| FT-008 | worker determinístico | mesma entrada gera resultado equivalente |
| FT-009 | testes de limites | regimes, unidades e campos condicionais |
| FT-010 | CI mínima | **CONCLUÍDO** — testes e validação explícita de schemas/exemplos em cada mudança; ver [CI_MINIMA_FT_010.md](CI_MINIMA_FT_010.md) |

## P1 — LTFT mínimo útil

| ID | Entrega | Aceite |
|---|---|---|
| FT-011 | seleção de produto | C1–C60 e cortes documentados |
| FT-012 | ASF em base de carbono | fechamento e testes analíticos |
| FT-012A | ASF avançada | **CONCLUÍDO** — ASF simples, mistura dupla e segmentação normalizadas até C∞, correções C1/C2 separadas, cauda analítica e testes; ver [ASF_AVANCADA_FT_012A.md](ASF_AVANCADA_FT_012A.md) |
| FT-013 | caso experimental completo | **CONCLUÍDO** — reator, alimentação, condições, prontidão e impressão digital auditável; ver [ACEITE_FT_013.md](ACEITE_FT_013.md) |
| FT-013A | contrato experimental v2 | **CONCLUÍDO** — diluição, partículas, geometria, ativação completa, analytics, fontes por campo e migração sem defaults arbitrários; ver [CONTRATO_EXPERIMENTAL_V2_FT_013A.md](CONTRATO_EXPERIMENTAL_V2_FT_013A.md) |
| FT-013B | diagnóstico de transporte | **CONCLUÍDO** — Weisz–Prater e Mears versionados, sensibilidade, proveniência e estado não avaliável por falta de dados |
| FT-014 | balanço de carbono | **CONCLUÍDO** — tolerância configurável, residual, fechamento e relatório; ver [BALANCOS_ELEMENTARES_FT_014_015.md](BALANCOS_ELEMENTARES_FT_014_015.md) |
| FT-015 | balanços H/O | **CONCLUÍDO** — espécies e bases documentadas, propagação de incerteza independente e bloqueio para H/O em base seca; ver [BALANCOS_ELEMENTARES_FT_014_015.md](BALANCOS_ELEMENTARES_FT_014_015.md) |
| FT-016 | auditor de evidência | **CONCLUÍDO — APROVADO PARA USO INTERNO CONTEXTUAL** — auditoria, hashes e compatibilidade aprovados; calibração automática, ranking e recomendação continuam bloqueados; ver [ACEITE_FT_016_018.md](ACEITE_FT_016_018.md) |
| FT-017 | comparação ASF/medição | **GATE CONCLUÍDO/BLOQUEADO** — fonte aprovada auditada; cortes incompatíveis permanecem bloqueados; ver [ACEITE_FT_017_028.md](ACEITE_FT_017_028.md) |
| FT-017A | ajuste e seleção do modelo ASF | **PREPARADA/BLOQUEADA** — infraestrutura e dados parciais catalogados; ajuste/AIC/BIC aguardam cortes completos e revisão |
| FT-018 | interface LTFT | **CONCLUÍDO** — fluxo guiado produto→regime→catalisador→condições→resultado→evidências, validação incremental e bloqueios visíveis; ver [ACEITE_FT_016_018.md](ACEITE_FT_016_018.md) |
| FT-019 | exportação JSON/CSV | **CONCLUÍDO** — JSON canônico, CSVs versionados e manifesto SHA-256 reproduzível; ver [EXPORTACAO_RELATORIO_FT_019_020.md](EXPORTACAO_RELATORIO_FT_019_020.md) |
| FT-020 | relatório científico | **CONCLUÍDO** — relatório Markdown com premissas, evidências, prontidão, limitações e bloqueios; ver [EXPORTACAO_RELATORIO_FT_019_020.md](EXPORTACAO_RELATORIO_FT_019_020.md) |

## P2 — validação e planejamento LTFT

| ID | Entrega | Aceite |
|---|---|---|
| FT-021 | corpus LTFT aprovado | **CONCLUÍDO PARA USO INTERNO** — três datasets aprovados pelo responsável, sem redistribuição pública; ver [ACEITE_FT_021.md](ACEITE_FT_021.md) |
| FT-022 | compatibilidade de casos | **CONCLUÍDO — APROVADO PARA USO INTERNO CONTEXTUAL** — regras e justificativa aprovadas; transferência quantitativa e recomendação continuam bloqueadas |
| FT-023 | domínio de aplicabilidade | **CONCLUÍDO — APROVADO PARA USO INTERNO CONTEXTUAL** — envelope e alertas aprovados; bloqueio de extrapolação e recomendação automática permanece ativo |
| FT-024 | modelo quantitativo inicial | **PORTA IMPLEMENTADA/BLOQUEADA** — só libera taxa com contrato validado, validação externa e incerteza definida |
| FT-025 | análise de sensibilidade | **CONCLUÍDO COMO INFRAESTRUTURA** — sensibilidade one-at-a-time e marcação de pontos fora da faixa declarada |
| FT-026 | gerador de plano experimental | **CONCLUÍDO COM BLOQUEIO** — plano estruturado, checklist e revisão humana obrigatória |
| FT-027 | piloto de laboratório | **CONTRATO IMPLEMENTADO/BLOQUEADO** — registro exige protocolo, data, método e dados brutos; nenhum piloto foi alegado como executado |

## P3 — preparação HTFT

| ID | Entrega | Aceite |
|---|---|---|
| FT-028 | caso de uso HTFT | **CONCLUÍDO** — caso diagnóstico HTFT e métricas de acompanhamento definidos |
| FT-029 | schema HTFT | **CONCLUÍDO** — contrato v1 para Fe, oxigenados, coque e reações secundárias |
| FT-030 | bloqueio cruzado | **CONCLUÍDO** — roteamento impede execução LTFT em HTFT |
| FT-031 | corpus HTFT | **CONCLUÍDO COMO FUNDAÇÃO** — diretório separado e política de proveniência; corpus ainda vazio |
| FT-032 | balanços HTFT | CO2, água, C/H/O e não identificados |
| FT-033 | interface HTFT bloqueada | diagnóstico sem recomendação |
| FT-034 | validação HTFT | conjunto externo e revisão independente |

## P4 — processo e avaliação técnico-econômica

| ID | Entrega | Aceite |
|---|---|---|
| FT-057 | contrato cinético | variáveis, unidades, parâmetros, fonte, domínio e incerteza versionados |
| FT-058 | modelo de reator LTFT | **CONCLUÍDO COMO CONTRATO/PORTA** — alimentação, vazão, geometria, pressão e fenômenos declarados; sem conversão sem cinética validada |
| FT-059 | propriedades termodinâmicas | **CONCLUÍDO COMO CONTRATO/PORTA** — EOS, mistura, pseudocomponentes, fases, fontes e validação exigidos |
| FT-060 | balanço integrado de massa e energia | **CONCLUÍDO COMO PORTA** — syngas, FT, upgrading e O₂ separados |
| FT-061 | contrato técnico-econômico | **CONCLUÍDO COMO CONTRATO** — fronteira, capacidade, custos e cenários explícitos |
| FT-062 | modelo econômico | **CONCLUÍDO COMO INFRAESTRUTURA** — receita, CAPEX/OPEX, H₂ e margem com entradas declaradas |
| FT-063 | validação integrada | **CONCLUÍDO COMO PORTA** — conjunto externo, resíduos, incerteza e revisão independente exigidos |

## P5 — DFT

| ID | Entrega | Aceite |
|---|---|---|
| FT-035 | contrato estrutural | estrutura completa e proveniência |
| FT-036 | protocolo de superfície | faceta, terminação, slab e cobertura |
| FT-037 | protocolo de adsorção | três energias comparáveis |
| FT-038 | adaptador de engine | entrada validada e versionada |
| FT-039 | parser de saída | convergência e erros detectados |
| FT-040 | relatório DFT | hipótese e limitações separadas de experimento |

## P6 — plataforma operacional

| ID | Entrega | Aceite |
|---|---|---|
| FT-041 | banco e migrações | backup/restauração testados |
| FT-042 | autenticação e perfis | menor privilégio e testes de acesso |
| FT-043 | fila e workers | idempotência, retries e cancelamento |
| FT-044 | auditoria | alterações científicas rastreadas |
| FT-045 | homologação | dados aprovados e testes ponta a ponta |
| FT-046 | observabilidade | logs, métricas e alertas ativos |
| FT-047 | segurança | revisão de dependências e segredos |
| FT-048 | produção | versão imutável, rollback e fumaça |

## Ordem imediata

Começar por FT-001 a FT-010. FT-011 só inicia depois da aprovação dos contratos
comuns. FT-024, FT-026, FT-034, FT-040, FT-058, FT-062 e FT-063 nunca liberam recomendação sem suas portas
científicas correspondentes.
