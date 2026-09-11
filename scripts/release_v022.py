from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected 1 match, found {count}")
    return text.replace(old, new, 1)


# ---------------------------------------------------------------------------
# Engine: D8 faces + player-specific zone progression.
# ---------------------------------------------------------------------------
p = Path('engine-v014.mjs')
s = p.read_text()
s = replace_once(
    s,
    "export const FACES=['SKULL',0,0,1,2,'GOLD'];",
    "export const FACES=['SKULL',0,0,1,1,2,2,'GOLD'];",
    'D8 face distribution',
)
old_available = "export function available(s,id){const c=CARDS[id];return !!c&&(c.kind==='final'?unlocked(s,4)&&s.final[0]===id:c.zone&&unlocked(s,c.zone)&&s.stacks[c.zone].some(st=>st[0]===id))}"
new_available = """export function playerCompletedMissions(s,playerIndex=s.turn){const p=s.players[playerIndex];if(!p)return [];return s.missionDiscard.filter(m=>m.result==='success'&&(m.playerIndex===playerIndex||(m.playerIndex==null&&m.player===p.name))).map(m=>m.id)}
export function zoneHasMission(s,z){return z===4?!!s.final?.length:(s.stacks?.[z]||[]).some(st=>st?.length)}
export function playerZoneEligible(s,z,playerIndex=s.turn){if(z<=1)return true;const prev=z-1;if(!zoneHasMission(s,prev))return true;return playerCompletedMissions(s,playerIndex).some(id=>CARDS[id]?.zone===prev)}
export function available(s,id){const c=CARDS[id];if(!c)return false;const z=c.kind==='final'?4:c.zone;if(!z||!unlocked(s,z)||!playerZoneEligible(s,z))return false;return c.kind==='final'?s.final[0]===id:s.stacks[c.zone].some(st=>st[0]===id)}"""
s = replace_once(s, old_available, new_available, 'player zone eligibility')
s = replace_once(
    s,
    "s.missionDiscard.unshift({id:c.id,player:p.name,result:'success'});",
    "s.missionDiscard.unshift({id:c.id,player:p.name,playerIndex:s.turn,result:'success'});",
    'successful mission ownership',
)
s = replace_once(
    s,
    "s.missionDiscard.unshift({id:c.id,player:p.name,result:'failed'})",
    "s.missionDiscard.unshift({id:c.id,player:p.name,playerIndex:s.turn,result:'failed'})",
    'failed final mission ownership',
)
s = s.replace("FACES[Math.floor(rng()*6)]", "FACES[Math.floor(rng()*FACES.length)]")
if "Math.floor(rng()*6)" in s:
    raise SystemExit('D6 RNG marker still exists in engine')
p.write_text(s)


# ---------------------------------------------------------------------------
# Voyage UI: telescope/spyglass + helm icons, completed missions, zone gate.
# ---------------------------------------------------------------------------
p = Path('voyage-v014.js')
s = p.read_text()
s = replace_once(
    s,
    "import {DATA,CARDS,SAVE_KEY,LOCATIONS,newGame,current,unlocked,locationOpen,legalWorker,available,act,testInfo,baseScore,totalScore,supplyCost,controls,normalizeSharedPools} from './engine-v014.mjs';",
    "import {DATA,CARDS,SAVE_KEY,LOCATIONS,newGame,current,unlocked,locationOpen,legalWorker,available,act,testInfo,baseScore,totalScore,supplyCost,controls,normalizeSharedPools,playerCompletedMissions,playerZoneEligible} from './engine-v014.mjs';",
    'import zone progression helpers',
)
old_icons = "const colors=['#df4a3f','#4598ef','#46b879','#e9c65b'],icons={Combat:'⚔',Sailing:'⚓',Search:'⌕'};"
new_icons = """const colors=['#df4a3f','#4598ef','#46b879','#e9c65b'];
const testIcon=(type)=>type==='Sailing'?`<span class=\"testIcon sailingIcon\" role=\"img\" aria-label=\"Sailing\"><svg viewBox=\"0 0 48 48\" focusable=\"false\"><circle cx=\"24\" cy=\"24\" r=\"11\"/><circle cx=\"24\" cy=\"24\" r=\"3.5\"/><path d=\"M24 3v10M24 35v10M3 24h10M35 24h10M9.2 9.2l7.1 7.1M31.7 31.7l7.1 7.1M38.8 9.2l-7.1 7.1M16.3 31.7l-7.1 7.1\"/><path d=\"M21 4h6l2 6-5 3-5-3zM44 21v6l-6 2-3-5 3-5zM27 44h-6l-2-6 5-3 5 3zM4 27v-6l6-2 3 5-3 5z\"/></svg></span>`:type==='Search'?`<span class=\"testIcon searchIcon\" role=\"img\" aria-label=\"Search\"><svg viewBox=\"0 0 56 40\" focusable=\"false\"><path d=\"M7 29L34 12l7 8-27 17z\"/><path d=\"M34 12l7-5 8 10-8 5z\"/><path d=\"M7 29l-3 5 7 4 3-5z\"/><path d=\"M19 25l7 8\"/><circle cx=\"46\" cy=\"12\" r=\"5\"/></svg></span>`:'⚔';
const icons={Combat:testIcon('Combat'),Sailing:testIcon('Sailing'),Search:testIcon('Search')};"""
s = replace_once(s, old_icons, new_icons, 'new test icons')
s = replace_once(s, 'The Final Isle · v0.21', 'The Final Isle · v0.22', 'HUD version')
s = replace_once(s, "'All 81 cards · v0.15 Final'", "'All 81 cards · v0.22'", 'card library version')

