import fs from 'node:fs/promises';
import { FileBlob, Workbook, SpreadsheetFile } from '@oai/artifact-tool';
import { fileURLToPath } from 'node:url';

const csvPath=fileURLToPath(new URL('../data/planned/ft024_external_campaign_100_runs.csv',import.meta.url));
const outPath=fileURLToPath(new URL('../data/planned/ft024_external_campaign.xlsx',import.meta.url));
const previewPath=fileURLToPath(new URL('../data/planned/.ft024-external-campaign-preview.png',import.meta.url));
const raw=(await fs.readFile(csvPath,'utf8')).trim().split(/\r?\n/).map(line=>line.split(','));
const numeric=new Set(['randomization_order','temperature_c','pressure_bar','h2_co_ratio','p_h2_bar','p_co_bar','ghsv_h_1','catalyst_mass_g','steady_state_h']);
for(const row of raw.slice(1)) for(let i=0;i<row.length;i++) if(numeric.has(raw[0][i])) row[i]=Number(row[i]);

const wb=Workbook.create();
const summary=wb.worksheets.add('Resumo'); summary.showGridlines=false;
summary.getRange('A2:F2').merge(); summary.getRange('A2').values=[['FT-024 — campanha externa independente']];
summary.getRange('A2:F2').format.font={name:'Arial',size:15,bold:true,color:'#17324D'};
summary.getRange('A4:B10').values=[['Indicador','Estado'],['Campanha','FT024-EXT-001'],['Corridas planejadas',100],['Condições únicas',50],['Lotes independentes',2],['Medições observadas',0],['Validação externa','PENDENTE']];
summary.getRange('A4:B4').format={fill:'#17324D',font:{name:'Arial',bold:true,color:'#FFFFFF'},horizontalAlignment:'center'};
summary.getRange('A5:B10').format.font={name:'Arial',size:10};
summary.getRange('A12:F12').merge(); summary.getRange('A12').values=[['Aviso científico']];
summary.getRange('A13:F13').merge(); summary.getRange('A13').values=[['Este arquivo contém condições planejadas e campos vazios. Não contém resultados experimentais.']];
summary.getRange('A14:F14').merge(); summary.getRange('A14').values=[['A FT-024 só poderá ser liberada após execução por laboratório independente, rastreabilidade dos dados brutos e aprovação dos critérios pré-registrados.']];
summary.getRange('A12:F12').format={fill:'#F4B183',font:{name:'Arial',bold:true,color:'#7F2704'}};
summary.getRange('A13:F14').format={font:{name:'Arial',size:10},wrapText:true};
summary.getRange('A:A').format.columnWidth=34; summary.getRange('B:B').format.columnWidth=22;

const plan=wb.worksheets.add('Plano e captura'); plan.showGridlines=false;
const last=raw.length; const endCol='Z';
plan.getRange(`A1:${endCol}${last}`).values=raw;
plan.getRange(`A1:${endCol}1`).format={fill:'#17324D',font:{name:'Arial',bold:true,color:'#FFFFFF'},horizontalAlignment:'center',wrapText:true};
plan.getRange(`A2:${endCol}${last}`).format.font={name:'Arial',size:9};
plan.freezePanes.freezeRows(1); plan.freezePanes.freezeColumns(3);
plan.getRange('A:C').format.columnWidth=20; plan.getRange('D:G').format.columnWidth=27;
plan.getRange('H:O').format.columnWidth=15; plan.getRange('P:R').format.columnWidth=21;
plan.getRange('S:Z').format.columnWidth=24;
plan.getRange(`P2:Z${last}`).format.fill='#FFF2CC';

const criteria=wb.worksheets.add('Liberação'); criteria.showGridlines=false;
criteria.getRange('A2:D2').merge(); criteria.getRange('A2').values=[['Porta de liberação da campanha']];
criteria.getRange('A2:D2').format.font={name:'Arial',size:15,bold:true,color:'#17324D'};
criteria.getRange('A4:C12').values=[['Pré-requisito','Critério','Estado inicial'],['Execução independente','Laboratório e operadores independentes','PENDENTE'],['Rastreabilidade','Arquivos brutos e SHA-256 por corrida','PENDENTE'],['Tamanho','>=20 condições únicas elegíveis','PENDENTE'],['Compatibilidade','Catalisador, preparação e domínio compatíveis','PENDENTE'],['Transporte','Critérios térmicos e difusionais aprovados','PENDENTE'],['Erro','NMAE <=15%; NRMSE <=20%; viés <=5%','PENDENTE'],['Resíduos','Sem tendência material e outliers <=1%','PENDENTE'],['Incerteza','PI95 com cobertura 90–99% e bootstrap','PENDENTE']];
criteria.getRange('A4:C4').format={fill:'#17324D',font:{name:'Arial',bold:true,color:'#FFFFFF'},horizontalAlignment:'center'};
criteria.getRange('A5:C12').format={font:{name:'Arial',size:10},wrapText:true};
criteria.getRange('A:A').format.columnWidth=24; criteria.getRange('B:B').format.columnWidth=52; criteria.getRange('C:C').format.columnWidth=20;

wb.recalculate();
console.log((await wb.inspect({kind:'table',range:'Resumo!A4:B14',include:'values,formulas',tableMaxRows:20,tableMaxCols:6})).ndjson);
console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:300},summary:'final formula error scan'})).ndjson);
const preview=await wb.render({sheetName:'Resumo',range:'A1:F15',scale:1.5,format:'png'});
await fs.writeFile(previewPath,new Uint8Array(await preview.arrayBuffer()));
await (await SpreadsheetFile.exportXlsx(wb)).save(outPath);
const reopened=await SpreadsheetFile.importXlsx(await FileBlob.load(outPath));
console.log((await reopened.inspect({kind:'table',range:'Plano e captura!A1:Z4',include:'values,formulas',tableMaxRows:5,tableMaxCols:26})).ndjson);
