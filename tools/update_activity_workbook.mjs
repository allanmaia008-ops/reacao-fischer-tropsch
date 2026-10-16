import fs from 'node:fs/promises';
import { FileBlob, SpreadsheetFile } from '@oai/artifact-tool';

const inputPath = 'C:/Users/allan/OneDrive/programas/Plataforma_LTFT/docs/Planilha_Atividades_Plataforma_Fischer_Tropsch.xlsx';
const outputPath = inputPath;
const input = await FileBlob.load(inputPath);
const wb = await SpreadsheetFile.importXlsx(input);
const info = await wb.inspect({kind:'sheet', include:'id,name'});
console.log(info.ndjson);
const sheet = wb.worksheets.getItem('Atividades');
const used = sheet.getUsedRange();
const values = used.values;
let headerRow = values.findIndex(row => row.some(v => ['id','atividade','status'].includes(String(v ?? '').trim().toLowerCase())));
if (headerRow < 0) { console.log(JSON.stringify(values.slice(0,8))); throw new Error('Linha de cabeçalho não encontrada'); }
const headers = values[headerRow].map(v => String(v ?? '').trim().toLowerCase());
const idCol = headers.findIndex(h => h === 'id' || h === 'atividade' || h.includes('código'));
const statusCol = headers.findIndex(h => h === 'status' || h.includes('situação'));
if (idCol < 0 || statusCol < 0) throw new Error(`Colunas não encontradas: ${headers.join('|')}`);
const status = new Map([
  ['FT-016','CONCLUÍDO — APROVADO PARA USO INTERNO CONTEXTUAL'],
  ['FT-017','GATE CONCLUÍDO/BLOQUEADO'],['FT-017A','PREPARADA/BLOQUEADA'],
  ['FT-018','CONCLUÍDO'],['FT-019','CONCLUÍDO'],['FT-020','CONCLUÍDO'],
  ['FT-021','CONCLUÍDO — APROVADO PARA USO INTERNO CONTEXTUAL'],['FT-022','CONCLUÍDO — APROVADO PARA USO INTERNO CONTEXTUAL'],['FT-023','CONCLUÍDO — APROVADO PARA USO INTERNO CONTEXTUAL'],
  ['FT-024','PORTA IMPLEMENTADA/BLOQUEADA'],['FT-025','CONCLUÍDO — INFRAESTRUTURA'],
  ['FT-026','CONCLUÍDO COM BLOQUEIO'],['FT-027','CONTRATO IMPLEMENTADO/BLOQUEADO'],['FT-028','CONCLUÍDO']
]);
for (let r = headerRow + 1; r < values.length; r++) {
  const id = String(values[r][idCol] ?? '').trim().toUpperCase();
  if (status.has(id)) sheet.getCell(r, statusCol).values = [[status.get(id)]];
}
const note = sheet.getRangeByIndexes(values.length + 1, 0, 1, Math.max(headers.length, 3));
note.merge();
note.values = [['Atualizado em 2026-10-16: FT-017 a FT-028 revisadas. FT-017/017A e FT-024/027 permanecem bloqueadas por dados experimentais, calibração ou execução real.']];
note.format.wrapText = true;
wb.recalculate();
const check = await wb.inspect({kind:'region', sheetId:sheet.name, range:`A1:${String.fromCharCode(65+Math.min(headers.length,26)-1)}${Math.min(values.length,40)}`, maxChars:4000});
console.log(check.ndjson);
const out = await SpreadsheetFile.exportXlsx(wb);
await out.save(outputPath);
