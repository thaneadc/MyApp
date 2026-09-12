from pathlib import Path

ROOT=Path('.')
p=ROOT/'voyage-v014.js'
s=p.read_text(encoding='utf-8')
old="""const complete=()=>{busy=false;showPending();if(state.status!=='won'&&state.exp){const e=state.exp,old=previous.exp;if(e.phase==='loss'&&old?.phase!=='loss')resultFlash(dlg,false);else if(e.success===true&&old?.success!==true)resultFlash(dlg,true);else if(old&&e.step>old.step)resultFlash(dlg,true,true)}scheduleAI()}"""
new="""const complete=()=>{busy=false;showPending();if(state.status!=='won'&&state.exp){const e=state.exp,old=previous.exp,isFinal=CARDS[e.mission]?.kind==='final';if(e.phase==='loss'&&old?.phase!=='loss'){resultFlash(dlg,false);if(isAITurn()&&isFinal)aiDelayOverride=2000}else if(e.success===true&&old?.success!==true)resultFlash(dlg,true);else if(old&&e.step>old.step){resultFlash(dlg,true,true);if(isAITurn()&&isFinal)aiDelayOverride=2300}else if(a.type==='roll'&&isAITurn()&&isFinal&&e.step===1&&e.phase==='dice')aiDelayOverride=1800}scheduleAI()}"""
if old not in s:
    raise SystemExit('doAct completion block changed; patch target not found')
p.write_text(s.replace(old,new),encoding='utf-8')

# Add a deterministic lifecycle regression: passing Step 1 must not win the game.
t=ROOT/'tests/final-two-step-lifecycle-v0321.mjs'
t.write_text("""import assert from 'node:assert/strict';
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
""",encoding='utf-8')

# Add static guards for AI pacing so Step 2 remains visible after the Step 1 flash.
t=ROOT/'tests/ai-final-step2-visibility-v0321.mjs'
t.write_text("""import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const ui=readFileSync(new URL('../voyage-v014.js',import.meta.url),'utf8');
assert.match(ui,/e\.step>old\.step\)\{resultFlash\(dlg,true,true\);if\(isAITurn\(\)&&isFinal\)aiDelayOverride=2300/,'AI must wait until the Step 1 success overlay clears');
assert.match(ui,/a\.type==='roll'&&isAITurn\(\)&&isFinal&&e\.step===1&&e\.phase==='dice'\)aiDelayOverride=1800/,'AI must keep Step 2 dice visible before resolving');
console.log('AI Final Step 2 visibility regression passed');
""",encoding='utf-8')
