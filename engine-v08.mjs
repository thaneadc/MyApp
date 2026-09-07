import {DATA} from './cards-v08.js';
export {DATA};
export const CARDS=Object.fromEntries(DATA.cards.map(c=>[c.id,c]));
export const SAVE_KEY='captainsDashRules08';
export const FACES=['SKULL',0,0,1,2,'GOLD'];
export const DEFAULTS={workerBlocking:false,crewCopies:4,veteranIncludesElite:true,witchCost:2,atlasHighTargets:[4,6,10],finalCheck:'participating Crew and active Treasure',step1Exhaustion:'exhausted Crew contributes no Power or ability'};
const clone=x=>JSON.parse(JSON.stringify(x));
const must=(ok,msg)=>{if(!ok)throw Error(msg)};
export function shuffle(a,rng=Math.random){a=[...a];for(let i=a.length-1;i>0;i--){let j=Math.floor(rng()*(i+1));[a[i],a[j]]=[a[j],a[i]]}return a}
export function instance(s,id){return {id,uid:'card-'+s.nextId++,exhausted:false}}
export function current(s){return s.players[s.turn]}
export function unlocked(s,z){return z===1||s.progress[z-2]>=[2,3,1][z-2]}
export function newGame(setup={},rng=Math.random){
 const s={version:'rules-0.8.1',nextId:1,turn:0,round:1,status:'playing',mode:setup.mode||'local',progress:[0,0,0],stacks:{},final:[],missionDiscard:[],treasureDiscard:[],crewDiscard:[],log:[],exp:null,pending:null,defaults:DEFAULTS};
 s.players=Array.from({length:Math.max(2,Math.min(4,setup.players||2))},(_,i)=>({name:setup.names?.[i]||'Player '+(i+1),gold:i?4:3,supply:i>=2?5:4,crew:[],treasures:[],blessing:null,discount:0}));
 for(const p of s.players)p.crew=[instance(s,'C01'),instance(s,'C01')];
 s.crewDeck=shuffle(DATA.cards.filter(c=>c.kind==='crew'&&c.tier==='Common').flatMap(c=>Array(4).fill(c.id)),rng);
 s.veteranDeck=shuffle(DATA.cards.filter(c=>c.kind==='crew'&&c.tier!=='Common').flatMap(c=>Array(4).fill(c.id)),rng);
 s.market=s.crewDeck.splice(0,5);s.veteranMarket=s.veteranDeck.splice(0,3);
 s.treasureDeck=shuffle(DATA.cards.filter(c=>c.kind==='treasure').map(c=>c.id),rng);
 for(const z of [1,2,3]){const n=z===3?2:3;const ids=shuffle(DATA.cards.filter(c=>c.zone===z).map(c=>c.id),rng).slice(0,n*2);s.stacks[z]=Array.from({length:n},(_,i)=>ids.slice(i*2,i*2+2))}
 s.final=shuffle(DATA.cards.filter(c=>c.kind==='final').map(c=>c.id),rng).slice(0,5);return s;
}
function log(s,t){s.log.unshift(t);s.log=s.log.slice(0,100)}
function endTurn(s){s.pending=null;s.exp=null;if(s.status!=='playing')return;s.turn=(s.turn+1)%s.players.length;if(s.turn===0)s.round++}
export function available(s,id){const c=CARDS[id];return !!c&&(c.kind==='final'?s.final[0]===id&&unlocked(s,4):!!c.zone&&unlocked(s,c.zone)&&s.stacks[c.zone].some(st=>st[0]===id))}
function selected(p,e){return p.crew.filter(c=>e.crew.includes(c.uid)&&!c.exhausted)}
function hasCrew(p,e,id){return selected(p,e).some(c=>c.id===id)}
function hasT(e,id){return e.treasures.includes(id)}
function removeCrew(s,p,uid){const c=p.crew.find(c=>c.uid===uid);must(c,'Crew unavailable');p.crew=p.crew.filter(c=>c.uid!==uid);s.crewDiscard.push(c.id)}
export function crewPower(p,e){const z=CARDS[e.mission].zone||4;return selected(p,e).reduce((n,c)=>n+(c.id==='C05'&&z>=2?2:CARDS[c.id].power),0)}
export function basePower(p,e){const z=CARDS[e.mission].zone||4;return crewPower(p,e)+(z>=3?e.treasures.length:0)+(z===4&&hasT(e,'T02')?1:0)+(e.blessing==='war'?1:0)+(e.edge||0)}
export function supplyCost(p,z,treasures){return Math.max(1,[1,3,6,9][z-1]-(treasures.includes('T18')?1:0)-(p.blessing==='wind'?1:0))}
export function finalOptions(p,e){const ready=selected(p,e),v=ready.filter(c=>CARDS[c.id].tier!=='Common').length;const id=e.mission;
 return {check:(id==='F1'&&e.treasures.length>=3)||(id==='F2'&&v>=2)||(id==='F5'&&ready.length===4&&v>=2&&e.treasures.length>=2)||(id==='F6'&&crewPower(p,e)>=10)||(id==='F7'&&new Set(ready.map(c=>c.id)).size>=3&&v>=1),veterans:ready.filter(c=>CARDS[c.id].tier!=='Common')};
}
function drawTreasure(s,rng){if(!s.treasureDeck.length){s.treasureDeck=shuffle(s.treasureDiscard,rng);s.treasureDiscard=[]}return s.treasureDeck.shift()}
function rewardQueue(s,p,count,drawN=1){for(let i=0;i<count;i++)s.exp.queue.push({type:'treasure',draw:Math.max(drawN,hasCrew(p,s.exp,'C10')?2:1)})}
function nextReward(s,rng){const e=s.exp,p=current(s);if(!e.queue.length){e.phase='result';return}const job=e.queue.shift();const choices=[];for(let i=0;i<job.draw;i++){const id=drawTreasure(s,rng);if(id)choices.push(id)}if(!choices.length)return nextReward(s,rng);e.choices=choices;e.phase='treasure';}
function completeResolution(s,rng){const e=s.exp,p=current(s),c=CARDS[e.mission],z=c.zone||4;
 if(hasCrew(p,e,'C08'))p.supply+=Math.floor(e.paid/2);
 if(e.success){
  if(c.kind==='final'){s.status='won';s.winner=s.turn;e.phase='result';log(s,p.name+' conquered '+c.name);return}
  const r=c.reward;p.gold+=r.gold||0;p.supply+=r.supply||0;
  if(hasCrew(p,e,'C04'))p.gold++;
  if(hasT(e,'T04'))p.discount++;
  if(hasT(e,'T08')&&!e.control)p.gold+=2;
  if(hasT(e,'T10'))p.supply++;
  if(hasT(e,'T12')&&c.target>=DEFAULTS.atlasHighTargets[z-1])p.gold+=2;
  if(hasT(e,'T17'))p.gold+=2;if(hasT(e,'T20'))p.gold+=3;
  if(hasCrew(p,e,'C14')){const ex=p.crew.find(x=>x.exhausted);if(ex)ex.exhausted=false}
  for(let i=0;i<(r.crew||0);i++){const id=s.crewDeck.shift();if(id)p.crew.push(instance(s,id))}
  for(let i=0;i<(r.veteran||0);i++){const id=s.veteranDeck.shift();if(id)p.crew.push(instance(s,id))}
  while(s.market.length<5&&s.crewDeck.length)s.market.push(s.crewDeck.shift());
  while(s.veteranMarket.length<3&&s.veteranDeck.length)s.veteranMarket.push(s.veteranDeck.shift());
  rewardQueue(s,p,r.treasure||0);if(r.drawTreasure)rewardQueue(s,p,1,r.drawTreasure);
  s.stacks[z].find(st=>st[0]===c.id).shift();s.progress[z-1]++;s.missionDiscard.unshift({id:c.id,player:p.name,result:'success'});
 }else{
  if(hasCrew(p,e,'C06'))p.supply++;
  if(hasT(e,'T03')&&!e.dice.includes('SKULL'))p.supply++;
  if(hasT(e,'T15')&&!e.dice.includes('SKULL'))p.gold+=2;
  if(hasT(e,'T20'))p.gold=Math.max(0,p.gold-1);
  if(c.kind==='final'){s.final.shift();s.missionDiscard.unshift({id:c.id,player:p.name,result:'failed'});if(!s.final.length)s.status='shared_loss'}
 }
 log(s,`${p.name}: ${c.name} — ${e.success?'SUCCESS':'FAILED'} (${e.total} Power)`);nextReward(s,rng);
}
function checkResult(s,rng){const e=s.exp,p=current(s),c=CARDS[e.mission];e.total=basePower(p,e)+e.dice.reduce((n,d)=>n+(typeof d==='number'?d:0),0)+(e.bonus||0);e.success=!e.dice.includes('SKULL')&&e.total>=c.target;e.queue=[];
 // Snapshot abilities before losing or exhausting the Crew that provided them.
 e.resolutionCrew=selected(p,e).map(x=>x.uid);
 if(!e.success&&e.crew.some(uid=>p.crew.some(x=>x.uid===uid))){e.phase='loss';return}
 completeResolution(s,rng);
}
export function controls(s){const e=s.exp,p=current(s);if(!e||e.phase!=='dice'||e.control||e.dice.includes('SKULL'))return [];
 const ids=[];const zero=e.dice.includes(0),gold=e.dice.includes('GOLD');const total=basePower(p,e)+e.dice.reduce((n,d)=>n+(typeof d==='number'?d:0),0);
 if(zero&&hasCrew(p,e,'C07'))ids.push('C07');if(zero&&hasT(e,'T14'))ids.push('T14');
 if(hasT(e,'T13'))ids.push('T13');if(gold&&hasCrew(p,e,'C15'))ids.push('C15');
 if(hasCrew(p,e,'C09')&&CARDS[e.mission].target-total===1)ids.push('C09');
 if(e.blessing==='fortune')ids.push('fortune');return ids;
}
function diceBonuses(p,e){
 e.awarded ||= {};
 const g=e.dice.includes('GOLD');
 for(const [id,trigger,resource] of [['C02',g&&hasCrew(p,e,'C02'),'gold'],['C03',g&&hasCrew(p,e,'C03'),'supply'],['T06',e.dice.includes(2)&&hasT(e,'T06'),'gold'],['T16',g&&e.dice.includes('SKULL')&&hasT(e,'T16'),'gold']]){
  if(trigger&&!e.awarded[id]){p[resource]++;e.awarded[id]=true}
 }
}
export function act(original,a,rng=Math.random){const s=clone(original),p=current(s);must(s.status==='playing','This voyage is finished');
 const e=s.exp;
 if(a.type==='launch'){
  must(!e&&!s.pending,'Finish the current action');must(available(s,a.mission),'Mission unavailable');
  const c=CARDS[a.mission],z=c.zone||4;must(a.crew.length<=4&&a.crew.length>0&&new Set(a.crew).size===a.crew.length,'Select 1–4 different Crew cards');must(a.crew.every(uid=>p.crew.some(x=>x.uid===uid&&!x.exhausted)),'Select ready Crew');
  must(a.treasures.length<=3&&new Set(a.treasures).size===a.treasures.length&&a.treasures.every(id=>p.treasures.includes(id)),'Select up to 3 owned Treasures');
  const exp={mission:a.mission,crew:a.crew,treasures:a.treasures,phase:'ready',dice:[],paid:0,edge:0,bonus:0,control:null,blessing:p.blessing,queue:[]};
  const base=supplyCost(p,z,a.treasures);let extra=0,gold=0;const opt=a.approach||'skip';const fo=finalOptions(p,exp);
  if(c.kind==='final'&&opt!=='skip'){
   if(opt==='check'){must(fo.check,'Favored Approach not met');exp.edge=1}
   else if(c.id==='F2'&&opt==='sacrifice'){must(a.crew.includes(a.sacrifice),'Choose participating Crew to sacrifice');removeCrew(s,p,a.sacrifice);exp.crew=exp.crew.filter(x=>x!==a.sacrifice);exp.edge=1}
   else if(c.id==='F3'&&opt==='supply'){extra=3;exp.edge=1}
   else if(c.id==='F3'&&opt==='exhaust'){must(fo.veterans.some(x=>x.uid===a.sacrifice),'Choose a ready participating Veteran');p.crew.find(x=>x.uid===a.sacrifice).exhausted=true;exp.edge=1}
   else if(c.id==='F4'&&opt==='gold'){gold=6;exp.edge=1}
   else if(c.id==='F4'&&opt==='treasure'){must(a.treasures.includes(a.sacrifice),'Choose active Treasure');p.treasures=p.treasures.filter(x=>x!==a.sacrifice);exp.treasures=exp.treasures.filter(x=>x!==a.sacrifice);s.treasureDiscard.push(a.sacrifice);exp.edge=1}
   else if(c.id==='F8'&&opt==='safe'){gold=3;extra=2;exp.edge=1}
   else throw Error('Invalid Final approach');
  }
  if(a.powder){must(exp.treasures.includes('T07'),'Black Powder Horn required');extra++}
  must(p.supply>=base+extra&&p.gold>=gold,'Insufficient Gold or Supply');p.supply-=base+extra;p.gold-=gold;if(a.powder)p.gold+=2;
  exp.paid=base+extra;p.blessing=null;s.exp=exp;log(s,p.name+' sails to '+c.name);return s;
 }
 if(e){
  if(a.type==='roll'){must(e.phase==='ready','Dice already rolled');e.dice=Array.from({length:CARDS[e.mission].kind==='final'?3:CARDS[e.mission].zone},()=>FACES[Math.floor(rng()*6)]);const g=e.dice.filter(d=>d==='GOLD').length;p.gold+=g;
   if(g&&hasT(e,'T09'))p.gold+=g;diceBonuses(p,e);
   e.phase='dice';if(e.dice.includes('SKULL'))checkResult(s,rng);return s;
  }
  if(a.type==='control'){
   must(controls(s).includes(a.id),'Dice Control unavailable');e.control=a.id;
   if(['C07','T14'].includes(a.id))e.dice[e.dice.indexOf(0)]=1;
   if(['T13','C15','C09'].includes(a.id))e.bonus++;
   if(a.id==='C09'){const crew=p.crew.find(x=>e.crew.includes(x.uid)&&x.id==='C09'&&!x.exhausted);e.usedSharpshooter=crew.uid;/* Exhaust after resolution; its participating Power still counts. */}
   if(a.id==='fortune'){must(Number.isInteger(a.index)&&a.index>=0&&a.index<e.dice.length&&e.dice[a.index]!=='SKULL','Select non-Skull die');const face=FACES[Math.floor(rng()*6)];e.dice[a.index]=face;if(face==='GOLD')p.gold+=1+(hasT(e,'T09')?1:0);diceBonuses(p,e);if(face==='SKULL')checkResult(s,rng)}return s;
  }
  if(a.type==='resolve'){must(e.phase==='dice','Roll first');checkResult(s,rng);return s}
  if(a.type==='loss'){
   must(e.phase==='loss','No Crew loss pending');const participating=p.crew.filter(x=>e.crew.includes(x.uid));
   // Capture end-of-expedition passive sources before prevention / casualty.
   const refund=hasCrew(p,e,'C08')?Math.floor(e.paid/2):0;const hidden=hasCrew(p,e,'C06');
   if(a.prevent==='surgeon'){const surgeon=selected(p,e).find(x=>x.id==='C12');must(surgeon,'Ready participating Surgeon required');surgeon.exhausted=true}
   else if(a.prevent==='medallion'){must(hasT(e,'T19'),'Active Medallion required');p.treasures=p.treasures.filter(x=>x!=='T19');e.treasures=e.treasures.filter(x=>x!=='T19');s.treasureDiscard.push('T19')}
   else {const berserker=participating.find(x=>x.id==='C11');must(participating.some(x=>x.uid===a.uid),'Choose participating Crew');must(!berserker||berserker.uid===a.uid,'Berserker must be lost first');if(hasT(e,'T05'))p.gold+=2;removeCrew(s,p,a.uid)}
   // Account for abilities belonging to the lost card exactly once.
   if(refund&&!hasCrew(p,e,'C08'))p.supply+=refund;if(hidden&&!hasCrew(p,e,'C06'))p.supply++;
   completeResolution(s,rng);return s;
  }
  if(a.type==='keepTreasure'){must(e.phase==='treasure'&&e.choices.includes(a.id),'Choose a revealed Treasure');p.treasures.push(a.id);s.treasureDiscard.push(...e.choices.filter(id=>id!==a.id));e.choices=[];nextReward(s,rng);return s}
  if(a.type==='finish'){must(e.phase==='result','Finish resolution first');if(e.usedSharpshooter){const c=p.crew.find(c=>c.uid===e.usedSharpshooter);if(c)c.exhausted=true}endTurn(s);return s}
  throw Error('Finish your Expedition first');
 }
 if(a.type==='work'){must(!s.pending,'Finish Black Market recruitment');p.gold+=2;log(s,p.name+' worked at the harbor (+2 Gold)');endTurn(s)}
 else if(a.type==='market'){must(!s.pending,'Finish current action');must(Number.isInteger(a.amount)&&a.amount>=1&&a.amount<=5&&a.amount<=p.gold,'Buy 1–5 Supply within your Gold');p.gold-=a.amount;p.supply+=a.amount;endTurn(s)}
 else if(a.type==='blackRefresh'){must(!s.pending,'Market already refreshed');s.crewDeck=shuffle([...s.crewDeck,...s.market],rng);s.market=s.crewDeck.splice(0,5);s.pending='black';}
 else if(a.type==='blackSkip'){must(s.pending==='black','No refresh pending');endTurn(s)}
 else if(a.type==='recruit'){const isVet=a.pool==='veteran';must(!s.pending||(!isVet&&s.pending==='black'),'Finish current action');const market=isVet?s.veteranMarket:s.market,deck=isVet?s.veteranDeck:s.crewDeck;must(market.includes(a.id),'Crew unavailable');const price=Math.max(0,CARDS[a.id].cost-(s.pending==='black'?1:0)-p.discount);must(p.gold>=price,'Not enough Gold');p.gold-=price;p.discount=0;p.crew.push(instance(s,a.id));market.splice(market.indexOf(a.id),1);if(deck.length)market.push(deck.shift());endTurn(s)}
 else if(a.type==='ready'){must(!s.pending,'Finish current action');must(a.ids.length>=1&&a.ids.length<=2&&new Set(a.ids).size===a.ids.length&&a.ids.every(uid=>p.crew.some(c=>c.uid===uid&&c.exhausted)),'Select 1–2 exhausted Crew');for(const c of p.crew)if(a.ids.includes(c.uid))c.exhausted=false;endTurn(s)}
 else if(a.type==='bless'){must(!s.pending,'Finish current action');must(['wind','war','sight','fortune'].includes(a.id)&&p.gold>=2,'Blessing costs 2 Gold');must(!p.blessing,'Use your current Blessing first');p.gold-=2;p.blessing=a.id;endTurn(s)}
 else throw Error('Unknown action');return s;
}
