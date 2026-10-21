# Infraestrutura aprovada — Projeto Fischer–Tropsch

Data: 2026-10-20. Decisão autorizada pelo responsável pelo projeto nesta conversa.
Versão de entrega: 0.2.0.

## Decisão operacional

Aprovada a operação pública do aplicativo científico sem persistência de dados
de usuários: GitHub como fonte versionada e Streamlit Community Cloud como
hospedagem. Não há contratação de serviços pagos nesta decisão.

| Componente | Definição |
| --- | --- |
| Código | allanmaia008-ops/reacao-fischer-tropsch, branch main |
| Interface | app.py, título Projeto Fischer–Tropsch |
| Runtime de referência | Python 3.12; dependências diretas fixadas em requirements.txt |
| Hospedagem | Streamlit Community Cloud, aplicação associada ao repositório |
| Endereço cadastrado no GitHub | https://reacao-fischer-tropsch.streamlit.app/ |
| Validação | GitHub Actions Qualidade: schemas e testes, incluindo AppTest |
| Identificação | Versão visível no aplicativo, commit Git e tag de release |
| Dados do usuário | Estado de sessão temporário e exportação local; sem garantia de retenção |
| Segredos | Nenhum exigido pela interface pública; proibidos no código e nos exports |
| Responsável operacional | Proprietário do repositório, allanmaia008-ops |

O endereço cadastrado não constitui prova de implantação. A confirmação de uma
release requer conferir sua versão na aplicação, além do sucesso da CI.
O marcador público `/app/static/release.json` permite conferir a versão dos
arquivos servidos sem autenticação. Ele não substitui o teste interativo.
Somente metadados públicos de release devem ser colocados em `static/`.

## Fronteira científica e dados

A aprovação da infraestrutura NÃO aprova modelos científicos, experimentos,
DFT ou recomendações de catalisador. Mantêm-se as verificações de domínio e os
bloqueios existentes. Não publicar PDFs licenciados, chaves de API, sessões,
bancos locais ou resultados privados. Os novos dados de pesquisa não entram
nesta release operacional sem auditoria própria de conteúdo e redistribuição.

## Arquitetura multiusuário aprovada para evolução

Separar o frontend Streamlit de uma API Python autenticada por OIDC, PostgreSQL
gerenciado para metadados e fila transacional, armazenamento S3 compatível
privado para artefatos e workers isolados para execução. DFT deve ser executado
em recurso computacional próprio, nunca no processo da interface pública.
Exigir TLS, privilégios mínimos, backups criptografados e teste de restauração,
controle de acesso por projeto, auditoria externa e limites de recursos.

Esses serviços não foram provisionados por esta decisão. Os módulos SQLite,
autenticação e worker presentes no código são pilotos locais, não infraestrutura
multiusuário disponível. FT-041 a FT-047 mantêm suas pendências de implantação
e validação correspondentes; não registrar aceites fictícios para encerrá-las.

## Publicação e recuperação

1. Testar uma cópia limpa contendo exatamente os arquivos da release.
2. Publicar commit em main e conferir a execução da CI correspondente.
3. Criar tag/release somente após sucesso dos testes.
4. Conferir a atualização no Streamlit e a identificação 0.2.0 na interface.
5. Executar planejamento LTFT e exportação, verificando os bloqueios científicos.

Em regressão: reverter o commit de release por um novo commit (sem force push),
aguardar a implantação e repetir o teste de fumaça. A referência anterior é
40d4910526855400411dbcc72b4bb42007fdf68d. Git recupera código, não sessões de usuários.
Sem banco persistente na interface, não prometer backup de resultados de sessão.

Community Cloud não deve ser tratado como serviço com disponibilidade contratual
ou execução contínua garantidas. O operador deve verificar erros de build/runtime
no painel e o funcionamento após cada release. Monitoramento externo e alertas
ainda exigem implantação própria; não existem por esta decisão documental.
