from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly 1 match, found {count}")
    return text.replace(old, new, 1)


# Setup / AI player count -----------------------------------------------------
p = Path("menu.js")
s = p.read_text()
s = replace_once(
    s,
    '  const seaNames=["Anne","Black","Morgan","Silver","Flint","Rackham","Bonny","Vane","Drake","Kidd","Read","Bellamy"];\n',
    '  const seaNames=["Anne","Black","Morgan","Silver","Flint","Rackham","Bonny","Vane","Drake","Kidd","Read","Bellamy"];\n  const aiNames=["AI Blackbeard","AI Morgan","AI Silver"];\n',
    "add AI names",
)
s = replace_once(
    s,
    '''  function setCount(n, values) {
    count=n;
    document.querySelectorAll("[data-count]").forEach(b=>b.classList.toggle("on",+b.dataset.count===n));
    renderNames(values);
  }
  document.querySelectorAll("[data-count]").forEach(b=>b.addEventListener("click",()=>{setCount(gameMode==="ai"?2:+b.dataset.count);clickSfx(500)}));
  renderNames();
  document.querySelectorAll("[data-game-mode]").forEach(b=>b.addEventListener("click",()=>{
    gameMode=b.dataset.gameMode;document.querySelectorAll("[data-game-mode]").forEach(x=>x.classList.toggle("on",x===b));
    if(gameMode==="ai"){setCount(2);const ins=[...document.querySelectorAll("#names input")];if(ins[1])ins[1].value="AI Blackbeard";}clickSfx(510);
  }));
''',
    '''  function syncModeNames() {
    const ins=[...document.querySelectorAll("#names input")];
    ins.forEach((x,i)=>{
      const ai=gameMode==="ai"&&i>0;
      x.readOnly=ai;
      x.classList.toggle("aiName",ai);
      if(ai)x.value=aiNames[i-1]||`AI Captain ${i}`;
    });
  }
  function setCount(n, values) {
    count=Math.max(2,Math.min(4,n));
    document.querySelectorAll("[data-count]").forEach(b=>b.classList.toggle("on",+b.dataset.count===count));
    renderNames(values);
    syncModeNames();
  }
  document.querySelectorAll("[data-count]").forEach(b=>b.addEventListener("click",()=>{
    const values=[...document.querySelectorAll("#names input")].map(x=>x.value);
    setCount(+b.dataset.count,values);
    clickSfx(500);
  }));
  renderNames();
  syncModeNames();
  document.querySelectorAll("[data-game-mode]").forEach(b=>b.addEventListener("click",()=>{
    const values=[...document.querySelectorAll("#names input")].map(x=>x.value);
    gameMode=b.dataset.gameMode;document.querySelectorAll("[data-game-mode]").forEach(x=>x.classList.toggle("on",x===b));
    setCount(count,values);
    clickSfx(510);
  }));
''',
    "enable 2-4 AI setup",
)
s = replace_once(s, '      version:"0.15",', '      version:"0.17",', "setup version")
s = replace_once(
    s,
    '''  document.getElementById("randomNames").addEventListener("click",()=>{
    const shuffled=[...seaNames].sort(()=>Math.random()-.5);
    document.querySelectorAll("#names input").forEach((x,i)=>x.value=shuffled[i]);
    clickSfx(620);
  });
''',
    '''  document.getElementById("randomNames").addEventListener("click",()=>{
    const shuffled=[...seaNames].sort(()=>Math.random()-.5);
    document.querySelectorAll("#names input").forEach((x,i)=>{if(gameMode!=="ai"||i===0)x.value=shuffled[i]});
    syncModeNames();
    clickSfx(620);
  });
''',
    "preserve AI names",
)
s = s.replace("This replaces the saved v0.15 voyage on this device.", "This replaces the saved voyage on this device.")
s = replace_once(
    s,
    '    document.getElementById("voyageSummary").textContent=`${s.players} Captains · ${s.mode==="ai"?"Solo vs AI":"Local Pass & Play"} · Final Isle awaits`;',
    '    document.getElementById("voyageSummary").textContent=`${s.players} Captains · ${s.mode==="ai"?"1 Human + "+(s.players-1)+" AI":"Local Pass & Play"} · Final Isle awaits`;',
    "AI voyage summary",
)
p.write_text(s)


