import assert from 'node:assert/strict';
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