old_prep = "function prep(id){if(state.exp)return showExp();if(state.location!=='dock'){modal(CARDS[id].name,card(id)+'<p>Place or take a Pirate at Dock to launch an Expedition.</p>');return}if(!available(state,id))return toast('Zone locked.');const c=CARDS[id],p=current(state),peek=p.crew.some(c=>c.id==='C13'&&!c.exhausted)||p.treasures.includes('T01');"
new_prep = "function prep(id){if(state.exp)return showExp();if(state.location!=='dock'){modal(CARDS[id].name,card(id)+'<p>Place or take a Pirate at Dock to launch an Expedition.</p>');return}const c=CARDS[id],z=c.kind==='final'?4:c.zone;if(!unlocked(state,z))return toast('Zone locked.');if(!playerZoneEligible(state,z))return toast(`Complete a Zone ${['','I','II','III'][z-1]} Mission first — unless no Missions remain there.`);if(!available(state,id))return toast('Mission unavailable.');const p=current(state),peek=p.crew.some(c=>c.id==='C13'&&!c.exhausted)||p.treasures.includes('T01');"
s = replace_once(s, old_prep, new_prep, 'Dock prerequisite message')

s = s.replace("Array.from({length:diceCount},()=>'<div class=\"die dieWaiting\">?</div>').join('')", "Array.from({length:diceCount},()=>'<div class=\"die dieWaiting d8\" title=\"D8\"><small>D8</small><b>?</b></div>').join('')")
s = s.replace("`Roll ${diceCount} dice`", "`Roll ${diceCount} d8${diceCount===1?'':'s'}`")
s = s.replace("<div class=\"die ${d==='SKULL'?'skullDie':d==='GOLD'?'goldDie':''}\">", "<div class=\"die d8 ${d==='SKULL'?'skullDie':d==='GOLD'?'goldDie':''}\">")

old_player = "if(name==='player'){const p=state.players[+d.index];modal(p.name+' · Crew & Treasure',`<div class=\"captainIdentity\"><img src=\"assets/${portraits[state.turn]}\" alt=\"Captain portrait\"><div><h2>${esc(p.name)}</h2><p class=\"captainResources\">${resourceIcon('gold')} ${p.gold} Gold · ${resourceIcon('supply')} ${p.supply} Supply</p></div></div>`+'<h3>Crew</h3><div class=\"vGrid\">'+(p.crew.map(c=>card(c.id,crewStatusIcon(c.exhausted))).join('')||'<p>No Crew aboard.</p>')+'</div><h3>Treasure</h3><div class=\"vGrid\">'+(p.treasures.map(id=>card(id)).join('')||'<p>No Treasure yet.</p>')+'</div>');return}"
new_player = "if(name==='player'){const index=+d.index,p=state.players[index],completed=playerCompletedMissions(state,index);const completedHtml=completed.length?completed.map(id=>{const c=CARDS[id];return `<article class=\"completedMissionCard\"><div class=\"completedMissionArt\">${art(c)}</div><div><small>ZONE ${['','I','II','III'][c.zone]}</small><strong>${esc(c.name)}</strong><span>${icons[c.test]} ${esc(c.test)} · Target ${c.target}</span>${rewardBadges(c)}</div><b class=\"completedCheck\">✓</b></article>`}).join(''):'<p class=\"emptyCompleted\">No completed Missions yet.</p>';modal(p.name+' · Captain Log',`<div class=\"captainIdentity\"><img src=\"assets/${portraits[index]}\" alt=\"Captain portrait\"><div><h2>${esc(p.name)}</h2><p class=\"captainResources\">${resourceIcon('gold')} ${p.gold} Gold · ${resourceIcon('supply')} ${p.supply} Supply · ${crewGroupIcon()} ${p.crew.filter(c=>!c.exhausted).length}/${p.crew.length} Ready</p></div></div>`+'<h3>Crew</h3><div class=\"vGrid\">'+(p.crew.map(c=>card(c.id,crewStatusIcon(c.exhausted))).join('')||'<p>No Crew aboard.</p>')+'</div><h3>Treasure</h3><div class=\"vGrid\">'+(p.treasures.map(id=>card(id)).join('')||'<p>No Treasure yet.</p>')+'</div><section class=\"completedMissions\"><header><h3>Completed Missions</h3><span>'+completed.length+' cleared</span></header><div class=\"completedMissionGrid\">'+completedHtml+'</div></section>');return}"
s = replace_once(s, old_player, new_player, 'completed missions in captain detail')
p.write_text(s)


