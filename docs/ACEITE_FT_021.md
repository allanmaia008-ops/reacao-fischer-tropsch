# FT-021 — gate do corpus LTFT

O gate foi implementado em `src/plataforma_ltft/corpus_approval.py` e avalia, por dataset, `source_url_or_doi`, `license`, `full_text_verified` e `evidence_status`.

As origens persistentes foram atualizadas no manifesto: a tese de van der Laan (1999) para as equações cinéticas e o DOI `10.1021/acscatal.5b00057` para os conjuntos CoRu/óxidos.

Resultado atual do manifesto versionado:

- 3 datasets avaliados;
- 0 aprovados para uso científico quantitativo;
- status global: `blocked`;
- todos permanecem proibidos para calibração automática, ranking e recomendação de condições.

Isso é um aceite da execução da atividade, não uma aprovação fictícia do corpus. O bloqueio remanescente é verificar licença/reuso, leitura integral e atualizar o status de evidência após revisão humana.
