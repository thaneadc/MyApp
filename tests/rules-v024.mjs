import assert from 'node:assert/strict';
import {newGame,act} from '../engine-v014.mjs';

const paid=newGame({players:2},()=>0.42);
paid.location='black';
paid.players[0].gold=2;
const paidIds=[...paid.market.slice(0,2)];
const refreshed=act(paid,{type:'refresh',ids:paidIds},()=>0.31);
assert.equal(refreshed.players[0].gold,0,'Refreshing two Black Market cards costs 2 Gold');
assert.equal(refreshed.blackRefreshed,true);
assert.equal(refreshed.market.length,3,'Common Crew market refills to three face-up cards');

const poor=newGame({players:2},()=>0.42);
poor.location='black';
poor.players[0].gold=1;
assert.throws(()=>act(poor,{type:'refresh',ids:poor.market.slice(0,2)},()=>0.31),/Not enough Gold/,'Cannot refresh more cards than Gold available');

const none=newGame({players:2},()=>0.42);
none.location='black';
assert.throws(()=>act(none,{type:'refresh',ids:[]},()=>0.31),/Select 1–3 market cards/,'Black Market refresh must choose at least one card');

console.log('v0.24 assertions passed: Black Market refresh costs 1 Gold per card and validates affordability.');
