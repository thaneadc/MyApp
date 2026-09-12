import fs from 'node:fs';
import assert from 'node:assert/strict';

const js=fs.readFileSync('voyage-v014.js','utf8');
const css=fs.readFileSync('voyage-table.css','utf8');

assert(js.includes('class="vCard physicalCard ${c.kind} ${c.kind===\'crew\'?c.tier.toLowerCase():\'\'}"'), 'Crew cards must expose Common/Veteran tier as a CSS class');
assert(css.includes('.physicalCard.crew.veteran .cardRibbon'), 'Veteran Crew ribbon must have its own style');
assert(css.includes('linear-gradient(#74458f,#4a285f)'), 'Veteran ribbon must use the purple gradient');
assert(!css.includes('.physicalCard.crew.common .cardRibbon{\n  background:linear-gradient(#74458f,#4a285f)'), 'Common Crew must not use the Veteran purple ribbon');

console.log('Veteran purple ribbon regression passed');
