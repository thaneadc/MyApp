import assert from 'node:assert/strict';
import {DATA,CARDS,newGame,current,act,unlocked,legalWorker,baseScore,supplyCost,controls} from '../engine-v014.mjs';
let checks=0;const eq=(a,b)=>{assert.deepEqual(a,b);checks++},throws=(f)=>{assert.throws(f);checks++};
eq(DATA.cards.length,81);eq(DATA.cards.filter(c=>c.kind==='final').length,5);
for(const c of DATA.cards){if(c.kind==='crew')eq(Object.keys(c.stats),['Combat','Sailing','Search']);if(c.zone)assert(c.test.split(/\s*\+\s*/).every(t=>['Combat','Sailing','Search'].includes(t)));}
for(const n of [2,3,4]){const s=newGame({players:n});eq(s.market.length,3);eq(s.veteranMarket.length,3);eq(s.final.length,3);eq(s.players.map(p=>[p.gold,p.supply,p.crew.length]),[[2,2,1],[3,2,1],[3,3,1],[3,3,1]].slice(0,n));eq(unlocked(s,2),n===2);eq(Object.values(s.stacks).map(a=>a.map(st=>st.length)),[[2,2,2],[2,2,2],[2,2]]);}
let s;
for(const n of [2,3,4]){
 s=newGame({players:n});eq(s.workers.tavern,true);eq(s.workers.dock,true);throws(()=>act(s,{type:'work'}));
 for(let turn=0;turn<24;turn++){
  const player=s.turn,place=Object.keys(s.workers).find(l=>legalWorker(s,l));
  s=act(s,{type:'worker',location:place});s=act(s,{type:'skip'});
  eq(s.phase,'take');eq(s.turn,player);eq(legalWorker(s,place),false);throws(()=>act(s,{type:'worker',location:place}));
  const take=Object.keys(s.workers).find(l=>legalWorker(s,l));assert(take);
  s=act(s,{type:'worker',location:take});s=act(s,{type:'skip'});
  eq(s.turn,(player+1)%n);eq(Object.values(s.workers).filter(Boolean).length,2);eq(s.phase,'place');
 }
}
function expedition(id='Z1-01',crew=['C02'],treasures=[]){let s=newGame();const p=current(s);p.gold=30;p.supply=30;p.crew=crew.map((id,i)=>({id,uid:'test'+i,exhausted:false}));p.treasures=treasures;s.progress=[2,2,1];const zone=id.startsWith('F')?4:+id[1];for(let prev=1;prev<zone;prev++){const prior=DATA.cards.find(c=>c.zone===prev)?.id;if(prior)s.missionDiscard.unshift({id:prior,player:p.name,playerIndex:s.turn,result:'success'})}if(id.startsWith('F'))s.final=[id];else s.stacks[+id[1]][0]=[id];s.workers.dock=null;s=act(s,{type:'worker',location:'dock'});return act(s,{type:'launch',mission:id,crew:p.crew.map(c=>c.uid)})}
let e=expedition();eq(baseScore(current(e),e.exp),3);e=act(e,{type:'roll'},()=>.2);e=act(e,{type:'resolve'});eq(e.exp.success,true);eq(current(e).gold,35);eq(e.progress[0],3);
e=expedition('Z1-03',['C02']);eq(baseScore(current(e),e.exp),0);e=act(e,{type:'roll'},()=>.2);e=act(e,{type:'resolve'});eq(e.exp.phase,'loss');e=act(e,{type:'loss',id:'test0'});eq(current(e).crew.length,0);eq(e.stacks[1][0][0],'Z1-03');
e=expedition('Z2-01',['C02'],['T09']);let values=[0,.99];e=act(e,{type:'roll'},()=>values.shift());eq(e.exp.phase,'loss');eq(current(e).gold,32);eq(controls(e),[]);throws(()=>act(e,{type:'control',id:'fortune',index:0}));
e=expedition('Z1-02',['C04']);e=act(e,{type:'roll'},()=>.2);eq(controls(e).length,1);e=act(e,{type:'control',id:'test0'},()=>0);eq(e.exp.phase,'loss');
e=expedition('Z1-01',['C12']);eq(current(e).crew[0].exhausted,true);e=act(e,{type:'roll'},()=>0);e=act(e,{type:'loss',prevent:'surgeon'});eq(current(e).crew.length,1);eq(current(e).crew[0].exhausted,true);
e=expedition('Z1-01',['C10','C01']);e=act(e,{type:'roll'},()=>0);throws(()=>act(e,{type:'loss',id:'test1'}));e=act(e,{type:'loss',id:'test0'});eq(current(e).crew[0].id,'C01');
e=expedition('Z1-01',['C01'],['T19']);e=act(e,{type:'roll'},()=>0);e=act(e,{type:'loss',prevent:'medallion'});eq(current(e).treasures,[]);eq(e.treasureDiscard,['T19']);
e=expedition('Z3-01',['C06'],['T18']);eq(e.exp.paid,3);eq(supplyCost(current(e),1),1);
e=expedition('F1',['C14','C14','C14','C14']);eq(e.exp.paid,9);e=act(e,{type:'roll'},()=>.2);e=act(e,{type:'resolve'});eq(e.exp.step,1);eq(e.status,'playing');eq(e.exp.phase,'ready');eq(current(e).supply,21);eq(baseScore(current(e),e.exp),16);e=act(e,{type:'roll'},()=>.2);e=act(e,{type:'resolve'});eq(e.status,'won');
e=expedition('F1',['C14','C14','C14','C14']);e=act(e,{type:'roll'},()=>.2);e=act(e,{type:'resolve'});e=act(e,{type:'roll'},()=>0);e=act(e,{type:'loss',id:'test0'});eq(e.final,['F1']);eq(e.status,'playing');
e=expedition('F1',['C01']);e.final=['F1','F2','F3'];e=act(e,{type:'roll'},()=>0);e=act(e,{type:'loss',id:'test0'});eq(e.final,['F2','F3']);
e=expedition('F4',['C01']);eq(e.exp.mission,'F4');e=expedition('F5',['C01']);eq(e.exp.mission,'F5');e=expedition('F3',['C14']);eq(current(e).gold,30);
s=newGame();s.progress=[2,1,0];eq(legalWorker(s,'black'),true);eq(legalWorker(s,'veteran'),false);s.progress[1]=2;eq(legalWorker(s,'veteran'),true);eq(unlocked(s,3),true);
s=newGame();s.workers.tavern=null;current(s).gold=30;current(s).crew=Array.from({length:4},(_,i)=>({id:'C01',uid:'x'+i,exhausted:false}));s=act(s,{type:'worker',location:'tavern'});s=act(s,{type:'recruit',id:s.market[0]});eq(s.overflow,'crew');throws(()=>act(s,{type:'worker',location:'work'}));s=act(s,{type:'discardOwned',id:'x0'});eq(current(s).crew.length,4);eq(s.players[0].crew.length,4);eq(s.turn,0);eq(s.phase,'take');
// Save/resume keeps the paid Expedition and the intermediate worker phase.
e=expedition();eq(JSON.parse(JSON.stringify(e)),e);throws(()=>act(e,{type:'launch',mission:'Z1-01',crew:['test0']}));
console.log(`${checks} v0.15 assertions passed: setup, stats, worker phases, dice, protection, rewards, caps, Final tests and resume.`);