# Board / AI turn behavior ----------------------------------------------------
p = Path("voyage-v014.js")
s = p.read_text()
s = replace_once(
    s,
    "const isAITurn=()=>state?.mode==='ai'&&state.turn===1&&state.status==='playing';",
    "const isAITurn=()=>state?.mode==='ai'&&state.turn>0&&state.status==='playing';",
    "all non-human captains are AI",
)
s = replace_once(s, "The Final Isle · v0.16", "The Final Isle · v0.17", "HUD release version")
s = replace_once(s, "isAITurn()?'Blackbeard is thinking'", "isAITurn()?esc(p.name)+' is thinking'", "AI thinking label")
s = replace_once(
    s,
    "${i===state.turn?'YOUR TURN':'PRIVATE'}",
    "${i===state.turn?(state.mode==='ai'&&i>0?'AI TURN':'YOUR TURN'):'PRIVATE'}",
    "AI player dock label",
)
s = replace_once(
    s,
    'class="havenSpace ${legalWorker(state,id)?\'legal \'+state.phase:\'\'}"',
    'class="havenSpace ${legalWorker(state,id)?\'legal \'+state.phase:\'\'}${isAITurn()&&state.location===id?\' aiChosen\':\'\'}"',
    "AI location pulse hook",
)
s = replace_once(
    s,
    '</header><div class="atlasBoard ${zoom?\'zoomedAtlas\':\'\'}">',
    '</header>${isAITurn()?`<div class="aiTurnBanner" role="status" aria-live="polite"><img src="assets/${portraits[state.turn]}" alt=""><div><small>AI TURN</small><strong>${esc(p.name)}</strong><span>${state.exp?\'Resolving expedition\':state.location?\'Resolving \'+LOCATIONS[state.location]:state.phase===\'place\'?\'Choosing where to place a Pirate\':\'Choosing where to take a Pirate\'}</span></div><i></i></div>`:\'\'}<div class="atlasBoard ${zoom?\'zoomedAtlas\':\'\'}">',
    "AI turn banner",
)
old_recruit = '''<section class="recruitPanel"><header><h2>Crew Market</h2><span>3 face-up · Recruit at Tavern</span></header><div class="marketTiles">${state.market.map(id=>`<button class="marketTile" data-action="inspect" data-id="${id}" aria-label="Inspect ${esc(CARDS[id].name)}">${art(CARDS[id])}<strong>${esc(CARDS[id].name)}</strong><span>🪙 ${CARDS[id].cost}</span></button>`).join('')}</div></section>'''
new_recruit = '''<section class="recruitPanel"><header><h2>Crew & Treasure</h2><span>Common Crew · Veteran · Treasure</span></header><div class="recruitBody"><div class="marketGroup"><div class="shelfLabel"><b>Crew Market</b><small>3 face-up · Tavern</small></div><div class="marketTiles">${state.market.map(id=>`<button class="marketTile" data-action="inspect" data-id="${id}" aria-label="Inspect ${esc(CARDS[id].name)}">${art(CARDS[id])}<strong>${esc(CARDS[id].name)}</strong><span>🪙 ${CARDS[id].cost}</span></button>`).join('')}</div></div><div class="deckShelf"><div class="deckSlot veteranSlot ${locationOpen(state,'veteran')?'unlocked':'locked'}" aria-label="Veteran deck"><span class="deckIcon">⚔</span><strong>Veteran</strong><small>${locationOpen(state,'veteran')?(state.veteranDeck.length+state.veteranMarket.length)+' cards · Open':'Locked at start · Clear 2 Zone II'}</small>${locationOpen(state,'veteran')?'':'<span class="deckLock">🔒</span>'}</div><div class="deckSlot treasureSlot" aria-label="Treasure deck"><span class="deckIcon">◆</span><strong>Treasure</strong><small>${state.treasureDeck.length} cards</small></div></div></div></section>'''
s = replace_once(s, old_recruit, new_recruit, "Veteran and Treasure shelf")
old_ai_pending = '''if(isAITurn()){modal('Blackbeard’s turn','<div class="handoffScreen"><img src="assets/'+portraits[1]+'" alt="Blackbeard"><h2>Blackbeard is taking his turn</h2><p>His Crew and Treasure are private.</p></div>',true);return}'''
new_ai_pending = '''if(isAITurn()){if(state.exp){showExp();return}if(dlg.open)dlg.close();return}'''
s = replace_once(s, old_ai_pending, new_ai_pending, "non-blocking AI turn")
s = replace_once(s, "Blackbeard is taking this turn.", "The AI captain is taking this turn.", "generic AI lock message")
s = replace_once(
    s,
    "function scheduleAI(){clearTimeout(aiTimer);if(!root.hidden&&state.status==='playing'&&state.mode==='ai'&&state.turn===1)aiTimer=setTimeout(aiStep,650)}",
    "function scheduleAI(){clearTimeout(aiTimer);if(!root.hidden&&isAITurn())aiTimer=setTimeout(aiStep,1050)}",
    "AI timing and multi-AI scheduling",
)
p.write_text(s)