# ---------------------------------------------------------------------------
# Styling for v0.22 test icons, D8 and completed mission archive.
# ---------------------------------------------------------------------------
p = Path('voyage-table.css')
s = p.read_text()
marker = '/* v0.22 — D8, maritime test icons and captain mission archive. */'
if marker not in s:
    s += r'''

/* v0.22 — D8, maritime test icons and captain mission archive. */
.testIcon{width:1.25em;height:1.25em;display:inline-grid;place-items:center;vertical-align:-.2em;color:currentColor}.testIcon svg{width:100%;height:100%;overflow:visible}.testIcon svg *{fill:none;stroke:currentColor;stroke-width:3;stroke-linecap:round;stroke-linejoin:round}.searchIcon svg{width:1.45em}.searchIcon svg circle{fill:currentColor;stroke-width:1.5}.sailingIcon svg path:nth-of-type(2){fill:currentColor;stroke-width:1.4}.missionTestType .testGlyph .testIcon{width:32px;height:32px}.tileRibbon .testIcon{width:1.15em;height:1.15em}.vStats .testIcon{width:1.05em;height:1.05em}.expMissionCard>header .testIcon,.expMiniCard>span .testIcon{width:1.15em;height:1.15em}
.die.d8{position:relative;border-radius:8px;clip-path:polygon(25% 2%,75% 2%,98% 50%,75% 98%,25% 98%,2% 50%);min-width:76px;min-height:76px;display:grid;place-items:center}.die.d8:after{content:'';position:absolute;inset:9px;clip-path:inherit;border:1px solid #f2d68a66;pointer-events:none}.dieWaiting.d8{grid-template-rows:auto auto}.dieWaiting.d8 small{font:800 9px/1 system-ui;letter-spacing:.16em;opacity:.7;margin-top:9px}.dieWaiting.d8 b{font:700 28px/1 Georgia;margin-bottom:10px}
.completedMissions{margin-top:30px;padding-top:20px;border-top:2px solid #c9a35466}.completedMissions>header{display:flex;align-items:center;justify-content:space-between;gap:16px;margin-bottom:14px}.completedMissions>header h3{margin:0}.completedMissions>header span{font:800 12px system-ui;letter-spacing:.08em;color:#f1d286;background:#183c48;border:1px solid #bd9953;border-radius:999px;padding:7px 11px}.completedMissionGrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(245px,1fr));gap:12px}.completedMissionCard{position:relative;display:grid;grid-template-columns:108px minmax(0,1fr);gap:11px;align-items:center;min-height:126px;padding:8px 42px 8px 8px;background:linear-gradient(145deg,#f3dfac,#d5b574);color:#2d2116;border:3px double #936c34;border-radius:10px;box-shadow:0 5px 12px #0006}.completedMissionArt{height:106px;border:2px solid #89652f;border-radius:7px;overflow:hidden;background:#17313a}.completedMissionArt .art{width:100%;height:100%}.completedMissionCard>div:nth-child(2){display:flex;flex-direction:column;gap:5px;min-width:0}.completedMissionCard small{font:800 9px system-ui;letter-spacing:.1em;color:#725126}.completedMissionCard strong{font:700 17px/1.05 Georgia}.completedMissionCard span{font:12px/1.25 system-ui;display:flex;align-items:center;gap:3px}.completedMissionCard .rewardIcons{justify-content:flex-start;gap:4px;margin-top:3px}.completedMissionCard .rewardBadge{transform:scale(.82);transform-origin:left center}.completedCheck{position:absolute;right:10px;top:10px;width:26px;height:26px;border-radius:50%;display:grid;place-items:center;background:#245d3c;color:#fff0bf;border:2px solid #c9a354;font:800 16px system-ui}.emptyCompleted{grid-column:1/-1;padding:18px;border:1px dashed #c9a35466;border-radius:10px;text-align:center;color:#cfc3a8}
@media(max-width:700px){.completedMissionGrid{grid-template-columns:1fr}.completedMissionCard{grid-template-columns:92px minmax(0,1fr)}.completedMissionArt{height:92px}.die.d8{min-width:62px;min-height:62px}}
'''
p.write_text(s)


