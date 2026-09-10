from pathlib import Path
import re


def replace_once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected 1 match, found {n}")
    return text.replace(old, new, 1)

p = Path('voyage-v014.js')
s = p.read_text()

# Locked zones show only card backs.
old_locked = ':`<div class="lockedMissionVeil" aria-label="Mission cards hidden until this zone unlocks"><span class="lockedMissionIcon">🔒</span><strong>Missions Hidden</strong><small>Unlock this zone to reveal its Mission cards.</small></div>`}'
new_locked = ':stacks.map((st,i)=>`<div class="missionCardBack" aria-label="Hidden Mission card"><span class="cardBackSkull">☠</span><strong>CAPTAIN’S DASH</strong><small>MISSION</small></div>`).join(\'\')}'
if old_locked in s:
    s = replace_once(s, old_locked, new_locked, 'locked mission backs')
elif 'missionCardBack' not in s:
    # First v0.19 pass, starting from v0.18.
    zone_anchor = ' const zones=[1,2,3,4].map(z=>'
    anchor = s.index(zone_anchor)
    start = s.index('<div class="zoneCards">${stacks.map', anchor)
    end_marker = "}).join('')}</div></section>"
    end = s.index(end_marker, start) + len("}).join('')}</div>")
    old = s[start:end]
    payload = old[len('<div class="zoneCards">${'):-len('</div>')]
    if payload.endswith('}'):
        payload = payload[:-1]
    new = '<div class="zoneCards">${open?' + payload + new_locked[1:] + '</div>'
    s = s[:start] + new + s[end:]

# Dock selection states on mission tiles.
old_tile = '<button class="missionTile" data-mission="${c.id}" aria-label="${esc(c.name)}">'
new_tile = '<button class="missionTile ${state.location===\'dock\'?(available(state,c.id)&&current(state).supply>=[1,3,6,9][(c.zone||4)-1]?\'dockSelectable\':\'dockUnavailable\'):\'\'}" data-mission="${c.id}" ${state.location===\'dock\'&&!(available(state,c.id)&&current(state).supply>=[1,3,6,9][(c.zone||4)-1])?\'disabled\':\'\'} aria-label="${esc(c.name)}">'
if old_tile in s:
    s = replace_once(s, old_tile, new_tile, 'dock mission states')
elif 'dockSelectable' not in s:
    raise SystemExit('mission tile marker not found')

# Dock returns to board instead of opening a blocking mission list.
pat = re.compile(r" if\(l==='dock'\)html=`[^\n]*`;\n")
if pat.search(s):
    s = pat.sub(" if(l==='dock'){if(dlg.open)dlg.close();toast('Choose a glowing Mission card on the board.');return}\n", s, count=1)
elif "Choose a glowing Mission card on the board." not in s:
    raise SystemExit('dock modal marker not found')

# Release labels for first pass only.
s = s.replace('The Final Isle · v0.18', 'The Final Isle · v0.19', 1)
p.write_text(s)

p = Path('voyage-table.css')
s = p.read_text()
marker = '/* v0.19 dock board selection + locked-zone card backs */'
if marker not in s:
    s += r'''

/* v0.19 dock board selection + locked-zone card backs */
.lockedMissionVeil{display:none!important}
.zoneLocked .zoneCards{filter:none!important;opacity:1!important;gap:10px;align-items:center;justify-content:center}
.zoneLocked .missionTile{display:none!important}
.missionCardBack{flex:1;min-width:0;max-width:154px;aspect-ratio:2/3;max-height:100%;border:5px double #c59a50;border-radius:10px;background:radial-gradient(circle at 50% 44%,#274f5d 0 16%,#0e303d 17% 44%,#071e29 45% 100%);box-shadow:0 6px 12px #0009,inset 0 0 0 3px #06151d,inset 0 0 0 5px #b98d4528;display:flex;flex-direction:column;align-items:center;justify-content:center;color:#e6c87e;text-align:center;pointer-events:none;position:relative;overflow:hidden}
.missionCardBack:before,.missionCardBack:after{content:'';position:absolute;inset:9px;border:1px solid #d4ae6460;border-radius:6px}.missionCardBack:after{inset:18px;border-style:dashed;opacity:.65}.missionCardBack .cardBackSkull{font-size:42px;line-height:1;filter:drop-shadow(0 3px 3px #000);margin-bottom:10px}.missionCardBack strong{font:700 clamp(10px,.9vw,14px) Georgia;letter-spacing:.08em;z-index:1}.missionCardBack small{font:700 9px system-ui;letter-spacing:.18em;margin-top:4px;color:#c6a75f;z-index:1}.zone4 .missionCardBack{max-width:158px}
#voyage .missionTile.dockSelectable{cursor:pointer;outline:4px solid #8ff5ff;box-shadow:0 0 0 4px #08677a88,0 0 30px #6ee7ff,0 7px 13px #000a;animation:dockMissionGlow .8s ease-in-out infinite alternate;transform:translateY(-3px)}
#voyage .missionTile.dockUnavailable{filter:grayscale(.65) brightness(.58);opacity:.52;cursor:not-allowed;box-shadow:0 4px 8px #0008}
@keyframes dockMissionGlow{from{box-shadow:0 0 0 3px #08677a77,0 0 18px #6ee7ff99,0 7px 13px #000a}to{box-shadow:0 0 0 5px #0d799488,0 0 34px #8ff5ff,0 7px 13px #000a}}
@media(max-width:850px){.missionCardBack{max-width:120px}.missionCardBack .cardBackSkull{font-size:32px}#voyage .missionTile.dockSelectable{outline-width:3px}}
@media(prefers-reduced-motion:reduce){#voyage .missionTile.dockSelectable{animation:none}}
'''
p.write_text(s)

# First-pass release labels.
p = Path('index.html')
s = p.read_text()
s = s.replace("<title>Captain's Dash: The Final Isle — v0.18 Test</title>", "<title>Captain's Dash: The Final Isle — v0.19 Test</title>", 1)
s = s.replace("CAPTAIN'S DASH · FULL GAME · v0.18 TEST", "CAPTAIN'S DASH · FULL GAME · v0.19 TEST", 1)
s = s.replace('Interactive Web Edition · v0.18 Test.', 'Interactive Web Edition · v0.19 Test.', 1)
p.write_text(s)

p = Path('menu.js')
s = p.read_text().replace('version:"0.18"', 'version:"0.19"', 1)
p.write_text(s)

checks = {
    'voyage-v014.js': ['The Final Isle · v0.19', 'missionCardBack', 'dockSelectable', 'dockUnavailable', 'Choose a glowing Mission card on the board.'],
    'voyage-table.css': ['v0.19 dock board selection + locked-zone card backs', '@keyframes dockMissionGlow'],
    'index.html': ['v0.19 Test', 'v0.19 TEST'],
}
for file, markers in checks.items():
    text = Path(file).read_text()
    for marker in markers:
        if marker not in text:
            raise SystemExit(f'{file}: missing {marker}')

print('v0.19 dock selection and locked-zone backs verified')
