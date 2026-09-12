from pathlib import Path


def replace_once(path, old, new):
    p = Path(path)
    text = p.read_text(encoding='utf-8')
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{path}: expected exactly one match, found {count}: {old[:100]!r}')
    p.write_text(text.replace(old, new, 1), encoding='utf-8')


# Master Rule v0.30 says zone progression is global. Remove the accidental
# per-player previous-zone completion gate while preserving the existing helper
# used by the UI.
replace_once(
    'engine-v014.mjs',
    "export function playerZoneEligible(s,z,playerIndex=s.turn){if(z<=1)return true;const prev=z-1;if(!zoneHasMission(s,prev))return true;return playerCompletedMissions(s,playerIndex).some(id=>CARDS[id]?.zone===prev)}",
    "export function playerZoneEligible(s,z,playerIndex=s.turn){return unlocked(s,z)}"
)
replace_once(
    'engine-v014.mjs',
    "if(!z||!unlocked(s,z)||!playerZoneEligible(s,z))return false;",
    "if(!z||!unlocked(s,z))return false;"
)

# Late-game AI should ready crew before repeatedly visiting the Dock.
replace_once(
    'voyage-v014.js',
    "const order=tired&&ready<=1?['quarters',...normalOrder.filter(x=>x!=='quarters')]:normalOrder;",
    "const order=tired&&(unlocked(state,3)||ready<=1)?['quarters',...normalOrder.filter(x=>x!=='quarters')]:normalOrder;"
)

# With 3 dice, allow sensible push-your-luck attempts that need up to 4 power
# from dice instead of requiring the pre-dice score to be within only 2 points.
replace_once(
    'voyage-v014.js',
    "baseScore(p,e)>=testInfo(e).target-2",
    "baseScore(p,e)>=testInfo(e).target-((c.zone||4)>=3?4:2)"
)

# Final F3 can be paid with either 6 Gold or one Treasure.
replace_once(
    'voyage-v014.js',
    "(id!=='F3'||p.gold>=6)",
    "(id!=='F3'||p.gold>=6||p.treasures.length)"
)

# Final F4/F5 requirements must be checked against the Ready Crew actually
# selected for the expedition, not exhausted crew sitting in the roster.
replace_once(
    'voyage-v014.js',
    "(id!=='F4'||p.crew.length===4&&p.crew.filter(x=>CARDS[x.id].tier==='Veteran').length>=2&&p.treasures.length>=2)",
    "(id!=='F4'||crew.length===4&&p.crew.filter(x=>crew.includes(x.uid)&&CARDS[x.id].tier==='Veteran').length>=2&&p.treasures.length>=2)"
)
replace_once(
    'voyage-v014.js',
    "(id!=='F5'||new Set(p.crew.map(c=>c.id)).size>=3&&p.crew.some(x=>CARDS[x.id].tier==='Veteran'))",
    "(id!=='F5'||new Set(p.crew.filter(x=>crew.includes(x.uid)).map(c=>c.id)).size>=3&&p.crew.some(x=>crew.includes(x.uid)&&CARDS[x.id].tier==='Veteran'))"
)

# If F3 is affordable only through Treasure, have the AI submit the required
# payment fields instead of defaulting to the 6-Gold path and failing act().
replace_once(
    'voyage-v014.js',
    "if(id)a={type:'launch',mission:id,crew}",
    "if(id){a={type:'launch',mission:id,crew};if(id==='F3'&&p.gold<6&&p.treasures.length){a.payment='treasure';a.sacrifice=p.treasures[0]}}"
)

Path('tests/ai-zone3-final-v0301.mjs').write_text(r'''import assert from 'node:assert/strict';
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
''',encoding='utf-8')

print('Applied AI Zone III / Final v0.30.1 bugfix patch')
