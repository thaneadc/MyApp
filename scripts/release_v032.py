from pathlib import Path
import json,re

ROOT=Path('.')

def must_replace(text, old, new, label):
    if old not in text:
        raise SystemExit(f'missing replacement target: {label}')
    return text.replace(old,new)

# Card database: keep v0.31 balance, replace Final Missions with v0.32 source of truth.
p=ROOT/'cards-v014.js'
s=p.read_text(encoding='utf-8')
m=re.fullmatch(r"export const DATA = (.*);\s*",s,re.S)
if not m: raise SystemExit('cards-v014.js format changed')
data=json.loads(m.group(1))
data['version']='0.32 Master Rules'
by={c['id']:c for c in data['cards']}
finals={
 'F1':[
   {'name':'Fight for Coward!','test':'Combat + Sailing','target':18,'text':'- Test Type: Combat + Sailing\n- Target: 18'},
   {'name':'Treasure of the LOST CITY!','test':'Search','target':16,'text':'- Test Type: Search\n- Target: 16'}],
 'F2':[
   {'name':'Beware Whirlpool!','test':'Sailing','target':12,'text':'- Test Type: Sailing\n- Target: 12'},
   {'name':'Fight the Guardian!','test':'Combat','target':16,'text':'- Test Type: Combat\n- Target: 16'}],
 'F3':[
   {'name':'Search for your sage!','test':'Search','target':12,'text':'- Test Type: Search\n- Target: 12'},
   {'name':'Fight for your life!','test':'Combat','target':16,'text':'- Test Type: Combat\n- Target: 16'}],
 'F4':[
   {'name':'Sail to the Throne of OUR KING','test':'Sailing','target':12,'text':'- Test Type: Sailing\n- Target: 12'},
   {'name':'Bring OUR PIRATE KING back!','test':'Search + Combat','target':22,'text':'- Test Type: Search + Combat\n- Target: 22'}],
 'F5':[
   {'name':'Approach them!','test':'Search','target':11,'text':'- Test Type: Search\n- Target: 11'},
   {'name':'Leave them alone!','test':'Sailing + Combat','target':22,'text':'- Test Type: Sailing + Combat\n- Target: 22'}]
}
for fid,steps in finals.items(): by[fid]['steps']=steps
p.write_text('export const DATA = '+json.dumps(data,ensure_ascii=False,indent=2)+';\n',encoding='utf-8')

# Engine: v0.32 has no special entry requirements or payment on F3/F4/F5.
p=ROOT/'engine-v014.mjs'
s=p.read_text(encoding='utf-8')
old=""" const crew=selected(p,exp),vet=crew.filter(c=>CARDS[c.id].tier==='Veteran').length;\n if(c.id==='F4')must(crew.length===4&&vet>=2&&p.treasures.length>=2,'Requires 4 Crew, 2 Veterans and 2 Treasures');if(c.id==='F5')must(new Set(crew.map(c=>c.id)).size>=3&&vet>=1,'Requires 3 different Crew types and 1 Veteran');\n let gold=0;if(c.id==='F3'){if(a.payment==='treasure'){must(p.treasures.includes(a.sacrifice),'Choose Treasure to discard');p.treasures=p.treasures.filter(id=>id!==a.sacrifice);exp.treasures=[...p.treasures];s.treasureDiscard.push(a.sacrifice)}else gold=6}\n"""
new=""" const crew=selected(p,exp);\n let gold=0;\n"""
s=must_replace(s,old,new,'remove v0.31 Final entry/payment gates')
p.write_text(s,encoding='utf-8')

