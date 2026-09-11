from pathlib import Path


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected 1 match, found {count}")
    return text.replace(old, new, 1)


# ---------------------------------------------------------------------------
# Engine: persist selected portrait and make Crew Quarters rest explicit/logged.
# ---------------------------------------------------------------------------
p = Path('engine-v014.mjs')
s = p.read_text()
s = replace_once(
    s,
    "s.players=Array.from({length:Math.max(2,Math.min(4,setup.players||2))},(_,i)=>({name:setup.names?.[i]||'Player '+(i+1),gold:i?3:2,supply:i>=2?3:2,crew:[instance(s,'C01')],treasures:[],blessing:null}));",
    "s.players=Array.from({length:Math.max(2,Math.min(4,setup.players||2))},(_,i)=>({name:setup.names?.[i]||'Player '+(i+1),portrait:setup.portraits?.[i]||null,gold:i?3:2,supply:i>=2?3:2,crew:[instance(s,'C01')],treasures:[],blessing:null}));",
    'persist captain portraits',
)
s = replace_once(
    s,
    " else if(a.type==='ready'){must(loc==='quarters','Use Crew Quarters');for(const c of p.crew)c.exhausted=false}",
    " else if(a.type==='ready'){must(loc==='quarters','Use Crew Quarters');const rested=p.crew.filter(c=>c.exhausted).length;for(const c of p.crew)c.exhausted=false;log(s,p.name+' rested at Crew Quarters — '+rested+' Crew Ready')}",
    'Crew Quarters ready-all logging',
)
p.write_text(s)


# ---------------------------------------------------------------------------
# Menu: 10 portrait choices total (4 existing + 6 alternates), click to cycle.
# ---------------------------------------------------------------------------
p = Path('menu.js')
s = p.read_text()
s = replace_once(
    s,
    '  const captainNames=["Captain Anne","Captain Black","Captain Morgan","Captain Silver"];\n  const colors=["#c9302c","#1f76b4","#21924a","#d7aa1d"];',
    '  const captainNames=["Captain Anne","Captain Black","Captain Morgan","Captain Silver"];\n  const defaultPortraits=["014ea26d527fb00d.jpg","5d6137ac745946c3.jpg","c70de609c89d8c4c.jpg","724be8a80f197bb0.jpg"];\n  const portraitOptions=[...defaultPortraits,"captain-alt-01.svg","captain-alt-02.svg","captain-alt-03.svg","captain-alt-04.svg","captain-alt-05.svg","captain-alt-06.svg"];\n  let selectedPortraits=[...defaultPortraits];\n  const colors=["#c9302c","#1f76b4","#21924a","#d7aa1d"];',
    'portrait option arrays',
)

s = replace_once(
    s,
    '  function syncModeNames() {',
    '''  function renderCaptainPortraits() {
    document.querySelectorAll(".captain").forEach((c,i)=>{
      const img=c.querySelector("img");
      if(img)img.src=`assets/${selectedPortraits[i]||defaultPortraits[i]}`;
      c.dataset.portrait=selectedPortraits[i]||defaultPortraits[i];
      c.setAttribute("aria-label",`${captainNames[i]} portrait. Tap to change portrait.`);
      c.tabIndex=i<count?0:-1;
    });
  }
  function applyPortraits(values) {
    if(Array.isArray(values))for(let i=0;i<4;i++)if(values[i]&&portraitOptions.includes(values[i]))selectedPortraits[i]=values[i];
    renderCaptainPortraits();
  }
  function cyclePortrait(i,dir=1) {
    if(i>=count)return;
    const current=portraitOptions.indexOf(selectedPortraits[i]);
    selectedPortraits[i]=portraitOptions[(Math.max(0,current)+dir+portraitOptions.length)%portraitOptions.length];
    renderCaptainPortraits();
    clickSfx(560,.06);
  }
  document.querySelectorAll(".captain").forEach((c,i)=>{
    c.setAttribute("role","button");
    c.addEventListener("click",()=>cyclePortrait(i,1));
    c.addEventListener("keydown",e=>{if((e.key==="Enter"||e.key===" ")&&i<count){e.preventDefault();cyclePortrait(i,e.shiftKey?-1:1)}});
  });

  function syncModeNames() {''',
    'portrait controls',
)

