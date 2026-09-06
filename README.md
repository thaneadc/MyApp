# Captain's Dash: The Final Isle

Full-resolution interactive browser board game prototype.

## Current build: v0.8.0

The game now uses separate scripts and original image assets. Run `npm run build` to produce the static `dist/` deployment. No artwork was resized in this update.

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

## Changes in v0.8
- Location actions remain open until resolved; the next action is locked meanwhile.
- New Game and Continue are separate flows.
- Dice and optional abilities are selected by the player; expedition rolls, used abilities, and costs are saved.
- Late-game expeditions resume at the saved stage without paying the entry cost again.
- Resource counters refresh immediately after expedition costs and paid abilities.
- Crew & Treasure is hidden while on the main menu.

## Validation — 6 September 2026
- `node tests/rules.mjs`: 94 mission success/failure scenarios passed across the 47-mission catalog, plus dice thresholds, ability limits, and 2/3/4-player progression.
- Five seeded AI simulations reached a winner in rounds 13–17. These are engine simulations, not full browser playthroughs.
- Browser: late-game fixture → Dock → Final Isle → three stages → manual Lucky Doubloon use → winner screen passed.
- Browser: navigation away during stage 2 → Continue restored stage 2, all three dice showing 3, and 3 remaining Supplies (entry cost was not charged again).
- Browser: Final Isle failure → penalty → Continue returned to Take a Pirate phase.
- Static build passed; all 47 referenced artwork files exist. Generated test fixtures are excluded from deployment and Git.
- Native iPad/Safari testing remains outstanding. Online multiplayer is not implemented; local pass-and-play and solo AI are available.

## Publishing
Source and full-resolution assets are published to `thaneadc/MyApp` with user approval.
For a normal Git import, run `npm run build` and publish `dist/`.
For connector uploads with a 4 MB limit, `scripts/build-release.mjs <commit-sha>` downloads the 52 runtime files from that immutable GitHub revision and verifies every SHA-256 hash against `release-manifest.json`. Vercel then serves all files locally; gameplay has no GitHub runtime dependency.
