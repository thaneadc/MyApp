from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected 1 match, found {count}")
    return text.replace(old, new, 1)


# ---------------------------------------------------------------------------
# Engine: Black Market refresh costs 1 Gold per refreshed card.
# ---------------------------------------------------------------------------
p = Path('engine-v014.mjs')
s = p.read_text()
old_refresh = " else if(a.type==='refresh'){must(loc==='black'&&!s.blackRefreshed,'Refresh unavailable');must(Array.isArray(a.ids)&&a.ids.length<=3,'Select up to 3 market cards');for(const id of a.ids){const index=s.market.indexOf(id);must(index>=0,'Select only available market copies');s.market.splice(index,1)}s.crewDeck=shuffle([...s.crewDeck,...a.ids],rng);while(s.market.length<3&&s.crewDeck.length)s.market.push(s.crewDeck.shift());s.blackRefreshed=true;return s}"
new_refresh = " else if(a.type==='refresh'){must(loc==='black'&&!s.blackRefreshed,'Refresh unavailable');must(Array.isArray(a.ids)&&a.ids.length>=1&&a.ids.length<=3,'Select 1–3 market cards');must(p.gold>=a.ids.length,'Not enough Gold to refresh those cards');for(const id of a.ids){const index=s.market.indexOf(id);must(index>=0,'Select only available market copies');s.market.splice(index,1)}p.gold-=a.ids.length;s.crewDeck=shuffle([...s.crewDeck,...a.ids],rng);while(s.market.length<3&&s.crewDeck.length)s.market.push(s.crewDeck.shift());s.blackRefreshed=true;return s}"
s = replace_once(s, old_refresh, new_refresh, 'Black Market refresh cost')
p.write_text(s)


# ---------------------------------------------------------------------------
# Voyage UI: icon family, Veteran face-up market, refresh-cost UI, version.
# ---------------------------------------------------------------------------
p = Path('voyage-v014.js')
s = p.read_text()
old_icon = '''const testIcon=(type)=>type==='Sailing'?`<span class="testIcon sailingIcon" role="img" aria-label="Sailing"><svg viewBox="0 0 64 64" focusable="false"><circle class="helmRing" cx="32" cy="32" r="16"/><circle class="helmHub" cx="32" cy="32" r="5"/><path class="helmSpokes" d="M32 5v18M32 41v18M5 32h18M41 32h18M12.9 12.9l12.7 12.7M38.4 38.4l12.7 12.7M51.1 12.9L38.4 25.6M25.6 38.4L12.9 51.1"/><circle class="helmHandle" cx="32" cy="5" r="3.7"/><circle class="helmHandle" cx="32" cy="59" r="3.7"/><circle class="helmHandle" cx="5" cy="32" r="3.7"/><circle class="helmHandle" cx="59" cy="32" r="3.7"/><circle class="helmHandle" cx="12.9" cy="12.9" r="3.7"/><circle class="helmHandle" cx="51.1" cy="51.1" r="3.7"/><circle class="helmHandle" cx="51.1" cy="12.9" r="3.7"/><circle class="helmHandle" cx="12.9" cy="51.1" r="3.7"/></svg></span>`:type==='Search'?`<span class="testIcon searchIcon" role="img" aria-label="Search"><svg viewBox="0 0 72 48" focusable="false"><path class="binocularBody" d="M8 35l8-22h13l3 8h8l3-8h13l8 22"/><circle class="binocularLens" cx="20" cy="34" r="10"/><circle class="binocularLens" cx="52" cy="34" r="10"/><path class="binocularBridge" d="M29 24c4-3 10-3 14 0M16 13l3-5h8l2 5M43 13l2-5h8l3 5"/></svg></span>`:'⚔';'''
new_icon = '''const testIcon=(type)=>type==='Combat'?`<span class="testIcon combatIcon" role="img" aria-label="Combat"><svg viewBox="0 0 64 64" focusable="false"><path class="cutlassBlade" d="M12 9c8 15 20 29 40 43M52 9C44 24 32 39 12 52"/><path class="cutlassGuard" d="M14 43l8 9M42 52l8-9"/><path class="cutlassGrip" d="M11 50l5 5M53 50l-5 5"/></svg></span>`:type==='Sailing'?`<span class="testIcon sailingIcon" role="img" aria-label="Sailing"><svg viewBox="0 0 64 64" focusable="false"><circle class="helmRing" cx="32" cy="32" r="16"/><circle class="helmHub" cx="32" cy="32" r="5"/><path class="helmSpokes" d="M32 5v18M32 41v18M5 32h18M41 32h18M12.9 12.9l12.7 12.7M38.4 38.4l12.7 12.7M51.1 12.9L38.4 25.6M25.6 38.4L12.9 51.1"/><circle class="helmHandle" cx="32" cy="5" r="3.7"/><circle class="helmHandle" cx="32" cy="59" r="3.7"/><circle class="helmHandle" cx="5" cy="32" r="3.7"/><circle class="helmHandle" cx="59" cy="32" r="3.7"/><circle class="helmHandle" cx="12.9" cy="12.9" r="3.7"/><circle class="helmHandle" cx="51.1" cy="51.1" r="3.7"/><circle class="helmHandle" cx="51.1" cy="12.9" r="3.7"/><circle class="helmHandle" cx="12.9" cy="51.1" r="3.7"/></svg></span>`:type==='Search'?`<span class="testIcon searchIcon" role="img" aria-label="Search"><svg viewBox="0 0 72 48" focusable="false"><path class="spyglassBody" d="M10 31l36-18 8 12-36 18z"/><path class="spyglassRim" d="M45 13l10-5 9 14-10 5z"/><path class="spyglassGrip" d="M10 31l-5 4 7 10 6-2z"/><path class="spyglassBand" d="M24 24l7 11M35 19l7 11"/></svg></span>`:'';'''
s = replace_once(s, old_icon, new_icon, 'unified pirate test icons')

