from pathlib import Path


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected 1 match, found {count}")
    return text.replace(old, new, 1)


# ---------------------------------------------------------------------------
# menu.js — release label only; retain v0.17 multi-AI behavior.
# ---------------------------------------------------------------------------
p = Path('menu.js')
s = p.read_text()
s = replace_once(s, '      version:"0.17",', '      version:"0.18",', 'menu setup version')
p.write_text(s)


# ---------------------------------------------------------------------------
# voyage-v014.js — resource art, location cards, zone costs, token-only undo,
# and graphical Supply purchase buttons.
# ---------------------------------------------------------------------------
p = Path('voyage-v014.js')
s = p.read_text()

s = replace_once(
    s,
    "let state=null,zoom=false,aiTimer=null,guidePage=1;",
    "let state=null,zoom=false,aiTimer=null,guidePage=1,undoWorkerState=null;",
    'undo state variable',
)

s = replace_once(
    s,
    "const lines=t=>esc(t).replaceAll('\\n','<br>');",
    "const lines=t=>esc(t).replaceAll('\\n','<br>');\nconst resourceIcon=(type,label='')=>`<span class=\"resourceIcon ${type}\" aria-hidden=\"true\"></span>${label?`<span class=\"resourceLabel\">${esc(label)}</span>`:''}`;\nconst canUndoWorker=()=>!!undoWorkerState&&!isAITurn()&&state?.status==='playing'&&!!state.location&&!state.exp;",
    'resource helper and undo predicate',
)

old_details = "function details(c){if(c.kind==='crew')return `<div class=\"vStats\">${Object.entries(c.stats).map(([t,v])=>`<span>${icons[t]} ${t}<b>${v}</b></span>`).join('')}</div><p>${esc(c.tier)} · ${c.cost} Gold</p><p>${lines(c.text)}</p>`;if(c.kind==='treasure')return `<b>${esc(c.type)} · Passive</b><p>${lines(c.text)}</p>`;if(c.kind==='final')return c.steps.map((s,i)=>`<section class=\"testPanel\"><b>Step ${i+1} · ${esc(s.name)}</b><p>${lines(s.text)}</p></section>`).join('')+'<p>9 Supply · 3 dice per test · Win both tests to win the game.</p>';return `<div class=\"vStats\"><span>${icons[c.test]} ${c.test}</span><span>Target <b>${c.target}</b></span></div><p>${[1,3,6][c.zone-1]} Supply · ${c.zone} dice</p><div class=\"reward\"><b>Success</b><p>${lines(c.text)}</p></div>`}"
new_details = "function details(c){if(c.kind==='crew')return `<div class=\"vStats\">${Object.entries(c.stats).map(([t,v])=>`<span>${icons[t]} ${t}<b>${v}</b></span>`).join('')}</div><p class=\"resourceLine\">${esc(c.tier)} · ${resourceIcon('gold')} <b>${c.cost}</b> Gold</p><p>${lines(c.text)}</p>`;if(c.kind==='treasure')return `<b>${esc(c.type)} · Passive</b><p>${lines(c.text)}</p>`;if(c.kind==='final')return c.steps.map((s,i)=>`<section class=\"testPanel\"><b>Step ${i+1} · ${esc(s.name)}</b><p>${lines(s.text)}</p></section>`).join('')+`<p class=\"resourceLine\">${resourceIcon('supply')} <b>9</b> Supply · 3 dice per test · Win both tests to win the game.</p>`;return `<div class=\"vStats\"><span>${icons[c.test]} ${c.test}</span><span>Target <b>${c.target}</b></span></div><p class=\"resourceLine\">${resourceIcon('supply')} <b>${[1,3,6][c.zone-1]}</b> Supply · ${c.zone} dice</p><div class=\"reward\"><b>Success</b><p>${lines(c.text)}</p></div>`}"
s = replace_once(s, old_details, new_details, 'card resource icons')

