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
    'Completar protocolo e revisão no laboratório; executar ensaio; anexar dados brutos, hash e comparação revisada.']]
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
