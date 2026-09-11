import {DATA} from './cards-v014.js';
export {DATA};
export const CARDS=Object.fromEntries(DATA.cards.map(c=>[c.id,c]));
export const SAVE_KEY='captainsDashRules015';
export const FACES=['SKULL',0,0,1,2,'GOLD'];
export const LOCATIONS={tavern:'Tavern',market:'Market',dock:'Dock',work:'Harbor Work',quarters:'Crew Quarters',black:'Black Market',veteran:"Veteran’s Den",witch:'Sea Witch'};
const must=(v,m)=>{if(!v)throw Error(m)};
export const current=s=>s.players[s.turn];
export function normalizeSharedPools(s){
 if(!s||!Array.isArray(s.players))return s;
 const fallback=(key)=>s.players.find(p=>Array.isArray(p?.[key]))?.[key];
 if(!Array.isArray(s.market))s.market=[...(fallback('market')||[])];
 if(!Array.isArray(s.veteranMarket))s.veteranMarket=[...(fallback('veteranMarket')||[])];
 if(!Array.isArray(s.treasureDeck))s.treasureDeck=[...(fallback('treasureDeck')||[])];
 for(const p of s.players){delete p.market;delete p.veteranMarket;delete p.treasureDeck;delete p.crewDeck;delete p.veteranDeck}
 return s;
}
export function shuffle(xs,rng=Math.random){const a=[...xs];for(let i=a.length-1;i>0;i--){const j=Math.floor(rng()*(i+1));[a[i],a[j]]=[a[j],a[i]]}return a}
const instance=(s,id)=>({id,uid:'crew-'+s.nextId++,exhausted:false});
export function unlocked(s,z){return z===1||(z===2&&s.players.length===2)||s.progress[z-2]>=[2,2,1][z-2]}
export function locationOpen(s,l){return l==='black'?s.progress[1]>=1:l==='veteran'?s.progress[1]>=2:l==='witch'?unlocked(s,4):Object.hasOwn(LOCATIONS,l)}
export function legalWorker(s,l){return !s.location&&!s.exp&&!s.overflow&&locationOpen(s,l)&&(s.phase==='place'?s.workers[l]===null:s.workers[l]!==null&&l!==s.placed)}
export function available(s,id){const c=CARDS[id];return !!c&&(c.kind==='final'?unlocked(s,4)&&s.final[0]===id:c.zone&&unlocked(s,c.zone)&&s.stacks[c.zone].some(st=>st[0]===id))}
export function newGame(setup={},rng=Math.random){
 const s={version:'0.15',nextId:1,turn:0,round:1,status:'playing',mode:setup.mode||'local',phase:'place',placed:null,location:null,workers:Object.fromEntries(Object.keys(LOCATIONS).map(l=>[l,["tavern","dock"].includes(l)?true:null])),progress:[0,0,0],stacks:{},final:[],missionDiscard:[],treasureDiscard:[],crewDiscard:[],log:[],exp:null,overflow:null,blackRefreshed:false};
 s.players=Array.from({length:Math.max(2,Math.min(4,setup.players||2))},(_,i)=>({name:setup.names?.[i]||'Player '+(i+1),gold:i?3:2,supply:i>=2?3:2,crew:[instance(s,'C01')],treasures:[],blessing:null}));
 s.crewDeck=shuffle(DATA.cards.filter(c=>c.kind==='crew'&&c.tier==='Common').flatMap(c=>Array(c.id==='C01'?4-s.players.length:4).fill(c.id)),rng);
 s.veteranDeck=shuffle(DATA.cards.filter(c=>c.tier==='Veteran').flatMap(c=>Array(4).fill(c.id)),rng);
 s.market=s.crewDeck.splice(0,3);s.veteranMarket=s.veteranDeck.splice(0,3);s.treasureDeck=shuffle(DATA.cards.filter(c=>c.kind==='treasure').map(c=>c.id),rng);normalizeSharedPools(s);
 for(const z of [1,2,3]){const n=z===3?2:3,ids=shuffle(DATA.cards.filter(c=>c.zone===z).map(c=>c.id),rng).slice(0,n*2);s.stacks[z]=Array.from({length:n},(_,i)=>ids.slice(i*2,i*2+2))}
 s.final=shuffle(DATA.cards.filter(c=>c.kind==='final').map(c=>c.id),rng).slice(0,3);return s;
}
function log(s,t){s.log.unshift(t);s.log=s.log.slice(0,100)}
function endAction(s){s.exp=null;s.location=null;s.blackRefreshed=false;if(s.status!=='playing')return;if(s.phase==='place'){s.phase='take';return}s.phase='place';s.placed=null;s.turn=(s.turn+1)%s.players.length;if(!s.turn)s.round++}
const selected=(p,e)=>p.crew.filter(c=>e.crew.includes(c.uid)&&!c.exhausted);
const count=(p,e,id)=>selected(p,e).filter(c=>c.id===id).length;
const has=(e,id)=>e.treasures.includes(id);
export function testInfo(e){const c=CARDS[e.mission];return c.kind==='final'?c.steps[e.step||0]:c}
export function crewScore(p,e){const t=testInfo(e).test,z=CARDS[e.mission].zone||4;let n=selected(p,e).reduce((v,c)=>v+CARDS[c.id].stats[t],0);if(t==='Combat')n+=count(p,e,'C02')+count(p,e,'C10');if(t==='Sailing'&&z>=2)n+=count(p,e,'C03')+count(p,e,'C08');if(t==='Search')n+=count(p,e,'C11');return n}
export function baseScore(p,e){const t=testInfo(e).test,z=CARDS[e.mission].zone||4;let n=crewScore(p,e);const bonus={Combat:{T05:2,T08:1},Sailing:{T04:2},Search:{T01:1,T02:z===4?2:1,T10:1,T12:1}};for(const [id,v]of Object.entries(bonus[t]))if(has(e,id))n+=v;if(e.blessing===t)n+=3;if(e.powder&&t==='Combat')n+=2;return n}
export function totalScore(p,e){return baseScore(p,e)+e.dice.reduce((n,d)=>n+(typeof d==='number'?d:0),0)+(has(e,'T13')&&!e.dice.includes('SKULL')?2:0)+(testInfo(e).test==='Combat'&&count(p,e,'C15')&&e.dice.includes('GOLD')?1:0)}
export function supplyCost(p,z,treasures=p.treasures,crew=p.crew.filter(c=>!c.exhausted).map(c=>c.uid)){return Math.max(1,[1,3,6,9][z-1]-(treasures.includes('T18')?2:0)-p.crew.filter(c=>crew.includes(c.uid)&&!c.exhausted&&c.id==='C06').length)}
function discardCrew(s,p,uid){const c=p.crew.find(c=>c.uid===uid);must(c,'Choose an owned Crew');s.crewDiscard.push(c.id);p.crew=p.crew.filter(c=>c.uid!==uid)}
function checkCapacity(s){const p=current(s);s.overflow=p.crew.length>4?'crew':p.treasures.length>3?'treasure':null;return !!s.overflow}
function drawTreasure(s,rng){if(!s.treasureDeck.length){s.treasureDeck=shuffle(s.treasureDiscard,rng);s.treasureDiscard=[]}return s.treasureDeck.shift()}
function nextReward(s,rng){if(checkCapacity(s))return;const e=s.exp;if(!e)return endAction(s);const job=e.queue.shift();if(!job){e.phase='result';return}const choices=[];for(let i=0;i<job;i++){const id=drawTreasure(s,rng);if(id)choices.push(id)}if(!choices.length)return nextReward(s,rng);e.choices=choices;e.phase='treasure';}
function resolveOutcome(s,rng){const p=current(s),e=s.exp,c=CARDS[e.mission],t=testInfo(e).test;
 if(e.success){if(c.kind==='final'){s.status='won';s.winner=s.turn;e.phase='result';log(s,p.name+' wins '+c.name);return}
 const r=c.reward;p.gold+=(r.gold||0)+count(p,e,'C05')*2+count(p,e,'C11');p.supply+=r.supply||0;
 if(t==='Combat'&&has(e,'T08'))p.gold+=2;if(has(e,'T10'))p.supply++;if(t==='Search'&&c.target>=8&&has(e,'T12'))p.gold+=2;if(has(e,'T17'))p.gold+=2;if(has(e,'T20'))p.gold+=3;
 if(count(p,e,'C14')){const x=p.crew.find(c=>c.exhausted);if(x)x.exhausted=false}
 for(const [key,deck] of [['crew','crewDeck'],['veteran','veteranDeck']])for(let i=0;i<(r[key]||0);i++){const id=s[deck].shift();if(id)p.crew.push(instance(s,id))}
 for(let i=0;i<(r.treasure||0);i++)e.queue.push(count(p,e,'C09')?2:1);if(r.drawTreasure)e.queue.push(2);
 s.stacks[c.zone].find(st=>st[0]===c.id).shift();s.progress[c.zone-1]++;s.missionDiscard.unshift({id:c.id,player:p.name,result:'success'});
 }else{if(!e.dice.includes('SKULL')){if(has(e,'T03'))p.supply++;if(has(e,'T15'))p.gold+=2}if(has(e,'T20'))p.gold=Math.max(0,p.gold-1);if(c.kind==='final'&&s.final.length>1){s.final.shift();s.missionDiscard.unshift({id:c.id,player:p.name,result:'failed'})}}
 log(s,`${p.name}: ${c.name} — ${e.success?'SUCCESS':'FAIL'} (${e.total} ${t})`);nextReward(s,rng);
}
function checkResult(s,rng){const p=current(s),e=s.exp;e.total=totalScore(p,e);e.success=!e.dice.includes('SKULL')&&e.total>=testInfo(e).target;if(e.success&&CARDS[e.mission].kind==='final'&&e.step===0){log(s,p.name+' passed Final Step 1');e.firstDice=[...e.dice];e.step=1;e.phase='ready';e.dice=[];e.used=[];e.awarded={};e.success=null;return}if(!e.success){e.phase='loss';return}resolveOutcome(s,rng)}
function awardDice(p,e,newFaces){p.gold+=newFaces.filter(d=>d==='GOLD').length*(has(e,'T09')?2:1);e.awarded||={};if(testInfo(e).test==='Combat'&&has(e,'T06')&&e.dice.includes(2)&&!e.awarded.T06){p.gold++;e.awarded.T06=true}if(has(e,'T16')&&e.dice.includes('SKULL')&&e.dice.includes('GOLD')&&!e.awarded.T16){p.gold++;e.awarded.T16=true}}
export function controls(s){const e=s.exp;if(!e||e.phase!=='dice'||e.dice.includes('SKULL'))return [];const p=current(s),t=testInfo(e).test,opts=[];if(e.dice.includes(0)){for(const c of selected(p,e))if((c.id==='C04'&&t==='Search'||c.id==='C07'&&t==='Combat')&&!e.used.includes(c.uid))opts.push({id:c.uid,label:CARDS[c.id].name+' · reroll a 0'});if(has(e,'T14')&&!e.used.includes('T14'))opts.push({id:'T14',label:'Loaded Bones · 0 → 1'})}if(e.blessing==='fortune'&&!e.fortuneUsed)opts.push({id:'fortune',label:'Fortune · reroll one die'});return opts}
export function act(original,a,rng=Math.random){const s=normalizeSharedPools(structuredClone(original)),p=current(s),e=s.exp;must(s.version==='0.15'&&s.status==='playing','Start a v0.15 voyage');
 if(s.overflow){must(a.type==='discardOwned','Choose a card to discard first');if(s.overflow==='crew')discardCrew(s,p,a.id);else{must(p.treasures.includes(a.id),'Choose owned Treasure');p.treasures.splice(p.treasures.indexOf(a.id),1);s.treasureDiscard.push(a.id)}if(!checkCapacity(s)){if(e)nextReward(s,rng);else endAction(s)}return s}
 if(a.type==='worker'){must(legalWorker(s,a.location),'Choose a legal location: take a shared Pirate from another location, never the just-placed Pirate');s.location=a.location;if(s.phase==='place'){s.workers[a.location]=true;s.placed=a.location}else s.workers[a.location]=null;return s}
 if(e){
 if(a.type==='roll'){must(e.phase==='ready','Already rolled');e.dice=Array.from({length:CARDS[e.mission].zone||3},()=>FACES[Math.floor(rng()*6)]);awardDice(p,e,e.dice);e.phase='dice';if(e.dice.includes('SKULL'))checkResult(s,rng);return s}
 if(a.type==='control'){must(controls(s).some(o=>o.id===a.id),'Ability unavailable');if(a.id==='T14'){e.dice[e.dice.indexOf(0)]=1;e.used.push(a.id)}else{const index=a.id==='fortune'?a.index:e.dice.indexOf(0);must(Number.isInteger(index)&&index>=0&&index<e.dice.length&&e.dice[index]!=='SKULL','Choose a non-Skull die');if(a.id==='fortune')e.fortuneUsed=true;else e.used.push(a.id);const face=FACES[Math.floor(rng()*6)];e.dice[index]=face;awardDice(p,e,[face]);if(face==='SKULL')checkResult(s,rng)}return s}
 if(a.type==='resolve'){must(e.phase==='dice','Roll first');checkResult(s,rng);return s}
 if(a.type==='loss'){must(e.phase==='loss','No Crew loss pending');if(a.prevent==='surgeon'){must(count(p,e,'C12')&&!e.surgeonUsed,'Surgeon unavailable');e.surgeonUsed=true}else if(a.prevent==='medallion'){must(has(e,'T19'),'Medallion unavailable');p.treasures=p.treasures.filter(id=>id!=='T19');e.treasures=e.treasures.filter(id=>id!=='T19');s.treasureDiscard.push('T19')}else{const crew=selected(p,e),b=crew.find(c=>c.id==='C10');must(crew.some(c=>c.uid===a.id)&&(!b||b.uid===a.id),'Berserker must be lost first');discardCrew(s,p,a.id)}resolveOutcome(s,rng);return s}
 if(a.type==='keepTreasure'){must(e.phase==='treasure'&&e.choices.includes(a.id),'Select a drawn Treasure');p.treasures.push(a.id);s.treasureDiscard.push(...e.choices.filter(id=>id!==a.id));e.choices=[];nextReward(s,rng);return s}
 if(a.type==='finish'){must(e.phase==='result','Finish the Expedition');endAction(s);return s}throw Error('Finish the Expedition first');
 }
 must(s.location,'Place or take a Pirate first');const loc=s.location;
 if(a.type==='skip'){must(!s.blackRefreshed,'Finish Black Market');endAction(s);return s}
 if(a.type==='launch'){
 must(loc==='dock'&&available(s,a.mission),'Use Dock and choose an available Mission');must(Array.isArray(a.crew)&&a.crew.length>0&&a.crew.length<=4&&new Set(a.crew).size===a.crew.length&&a.crew.every(uid=>p.crew.some(c=>c.uid===uid&&!c.exhausted)),'Select 1–4 ready Crew');
 const c=CARDS[a.mission],z=c.zone||4,exp={mission:c.id,crew:a.crew,treasures:[...p.treasures],step:0,phase:'ready',dice:[],queue:[],used:[],awarded:{},blessing:p.blessing,powder:!!a.powder,fortuneUsed:false};
 const crew=selected(p,exp),vet=crew.filter(c=>CARDS[c.id].tier==='Veteran').length;
 if(c.id==='F4')must(crew.length===4&&vet>=2&&p.treasures.length>=2,'Requires 4 Crew, 2 Veterans and 2 Treasures');if(c.id==='F5')must(new Set(crew.map(c=>c.id)).size>=3&&vet>=1,'Requires 3 different Crew types and 1 Veteran');
 let gold=0;if(c.id==='F3'){if(a.payment==='treasure'){must(p.treasures.includes(a.sacrifice),'Choose Treasure to discard');p.treasures=p.treasures.filter(id=>id!==a.sacrifice);exp.treasures=[...p.treasures];s.treasureDiscard.push(a.sacrifice)}else gold=6}
 if(a.powder)must(has(exp,'T07')&&(c.test==='Combat'||c.steps?.some(st=>st.test==='Combat')),'Black Powder Horn requires a Combat test');
 const cost=supplyCost(p,z,exp.treasures,a.crew)+(a.powder?1:0);must(p.gold>=gold&&p.supply>=cost,'Not enough Gold or Supply');p.gold-=gold;p.supply-=cost;exp.paid=cost;p.blessing=null;s.exp=exp;return s;
 }
 if(a.type==='work'){must(loc==='work','Use Harbor Work');p.gold+=3}
 else if(a.type==='market'){must(loc==='market','Use Market');must(Number.isInteger(a.amount)&&a.amount>=1&&a.amount<=5&&p.gold>=a.amount,'Buy 1–5 Supply within your Gold');p.gold-=a.amount;p.supply+=a.amount}
 else if(a.type==='refresh'){must(loc==='black'&&!s.blackRefreshed,'Refresh unavailable');must(Array.isArray(a.ids)&&a.ids.length<=3,'Select up to 3 market cards');for(const id of a.ids){const index=s.market.indexOf(id);must(index>=0,'Select only available market copies');s.market.splice(index,1)}s.crewDeck=shuffle([...s.crewDeck,...a.ids],rng);while(s.market.length<3&&s.crewDeck.length)s.market.push(s.crewDeck.shift());s.blackRefreshed=true;return s}
 else if(a.type==='blackSkip'){must(loc==='black'&&s.blackRefreshed,'Refresh first')}
 else if(a.type==='recruit'){must(['tavern','veteran','black'].includes(loc)&&locationOpen(s,loc),'Use an unlocked recruitment location');must(loc!=='black'||s.blackRefreshed,'Refresh first');const market=loc==='veteran'?s.veteranMarket:s.market,deck=loc==='veteran'?s.veteranDeck:s.crewDeck;must(market.includes(a.id),'Crew unavailable');const cost=Math.max(0,CARDS[a.id].cost-(loc==='black'?1:0));must(p.gold>=cost,'Not enough Gold');p.gold-=cost;p.crew.push(instance(s,a.id));market.splice(market.indexOf(a.id),1);if(deck.length)market.push(deck.shift())}
 else if(a.type==='ready'){must(loc==='quarters','Use Crew Quarters');must(a.ids.length<=4&&new Set(a.ids).size===a.ids.length&&a.ids.every(uid=>p.crew.some(c=>c.uid===uid&&c.exhausted)),'Choose up to 4 exhausted Crew');for(const c of p.crew)if(a.ids.includes(c.uid))c.exhausted=false}
 else if(a.type==='bless'){must(loc==='witch'&&locationOpen(s,loc)&&p.gold>=3,'Sea Witch costs 3 Gold');must(['Combat','Sailing','Search','fortune'].includes(a.id),'Unknown blessing');p.gold-=3;p.blessing=a.id}
 else throw Error('Unknown action');
 log(s,p.name+' used '+LOCATIONS[loc]);if(!checkCapacity(s))endAction(s);return s;
}