s = replace_once(
    s,
    "function card(id,extra=''){const c=CARDS[id],type=c.kind==='crew'?c.tier:c.kind==='treasure'?'Treasure':c.kind==='final'?'Final Isle':'Zone '+['','I','II','III'][c.zone];return `<article class=\"vCard physicalCard ${c.kind}\" aria-label=\"${esc(c.name)} card\"><div class=\"cardRibbon\">${esc(type)} ${c.kind==='crew'?`<span>🪙 ${c.cost}</span>`:''}</div>",
    "function card(id,extra=''){const c=CARDS[id],type=c.kind==='crew'?c.tier:c.kind==='treasure'?'Treasure':c.kind==='final'?'Final Isle':'Zone '+['','I','II','III'][c.zone];return `<article class=\"vCard physicalCard ${c.kind}\" aria-label=\"${esc(c.name)} card\"><div class=\"cardRibbon\">${esc(type)} ${c.kind==='crew'?`<span class=\"resourceLine\">${resourceIcon('gold')} ${c.cost}</span>`:''}</div>",
    'crew ribbon gold icon',
)

old_doact = "function doAct(a){if(busy)return false;try{const previous=state;state=act(state,a);if(previous.turn!==state.turn&&!isAITurn())handoff=true;if(state.exp){const c=CARDS[state.exp.mission];state.exp.boardSlot=previous.exp?.mission===state.exp.mission?previous.exp.boardSlot:Math.max(0,(previous.stacks[c.zone]||[]).findIndex(st=>st[0]===c.id))}save();render();"
new_doact = "function doAct(a){if(busy)return false;const undoCandidate=a.type==='worker'&&!isAITurn()?structuredClone(state):null;try{const previous=state;state=act(state,a);if(undoCandidate)undoWorkerState=undoCandidate;else if(a.type!=='worker')undoWorkerState=null;if(previous.turn!==state.turn&&!isAITurn())handoff=true;if(state.exp){const c=CARDS[state.exp.mission];state.exp.boardSlot=previous.exp?.mission===state.exp.mission?previous.exp.boardSlot:Math.max(0,(previous.stacks[c.zone]||[]).findIndex(st=>st[0]===c.id))}save();render();"
s = replace_once(s, old_doact, new_doact, 'token-only undo snapshot')

old_dock = "function playerDock(){return '<section class=\"playerDock\" aria-label=\"All captains\">'+state.players.map((p,i)=>`<button class=\"playerPanel ${i===state.turn?'active':''}\" data-action=\"player\" data-index=\"${i}\" style=\"--captain:${colors[i]}\" aria-label=\"${i===state.turn?'View your captain':'Private captain'} ${esc(p.name)}\" ${i!==state.turn||isAITurn()||handoff?'disabled':''}><img class=\"captainPortrait\" src=\"assets/${portraits[i]}\" alt=\"Captain portrait\"><div><strong>${esc(p.name)} <small>${i===state.turn?(state.mode==='ai'&&i>0?'AI TURN':'YOUR TURN'):'PRIVATE'}</small></strong><div class=\"playerNumbers\"><span>🪙 <b>${p.gold}</b></span><span>▣ <b>${p.supply}</b></span><span>♟ <b>${p.crew.length}/4</b></span><span>◆ <b>${p.treasures.length}/3</b></span></div></div></button>`).join('')+'</section>'}"
new_dock = "function playerDock(){return '<section class=\"playerDock\" aria-label=\"All captains\">'+state.players.map((p,i)=>`<button class=\"playerPanel ${i===state.turn?'active':''}\" data-action=\"player\" data-index=\"${i}\" style=\"--captain:${colors[i]}\" aria-label=\"${i===state.turn?'View your captain':'Private captain'} ${esc(p.name)}\" ${i!==state.turn||isAITurn()||handoff?'disabled':''}><img class=\"captainPortrait\" src=\"assets/${portraits[i]}\" alt=\"Captain portrait\"><div><strong>${esc(p.name)} <small>${i===state.turn?(state.mode==='ai'&&i>0?'AI TURN':'YOUR TURN'):'PRIVATE'}</small></strong><div class=\"playerNumbers\"><span>${resourceIcon('gold')}<b>${p.gold}</b></span><span>${resourceIcon('supply')}<b>${p.supply}</b></span><span>♟ <b>${p.crew.length}/4</b></span><span>${resourceIcon('treasure')}<b>${p.treasures.length}/3</b></span></div></div></button>`).join('')+'</section>'}"
s = replace_once(s, old_dock, new_dock, 'player resource icons')

