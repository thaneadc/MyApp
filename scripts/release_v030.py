from pathlib import Path
import json
import re


def read(path):
    return Path(path).read_text(encoding='utf-8')


def write(path, text):
    Path(path).write_text(text, encoding='utf-8')


def require_replace(text, old, new, label):
    if old not in text:
        raise SystemExit(f'{label}: anchor missing')
    return text.replace(old, new, 1)


# -----------------------------------------------------------------------------
# cards-v014.js — Master Rule v0.30 is the source of truth for Crew/Veteran,
# Zone I–III Mission and Final Mission card data.
# -----------------------------------------------------------------------------
path = 'cards-v014.js'
raw = read(path)
m = re.fullmatch(r'\s*export const DATA = (\{.*\});\s*', raw, re.S)
if not m:
    raise SystemExit('cards-v014.js: DATA wrapper not recognized')
data = json.loads(m.group(1))
data['version'] = '0.30 Master Rules'
by_id = {c['id']: c for c in data['cards']}

crew = {
    'C01': ('Common', 2, 1, 1, 1, '- No special ability'),
    'C02': ('Common', 3, 3, 0, 0, 'Bombardment\n- In Zone II and beyond, gain +1 Combat'),
    'C03': ('Veteran', 6, 1, 5, 1, 'Sea Route\n- In Zone III or Final Isle, gain +1 Sailing'),
    'C04': ('Common', 3, 0, 2, 2, 'Keen Eye\n- On a Search Mission, reroll one die showing 0\n- You must keep the new result'),
    'C05': ('Common', 4, 1, 2, 1, 'Plunder\n- After any Mission success, gain +2 Gold'),
    'C06': ('Veteran', 6, 3, 4, 2, 'Prepared Crew\n- Spend 1 fewer Supply when starting an Expedition\n- Minimum cost remains 1'),
    'C07': ('Veteran', 6, 4, 2, 2, 'Take Aim\n- After rolling a Combat Mission without Skull,\n  reroll one die showing 0\n- You must keep the new result'),
    'C08': ('Common', 3, 0, 3, 0, 'Full Sail\n- If this Crew joins a Zone II, Zone III or Final Mission,\n  gain +1 Sailing'),
    'C09': ('Veteran', 7, 1, 3, 5, 'Treasure Sense\n- When you gain Treasure, draw 2 and keep 1'),
    'C10': ('Veteran', 7, 9, 0, 0, 'Reckless Assault\n- If the Mission fails and you must lose 1 Crew,\n  Berserker must be lost first'),
    'C11': ('Common', 3, 1, 1, 2, 'Black Market Connections\n- When this Mission succeeds, gain +1 Gold\n- On a Search Mission, gain +1 Search'),
    'C12': ('Common', 4, 1, 1, 1, 'Patch Them Up\n- Once per Expedition, ignore one Crew loss caused by Mission failure'),
    'C13': ('Common', 5, 1, 1, 3, 'Chart the Unknown\n- Before selecting a Mission, you may look at the face-down card\n  beneath one Mission stack'),
    'C14': ('Veteran', 8, 4, 4, 4, 'Old Salt\n- After Mission success, ready 1 exhausted Crew'),
    'C15': ('Veteran', 8, 6, 3, 3, 'Broadside\n- On a Combat Mission, one Gold result may also count as +1'),
}
for cid, (tier, cost, combat, sailing, search, text) in crew.items():
    c = by_id[cid]
    c['tier'] = tier
    c['cost'] = cost
    c['stats'] = {'Combat': combat, 'Sailing': sailing, 'Search': search}
    c['text'] = text