s = replace_once(
    s,
    '    renderNames(values);\n    syncModeNames();\n  }',
    '    renderNames(values);\n    syncModeNames();\n    renderCaptainPortraits();\n  }',
    'render portraits with player count',
)
s = replace_once(s, '  renderNames();\n  syncModeNames();', '  renderNames();\n  syncModeNames();\n  renderCaptainPortraits();', 'initial portrait render')

s = replace_once(
    s,
    '      version:"0.24",\n      players:count,\n      names:[...document.querySelectorAll("#names input")].map(x=>x.value.trim()||"Captain"),\n      captains:captainNames.slice(0,count),\n      mode:gameMode,',
    '      version:"0.25",\n      players:count,\n      names:[...document.querySelectorAll("#names input")].map(x=>x.value.trim()||"Captain"),\n      captains:captainNames.slice(0,count),\n      portraits:selectedPortraits.slice(0,count),\n      mode:gameMode,',
    'setup portrait persistence',
)

s = replace_once(
    s,
    'if(full&&full.players?.length){const sv={players:full.players.length,names:full.players.map(p=>p.name),captains:full.players.map(p=>p.captain),mode:full.mode||"local",updatedAt:Date.now()};setCount(sv.players,sv.names);gameMode=sv.mode;',
    'if(full&&full.players?.length){const sv={players:full.players.length,names:full.players.map(p=>p.name),captains:full.players.map(p=>p.captain),portraits:full.players.map((p,i)=>p.portrait||defaultPortraits[i]),mode:full.mode||"local",updatedAt:Date.now()};applyPortraits(sv.portraits);setCount(sv.players,sv.names);gameMode=sv.mode;',
    'resume full-game portraits',
)

s = replace_once(
    s,
    'const st=JSON.parse(localStorage.getItem("captainsDashSetup")||"null");if(!st)return;setCount(Math.max(2,Math.min(4,st.players||2)),st.names);gameMode=st.mode||"local";',
    'const st=JSON.parse(localStorage.getItem("captainsDashSetup")||"null");if(!st)return;applyPortraits(st.portraits);setCount(Math.max(2,Math.min(4,st.players||2)),st.names);gameMode=st.mode||"local";',
    'restore setup portraits',
)
p.write_text(s)


# ---------------------------------------------------------------------------
# Voyage: use saved portrait everywhere; make AI Crew Quarters clearly resolve.
# ---------------------------------------------------------------------------
p = Path('voyage-v014.js')
s = p.read_text()
s = replace_once(
    s,
    "const portraits=['014ea26d527fb00d.jpg','5d6137ac745946c3.jpg','c70de609c89d8c4c.jpg','724be8a80f197bb0.jpg'];",
    "const portraits=['014ea26d527fb00d.jpg','5d6137ac745946c3.jpg','c70de609c89d8c4c.jpg','724be8a80f197bb0.jpg'];\nconst portraitFor=i=>state?.players?.[i]?.portrait||portraits[i];",
    'portrait helper',
)
s = s.replace('assets/${portraits[i]}', 'assets/${portraitFor(i)}')
s = s.replace('assets/${portraits[state.turn]}', 'assets/${portraitFor(state.turn)}')
s = s.replace('assets/${portraits[index]}', 'assets/${portraitFor(index)}')
s = replace_once(s, 'let state=null,zoom=false,aiTimer=null,guidePage=1,undoWorkerState=null;', 'let state=null,zoom=false,aiTimer=null,guidePage=1,undoWorkerState=null,aiDelayOverride=0;', 'AI delay state')
s = s.replace('The Final Isle · v0.24', 'The Final Isle · v0.25')
s = s.replace("'All 81 cards · v0.24'", "'All 81 cards · v0.25'")

s = replace_once(
    s,
    "function scheduleAI(){clearTimeout(aiTimer);if(!root.hidden&&isAITurn())aiTimer=setTimeout(aiStep,1050)}",
    "function scheduleAI(){clearTimeout(aiTimer);if(!root.hidden&&isAITurn()){const delay=aiDelayOverride||1050;aiDelayOverride=0;aiTimer=setTimeout(aiStep,delay)}}",
    'AI delay override',
)

