from pathlib import Path
import json,re

ROOT=Path('.')

p=ROOT/'cards-v014.js'
s=p.read_text(encoding='utf-8')
m=re.fullmatch(r"export const DATA = (.*);\s*",s,re.S)
if not m: raise SystemExit('cards-v014.js format changed')
data=json.loads(m.group(1))
data['version']='0.31 Master Rules'
by={c['id']:c for c in data['cards']}
by['C06']['cost']=7
by['C15']['stats']['Combat']=5
for mid in ['Z3-01','Z3-02','Z3-06','Z3-07']:
    by[mid]['target']=16
p.write_text('export const DATA = '+json.dumps(data,ensure_ascii=False,indent=2)+';\n',encoding='utf-8')

p=ROOT/'engine-v014.mjs'
s=p.read_text(encoding='utf-8')
s=s.replace("export const FACES=['SKULL',0,1,1,2,2,3,'GOLD'];","export const FACES=['SKULL',0,0,1,1,2,2,'GOLD'];")
p.write_text(s,encoding='utf-8')

p=ROOT/'voyage-v014.js'
s=p.read_text(encoding='utf-8').replace('The Final Isle · v0.30','The Final Isle · v0.31').replace('All 81 cards · v0.30','All 81 cards · v0.31')
p.write_text(s,encoding='utf-8')

p=ROOT/'menu.js'
s=p.read_text(encoding='utf-8').replace('version:"0.30"','version:"0.31"')
p.write_text(s,encoding='utf-8')

p=ROOT/'index.html'
s=p.read_text(encoding='utf-8').replace('v0.30','v0.31').replace('SKULL / 0 / 1 / 1 / 2 / 2 / 3 / GOLD','SKULL / 0 / 0 / 1 / 1 / 2 / 2 / GOLD')
p.write_text(s,encoding='utf-8')

p=ROOT/'tests/rules-v031.mjs'
p.write_text("""import assert from 'node:assert/strict';
import {DATA,CARDS,FACES} from '../engine-v014.mjs';
assert.equal(DATA.version,'0.31 Master Rules');
assert.deepEqual(FACES,['SKULL',0,0,1,1,2,2,'GOLD']);
assert.equal(CARDS.C06.cost,7);
assert.equal(CARDS.C15.stats.Combat,5);
for(const id of ['Z3-01','Z3-02','Z3-06','Z3-07']) assert.equal(CARDS[id].target,16,id+' target');
assert.equal(CARDS['Z3-03'].target,12);
assert.equal(CARDS['Z3-04'].target,12);
assert.equal(CARDS['Z3-05'].target,12);
assert.equal(CARDS['Z3-08'].target,11);
assert.equal(CARDS['Z3-09'].target,13);
console.log('v0.31 balance regression passed');
""",encoding='utf-8')