missions = {
    'Z1-01': ('Combat', 3, {'gold': 5}),
    'Z1-02': ('Search', 4, {'treasure': 1}),
    'Z1-03': ('Sailing', 3, {'supply': 4}),
    'Z1-04': ('Combat', 4, {'gold': 4, 'supply': 2}),
    'Z1-05': ('Sailing', 4, {'crew': 1, 'supply': 2}),
    'Z1-06': ('Combat', 4, {'crew': 1, 'gold': 3}),
    'Z1-07': ('Search', 4, {'supply': 3, 'gold': 3}),
    'Z1-08': ('Combat', 4, {'gold': 5, 'supply': 1}),
    'Z1-09': ('Search', 4, {'treasure': 1, 'gold': 3}),
    'Z1-10': ('Sailing', 3, {'supply': 6}),
    'Z1-11': ('Search', 3, {'treasure': 1, 'supply': 2}),
    'Z1-12': ('Sailing', 3, {'gold': 2, 'supply': 4}),
    'Z1-13': ('Combat', 4, {'crew': 1, 'gold': 4}),
    'Z1-14': ('Search', 4, {'treasure': 1, 'gold': 4}),
    'Z1-15': ('Sailing', 4, {'gold': 4, 'supply': 3}),
    'Z1-16': ('Combat', 4, {'crew': 1, 'supply': 3}),
    'Z1-17': ('Search', 5, {'treasure': 1, 'supply': 3}),
    'Z1-18': ('Sailing', 5, {'gold': 3, 'treasure': 1, 'supply': 1}),
    'Z2-01': ('Combat', 7, {'gold': 6, 'treasure': 1, 'supply': 3}),
    'Z2-02': ('Search', 7, {'supply': 8, 'treasure': 1}),
    'Z2-03': ('Combat', 7, {'gold': 10}),
    'Z2-04': ('Sailing', 6, {'supply': 7, 'gold': 4}),
    'Z2-05': ('Combat', 8, {'crew': 1, 'gold': 5, 'supply': 3}),
    'Z2-06': ('Search', 7, {'supply': 5, 'gold': 5}),
    'Z2-07': ('Search', 7, {'treasure': 1, 'crew': 1, 'supply': 3}),
    'Z2-08': ('Combat', 7, {'veteran': 1, 'supply': 4, 'gold': 3}),
    'Z2-09': ('Sailing', 6, {'supply': 8}),
    'Z2-10': ('Search', 6, {'treasure': 1, 'gold': 4, 'supply': 2}),
    'Z2-11': ('Sailing', 7, {'gold': 7, 'supply': 4}),
    'Z2-12': ('Search', 7, {'treasure': 1, 'supply': 5}),
    'Z2-13': ('Sailing', 7, {'crew': 1, 'supply': 5}),
    'Z2-14': ('Combat', 7, {'veteran': 1, 'supply': 4}),
    'Z3-01': ('Combat + Sailing', 15, {'supply': 8, 'gold': 8, 'treasure': 1}),
    'Z3-02': ('Combat + Search', 15, {'veteran': 1, 'supply': 7, 'gold': 5}),
    'Z3-03': ('Search', 12, {'veteran': 2, 'supply': 6}),
    'Z3-04': ('Sailing', 12, {'supply': 12, 'treasure': 2}),
    'Z3-05': ('Combat', 12, {'veteran': 1, 'gold': 6, 'supply': 8}),
    'Z3-06': ('Search + Sailing', 15, {'supply': 8, 'gold': 6, 'drawTreasure': 2}),
    'Z3-07': ('Sailing + Search', 15, {'veteran': 1, 'treasure': 1, 'supply': 8}),
    'Z3-08': ('Sailing', 11, {'supply': 9, 'veteran': 1, 'gold': 8}),
    'Z3-09': ('Combat', 13, {'veteran': 2, 'treasure': 1, 'supply': 10}),
}
labels = {'gold': 'Gold', 'supply': 'Supply', 'treasure': 'Treasure', 'crew': 'Crew', 'veteran': 'Veteran'}
def reward_text(reward):
    lines = []
    for k, v in reward.items():
        if k == 'drawTreasure':
            lines.append(f'- Draw Treasure {v}, Keep 1')
        else:
            lines.append(f'- {labels[k]} {v}')
    return '\n'.join(lines)

for mid, (test, target, reward) in missions.items():
    c = by_id[mid]
    c['test'] = test
    c['target'] = target
    c['reward'] = reward
    c['text'] = reward_text(reward)

