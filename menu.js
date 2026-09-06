
(() => {
  "use strict";
  const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const app=document.getElementById("app");
  const panels=[...document.querySelectorAll(".panel")];
  const menuButtons=[...document.querySelectorAll(".menuBtn")];
  const captainNames=["Captain Anne","Captain Black","Captain Morgan","Captain Silver"];
  const colors=["#c9302c","#1f76b4","#21924a","#d7aa1d"];
  const seaNames=["Anne","Black","Morgan","Silver","Flint","Rackham","Bonny","Vane","Drake","Kidd","Read","Bellamy"];
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
  function toggleAmbient(force) {
    musicEnabled=force ?? !musicEnabled;
    document.getElementById("musicBtn").style.opacity=musicEnabled?"1":".45";
    if(!musicEnabled || settings.music<=0) {
      if(ambientGain) ambientGain.gain.setTargetAtTime(0,audioCtx.currentTime,.15);
      return;
    }
    try {
      audioCtx ||= new (window.AudioContext||window.webkitAudioContext)();
      if(!ambientNode) {
        const buffer=audioCtx.createBuffer(1,audioCtx.sampleRate*2,audioCtx.sampleRate);
        const data=buffer.getChannelData(0);
        for(let i=0;i<data.length;i++) data[i]=(Math.random()*2-1)*.26;
        const src=audioCtx.createBufferSource(); src.buffer=buffer; src.loop=true;
        const filter=audioCtx.createBiquadFilter(); filter.type="lowpass"; filter.frequency.value=430;
        ambientGain=audioCtx.createGain(); ambientGain.gain.value=0;
        src.connect(filter); filter.connect(ambientGain); ambientGain.connect(audioCtx.destination); src.start();
        ambientNode=src;
      }
      ambientGain.gain.setTargetAtTime((settings.music/100)*.035,audioCtx.currentTime,.3);
    } catch(e) {}
  }
  function closePanels() {
    panels.forEach(p=>p.classList.remove("show"));
    menuButtons.forEach(b=>b.classList.remove("active"));
  }
  function openPanel(name) {
    closePanels();
    const p=document.getElementById(name+"Panel"); if(p) p.classList.add("show");
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
  function setCount(n, values) {
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

  function currentSetup() {
    return {
      version:"0.3.1-step1",
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
    const raw=localStorage.getItem("captainsDashBoardStep7")||localStorage.getItem("captainsDashSetup");
    document.getElementById("continueBtn").disabled=!raw;
    document.getElementById("continueText").textContent=raw?"Resume your saved voyage":"No saved voyage yet";
  }
  refreshContinue();
  window.addEventListener('captainsdash:saved',refreshContinue);

  document.getElementById("continueBtn").addEventListener("click",()=>{
    try {
      const full=JSON.parse(localStorage.getItem("captainsDashBoardStep7")||"null");
      if(full&&full.players?.length){const sv={players:full.players.length,names:full.players.map(p=>p.name),captains:full.players.map(p=>p.captain),mode:full.mode||"local",updatedAt:Date.now()};setCount(sv.players,sv.names);gameMode=sv.mode;document.getElementById("voyageSummary").textContent=`${sv.players} Captains · Saved Full Game`;document.getElementById("roster").innerHTML=sv.names.map((n,i)=>`<span>${sv.captains[i]} — ${esc(n)}</span>`).join("");document.getElementById("transition").classList.add("show");window.dispatchEvent(new CustomEvent("captainsdash:startgame",{detail:{...sv,resume:true}}));return;}
      const st=JSON.parse(localStorage.getItem("captainsDashSetup")||"null");if(!st)return;setCount(Math.max(2,Math.min(4,st.players||2)),st.names);gameMode=st.mode||"local";openPanel("setup");toast("Saved voyage restored.");
    } catch(e){toast("Could not restore the saved game.")}
  });
  document.getElementById("randomNames").addEventListener("click",()=>{
    const shuffled=[...seaNames].sort(()=>Math.random()-.5);
    document.querySelectorAll("#names input").forEach((x,i)=>x.value=shuffled[i]);
    clickSfx(620);
  });
  document.getElementById("startBtn").addEventListener("click",()=>{
    if(localStorage.getItem("captainsDashBoardStep7")&&!window.confirm("Start a new voyage? This replaces the saved game on this device."))return;
    saveSetup(); clickSfx(660,.08);
    const s=currentSetup();
    document.getElementById("voyageSummary").textContent=`${s.players} Captains · ${s.mode==="ai"?"Solo vs AI":"Local Pass & Play"} · Final Isle awaits`;
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
  document.getElementById("guideNote").addEventListener("click",()=>toast("Guidebook v0.3 remains the rules source of truth."));

  // Scene parallax on pointer devices. No sensor permissions are requested.
  app.addEventListener("pointermove",e=>{
    if(settings.reduceMotion) return;
    const x=(e.clientX/window.innerWidth-.5)*14, y=(e.clientY/window.innerHeight-.5)*10;
    app.style.setProperty("--px",x+"px"); app.style.setProperty("--py",y+"px");
  },{passive:true});

  // First user gesture can start ambient audio if enabled.
  document.addEventListener("pointerdown",()=>{if(musicEnabled) toggleAmbient(true)},{once:true,passive:true});

  // Open Setup by default only on very wide screens; mobile stays on clean Home.
  if(window.matchMedia("(min-width:1100px)").matches) openPanel("setup");
})();
