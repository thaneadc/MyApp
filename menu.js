
(() => {
  "use strict";
  const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const app=document.getElementById("app");
  const panels=[...document.querySelectorAll(".panel")];
  const menuButtons=[...document.querySelectorAll(".menuBtn")];
  const captainNames=["Captain Anne","Captain Black","Captain Morgan","Captain Silver"];
  const colors=["#c9302c","#1f76b4","#21924a","#d7aa1d"];
  const seaNames=["Anne","Black","Morgan","Silver","Flint","Rackham","Bonny","Vane","Drake","Kidd","Read","Bellamy"];
  const aiNames=["AI Blackbeard","AI Morgan","AI Silver"];
  let count=2;
  let gameMode="local";
  let settings={music:35,sfx:60,hints:true,reduceMotion:false,autoSave:true};
  let audioCtx=null, ambientNode=null, ambientGain=null, sfxEnabled=true, musicEnabled=true;

  function toast(msg) {
    const t=document.getElementById("toast"); t.textContent=msg; t.classList.add("show");
    clearTimeout(toast._t); toast._t=setTimeout(()=>t.classList.remove("show"),1800);
  }
  function clickSfx(freq=420,dur=.045) {
    if(!sfxEnabled || settings.sfx<=0) return;
    try {
      audioCtx ||= new (window.AudioContext||window.webkitAudioContext)();
      const o=audioCtx.createOscillator(), g=audioCtx.createGain();
      o.frequency.value=freq; o.type="triangle"; g.gain.value=(settings.sfx/100)*.035;
      o.connect(g); g.connect(audioCtx.destination); o.start(); g.gain.exponentialRampToValueAtTime(.0001,audioCtx.currentTime+dur); o.stop(audioCtx.currentTime+dur);
    } catch(e) {}
  }
  const MUSIC_TRACKS={adventure:'assets/captains-dash-adventure-v2.ogg',adrenaline:'assets/captains-dash-adrenaline-v2.ogg'};
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
  function toggleAmbient(force) {
    musicEnabled=force ?? !musicEnabled;
    soundtrack.volume=Math.max(0,Math.min(1,settings.music/100));
    if(!musicEnabled||settings.music<=0) soundtrack.pause();
    else {musicStarted=true;soundtrack.play().catch(()=>toast('Tap Music to start the soundtrack.'));}
    document.querySelectorAll('[data-music-toggle],#musicBtn').forEach(b=>{b.style.opacity=musicEnabled?'1':'.45';b.setAttribute('aria-pressed',String(musicEnabled));});
  }
  document.addEventListener('click',ev=>{if(ev.target.closest('[data-music-toggle]'))toggleAmbient();});
  window.addEventListener('captainsdash:music-mode',ev=>setMusicMode(ev.detail?.mode));
  window.addEventListener('captainsdash:startgame',()=>{setMusicMode('adventure');toggleAmbient(musicEnabled)});
  document.addEventListener('visibilitychange',()=>{if(document.hidden)soundtrack.pause();else if(musicStarted&&musicEnabled&&settings.music>0)soundtrack.play().catch(()=>{});});
  function closePanels() {
    document.body.classList.remove("menu-modal-open");
    panels.forEach(p=>p.classList.remove("show"));
    menuButtons.forEach(b=>b.classList.remove("active"));
  }
  function openPanel(name) {
    closePanels();
    const p=document.getElementById(name+"Panel"); if(p) {p.classList.add("show");document.body.classList.add("menu-modal-open");p.setAttribute("role","dialog");p.setAttribute("aria-modal","true");p.querySelector("button")?.focus();}
    const b=document.querySelector(`[data-panel="${name}"]`); if(b) b.classList.add("active");
    clickSfx(360);
  }
  document.querySelectorAll("[data-panel]").forEach(b=>b.addEventListener("click",()=>openPanel(b.dataset.panel)));
  document.querySelectorAll("[data-close]").forEach(b=>b.addEventListener("click",()=>{closePanels();clickSfx(290)}));

  function renderNames(values) {
    const host=document.getElementById("names"); host.innerHTML="";
    for(let i=0;i<count;i++) {
      const row=document.createElement("label"); row.className="nameRow";
      row.innerHTML=`<span class="badge" style="background:${colors[i]}"></span><input maxlength="18" aria-label="Player ${i+1} name" value="${esc((values&&values[i])||"Player "+(i+1))}">`;
      host.appendChild(row);
    }
    document.querySelectorAll(".captain").forEach((c,i)=>c.classList.toggle("inactive",i>=count));
  }
  function syncModeNames() {
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

  function currentSetup() {
    return {
      version:"0.22",
      players:count,
      names:[...document.querySelectorAll("#names input")].map(x=>x.value.trim()||"Captain"),
      captains:captainNames.slice(0,count),
      mode:gameMode,
      updatedAt:Date.now()
    };
  }
  function saveSetup() {
    if(!settings.autoSave) return;
    localStorage.setItem("captainsDashSetup",JSON.stringify(currentSetup()));
    refreshContinue();
  }
  function refreshContinue() {
    const raw=localStorage.getItem("captainsDashRules015")||localStorage.getItem("captainsDashSetup");
    document.getElementById("continueBtn").disabled=!raw;
    document.getElementById("continueText").textContent=raw?"Resume your saved voyage":"No saved voyage yet";
  }
  refreshContinue();
  window.addEventListener('captainsdash:saved',refreshContinue);

  document.getElementById("continueBtn").addEventListener("click",()=>{
    try {
      const full=JSON.parse(localStorage.getItem("captainsDashRules015")||"null");
      if(full&&full.players?.length){const sv={players:full.players.length,names:full.players.map(p=>p.name),captains:full.players.map(p=>p.captain),mode:full.mode||"local",updatedAt:Date.now()};setCount(sv.players,sv.names);gameMode=sv.mode;document.getElementById("voyageSummary").textContent=`${sv.players} Captains · Saved Full Game`;document.getElementById("roster").innerHTML=sv.names.map((n,i)=>`<span>${sv.captains[i]} — ${esc(n)}</span>`).join("");document.getElementById("transition").classList.add("show");window.dispatchEvent(new CustomEvent("captainsdash:startgame",{detail:{...sv,resume:true}}));return;}
      const st=JSON.parse(localStorage.getItem("captainsDashSetup")||"null");if(!st)return;setCount(Math.max(2,Math.min(4,st.players||2)),st.names);gameMode=st.mode||"local";openPanel("setup");toast("Saved voyage restored.");
    } catch(e){toast("Could not restore the saved game.")}
  });
  document.getElementById("randomNames").addEventListener("click",()=>{
    const shuffled=[...seaNames].sort(()=>Math.random()-.5);
    document.querySelectorAll("#names input").forEach((x,i)=>{if(gameMode!=="ai"||i===0)x.value=shuffled[i]});
    syncModeNames();
    clickSfx(620);
  });
  function confirmNewVoyage(){return new Promise(resolve=>{const d=document.createElement('dialog');d.className='menuConfirm';d.innerHTML='<h2>Start a new voyage?</h2><p>This replaces the saved voyage on this device.</p><div class="buttons"><button data-answer="no">Keep saved voyage</button><button data-answer="yes">Start new voyage</button></div>';document.body.appendChild(d);d.addEventListener('click',e=>{const a=e.target.closest('[data-answer]');if(a){d.close();d.remove();resolve(a.dataset.answer==='yes')}});d.addEventListener('cancel',()=>{d.remove();resolve(false)});d.showModal()})}
  document.getElementById("startBtn").addEventListener("click",async()=>{
    if(localStorage.getItem("captainsDashRules015")&&!await confirmNewVoyage())return;
    saveSetup(); clickSfx(660,.08);
    const s=currentSetup();
    document.getElementById("voyageSummary").textContent=`${s.players} Captains · ${s.mode==="ai"?"1 Human + "+(s.players-1)+" AI":"Local Pass & Play"} · Final Isle awaits`;
    document.getElementById("roster").innerHTML=s.names.map((n,i)=>`<span>${captainNames[i]} — ${esc(n)}</span>`).join("");
    document.getElementById("transition").classList.add("show");
    window.dispatchEvent(new CustomEvent("captainsdash:startgame",{detail:s}));
  });
  document.getElementById("backMenu").addEventListener("click",()=>document.getElementById("transition").classList.remove("show"));

  function loadSettings() {
    try{settings={...settings,...JSON.parse(localStorage.getItem("captainsDashSettings")||"{}")}}catch(e){}
    document.getElementById("musicRange").value=settings.music;
    document.getElementById("sfxRange").value=settings.sfx;
    setSwitch("hintsSwitch",settings.hints);
    setSwitch("motionSwitch",settings.reduceMotion);
    setSwitch("saveSwitch",settings.autoSave);
    document.body.classList.toggle("reduce",settings.reduceMotion);
  }
  function setSwitch(id,on) {const b=document.getElementById(id);b.classList.toggle("on",!!on);b.setAttribute("aria-pressed",String(!!on))}
  ["hintsSwitch","motionSwitch","saveSwitch"].forEach(id=>document.getElementById(id).addEventListener("click",e=>{
    const on=!e.currentTarget.classList.contains("on"); setSwitch(id,on); clickSfx(390);
  }));
  document.getElementById("applySettings").addEventListener("click",()=>{
    settings.music=+document.getElementById("musicRange").value;
    settings.sfx=+document.getElementById("sfxRange").value;
    settings.hints=document.getElementById("hintsSwitch").classList.contains("on");
    settings.reduceMotion=document.getElementById("motionSwitch").classList.contains("on");
    settings.autoSave=document.getElementById("saveSwitch").classList.contains("on");
    localStorage.setItem("captainsDashSettings",JSON.stringify(settings));
    document.body.classList.toggle("reduce",settings.reduceMotion);
    toggleAmbient(musicEnabled); toast("Settings applied.");
  });
  loadSettings();

  document.getElementById("musicBtn").addEventListener("click",()=>{toggleAmbient();clickSfx(520)});
  document.getElementById("sfxBtn").addEventListener("click",()=>{sfxEnabled=!sfxEnabled;document.getElementById("sfxBtn").style.opacity=sfxEnabled?"1":".45"; if(sfxEnabled) clickSfx(520)});
  document.getElementById("fullBtn").addEventListener("click",async()=>{
    try{if(!document.fullscreenElement) await document.documentElement.requestFullscreen(); else await document.exitFullscreen();}catch(e){toast("Fullscreen is not available in this browser.")}
  });
  document.getElementById("langBtn").addEventListener("click",()=>toast("Game language is English for this prototype."));

  document.addEventListener('keydown',e=>{if(e.key==='Escape')closePanels();if(e.key==='Tab'){const p=panels.find(p=>p.classList.contains('show'));if(!p)return;const els=[...p.querySelectorAll('button:not(:disabled),input,select:not(:disabled)')];const first=els[0],last=els.at(-1);if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus()}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus()}}});
  window.addEventListener('captainsdash:startgame',closePanels);
  // Scene parallax on pointer devices. No sensor permissions are requested.
  app.addEventListener("pointermove",e=>{
    if(settings.reduceMotion) return;
    const x=(e.clientX/window.innerWidth-.5)*14, y=(e.clientY/window.innerHeight-.5)*10;
    app.style.setProperty("--px",x+"px"); app.style.setProperty("--py",y+"px");
  },{passive:true});

  // First user gesture can start ambient audio if enabled.
  document.addEventListener("pointerdown",()=>{if(musicEnabled) toggleAmbient(true)},{once:true,passive:true});

  // Open Setup by default only on very wide screens; mobile stays on clean Home.

})();
