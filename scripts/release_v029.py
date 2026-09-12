from pathlib import Path
import json
import re
import tempfile
import urllib.request
from PIL import Image

SHARES = [
    ('UaBNiQSQ7mUi', 'captain-user-01.webp'),
    ('otrHFLKS7u90', 'captain-user-02.webp'),
    ('re9sBQbTG-jD', 'captain-user-03.webp'),
    ('0rSXQbHJugoi', 'captain-user-04.webp'),
    ('RIKKQ9n6nMK2', 'captain-user-05.webp'),
    ('sJBv_JJ7Tkr2', 'captain-user-06.webp'),
]
API='https://api.firestorage.ai/dev/file'

def read(path): return Path(path).read_text(encoding='utf-8')
def write(path, text): Path(path).write_text(text, encoding='utf-8')

def sub_once(text, pattern, repl, label, flags=0):
    out,n=re.subn(pattern,repl,text,count=1,flags=flags)
    if n!=1: raise SystemExit(f'{label}: expected 1 replacement, got {n}')
    return out

def download_share(share_id, target):
    with urllib.request.urlopen(f'{API}/shares/{share_id}/files?maxResults=1000', timeout=30) as r:
        listing=json.load(r)
    candidates=[]
    def walk(v):
        if isinstance(v,dict):
            if any(k in v for k in ('id','fileId','file_id')) and any(k in v for k in ('name','fileName','file_name','mimeType','mime_type')):
                candidates.append(v)
            for x in v.values(): walk(x)
        elif isinstance(v,list):
            for x in v: walk(x)
    walk(listing)
    if not candidates:
        raise SystemExit(f'No file found in Firestorage share {share_id}: keys={list(listing) if isinstance(listing,dict) else type(listing)}')
    item=candidates[0]
    file_id=item.get('id') or item.get('fileId') or item.get('file_id')
    req=urllib.request.Request(f'{API}/shares/{share_id}/files/{file_id}/download', data=b'{}', headers={'Content-Type':'application/json'}, method='POST')
    with urllib.request.urlopen(req, timeout=30) as r:
        payload=json.load(r)
    url=payload.get('downloadUrl') or payload.get('download_url') or payload.get('url')
    if not url:
        raise SystemExit(f'No download URL for Firestorage share {share_id}: {payload}')
    with urllib.request.urlopen(url, timeout=60) as r:
        raw=r.read()
    with tempfile.NamedTemporaryFile(suffix='.png') as tmp:
        tmp.write(raw); tmp.flush()
        im=Image.open(tmp.name).convert('RGB')
        if im.width != im.height:
            side=min(im.width,im.height); left=(im.width-side)//2; top=(im.height-side)//2
            im=im.crop((left,top,left+side,top+side))
        im=im.resize((512,512),Image.Resampling.LANCZOS)
        Path(target).parent.mkdir(parents=True,exist_ok=True)
        im.save(target,'WEBP',quality=88,method=6)
        if Path(target).stat().st_size < 15000:
            raise SystemExit(f'{target} looks too small')

for share,name in SHARES:
    download_share(share, f'assets/{name}')

# menu.js — restore cycling with the four original portraits + six supplied portraits.
path='menu.js'; s=read(path)
old='''  const defaultPortraits=["014ea26d527fb00d.jpg","5d6137ac745946c3.jpg","c70de609c89d8c4c.jpg","724be8a80f197bb0.jpg"];
  let selectedPortraits=[...defaultPortraits];'''
new='''  const defaultPortraits=["014ea26d527fb00d.jpg","5d6137ac745946c3.jpg","c70de609c89d8c4c.jpg","724be8a80f197bb0.jpg"];
  const portraitOptions=[...defaultPortraits,"captain-user-01.webp","captain-user-02.webp","captain-user-03.webp","captain-user-04.webp","captain-user-05.webp","captain-user-06.webp"];
  let selectedPortraits=[...defaultPortraits];'''
