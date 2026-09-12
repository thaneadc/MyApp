import assert from 'node:assert/strict';
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
assert.doesNotMatch(voyage,/Pay 6 Gold/);assert.doesNotMatch(voyage,/Requires 4 Crew/);assert.match(voyage,/v0\.32/);
console.log('v0.32 Final Mission regression passed');
