import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {newGame,available,playerZoneEligible} from '../engine-v014.mjs';

// Global progression: an AI that personally cleared no prior-zone mission must
// still be allowed into a globally unlocked Zone III and Final Isle.
const s=newGame({mode:'ai',players:3},()=>0.417);
s.progress=[2,2,1];
const aiIndex=s.players.findIndex(p=>p.isAI);
assert(aiIndex>=0,'expected at least one AI player');
s.turn=aiIndex;
const z3=s.stacks[3].find(st=>st.length)?.[0];
assert(z3,'expected a Zone III mission');
assert.equal(playerZoneEligible(s,3,aiIndex),true);
assert.equal(available(s,z3),true,'globally unlocked Zone III must be available to AI');
const finalId=s.final[0];
assert(finalId,'expected a Final mission');
assert.equal(playerZoneEligible(s,4,aiIndex),true);
assert.equal(available(s,finalId),true,'globally unlocked Final must be available to AI');

// Static guards for the late-game AI fixes.
const ui=readFileSync(new URL('../voyage-v014.js',import.meta.url),'utf8');
assert(!ui.includes('baseScore(p,e)>=testInfo(e).target-2'),'old over-conservative threshold must be removed');
assert(ui.includes("target-((c.zone||4)>=3?4:2)"),'Zone III/Final should allow up to 4 dice power gap');
assert(ui.includes("(id!=='F3'||p.gold>=6||p.treasures.length)"),'F3 must accept Treasure affordability');
assert(ui.includes("a.payment='treasure';a.sacrifice=p.treasures[0]"),'AI must submit F3 Treasure payment');
assert(ui.includes("crew.length===4&&p.crew.filter(x=>crew.includes(x.uid)&&CARDS[x.id].tier==='Veteran').length>=2"),'F4 must use Ready Crew');
assert(ui.includes("p.crew.filter(x=>crew.includes(x.uid)).map(c=>c.id)"),'F5 unique crew check must use Ready Crew');
assert(ui.includes("tired&&(unlocked(state,3)||ready<=1)"),'late-game AI should recover exhausted crew before docking');

console.log('AI Zone III / Final v0.30.1 regression passed');
