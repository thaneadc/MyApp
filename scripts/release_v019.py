from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected 1 match, found {n}")
    return text.replace(old, new, 1)

# Hide all mission information in locked zones.
p = Path('voyage-v014.js')
s = p.read_text()
zone_anchor = ' const zones=[1,2,3,4].map(z=>'
anchor = s.index(zone_anchor)
start = s.index('<div class="zoneCards">${stacks.map', anchor)
end_marker = "}).join('')}</div></section>"
end = s.index(end_marker, start) + len("}).join('')}</div>")
old = s[start:end]
payload = old[len('<div class="zoneCards">${'):-len('</div>')]
new = '<div class="zoneCards">${open?' + payload + ':`<div class="lockedMissionVeil" aria-label="Mission cards hidden until this zone unlocks"><span class="lockedMissionIcon">🔒</span><strong>Missions Hidden</strong><small>Unlock this zone to reveal its Mission cards.</small></div>`}</div>'
s = s[:start] + new + s[end:]
s = replace_once(s, 'The Final Isle · v0.18', 'The Final Isle · v0.19', 'HUD version')
p.write_text(s)

# Add locked-zone concealment styling.
p = Path('voyage-table.css')
s = p.read_text()
marker = '/* v0.19 — conceal mission identities while a zone is locked. */'
if marker not in s:
    s += r'''

/* v0.19 — conceal mission identities while a zone is locked. */
.lockedMissionVeil{width:100%;min-height:180px;align-self:stretch;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8px;padding:22px 14px;border:2px dashed #cda85f88;border-radius:12px;background:linear-gradient(180deg,#0b2734d9,#071820e8);box-shadow:inset 0 0 35px #0007;color:#efd699;text-align:center;pointer-events:none}
.lockedMissionVeil .lockedMissionIcon{font-size:34px;filter:drop-shadow(0 3px 4px #0008)}
.lockedMissionVeil strong{font:700 clamp(18px,1.7vw,28px) Georgia,"Times New Roman",serif;letter-spacing:.02em}
.lockedMissionVeil small{max-width:230px;font:12px/1.35 system-ui,sans-serif;color:#d8cfbd}
.zoneLocked .zoneCards{filter:none!important;opacity:1!important}
.zoneLocked .missionTile{display:none!important}
@media(max-width:850px){.lockedMissionVeil{min-height:130px;padding:14px 9px}.lockedMissionVeil .lockedMissionIcon{font-size:28px}.lockedMissionVeil strong{font-size:18px}.lockedMissionVeil small{font-size:10px}}
'''
p.write_text(s)

# Visible release labels.
p = Path('index.html')
s = p.read_text()
s = replace_once(s, "<title>Captain's Dash: The Final Isle — v0.18 Test</title>", "<title>Captain's Dash: The Final Isle — v0.19 Test</title>", 'document title')
s = replace_once(s, "CAPTAIN'S DASH · FULL GAME · v0.18 TEST", "CAPTAIN'S DASH · FULL GAME · v0.19 TEST", 'menu release label')
s = replace_once(s, 'Interactive Web Edition · v0.18 Test.', 'Interactive Web Edition · v0.19 Test.', 'footer release label')
p.write_text(s)

p = Path('menu.js')
s = p.read_text()
s = s.replace('version:"0.18"', 'version:"0.19"', 1)
p.write_text(s)

# Release verification.
checks = {
    'voyage-v014.js': ['The Final Isle · v0.19', 'open?stacks.map', 'lockedMissionVeil', 'Missions Hidden'],
    'voyage-table.css': ['v0.19 — conceal mission identities', '.zoneLocked .missionTile{display:none!important}'],
    'index.html': ['v0.19 Test', 'v0.19 TEST'],
}
for file, markers in checks.items():
    text = Path(file).read_text()
    for marker in markers:
        if marker not in text:
            raise SystemExit(f'{file}: missing {marker}')

print('v0.19 locked-zone concealment verified')