old_zones = " const zones=[1,2,3,4].map(z=>{const stacks=z===4?[state.final]:state.stacks[z],open=unlocked(state,z);return `<section class=\"seaZone zone${z} ${open?'':'zoneLocked'}\"><header><h2>${['','I · Coastal Waters','II · Open Sea','III · Deadly Waters','Final Isle'][z]}</h2><span>${open?`${[1,3,6,9][z-1]} Supply · ${Math.min(z,3)} dice`:'🔒 '+['','','Complete 2 Zone I','Complete 2 Zone II','Complete 1 Zone III'][z]}</span></header><div class=\"zoneCards\">"
new_zones = " const zones=[1,2,3,4].map(z=>{const stacks=z===4?[state.final]:state.stacks[z],open=unlocked(state,z),cost=[1,3,6,9][z-1],gate=['','','Complete 2 Zone I','Complete 2 Zone II','Complete 1 Zone III'][z];return `<section class=\"seaZone zone${z} ${open?'':'zoneLocked'}\"><header><h2>${['','I · Coastal Waters','II · Open Sea','III · Deadly Waters','Final Isle'][z]}</h2><span class=\"zoneSupplyBadge\">${resourceIcon('supply')}<b>${cost} Supply</b><small>to sail here</small></span>${open?'':`<span class=\"zoneGate\">🔒 ${gate}</span>`}</header><div class=\"zoneCards\">"
s = replace_once(s, old_zones, new_zones, 'zone supply badges')

s = replace_once(
    s,
    " const symbols={tavern:'🍺',market:'🪙',dock:'⚓',work:'⚒',quarters:'♟',black:'◆',veteran:'⚔',witch:'✦'};",
    " const symbols={tavern:'🍺',market:'●',dock:'⚓',work:'⚒',quarters:'♟',black:'◆',veteran:'⚔',witch:'✦'};\n const locationHelp={tavern:'Recruit 1 face-up Crew · pay its Gold cost',market:'Buy up to 5 Supply · 1 Gold each',dock:'Launch an Expedition',work:'Gain 3 Gold',quarters:'Ready up to 4 exhausted Crew',black:'Refresh up to 3 Crew · recruit for 1 Gold less',veteran:'Recruit 1 Veteran Crew',witch:'Pay 3 Gold · choose a blessing'};\n const locationGate={black:'Unlock: complete 1 Zone II mission',veteran:'Unlock: complete 2 Zone II missions',witch:'Unlock: reach the Final Isle'};\n const illustratedLocations=new Set(['tavern','market','dock','work','quarters']);",
    'location card metadata',
)

old_hud = "${button('crew','My Captain',isAITurn()||handoff?'disabled':'')}${button('help','Guide')}${button('tools','☰','aria-label=\"Game options\"')}</header>"
new_hud = "${button('crew','My Captain',isAITurn()||handoff?'disabled':'')}${canUndoWorker()?button('undoWorker','↶ Undo Token','class=\"undoWorkerBtn\"'):''}${button('help','Guide')}${button('tools','☰','aria-label=\"Game options\"')}</header>"
s = replace_once(s, old_hud, new_hud, 'HUD undo button')
s = replace_once(s, 'The Final Isle · v0.17', 'The Final Isle · v0.18', 'HUD version')

