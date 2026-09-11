from pathlib import Path
import re


def read(path):
    return Path(path).read_text(encoding='utf-8')


def write(path, text):
    Path(path).write_text(text, encoding='utf-8')


def sub_once(text, pattern, repl, label, flags=0):
    out, n = re.subn(pattern, repl, text, count=1, flags=flags)
    if n != 1:
        raise SystemExit(f'{label}: expected 1 replacement, got {n}')
    return out

# --- menu.js: restore the original four fixed portraits and remove portrait selection/randomization.
path='menu.js'
s=read(path)
s=sub_once(
    s,
    r'''  const portraitOptions=Array\.from\(\{length:10\},\(_?,?i\)=>`captain-v026-\$\{String\(i\+1\)\.padStart\(2,"0"\)\}\.svg`\);\n  const defaultPortraits=portraitOptions\.slice\(0,4\);\n  const randomPortraitSet=\(\)=>\{.*?\n  \};\n  let selectedPortraits=randomPortraitSet\(\);''',
    '''  const defaultPortraits=["014ea26d527fb00d.jpg","5d6137ac745946c3.jpg","c70de609c89d8c4c.jpg","724be8a80f197bb0.jpg"];\n  let selectedPortraits=[...defaultPortraits];''',
    'menu portrait constants',
    re.S,
)
s=s.replace('document.querySelectorAll("[data-panel]").forEach(b=>b.addEventListener("click",()=>{if(b.dataset.panel==="setup")randomizePortraits();openPanel(b.dataset.panel)}));',
            'document.querySelectorAll("[data-panel]").forEach(b=>b.addEventListener("click",()=>openPanel(b.dataset.panel)));')
if 'randomizePortraits();openPanel' in s:
    raise SystemExit('menu setup randomization still present')

s=sub_once(
    s,
    r'''  function renderCaptainPortraits\(\) \{.*?\n  document\.querySelectorAll\("\.captain"\)\.forEach\(\(c,i\)=>\{.*?\n  \}\);''',
    '''  function renderCaptainPortraits() {\n    document.querySelectorAll(".captain").forEach((c,i)=>{\n      const img=c.querySelector("img");\n      const portrait=defaultPortraits[i]||defaultPortraits[0];\n      if(img)img.src=`assets/${portrait}`;\n      c.dataset.portrait=portrait;\n      c.setAttribute("aria-label",`${captainNames[i]} portrait`);\n      c.removeAttribute("role");\n      c.tabIndex=-1;\n    });\n  }\n  function applyPortraits() {\n    selectedPortraits=[...defaultPortraits];\n    renderCaptainPortraits();\n  }''',
    'menu portrait functions',
    re.S,
)
s=s.replace('version:"0.26"','version:"0.27"')
s=s.replace('portraits:full.players.map((p,i)=>p.portrait||defaultPortraits[i])','portraits:defaultPortraits.slice(0,full.players.length)')
# currentSetup still serializes selectedPortraits, now always the original fixed set.
for forbidden in ['portraitOptions','randomPortraitSet','normalizePortraits','cyclePortrait(']:
    if forbidden in s:
        raise SystemExit(f'menu still contains portrait changer: {forbidden}')
for expected in ['014ea26d527fb00d.jpg','5d6137ac745946c3.jpg','c70de609c89d8c4c.jpg','724be8a80f197bb0.jpg','captains-dash-final-clean-v3.ogg','captains-dash-victory-v2.ogg','version:"0.27"']:
    if expected not in s:
        raise SystemExit(f'menu missing {expected}')
write(path,s)

