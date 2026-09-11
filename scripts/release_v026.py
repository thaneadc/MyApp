from pathlib import Path


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly 1 match, found {count}")
    return text.replace(old, new, 1)


# ---------------------------------------------------------------------------
# Generate 10 close-up pirate portraits. These replace the simple v0.25 icons.
# Each image is face-forward, square, and deliberately cropped for setup/player UI.
# ---------------------------------------------------------------------------
PORTRAITS = [
    dict(bg1='#102b36', bg2='#07161d', skin='#c98758', skin2='#8d5033', hair='#2a1712', coat='#6d2723', accent='#d8ad55', hat='#2b1c18', band='#a4312e', beard='full', patch='right', scar='left'),
    dict(bg1='#31404a', bg2='#111820', skin='#8d573d', skin2='#593425', hair='#171311', coat='#163e50', accent='#d2b66a', hat='#16191d', band='#c49a35', beard='goatee', patch='left', scar='none'),
    dict(bg1='#3d251b', bg2='#180d0a', skin='#dfad7e', skin2='#a36c4c', hair='#5a2a19', coat='#4c6634', accent='#e4c16d', hat='#4b261a', band='#26758a', beard='none', patch='none', scar='right'),
    dict(bg1='#1e3d33', bg2='#081914', skin='#75452f', skin2='#4a2a20', hair='#0f0d0c', coat='#6e4a1f', accent='#d8a94f', hat='#252019', band='#8b2d32', beard='full', patch='left', scar='none'),
    dict(bg1='#3a3144', bg2='#16111c', skin='#b27655', skin2='#754634', hair='#20131a', coat='#243f68', accent='#e1b45a', hat='#241923', band='#7f305d', beard='goatee', patch='none', scar='left'),
    dict(bg1='#264653', bg2='#0d2028', skin='#e1a879', skin2='#9b6547', hair='#b06c2e', coat='#5d2f2c', accent='#f0cb78', hat='#30221b', band='#1d7890', beard='full', patch='right', scar='none'),
    dict(bg1='#41301e', bg2='#1a1109', skin='#915d43', skin2='#603b2c', hair='#33302c', coat='#2e5c55', accent='#cda55c', hat='#46321e', band='#b43a2f', beard='none', patch='left', scar='right'),
    dict(bg1='#1f3544', bg2='#08141d', skin='#c19475', skin2='#85614a', hair='#d8d0be', coat='#5c3b66', accent='#e0bd68', hat='#26222b', band='#315d9a', beard='full', patch='none', scar='left'),
    dict(bg1='#4a2528', bg2='#190b0d', skin='#5c3a2e', skin2='#39231d', hair='#17100f', coat='#7a4a1f', accent='#e6bd62', hat='#191516', band='#c7a341', beard='goatee', patch='right', scar='none'),
    dict(bg1='#214137', bg2='#071914', skin='#d29166', skin2='#93583e', hair='#3a2018', coat='#285d72', accent='#e7bd63', hat='#2d211a', band='#a92f39', beard='none', patch='none', scar='right'),
]


