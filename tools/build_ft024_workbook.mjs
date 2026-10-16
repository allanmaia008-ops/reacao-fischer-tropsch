import fs from 'node:fs/promises';
import { FileBlob, Workbook, SpreadsheetFile } from '@oai/artifact-tool';
import { fileURLToPath } from 'node:url';

const csvPath = fileURLToPath(new URL('../data/evidence/ft024_cobalt_cerium_measurements.csv', import.meta.url));
const outputPath = fileURLToPath(new URL('../data/evidence/ft024_cobalt_cerium_database.xlsx', import.meta.url));
const text = await fs.readFile(csvPath, 'utf8');
const rows = text.trim().split(/\r?\n/).map(line => line.split(','));
const numeric = new Set(['temperature_c','pressure_bar','h2_co_ratio','response_value']);
const headers = rows[0];
for (const row of rows.slice(1)) for (let i=0;i<row.length;i++) if (numeric.has(headers[i])) row[i]=Number(row[i]);

const wb = Workbook.create();
const summary = wb.worksheets.add('Resumo');
summary.showGridlines = false;
summary.getRange('A2:F2').merge(); summary.getRange('A2').values=[['FT-024 — banco experimental de catalisadores Co–Ce']];
summary.getRange('A2:F2').format.font={name:'Arial',size:15,bold:true,color:'#17324D'};
summary.getRange('A4:B9').values=[
  ['Indicador','Valor'],['Medições publicadas',374],['Condições experimentais únicas',52],
  ['Ensaios do catalisador exato',22],['Ensaios contextuais Fe–Co–Ce',30],['Ensaios de validação externa elegíveis',0]
];
summary.getRange('A4:B4').format={fill:'#17324D',font:{name:'Arial',bold:true,color:'#FFFFFF'},horizontalAlignment:'center'};
summary.getRange('A5:B9').format.font={name:'Arial',size:10};
summary.getRange('A11:F13').values=[
 ['Limite científico'],['374 linhas são medições; não representam 374 experimentos independentes.'],
 ['A validação externa permanece bloqueada: o conjunto estrito é do estudo de calibração e o conjunto contextual muda catalisador/suporte.']
];
summary.getRange('A11:F11').merge(); summary.getRange('A12:F12').merge(); summary.getRange('A13:F13').merge();
summary.getRange('A11:F11').format={fill:'#F4B183',font:{name:'Arial',bold:true,color:'#7F2704'}};
summary.getRange('A12:F13').format={font:{name:'Arial',size:10},wrapText:true};
summary.getRange('A:A').format.columnWidth=38; summary.getRange('B:B').format.columnWidth=18;

const data = wb.worksheets.add('Medições');
data.showGridlines = false; data.getRange(`A1:V${rows.length}`).values=rows;
data.getRange('A1:V1').format={fill:'#17324D',font:{name:'Arial',bold:true,color:'#FFFFFF'},horizontalAlignment:'center',wrapText:true};
data.getRange(`A2:V${rows.length}`).format.font={name:'Arial',size:9};
data.getRange(`H2:K${rows.length}`).format.numberFormat='0.000';
data.getRange(`M2:M${rows.length}`).format.numberFormat='0.000000';
data.freezePanes.freezeRows(1); data.freezePanes.freezeColumns(2);
data.getRange('A:A').format.columnWidth=38; data.getRange('B:D').format.columnWidth=26;
data.getRange('E:G').format.columnWidth=24; data.getRange('H:M').format.columnWidth=16;
data.getRange('N:V').format.columnWidth=28;

const criteria = wb.worksheets.add('Critérios'); criteria.showGridlines=false;
criteria.getRange('A2:D2').merge(); criteria.getRange('A2').values=[['Critérios propostos de validação FT-024']];
criteria.getRange('A2:D2').format.font={name:'Arial',size:15,bold:true,color:'#17324D'};
criteria.getRange('A4:C15').values=[
 ['Dimensão','Critério','Regra'],['Independência','Obrigatória','Dados não usados no ajuste/seleção'],
 ['Compatibilidade','Obrigatória','Mesmo catalisador, preparação e domínio'],['Tamanho','Mínimo','20 condições externas únicas'],
 ['MAE','Aceite','NMAE pela média <= 15%'],['MSE/RMSE','Aceite','Reportar MSE; NRMSE pela média <= 20%'],
 ['Viés','Aceite','|resíduo médio| <= 5% da média'],['Cobertura PI 95%','Aceite','90% a 99%'],
 ['Outliers','Aceite','<= 1% com |resíduo padronizado| > 3'],['Tendência','Aceite','|Spearman| < 0,30 por variável'],
 ['Heterocedasticidade','Aceite','p >= 0,05 ou reespecificar variância'],['Incerteza','Obrigatória','Bootstrap agrupado >= 2.000 e propagação da medição']
];
criteria.getRange('A4:C4').format={fill:'#17324D',font:{name:'Arial',bold:true,color:'#FFFFFF'},horizontalAlignment:'center'};
criteria.getRange('A5:C15').format={font:{name:'Arial',size:10},wrapText:true};
criteria.getRange('A:A').format.columnWidth=24; criteria.getRange('B:B').format.columnWidth=18; criteria.getRange('C:C').format.columnWidth=52;

wb.recalculate();
const check=await wb.inspect({kind:'table',range:'Resumo!A4:B13',include:'values,formulas',tableMaxRows:20,tableMaxCols:6});
console.log(check.ndjson);
const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:300},summary:'final formula error scan'});
console.log(errors.ndjson);
const preview=await wb.render({sheetName:'Resumo',range:'A1:F14',scale:1.5,format:'png'});
await fs.writeFile(fileURLToPath(new URL('../data/evidence/.ft024-database-preview.png', import.meta.url)),new Uint8Array(await preview.arrayBuffer()));
const dataPreview=await wb.render({sheetName:'Medições',range:'A1:V12',scale:0.8,format:'png'});
await fs.writeFile(fileURLToPath(new URL('../data/evidence/.ft024-data-preview.png', import.meta.url)),new Uint8Array(await dataPreview.arrayBuffer()));
const criteriaPreview=await wb.render({sheetName:'Critérios',range:'A1:C16',scale:1.2,format:'png'});
await fs.writeFile(fileURLToPath(new URL('../data/evidence/.ft024-criteria-preview.png', import.meta.url)),new Uint8Array(await criteriaPreview.arrayBuffer()));
await (await SpreadsheetFile.exportXlsx(wb)).save(outputPath);
const reopened=await SpreadsheetFile.importXlsx(await FileBlob.load(outputPath));
const post=await reopened.inspect({kind:'table',range:'Medições!A1:V4',include:'values,formulas',tableMaxRows:5,tableMaxCols:22});
console.log(post.ndjson);