finals = {
    'F1': [
        ('Fight for Coward!', 'Combat', 12, '- Test Type: Combat\n- Target: 12'),
        ('Treasure of the LOST CITY!', 'Search', 16, '- Test Type: Search\n- Target: 16'),
    ],
    'F2': [
        ('Beware Whirlpool!', 'Sailing', 12, '- Test Type: Sailing\n- Target: 12'),
        ('Fight the Guardian!', 'Combat', 16, '- Test Type: Combat\n- Target: 16'),
    ],
    'F3': [
        ('Search for your sage!', 'Search', 10, '- Pay 6 Gold\nOR discard 1 Treasure\nReward:\n- Test Type: Search\n- Target: 10'),
        ('Fight for your life!', 'Combat', 16, '- Test Type: Combat\n- Target: 16'),
    ],
    'F4': [
        ('Sail to the Throne of OUR KING', 'Sailing', 10, 'Must have all:\n- 4 Crew\n- at least 2 Veteran\n- at least 2 Treasure\n\n- Test Type: Sailing\n- Target: 10'),
        ('Bring OUR PIRATE KING back!', 'Search', 16, '- Test Type: Search\n- Target: 16'),
    ],
    'F5': [
        ('Approach them!', 'Search', 10, '- At least 3 different Crew types\n- At least 1 Veteran\n\n- Test Type: Search\n- Target: 10'),
        ('Leave them alone!', 'Sailing', 16, '- Test Type: Sailing\n- Target: 16'),
    ],
}
for fid, steps in finals.items():
    by_id[fid]['steps'] = [
        {'name': name, 'test': test, 'target': target, 'text': text}
        for name, test, target, text in steps
    ]

write(path, 'export const DATA = ' + json.dumps(data, ensure_ascii=False, indent=2) + ';\n')


# -----------------------------------------------------------------------------
# engine-v014.mjs — d8 faces and combined Zone III tests.
# A combined test such as "Combat + Sailing" adds both relevant Crew stats,
# both relevant passives/abilities, then adds the normal Zone III 3d8 result.
# -----------------------------------------------------------------------------
path = 'engine-v014.mjs'
s = read(path)
s = require_replace(s,
    "export const FACES=['SKULL',0,0,1,1,2,2,'GOLD'];",
    "export const FACES=['SKULL',0,1,1,2,2,3,'GOLD'];",
    'd8 faces')

old = """export function testInfo(e){const c=CARDS[e.mission];return c.kind==='final'?c.steps[e.step||0]:c}\nexport function crewScore(p,e){const t=testInfo(e).test,z=CARDS[e.mission].zone||4;let n=selected(p,e).reduce((v,c)=>v+CARDS[c.id].stats[t],0);if(t==='Combat')n+=count(p,e,'C02')+count(p,e,'C10');if(t==='Sailing'&&z>=2)n+=count(p,e,'C03')+count(p,e,'C08');if(t==='Search')n+=count(p,e,'C11');return n}\nexport function baseScore(p,e){const t=testInfo(e).test,z=CARDS[e.mission].zone||4;let n=crewScore(p,e);const bonus={Combat:{T05:2,T08:1},Sailing:{T04:2},Search:{T01:1,T02:z===4?2:1,T10:1,T12:1}};for(const [id,v]of Object.entries(bonus[t]))if(has(e,id))n+=v;if(e.blessing===t)n+=3;if(e.powder&&t==='Combat')n+=2;return n}\nexport function totalScore(p,e){return baseScore(p,e)+e.dice.reduce((n,d)=>n+(typeof d==='number'?d:0),0)+(has(e,'T13')&&!e.dice.includes('SKULL')?2:0)+(testInfo(e).test==='Combat'&&count(p,e,'C15')&&e.dice.includes('GOLD')?1:0)}"""
new = """export function testInfo(e){const c=CARDS[e.mission];return c.kind==='final'?c.steps[e.step||0]:c}\nconst splitTests=t=>String(t||'').split(/\\s*\\+\\s*/).filter(Boolean);\nconst hasTest=(e,t)=>splitTests(testInfo(e).test).includes(t);\nconst cardHasTest=(c,t)=>splitTests(c?.test).includes(t)||c?.steps?.some(st=>splitTests(st.test).includes(t));\nexport function crewScore(p,e){const tests=splitTests(testInfo(e).test),z=CARDS[e.mission].zone||4;let n=selected(p,e).reduce((v,c)=>v+tests.reduce((sum,t)=>sum+(CARDS[c.id].stats[t]||0),0),0);if(tests.includes('Combat')&&z>=2)n+=count(p,e,'C02');if(tests.includes('Sailing')&&z>=3)n+=count(p,e,'C03');if(tests.includes('Sailing')&&z>=2)n+=count(p,e,'C08');if(tests.includes('Search'))n+=count(p,e,'C11');return n}\nexport function baseScore(p,e){const tests=splitTests(testInfo(e).test),z=CARDS[e.mission].zone||4;let n=crewScore(p,e);const bonus={Combat:{T05:2,T08:1},Sailing:{T04:2},Search:{T01:1,T02:z===4?2:1,T10:1,T12:1}};for(const t of tests)for(const [id,v]of Object.entries(bonus[t]||{}))if(has(e,id))n+=v;if(tests.includes(e.blessing))n+=3;if(e.powder&&tests.includes('Combat'))n+=2;return n}\nexport function totalScore(p,e){return baseScore(p,e)+e.dice.reduce((n,d)=>n+(typeof d==='number'?d:0),0)+(has(e,'T13')&&!e.dice.includes('SKULL')?2:0)+(hasTest(e,'Combat')&&count(p,e,'C15')&&e.dice.includes('GOLD')?1:0)}"""
s = require_replace(s, old, new, 'combined test scoring')

