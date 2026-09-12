import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const ui=readFileSync(new URL('../voyage-v014.js',import.meta.url),'utf8');
assert.match(ui,/e\.step>old\.step\)\{resultFlash\(dlg,true,true\);if\(isAITurn\(\)&&isFinal\)aiDelayOverride=2300/,'AI must wait until the Step 1 success overlay clears');
assert.match(ui,/a\.type==='roll'&&isAITurn\(\)&&isFinal&&e\.step===1&&e\.phase==='dice'\)aiDelayOverride=1800/,'AI must keep Step 2 dice visible before resolving');
console.log('AI Final Step 2 visibility regression passed');