# --- index.html: show the original fixed portraits and remove visual affordances for changing them.
path='index.html'
s=read(path)
s=s.replace('v0.26 Test','v0.27 Test').replace('v0.26 TEST','v0.27 TEST')
s=sub_once(
    s,
    r'''\.captains\{display:grid;grid-template-columns:repeat\(4,1fr\);gap:8px\}.*?\.captain span\{display:block;font-size:12px;padding:6px 2px;text-align:center\}''',
    '''.captains{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}\n.captain{position:relative;border:2px solid #795b3e;border-radius:10px;background:#221b16;overflow:hidden;color:white;padding:0;min-height:142px;cursor:default;transition:.15s}\n.captain.active{border-color:var(--gold);box-shadow:0 0 0 2px #f0c75f35}\n.captain.inactive{filter:grayscale(.85) brightness(.58);opacity:.65}\n.captain img{width:100%;height:96px;object-fit:cover;display:block}\n.captainTitle{display:flex;align-items:baseline;justify-content:space-between;gap:12px}\n.captain span{display:block;font-size:12px;padding:6px 2px;text-align:center}''',
    'index captain css',
    re.S,
)
s=s.replace('<div class="sectionTitle captainTitle">Captains <small>Tap a portrait to change captain · portraits stay unique</small></div>','<div class="sectionTitle captainTitle">Captains</div>')
repls={
 'assets/captain-v026-01.svg':'assets/014ea26d527fb00d.jpg',
 'assets/captain-v026-02.svg':'assets/5d6137ac745946c3.jpg',
 'assets/captain-v026-03.svg':'assets/c70de609c89d8c4c.jpg',
 'assets/captain-v026-04.svg':'assets/724be8a80f197bb0.jpg',
}
for a,b in repls.items(): s=s.replace(a,b)
if 'Tap a portrait to change captain' in s or 'portraits stay unique' in s:
    raise SystemExit('index still advertises portrait switching')
for expected in repls.values():
    if expected not in s: raise SystemExit(f'index missing {expected}')
write(path,s)

# --- voyage UI: original fixed portraits, including old saved games.
path='voyage-v014.js'
s=read(path)
s=s.replace("const portraits=['captain-v026-01.svg','captain-v026-02.svg','captain-v026-03.svg','captain-v026-04.svg'];",
            "const portraits=['014ea26d527fb00d.jpg','5d6137ac745946c3.jpg','c70de609c89d8c4c.jpg','724be8a80f197bb0.jpg'];")
s=s.replace('The Final Isle · v0.26','The Final Isle · v0.27')
old="state=normalizeSharedPools(saved?.version==='0.15'?saved:newGame(ev.detail));undoWorkerState=null;"
new="state=normalizeSharedPools(saved?.version==='0.15'?saved:newGame(ev.detail));state.players.forEach((p,i)=>{p.portrait=portraits[i]||portraits[0]});undoWorkerState=null;"
if old not in s: raise SystemExit('voyage startgame migration anchor missing')
s=s.replace(old,new,1)
for expected in ['014ea26d527fb00d.jpg','724be8a80f197bb0.jpg','The Final Isle · v0.27','p.portrait=portraits[i]']:
    if expected not in s: raise SystemExit(f'voyage missing {expected}')
write(path,s)

# --- v0.27 focused regression test.
Path('tests/rules-v027.mjs').write_text(r'''import assert from 'node:assert/strict';
import fs from 'node:fs';

const menu=fs.readFileSync(new URL('../menu.js',import.meta.url),'utf8');
const ui=fs.readFileSync(new URL('../voyage-v014.js',import.meta.url),'utf8');
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const originals=['014ea26d527fb00d.jpg','5d6137ac745946c3.jpg','c70de609c89d8c4c.jpg','724be8a80f197bb0.jpg'];

assert.match(menu,/version:"0\.27"/);
for(const p of originals){assert.match(menu,new RegExp(p.replace('.', '\\.')));assert.match(ui,new RegExp(p.replace('.', '\\.')));assert.match(html,new RegExp(p.replace('.', '\\.')));}
assert.doesNotMatch(menu,/randomPortraitSet|normalizePortraits|portraitOptions|cyclePortrait\(/);
assert.doesNotMatch(html,/Tap a portrait to change captain|portraits stay unique/);
assert.match(ui,/state\.players\.forEach\(\(p,i\)=>\{p\.portrait=portraits\[i\]\|\|portraits\[0\]\}\)/,'Old saves must migrate back to the fixed original portraits');
assert.match(menu,/captains-dash-final-clean-v3\.ogg/);
assert.match(menu,/captains-dash-victory-v2\.ogg/);
assert.match(ui,/state\.status===['"]won['"]\?['"]victory['"]:unlocked\(state,4\)\?['"]final['"]:['"]adventure['"]/);
assert.match(html,/v0\.27 TEST/);
console.log('v0.27 assertions passed: original four portraits restored and portrait switching removed; v0.26 music retained.');
''',encoding='utf-8')

print('v0.27 portrait rollback patch applied')
