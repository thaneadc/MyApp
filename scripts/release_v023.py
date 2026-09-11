from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected 1 match, found {count}")
    return text.replace(old, new, 1)


# ---------------------------------------------------------------------------
# Engine: Crew Quarters now readies every exhausted Crew in one action.
# ---------------------------------------------------------------------------
p = Path('engine-v014.mjs')
s = p.read_text()
s = replace_once(
    s,
    " else if(a.type==='ready'){must(loc==='quarters','Use Crew Quarters');must(a.ids.length<=4&&new Set(a.ids).size===a.ids.length&&a.ids.every(uid=>p.crew.some(c=>c.uid===uid&&c.exhausted)),'Choose up to 4 exhausted Crew');for(const c of p.crew)if(a.ids.includes(c.uid))c.exhausted=false}",
    " else if(a.type==='ready'){must(loc==='quarters','Use Crew Quarters');for(const c of p.crew)c.exhausted=false}",
    'Crew Quarters ready all',
)
p.write_text(s)


# ---------------------------------------------------------------------------
# Voyage UI: improved maritime icons, Expedition/prep card layout and quarters.
# ---------------------------------------------------------------------------
p = Path('voyage-v014.js')
s = p.read_text()
old_icon = '''const testIcon=(type)=>type==='Sailing'?`<span class="testIcon sailingIcon" role="img" aria-label="Sailing"><svg viewBox="0 0 48 48" focusable="false"><circle cx="24" cy="24" r="11"/><circle cx="24" cy="24" r="3.5"/><path d="M24 3v10M24 35v10M3 24h10M35 24h10M9.2 9.2l7.1 7.1M31.7 31.7l7.1 7.1M38.8 9.2l-7.1 7.1M16.3 31.7l-7.1 7.1"/><path d="M21 4h6l2 6-5 3-5-3zM44 21v6l-6 2-3-5 3-5zM27 44h-6l-2-6 5-3 5 3zM4 27v-6l6-2 3 5-3 5z"/></svg></span>`:type==='Search'?`<span class="testIcon searchIcon" role="img" aria-label="Search"><svg viewBox="0 0 56 40" focusable="false"><path d="M7 29L34 12l7 8-27 17z"/><path d="M34 12l7-5 8 10-8 5z"/><path d="M7 29l-3 5 7 4 3-5z"/><path d="M19 25l7 8"/><circle cx="46" cy="12" r="5"/></svg></span>`:'⚔';'''
new_icon = '''const testIcon=(type)=>type==='Sailing'?`<span class="testIcon sailingIcon" role="img" aria-label="Sailing"><svg viewBox="0 0 64 64" focusable="false"><circle class="helmRing" cx="32" cy="32" r="16"/><circle class="helmHub" cx="32" cy="32" r="5"/><path class="helmSpokes" d="M32 5v18M32 41v18M5 32h18M41 32h18M12.9 12.9l12.7 12.7M38.4 38.4l12.7 12.7M51.1 12.9L38.4 25.6M25.6 38.4L12.9 51.1"/><circle class="helmHandle" cx="32" cy="5" r="3.7"/><circle class="helmHandle" cx="32" cy="59" r="3.7"/><circle class="helmHandle" cx="5" cy="32" r="3.7"/><circle class="helmHandle" cx="59" cy="32" r="3.7"/><circle class="helmHandle" cx="12.9" cy="12.9" r="3.7"/><circle class="helmHandle" cx="51.1" cy="51.1" r="3.7"/><circle class="helmHandle" cx="51.1" cy="12.9" r="3.7"/><circle class="helmHandle" cx="12.9" cy="51.1" r="3.7"/></svg></span>`:type==='Search'?`<span class="testIcon searchIcon" role="img" aria-label="Search"><svg viewBox="0 0 72 48" focusable="false"><path class="binocularBody" d="M8 35l8-22h13l3 8h8l3-8h13l8 22"/><circle class="binocularLens" cx="20" cy="34" r="10"/><circle class="binocularLens" cx="52" cy="34" r="10"/><path class="binocularBridge" d="M29 24c4-3 10-3 14 0M16 13l3-5h8l2 5M43 13l2-5h8l3 5"/></svg></span>`:'⚔';'''
s = replace_once(s, old_icon, new_icon, 'maritime icons')
s = replace_once(s, "const resourceIcon=(type,label='')=>`<span class=\"resourceIcon ${type}\" aria-hidden=\"true\"></span>${label?`<span class=\"resourceLabel\">${esc(label)}</span>`:''}`;", "const resourceIcon=(type,label='')=>`<span class=\"resourceIcon ${type}\" aria-hidden=\"true\"></span>${label?`<span class=\"resourceLabel\">${esc(label)}</span>`:''}`;\nconst artFit=c=>{const a=c.art;return `<svg class=\"art\" role=\"img\" aria-label=\"${esc(c.name)}\" viewBox=\"${a.x} ${a.y} ${a.width} ${a.height}\" preserveAspectRatio=\"xMidYMid meet\"><image href=\"assets/v08-${a.sheet}.png\" width=\"${a.sourceWidth}\" height=\"${a.sourceHeight}\"/></svg>`};", 'fit artwork helper')
s = s.replace("quarters:'Ready up to 4 exhausted Crew'", "quarters:'Ready all exhausted Crew'")
s = replace_once(s, 'The Final Isle · v0.22', 'The Final Isle · v0.23', 'HUD version')
s = replace_once(s, "'All 81 cards · v0.22'", "'All 81 cards · v0.23'", 'card library version')