old_haven = "<div class=\"havenSpaces\">${Object.keys(LOCATIONS).map(id=>`<button data-worker=\"${id}\" class=\"havenSpace ${legalWorker(state,id)?'legal '+state.phase:''}${isAITurn()&&state.location===id?' aiChosen':''}\" ${legalWorker(state,id)?'':'disabled'} aria-label=\"${LOCATIONS[id]} ${state.workers[id]===null?'empty':'shared Pirate'}\"><span class=\"locationSymbol\">${symbols[id]}</span><strong>${LOCATIONS[id]}</strong>${state.workers[id]!==null?hat():''}${!locationOpen(state,id)?'<span class=\"locationLock\">🔒</span>':''}</button>`).join('')}</div>"
new_haven = "<div class=\"havenSpaces\">${Object.keys(LOCATIONS).map(id=>`<button data-worker=\"${id}\" class=\"havenSpace locationCard ${legalWorker(state,id)?'legal '+state.phase:''}${isAITurn()&&state.location===id?' aiChosen':''}\" ${legalWorker(state,id)?'':'disabled'} aria-label=\"${LOCATIONS[id]}: ${locationHelp[id]}\"><span class=\"locationArt loc-${id} ${illustratedLocations.has(id)?'illustrated':'unlockableArt'}\">${illustratedLocations.has(id)?'':`<span>${symbols[id]}</span>`}</span><span class=\"locationCopy\"><strong>${LOCATIONS[id]}</strong><small>${locationHelp[id]}</small></span>${state.workers[id]!==null?hat():''}${!locationOpen(state,id)?`<span class=\"locationLock\"><b>🔒</b><small>${locationGate[id]}</small></span>`:''}</button>`).join('')}</div>"
s = replace_once(s, old_haven, new_haven, 'illustrated location cards')

s = replace_once(
    s,
    "<button class=\"marketTile\" data-action=\"inspect\" data-id=\"${id}\" aria-label=\"Inspect ${esc(CARDS[id].name)}\">${art(CARDS[id])}<strong>${esc(CARDS[id].name)}</strong><span>🪙 ${CARDS[id].cost}</span></button>",
    "<button class=\"marketTile\" data-action=\"inspect\" data-id=\"${id}\" aria-label=\"Inspect ${esc(CARDS[id].name)}\">${art(CARDS[id])}<strong>${esc(CARDS[id].name)}</strong><span class=\"resourceLine\">${resourceIcon('gold')} ${CARDS[id].cost}</span></button>",
    'Crew Market gold icon',
)

s = replace_once(
    s,
    "<div class=\"deckSlot treasureSlot\" aria-label=\"Treasure deck\"><span class=\"deckIcon\">◆</span><strong>Treasure</strong><small>${state.treasureDeck.length} cards</small></div>",
    "<div class=\"deckSlot treasureSlot\" aria-label=\"Treasure deck\"><span class=\"deckIcon resourceDeckIcon\">${resourceIcon('treasure')}</span><strong>Treasure</strong><small>${state.treasureDeck.length} cards</small></div>",
    'Treasure deck icon',
)

old_market = " if(l==='market')html=`<p>Buy up to 5 Supply at 1 Gold each. You have ${p.gold} Gold.</p><input type=\"number\" id=\"amount\" min=\"1\" max=\"5\" value=\"1\" aria-label=\"Supply amount\">${button('market','Buy Supply')}`;"
new_market = " if(l==='market')html=`<div class=\"marketPurchaseIntro\">${resourceIcon('supply')}<p>Choose how many Supplies to buy. Each Supply costs ${resourceIcon('gold')} 1 Gold. You have <b>${p.gold}</b> Gold.</p></div><div class=\"supplyBuyGrid\">${[1,2,3,4,5].map(n=>button('market',`${resourceIcon('supply')}<strong>+${n} Supply</strong><small>${resourceIcon('gold')} ${n} Gold</small>`,`class=\"supplyBuyBtn\" data-amount=\"${n}\" ${p.gold<n?'disabled':''}`)).join('')}</div>`;"
s = replace_once(s, old_market, new_market, 'graphical supply purchase')

s = replace_once(
    s,
    " modal(LOCATIONS[l],'<p class=\"pirateBanter\">“'+banter[l]+'”</p>'+html+'<div class=\"vToolbar\">'+skip+'</div>');",
    " modal(LOCATIONS[l],'<p class=\"pirateBanter\">“'+banter[l]+'”</p>'+html+'<div class=\"vToolbar\">'+(canUndoWorker()?button('undoWorker','↶ Undo Token','class=\"undoWorkerBtn\"'):'')+skip+'</div>');",
    'modal undo button',
)

s = replace_once(
    s,
    "function action(name,d={}){if(busy)return;",
    "function action(name,d={}){if(busy)return;if(name==='undoWorker'){if(!canUndoWorker())return toast('Undo is available only before resolving the location action.');state=structuredClone(undoWorkerState);undoWorkerState=null;busy=false;save();if(dlg.open)dlg.close();render();showPending();return}",
    'undo action handler',
)

