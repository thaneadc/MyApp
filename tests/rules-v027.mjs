import assert from 'node:assert/strict';
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
