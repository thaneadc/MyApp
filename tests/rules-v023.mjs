import assert from 'node:assert/strict';
import fs from 'node:fs';
import {newGame,act} from '../engine-v014.mjs';

const s=newGame({players:2},()=>0.41);
s.players[0].crew[0].exhausted=true;
s.players[0].crew.push({id:'C01',uid:'crew-v023-test',exhausted:true});
s.location='quarters';
const rested=act(s,{type:'ready'});
assert.equal(rested.players[0].crew.every(c=>!c.exhausted),true,'Crew Quarters must ready every exhausted Crew');
assert.equal(rested.location,null,'Crew Quarters action should resolve normally');
assert.equal(rested.phase,'take','Place-phase Crew Quarters action should continue to take phase');

const ui=fs.readFileSync(new URL('../voyage-v014.js',import.meta.url),'utf8');
const css=fs.readFileSync(new URL('../voyage-table.css',import.meta.url),'utf8');
assert.match(ui,/quartersReadyAll/);
assert.match(ui,/prepExpeditionLayout/);
assert.match(ui,/binocularLens/);
assert.match(ui,/helmHandle/);
assert.doesNotMatch(ui,/name="ready"/,'Crew Quarters must not show per-Crew ready checkboxes');
assert.match(css,/\.prepCrewChoice/);
assert.match(css,/\.quartersReadyAll/);
assert.match(css,/\.expMiniCard\{flex:0 0 176px/);

console.log('v0.23 assertions passed: Crew Quarters readies all Crew, no per-Crew selection, refined Expedition layout and maritime icons.');
