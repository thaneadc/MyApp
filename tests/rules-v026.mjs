import assert from 'node:assert/strict';
import fs from 'node:fs';

const menu=fs.readFileSync(new URL('../menu.js',import.meta.url),'utf8');
const ui=fs.readFileSync(new URL('../voyage-v014.js',import.meta.url),'utf8');
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');

assert.match(menu,/version:"0\.26"/);
assert.match(menu,/randomPortraitSet/,'New-game portraits should be randomized');
assert.match(menu,/normalizePortraits/,'Restored portrait selections should be normalized');
assert.match(menu,/used=new Set/,'Portrait selection should prevent duplicates');
assert.match(menu,/captain-v026-10\.svg|Array\.from\(\{length:10\}/,'Ten portrait choices should be available');
assert.match(menu,/captains-dash-final-clean-v3\.ogg/,'Final Mission should use Clean v3');
assert.match(menu,/captains-dash-victory-v2\.ogg/,'Victory should use Victory v2');
assert.match(menu,/soundtrack\.loop=mode!==['"]victory['"]/,'Victory music should be a one-shot');
assert.match(ui,/state\.status===['"]won['"]\?['"]victory['"]:unlocked\(state,4\)\?['"]final['"]:['"]adventure['"]/,'Music mode should follow game phase');
assert.match(html,/v0\.26 TEST/);
assert.match(html,/portraits stay unique/);
assert.match(html,/object-position:center 28%/,'Setup portrait should emphasize the face');

for(let i=1;i<=10;i++){
  const name=`captain-v026-${String(i).padStart(2,'0')}.svg`;
  const path=new URL(`../assets/${name}`,import.meta.url);
  assert.equal(fs.existsSync(path),true,`${name} must exist`);
  const svg=fs.readFileSync(path,'utf8');
  assert.match(svg,/viewBox="0 0 256 256"/);
  assert.match(svg,/Pirate captain portrait/);
}

for(const [name,min] of [['captains-dash-final-clean-v3.ogg',700000],['captains-dash-victory-v2.ogg',200000]]){
  const path=new URL(`../assets/${name}`,import.meta.url);
  assert.equal(fs.existsSync(path),true,`${name} must exist`);
  const raw=fs.readFileSync(path);
  assert.equal(raw.subarray(0,4).toString(),'OggS',`${name} must be OGG audio`);
  assert.ok(raw.length>min,`${name} looks too small`);
}

console.log('v0.26 assertions passed: unique randomized close-up pirate portraits, Final Clean v3, and Victory v2 music.');
