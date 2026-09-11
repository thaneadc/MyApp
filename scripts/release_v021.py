from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected 1 match, found {count}")
    return text.replace(old, new, 1)


# ---------------------------------------------------------------------------
# Engine: expedition Crew are committed/exhausted until Crew Quarters.
# ---------------------------------------------------------------------------
p = Path('engine-v014.mjs')
s = p.read_text()
s = replace_once(
    s,
    "const selected=(p,e)=>p.crew.filter(c=>e.crew.includes(c.uid)&&!c.exhausted);",
    "const selected=(p,e)=>p.crew.filter(c=>e.crew.includes(c.uid));",
    'expedition crew remain selectable after exhaustion',
)
s = replace_once(
    s,
    "const cost=supplyCost(p,z,exp.treasures,a.crew)+(a.powder?1:0);must(p.gold>=gold&&p.supply>=cost,'Not enough Gold or Supply');p.gold-=gold;p.supply-=cost;exp.paid=cost;p.blessing=null;s.exp=exp;return s;",
    "const cost=supplyCost(p,z,exp.treasures,a.crew)+(a.powder?1:0);must(p.gold>=gold&&p.supply>=cost,'Not enough Gold or Supply');p.gold-=gold;p.supply-=cost;for(const x of p.crew)if(a.crew.includes(x.uid))x.exhausted=true;exp.paid=cost;p.blessing=null;s.exp=exp;return s;",
    'exhaust participating crew on launch',
)
p.write_text(s)


# ---------------------------------------------------------------------------
# Voyage UI: Ready/Total HUD, visible Crew state, cinematic Expedition table.
# ---------------------------------------------------------------------------
p = Path('voyage-v014.js')
s = p.read_text()

needle = "const crewGroupIcon=(veteran=false)=>`<span class=\"crewGroupIcon ${veteran?'veteran':''}\" aria-hidden=\"true\"><svg viewBox=\"0 0 48 34\" focusable=\"false\"><ellipse class=\"crewOval\" cx=\"24\" cy=\"18\" rx=\"22\" ry=\"15\"/><circle cx=\"24\" cy=\"10\" r=\"5\"/><circle cx=\"13\" cy=\"13\" r=\"4\"/><circle cx=\"35\" cy=\"13\" r=\"4\"/><path d=\"M14 27c.8-7 4.2-10.5 10-10.5S33.2 20 34 27z\"/><path d=\"M5.5 25c.5-5.3 3.1-8 7.4-8 3 0 5.2 1.4 6.4 4-1.3 1.4-2.1 3.4-2.5 6H5.5zM42.5 25c-.5-5.3-3.1-8-7.4-8-3 0-5.2 1.4-6.4 4 1.3 1.4 2.1 3.4 2.5 6h11.3z\"/>${veteran?'<path class=\"crewStar\" d=\"M24 2.5l1.5 3 3.3.5-2.4 2.3.6 3.3-3-1.6-3 1.6.6-3.3L19.2 6l3.3-.5z\"/>':''}</svg></span>`;"
addition = needle + "\nconst crewStatusIcon=exhausted=>`<span class=\"crewStatusIcon ${exhausted?'exhausted':'ready'}\" role=\"img\" aria-label=\"${exhausted?'Exhausted Crew':'Ready Crew'}\" title=\"${exhausted?'Exhausted — visit Crew Quarters to ready':'Ready for an Expedition'}\"><svg viewBox=\"0 0 64 64\" focusable=\"false\"><circle class=\"statusDisc\" cx=\"32\" cy=\"32\" r=\"27\"/>${exhausted?'<path class=\"statusMoon\" d=\"M42 18c-10 2-16 12-13 22 2 7 8 12 15 13-4 3-9 5-14 4-13-2-21-14-19-27 2-12 13-20 25-19 2 0 4 0 6 1z\"/><path class=\"statusZ\" d=\"M38 15h13l-12 12h13\"/>':'<path class=\"statusCheck\" d=\"M18 33l9 9 20-22\"/>'}</svg><small>${exhausted?'EXHAUSTED':'READY'}</small></span>`;"
s = replace_once(s, needle, addition, 'crew status icon helper')