def portrait_svg(i, cfg):
    beard = ''
    if cfg['beard'] == 'full':
        beard = f'''<path d="M75 141 Q82 207 128 226 Q174 207 181 141 Q163 177 128 181 Q93 177 75 141Z" fill="{cfg['hair']}" opacity=".94"/>
<path d="M92 157 Q128 186 164 157" fill="none" stroke="#000" stroke-opacity=".25" stroke-width="5"/>'''
    elif cfg['beard'] == 'goatee':
        beard = f'''<path d="M108 163 Q128 177 148 163 Q145 203 128 219 Q111 203 108 163Z" fill="{cfg['hair']}"/>
<path d="M103 151 Q128 162 153 151" fill="none" stroke="{cfg['hair']}" stroke-width="8" stroke-linecap="round"/>'''
    patch = ''
    if cfg['patch'] != 'none':
        eye_x = 99 if cfg['patch'] == 'left' else 157
        strap_a = 'M72 88 L184 126' if cfg['patch'] == 'right' else 'M72 124 L184 88'
        patch = f'''<path d="{strap_a}" stroke="#191515" stroke-width="6" opacity=".9"/>
<ellipse cx="{eye_x}" cy="116" rx="18" ry="13" fill="#191515"/><path d="M{eye_x-12} 115 Q{eye_x} 125 {eye_x+12} 115" fill="none" stroke="#6c4d36" stroke-width="2"/>'''
    scar = ''
    if cfg['scar'] != 'none':
        x = 91 if cfg['scar'] == 'left' else 165
        scar = f'''<path d="M{x} 121 l-8 18 M{x-3} 127 l-7 -3 M{x-7} 135 l-7 -3" stroke="#6f342b" stroke-width="3" stroke-linecap="round" opacity=".75"/>'''
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" role="img" aria-label="Pirate captain portrait {i}">
<defs>
 <radialGradient id="bg" cx="50%" cy="30%" r="80%"><stop offset="0" stop-color="{cfg['bg1']}"/><stop offset="1" stop-color="{cfg['bg2']}"/></radialGradient>
 <linearGradient id="face" x1="0" y1="0" x2="1" y2="1"><stop stop-color="{cfg['skin']}"/><stop offset="1" stop-color="{cfg['skin2']}"/></linearGradient>
 <linearGradient id="coat" x1="0" y1="0" x2="0" y2="1"><stop stop-color="{cfg['coat']}"/><stop offset="1" stop-color="#161414"/></linearGradient>
 <filter id="shadow"><feDropShadow dx="0" dy="5" stdDeviation="5" flood-color="#000" flood-opacity=".55"/></filter>