s = replace_once(
    s,
    "if(name==='market')a.amount=+body.querySelector('#amount').value;",
    "if(name==='market')a.amount=Math.max(1,Math.min(5,+d.amount||1));",
    'market button amount',
)

s = replace_once(
    s,
    "d==='GOLD'?'🪙':d",
    "d==='GOLD'?resourceIcon('gold'):d",
    'gold die face',
)

s = replace_once(
    s,
    "<p>🪙 ${p.gold} Gold · ▣ ${p.supply} Supply</p>",
    "<p class=\"captainResources\">${resourceIcon('gold')} ${p.gold} Gold · ${resourceIcon('supply')} ${p.supply} Supply</p>",
    'captain modal resource icons',
)

s = replace_once(
    s,
    "state=saved?.version==='0.15'?saved:newGame(ev.detail);handoff=",
    "state=saved?.version==='0.15'?saved:newGame(ev.detail);undoWorkerState=null;handoff=",
    'reset undo on game start',
)

p.write_text(s)


# ---------------------------------------------------------------------------
# voyage-flair.js — final screen resource art.
# ---------------------------------------------------------------------------
p = Path('voyage-flair.js')
s = p.read_text()
s = replace_once(
    s,
    '<div class="victoryStats">${p.gold} Gold · ${p.supply} Supply · ${p.crew.length} Crew · ${p.treasures.length} Treasures</div>',
    '<div class="victoryStats"><span><i class="resourceIcon gold"></i>${p.gold} Gold</span><span><i class="resourceIcon supply"></i>${p.supply} Supply</span><span>♟ ${p.crew.length} Crew</span><span><i class="resourceIcon treasure"></i>${p.treasures.length} Treasures</span></div>',
    'finale resource icons',
)
p.write_text(s)


# ---------------------------------------------------------------------------
# voyage-table.css — visual treatment from the supplied references.
# ---------------------------------------------------------------------------
p = Path('voyage-table.css')
s = p.read_text()
marker = '/* v0.18 — illustrated actions, resource art, zone supply cards, token undo, graphical market. */'
if marker in s:
    raise SystemExit('v0.18 CSS already present')