s = require_replace(s,
    "function resolveOutcome(s,rng){const p=current(s),e=s.exp,c=CARDS[e.mission],t=testInfo(e).test;",
    "function resolveOutcome(s,rng){const p=current(s),e=s.exp,c=CARDS[e.mission],t=testInfo(e).test,tests=splitTests(t);",
    'resolveOutcome tests')
s = require_replace(s,
    "if(t==='Combat'&&has(e,'T08'))p.gold+=2;if(has(e,'T10'))p.supply++;if(t==='Search'&&c.target>=8&&has(e,'T12'))p.gold+=2;",
    "if(tests.includes('Combat')&&has(e,'T08'))p.gold+=2;if(has(e,'T10'))p.supply++;if(tests.includes('Search')&&c.target>=8&&has(e,'T12'))p.gold+=2;",
    'reward test passives')
s = require_replace(s,
    "function awardDice(p,e,newFaces){p.gold+=newFaces.filter(d=>d==='GOLD').length*(has(e,'T09')?2:1);e.awarded||={};if(testInfo(e).test==='Combat'&&has(e,'T06')&&e.dice.includes(2)&&!e.awarded.T06){p.gold++;e.awarded.T06=true}",
    "function awardDice(p,e,newFaces){p.gold+=newFaces.filter(d=>d==='GOLD').length*(has(e,'T09')?2:1);e.awarded||={};if(hasTest(e,'Combat')&&has(e,'T06')&&e.dice.includes(2)&&!e.awarded.T06){p.gold++;e.awarded.T06=true}",
    'royal flintlock combined tests')
s = require_replace(s,
    "export function controls(s){const e=s.exp;if(!e||e.phase!=='dice'||e.dice.includes('SKULL'))return [];const p=current(s),t=testInfo(e).test,opts=[];if(e.dice.includes(0)){for(const c of selected(p,e))if((c.id==='C04'&&t==='Search'||c.id==='C07'&&t==='Combat')&&!e.used.includes(c.uid))opts.push({id:c.uid,label:CARDS[c.id].name+' · reroll a 0'});",
    "export function controls(s){const e=s.exp;if(!e||e.phase!=='dice'||e.dice.includes('SKULL'))return [];const p=current(s),tests=splitTests(testInfo(e).test),opts=[];if(e.dice.includes(0)){for(const c of selected(p,e))if((c.id==='C04'&&tests.includes('Search')||c.id==='C07'&&tests.includes('Combat'))&&!e.used.includes(c.uid))opts.push({id:c.uid,label:CARDS[c.id].name+' · reroll a 0'});",
    'crew rerolls combined tests')
s = require_replace(s,
    "if(a.powder)must(has(exp,'T07')&&(c.test==='Combat'||c.steps?.some(st=>st.test==='Combat')),'Black Powder Horn requires a Combat test');",
    "if(a.powder)must(has(exp,'T07')&&cardHasTest(c,'Combat'),'Black Powder Horn requires a Combat test');",
    'powder combined tests')
write(path, s)