old_quarters = " if(l==='quarters')html=`<p>Ready up to 4 exhausted Crew.</p>${p.crew.filter(c=>c.exhausted).map(c=>`<label><input type=\"checkbox\" name=\"ready\" value=\"${c.uid}\">${esc(CARDS[c.id].name)}</label>`).join('')||'<p>No exhausted Crew.</p>'}${button('ready','Ready selected Crew')}`;"
new_quarters = " if(l==='quarters'){const tired=p.crew.filter(c=>c.exhausted);html=`<div class=\"quartersReadyAll\"><div class=\"quartersReadyIcon\">${crewGroupIcon()}</div><h3>${tired.length?tired.length+' exhausted Crew will rest':'All Crew are already Ready'}</h3><p>${tired.length?'Crew Quarters restores every exhausted Crew in one action. No selection is needed.':'You may finish this action without changing Crew status.'}</p>${tired.length?`<div class=\"quartersCrewPreview\">${tired.map(x=>{const c=CARDS[x.id];return `<article><div>${artFit(c)}</div><strong>${esc(c.name)}</strong>${crewStatusIcon(true)}</article>`}).join('')}</div>`:''}${button('ready',tired.length?'Rest & Ready All Crew':'Confirm Crew Quarters')}</div>`;}"
s = replace_once(s, old_quarters, new_quarters, 'Crew Quarters visual ready all')

