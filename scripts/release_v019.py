from pathlib import Path

# Captain's Dash v0.19 release notes / verification markers.
# The final implementation is committed directly in voyage-v014.js and voyage-table.css.
# This file is intentionally non-mutating so re-running release workflows cannot alter
# an already-finalized v0.19 build.

checks = {
    'voyage-v014.js': [
        'The Final Isle · v0.19',
        'missionCardBack',
        'dockSelectable',
        'dockUnavailable',
        'Choose a glowing Mission card on the board.',
    ],
    'voyage-table.css': [
        'v0.19 dock board selection + locked-zone card backs',
        '@keyframes dockMissionGlow',
    ],
    'index.html': ['v0.19 Test', 'v0.19 TEST'],
}

for file, markers in checks.items():
    text = Path(file).read_text()
    for marker in markers:
        if marker not in text:
            raise SystemExit(f'{file}: missing {marker}')

print('v0.19 finalized: Dock board selection + locked-zone card backs verified')