s += r'''

/* v0.18 — illustrated actions, resource art, zone supply cards, token undo, graphical market. */
.resourceIcon{display:inline-block;width:1.45em;height:1.45em;vertical-align:-.36em;flex:0 0 auto;background-image:url('assets/resources-v018.jpg');background-size:300% 100%;background-repeat:no-repeat;border-radius:18%;box-shadow:0 1px 2px #0006}
.resourceIcon.gold{background-position:0 0}.resourceIcon.supply{background-position:50% 0}.resourceIcon.treasure{background-position:100% 0}.resourceLine{display:inline-flex!important;align-items:center;justify-content:center;gap:5px}.resourceLine .resourceIcon{width:24px;height:24px;vertical-align:middle}.resourceDeckIcon .resourceIcon{width:42px;height:42px}.captainResources .resourceIcon{width:30px;height:30px}.victoryStats{display:flex!important;gap:14px;justify-content:center;flex-wrap:wrap}.victoryStats span{display:inline-flex;align-items:center;gap:5px}.victoryStats .resourceIcon{width:28px;height:28px}

/* Pirate Haven cards: artwork takes the upper portion, rules reminder stays visible below. */
#voyage .havenSpace.locationCard{padding:0!important;overflow:hidden;justify-content:flex-start;background:linear-gradient(#f4dfad,#d6aa68)!important;border:3px solid #6e4a25!important;box-shadow:0 4px 9px #0008,inset 0 0 0 1px #f8e8bd;color:#2c2015!important}
.locationArt{width:100%;height:48%;min-height:48px;display:grid;place-items:center;overflow:hidden;flex:0 0 48%;border-bottom:2px solid #7b552a;background-color:#143846;background-repeat:no-repeat}
.locationArt.illustrated{background-image:url('assets/locations-v018.jpg');background-size:500% 100%;background-position-y:center}.loc-tavern{background-position-x:0}.loc-market{background-position-x:25%}.loc-dock{background-position-x:50%}.loc-work{background-position-x:75%}.loc-quarters{background-position-x:100%}
.locationArt.unlockableArt{background:radial-gradient(circle at 68% 28%,#3a6571,#102d39 48%,#081d25);color:#f2d58e;font-size:38px;text-shadow:0 3px 5px #000}.loc-black.unlockableArt{background:radial-gradient(circle at 70% 30%,#6d3426,#241c1a 58%,#100f10)}.loc-veteran.unlockableArt{background:radial-gradient(circle at 70% 30%,#6a5940,#223740 58%,#0d242c)}.loc-witch.unlockableArt{background:radial-gradient(circle at 70% 28%,#17777c,#18394c 55%,#071c29)}
.locationCopy{display:flex;flex:1;min-height:0;width:100%;flex-direction:column;align-items:center;justify-content:center;padding:5px 6px 7px;text-align:center}.locationCopy strong{font:bold clamp(12px,1vw,17px)/1.05 Georgia!important;color:#2a1e14}.locationCopy small{font:600 clamp(9px,.72vw,12px)/1.16 system-ui;color:#4c3826;margin-top:4px;max-width:96%}
.havenSpace .silverHat{z-index:7;width:62px!important;height:52px!important;right:3px!important;top:3px!important}.locationLock{z-index:8!important;position:absolute!important;inset:0!important;display:flex!important;flex-direction:column;align-items:center;justify-content:center;gap:4px;background:#081d25d9!important;color:#ffe3a7!important;border-radius:5px}.locationLock b{font-size:27px}.locationLock small{font:700 9px/1.2 system-ui;max-width:90%;padding:4px 6px;background:#e7d09be8;color:#3b2b1d;border-radius:4px}
#voyage .havenSpace.legal.locationCard{outline:3px solid #fff0a8!important;box-shadow:0 0 0 2px #6d4a22,0 0 19px #ffd86e!important}#voyage .havenSpace.legal.take.locationCard{outline-color:#8ce9ff!important;box-shadow:0 0 0 2px #0e5366,0 0 19px #72def5!important}

/* Zone requirements remain visible even when a zone is locked. */
.atlasBoard .seaZone>header{display:flex;flex-direction:column;align-items:center;gap:4px}.zoneSupplyBadge{display:grid!important;grid-template-columns:31px auto;grid-template-rows:auto auto;align-items:center;column-gap:6px;margin-top:3px!important;padding:3px 9px 4px;border:2px solid #9f793d;border-radius:6px;background:#f1ddb0;color:#2d2116!important;box-shadow:inset 0 0 0 1px #fff3c6}.zoneSupplyBadge .resourceIcon{grid-row:1/3;width:31px;height:31px}.zoneSupplyBadge b{font:bold 13px/1 Georgia}.zoneSupplyBadge small{font:9px/1.05 system-ui;color:#61492f}.zoneGate{display:block!important;margin:0!important;padding:2px 6px;border-radius:4px;background:#271d18d9;color:#ffe2a1!important;font:700 9px/1.1 system-ui!important}.zone1 .zoneSupplyBadge{border-color:#386c9c}.zone2 .zoneSupplyBadge{border-color:#9a3a38}.zone3 .zoneSupplyBadge{border-color:#71469a}.zone4 .zoneSupplyBadge{border-color:#9c6234}
.zoneLocked header{opacity:1!important}.zoneLocked .zoneSupplyBadge{filter:none!important}

/* One-level undo is intentionally limited to the unresolved worker placement/take. */
#voyage .undoWorkerBtn,#voyageDialog .undoWorkerBtn{background:linear-gradient(#9b6b22,#604114)!important;border-color:#ffd77a!important;color:#fff1c7!important;font-weight:700;box-shadow:0 0 0 1px #ffdd7b33,0 3px 8px #0006}.undoWorkerBtn:before{content:'↶';margin-right:5px}.vHud .undoWorkerBtn:before{display:none}

/* Supply purchase uses visual barrel choices instead of a numeric input. */
.marketPurchaseIntro{display:flex;align-items:center;justify-content:center;gap:14px;max-width:760px;margin:4px auto 16px;padding:11px 15px;border:1px solid #8d7141;border-radius:10px;background:#e8d4a012;color:#f4e4c1}.marketPurchaseIntro>.resourceIcon{width:58px;height:58px}.marketPurchaseIntro p{margin:0}.marketPurchaseIntro .resourceIcon{width:26px;height:26px}
.supplyBuyGrid{display:grid;grid-template-columns:repeat(5,minmax(105px,1fr));gap:10px;max-width:880px;margin:auto}.supplyBuyGrid #voyageBody button,.supplyBuyBtn{margin:0!important}.supplyBuyBtn{min-height:150px!important;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:5px;padding:10px!important;background:linear-gradient(#ead7a8,#c99b5b)!important;color:#2d2116!important;border:3px double #745025!important;box-shadow:0 5px 9px #0007!important}.supplyBuyBtn>.resourceIcon{width:66px;height:66px}.supplyBuyBtn strong{font:bold 17px Georgia}.supplyBuyBtn small{display:flex;align-items:center;gap:4px;font:700 12px system-ui}.supplyBuyBtn small .resourceIcon{width:24px;height:24px}.supplyBuyBtn:not(:disabled):hover{transform:translateY(-2px);filter:brightness(1.07)}.supplyBuyBtn:disabled{filter:grayscale(.75);opacity:.38!important}

#voyage .playerNumbers span{display:inline-flex;align-items:center;gap:4px}.playerNumbers .resourceIcon{width:24px;height:24px}.marketTile .resourceIcon{width:22px;height:22px}

@media(max-height:780px) and (min-width:851px){.locationArt{height:42%;flex-basis:42%;min-height:38px}.locationCopy small{font-size:8px}.locationCopy{padding:3px}.zoneSupplyBadge{transform:scale(.9);transform-origin:center top}.supplyBuyBtn{min-height:130px!important}}
@media(max-width:850px){.locationCopy small{font-size:9px}.locationArt{min-height:55px}.zoneSupplyBadge .resourceIcon{width:26px;height:26px}.zoneSupplyBadge{grid-template-columns:26px auto}.supplyBuyGrid{grid-template-columns:repeat(2,minmax(120px,1fr))}.supplyBuyBtn{min-height:130px!important}.marketPurchaseIntro>.resourceIcon{width:48px;height:48px}}
'''
p.write_text(s)