old_prep = ''' modal('Prepare Expedition',`<div class="vSplit">${card(id)}<div class="vForm"><h3>Select ready Crew</h3>${p.crew.map(x=>`<label><input type="checkbox" name="crew" value="${x.uid}" ${x.exhausted?'disabled':'checked'}>${esc(CARDS[x.id].name)} · ${Object.entries(CARDS[x.id].stats).map(([t,v])=>icons[t]+v).join(' / ')}</label>`).join('')}<p>All ${p.treasures.length} owned Treasure passives apply.</p>${c.id==='F3'?`<p>Step 1 cost</p><select id="payment"><option value="gold">Pay 6 Gold</option><option value="treasure">Discard 1 Treasure</option></select><select id="sacrifice" aria-label="Treasure to discard">${p.treasures.map(id=>`<option value="${id}">${esc(CARDS[id].name)}</option>`).join('')}</select>`:''}${p.treasures.includes('T07')&&(c.test==='Combat'||c.steps?.some(st=>st.test==='Combat'))?'<label><input type="checkbox" id="powder"> Black Powder Horn: +1 Supply for +2 Combat</label>':''}<div id="previewCost" class="vSummary"></div>${button('launch','Pay & launch',`data-id="${id}"`)}${peek?button('peek','Look beneath this stack',`data-id="${id}"`):''}${button('resume','Back to Missions')}</div></div>`);'''
new_prep = ''' const prepCrew=p.crew.map(x=>{const crew=CARDS[x.id];return `<label class="prepCrewChoice ${x.exhausted?'disabled':''}"><input type="checkbox" name="crew" value="${x.uid}" ${x.exhausted?'disabled':'checked'}><span class="prepCrewCheck">✓</span><div class="prepCrewArt">${artFit(crew)}</div><strong>${esc(crew.name)}</strong><div class="prepCrewStats">${Object.entries(crew.stats).map(([t,v])=>`<span>${icons[t]}<b>${v}</b></span>`).join('')}</div>${crewStatusIcon(x.exhausted)}</label>`}).join('');
 const prepTreasure=p.treasures.length?p.treasures.map(tid=>{const tr=CARDS[tid];return `<article class="prepTreasureCard"><div>${artFit(tr)}</div><strong>${esc(tr.name)}</strong><small>${esc(tr.type||'Treasure')}</small></article>`}).join(''):'<p class="prepEmpty">No Treasure aboard.</p>';
 modal('Prepare Expedition',`<div class="prepExpeditionLayout"><section class="prepLoadout"><header><div><small>YOUR LOADOUT</small><h3>Select Ready Crew</h3></div><span>${crewGroupIcon()} ${p.crew.filter(x=>!x.exhausted).length}/${p.crew.length} Ready</span></header><div class="prepCrewGrid">${prepCrew}</div><h4>Treasure Passives</h4><div class="prepTreasureGrid">${prepTreasure}</div>${c.id==='F3'?`<div class="prepSpecial"><p>Step 1 cost</p><select id="payment"><option value="gold">Pay 6 Gold</option><option value="treasure">Discard 1 Treasure</option></select><select id="sacrifice" aria-label="Treasure to discard">${p.treasures.map(id=>`<option value="${id}">${esc(CARDS[id].name)}</option>`).join('')}</select></div>`:''}${p.treasures.includes('T07')&&(c.test==='Combat'||c.steps?.some(st=>st.test==='Combat'))?'<label class="prepPowder"><input type="checkbox" id="powder"> Black Powder Horn: +1 Supply for +2 Combat</label>':''}<div id="previewCost" class="vSummary prepSummary"></div><div class="prepActions">${button('launch','Pay & launch',`data-id="${id}"`)}${peek?button('peek','Look beneath this stack',`data-id="${id}"`):''}${button('resume','Back to Missions')}</div></section><aside class="prepMissionFocus"><header><small>MISSION</small><strong>${esc(c.name)}</strong></header>${card(id)}</aside></div>`);'''
s = replace_once(s, old_prep, new_prep, 'visual expedition preparation')

s = replace_once(
    s,
    " const miniCrew=expeditionCrew.map(x=>{const c=CARDS[x.id];return `<article class=\"expMiniCard crewMini\"><div class=\"expMiniArt\">${art(c)}</div><strong>${esc(c.name)}</strong><span>${icons[info.test]} ${info.test} <b>${c.stats[info.test]||0}</b></span>${crewStatusIcon(x.exhausted)}</article>`}).join('');",
    " const miniCrew=expeditionCrew.map(x=>{const c=CARDS[x.id];return `<article class=\"expMiniCard crewMini\"><div class=\"expMiniArt\">${artFit(c)}</div><strong>${esc(c.name)}</strong><span>${icons[info.test]} ${info.test} <b>${c.stats[info.test]||0}</b></span>${crewStatusIcon(x.exhausted)}</article>`}).join('');",
    'Expedition Crew artwork fit',
)
s = replace_once(
    s,
    " const miniTreasure=e.treasures.map(id=>{const c=CARDS[id];return `<article class=\"expMiniCard treasureMini\"><div class=\"expMiniArt\">${art(c)}</div><strong>${esc(c.name)}</strong><span>${esc(c.type||'Treasure')}</span></article>`}).join('')||'<div class=\"expEmpty\">No Treasure aboard</div>';",
    " const miniTreasure=e.treasures.map(id=>{const c=CARDS[id];return `<article class=\"expMiniCard treasureMini\"><div class=\"expMiniArt\">${artFit(c)}</div><strong>${esc(c.name)}</strong><span>${esc(c.type||'Treasure')}</span></article>`}).join('')||'<div class=\"expEmpty\">No Treasure aboard</div>';",
    'Expedition Treasure artwork fit',
)