# ---------------------------------------------------------------------------
# Visible release labels.
# ---------------------------------------------------------------------------
p = Path('menu.js')
s = p.read_text()
s = replace_once(s, '      version:"0.21",', '      version:"0.22",', 'setup version')
p.write_text(s)

p = Path('index.html')
s = p.read_text()
s = s.replace('v0.21 Test', 'v0.22 Test')
s = s.replace('v0.21 TEST', 'v0.22 TEST')
if 'v0.22 Test' not in s and 'v0.22 TEST' not in s:
    raise SystemExit('index v0.22 marker missing')
p.write_text(s)


# ---------------------------------------------------------------------------
# Existing regression helper: seed prior-zone clears when testing a deeper
# Mission directly. This keeps old mission-mechanics tests valid under the
# new v0.22 personal progression gate.
# ---------------------------------------------------------------------------
p = Path('tests/rules-v014.mjs')
s = p.read_text()
old_helper = "function expedition(id='Z1-01',crew=['C02'],treasures=[]){let s=newGame();const p=current(s);p.gold=30;p.supply=30;p.crew=crew.map((id,i)=>({id,uid:'test'+i,exhausted:false}));p.treasures=treasures;s.progress=[2,2,1];if(id.startsWith('F'))s.final=[id];else s.stacks[+id[1]][0]=[id];s.workers.dock=null;s=act(s,{type:'worker',location:'dock'});return act(s,{type:'launch',mission:id,crew:p.crew.map(c=>c.uid)})}"
new_helper = "function expedition(id='Z1-01',crew=['C02'],treasures=[]){let s=newGame();const p=current(s);p.gold=30;p.supply=30;p.crew=crew.map((id,i)=>({id,uid:'test'+i,exhausted:false}));p.treasures=treasures;s.progress=[2,2,1];const zone=id.startsWith('F')?4:+id[1];for(let prev=1;prev<zone;prev++){const prior=DATA.cards.find(c=>c.zone===prev)?.id;if(prior)s.missionDiscard.unshift({id:prior,player:p.name,playerIndex:s.turn,result:'success'})}if(id.startsWith('F'))s.final=[id];else s.stacks[+id[1]][0]=[id];s.workers.dock=null;s=act(s,{type:'worker',location:'dock'});return act(s,{type:'launch',mission:id,crew:p.crew.map(c=>c.uid)})}"
s = replace_once(s, old_helper, new_helper, 'legacy expedition test fixture progression')
p.write_text(s)


# Static checks.
checks = {
    'engine-v014.mjs': ["FACES=['SKULL',0,0,1,1,2,2,'GOLD']", 'playerZoneEligible', 'playerCompletedMissions', 'FACES.length', 'playerIndex:s.turn'],
    'voyage-v014.js': ['The Final Isle · v0.22', 'sailingIcon', 'searchIcon', 'Completed Missions', 'completedMissionCard', 'playerZoneEligible', 'Roll ${diceCount} d8'],
    'voyage-table.css': ['v0.22 — D8', '.completedMissionCard', '.die.d8', '.testIcon'],
    'menu.js': ['version:"0.22"'],
    'tests/rules-v014.mjs': ['playerIndex:s.turn', 'for(let prev=1;prev<zone;prev++)'],
}
for file, markers in checks.items():
    text = Path(file).read_text()
    for marker in markers:
        if marker not in text:
            raise SystemExit(f'{file}: missing {marker}')
print('v0.22 patch markers verified')
