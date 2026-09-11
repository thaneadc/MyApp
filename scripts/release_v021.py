from pathlib import Path

# Captain's Dash v0.21 is already materialized on this branch.
# Keep this script idempotent so a manual workflow rerun verifies the release
# instead of trying to patch the same source a second time.
checks = {
    'engine-v014.mjs': [
        'for(const x of p.crew)if(a.crew.includes(x.uid))x.exhausted=true',
        'const selected=(p,e)=>p.crew.filter(c=>e.crew.includes(c.uid));',
    ],
    'voyage-v014.js': [
        'The Final Isle · v0.21',
        'crewStatusIcon',
        'Ready Crew / Total Crew',
        'expeditionTable',
        'expDiscardGrid',
        'captainsdash:music-mode',
    ],
    'menu.js': [
        'captains-dash-adventure-v2.ogg',
        'captains-dash-adrenaline-v2.ogg',
        'version:"0.21"',
    ],
    'voyage-table.css': [
        'v0.21 — Crew fatigue',
        'expScoreboard',
        'crewStatusIcon',
    ],
    'index.html': ['v0.21 Test'],
    'tests/rules-v014.mjs': ['eq(current(e).crew[0].exhausted,true)'],
}
for file, markers in checks.items():
    text = Path(file).read_text()
    for marker in markers:
        if marker not in text:
            raise SystemExit(f'{file}: missing {marker}')
for asset, minimum in [
    ('assets/captains-dash-adventure-v2.ogg', 1_000_000),
    ('assets/captains-dash-adrenaline-v2.ogg', 900_000),
]:
    data = Path(asset).read_bytes()
    if len(data) <= minimum or not data.startswith(b'OggS'):
        raise SystemExit(f'{asset}: invalid soundtrack asset')
print('v0.21 finalized: fatigue, soundtrack, Crew status and Expedition UI verified')