s = replace_once(
    s,
    "if(name==='ready'||name==='refresh')a.ids=[...body.querySelectorAll(`[name=${name}]:checked`)].map(x=>x.value);",
    "if(name==='refresh')a.ids=[...body.querySelectorAll('[name=refresh]:checked')].map(x=>x.value);",
    'ready action needs no selection',
)
s = replace_once(
    s,
    "else if(l==='dock'){const crew=p.crew.filter(c=>!c.exhausted).map(c=>c.uid);",
    "else if(l==='quarters')a={type:'ready'};else if(l==='dock'){const crew=p.crew.filter(c=>!c.exhausted).map(c=>c.uid);",
    'AI uses Crew Quarters',
)
p.write_text(s)


# ---------------------------------------------------------------------------
# v0.23 styling.
# ---------------------------------------------------------------------------
p = Path('voyage-table.css')
s = p.read_text()
marker = '/* v0.23 — readable Expedition cards, ready-all quarters and refined maritime glyphs. */'
if marker not in s:
    s += r'''

/* v0.23 — readable Expedition cards, ready-all quarters and refined maritime glyphs. */
.testIcon{width:1.35em;height:1.35em;vertical-align:-.27em}.testIcon svg *{stroke-width:3.7}.sailingIcon{width:1.42em;height:1.42em}.sailingIcon .helmRing{stroke-width:4.1}.sailingIcon .helmHub,.sailingIcon .helmHandle{fill:currentColor!important;stroke:currentColor!important;stroke-width:1.5!important}.sailingIcon .helmSpokes{stroke-width:4.1!important}.searchIcon{width:1.55em;height:1.25em}.searchIcon .binocularLens{fill:none!important;stroke-width:4.4!important}.searchIcon .binocularBody,.searchIcon .binocularBridge{stroke-width:4.2!important}.physicalCard .vStats span{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px}.physicalCard .vStats span>.testIcon{width:31px!important;height:31px!important;margin-bottom:1px}.physicalCard .vStats span b{display:block}.missionTestType .testGlyph .testIcon{width:35px;height:35px}

.prepExpeditionLayout{display:grid;grid-template-columns:minmax(520px,1.25fr) minmax(300px,.75fr);gap:20px;align-items:start}.prepLoadout,.prepMissionFocus{border:2px solid #ae8748;border-radius:14px;background:linear-gradient(155deg,#103541,#071f29);box-shadow:inset 0 0 0 1px #f1d98a22,0 8px 22px #0007;padding:15px}.prepLoadout>header,.prepMissionFocus>header{display:flex;align-items:center;justify-content:space-between;gap:12px;padding-bottom:11px;margin-bottom:13px;border-bottom:1px solid #cba65c55}.prepLoadout>header small,.prepMissionFocus>header small{display:block;font:800 9px system-ui;letter-spacing:.14em;color:#ad9d7f}.prepLoadout>header h3{margin:2px 0 0;color:#f0d69a;font:bold 25px Georgia}.prepLoadout>header>span{display:flex;align-items:center;gap:5px;font:700 13px system-ui;color:#ead6a7}.prepCrewGrid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:11px}.prepCrewChoice{position:relative;display:grid;grid-template-columns:116px minmax(0,1fr);grid-template-rows:auto auto 1fr;gap:3px 10px;min-height:142px;border:2px solid #9b7845;border-radius:10px;background:#e8d39e;color:#281d13;overflow:hidden;cursor:pointer;box-shadow:0 4px 10px #0005;transition:.15s}.prepCrewChoice>input{position:absolute;opacity:0;pointer-events:none}.prepCrewChoice:has(input:checked){border-color:#75d7ea;box-shadow:0 0 0 3px #21758b88,0 5px 13px #0007}.prepCrewChoice.disabled{filter:grayscale(.72) brightness(.62);cursor:not-allowed}.prepCrewCheck{position:absolute;z-index:4;right:7px;top:7px;width:26px;height:26px;border-radius:50%;display:none;place-items:center;background:#1c6f55;color:#fff2bd;border:2px solid #d7b45f;font:900 15px system-ui}.prepCrewChoice:has(input:checked) .prepCrewCheck{display:grid}.prepCrewArt{grid-row:1/4;height:142px;background:#173843;border-right:2px solid #9b7845;overflow:hidden}.prepCrewArt .art{width:100%;height:100%}.prepCrewChoice>strong{align-self:end;padding:9px 35px 0 0;font:bold 15px/1.1 Georgia}.prepCrewStats{display:flex;gap:8px;align-items:center;padding-right:6px}.prepCrewStats span{display:inline-flex;align-items:center;gap:2px;font:700 11px system-ui}.prepCrewStats .testIcon{width:22px;height:22px}.prepCrewChoice>.crewStatusIcon{position:static;grid-column:2;align-self:start;justify-self:start;transform:scale(.58);transform-origin:left top;margin-top:-3px;margin-bottom:-18px}.prepLoadout h4{margin:17px 0 8px;color:#e8d09a;font:800 11px system-ui;letter-spacing:.12em;text-transform:uppercase}.prepTreasureGrid{display:flex;gap:9px;flex-wrap:wrap}.prepTreasureCard{width:142px;border:2px solid #967440;border-radius:9px;overflow:hidden;background:#d9c38d;color:#2a1f15;box-shadow:0 4px 9px #0005}.prepTreasureCard>div{height:86px;background:#173641;overflow:hidden}.prepTreasureCard .art{width:100%;height:100%}.prepTreasureCard strong,.prepTreasureCard small{display:block;text-align:center;padding:5px 5px 0}.prepTreasureCard strong{font:bold 12px Georgia}.prepTreasureCard small{padding:3px 5px 7px;font:10px system-ui}.prepEmpty{padding:13px;border:1px dashed #b89a665c;border-radius:8px;color:#ad9f82}.prepSummary{margin:15px 0 9px;padding:11px 13px;border:1px solid #b99554;border-radius:10px;background:#0a2630;color:#ffe4a9;font:700 14px system-ui}.prepActions{display:flex;gap:8px;flex-wrap:wrap}.prepActions button{margin:0!important}.prepMissionFocus{position:sticky;top:0}.prepMissionFocus>header{flex-direction:column;align-items:flex-start}.prepMissionFocus>header strong{color:#f0d69a;font:bold 19px Georgia}.prepMissionFocus .vCard{max-width:330px}.prepSpecial,.prepPowder{display:block;margin-top:12px;padding:10px;border:1px solid #9a7b4d;border-radius:8px;background:#0a2530}.prepSpecial p{margin:0 0 7px}.prepSpecial select{margin-right:7px}.prepPowder{color:#ead7ab}.prepPowder input{margin-right:7px}

.expeditionTable{grid-template-columns:minmax(500px,1.3fr) minmax(330px,.7fr);gap:20px}.expMiniGrid{display:flex;flex-wrap:wrap;gap:12px;align-items:stretch}.expMiniCard{flex:0 0 176px;min-height:246px;display:flex;flex-direction:column}.expMiniArt{height:158px;background:linear-gradient(#173a47,#0f2c36);display:grid;place-items:center;padding:3px}.expMiniArt .art{width:100%;height:100%;max-width:100%;max-height:100%}.expMiniCard>strong{font-size:13px;min-height:38px;padding-top:8px}.expMiniCard>span:not(.crewStatusIcon){margin-top:auto;padding-bottom:9px}.treasureRow .expMiniCard{flex-basis:166px;min-height:225px}.treasureRow .expMiniArt{height:144px}.expLoadout{min-width:0}.expMissionCard{min-width:0}.expMissionCard .vCard{max-width:340px}.expLoadout h4{margin-top:15px}.expEmpty{flex:1 1 100%}

.quartersReadyAll{text-align:center;max-width:920px;margin:0 auto;padding:6px 4px 2px}.quartersReadyIcon{width:76px;height:58px;margin:0 auto 7px;display:grid;place-items:center;border:2px solid #b68d50;border-radius:50%;background:#163d49}.quartersReadyIcon .crewGroupIcon{width:58px;height:43px}.quartersReadyAll h3{margin:6px 0;color:#f0d69b;font:bold 25px Georgia}.quartersReadyAll>p{margin:5px auto 14px;max-width:650px;color:#d9cdb2}.quartersCrewPreview{display:flex;justify-content:center;gap:11px;flex-wrap:wrap;margin:13px 0 17px}.quartersCrewPreview article{position:relative;width:150px;overflow:hidden;border:2px solid #a47d45;border-radius:10px;background:#e4cf99;color:#281d13;box-shadow:0 5px 10px #0006}.quartersCrewPreview article>div:first-child{height:105px;background:#173743;overflow:hidden}.quartersCrewPreview article .art{width:100%;height:100%}.quartersCrewPreview article>strong{display:block;padding:7px 5px 9px;font:bold 12px Georgia}.quartersCrewPreview article>.crewStatusIcon{position:absolute;right:5px;top:5px;transform:scale(.52);transform-origin:right top}.quartersReadyAll>[data-action=ready]{min-width:230px;background:linear-gradient(#277154,#174936)!important;border-color:#8edca5!important;color:#f2ffe9!important;font-weight:800!important}

@media(max-width:1000px){.prepExpeditionLayout,.expeditionTable{grid-template-columns:1fr}.prepMissionFocus,.expMissionCard{order:-1;position:static}.prepMissionFocus .vCard,.expMissionCard .vCard{max-width:310px}.prepCrewGrid{grid-template-columns:1fr}.expMiniCard{flex-basis:160px}.expMiniArt{height:145px}}
@media(max-width:620px){.prepCrewChoice{grid-template-columns:96px minmax(0,1fr)}.prepCrewArt{height:130px}.prepTreasureCard{width:128px}.expMiniCard{flex-basis:calc(50% - 6px);min-width:0}.expMiniArt{height:130px}.treasureRow .expMiniCard{flex-basis:calc(50% - 6px)}}
'''
p.write_text(s)


