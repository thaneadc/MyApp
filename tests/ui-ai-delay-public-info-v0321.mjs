import assert from 'node:assert/strict';
import fs from 'node:fs';

const js=fs.readFileSync(new URL('../voyage-v014.js',import.meta.url),'utf8');
const css=fs.readFileSync(new URL('../voyage-table.css',import.meta.url),'utf8');

// Failure discard Crew names must be high-contrast black.
assert.match(css,/\.expDiscardGrid \.physicalCard h3\{color:#000!important\}/);

// AI outcome pacing: add roughly two seconds over the normal 1.05s cadence.
assert.match(js,/e\.phase==='loss'.*aiDelayOverride=isFinal\?4000:3050/);
assert.match(js,/e\.success===true.*aiDelayOverride=3050/);
assert.match(js,/e\.step===1&&e\.phase==='dice'\)aiDelayOverride=3800/);

// Captain Information is public for all players; no private-card blocker remains.
assert.doesNotMatch(js,/Private captain/);
assert.doesNotMatch(js,/This captain’s cards are private/);
assert.doesNotMatch(js,/i!==state\.turn\|\|isAITurn\(\)\|\|handoff\?'disabled'/);
assert.match(js,/aria-label=\"View captain \$\{esc\(p\.name\)\}\"/);
assert.match(js,/:'VIEW'\}/);
assert.match(js,/handoff&&!isAITurn\(\)&&!\['readyCaptain','player'\]\.includes\(b\.dataset\.action\)/);

// Existing Captain Information remains fully detailed, including Blessing/Crew/Treasure/archive.
assert.match(js,/captainBlessing/);
assert.match(js,/<h3>Crew<\/h3>/);
assert.match(js,/<h3>Treasure<\/h3>/);
assert.match(js,/Completed Missions/);

console.log('UI readability, AI pacing, and public Captain Information regression passed');