s = replace_once(
    s,
    '<span class="crewCount">${crewGroupIcon()}<b>${p.crew.length}/4</b></span>',
    '<span class="crewCount" title="Ready Crew / Total Crew" aria-label="${p.crew.filter(c=>!c.exhausted).length} Ready Crew of ${p.crew.length} total">${crewGroupIcon()}<b>${p.crew.filter(c=>!c.exhausted).length}/${p.crew.length}</b><small>READY</small></span>',
    'ready crew over total HUD',
)

s = replace_once(s, 'The Final Isle · v0.20', 'The Final Isle · v0.21', 'HUD version')

render_anchor = "function render(){root.hidden=false;document.querySelector('#app').hidden=true;const p=current(state);"
s = replace_once(
    s,
    render_anchor,
    render_anchor + "window.dispatchEvent(new CustomEvent('captainsdash:music-mode',{detail:{mode:unlocked(state,4)?'adrenaline':'adventure'}}));",
    'dynamic music switch',
)

old_status = "p.crew.map(c=>card(c.id,'<p>'+(c.exhausted?'Exhausted':'Ready')+'</p>')).join('')"
s = replace_once(s, old_status, "p.crew.map(c=>card(c.id,crewStatusIcon(c.exhausted))).join('')", 'crew status cards')

menu_old = "if(name==='menu'){clearTimeout(aiTimer);dlg.close();root.hidden=true;document.querySelector('#app').hidden=false;return}"
menu_new = "if(name==='menu'){clearTimeout(aiTimer);window.dispatchEvent(new CustomEvent('captainsdash:music-mode',{detail:{mode:'adventure'}}));dlg.close();root.hidden=true;document.querySelector('#app').hidden=false;return}"
s = replace_once(s, menu_old, menu_new, 'menu adventure music')

