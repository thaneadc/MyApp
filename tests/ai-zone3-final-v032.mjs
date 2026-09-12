import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {newGame,available,playerZoneEligible} from '../engine-v014.mjs';

// Global progression remains shared for Zone III and Final Isle.
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

const ui=readFileSync(new URL('../voyage-v014.js',import.meta.url),'utf8');
const engine=readFileSync(new URL('../engine-v014.mjs',import.meta.url),'utf8');
assert(!ui.includes('baseScore(p,e)>=testInfo(e).target-2'),'old over-conservative threshold must stay removed');
assert(ui.includes("target-((c.zone||4)>=3?4:2)"),'Zone III/Final should allow up to 4 dice power gap');
assert(ui.includes("tired&&(unlocked(state,3)||ready<=1)"),'late-game AI should recover exhausted crew before docking');
// v0.32 removes the special F3 payment and F4/F5 composition gates for both humans and AI.
assert(!ui.includes("id!=='F3'||p.gold>=6||p.treasures.length"));
assert(!ui.includes("a.payment='treasure'"));
assert(!ui.includes("id!=='F4'||crew.length===4"));
assert(!ui.includes("id!=='F5'||new Set"));
assert(!engine.includes('Requires 4 Crew, 2 Veterans and 2 Treasures'));
assert(!engine.includes('Requires 3 different Crew types and 1 Veteran'));
assert(!engine.includes("c.id==='F3'"));

console.log('AI Zone III / Final v0.32 regression passed');
