from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected 1 match, found {n}")
    return text.replace(old, new, 1)


# ---------------------------------------------------------------------------
# Engine: make Crew Market / Veteran Market / Treasure deck explicitly global.
# ---------------------------------------------------------------------------
p = Path('engine-v014.mjs')
s = p.read_text()
helper_anchor = "export const current=s=>s.players[s.turn];\n"
helper = """export const current=s=>s.players[s.turn];
export function normalizeSharedPools(s){
 if(!s||!Array.isArray(s.players))return s;
 const fallback=(key)=>s.players.find(p=>Array.isArray(p?.[key]))?.[key];
 if(!Array.isArray(s.market))s.market=[...(fallback('market')||[])];
 if(!Array.isArray(s.veteranMarket))s.veteranMarket=[...(fallback('veteranMarket')||[])];
 if(!Array.isArray(s.treasureDeck))s.treasureDeck=[...(fallback('treasureDeck')||[])];
 for(const p of s.players){delete p.market;delete p.veteranMarket;delete p.treasureDeck;delete p.crewDeck;delete p.veteranDeck}
 return s;
}
"""
s = replace_once(s, helper_anchor, helper, 'shared-pool normalizer')
s = replace_once(
    s,
    " s.market=s.crewDeck.splice(0,3);s.veteranMarket=s.veteranDeck.splice(0,3);s.treasureDeck=shuffle(DATA.cards.filter(c=>c.kind==='treasure').map(c=>c.id),rng);",
    " s.market=s.crewDeck.splice(0,3);s.veteranMarket=s.veteranDeck.splice(0,3);s.treasureDeck=shuffle(DATA.cards.filter(c=>c.kind==='treasure').map(c=>c.id),rng);normalizeSharedPools(s);",
    'new-game shared pools',
)
s = replace_once(
    s,
    "export function act(original,a,rng=Math.random){const s=structuredClone(original),p=current(s),e=s.exp;",
    "export function act(original,a,rng=Math.random){const s=normalizeSharedPools(structuredClone(original)),p=current(s),e=s.exp;",
    'act shared pools',
)
p.write_text(s)


# ---------------------------------------------------------------------------
# UI: shared market, improved Mission stats, Crew icon, icon-based rewards.
# ---------------------------------------------------------------------------
p = Path('voyage-v014.js')
s = p.read_text()
s = replace_once(
    s,
    "import {DATA,CARDS,SAVE_KEY,LOCATIONS,newGame,current,unlocked,locationOpen,legalWorker,available,act,testInfo,baseScore,totalScore,supplyCost,controls} from './engine-v014.mjs';",
    "import {DATA,CARDS,SAVE_KEY,LOCATIONS,newGame,current,unlocked,locationOpen,legalWorker,available,act,testInfo,baseScore,totalScore,supplyCost,controls,normalizeSharedPools} from './engine-v014.mjs';",
    'import normalizeSharedPools',
)

helper_anchor = "const canUndoWorker=()=>!!undoWorkerState&&!isAITurn()&&state?.status==='playing'&&!!state.location&&!state.exp;\n"
helpers = r'''const canUndoWorker=()=>!!undoWorkerState&&!isAITurn()&&state?.status==='playing'&&!!state.location&&!state.exp;
const crewGroupIcon=(veteran=false)=>`<span class="crewGroupIcon ${veteran?'veteran':''}" aria-hidden="true"><svg viewBox="0 0 48 34" focusable="false"><ellipse class="crewOval" cx="24" cy="18" rx="22" ry="15"/><circle cx="24" cy="10" r="5"/><circle cx="13" cy="13" r="4"/><circle cx="35" cy="13" r="4"/><path d="M14 27c.8-7 4.2-10.5 10-10.5S33.2 20 34 27z"/><path d="M5.5 25c.5-5.3 3.1-8 7.4-8 3 0 5.2 1.4 6.4 4-1.3 1.4-2.1 3.4-2.5 6H5.5zM42.5 25c-.5-5.3-3.1-8-7.4-8-3 0-5.2 1.4-6.4 4 1.3 1.4 2.1 3.4 2.5 6h11.3z"/>${veteran?'<path class="crewStar" d="M24 2.5l1.5 3 3.3.5-2.4 2.3.6 3.3-3-1.6-3 1.6.6-3.3L19.2 6l3.3-.5z"/>':''}</svg></span>`;
function rewardBadges(c){
 const r=c.reward||{},items=[];
 if(r.gold)items.push(['gold',r.gold,'Gold']);
 if(r.supply)items.push(['supply',r.supply,'Supply']);
 if(r.treasure)items.push(['treasure',r.treasure,'Treasure']);
 if(r.crew)items.push(['crew',r.crew,'Crew']);
 if(r.veteran)items.push(['veteran',r.veteran,'Veteran Crew']);
 if(r.drawTreasure)items.push(['drawTreasure',r.drawTreasure,'Draw Treasure']);
 return `<div class="rewardIcons" aria-label="Mission rewards">${items.map(([type,n,label])=>`<span class="rewardBadge ${type}" title="${label} ×${n}">${type==='crew'?crewGroupIcon(false):type==='veteran'?crewGroupIcon(true):resourceIcon(type==='drawTreasure'?'treasure':type)}<b>×${n}</b>${type==='drawTreasure'?'<small>KEEP 1</small>':''}</span>`).join('')}</div>`;
}
function missionTestBox(c){return `<div class="missionTestBox"><span class="missionTestType"><i class="testGlyph">${icons[c.test]}</i><span><small>TEST</small><strong>${esc(c.test)}</strong></span></span><span class="missionTarget"><small>TARGET</small><strong>${c.target}</strong></span></div>`}
'''
s = replace_once(s, helper_anchor, helpers, 'v0.20 UI helpers')

