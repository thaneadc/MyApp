import {readFileSync,writeFileSync,copyFileSync} from 'node:fs';
import {DATA as old} from '../cards-v08.js';
const src=readFileSync('RULES-v0.14.txt','utf8');
const blocks=[...src.matchAll(/^(C\d{2}|T\d{2}|Z[123]-\d{2}|F\d) (.+)\n([\s\S]*?)(?=\n(?:C\d{2}|T\d{2}|Z[123]-\d{2}|F\d) |\n={5,})/gm)];
const aliases={'HEAVY FIRE':'GUNNER','EXPERIENCED NAVIGATOR':'NAVIGATOR','THE LOST CITY OF ORO':'LOST CITY OF ORO','THRONE OF THE PIRATE KING':"PIRATE KING’S THRONE"};
const normalize=s=>s.toUpperCase().replace(/[’']/g,'').replace(/^THE /,'');
const cards=blocks.map(([,id,name,b])=>{
 const kind=id[0]==='C'?'crew':id[0]==='T'?'treasure':id[0]==='F'?'final':'zone'+id[1];
 const art=(old.cards.find(c=>normalize(c.name)===normalize(aliases[name]||name))||old.cards.find(c=>c.id===id)).art;
 const c={id,name,kind,art};
 if(kind==='crew'){c.tier=b.match(/Tier: (.+)/)[1];c.cost=+b.match(/Cost: (\d+)/)[1];c.stats=Object.fromEntries(['Combat','Sailing','Search'].map(t=>[t,+b.match(new RegExp(t+': (\\d+)'))[1]]));c.text=b.split('Ability:')[1].trim();}
 else if(kind==='treasure'){c.type=b.match(/Type: (.+)/)[1];c.text=b.split('Effect:')[1].trim();}
 else if(kind==='final'){c.steps=[...b.matchAll(/Step [12]: (.+)\n([\s\S]*?)(?=Step 2:|Success:)/g)].map(([,name,t])=>({name,test:t.match(/Test Type: (\w+)/)[1].replace(/^Sail$/,'Sailing'),target:+t.match(/Target: (\d+)/)[1],text:t.trim()}));}
 else {c.zone=+id[1];c.test=b.match(/Test: (\w+)/)[1];c.target=+b.match(/Target: (\d+)/)[1];c.text=b.split('Reward:')[1].trim();c.reward={};for(const [,r,n] of c.text.matchAll(/^- (Gold|Supply|Crew|Veteran|Treasure) (\d+)/gm))c.reward[r.toLowerCase()]=+n;if(c.text.includes('Draw Treasure 2'))c.reward.drawTreasure=2;}
 return c;
});
if(cards.length!==81||cards.filter(c=>c.kind==='final').some(c=>c.steps.length!==2))throw Error('Card import incomplete');
writeFileSync('cards-v014.js','export const DATA = '+JSON.stringify({version:'0.14 Final',cards},null,2)+';\n');
console.log('Imported all 81 card types from v0.14 Final');