# ---------------------------------------------------------------------------
# Visible release labels.
# ---------------------------------------------------------------------------
p = Path('index.html')
s = p.read_text()
replacements = {
    "<title>Captain's Dash: The Final Isle — v0.17 Test</title>": "<title>Captain's Dash: The Final Isle — v0.18 Test</title>",
    "CAPTAIN'S DASH · FULL GAME · v0.17 TEST": "CAPTAIN'S DASH · FULL GAME · v0.18 TEST",
    "Interactive Web Edition · v0.17 Test.": "Interactive Web Edition · v0.18 Test.",
}
for old, new in replacements.items():
    s = replace_once(s, old, new, 'index release label')
p.write_text(s)


# ---------------------------------------------------------------------------
# Static assertions before CI runs syntax/rules/build checks.
# ---------------------------------------------------------------------------
checks = {
    'menu.js': ['version:"0.18"'],
    'voyage-v014.js': [
        'undoWorkerState',
        "resourceIcon('supply')",
        'locationHelp=',
        'zoneSupplyBadge',
        'supplyBuyGrid',
        "data-amount=\"${n}\"",
        "name==='undoWorker'",
        'The Final Isle · v0.18',
    ],
    'voyage-table.css': [
        'assets/locations-v018.jpg',
        'assets/resources-v018.jpg',
        '.zoneSupplyBadge',
        '.supplyBuyGrid',
        '.undoWorkerBtn',
    ],
    'index.html': ['v0.18 TEST'],
}
for file, markers in checks.items():
    text = Path(file).read_text()
    for marker in markers:
        if marker not in text:
            raise SystemExit(f'{file}: missing marker {marker}')

print('v0.18 code patch verified')