# Version labels.
s = replace_once(s, 'The Final Isle · v0.23', 'The Final Isle · v0.24', 'HUD version')
s = replace_once(s, "'All 81 cards · v0.23'", "'All 81 cards · v0.24'", 'card library version')

# Central face-up market switches from Common to Veteran once Veteran's Den is open.
s = replace_once(
    s,
    '<div class="shelfLabel"><b>Crew Market <em class="sharedBadge">SHARED</em></b><small>3 face-up · Tavern</small></div><div class="marketTiles">${state.market.map(id=>',
    '<div class="shelfLabel"><b>${locationOpen(state,\'veteran\')?\'Veteran Crew Market\':\'Crew Market\'} <em class="sharedBadge">SHARED</em></b><small>${locationOpen(state,\'veteran\')?"3 face-up · Veteran’s Den":"3 face-up · Tavern"}</small></div><div class="marketTiles">${(locationOpen(state,\'veteran\')?state.veteranMarket:state.market).map(id=>',
    'Veteran market takes over central face-up display',
)
s = replace_once(
    s,
    '<strong>Veteran <em class="sharedBadge">SHARED</em></strong><small>${locationOpen(state,\'veteran\')?(state.veteranDeck.length+state.veteranMarket.length)+\' cards · Open\':\'Locked at start · Clear 2 Zone II\'}</small>',
    '<strong>${locationOpen(state,\'veteran\')?\'Veteran Reserve\':\'Veteran\'} <em class="sharedBadge">SHARED</em></strong><small>${locationOpen(state,\'veteran\')?state.veteranDeck.length+\' cards · Reserve deck\':\'Locked at start · Clear 2 Zone II\'}</small>',
    'Veteran reserve label',
)

# Black Market UI: show 1 Gold/card and live selected cost.
old_black = '''if(l==='black'&&!state.blackRefreshed)html=`<p>Select up to 3 cards to refresh, then recruit at 1 Gold less.</p><div class="vGrid">${ids.map(id=>card(id,`<label><input type="checkbox" name="refresh" value="${id}"> Refresh</label>`)).join('')}</div>${button('refresh','Refresh selected cards')}`;'''
new_black = '''if(l==='black'&&!state.blackRefreshed)html=`<div class="blackMarketCost"><strong>Refresh costs ${resourceIcon('gold')} 1 Gold per card</strong><span>You have ${resourceIcon('gold')} <b>${p.gold}</b> Gold</span></div><p>Select 1–3 Common Crew cards to replace. After refreshing, recruit at 1 Gold less.</p><div class="vGrid">${ids.map(id=>card(id,`<label class="refreshChoice"><input type="checkbox" name="refresh" value="${id}"> Refresh this card · ${resourceIcon('gold')} 1</label>`)).join('')}</div><div class="blackRefreshFooter"><span id="blackRefreshSummary">Selected: 0 · Cost: 0 Gold</span>${button('refresh','Select cards to refresh','id="blackRefreshBtn" disabled')}</div>`;'''
s = replace_once(s, old_black, new_black, 'Black Market cost UI')

old_modal = " modal(LOCATIONS[l],'<p class=\"pirateBanter\">“'+banter[l]+'”</p>'+html+'<div class=\"vToolbar\">'+(canUndoWorker()?button('undoWorker','↶ Undo Token','class=\"undoWorkerBtn\"'):'')+skip+'</div>');"
new_modal = " modal(LOCATIONS[l],'<p class=\"pirateBanter\">“'+banter[l]+'”</p>'+html+'<div class=\"vToolbar\">'+(canUndoWorker()?button('undoWorker','↶ Undo Token','class=\"undoWorkerBtn\"'):'')+skip+'</div>');if(l==='black'&&!state.blackRefreshed){const updateRefreshCost=()=>{const n=body.querySelectorAll('[name=refresh]:checked').length,btn=body.querySelector('#blackRefreshBtn'),summary=body.querySelector('#blackRefreshSummary'),cost=n;summary.textContent=`Selected: ${n} · Cost: ${cost} Gold`;btn.disabled=n<1||n>3||cost>p.gold;btn.textContent=n?`Refresh ${n} card${n===1?'':'s'} · ${cost} Gold`:'Select cards to refresh'};body.onchange=updateRefreshCost;updateRefreshCost();}"
s = replace_once(s, old_modal, new_modal, 'Black Market live cost summary')