# -----------------------------------------------------------------------------
# voyage-v014.js — render combined test icons/values and v0.30 labels.
# -----------------------------------------------------------------------------
path = 'voyage-v014.js'
s = read(path)
anchor = "const icons={Combat:testIcon('Combat'),Sailing:testIcon('Sailing'),Search:testIcon('Search')};"
insert = anchor + "\nconst testTypes=t=>String(t||'').split(/\\s*\\+\\s*/).filter(Boolean);\nconst testGlyphs=t=>testTypes(t).map(x=>icons[x]||'').join('<span class=\"testPlus\">+</span>');\nconst hasTestType=(t,type)=>testTypes(t).includes(type);\nconst crewTestValue=(c,t)=>testTypes(t).reduce((n,k)=>n+(c.stats?.[k]||0),0);"
s = require_replace(s, anchor, insert, 'voyage test helpers')
s = require_replace(s,
    "function missionTestBox(c){return `<div class=\"missionTestBox\"><span class=\"missionTestType\"><i class=\"testGlyph\">${icons[c.test]}</i><span><small>TEST</small><strong>${esc(c.test)}</strong></span></span><span class=\"missionTarget\"><small>TARGET</small><strong>${c.target}</strong></span></div>`}",
    "function missionTestBox(c){return `<div class=\"missionTestBox\"><span class=\"missionTestType\"><i class=\"testGlyph\">${testGlyphs(c.test)}</i><span><small>TEST</small><strong>${esc(c.test)}</strong></span></span><span class=\"missionTarget\"><small>TARGET</small><strong>${c.target}</strong></span></div>`}",
    'mission combined icons')
s = require_replace(s,
    "${c.kind==='final'?'TWO TESTS':icons[c.test]+' '+c.target}",
    "${c.kind==='final'?'TWO TESTS':testGlyphs(c.test)+' '+c.target}",
    'board mission tile icons')
s = require_replace(s,
    "${icons[info.test]} ${info.test} <b>${c.stats[info.test]||0}</b>",
    "${testGlyphs(info.test)} ${esc(info.test)} <b>${crewTestValue(c,info.test)}</b>",
    'expedition crew combined value')
s = require_replace(s,
    "${icons[info.test]} ${esc(info.test)} Test",
    "${testGlyphs(info.test)} ${esc(info.test)} Test",
    'expedition test header')
s = require_replace(s,
    "${icons[c.test]} ${esc(c.test)} · Target ${c.target}",
    "${testGlyphs(c.test)} ${esc(c.test)} · Target ${c.target}",
    'completed mission combined icons')
s = require_replace(s,
    "p.treasures.includes('T07')&&(c.test==='Combat'||c.steps?.some(st=>st.test==='Combat'))",
    "p.treasures.includes('T07')&&(hasTestType(c.test,'Combat')||c.steps?.some(st=>hasTestType(st.test,'Combat')))",
    'voyage powder combined tests')
s = s.replace('The Final Isle · v0.29', 'The Final Isle · v0.30')
s = s.replace("modal('All 81 cards · v0.26'", "modal('All 81 cards · v0.30'")
write(path, s)


# -----------------------------------------------------------------------------
# menu/index release labels and d8 face legend.
# -----------------------------------------------------------------------------
path = 'menu.js'
s = read(path)
s = require_replace(s, 'version:"0.29"', 'version:"0.30"', 'menu setup version')
write(path, s)

path = 'index.html'
s = read(path)
s = s.replace('v0.29 Test', 'v0.30 Test').replace('v0.29 TEST', 'v0.30 TEST')
s = require_replace(s,
    '<span>🎲 <b>Custom Dice</b> · SKULL / 0 / 0 / 1 / 2 / GOLD</span>',
    '<span>🎲 <b>Custom d8</b> · SKULL / 0 / 1 / 1 / 2 / 2 / 3 / GOLD</span>',
    'd8 footer legend')
write(path, s)


