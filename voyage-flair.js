export const banter={
 tavern:"Fresh hands, tall tales. Hire the one who lies least.",
 market:"Even legends need lunch. The barrels cost extra.",
 dock:"The sea owes us a fortune. Let's collect.",
 work:"Honest work? Keep this quiet at the tavern.",
 quarters:"Wake up, you magnificent collection of bad decisions.",
 black:"No receipts. No questions. Especially no refunds.",
 veteran:"These old sea dogs charge for the scars, too.",
 witch:"A little magic, a little gold. What could possibly go wrong?"
};
export function reducedMotion(){return matchMedia('(prefers-reduced-motion: reduce)').matches||document.body.classList.contains('reduce')}
export function hat(){return '<img class="silverHat" src="assets/silver-pirate-hat.png" alt="Shared silver pirate hat">'}
export function workerHtml(s,id,label){const occupied=s.workers[id]!==null;return `${occupied?hat():''}<span class="spotHint">${label}</span>`}
export function animateWorker(root,id,phase,done){const spot=root.querySelector(`[data-worker="${id}"]`);if(!spot||reducedMotion()){done();return}const ghost=document.createElement('span');ghost.className='movingHat '+phase;ghost.innerHTML=hat();spot.append(ghost);root.setAttribute('aria-busy','true');setTimeout(()=>{ghost.remove();root.removeAttribute('aria-busy');done()},480)}
export function resultFlash(host,success,step=false){const el=document.createElement('div');el.className='missionFlash '+(success?'success':'failure');el.setAttribute('role','status');el.innerHTML=`<span>${success?'✦':'☠'}</span><strong>${step?'FIRST TEST CONQUERED!':success?'MISSION CONQUERED!':'THE SEA BITES BACK!'}</strong><p>${step?'One more test, Captain. Keep your hat on.':success?'A fine haul. Try not to look too smug.':'We lost this one. The legend is not over.'}</p>`;host.append(el);setTimeout(()=>el.remove(),reducedMotion()?900:1700)}
export const endings={
 F1:{theme:'oro',title:'THE GOLDEN CITY IS YOURS',line:'Oro opens its gates. Your crew will never pay for a drink again.',symbol:'✦',effect:'goldfall'},
 F2:{theme:'fortress',title:'SKULL FORTRESS HAS FALLEN',line:'The guardian is beaten. Hoist your flag where fear once ruled.',symbol:'⚑',effect:'banners'},
 F3:{theme:'temple',title:'THE CURSE IS BROKEN',line:'The temple falls silent. Even the ghosts owe you a thank-you.',symbol:'◈',effect:'runes'},
 F4:{theme:'king',title:'LONG LIVE THE PIRATE KING',line:'The throne is reclaimed. A crown suits that troublesome head.',symbol:'♛',effect:'coronation'},
 F5:{theme:'sirens',title:'THE SIRENS SING YOUR LEGEND',line:'Their spell is broken. The horizon belongs to your crew.',symbol:'♫',effect:'tides'}
};
export function finale(s,cards,art,esc,button){const id=s.exp?.mission||s.final[0],c=cards[id],e=endings[id]||endings.F1,p=s.players[s.winner??s.turn];return `<section class="finale ${e.theme}" aria-label="Final mission victory"><div class="finaleBackdrop">${art(c)}</div><div class="endingParticles ${e.effect}" aria-hidden="true">${Array.from({length:24},(_,i)=>`<i style="--i:${i}">${e.symbol}</i>`).join('')}</div><div class="finaleContent"><div class="victoryEmblem">${e.symbol}</div><p class="eyebrow">${esc(c.name)} · FINAL VICTORY</p><h1>${e.title}</h1><h2>Congratulations, ${esc(p.name)}!</h2><p>${e.line}</p><div class="victoryStats">${p.gold} Gold · ${p.supply} Supply · ${p.crew.length} Crew · ${p.treasures.length} Treasures</div><div>${button('replayEnding','Replay celebration')}${button('history','Voyage history')}${button('menu','Main Menu')}</div><p class="endingCredit">Designed by Thanead Chiawchanlikit</p></div></section>`}
export function guideGallery(){return `<div class="guideGallery">${[1,2,3,4].map(n=>`<figure><figcaption>Game Guide · Page ${n}</figcaption><img src="assets/guide-${n}.jpeg" alt="Game Guide page ${n}" loading="${n===1?'eager':'lazy'}"></figure>`).join('')}</div>`}
