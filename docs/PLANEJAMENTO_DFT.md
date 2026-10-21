# Planejamento DFT para superfícies de ferro na Fischer–Tropsch

**Revisado:** 2026-10-20

**Escopo inicial:** chi-Fe₅C₂(510), moléculas C1 e adsorção/dissociação de CO.
**Estado global:** preparação de infraestrutura. Não há corrida DFT nova executada.

## Decisão de método e fonte

O ponto de partida é o conjunto V1 de Zhang, Li e Lu, com 472 configurações de
Fe₅C₂(510), publicado em ScienceDB sob CC BY 4.0 e calculado originalmente com
VASP 5.3.5. O artigo descreve arquivos POSCAR, CONTCAR e OUTCAR. O metadado da
ScienceDB informa 203.320.659 bytes, enquanto o artigo descreve cerca de 1,4 GB,
690 diretórios e 1.961 arquivos. A divergência só pode ser resolvida depois de
obter o pacote e inventariar o conteúdo real.

Referências:

- Zhang, J.; Li, C.; Lu, K. A computational dataset for C1 molecules catalytic
  conversion over iron-based catalysts. Journal of Fuel Chemistry and
  Technology 54 (2026), article 20250429.
  https://doi.org/10.1016/S1872-5813(26)60683-4
- Conjunto de dados V1, ScienceDB. https://doi.org/10.57760/sciencedb.34259
- He et al. (2018), suplemento de facetas e configurações.
  https://doi.org/10.1021/acs.jpcc.7b11430

O pacote de dados ainda exige autenticação para a listagem/transferência de
arquivos na sessão anteriormente verificada. Até a cópia autorizada, usar
somente os metadados públicos; não inventar coordenadas ou resultados ausentes.

## Etapas e portas

| Ordem | ID | Entrega | Critério de aceite | Estado |
|---:|---|---|---|---|
| 1 | FT-035 | Contrato estrutural | Identidade, célula, sítios, carga/spin, arquivo, hash e proveniência validados. Exemplos sintéticos ficam rotulados. | Concluído como contrato |
| 2 | FT-036 | Protocolo de superfície | Faceta, terminação, slab, vácuo, supercélula, cobertura, camadas fixas e estudo de convergência declarados. | Concluído como protocolo; sem campanha real |
| 3 | FT-037 | Protocolo de adsorção | Superfície limpa, adsorbato isolado e sistema adsorvido convergidos com a mesma impressão metodológica. | Concluído como infraestrutura; sem energias reais |
| 4 | FT-038 | Adaptador | Geração determinística POSCAR/INCAR/KPOINTS e manifesto; POTCAR licenciado continua externo. | Concluído como infraestrutura |
| 5 | FT-039 | Parser | Distinguir falha, incompleto, não convergido, sintético e sucesso; validar energia, forças finais contra limiar explícito, número de átomos, término e hash. Marcador do otimizador não basta para provar limite de força. | Concluído como infraestrutura; falta auditoria de OUTCAR real |
| 6 | FT-040 | Relatório | Reunir fonte, estrutura, método, manifesto, saída, limitações e revisão independente. Bloqueio científico não pode ser removido. | Concluído como infraestrutura; sem resultado real |
| 7 | DFT-DATA-01 | Recuperar ScienceDB V1 | Acesso autorizado, arquivo preservado, licença registrada, inventário e SHA-256 por artefato; resolver discrepância de tamanho. | Bloqueado por obtenção autenticada |
| 8 | DFT-AUDIT-01 | Auditar caso sentinela | Parear tabela/artigo com estrutura, entradas, OUTCAR e energias; confirmar magnetismo, ordem magnética, POTCAR, smearing, SCF, forças e convenções energéticas. | Aguardando pacote |
| 9 | DFT-REPRO-01 | Reproduzir ou abrir trilha independente | VASP licenciado e inputs auditados para reprodução; caso contrário, protocolo separado de Quantum ESPRESSO com pseudopotenciais, parâmetros e convergência próprios. Nunca chamar trilhas distintas de reprodução bit a bit. | Aguardando decisão após auditoria |
| 10 | DFT-CONV-01 | Convergência de superfície/adsorção | Testar cutoff, malha k, camadas, vácuo, supercélula e cobertura; energia adsorção usa referências consistentes. | Pendente execução |
| 11 | DFT-NEB-01 | Cinética elementar por CI-NEB | Somente após geometrias e endpoints auditados; registrar imagens, força, caminho e frequências; comparar barreiras com estados de referência consistentes. | Pendente estruturas e recursos |
| 12 | DFT-REVIEW-01 | Revisão científica independente | Revisor confere inputs, hashes, convergência, spin, estados e limitações; relatório preserva fonte e dependências. | Pendente resultados |

## Regras de decisão

1. Não iniciar relaxações de produção nem CI-NEB com slabs reconstruídos a partir
   de figuras ou candidatos sintéticos.
2. Não tratar os cálculos publicados no conjunto como uma campanha independente
   recém-executada. Em validação/ML, agrupar derivados da mesma fonte para evitar
   vazamento entre treino e teste.
3. Não gerar nem distribuir POTCAR sem direito de uso institucional verificado.
4. Não comparar energias de adsorção/barreiras de métodos, pseudopotenciais,
   estados magnéticos ou referências incompatíveis.
5. Manter recomendação operacional e experimental bloqueada até os dados,
   domínio, incerteza e revisão necessários estarem demonstrados.
6. Quantum ESPRESSO é uma alternativa para uma campanha independente. A adoção
   requer escolher e registrar pseudopotenciais licenciados/abertos apropriados,
   testar spin e convergência e construir uma nova referência metodológica.

## Infraestrutura local já disponível

- Gerador de entradas VASP via pymatgen: FT-038.
- Parser VASP OUTCAR com hash, energia, força, sinais de SCF/relaxação e falhas:
  FT-039.
- Relatório JSON/Markdown de auditoria: FT-040.
- Manifesto público de metadados e registro de lacunas:
  data/structures/sciencedb_fe5c2_c1_dataset_v1/dataset_record.json.
- O ambiente verificado anteriormente não tinha VASP, Quantum ESPRESSO, CP2K
  ou ABINIT disponíveis no PATH. A disponibilidade deve ser verificada no host
  real de execução antes da campanha.
