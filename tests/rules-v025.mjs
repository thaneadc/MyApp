import assert from 'node:assert/strict';
import fs from 'node:fs';
import {newGame,act} from '../engine-v014.mjs';

const setup={players:3,mode:'ai',portraits:['captain-alt-01.svg','captain-alt-02.svg','captain-alt-03.svg']};
let s=newGame(setup,()=>0.31);
assert.equal(s.players[0].portrait,'captain-alt-01.svg');
assert.equal(s.players[1].portrait,'captain-alt-02.svg');
assert.equal(s.players[2].portrait,'captain-alt-03.svg');

s.turn=1;
s.players[1].crew[0].exhausted=true;
s.location='quarters';
s=act(s,{type:'ready'});
assert.equal(s.players[1].crew.every(c=>!c.exhausted),true,'AI Crew Quarters must ready every exhausted Crew');
assert.equal(s.log.some(x=>/rested at Crew Quarters/.test(x)),true,'Crew Quarters should log the ready-all result');

const menu=fs.readFileSync(new URL('../menu.js',import.meta.url),'utf8');
const ui=fs.readFileSync(new URL('../voyage-v014.js',import.meta.url),'utf8');
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
for(let i=1;i<=6;i++) assert.match(menu,new RegExp(`captain-alt-0${i}\\.svg`));
assert.match(menu,/portraits:selectedPortraits\.slice\(0,count\)/);
assert.match(menu,/cyclePortrait/);
assert.match(ui,/portraitFor=/);
assert.match(ui,/aiDelayOverride=2200/);
assert.match(ui,/tired&&ready<=1/);
assert.match(html,/Tap a portrait to change captain/);
console.log('v0.25 assertions passed: AI Crew Quarters readies Crew and selectable captain portraits persist into game state.');