# ---------------------------------------------------------------------------
# Visible release labels.
# ---------------------------------------------------------------------------
p = Path('menu.js')
s = p.read_text()
s = replace_once(s, '      version:"0.22",', '      version:"0.23",', 'setup version')
p.write_text(s)

p = Path('index.html')
s = p.read_text()
s = s.replace('v0.22 Test', 'v0.23 Test').replace('v0.22 TEST', 'v0.23 TEST')
if 'v0.23 Test' not in s and 'v0.23 TEST' not in s:
    raise SystemExit('index v0.23 marker missing')
p.write_text(s)

checks = {
    'engine-v014.mjs': ["a.type==='ready'", 'for(const c of p.crew)c.exhausted=false'],
    'voyage-v014.js': ['The Final Isle · v0.23', 'prepExpeditionLayout', 'quartersReadyAll', 'artFit', 'binocularLens', 'helmHandle', "else if(l==='quarters')a={type:'ready'}"],
    'voyage-table.css': ['v0.23 — readable Expedition cards', '.prepCrewChoice', '.quartersReadyAll', '.binocularLens', '.helmHandle'],
    'menu.js': ['version:"0.23"'],
}
for file, markers in checks.items():
    text = Path(file).read_text()
    for m in markers:
        if m not in text:
            raise SystemExit(f'{file}: missing {m}')
print('v0.23 patch markers verified')