if old not in s: raise SystemExit('menu portrait constants anchor missing')
s=s.replace(old,new,1)
old='''  function renderCaptainPortraits() {
    document.querySelectorAll(".captain").forEach((c,i)=>{
      const img=c.querySelector("img");
      const portrait=defaultPortraits[i]||defaultPortraits[0];
      if(img)img.src=`assets/${portrait}`;
      c.dataset.portrait=portrait;
      c.setAttribute("aria-label",`${captainNames[i]} portrait`);
      c.removeAttribute("role");
      c.tabIndex=-1;
    });
  }
  function applyPortraits() {
    selectedPortraits=[...defaultPortraits];
    renderCaptainPortraits();
  }'''
new='''  function renderCaptainPortraits() {
    document.querySelectorAll(".captain").forEach((c,i)=>{
      const img=c.querySelector("img");
      const portrait=selectedPortraits[i]||defaultPortraits[i]||defaultPortraits[0];
      if(img)img.src=`assets/${portrait}`;
      c.dataset.portrait=portrait;
      c.setAttribute("aria-label",`${captainNames[i]} portrait. Tap to change portrait.`);
      c.setAttribute("role","button");
      c.tabIndex=i<count?0:-1;
    });
  }
  function normalizePortraits(values) {
    const wanted=Array.isArray(values)?values:[];
    const used=new Set(),out=[];
    for(let i=0;i<4;i++){
      const candidate=wanted[i];
      if(portraitOptions.includes(candidate)&&!used.has(candidate)){out[i]=candidate;used.add(candidate);continue}
      const fallback=portraitOptions.find(x=>!used.has(x));out[i]=fallback;used.add(fallback);
    }
    return out;
  }
  function applyPortraits(values) {
    selectedPortraits=normalizePortraits(values?.length?values:defaultPortraits);
    renderCaptainPortraits();
  }
  function cyclePortrait(i,dir=1) {
    if(i>=count)return;
    const used=new Set(selectedPortraits.filter((_,j)=>j<count&&j!==i));
    const current=Math.max(0,portraitOptions.indexOf(selectedPortraits[i]));
    for(let step=1;step<=portraitOptions.length;step++){
      const idx=(current+dir*step+portraitOptions.length*4)%portraitOptions.length;
      if(!used.has(portraitOptions[idx])){selectedPortraits[i]=portraitOptions[idx];break}
    }
    renderCaptainPortraits();
    clickSfx(560,.06);
  }
  document.querySelectorAll(".captain").forEach((c,i)=>{
    c.addEventListener("click",()=>cyclePortrait(i,1));
    c.addEventListener("keydown",e=>{if((e.key==="Enter"||e.key===" ")&&i<count){e.preventDefault();cyclePortrait(i,e.shiftKey?-1:1)}});
  });'''
if old not in s: raise SystemExit('menu portrait functions anchor missing')
s=s.replace(old,new,1)
s=s.replace('version:"0.28"','version:"0.29"',1)
s=s.replace('portraits:defaultPortraits.slice(0,full.players.length)','portraits:full.players.map((p,i)=>p.portrait||defaultPortraits[i])',1)
for expected in ['portraitOptions','cyclePortrait','normalizePortraits','captain-user-06.webp','version:"0.29"']:
    if expected not in s: raise SystemExit(f'menu missing {expected}')
write(path,s)

# voyage-v014.js — selected portrait must travel with the player through randomized seating and saves.
path='voyage-v014.js'; s=read(path)
s=s.replace('The Final Isle · v0.28','The Final Isle · v0.29',1)
old="state=normalizeSharedPools(saved?.version==='0.15'?saved:newGame(ev.detail));state.players.forEach((p,i)=>{p.portrait=portraits[i]||portraits[0]});undoWorkerState=null;"
new="state=normalizeSharedPools(saved?.version==='0.15'?saved:newGame(ev.detail));state.players.forEach((p,i)=>{if(!p.portrait)p.portrait=portraits[i%portraits.length]||portraits[0]});undoWorkerState=null;"
if old not in s: raise SystemExit('voyage forced portrait overwrite anchor missing')
s=s.replace(old,new,1)
if 'if(!p.portrait)p.portrait=' not in s: raise SystemExit('voyage portrait preservation patch missing')
write(path,s)

