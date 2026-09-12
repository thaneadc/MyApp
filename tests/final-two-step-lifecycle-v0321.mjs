import assert from 'node:assert/strict';
import {newGame,current,act} from '../engine-v014.mjs';

let s=newGame({players:2},()=>0.417);
const p=current(s);
p.gold=30;
p.supply=30;
p.crew=Array.from({length:4},(_,i)=>({id:'C14',uid:'u'+i,exhausted:false}));
s.progress=[2,2,1];
s.final=['F2'];
s.workers.dock=null;
s=act(s,{type:'worker',location:'dock'});
s=act(s,{type:'launch',mission:'F2',crew:p.crew.map(c=>c.uid)});

// F2 Step 1 is Sailing 12. Four Veteran Pirates provide 16 before dice.
s=act(s,{type:'roll'},()=>0.2); // all dice -> 0, no Skull
s=act(s,{type:'resolve'});
assert.equal(s.status,'playing','passing Final Step 1 must not end the game');
assert.equal(s.exp.step,1,'Final Mission must advance to Step 2');
assert.equal(s.exp.phase,'ready','Step 2 must wait for a fresh roll');
assert.equal(s.exp.success,null,'Step 1 success must be cleared before Step 2');

// F2 Step 2 is Combat 16. The same four Veteran Pirates provide exactly 16.
s=act(s,{type:'roll'},()=>0.2);
s=act(s,{type:'resolve'});
assert.equal(s.status,'won','Final Mission may end the game only after Step 2 succeeds');
assert.equal(s.winner,0);

console.log('Final two-step lifecycle v0.32.1 regression passed');