# -----------------------------------------------------------------------------
# Focused v0.30 regression tests.
# -----------------------------------------------------------------------------
test = r'''import assert from 'node:assert/strict';
import fs from 'node:fs';
import {DATA,CARDS,FACES,baseScore,totalScore} from '../engine-v014.mjs';

assert.equal(DATA.version,'0.30 Master Rules');
assert.deepEqual(FACES,['SKULL',0,1,1,2,2,3,'GOLD']);

const crewExpected={
 C01:['Common',2,1,1,1], C02:['Common',3,3,0,0], C03:['Veteran',6,1,5,1],
 C04:['Common',3,0,2,2], C05:['Common',4,1,2,1], C06:['Veteran',6,3,4,2],
 C07:['Veteran',6,4,2,2], C08:['Common',3,0,3,0], C09:['Veteran',7,1,3,5],
 C10:['Veteran',7,9,0,0], C11:['Common',3,1,1,2], C12:['Common',4,1,1,1],
 C13:['Common',5,1,1,3], C14:['Veteran',8,4,4,4], C15:['Veteran',8,6,3,3]
};
for(const [id,[tier,cost,combat,sailing,search]] of Object.entries(crewExpected)){
 const c=CARDS[id];
 assert.equal(c.tier,tier,id+' tier'); assert.equal(c.cost,cost,id+' cost');
 assert.deepEqual(c.stats,{Combat:combat,Sailing:sailing,Search:search},id+' stats');
}

const z3={
 'Z3-01':['Combat + Sailing',15], 'Z3-02':['Combat + Search',15], 'Z3-03':['Search',12],
 'Z3-04':['Sailing',12], 'Z3-05':['Combat',12], 'Z3-06':['Search + Sailing',15],
 'Z3-07':['Sailing + Search',15], 'Z3-08':['Sailing',11], 'Z3-09':['Combat',13]
};
for(const [id,[test,target]] of Object.entries(z3)){assert.equal(CARDS[id].test,test,id+' test');assert.equal(CARDS[id].target,target,id+' target')}

assert.deepEqual(CARDS.F1?.steps,undefined); // guard accidental property-style lookup
const finalExpected={F1:[12,16],F2:[12,16],F3:[10,16],F4:[10,16],F5:[10,16]};
for(const [id,targets] of Object.entries(finalExpected))assert.deepEqual(CARDS[id].steps.map(x=>x.target),targets,id+' final targets');

const mk=(ids,mission,dice=[])=>{
 const crew=ids.map((id,i)=>({id,uid:'u'+i,exhausted:false}));
 const p={crew,treasures:[]};
 const e={mission,crew:crew.map(x=>x.uid),treasures:[],step:0,dice,blessing:null,powder:false};
 return {p,e};
};
let x=mk(['C02','C03'],'Z3-01');
assert.equal(baseScore(x.p,x.e),11,'Combat + Sailing must sum both stats and applicable crew abilities');
assert.equal(totalScore(x.p,{...x.e,dice:[1,2,3]}),17,'combined test must add the normal dice result once');
x=mk(['C10'],'Z3-09');
assert.equal(baseScore(x.p,x.e),9,'Berserker uses Combat 9 without a hidden +1 bonus');
x=mk(['C03'],'Z2-04');
assert.equal(baseScore(x.p,x.e),5,'Experienced Navigator gains no Sea Route bonus in Zone II');
x=mk(['C03'],'Z3-04');
assert.equal(baseScore(x.p,x.e),6,'Experienced Navigator gains +1 Sailing in Zone III');
x=mk(['C02'],'Z1-01');
assert.equal(baseScore(x.p,x.e),3,'Heavy Fire has no Bombardment bonus in Zone I');
x=mk(['C02'],'Z2-03');
assert.equal(baseScore(x.p,x.e),4,'Heavy Fire gains +1 Combat in Zone II+');

const voyage=fs.readFileSync(new URL('../voyage-v014.js',import.meta.url),'utf8');
const menu=fs.readFileSync(new URL('../menu.js',import.meta.url),'utf8');
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
assert.match(voyage,/testGlyphs/); assert.match(voyage,/v0\.30/); assert.match(menu,/version:"0\.30"/);
assert.match(html,/v0\.30 TEST/); assert.match(html,/SKULL \/ 0 \/ 1 \/ 1 \/ 2 \/ 2 \/ 3 \/ GOLD/);
console.log('v0.30 assertions passed: Master Rule crew/veteran values, mission targets, combined Zone III tests, Final targets and d8 faces.');
'''
Path('tests/rules-v030.mjs').write_text(test, encoding='utf-8')

print('v0.30 Master Rule card/engine/UI patch applied')