start = s.index('function showExp(){')
end = s.index('function showGuide(){', start)
new_show_exp = r'''function showExp(){
 body.onchange=null;
 const e=state.exp,p=current(state),mission=CARDS[e.mission],info=testInfo(e),diceCount=mission.zone||3;
 const expeditionCrew=p.crew.filter(c=>e.crew.includes(c.uid));
 const base=baseScore(p,e);
 const resolved=['loss','treasure','result'].includes(e.phase);
 const live=e.phase==='ready'?base:(resolved?e.total:totalScore(p,e));
 const skull=e.dice?.includes('SKULL');
 const verdict=e.phase==='ready'?'waiting':skull?'fail':live>=info.target?'pass':'pending';
 const verdictText=e.phase==='ready'?'READY TO ROLL':skull?'SKULL — MISSION FAILS':live>=info.target?'TARGET REACHED':`${Math.max(0,info.target-live)} MORE NEEDED`;
 const miniCrew=expeditionCrew.map(x=>{const c=CARDS[x.id];return `<article class="expMiniCard crewMini"><div class="expMiniArt">${art(c)}</div><strong>${esc(c.name)}</strong><span>${icons[info.test]} ${info.test} <b>${c.stats[info.test]||0}</b></span>${crewStatusIcon(x.exhausted)}</article>`}).join('');
 const miniTreasure=e.treasures.map(id=>{const c=CARDS[id];return `<article class="expMiniCard treasureMini"><div class="expMiniArt">${art(c)}</div><strong>${esc(c.name)}</strong><span>${esc(c.type||'Treasure')}</span></article>`}).join('')||'<div class="expEmpty">No Treasure aboard</div>';
 const diceHtml=e.phase==='ready'?Array.from({length:diceCount},()=>'<div class="die dieWaiting">?</div>').join(''):e.dice.map(d=>`<div class="die ${d==='SKULL'?'skullDie':d==='GOLD'?'goldDie':''}">${d==='SKULL'?'☠':d==='GOLD'?resourceIcon('gold'):d}</div>`).join('');
 let actions='';
 if(e.phase==='ready')actions=`<div class="expRollAction">${button('roll',`Roll ${diceCount} dice`,'class="expRollBtn"')}</div>`;
 else {
  if(e.phase==='dice')actions+=`<div class="expControls">${controls(state).map(o=>o.id==='fortune'?e.dice.map((d,i)=>d==='SKULL'?'':button('control','Fortune · reroll die '+(i+1),`data-id="fortune" data-index="${i}"`)).join(''):button('control',esc(o.label),`data-id="${o.id}"`)).join('')}${button('resolve','Resolve Test','class="resolveMissionBtn"')}</div>`;
  if(e.phase==='loss'){
   actions+='<section class="expLoss"><h3>THE SEA BITES BACK!</h3><p>Choose one participating Crew card to discard, or use protection.</p><div class="expProtection">';
   if(p.crew.some(c=>c.id==='C12'&&e.crew.includes(c.uid)))actions+=button('protect','Surgeon · prevent Crew loss','data-id="surgeon"');
   if(e.treasures.includes('T19'))actions+=button('protect','Discard Captain’s Medallion','data-id="medallion"');
   actions+='</div><div class="vGrid expDiscardGrid">'+p.crew.filter(c=>e.crew.includes(c.uid)).map(c=>card(c.id,crewStatusIcon(true)+button('loss','Discard this Crew',`data-id="${c.uid}" class="discardCrewBtn"`))).join('')+'</div></section>';
  }
  if(e.phase==='treasure')actions+='<section class="expTreasureChoice"><h3>Choose the Treasure to keep</h3><div class="vGrid">'+e.choices.map(id=>card(id,button('keepTreasure','Keep',`data-id="${id}"`))).join('')+'</div></section>';
  if(e.phase==='result')actions+=`<section class="expFinalResult ${e.success?'success':'failure'}"><h3>${e.success?'MISSION CONQUERED!':'THE SEA BITES BACK!'}</h3><p>${e.success?lines(mission.text||'Victory'):'Crew loss resolved. Supply stays spent.'}</p>${button('finish','Return to Pirate Haven')}</section>`;
 }
 const html=`<div class="expTopline"><span>${esc(mission.name)}${mission.kind==='final'?' · Step '+(e.step+1)+' of 2':''}</span><span>${resourceIcon('supply')} ${e.paid} Supply paid</span></div>
 <div class="expeditionTable">
  <section class="expLoadout"><header><h3>Your Expedition</h3><span>${crewGroupIcon()} ${expeditionCrew.length} Crew</span></header><h4>Crew</h4><div class="expMiniGrid">${miniCrew}</div><h4>Treasure</h4><div class="expMiniGrid treasureRow">${miniTreasure}</div></section>
  <section class="expMissionCard"><header><span>${icons[info.test]} ${esc(info.test)} Test</span><b>Target ${info.target}</b></header>${card(e.mission)}</section>
 </div>
 <section class="expScoreboard ${verdict}"><div class="scoreBlock"><small>CREW + PASSIVES</small><strong>${base}</strong></div><div class="scoreVs"><span>VS</span><b>${verdictText}</b></div><div class="scoreBlock target"><small>MISSION TARGET</small><strong>${info.target}</strong></div></section>
 <section class="expDiceTray"><header><span>${e.phase==='ready'?'Dice waiting':'Dice result'}</span>${e.phase==='ready'?'':`<b>Total ${live} / ${info.target}</b>`}</header><div class="dice">${diceHtml}</div>${skull?'<p class="skullWarning">☠ A Skull causes immediate Mission failure.</p>':''}</section>${actions}`;
 modal('Expedition',html,true);
}
'''
s = s[:start] + new_show_exp + s[end:]
p.write_text(s)


