import assert from 'node:assert/strict';
import {FACES,CARDS,newGame,available,playerZoneEligible,playerCompletedMissions} from '../engine-v014.mjs';

assert.deepEqual(FACES,['SKULL',0,0,1,1,2,2,'GOLD']);
assert.equal(FACES.length,8);
assert.equal(FACES.filter(x=>x==='SKULL').length,1);
assert.equal(FACES.filter(x=>x===0).length,2);
assert.equal(FACES.filter(x=>x===1).length,2);
assert.equal(FACES.filter(x=>x===2).length,2);
assert.equal(FACES.filter(x=>x==='GOLD').length,1);

const s=newGame({players:2},()=>0.42);
const z1=s.stacks[1][0][0],z2=s.stacks[2][0][0];
assert.equal(playerZoneEligible(s,1,0),true);
assert.equal(playerZoneEligible(s,2,0),false,'Zone II requires this captain to clear Zone I while Zone I Missions remain');
assert.equal(available(s,z2),false,'Zone II Mission must not be available before personal Zone I clear');

s.missionDiscard.unshift({id:z1,player:s.players[0].name,playerIndex:0,result:'success'});
assert.deepEqual(playerCompletedMissions(s,0),[z1]);
assert.equal(playerZoneEligible(s,2,0),true);
assert.equal(available(s,z2),true);
assert.equal(playerZoneEligible(s,2,1),false,'Other captain does not inherit the clear');

const noPrior=newGame({players:2},()=>0.37);
noPrior.stacks[1]=noPrior.stacks[1].map(()=>[]);
assert.equal(playerZoneEligible(noPrior,2,0),true,'Deeper Zone becomes eligible if no prior-Zone Mission remains');

const z3state=newGame({players:3},()=>0.31);
z3state.progress[0]=2;
z3state.progress[1]=2;
const z2id=z3state.stacks[2][0][0];
assert.equal(playerZoneEligible(z3state,3,0),false);
z3state.missionDiscard.unshift({id:z2id,player:z3state.players[0].name,playerIndex:0,result:'success'});
assert.equal(playerZoneEligible(z3state,3,0),true);

const finalState=newGame({players:3},()=>0.28);
finalState.progress=[2,2,1];
const z3id=finalState.stacks[3][0][0];
assert.equal(playerZoneEligible(finalState,4,0),false);
finalState.missionDiscard.unshift({id:z3id,player:finalState.players[0].name,playerIndex:0,result:'success'});
assert.equal(playerZoneEligible(finalState,4,0),true);
assert.ok(CARDS[z3id].zone===3);

console.log('v0.22 assertions passed: D8 distribution, personal Zone progression, empty-prior-zone exception, completed Mission ownership.');