# v0.17 tabletop layout -------------------------------------------------------
p = Path("voyage-table.css")
s = p.read_text()
marker = "/* v0.17 — larger Pirate Haven token spaces, compact Crew market, Veteran/Treasure decks, Final Test top-right, visible AI turns. */"
if marker not in s:
    s += r'''

/* v0.17 — larger Pirate Haven token spaces, compact Crew market, Veteran/Treasure decks, Final Test top-right, visible AI turns. */
@media (min-width:851px){
  .atlasBoard{grid-template-columns:28% 28% 24% 20%;grid-template-rows:55% 45%;padding:10px 12px 14px}
  .zone1{grid-area:1/1}.zone2{grid-area:1/2}.zone3{grid-area:1/3}
  .zone4{grid-area:1/4/2/5;justify-content:flex-start;padding:6px 7px 2px}
  .zone4 header{margin-bottom:6px;padding:5px 9px}
  .zone4 .zoneCards{flex:1;align-items:flex-start;justify-content:center}
  .zone4 .missionTile{width:min(100%,158px);max-width:158px;max-height:245px}
  .havenPanel{grid-area:2/1/3/3;justify-content:flex-end;align-self:stretch;padding:6px 12px 8px}
  .havenPanel header{margin-bottom:8px;padding:5px 22px}
  .havenSpaces{grid-template-columns:repeat(4,minmax(0,1fr));gap:9px;width:100%;height:100%}
  #voyage .havenSpace{min-height:78px;padding:9px 5px;border-width:3px;border-radius:9px}
  .locationSymbol{font-size:34px}
  .havenSpace strong{font-size:clamp(12px,1.05vw,16px)}
  .havenSpace .silverHat{width:58px;height:48px;right:3px;top:3px}
  .recruitPanel{grid-area:2/3/3/5;justify-content:flex-end;align-items:stretch;padding:6px 8px 8px}
  .recruitPanel header{align-self:center;margin-bottom:5px;padding:4px 18px}
  .recruitBody{display:flex;gap:10px;align-items:stretch;min-height:0;flex:1;width:100%}
  .marketGroup{display:flex;flex-direction:column;min-width:0;flex:1.35}
  .shelfLabel{display:flex;align-items:center;justify-content:space-between;gap:8px;color:#ffe7ad;font:12px system-ui;padding:0 2px 4px;text-shadow:0 1px 2px #000}
  .shelfLabel b{font:700 14px Georgia}.shelfLabel small{font-size:10px;color:#d8cfba}
  .marketTiles{gap:7px;justify-content:space-between;height:auto;flex:1;min-height:0}
  #voyage .marketTile{width:31%;max-width:102px;min-height:112px;padding:3px;border-width:2px}
  .marketTile strong{font-size:10px;padding:2px;min-height:2.3em;display:grid;place-items:center}
  .marketTile>span{font-size:11px}
  .deckShelf{display:flex;gap:8px;justify-content:flex-end;align-items:stretch;flex:.9;min-width:150px}
  .deckSlot{position:relative;flex:1;min-width:68px;max-width:102px;border:4px double #c99f55;border-radius:9px;background:linear-gradient(145deg,#183f4a,#0b2731 58%,#061b23);box-shadow:0 5px 10px #0008,inset 0 0 0 1px #f2da9226;color:#f1d79a;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:8px 5px;overflow:hidden}
  .deckSlot:before{content:'';position:absolute;inset:5px;border:1px solid #d6b46355;border-radius:5px;pointer-events:none}
  .deckSlot .deckIcon{font-size:32px;line-height:1;margin-bottom:8px}.deckSlot strong{font:700 15px Georgia}.deckSlot small{font:9px/1.25 system-ui;margin-top:7px;color:#d8c9a8;max-width:90px}
  .treasureSlot{background:linear-gradient(145deg,#5b421f,#2b2012 60%,#17130c)}
  .veteranSlot.locked{filter:saturate(.35) brightness(.72)}.deckLock{position:absolute;right:5px;top:4px;font-size:18px;filter:none}
}
.aiTurnBanner{position:absolute;z-index:65;top:84px;left:50%;transform:translateX(-50%);display:flex;align-items:center;gap:11px;min-width:300px;max-width:min(520px,72vw);padding:8px 18px 8px 9px;border:2px solid #f0c664;border-radius:999px;background:linear-gradient(90deg,#102f3bf2,#071d27f2);box-shadow:0 8px 24px #000a,0 0 24px #d8ae4938;color:#f4dfae;pointer-events:none;animation:aiBannerIn .32s ease-out}
.aiTurnBanner img{width:44px;height:44px;object-fit:cover;border-radius:50%;border:2px solid #c9a354}.aiTurnBanner div{display:grid;grid-template-columns:auto 1fr;column-gap:8px;align-items:baseline;min-width:0}.aiTurnBanner small{font:700 10px system-ui;letter-spacing:.13em;color:#8fe4ff}.aiTurnBanner strong{font:700 17px Georgia;white-space:nowrap}.aiTurnBanner span{grid-column:1/3;font:12px system-ui;color:#d7d4c9;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.aiTurnBanner i{width:9px;height:9px;border-radius:50%;background:#8fe4ff;box-shadow:0 0 0 0 #8fe4ff88;animation:aiThinking 1.15s infinite}
#voyage .havenSpace.aiChosen{outline:4px solid #7ee7ff!important;box-shadow:0 0 0 5px #0b526b99,0 0 28px #6eddf2!important;animation:aiSpacePulse .85s ease-in-out infinite alternate}
@keyframes aiBannerIn{from{opacity:0;transform:translate(-50%,-12px) scale(.96)}to{opacity:1;transform:translateX(-50%) scale(1)}}
@keyframes aiThinking{70%{box-shadow:0 0 0 9px #8fe4ff00}100%{box-shadow:0 0 0 0 #8fe4ff00}}
@keyframes aiSpacePulse{from{transform:scale(1)}to{transform:scale(1.025)}}
@media(max-width:850px){.aiTurnBanner{top:74px;min-width:250px;max-width:80vw}.recruitBody{display:flex;gap:7px}.marketGroup{min-width:0;flex:1}.deckShelf{display:flex;gap:5px;width:150px}.deckSlot{flex:1;min-width:0;padding:5px}.deckSlot .deckIcon{font-size:24px}.deckSlot strong{font-size:12px}.deckSlot small{font-size:8px}}
@media(prefers-reduced-motion:reduce){.aiTurnBanner,#voyage .havenSpace.aiChosen,.aiTurnBanner i{animation:none!important}}
'''
p.write_text(s)