# ---------------------------------------------------------------------------
# Music controller: Adventure v2 by default, Adrenaline v2 at Final Isle.
# ---------------------------------------------------------------------------
p = Path('menu.js')
s = p.read_text()
old_audio = '''  const soundtrack=new Audio();
  soundtrack.id='pirateMusic';
  soundtrack.loop=true;
  soundtrack.preload='metadata';
  soundtrack.src=soundtrack.canPlayType('audio/ogg; codecs="vorbis"')?'assets/pirate-theme.ogg':'assets/pirate-theme.mp3';
  document.body.appendChild(soundtrack);
  let musicStarted=false;
'''
new_audio = '''  const MUSIC_TRACKS={adventure:'assets/captains-dash-adventure-v2.ogg',adrenaline:'assets/captains-dash-adrenaline-v2.ogg'};
  const soundtrack=new Audio();
  soundtrack.id='pirateMusic';
  soundtrack.loop=true;
  soundtrack.preload='auto';
  soundtrack.src=MUSIC_TRACKS.adventure;
  document.body.appendChild(soundtrack);
  let musicStarted=false,musicMode='adventure';
  function setMusicMode(mode='adventure') {
    mode=mode==='adrenaline'?'adrenaline':'adventure';
    if(mode===musicMode&&soundtrack.src.includes(MUSIC_TRACKS[mode]))return;
    const shouldPlay=musicEnabled&&settings.music>0&&(musicStarted||!soundtrack.paused);
    musicMode=mode;
    soundtrack.pause();
    soundtrack.src=MUSIC_TRACKS[mode];
    soundtrack.loop=true;
    soundtrack.currentTime=0;
    soundtrack.volume=Math.max(0,Math.min(1,settings.music/100));
    if(shouldPlay){musicStarted=true;soundtrack.play().catch(()=>{});}
  }
'''
s = replace_once(s, old_audio, new_audio, 'soundtrack v2 controller')
s = replace_once(
    s,
    "  window.addEventListener('captainsdash:startgame',()=>toggleAmbient(musicEnabled));",
    "  window.addEventListener('captainsdash:music-mode',ev=>setMusicMode(ev.detail?.mode));\n  window.addEventListener('captainsdash:startgame',()=>{setMusicMode('adventure');toggleAmbient(musicEnabled)});",
    'music mode event',
)
s = replace_once(s, '      version:"0.20",', '      version:"0.21",', 'setup release version')
p.write_text(s)