start = s.index('function details(c){')
end = s.index('function card(id,extra=', start)
new_details = r'''function details(c){if(c.kind==='crew')return `<div class="vStats">${Object.entries(c.stats).map(([t,v])=>`<span>${icons[t]} ${t}<b>${v}</b></span>`).join('')}</div><p class="resourceLine">${esc(c.tier)} · ${resourceIcon('gold')} <b>${c.cost}</b> Gold</p><p>${lines(c.text)}</p>`;if(c.kind==='treasure')return `<b>${esc(c.type)} · Passive</b><p>${lines(c.text)}</p>`;if(c.kind==='final')return c.steps.map((s,i)=>`<section class="testPanel"><b>Step ${i+1} · ${esc(s.name)}</b><p>${lines(s.text)}</p></section>`).join('')+`<p class="resourceLine">${resourceIcon('supply')} <b>9</b> Supply · 3 dice per test · Win both tests to win the game.</p>`;return `${missionTestBox(c)}<p class="resourceLine missionSupplyLine">${resourceIcon('supply')} <b>${[1,3,6][c.zone-1]}</b> Supply · ${c.zone} dice</p><div class="reward rewardVisual"><b>Success</b>${rewardBadges(c)}</div>`}
'''
s = s[:start] + new_details + s[end:]

# Crew-count icon in player strip.
s = replace_once(
    s,
    "<span>♟ <b>${p.crew.length}/4</b></span>",
    "<span class=\"crewCount\">${crewGroupIcon()}<b>${p.crew.length}/4</b></span>",
    'crew count icon',
)

# Explicitly label all central pools as shared.
s = replace_once(
    s,
    '<div class="shelfLabel"><b>Crew Market</b><small>3 face-up · Tavern</small></div>',
    '<div class="shelfLabel"><b>Crew Market <em class="sharedBadge">SHARED</em></b><small>3 face-up · Tavern</small></div>',
    'shared crew market badge',
)
s = replace_once(
    s,
    '<strong>Veteran</strong><small>${locationOpen(state,\'veteran\')?(state.veteranDeck.length+state.veteranMarket.length)+\' cards · Open\':\'Locked at start · Clear 2 Zone II\'}</small>',
    '<strong>Veteran <em class="sharedBadge">SHARED</em></strong><small>${locationOpen(state,\'veteran\')?(state.veteranDeck.length+state.veteranMarket.length)+\' cards · Open\':\'Locked at start · Clear 2 Zone II\'}</small>',
    'shared veteran badge',
)
s = replace_once(
    s,
    '<strong>Treasure</strong><small>${state.treasureDeck.length} cards</small>',
    '<strong>Treasure <em class="sharedBadge">SHARED</em></strong><small>${state.treasureDeck.length} cards</small>',
    'shared treasure badge',
)

# Normalize resumed saves before any player-specific view can render.
s = replace_once(
    s,
    "state=saved?.version==='0.15'?saved:newGame(ev.detail);undoWorkerState=null;",
    "state=normalizeSharedPools(saved?.version==='0.15'?saved:newGame(ev.detail));undoWorkerState=null;",
    'normalize resumed shared pools',
)

s = s.replace('The Final Isle · v0.19', 'The Final Isle · v0.20')
p.write_text(s)