# UI + AI: remove F3 payment controls and old F4/F5 eligibility gates; update version labels.
p=ROOT/'voyage-v014.js'
s=p.read_text(encoding='utf-8')
s=s.replace('The Final Isle · v0.31','The Final Isle · v0.32').replace('All 81 cards · v0.31','All 81 cards · v0.32')
old="""${c.id==='F3'?`<div class=\"prepSpecial\"><p>Step 1 cost</p><select id=\"payment\"><option value=\"gold\">Pay 6 Gold</option><option value=\"treasure\">Discard 1 Treasure</option></select><select id=\"sacrifice\" aria-label=\"Treasure to discard\">${p.treasures.map(id=>`<option value=\"${id}\">${esc(CARDS[id].name)}</option>`).join('')}</select></div>`:''}"""
s=must_replace(s,old,'','remove F3 preparation payment UI')
old="""const update=()=>{const crew=[...body.querySelectorAll('[name=crew]:checked')].map(x=>x.value),treasures=p.treasures.filter(t=>!(c.id==='F3'&&body.querySelector('#payment').value==='treasure'&&body.querySelector('#sacrifice').value===t)),e={mission:id,crew,treasures,step:0,blessing:p.blessing,powder:!!body.querySelector('#powder')?.checked};body.querySelector('#previewCost').textContent=`${crew.length}/4 Crew · ${testInfo(e).test} ${baseScore(p,e)} before dice · ${supplyCost(p,c.zone||4,treasures,crew)+(e.powder?1:0)} Supply${c.id==='F3'&&body.querySelector('#payment').value==='gold'?' + 6 Gold':''}`;let reason='';try{act(state,{type:'launch',mission:id,crew,payment:body.querySelector('#payment')?.value,sacrifice:body.querySelector('#sacrifice')?.value,powder:e.powder})}"""
new="""const update=()=>{const crew=[...body.querySelectorAll('[name=crew]:checked')].map(x=>x.value),treasures=[...p.treasures],e={mission:id,crew,treasures,step:0,blessing:p.blessing,powder:!!body.querySelector('#powder')?.checked};body.querySelector('#previewCost').textContent=`${crew.length}/4 Crew · ${testInfo(e).test} ${baseScore(p,e)} before dice · ${supplyCost(p,c.zone||4,treasures,crew)+(e.powder?1:0)} Supply`;let reason='';try{act(state,{type:'launch',mission:id,crew,powder:e.powder})}"""
s=must_replace(s,old,new,'simplify Final preparation preview')
old="""if(name==='launch')Object.assign(a,{mission:d.id,crew:[...body.querySelectorAll('[name=crew]:checked')].map(x=>x.value),payment:body.querySelector('#payment')?.value,sacrifice:body.querySelector('#sacrifice')?.value,powder:!!body.querySelector('#powder')?.checked});"""
new="""if(name==='launch')Object.assign(a,{mission:d.id,crew:[...body.querySelectorAll('[name=crew]:checked')].map(x=>x.value),powder:!!body.querySelector('#powder')?.checked});"""
s=must_replace(s,old,new,'remove Final payment launch payload')
old="""&&(id!=='F3'||p.gold>=6||p.treasures.length)&&(id!=='F4'||crew.length===4&&p.crew.filter(x=>crew.includes(x.uid)&&CARDS[x.id].tier==='Veteran').length>=2&&p.treasures.length>=2)&&(id!=='F5'||new Set(p.crew.filter(x=>crew.includes(x.uid)).map(c=>c.id)).size>=3&&p.crew.some(x=>crew.includes(x.uid)&&CARDS[x.id].tier==='Veteran'))"""
s=must_replace(s,old,'','remove AI Final special gates')
old="""if(id){a={type:'launch',mission:id,crew};if(id==='F3'&&p.gold<6&&p.treasures.length){a.payment='treasure';a.sacrifice=p.treasures[0]}}"""
new="""if(id){a={type:'launch',mission:id,crew}}"""
s=must_replace(s,old,new,'remove AI F3 payment')
p.write_text(s,encoding='utf-8')

# Menu / landing page version labels.
p=ROOT/'menu.js'
s=p.read_text(encoding='utf-8').replace('version:"0.31"','version:"0.32"')
p.write_text(s,encoding='utf-8')
p=ROOT/'index.html'
s=p.read_text(encoding='utf-8').replace('v0.31','v0.32')
p.write_text(s,encoding='utf-8')

# Core regression expectations that changed with v0.32 Final rules.
p=ROOT/'tests/rules-v014.mjs'
s=p.read_text(encoding='utf-8')
old="""throws(()=>expedition('F4',['C01']));throws(()=>expedition('F5',['C14','C14','C14']));e=expedition('F3',['C14']);eq(current(e).gold,24);"""
new="""e=expedition('F4',['C01']);eq(e.exp.mission,'F4');e=expedition('F5',['C01']);eq(e.exp.mission,'F5');e=expedition('F3',['C14']);eq(current(e).gold,30);"""
s=must_replace(s,old,new,'legacy Final expectations')
p.write_text(s,encoding='utf-8')

# New v0.32 regression.
p=ROOT/'tests/rules-v032.mjs'
p.write_text("""import assert from 'node:assert/strict';
import fs from 'node:fs';
import {DATA,CARDS,newGame,current,act,baseScore} from '../engine-v014.mjs';
assert.equal(DATA.version,'0.32 Master Rules');
const expected={
 F1:[['Combat + Sailing',18],['Search',16]],
 F2:[['Sailing',12],['Combat',16]],
 F3:[['Search',12],['Combat',16]],
 F4:[['Sailing',12],['Search + Combat',22]],
 F5:[['Search',11],['Sailing + Combat',22]],
};
for(const [id,steps] of Object.entries(expected)){
 assert.deepEqual(CARDS[id].steps.map(s=>[s.test,s.target]),steps,id);
}
// Combined Final scoring must sum both relevant Crew stats and existing bonuses.
const p={crew:[{id:'C14',uid:'u1',exhausted:false},{id:'C15',uid:'u2',exhausted:false}],treasures:[]};
assert.equal(baseScore(p,{mission:'F1',crew:['u1','u2'],treasures:[],step:0,blessing:null,powder:false}),16);
assert.equal(baseScore(p,{mission:'F4',crew:['u1','u2'],treasures:[],step:1,blessing:null,powder:false}),16);
// F3/F4/F5 no longer have entry payments or composition requirements.
function launch(id,crew=['C01']){
 let s=newGame({players:2});const pl=current(s);pl.gold=30;pl.supply=30;pl.crew=crew.map((cid,i)=>({id:cid,uid:'u'+i,exhausted:false}));s.progress=[2,2,1];s.final=[id];s.workers.dock=null;s=act(s,{type:'worker',location:'dock'});return act(s,{type:'launch',mission:id,crew:pl.crew.map(c=>c.uid)});
}
let s=launch('F3');assert.equal(current(s).gold,30);assert.equal(current(s).treasures.length,0);
s=launch('F4');assert.equal(s.exp.mission,'F4');
s=launch('F5');assert.equal(s.exp.mission,'F5');
const voyage=fs.readFileSync(new URL('../voyage-v014.js',import.meta.url),'utf8');
assert.doesNotMatch(voyage,/Pay 6 Gold/);assert.doesNotMatch(voyage,/Requires 4 Crew/);assert.match(voyage,/v0\\.32/);
console.log('v0.32 Final Mission regression passed');
""",encoding='utf-8')