# ---------------------------------------------------------------------------
# Card/Crew UI styling and Expedition presentation.
# ---------------------------------------------------------------------------
p = Path('voyage-table.css')
s = p.read_text()
marker='/* v0.21 — Crew fatigue, visual status and cinematic Expedition table. */'
if marker not in s:
    s += r'''

/* v0.21 — Crew fatigue, visual status and cinematic Expedition table. */
.playerNumbers .crewCount{position:relative;gap:4px}.playerNumbers .crewCount>small{font:700 7px/1 system-ui;letter-spacing:.08em;opacity:.72;margin-left:1px}.playerNumbers .crewCount .crewGroupIcon{width:30px;height:23px}
.crewStatusIcon{display:inline-grid;grid-template-columns:48px auto;grid-template-rows:48px;align-items:center;justify-content:center;gap:7px;min-height:58px;padding:5px 10px;border:2px solid currentColor;border-radius:12px;font:800 11px/1 system-ui;letter-spacing:.08em;text-align:left;box-shadow:inset 0 0 12px #0004,0 3px 8px #0004}
.crewStatusIcon svg{width:48px;height:48px;grid-row:1;overflow:visible}.crewStatusIcon small{font:800 11px/1 system-ui;letter-spacing:.09em}.crewStatusIcon .statusDisc{stroke:currentColor;stroke-width:3;fill:#102b34}.crewStatusIcon.ready{color:#8ff0b0;background:#123c2e}.crewStatusIcon.ready .statusCheck{fill:none;stroke:#d9ffe4;stroke-width:7;stroke-linecap:round;stroke-linejoin:round}.crewStatusIcon.exhausted{color:#ffc478;background:#4a291c}.crewStatusIcon.exhausted .statusMoon{fill:#ffd59b}.crewStatusIcon.exhausted .statusZ{fill:none;stroke:#fff0c9;stroke-width:4;stroke-linecap:round;stroke-linejoin:round}
.cardControls:has(.crewStatusIcon){display:flex;align-items:center;justify-content:center;gap:8px;min-height:70px;background:linear-gradient(#0b2832,#071d26);padding:7px}.cardControls:has(.crewStatusIcon) .crewStatusIcon{flex:0 0 auto}.cardControls:has(.crewStatusIcon) button{align-self:center}
.expTopline{display:flex;justify-content:space-between;align-items:center;gap:14px;margin:0 0 14px;padding:9px 14px;border:1px solid #d1a95766;border-radius:9px;background:#091f28;color:#ead7a8;font:700 13px system-ui;letter-spacing:.02em}.expTopline .resourceIcon{vertical-align:middle}
.expeditionTable{display:grid;grid-template-columns:minmax(0,1.18fr) minmax(300px,.82fr);gap:18px;align-items:start}.expLoadout,.expMissionCard{border:2px solid #b78b48;border-radius:14px;background:linear-gradient(155deg,#103442,#071f29);box-shadow:inset 0 0 0 1px #f1d98a22,0 8px 22px #0007;padding:14px}.expLoadout>header,.expMissionCard>header{display:flex;justify-content:space-between;align-items:center;gap:10px;margin:-3px -2px 12px;padding:0 3px 10px;border-bottom:1px solid #d7b26355}.expLoadout>header h3{margin:0;color:#f2d794;font-size:24px}.expLoadout>header>span,.expMissionCard>header{color:#ecd9ac;font:700 13px system-ui}.expLoadout>header .crewGroupIcon{width:34px;height:25px;vertical-align:middle}.expLoadout h4{margin:11px 0 7px;color:#e9d29a;font:700 13px system-ui;text-transform:uppercase;letter-spacing:.09em}
.expMiniGrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(116px,1fr));gap:9px}.expMiniCard{position:relative;min-width:0;border:2px solid #b88e50;border-radius:10px;background:#e8d39e;color:#281d13;overflow:hidden;box-shadow:0 5px 12px #0006}.expMiniArt{height:86px;border-bottom:2px solid #94703d;overflow:hidden;background:#163541}.expMiniArt .art{width:100%;height:100%;display:block}.expMiniCard>strong{display:block;padding:6px 5px 2px;text-align:center;font:700 12px/1.15 Georgia;min-height:34px}.expMiniCard>span:not(.crewStatusIcon){display:block;text-align:center;padding:2px 5px 7px;font:700 11px system-ui}.expMiniCard .crewStatusIcon{position:absolute;right:4px;top:4px;display:grid;grid-template-columns:25px;grid-template-rows:25px;width:29px;height:29px;min-height:0;padding:1px;border-radius:50%;overflow:hidden}.expMiniCard .crewStatusIcon svg{width:25px;height:25px}.expMiniCard .crewStatusIcon small{display:none}.expEmpty{grid-column:1/-1;padding:16px;border:1px dashed #c1a26b66;border-radius:8px;color:#aa9b7e;text-align:center;font:italic 13px Georgia}.treasureRow .expMiniCard{background:#d6c18d}
.expMissionCard>header{font-size:15px}.expMissionCard>header b{color:#fff0b6;font-size:18px}.expMissionCard .vCard{width:min(100%,360px);margin:0 auto;max-height:none}.expMissionCard .vCard .cardControls{display:none}
.expScoreboard{display:grid;grid-template-columns:minmax(135px,1fr) minmax(180px,.9fr) minmax(135px,1fr);align-items:stretch;gap:9px;margin:17px 0 11px}.scoreBlock,.scoreVs{border:2px solid #9d7944;border-radius:12px;background:linear-gradient(#123846,#092630);display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:86px;padding:8px;color:#ead5a1;box-shadow:inset 0 0 0 1px #ecd58b1e}.scoreBlock small{font:700 10px system-ui;letter-spacing:.1em}.scoreBlock strong{font:700 42px/1 Georgia;color:#fff0b7}.scoreVs span{font:700 11px system-ui;letter-spacing:.12em;color:#b7a98a}.scoreVs b{margin-top:5px;font:800 13px/1.25 system-ui;text-align:center;letter-spacing:.04em}.expScoreboard.pass .scoreVs{border-color:#65cf8d;background:#113d2c;color:#b9ffd0;box-shadow:0 0 18px #48d87933}.expScoreboard.fail .scoreVs{border-color:#e86a5d;background:#4b211e;color:#ffd0ca;box-shadow:0 0 18px #e1463b33}.expScoreboard.pending .scoreVs{border-color:#dfb75c;background:#463719;color:#ffe7a7}.expScoreboard.waiting .scoreVs{color:#d7c9a9}
.expDiceTray{border:2px solid #a8844c;border-radius:14px;background:radial-gradient(circle at 50% 20%,#16404d,#071d26 72%);padding:11px 14px 13px;box-shadow:inset 0 0 20px #0007}.expDiceTray>header{display:flex;justify-content:space-between;align-items:center;color:#e7d4aa;font:700 12px system-ui;text-transform:uppercase;letter-spacing:.08em}.expDiceTray .dice{display:flex;justify-content:center;gap:12px;flex-wrap:wrap;margin:10px 0 2px}.expDiceTray .die{width:66px;height:66px;font-size:30px;border-width:3px;box-shadow:0 5px 14px #0008}.expDiceTray .dieWaiting{display:grid;place-items:center;border-style:dashed;color:#e8d6ad88;background:#102c35;font:700 30px Georgia}.expDiceTray .skullDie{border-color:#e05a4f;box-shadow:0 0 18px #e4453977}.expDiceTray .goldDie{border-color:#eac65e;box-shadow:0 0 16px #e9bd4e55}.skullWarning{text-align:center;color:#ffb3a9;font:700 12px system-ui;margin:8px 0 0}
.expRollAction,.expControls{display:flex;justify-content:center;gap:9px;flex-wrap:wrap;margin-top:13px}.expRollBtn,.resolveMissionBtn{min-width:220px;min-height:54px;border:2px solid #e0b65e!important;background:linear-gradient(#9d392d,#69231f)!important;color:#fff5d4!important;font-weight:800!important;font-size:18px!important;box-shadow:0 0 20px #de9d3d33,0 5px 10px #0006!important}.expLoss,.expTreasureChoice,.expFinalResult{margin-top:16px;padding:14px;border:2px solid #a98249;border-radius:12px;background:#0a2631}.expLoss h3,.expFinalResult h3{margin:0 0 6px;color:#ffd1c9}.expProtection{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0 14px}.expDiscardGrid .vCard{max-width:260px}.discardCrewBtn{background:#7b2924!important;color:#fff!important;border-color:#d66f62!important}.expFinalResult.success{border-color:#63bd80;background:#123929}.expFinalResult.success h3{color:#b9ffd0}.expFinalResult.failure{border-color:#c75a4e;background:#3d211f}
@media(max-width:900px){.expeditionTable{grid-template-columns:1fr}.expMissionCard{order:-1}.expMissionCard .vCard{max-width:310px}.expScoreboard{grid-template-columns:1fr auto 1fr}.scoreBlock strong{font-size:34px}.expMiniGrid{grid-template-columns:repeat(2,minmax(0,1fr))}}
'''
p.write_text(s)


