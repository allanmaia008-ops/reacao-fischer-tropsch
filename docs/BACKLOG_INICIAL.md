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
| FT-012A | ASF avançada | **PLANEJADO** — ASF simples permanece referência; implementar mistura de duas ASF/segmentação, correções C1/C2, cauda analítica e testes; ver [PLANO_ASF_AVANCADA_TRANSPORTE.md](PLANO_ASF_AVANCADA_TRANSPORTE.md) |
| FT-013 | caso experimental completo | **CONCLUÍDO** — reator, alimentação, condições, prontidão e impressão digital auditável; ver [ACEITE_FT_013.md](ACEITE_FT_013.md) |
| FT-013A | contrato experimental v2 | **PLANEJADO** — diluição, partículas, geometria, ativação completa e detalhamento analítico, sem defaults arbitrários |
| FT-013B | diagnóstico de transporte | **PLANEJADO** — Weisz–Prater e Mears com estados calculado, reprovado ou não avaliável por falta de dados |
| FT-014 | balanço de carbono | **CONCLUÍDO** — tolerância configurável, residual, fechamento e relatório; ver [BALANCOS_ELEMENTARES_FT_014_015.md](BALANCOS_ELEMENTARES_FT_014_015.md) |
| FT-015 | balanços H/O | **CONCLUÍDO** — espécies e bases documentadas, propagação de incerteza independente e bloqueio para H/O em base seca; ver [BALANCOS_ELEMENTARES_FT_014_015.md](BALANCOS_ELEMENTARES_FT_014_015.md) |
| FT-016 | auditor de evidência | inconsistências e status rastreáveis |
| FT-017 | comparação ASF/medição | **EM EXECUÇÃO** — contrato, alinhamento de base, resíduos e incerteza implementados com exemplo sintético; falta conectar medições experimentais aprovadas; ver [COMPARACAO_ASF_MEDICAO_FT_017.md](COMPARACAO_ASF_MEDICAO_FT_017.md) |
| FT-017A | ajuste e seleção do modelo ASF | **BLOQUEADO** — comparar ASF simples e avançada por resíduos, AIC/BIC e incerteza somente após FT-012A e aprovação de dados experimentais |
| FT-018 | interface LTFT | fluxo produto→caso→resultado |
| FT-019 | exportação JSON/CSV | arquivos versionados e reproduzíveis |
| FT-020 | relatório científico | premissas, evidências e limitações |

## P2 — validação e planejamento LTFT

| ID | Entrega | Aceite |
|---|---|---|
| FT-021 | corpus LTFT aprovado | licença, origem e revisão completas |
| FT-022 | compatibilidade de casos | regras e justificativa auditáveis |
| FT-023 | domínio de aplicabilidade | alertas de extrapolação testados |
| FT-024 | modelo quantitativo inicial | cinética calibrada, domínio, validação externa e incerteza; sem inferir conversão só por T/P |
| FT-025 | análise de sensibilidade | variáveis e faixa de validade |
| FT-026 | gerador de plano experimental | revisão humana obrigatória |
| FT-027 | piloto de laboratório | protocolo e resultado documentados |

## P3 — preparação HTFT

| ID | Entrega | Aceite |
|---|---|---|
| FT-028 | caso de uso HTFT | produto e métrica aprovados |
| FT-029 | schema HTFT | Fe, fases, O/P, coque e reações secundárias |
| FT-030 | bloqueio cruzado | nenhum modelo LTFT executa em HTFT |
| FT-031 | corpus HTFT | separado, rastreável e revisado |
| FT-032 | balanços HTFT | CO2, água, C/H/O e não identificados |
| FT-033 | interface HTFT bloqueada | diagnóstico sem recomendação |
| FT-034 | validação HTFT | conjunto externo e revisão independente |

## P4 — processo e avaliação técnico-econômica

| ID | Entrega | Aceite |
|---|---|---|
| FT-057 | contrato cinético | variáveis, unidades, parâmetros, fonte, domínio e incerteza versionados |
| FT-058 | modelo de reator LTFT | balanços, alimentação, vazão, geometria, pressão e fenômenos adotados testados |
| FT-059 | propriedades termodinâmicas | EOS, mistura, pseudocomponentes, fases e faixa de validade comparados com dados |
| FT-060 | balanço integrado de massa e energia | syngas, FT e upgrading fechados; O2 produzido e consumido distinguidos |
| FT-061 | contrato técnico-econômico | fronteira, capacidade, ano-base, preços e cenários aprovados |
| FT-062 | modelo econômico | CAPEX/OPEX, H2, eletricidade, carbono e custo do combustível com sensibilidade |
| FT-063 | validação integrada | conjunto externo, resíduos, incerteza e revisão independente |

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
