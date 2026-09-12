import assert from 'node:assert/strict';
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
