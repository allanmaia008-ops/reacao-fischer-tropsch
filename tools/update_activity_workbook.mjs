import { FileBlob, SpreadsheetFile } from '@oai/artifact-tool';
import { fileURLToPath } from 'node:url';

// Anchor at A1; the used range may begin at A2. Use explicit cell addresses.
const path = fileURLToPath(new URL('../docs/Planilha_Atividades_Plataforma_Fischer_Tropsch.xlsx', import.meta.url));
const wb = await SpreadsheetFile.importXlsx(await FileBlob.load(path));
const sheet = wb.worksheets.getItem('Atividades');
const values = sheet.getRange('A1:I120').values;
const updates = new Map([
  ['FT-024', ['MODELO EXPLORATÓRIO / VALIDAÇÃO EXTERNA COMPATÍVEL PENDENTE',
    'FT024_FT027_EVIDENCIAS.md: 22 registros Co–Ce e 15 candidatos externos Co–Mn. A porta rejeitou o candidato por incompatibilidade de catalisador e alimentação; holdout interno documentado.',
    'Obter campanha independente do mesmo sistema Co–Ce e domínio; definir critérios de aceitação; manter recomendação bloqueada.']],
  ['FT-027', ['PREPARAÇÃO DOCUMENTAL / EXECUÇÃO EXPERIMENTAL PENDENTE',
    'FT024_FT027_EVIDENCIAS.md e ft027_pilot_pending.json: preparação e validação de metadados; nenhum ensaio próprio executado.',
    'Completar protocolo e revisão no laboratório; executar ensaio; anexar dados brutos, hash e comparação revisada.']],
  ['FT-028', ['CONCLUÍDO',
    'ACEITE_FT_028_029.md e htft_light_olefins_v1.json: alvo C2–C4, condições de referência, respostas, estabilidade, fechamento e replicatas definidos.',
    'Usar o caso como contrato diagnóstico; revisar limiares antes de execução e manter recomendação bloqueada.']],
  ['FT-029', ['CONCLUÍDO',
    'htft-case-v1.schema.json cobre Fe/promotores/fases, O/P C2–C4, oxigenados, coque, gradiente e reações secundárias; exemplos positivo e negativo validados na CI.',
    'Versionar o schema se o escopo mudar; avançar corpus e balanços HTFT em atividades próprias.']],
  ['FT-030', ['CONCLUÍDO',
    'Roteamento do caso e da evidência impede execução LTFT, calibração automática e transferência entre famílias incompatíveis.',
    'Manter testes de não regressão ao adicionar novos modelos ou datasets.']],
  ['FT-031', ['CONCLUÍDO — USO INTERNO CONTEXTUAL',
    'Corpus HTFT separado com 8 registros Fe a 350 °C; auditor verifica manifesto, hash, envelope e fechamento. Calibração e ranking permanecem proibidos.',
    'Confirmar licença antes de redistribuição externa; ampliar com estudos compatíveis revisados.']],
  ['FT-032', ['CONCLUÍDO — INFRAESTRUTURA',
    'Contrato e módulo fecham C/H/O com CO₂, água, hidrocarbonetos, oxigenados, coque e não identificados; exemplo sintético e testes aprovados.',
    'Aplicar a dados medidos quando houver ensaio HTFT completo.']],
  ['FT-033', ['CONCLUÍDO',
    'Interface HTFT mostra alvo C2–C4, 8 registros contextuais, requisitos analíticos e bloqueio; ASF é rotulada como referência matemática.',
    'Manter recomendação bloqueada até validação HTFT independente na FT-034.']]
]);
const expected = [];
for (const [id, fields] of updates) {
  const matches = values.map((row, i) => row[0] === id ? i + 1 : null).filter(Boolean);
  if (matches.length !== 1) throw new Error(`ID ausente/duplicado: ${id}`);
  const row = matches[0];
  sheet.getRange(`G${row}:I${row}`).values = [fields];
  sheet.getRange(`G${row}:I${row}`).format.wrapText = true;
  expected.push({id, row, fields});
}
wb.recalculate();
await (await SpreadsheetFile.exportXlsx(wb)).save(path);
const reopened = await SpreadsheetFile.importXlsx(await FileBlob.load(path));
const check = reopened.worksheets.getItem('Atividades');
for (const {id,row,fields} of expected) {
  if (check.getRange(`A${row}`).values[0][0] !== id ||
      JSON.stringify(check.getRange(`G${row}:I${row}`).values[0]) !== JSON.stringify(fields)) {
    throw new Error(`Verificação pós-exportação falhou: ${id}`);
  }
}
console.log(JSON.stringify(expected));
