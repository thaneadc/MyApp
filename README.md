# Captain's Dash: The Final Isle

Full-resolution interactive browser board game prototype.

## Current build: v0.7.2

This repository now serves the complete self-contained `index.html` build (4,418,567 bytes), including the full-resolution artwork and the mobile/touch fix for iPhone/iPad Safari.

### Implemented
- Main Menu / New Game / Continue / Settings
- Local Pass & Play for 2–4 players
- Solo vs AI prototype
- Full interactive board with pan/zoom/touch controls
- Place → Take Pirate worker-placement turn flow
- Tavern Crew market, Crew slots, Exhaust / Ready
- Treasure inventory and 3 Active Treasure slots
- Crew drag/drop and card interaction
- Custom dice `0,1,1,2,2,3`
- 15 Crew types
- 20 unique Treasures
- 47 Missions: Zone I 18, Zone II 14, Zone III 9, Final Isle 6
- Expedition resolution, rewards and failure penalties
- Zone I → II → III → Final Isle progression
- Autosave / Continue
- Final Island victory sequence

### Mobile fix in v0.7.2
Hidden overlays no longer intercept pointer/touch events on Safari. The tested mobile flow is:

`Play Game → Game Setup → Start Voyage → Board → Tavern → Recruit Crew`

### Rules source
Prototype Rulebook v0.3. The game-data values are authoritative when older concept artwork contains outdated printed text.
