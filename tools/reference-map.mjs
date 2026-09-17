import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import fs from 'fs';
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
const p = await b.newPage({ viewport:{width:390,height:900} });
const errs=[]; p.on('pageerror',e=>errs.push(String(e).slice(0,120)));
await p.clock.setFixedTime(new Date(2026,11,1,12,0));
await p.goto('http://127.0.0.1:8399/index.html?v='+Date.now(), { waitUntil:'domcontentloaded' });
await p.waitForTimeout(1700);
const r = await p.evaluate(() => {
  const built=_yrBuild(); if(!built) return {err:'no year'};
  const L=(typeof YR_LENSES!=='undefined')?YR_LENSES:null;
  if(!L) return {err:'no lenses'};
  const strip=s=>String(s==null?'':s).replace(/<[^>]*>/g,'').replace(/\s+/g,' ').trim();
  const HM=['','Nisan','Iyar','Sivan','Tammuz','Av','Elul','Tishrei','Cheshvan','Kislev','Tevet','Shevat','Adar I','Adar II'];
  const lensName=x=>strip(x.card||x.cycle||'lens');
  const rows=[];
  for(const D of built.days){
    const row={ yearDay:D.yearDay, greg:D.date.toISOString().slice(0,10),
                heb:D.heb.day+' '+HM[D.heb.month], parasha:D.parasha||'' };
    L.forEach((lens,i)=>{
      let v='';
      try{ const s=lens.seg(D); if(s&&s.n!==-1)
             v=[s.cell,s.cell2,s.cell3].map(strip).filter(Boolean).join(' · ');
      }catch(e){ v='ERR'; }
      row['L'+String(i+1).padStart(2,'0')]=v;
    });
    rows.push(row);
  }
  return { names:L.map((x,i)=>'L'+String(i+1).padStart(2,'0')+': '+lensName(x)),
           rows, n:L.length };
});
if(r.err){ console.log('ERROR', r.err); process.exit(1); }
console.log('lenses:', r.n, ' days:', r.rows.length, '\n');
r.names.forEach(n=>console.log('  '+n));
const hdr=Object.keys(r.rows[0]);
const csv=[hdr.join(',')].concat(r.rows.map(x=>hdr.map(h=>{
  const v=String(x[h]??'').replace(/"/g,'""'); return /[,"\n]/.test(v)?'"'+v+'"':v;}).join(','))).join('\n');
const out='/tmp/claude-0/-home-user-kabalahoftime/b6dfddf1-fb45-52cc-bb4a-9c1fdbe9ecfc/scratchpad/reference-map.csv';
fs.writeFileSync(out,csv);
const filled={}; r.names.forEach((n,i)=>{const k='L'+String(i+1).padStart(2,'0');
  filled[k]=r.rows.filter(x=>x[k]).length;});
console.log('\nrows with content, per lens:');
r.names.forEach((n,i)=>{const k='L'+String(i+1).padStart(2,'0');
  console.log('  '+n.padEnd(52)+String(filled[k]).padStart(4)+'/'+r.rows.length);});
console.log('\ncsv bytes:', csv.length, '→', out);
console.log('errors:', errs.length?errs.slice(0,3):'none');
await b.close();
