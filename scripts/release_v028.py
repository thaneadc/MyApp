from pathlib import Path

engine=Path('engine-v014.mjs')
text=engine.read_text()
old=""" s.players=Array.from({length:Math.max(2,Math.min(4,setup.players||2))},(_,i)=>({name:setup.names?.[i]||'Player '+(i+1),portrait:setup.portraits?.[i]||null,gold:i?3:2,supply:i>=2?3:2,crew:[instance(s,'C01')],treasures:[],blessing:null}));"""
new=""" const playerCount=Math.max(2,Math.min(4,setup.players||2));
 const seats=Array.from({length:playerCount},(_,i)=>({name:setup.names?.[i]||'Player '+(i+1),portrait:setup.portraits?.[i]||null,isAI:setup.mode==='ai'&&i>0,gold:0,supply:0,crew:[instance(s,'C01')],treasures:[],blessing:null}));
 s.players=shuffle(seats,rng);
 s.players.forEach((p,i)=>{p.gold=i?3:2;p.supply=i>=2?3:2});
 s.log.unshift('Turn order: '+s.players.map(p=>p.name).join(' → '));"""
if old not in text:
    raise SystemExit('newGame player creation block not found')
text=text.replace(old,new,1)
old_norm=""" for(const p of s.players){delete p.market;delete p.veteranMarket;delete p.treasureDeck;delete p.crewDeck;delete p.veteranDeck}"""
new_norm=""" const hasAIRole=s.players.some(p=>Object.hasOwn(p,'isAI'));
 if(s.mode==='ai'&&!hasAIRole)s.players.forEach((p,i)=>p.isAI=i>0);
 if(s.mode!=='ai')s.players.forEach(p=>p.isAI=false);
 for(const p of s.players){delete p.market;delete p.veteranMarket;delete p.treasureDeck;delete p.crewDeck;delete p.veteranDeck}"""
if old_norm not in text:
    raise SystemExit('normalizeSharedPools player loop not found')
text=text.replace(old_norm,new_norm,1)
engine.write_text(text)

ui=Path('voyage-v014.js')
text=ui.read_text()
old_ai="const isAITurn=()=>state?.mode==='ai'&&state.turn>0&&state.status==='playing';"
new_ai="const isAITurn=()=>state?.mode==='ai'&&state?.status==='playing'&&!!current(state)?.isAI;"
if old_ai not in text:
    raise SystemExit('isAITurn definition not found')
text=text.replace(old_ai,new_ai,1)
old_label="state.mode==='ai'&&i>0?'AI TURN':'YOUR TURN'"
new_label="state.mode==='ai'&&p.isAI?'AI TURN':'YOUR TURN'"
if old_label not in text:
    raise SystemExit('playerDock AI label not found')
text=text.replace(old_label,new_label,1)
text=text.replace('The Final Isle · v0.27','The Final Isle · v0.28')
ui.write_text(text)

menu=Path('menu.js')
text=menu.read_text().replace('version:"0.27"','version:"0.28"')
menu.write_text(text)

html=Path('index.html')
text=html.read_text().replace('v0.27 Test','v0.28 Test').replace('v0.27 TEST','v0.28 TEST')
html.write_text(text)

test=Path('tests/rules-v028.mjs')
test.write_text(r'''import assert from 'node:assert/strict';
import fs from 'node:fs';
import {newGame,current,normalizeSharedPools} from '../engine-v014.mjs';

const setup={players:3,mode:'ai',names:['Human','AI One','AI Two'],portraits:['014ea26d527fb00d.jpg','5d6137ac745946c3.jpg','c70de609c89d8c4c.jpg']};
const s=newGame(setup,()=>0);
assert.deepEqual(s.players.map(p=>p.name),['AI One','AI Two','Human'],'deterministic shuffle should change player order');
assert.deepEqual(s.players.map(p=>p.isAI),[true,true,false],'AI/human identity must move with each shuffled player');
assert.deepEqual(s.players.map(p=>[p.gold,p.supply]),[[2,2],[3,2],[3,3]],'starting resources should follow turn position after shuffle');
assert.equal(current(s).name,'AI One','first turn should be the first randomized seat');
assert.match(s.log[0],/^Turn order: AI One → AI Two → Human$/);

const legacy={mode:'ai',players:[{name:'Human'},{name:'AI One'},{name:'AI Two'}]};
normalizeSharedPools(legacy);
assert.deepEqual(legacy.players.map(p=>p.isAI),[false,true,true],'legacy saves should infer old human/AI roles');

const menu=fs.readFileSync(new URL('../menu.js',import.meta.url),'utf8');
const ui=fs.readFileSync(new URL('../voyage-v014.js',import.meta.url),'utf8');
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
assert.match(menu,/version:"0\.28"/);
assert.match(menu,/014ea26d527fb00d\.jpg/);
assert.doesNotMatch(menu,/randomPortraitSet|cyclePortrait\(/);
assert.match(menu,/captains-dash-final-clean-v3\.ogg/);
assert.match(menu,/captains-dash-victory-v2\.ogg/);
assert.match(ui,/current\(state\)\?\.isAI/,'AI turns must follow the shuffled player role');
assert.doesNotMatch(ui,/state\.mode==='ai'&&state\.turn>0/);
assert.match(ui,/state\.mode==='ai'&&p\.isAI\?'AI TURN':'YOUR TURN'/);
assert.match(html,/v0\.28 TEST/);
console.log('v0.28 assertions passed: player order randomized, AI roles preserved, original portraits retained.');
''')
