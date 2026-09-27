import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const html=fs.readFileSync(new URL('report_template.html',import.meta.url),'utf8');
const context=vm.createContext({});
vm.runInContext(html.slice(html.indexOf('const fields='),html.indexOf('let current=')),context);
const {sum,aggregate,buildRanking}=context;
const sample=(id,variance)=>({'Budget ID':id,'Account Group ID':id,'Account Group':id,'Account ID':id,'Account Name':id,'Cost Center ID':id,'Cost Center Name':id,actual:100+variance,budget:100,variance,service_actual:100+variance,volume:variance,rate_mix:0,unbudgeted:0,timing:0});
const grouped=aggregate([sample('A',100),sample('B',20),sample('C',-15),sample('D',0)],'id');
let r=buildRanking(grouped,50);
assert.equal(r.rows.length,2);assert.equal(r.rows[1].label,'Other expenses');assert.equal(r.rows[1].variance,5);assert.equal(r.rows[1].actual,305);assert.equal(r.rows[1].budget,300);assert.equal(r.rows[1].ids.size,3);
for(const min of [0,15,20,50,101]){r=buildRanking(grouped,min);assert.equal(sum(r.rows).actual,r.total.actual);assert.equal(sum(r.rows).budget,r.total.budget);assert.equal(sum(r.rows).variance,r.total.variance);assert.equal(r.total.ids.size,4);}
assert.equal(buildRanking(grouped,0).combinedCount,0);
assert.equal(buildRanking(grouped,15).combinedCount,1); // exact threshold remains separate
assert.equal(buildRanking(grouped,101).rows[0].label,'Other expenses');
r=buildRanking(grouped,50,'B');assert.equal(r.rows[0].label,'Other expenses');assert.equal(r.total.actual,120);
r=buildRanking(grouped,50,'no-match');assert.equal(r.rows.length,0);assert.equal(r.total.actual,0);
const data=JSON.parse(fs.readFileSync(new URL('report/variance_report.html',import.meta.url),'utf8').match(/<script id="dataset" type="application\/json">([\s\S]*?)<\/script>/)[1]);
let scenarios=0;
for(const level of ['group','account','cc','id'])for(const min of [0,1000,100000,1e9])for(const months of [[1,12],[3,3],[7,9]]){
 const rows=data.rows.filter(r=>r.month>=months[0]&&r.month<=months[1]);const result=buildRanking(aggregate(rows,level),min);const total=sum(rows),shown=sum(result.rows);
 for(const k of ['actual','budget','variance','volume','rate_mix','timing','unbudgeted'])assert.ok(Math.abs(total[k]-shown[k])<.005,`${level}/${min}/${months}: ${k}`);
 assert.equal(result.total.ids.size,new Set(rows.map(r=>r['Budget ID'])).size);scenarios++;
}
console.log(`Ranking tests passed: offsetting expenses, boundary/zero/all thresholds, search scope and ${scenarios} workbook scenarios.`);
const {filterDetailRows}=context;
const other=buildRanking(aggregate(data.rows,'group'),100000).rows.find(r=>r.combinedCount);
assert.ok(other);
const original=sum(other.rows);
for(const key of ['Cost Center ID','Account Group ID','Account ID','Budget ID']){
 const value=other.rows[0][key];const filtered=filterDetailRows(other.rows,{[key]:value});
 assert.ok(filtered.length);assert.ok(filtered.every(r=>r[key]===value));
 assert.ok(filtered.every(r=>other.ids.has(r['Budget ID'])));
 const totals=sum(filtered);assert.ok(Math.abs(totals.variance-totals.volume-totals.rate_mix-totals.unbudgeted-totals.timing)<.005);
}
assert.equal(filterDetailRows(other.rows,{'Budget ID':'not-in-other'}).length,0);
assert.equal(sum(other.rows).actual,original.actual);
// Exercise actual UI handlers in a minimal DOM fixture, without controlling a browser.
const nodes=new Map();const get=id=>{if(!nodes.has(id))nodes.set(id,{value:'',innerHTML:'',textContent:'',onclick:null,onchange:null});return nodes.get(id);};
get('dataset').textContent=JSON.stringify(data);get('start').value='1';get('level').value='group';get('threshold').value='100000';
const ui=vm.createContext({document:{getElementById:get,querySelectorAll:()=>[]},setTimeout,console});
vm.runInContext(html.match(/<\/script><script>([\s\S]*?)<\/script>/)[1],ui);
vm.runInContext('detail(ranked.find(r=>r.combinedCount))',ui);
assert.ok(get('detail').innerHTML.includes('<h2>Other expenses</h2>'));
assert.ok(get('detail').innerHTML.includes('Account groups'));
assert.ok(get('detail').innerHTML.includes('detailFilter3'));
const totalsBefore=get('rankingTotal').innerHTML;
get('detailFilter0').onchange({target:{value:other.rows[0]['Cost Center ID']}});
assert.equal(get('rankingTotal').innerHTML,totalsBefore);
assert.equal(vm.runInContext('selected.ids.size',ui),other.ids.size);
get('detailFilter3').onchange({target:{value:'not-in-other'}});
assert.equal(vm.runInContext('detailFilters["Budget ID"]',ui),'');
get('detailReset').onclick();assert.ok(!get('detail').innerHTML.includes('No included expenses match'));
vm.runInContext('detail(ranked.find(r=>!r.combinedCount))',ui);
assert.ok(get('detail').innerHTML.includes('detailFilter2'));
console.log('Detail filter tests passed: all dimensions, membership isolation, empty results, reset, unchanged ranking and actual UI handlers.');
const {resolvePeriod}=context;
const periods=[['year',1,12,1,1,1,12],['h1',1,12,1,1,1,6],['h2',1,12,1,1,7,12],['range',2,5,1,1,2,5],['range',6,6,1,1,6,6]];
for(let m=1;m<=12;m++)periods.push(['month',1,12,m,1,m,m]);
for(let q=1;q<=4;q++)periods.push(['quarter',1,12,1,q,(q-1)*3+1,q*3]);
for(const [mode,start,end,month,quarter,lo,hi] of periods){
 const p=resolvePeriod(mode,start,end,month,quarter);assert.equal(p.valid,true);assert.equal(p.start,lo);assert.equal(p.end,hi);
 get('start').value=String(start);get('end').value=String(end);get('periodMonth').value=String(month);get('periodQuarter').value=String(quarter);get('periodMode').value=mode;get('periodMode').onchange();
 assert.equal(get('rangeStartField').hidden,mode!=='range');assert.equal(get('monthField').hidden,mode!=='month');assert.equal(get('quarterField').hidden,mode!=='quarter');
 const expected=data.rows.filter(r=>r.month>=lo&&r.month<=hi);const actual=vm.runInContext('sum(current)',ui);
 assert.ok(Math.abs(actual.actual-sum(expected).actual)<.005);assert.ok(Math.abs(actual.budget-sum(expected).budget)<.005);
 const rankedTotals=vm.runInContext('sum(ranked)',ui);assert.ok(Math.abs(rankedTotals.actual-actual.actual)<.005);
 assert.equal(vm.runInContext('current.every(r=>r.month>=selectedPeriod().start&&r.month<=selectedPeriod().end)',ui),true);
}
assert.equal(resolvePeriod('range',12,1).valid,false);assert.equal(resolvePeriod('month',1,12,13).valid,false);
get('periodMode').value='range';get('start').value='12';get('end').value='1';get('periodMode').onchange();assert.ok(get('status').textContent.includes('on or after'));assert.equal(vm.runInContext('current.length',ui),0);
get('reset').onclick();assert.equal(get('periodMode').value,'year');assert.equal(get('rangeStartField').hidden,true);
console.log(`Period tests passed: ${periods.length} selections, quarterly and half-year boundaries, reconciliations, control visibility, invalid range and reset.`);
let comparisonCases=0;
for(const mode of ['budget','forecast','both','forecast_budget'])for(const scenario of ['FQ1','FQ2','FQ3'])for(const [lo,hi] of [[1,12],[1,3],[4,6],[7,9],[10,12]]){
 get('periodMode').value='range';get('start').value=String(lo);get('end').value=String(hi);get('comparisonMode').value=mode;get('forecastScenario').value=scenario;get('threshold').value='1000000000';get('comparisonMode').onchange();
 const source=data.rows.filter(r=>r.month>=lo&&r.month<=hi);const expected=source.reduce((s,r)=>s+(mode==='forecast_budget'?r[scenario]-r.budget:mode==='forecast'?r.actual-r[scenario]:r.actual-r.budget),0);
 const totals=vm.runInContext('sum(current)',ui);assert.ok(Math.abs(totals.variance-expected)<.005);
 const shown=vm.runInContext('sum(ranked)',ui);for(const k of ['actual','budget','forecast','variance','actual_forecast','forecast_delta'])assert.ok(Math.abs(shown[k]-totals[k])<.005);
 assert.ok(Math.abs(totals.base_variance-totals.forecast_delta-totals.actual_forecast)<.005);
 assert.ok(Math.abs(totals.closed_delta+totals.estimate_delta-totals.forecast_delta)<.005);
 assert.equal(get('forecastField').hidden,mode==='budget');
 if(mode==='both')assert.ok(get('rankingHeader').innerHTML.includes('Actual vs Budget')&&get('rankingHeader').innerHTML.includes('Actual vs Q'));
 if(mode==='forecast_budget'){assert.ok(get('detail').innerHTML.includes('supporting rows'));assert.ok(!get('detail').innerHTML.includes('<h3>Supporting transactions</h3>'));}
 if(mode==='forecast'&&hi<=Number(scenario.slice(-1))*3)assert.ok(Math.abs(totals.variance)<.005);
 // Filtering Other must restrict both forecast rows and actual context without changing the ranking.
 const before=get('rankingTotal').innerHTML;get('detailFilter0').onchange({target:{value:'01'}});assert.equal(get('rankingTotal').innerHTML,before);
 comparisonCases++;
}
vm.runInContext('var exported; csv=(name,headers,rows)=>{exported={name,headers,rows};};',ui);
get('export').onclick();assert.ok(vm.runInContext('exported.headers.some(x=>x.includes("Q3 forecast"))',ui));
get('forecastExport').onclick();assert.ok(vm.runInContext('exported.rows.length>0 && exported.rows.every(x=>x[1].startsWith("01-"))',ui));
console.log(`Forecast UI tests passed: ${comparisonCases} scenario/period combinations, closed-month equality, both bridges, Other/detail filters and forecast exports.`);
// Account-group drilldown and cascading option membership.
get('reset').onclick();
assert.ok(get('detail').innerHTML.includes('detailFilter2'));
const regularAccount=vm.runInContext('selected.rows[0]["Account ID"]',ui);
get('detailFilter2').onchange({target:{value:regularAccount}});
assert.equal(vm.runInContext('filterDetailRows(selected.rows,detailFilters).every(r=>r["Account ID"]===detailFilters["Account ID"])',ui),true);
get('threshold').value='1000000000';get('threshold').oninput();
const rankBefore=get('rankingTotal').innerHTML;
get('detailFilter1').onchange({target:{value:'G03'}});
const choiceValues=index=>[...get('detail').innerHTML.match(new RegExp(`<select id="detailFilter${index}">([\\s\\S]*?)</select>`))[1].matchAll(/<option value="([^"]+)"/g)].map(m=>m[1]);
const groupRows=data.rows.filter(r=>r['Account Group ID']==='G03');
assert.deepEqual(new Set(choiceValues(2)),new Set(groupRows.map(r=>r['Account ID'])));
assert.deepEqual(new Set(choiceValues(3)),new Set(groupRows.map(r=>r['Budget ID'])));
const account=groupRows[0]['Account ID'];get('detailFilter2').onchange({target:{value:account}});
assert.deepEqual(new Set(choiceValues(3)),new Set(groupRows.filter(r=>r['Account ID']===account).map(r=>r['Budget ID'])));
get('detailFilter3').onchange({target:{value:choiceValues(3)[0]}});
get('detailFilter1').onchange({target:{value:'G01'}});
assert.equal(vm.runInContext('detailFilters["Account ID"]',ui),'');assert.equal(vm.runInContext('detailFilters["Budget ID"]',ui),'');
assert.deepEqual(new Set(choiceValues(2)),new Set(data.rows.filter(r=>r['Account Group ID']==='G01').map(r=>r['Account ID'])));
get('detailFilter0').onchange({target:{value:'01'}});
assert.deepEqual(new Set(choiceValues(3)),new Set(data.rows.filter(r=>r['Cost Center ID']==='01'&&r['Account Group ID']==='G01').map(r=>r['Budget ID'])));
assert.equal(get('rankingTotal').innerHTML,rankBefore);
get('detailReset').onclick();assert.deepEqual(new Set(choiceValues(3)),new Set(data.rows.map(r=>r['Budget ID'])));
console.log('Cascading filter tests passed: regular account-group drilldown, exact group/account/ID options, cost-center scoping, stale selection clearing and reset.');

