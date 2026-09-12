from pathlib import Path

p=Path('voyage-v014.js')
s=p.read_text(encoding='utf-8')
old="<p class=\"captainResources\">${resourceIcon('gold')} ${p.gold} Gold · ${resourceIcon('supply')} ${p.supply} Supply · ${crewGroupIcon()} ${p.crew.filter(c=>!c.exhausted).length}/${p.crew.length} Ready</p></div></div>"
new="<p class=\"captainResources\">${resourceIcon('gold')} ${p.gold} Gold · ${resourceIcon('supply')} ${p.supply} Supply · ${crewGroupIcon()} ${p.crew.filter(c=>!c.exhausted).length}/${p.crew.length} Ready</p></div></div><div class=\"vSummary captainBlessing\"><strong>Sea Witch Blessing</strong><span>${p.blessing==='fortune'?'Fortune · reroll 1 non-Skull die':p.blessing?'+3 '+p.blessing:'No active Blessing'}</span></div>"
if old not in s:
    raise SystemExit('Captain resource block not found')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')

# Add a small regression test focused on Captain Information only.
t=Path('tests/captain-blessing-info-v0321.mjs')
t.write_text("""import assert from 'node:assert/strict';\nimport {readFileSync} from 'node:fs';\nconst ui=readFileSync(new URL('../voyage-v014.js',import.meta.url),'utf8');\nassert.match(ui,/Sea Witch Blessing/,'Captain Information should show Blessing status');\nassert.match(ui,/No active Blessing/,'Captain Information should show empty Blessing state');\nassert.match(ui,/Fortune · reroll 1 non-Skull die/,'Captain Information should describe Fortune');\nassert.match(ui,/p\\.blessing\\?\\'\\+3 \\'\\+p\\.blessing/,'Captain Information should show +3 stat blessings');\nconst dockBlock=ui.match(/function playerDock\\(\\)\\{[\\s\\S]*?function render\\(/)?.[0]||'';\nassert.doesNotMatch(dockBlock,/Sea Witch Blessing|No active Blessing/,'Blessing info should not be added to the right-side player panel');\nconsole.log('Captain Blessing information regression passed');\n""",encoding='utf-8')