# index.html — clickable portrait affordance and v0.29 label.
path='index.html'; s=read(path)
s=s.replace('v0.28 Test','v0.29 Test').replace('v0.28 TEST','v0.29 TEST')
s=s.replace('.captain{position:relative;border:2px solid #795b3e;border-radius:10px;background:#221b16;overflow:hidden;color:white;padding:0;min-height:142px;cursor:default;transition:.15s}',
'''.captain{position:relative;border:2px solid #795b3e;border-radius:10px;background:#221b16;overflow:hidden;color:white;padding:0;min-height:142px;cursor:default;transition:.15s}\n.captain:not(.inactive){cursor:pointer}\n.captain:not(.inactive):hover img,.captain:not(.inactive):focus img{filter:brightness(1.1);transform:scale(1.025)}\n.captain img{transition:filter .16s,transform .16s}\n.captain:focus{outline:2px solid #f4c866;outline-offset:2px}\n.captain:after{content:"↻";position:absolute;right:5px;top:5px;width:24px;height:24px;border-radius:50%;display:grid;place-items:center;background:#071820cc;color:#f4cf79;border:1px solid #e0b85c;font:700 16px system-ui}\n.captain.inactive:after{display:none}''',1)
s=s.replace('<div class="sectionTitle captainTitle">Captains</div>','<div class="sectionTitle captainTitle">Captains <small>Tap a portrait to change · portraits stay unique</small></div>',1)
if 'Tap a portrait to change' not in s: raise SystemExit('index portrait hint missing')
write(path,s)

# v0.29 focused regression tests.
Path('tests/rules-v029.mjs').write_text(r'''import assert from 'node:assert/strict';
import fs from 'node:fs';
import {newGame} from '../engine-v014.mjs';

const custom='captain-user-06.webp';
const setup={players:3,mode:'ai',names:['Human','AI One','AI Two'],portraits:[custom,'014ea26d527fb00d.jpg','5d6137ac745946c3.jpg']};
const s=newGame(setup,()=>0);
const human=s.players.find(p=>p.name==='Human');
assert.equal(human.portrait,custom,'selected portrait must stay attached to the same player after randomized turn order');
assert.equal(human.isAI,false,'human role must stay attached to the same player after shuffle');

const menu=fs.readFileSync(new URL('../menu.js',import.meta.url),'utf8');
const ui=fs.readFileSync(new URL('../voyage-v014.js',import.meta.url),'utf8');
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
assert.match(menu,/version:"0\.29"/);
assert.match(menu,/portraitOptions/);
assert.match(menu,/cyclePortrait/);
assert.match(menu,/normalizePortraits/);
assert.match(menu,/used=new Set/,'portrait chooser must skip portraits used by another active player');
assert.match(menu,/captain-user-01\.webp/);
assert.match(menu,/captain-user-06\.webp/);
assert.match(menu,/full\.players\.map\(\(p,i\)=>p\.portrait\|\|defaultPortraits\[i\]\)/,'resume should preserve saved portraits');
assert.match(ui,/if\(!p\.portrait\)p\.portrait=/,'game UI should only add a fallback portrait when one is missing');
assert.doesNotMatch(ui,/state\.players\.forEach\(\(p,i\)=>\{p\.portrait=portraits\[i\]/,'game start must not overwrite the selected portrait');
assert.match(html,/Tap a portrait to change/);
assert.match(html,/v0\.29 TEST/);
for(let i=1;i<=6;i++){
  const file=new URL(`../assets/captain-user-0${i}.webp`,import.meta.url);
  assert.equal(fs.existsSync(file),true,`${file.pathname} missing`);
  const raw=fs.readFileSync(file);
  assert.equal(raw.subarray(0,4).toString(),'RIFF');
  assert.equal(raw.subarray(8,12).toString(),'WEBP');
  assert.ok(raw.length>15000,'portrait file unexpectedly small');
}
console.log('v0.29 assertions passed: 10 selectable unique portraits and portrait identity survives randomized player order/save-resume.');
''',encoding='utf-8')

print('v0.29 portrait selection patch applied')