# AI must pay for refresh too; refresh only what it can afford.
s = replace_once(
    s,
    "if(l==='black'&&!state.blackRefreshed)a={type:'refresh',ids:state.market};else{",
    "if(l==='black'&&!state.blackRefreshed)a=p.gold?{type:'refresh',ids:state.market.slice(0,Math.min(3,p.gold))}:{type:'skip'};else{",
    'AI paid Black Market refresh',
)
p.write_text(s)


# ---------------------------------------------------------------------------
# CSS: icon family consistency, remove nested-stat stray border, Black Market.
# ---------------------------------------------------------------------------
p = Path('voyage-table.css')
s = p.read_text()
marker = '/* v0.24 — pirate icon family, clean stat cells, paid Black Market, Veteran market phase. */'
if marker not in s:
    s += r'''

/* v0.24 — pirate icon family, clean stat cells, paid Black Market, Veteran market phase. */
.combatIcon,.sailingIcon,.searchIcon{width:1.46em!important;height:1.46em!important;display:inline-grid;place-items:center;overflow:visible}.combatIcon svg,.sailingIcon svg,.searchIcon svg{width:100%;height:100%;overflow:visible}.combatIcon svg *,.sailingIcon svg *,.searchIcon svg *{fill:none;stroke:currentColor;stroke-linecap:round;stroke-linejoin:round}.combatIcon .cutlassBlade{stroke-width:4.4}.combatIcon .cutlassGuard{stroke-width:4.8}.combatIcon .cutlassGrip{stroke-width:5}.searchIcon .spyglassBody,.searchIcon .spyglassRim{stroke-width:4}.searchIcon .spyglassGrip,.searchIcon .spyglassBand{stroke-width:3.6}
/* v0.23's broad span selector also reached the nested icon span and drew a short right border. */
.physicalCard .vStats .testIcon{border-right:0!important;padding:0!important;background:transparent!important;min-width:0!important;flex:0 0 32px!important}.physicalCard .vStats>span:last-child{border-right:0!important}.physicalCard .vStats>span{overflow:hidden}
.blackMarketCost{display:flex;align-items:center;justify-content:space-between;gap:12px;margin:0 0 14px;padding:10px 14px;border:1px solid #b78e4c;border-radius:10px;background:linear-gradient(135deg,#2d1d17,#142d35);color:#f3dfae}.blackMarketCost strong,.blackMarketCost span{display:flex;align-items:center;gap:5px}.blackMarketCost .resourceIcon{width:28px;height:28px}.refreshChoice{display:flex!important;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}.refreshChoice .resourceIcon{width:22px;height:22px}.blackRefreshFooter{position:sticky;bottom:-1px;z-index:3;display:flex;align-items:center;justify-content:space-between;gap:12px;margin-top:14px;padding:10px 12px;border:1px solid #b28b4a;border-radius:10px;background:#09232deb;backdrop-filter:blur(5px);color:#f2dda9}.blackRefreshFooter span{font:700 13px system-ui}.blackRefreshFooter button{margin:0!important}.blackRefreshFooter button:disabled{opacity:.42!important}
.marketGroup:has(.marketTile) .sharedBadge{white-space:nowrap}
@media(max-width:700px){.blackMarketCost,.blackRefreshFooter{align-items:flex-start;flex-direction:column}.blackRefreshFooter button{width:100%}.combatIcon,.sailingIcon,.searchIcon{width:1.36em!important;height:1.36em!important}}
'''
p.write_text(s)


# ---------------------------------------------------------------------------
# Menu + landing labels.
# ---------------------------------------------------------------------------
p = Path('menu.js')
s = p.read_text()
s = replace_once(s, '      version:"0.23",', '      version:"0.24",', 'setup version')
p.write_text(s)

p = Path('index.html')
s = p.read_text()
if 'v0.23' not in s:
    raise SystemExit('index: v0.23 marker missing')
s = s.replace('v0.23', 'v0.24')
p.write_text(s)


# ---------------------------------------------------------------------------
# Static release checks.
# ---------------------------------------------------------------------------
checks = {
    'engine-v014.mjs': ["p.gold-=a.ids.length", "Select 1–3 market cards", "Not enough Gold to refresh those cards"],
    'voyage-v014.js': ["combatIcon", "spyglassBody", "Veteran Crew Market", "state.veteranMarket:state.market", "blackRefreshBtn", "state.market.slice(0,Math.min(3,p.gold))", "The Final Isle · v0.24"],
    'voyage-table.css': ["v0.24 — pirate icon family", ".physicalCard .vStats .testIcon{border-right:0", ".blackRefreshFooter"],
    'menu.js': ['version:"0.24"'],
    'index.html': ['v0.24'],
}
for file, markers in checks.items():
    text = Path(file).read_text()
    for m in markers:
        if m not in text:
            raise SystemExit(f'{file}: missing v0.24 marker {m}')

print('v0.24 patch markers verified')