# ---------------------------------------------------------------------------
# Release labels.
# ---------------------------------------------------------------------------
p = Path('index.html')
s = p.read_text().replace('v0.20 Test','v0.21 Test').replace('v0.20 TEST','v0.21 TEST')
p.write_text(s)

# Update the existing rule regression to the new fatigue rule for Surgeon cases.
p = Path('tests/rules-v014.mjs')
s = p.read_text()
s = replace_once(
    s,
    "e=expedition('Z1-01',['C12']);e=act(e,{type:'roll'},()=>0);e=act(e,{type:'loss',prevent:'surgeon'});eq(current(e).crew.length,1);eq(current(e).crew[0].exhausted,false);",
    "e=expedition('Z1-01',['C12']);eq(current(e).crew[0].exhausted,true);e=act(e,{type:'roll'},()=>0);e=act(e,{type:'loss',prevent:'surgeon'});eq(current(e).crew.length,1);eq(current(e).crew[0].exhausted,true);",
    'surgeon fatigue assertion',
)
p.write_text(s)

# Static sanity markers.
checks={
 'engine-v014.mjs':['for(const x of p.crew)if(a.crew.includes(x.uid))x.exhausted=true','const selected=(p,e)=>p.crew.filter(c=>e.crew.includes(c.uid));'],
 'voyage-v014.js':['The Final Isle · v0.21','crewStatusIcon','Ready Crew / Total Crew','expeditionTable','expDiscardGrid','captainsdash:music-mode'],
 'menu.js':['captains-dash-adventure-v2.ogg','captains-dash-adrenaline-v2.ogg','version:"0.21"'],
 'voyage-table.css':['v0.21 — Crew fatigue','expScoreboard','crewStatusIcon'],
 'index.html':['v0.21 Test'],
}
for file,markers in checks.items():
    text=Path(file).read_text()
    for marker in markers:
        if marker not in text:
            raise SystemExit(f'{file}: missing {marker}')
print('v0.21 patch markers verified')