# Visible release labels ------------------------------------------------------
p = Path("index.html")
s = p.read_text()
replacements = {
    "<title>Captain's Dash: The Final Isle — v0.15 Final</title>": "<title>Captain's Dash: The Final Isle — v0.17 Test</title>",
    "CAPTAIN'S DASH · FULL GAME · v0.15.1 FINAL": "CAPTAIN'S DASH · FULL GAME · v0.17 TEST",
    '<small>You vs an AI Captain · 2 players</small>': '<small>You + 1–3 AI Captains · 2–4 players</small>',
    "Interactive Web Edition · v0.15 Final.": "Interactive Web Edition · v0.17 Test.",
    '<span>👥 <b>2–4 Players</b> · Pass & Play</span>': '<span>👥 <b>2–4 Players</b> · Pass & Play / 1 Human + AI</span>',
}
for old, new in replacements.items():
    if old not in s:
        raise SystemExit(f"index marker missing: {old}")
    s = s.replace(old, new, 1)
p.write_text(s)


# Static release checks -------------------------------------------------------
checks = {
    "menu.js": ['version:"0.17"', "setCount(+b.dataset.count", "AI Morgan", "AI Silver"],
    "voyage-v014.js": ["state.turn>0", "The Final Isle · v0.17", "deckShelf", "aiTurnBanner", "setTimeout(aiStep,1050)"],
    "voyage-table.css": ["grid-area:1/4/2/5", "grid-area:2/1/3/3", "veteranSlot.locked", "aiSpacePulse"],
    "index.html": ["v0.17 TEST", "You + 1–3 AI Captains · 2–4 players"],
}
for file, markers in checks.items():
    text = Path(file).read_text()
    for m in markers:
        if m not in text:
            raise SystemExit(f"{file}: missing release marker {m}")

print("v0.17 patch markers verified")