# ---------------------------------------------------------------------------
# CSS polish.
# ---------------------------------------------------------------------------
p = Path('voyage-table.css')
s = p.read_text()
marker = '/* v0.20 — shared central pools, refined mission stats, crew-group icon, visual rewards. */'
if marker not in s:
    s += r'''

/* v0.20 — shared central pools, refined mission stats, crew-group icon, visual rewards. */
.sharedBadge{display:inline-block!important;margin:0 0 0 4px!important;padding:1px 5px!important;border:1px solid #c9a25288;border-radius:999px;background:#0c3544;color:#f6d68a;font:700 7px/1.35 system-ui,sans-serif!important;letter-spacing:.08em;vertical-align:middle;font-style:normal}
.shelfLabel .sharedBadge{font-size:7px!important}.deckSlot strong .sharedBadge{font-size:6px!important}
.crewGroupIcon{width:25px;height:20px;display:inline-grid;place-items:center;color:#d8ad62;flex:0 0 auto;filter:drop-shadow(0 1px 1px #0007)}
.crewGroupIcon svg{display:block;width:100%;height:100%;overflow:visible}.crewGroupIcon .crewOval{fill:#6a4527;stroke:#d2a85d;stroke-width:1.5}.crewGroupIcon svg circle,.crewGroupIcon svg path:not(.crewStar){fill:#f0d495}.crewGroupIcon .crewStar{fill:#fff0a4;stroke:#5f3d20;stroke-width:.7}
.playerNumbers .crewCount{display:inline-flex;align-items:center;gap:3px}.playerNumbers .crewCount .crewGroupIcon{width:27px;height:20px}
.missionTestBox{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(92px,.65fr);min-height:76px;margin:0 0 8px;border:2px solid #a88749;border-radius:7px;overflow:hidden;background:linear-gradient(180deg,#f5e5b8,#ead39c);box-shadow:inset 0 1px #fff8dd,inset 0 -2px #9c7b3f22}
.missionTestType,.missionTarget{display:flex;align-items:center;justify-content:center;gap:10px;padding:9px 12px;text-align:center}.missionTestType{border-right:1px solid #a88749}.missionTestType .testGlyph{width:38px;height:38px;border-radius:50%;display:grid;place-items:center;background:#173f4e;color:#f7df9f;border:2px solid #b28a49;box-shadow:inset 0 0 0 2px #0b2934;font:700 24px Georgia;font-style:normal}.missionTestType span,.missionTarget{flex-direction:column}.missionTestBox small{display:block;color:#72562f;font:700 9px/1 system-ui;letter-spacing:.13em;margin-bottom:4px}.missionTestBox .missionTestType strong{display:block;color:#2d2117;font:700 21px/1.05 Georgia}.missionTarget strong{display:block;color:#231911;font:700 38px/1 Georgia}.missionSupplyLine{margin:6px 0 9px!important;display:flex!important;align-items:center;justify-content:center;gap:4px;font-size:16px!important}
.rewardVisual{padding:0!important;border:1px solid #9a814e!important;background:#ead39c!important;overflow:hidden}.rewardVisual>b{display:block!important;margin:0!important;padding:5px 8px!important;background:#24523d!important;color:#f6e3aa!important;text-align:center!important;font:700 18px/1.1 Georgia!important}.rewardIcons{min-height:74px;padding:10px 8px;display:flex;align-items:center;justify-content:center;gap:9px;flex-wrap:wrap;background:linear-gradient(180deg,#f1ddb0,#e6cc92)}
.rewardBadge{position:relative;min-width:62px;min-height:52px;padding:5px 8px;display:inline-flex;align-items:center;justify-content:center;gap:5px;border:1px solid #b08a49;border-radius:9px;background:#fff2c9;box-shadow:0 2px 4px #5a3c1f33,inset 0 1px #fff;color:#392719}.rewardBadge .resourceIcon{width:34px!important;height:34px!important}.rewardBadge .crewGroupIcon{width:40px;height:31px}.rewardBadge b{font:700 21px/1 Georgia;color:#302115}.rewardBadge small{position:absolute;bottom:-7px;left:50%;transform:translateX(-50%);white-space:nowrap;padding:1px 4px;border-radius:4px;background:#173d49;color:#f4dfa7;font:700 7px system-ui;letter-spacing:.08em}
@media(max-width:850px){.missionTestBox{grid-template-columns:1.2fr .8fr;min-height:68px}.missionTestType .testGlyph{width:32px;height:32px;font-size:20px}.missionTestBox .missionTestType strong{font-size:18px}.missionTarget strong{font-size:32px}.rewardIcons{min-height:62px}.rewardBadge{min-width:52px;min-height:46px}.rewardBadge .resourceIcon{width:29px!important;height:29px!important}}
'''
p.write_text(s)


# ---------------------------------------------------------------------------
# Visible version labels.
# ---------------------------------------------------------------------------
p = Path('index.html')
s = p.read_text()
s = s.replace("v0.19 Test", "v0.20 Test").replace("v0.19 TEST", "v0.20 TEST")
p.write_text(s)

p = Path('menu.js')
s = p.read_text()
s = s.replace('version:"0.19"', 'version:"0.20"', 1)
p.write_text(s)


# ---------------------------------------------------------------------------
# Release checks.
# ---------------------------------------------------------------------------
checks = {
    'engine-v014.mjs': ['normalizeSharedPools', "delete p.market", 'normalizeSharedPools(structuredClone(original))'],
    'voyage-v014.js': ['The Final Isle · v0.20', 'rewardBadges', 'missionTestBox', 'crewGroupIcon', 'sharedBadge', 'normalizeSharedPools(saved'],
    'voyage-table.css': ['v0.20 — shared central pools', '.missionTestBox', '.rewardIcons', '.crewGroupIcon'],
    'index.html': ['v0.20 Test', 'v0.20 TEST'],
    'menu.js': ['version:"0.20"'],
}
for file, markers in checks.items():
    text = Path(file).read_text()
    for m in markers:
        if m not in text:
            raise SystemExit(f'{file}: missing v0.20 marker {m}')

print('v0.20 patch verified: shared pools + mission card visual polish')
