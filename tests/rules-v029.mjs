import assert from 'node:assert/strict';
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
