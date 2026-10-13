# Aceite da modernização UX — FT-056

Data da verificação: 2026-10-13.

## Escopo aprovado localmente

- fluxo guiado de seis etapas e persistência da sessão;
- página inicial e estado científico explícito;
- sistema visual responsivo, foco de teclado e movimento reduzido;
- entradas agrupadas, unidades, ajuda e validação imediata;
- painel ASF C1–C60 com cauda analítica e bloqueios;
- maturidade rastreável e comparação de dois ou três cenários ASF.

## Evidência de aceite

- testes unitários, de integração e Streamlit executados com `pytest`;
- teste de fumaça da aplicação e de `/_stcore/health` com HTTP 200;
- verificação estática dos recursos de foco, viewport móvel e movimento reduzido;
- CI em `.github/workflows/quality.yml` para regressão em push e pull request;
- verificação pública separada da verificação local.

## Limites preservados

A comparação é uma sensibilidade matemática ao α, não otimização. A conclusão
da porta UX não valida cinética, DFT, conversão, produtividade, catalisador ou
condição experimental. `recommendation_blocked` permanece verdadeiro.

## Critério de publicação

O código deve estar em `main`, o endereço público deve responder HTTP 200 e a
revisão implantada precisa exibir os elementos desta versão. HTTP 200 isolado
não comprova que o deploy já contém o commit mais recente.