old_order = "else if(!state.location){const ids=Object.keys(LOCATIONS).filter(l=>legalWorker(state,l)),order=p.crew.length<3&&p.gold>=3?['veteran','tavern','black','work','market','dock','quarters','witch']:p.supply<(unlocked(state,4)?9:unlocked(state,3)?6:3)?(p.gold?['market','work','dock','tavern','quarters','black','witch','veteran']:['work','dock','tavern','quarters','market','black','witch','veteran']):['dock','veteran','work','market','tavern','quarters','witch','black'];a={type:'worker',location:order.find(l=>ids.includes(l))}}"
new_order = "else if(!state.location){const ids=Object.keys(LOCATIONS).filter(l=>legalWorker(state,l)),tired=p.crew.filter(c=>c.exhausted).length,ready=p.crew.length-tired;const normalOrder=p.crew.length<3&&p.gold>=3?['veteran','tavern','black','work','market','dock','quarters','witch']:p.supply<(unlocked(state,4)?9:unlocked(state,3)?6:3)?(p.gold?['market','work','dock','tavern','quarters','black','witch','veteran']:['work','dock','tavern','quarters','market','black','witch','veteran']):['dock','veteran','work','market','tavern','quarters','witch','black'];const order=tired&&ready<=1?['quarters',...normalOrder.filter(x=>x!=='quarters')]:normalOrder;a={type:'worker',location:order.find(l=>ids.includes(l))}}"
s = replace_once(s, old_order, new_order, 'AI prioritizes Crew Quarters when fatigued')

s = replace_once(
    s,
    "else if(l==='quarters')a={type:'ready'};",
    "else if(l==='quarters'){const tired=p.crew.filter(c=>c.exhausted).length;if(tired){aiDelayOverride=2200;a={type:'ready',rested:tired}}else a={type:'skip'}};",
    'AI Crew Quarters ready action',
)

s = replace_once(
    s,
    "if(a&&!doAct(a))toast('AI action could not complete. Resume the action manually.');}",
    "if(a){const rested=a.type==='ready'?a.rested||0:0;const ok=doAct(a);if(!ok)toast('AI action could not complete. Resume the action manually.');else if(rested)toast(`${p.name} rested at Crew Quarters — ${rested} Crew are Ready.`);}}",
    'AI rest feedback',
)
p.write_text(s)


# ---------------------------------------------------------------------------
# Landing/setup CSS + version and hint.
# ---------------------------------------------------------------------------
p = Path('index.html')
s = p.read_text()
s = s.replace('v0.24', 'v0.25')
s = replace_once(s, '<div class="sectionTitle">Captains</div>', '<div class="sectionTitle captainTitle">Captains <small>Tap a portrait to change captain</small></div>', 'captain portrait hint')
css_marker = '.captain img{width:100%;height:96px;object-fit:cover;display:block}'
css_new = '.captain img{width:100%;height:96px;object-fit:cover;display:block}.captain:not(.inactive){cursor:pointer}.captain:not(.inactive):hover img,.captain:not(.inactive):focus img{filter:brightness(1.12);transform:scale(1.025)}.captain img{transition:filter .16s,transform .16s}.captain:focus{outline:2px solid #f4c866;outline-offset:2px}.captain:after{content:"↻";position:absolute;right:5px;top:5px;width:24px;height:24px;border-radius:50%;display:grid;place-items:center;background:#071820cc;color:#f4cf79;border:1px solid #e0b85c;font:700 16px system-ui}.captain.inactive:after{display:none}.captainTitle{display:flex;align-items:baseline;justify-content:space-between;gap:12px}.captainTitle small{font:11px system-ui;color:#725b40;font-weight:500}'
s = replace_once(s, css_marker, css_new, 'portrait picker CSS')
p.write_text(s)


# Static checks ---------------------------------------------------------------
checks = {
    'engine-v014.mjs': ['portrait:setup.portraits?.[i]||null', 'rested at Crew Quarters'],
    'menu.js': ['portraitOptions', 'captain-alt-06.svg', 'portraits:selectedPortraits.slice(0,count)', 'version:"0.25"'],
    'voyage-v014.js': ['portraitFor=', 'aiDelayOverride=2200', 'tired&&ready<=1', 'Crew are Ready', 'The Final Isle · v0.25'],
    'index.html': ['v0.25', 'Tap a portrait to change captain', 'captainTitle'],
}
for file, markers in checks.items():
    text = Path(file).read_text()
    for marker in markers:
        if marker not in text:
            raise SystemExit(f'{file}: missing marker {marker}')
print('v0.25 patch markers verified')