</defs>
<rect width="256" height="256" fill="url(#bg)"/>
<circle cx="44" cy="46" r="34" fill="{cfg['accent']}" opacity=".06"/><circle cx="218" cy="74" r="45" fill="#9de6ef" opacity=".04"/>
<!-- shoulders / coat -->
<path d="M26 256 Q31 201 76 184 Q101 174 128 174 Q155 174 180 184 Q225 201 230 256Z" fill="url(#coat)"/>
<path d="M66 191 L103 220 L91 256 H45 Q46 214 66 191Z" fill="#111b20" opacity=".55"/><path d="M190 191 L153 220 L165 256 H211 Q210 214 190 191Z" fill="#111b20" opacity=".55"/>
<path d="M88 190 L128 222 L168 190" fill="none" stroke="{cfg['accent']}" stroke-width="5" opacity=".8"/>
<!-- ears / neck -->
<ellipse cx="66" cy="126" rx="15" ry="22" fill="{cfg['skin2']}"/><ellipse cx="190" cy="126" rx="15" ry="22" fill="{cfg['skin2']}"/>
<path d="M105 160 H151 L157 195 Q128 213 99 195Z" fill="{cfg['skin2']}"/>
<!-- hair silhouette -->
<path d="M67 100 Q67 47 128 42 Q189 47 189 102 L179 92 Q166 68 128 68 Q89 68 77 94Z" fill="{cfg['hair']}"/>
<!-- face -->
<path d="M75 95 Q79 63 128 60 Q177 63 181 95 L177 143 Q170 174 128 187 Q86 174 79 143Z" fill="url(#face)" filter="url(#shadow)"/>
<!-- cheek light -->
<path d="M91 132 Q101 160 124 169" fill="none" stroke="#ffd8ad" stroke-opacity=".16" stroke-width="8" stroke-linecap="round"/>
<!-- brows / eyes -->
<path d="M82 105 Q99 95 116 104 M140 104 Q157 95 174 105" fill="none" stroke="{cfg['hair']}" stroke-width="7" stroke-linecap="round"/>
<ellipse cx="100" cy="117" rx="7" ry="5" fill="#eee0c5"/><ellipse cx="156" cy="117" rx="7" ry="5" fill="#eee0c5"/>
<circle cx="101" cy="117" r="3.2" fill="#17292b"/><circle cx="155" cy="117" r="3.2" fill="#17292b"/>
<!-- nose / mouth -->
<path d="M128 112 Q121 137 128 143 Q136 142 140 139" fill="none" stroke="#75412f" stroke-width="4" stroke-linecap="round"/>
<path d="M105 157 Q128 169 151 156 Q128 178 105 157Z" fill="#6d312b"/><path d="M112 158 Q128 163 144 157" stroke="#e6c2a4" stroke-width="2" opacity=".65"/>
{scar}
{patch}
{beard}
<!-- pirate hat -->
<path d="M47 77 Q57 41 89 34 Q128 18 167 34 Q199 41 209 77 Q179 66 157 69 Q128 75 99 69 Q77 66 47 77Z" fill="{cfg['hat']}" stroke="{cfg['accent']}" stroke-width="4"/>
<path d="M66 66 Q128 48 190 66" fill="none" stroke="{cfg['band']}" stroke-width="12"/>
<path d="M42 78 Q84 87 128 74 Q172 87 214 78 Q199 101 165 94 Q128 87 91 94 Q57 101 42 78Z" fill="{cfg['hat']}" stroke="#0b0909" stroke-width="3"/>
<!-- skull emblem -->
<circle cx="128" cy="53" r="10" fill="{cfg['accent']}"/><circle cx="124" cy="51" r="2" fill="#2b2018"/><circle cx="132" cy="51" r="2" fill="#2b2018"/><path d="M125 57h6 M119 63l18 9 M137 63l-18 9" stroke="{cfg['accent']}" stroke-width="3" stroke-linecap="round"/>
<!-- foreground vignette -->
<rect x="2" y="2" width="252" height="252" rx="22" fill="none" stroke="{cfg['accent']}" stroke-opacity=".7" stroke-width="4"/>
<path d="M0 0h256v256H0z" fill="none" stroke="#000" stroke-opacity=".32" stroke-width="16"/>
</svg>'''


Path('assets').mkdir(exist_ok=True)
for idx, cfg in enumerate(PORTRAITS, 1):
    Path(f'assets/captain-v026-{idx:02d}.svg').write_text(portrait_svg(idx, cfg))


# ---------------------------------------------------------------------------
# Menu: unique randomized portraits + Final/Victory soundtracks.
# ---------------------------------------------------------------------------
p = Path('menu.js')
s = p.read_text()
old_portraits = '''  const defaultPortraits=["014ea26d527fb00d.jpg","5d6137ac745946c3.jpg","c70de609c89d8c4c.jpg","724be8a80f197bb0.jpg"];
  const portraitOptions=[...defaultPortraits,"captain-alt-01.svg","captain-alt-02.svg","captain-alt-03.svg","captain-alt-04.svg","captain-alt-05.svg","captain-alt-06.svg"];
  let selectedPortraits=[...defaultPortraits];'''
new_portraits = '''  const portraitOptions=Array.from({length:10},(_,i)=>`captain-v026-${String(i+1).padStart(2,"0")}.svg`);
  const defaultPortraits=portraitOptions.slice(0,4);
  const randomPortraitSet=()=>{
    const a=[...portraitOptions];
    for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]]}
    return a.slice(0,4);
  };
  let selectedPortraits=randomPortraitSet();'''
s = replace_once(s, old_portraits, new_portraits, 'portrait pool')

old_music = "  const MUSIC_TRACKS={adventure:'assets/captains-dash-adventure-v2.ogg',adrenaline:'assets/captains-dash-adrenaline-v2.ogg'};"
new_music = "  const MUSIC_TRACKS={adventure:'assets/captains-dash-adventure-v2.ogg',final:'assets/captains-dash-final-clean-v3.ogg',victory:'assets/captains-dash-victory-v2.ogg'};"
s = replace_once(s, old_music, new_music, 'music track map')
s = replace_once(s, "    mode=mode==='adrenaline'?'adrenaline':'adventure';", "    mode=['adventure','final','victory'].includes(mode)?mode:'adventure';", 'music mode validation')
s = replace_once(s, "    soundtrack.loop=true;\n    soundtrack.currentTime=0;", "    soundtrack.loop=mode!=='victory';\n    soundtrack.currentTime=0;", 'victory one-shot')

old_panel_listener = '  document.querySelectorAll("[data-panel]").forEach(b=>b.addEventListener("click",()=>openPanel(b.dataset.panel)));'
new_panel_listener = '  document.querySelectorAll("[data-panel]").forEach(b=>b.addEventListener("click",()=>{if(b.dataset.panel==="setup")randomizePortraits();openPanel(b.dataset.panel)}));'
s = replace_once(s, old_panel_listener, new_panel_listener, 'randomize on new game')

old_apply_cycle = '''  function applyPortraits(values) {
    if(Array.isArray(values))for(let i=0;i<4;i++)if(values[i]&&portraitOptions.includes(values[i]))selectedPortraits[i]=values[i];
    renderCaptainPortraits();
  }
  function cyclePortrait(i,dir=1) {
    if(i>=count)return;
    const current=portraitOptions.indexOf(selectedPortraits[i]);
    selectedPortraits[i]=portraitOptions[(Math.max(0,current)+dir+portraitOptions.length)%portraitOptions.length];
    renderCaptainPortraits();
    clickSfx(560,.06);
  }'''
new_apply_cycle = '''  function normalizePortraits(values) {
    const wanted=Array.isArray(values)?values:[];
    const used=new Set(),out=[];
    for(let i=0;i<4;i++){
      const candidate=wanted[i];
      if(portraitOptions.includes(candidate)&&!used.has(candidate)){out[i]=candidate;used.add(candidate);continue}
      const fallback=portraitOptions.find(x=>!used.has(x));out[i]=fallback;used.add(fallback);
    }
    return out;
  }
  function randomizePortraits() {
    selectedPortraits=randomPortraitSet();
    renderCaptainPortraits();
  }
  function applyPortraits(values) {
    selectedPortraits=normalizePortraits(values);
    renderCaptainPortraits();
  }
  function cyclePortrait(i,dir=1) {
    if(i>=count)return;
    const used=new Set(selectedPortraits.filter((_,j)=>j!==i));
    const current=Math.max(0,portraitOptions.indexOf(selectedPortraits[i]));
    for(let step=1;step<=portraitOptions.length;step++){
      const idx=(current+dir*step+portraitOptions.length*4)%portraitOptions.length;
      if(!used.has(portraitOptions[idx])){selectedPortraits[i]=portraitOptions[idx];break}
    }
    renderCaptainPortraits();
    clickSfx(560,.06);
  }'''
s = replace_once(s, old_apply_cycle, new_apply_cycle, 'unique portrait selection')
s = replace_once(s, '      version:"0.25",', '      version:"0.26",', 'setup version')
p.write_text(s)


# ---------------------------------------------------------------------------
# Voyage: new portrait fallbacks + final/victory music state.
# ---------------------------------------------------------------------------
p = Path('voyage-v014.js')
s = p.read_text()
s = replace_once(
    s,
    "const portraits=['014ea26d527fb00d.jpg','5d6137ac745946c3.jpg','c70de609c89d8c4c.jpg','724be8a80f197bb0.jpg'];",
    "const portraits=['captain-v026-01.svg','captain-v026-02.svg','captain-v026-03.svg','captain-v026-04.svg'];",
    'voyage portrait fallbacks',
)
s = replace_once(
    s,
    "window.dispatchEvent(new CustomEvent('captainsdash:music-mode',{detail:{mode:unlocked(state,4)?'adrenaline':'adventure'}}));",
    "window.dispatchEvent(new CustomEvent('captainsdash:music-mode',{detail:{mode:state.status==='won'?'victory':unlocked(state,4)?'final':'adventure'}}));",
    'music state selection',
)
s = s.replace('The Final Isle · v0.25', 'The Final Isle · v0.26')
s = s.replace("'All 81 cards · v0.25'", "'All 81 cards · v0.26'")
p.write_text(s)


# ---------------------------------------------------------------------------
# Setup HTML/CSS: close-up crop, new default portraits, v0.26 labels.
# ---------------------------------------------------------------------------
p = Path('index.html')
s = p.read_text()
s = s.replace('v0.25 Test', 'v0.26 Test').replace('v0.25 TEST', 'v0.26 TEST')
s = replace_once(
    s,
    'Captains <small>Tap a portrait to change captain</small>',
    'Captains <small>Tap a portrait to change captain · portraits stay unique</small>',
    'portrait helper copy',
)
for old,new in zip(
    ['014ea26d527fb00d.jpg','5d6137ac745946c3.jpg','c70de609c89d8c4c.jpg','724be8a80f197bb0.jpg'],
    ['captain-v026-01.svg','captain-v026-02.svg','captain-v026-03.svg','captain-v026-04.svg'],
):
    s = s.replace(f'assets/{old}', f'assets/{new}', 1)
old_css = '.captain{position:relative;border:2px solid #795b3e;border-radius:10px;background:#221b16;overflow:hidden;color:white;padding:0;min-height:142px;cursor:default;transition:.15s}'
new_css = '.captain{position:relative;border:2px solid #795b3e;border-radius:12px;background:linear-gradient(#241c17,#110e0c);overflow:hidden;color:white;padding:0;min-height:158px;cursor:default;transition:.15s;box-shadow:0 5px 12px #0005}'
s = replace_once(s, old_css, new_css, 'captain card CSS')
old_img_css = '.captain img{width:100%;height:96px;object-fit:cover;display:block}.captain:not(.inactive)'
new_img_css = '.captain img{width:100%;height:112px;object-fit:cover;object-position:center 28%;display:block;background:#102832}.captain:not(.inactive)'
s = replace_once(s, old_img_css, new_img_css, 'portrait crop CSS')
p.write_text(s)


# ---------------------------------------------------------------------------
# v0.25 regression test: preserve behavior but stop requiring retired art files.
# ---------------------------------------------------------------------------
p = Path('tests/rules-v025.mjs')
s = p.read_text()
s = s.replace("portraits:['captain-alt-01.svg','captain-alt-02.svg','captain-alt-03.svg']", "portraits:['captain-v026-01.svg','captain-v026-02.svg','captain-v026-03.svg']")
s = s.replace("assert.equal(s.players[0].portrait,'captain-alt-01.svg');", "assert.equal(s.players[0].portrait,'captain-v026-01.svg');")
s = s.replace("assert.equal(s.players[1].portrait,'captain-alt-02.svg');", "assert.equal(s.players[1].portrait,'captain-v026-02.svg');")
s = s.replace("assert.equal(s.players[2].portrait,'captain-alt-03.svg');", "assert.equal(s.players[2].portrait,'captain-v026-03.svg');")
s = s.replace("for(let i=1;i<=6;i++) assert.match(menu,new RegExp(`captain-alt-0${i}\\\\.svg`));\n", "assert.match(menu,/portraitOptions/);\n")
p.write_text(s)


# ---------------------------------------------------------------------------
# Static release checks.
# ---------------------------------------------------------------------------
checks = {
    'menu.js': ['version:"0.26"','randomPortraitSet','normalizePortraits','used=new Set','captains-dash-final-clean-v3.ogg','captains-dash-victory-v2.ogg',"mode!==\'victory\'".replace('\\','')],
    'voyage-v014.js': ["state.status==='won'?'victory':unlocked(state,4)?'final':'adventure'",'captain-v026-01.svg','The Final Isle · v0.26'],
    'index.html': ['v0.26 TEST','portraits stay unique','captain-v026-04.svg','object-position:center 28%'],
}
for file, markers in checks.items():
    text=Path(file).read_text()
    for marker in markers:
        if marker not in text:
            raise SystemExit(f'{file}: missing v0.26 marker {marker}')
for i in range(1,11):
    text=Path(f'assets/captain-v026-{i:02d}.svg').read_text()
    if 'viewBox="0 0 256 256"' not in text or '<svg' not in text:
        raise SystemExit(f'portrait {i} invalid')
print('v0.26 patch markers verified')
