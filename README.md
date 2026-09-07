# Captain’s Dash: The Final Isle — v0.8.1

Interactive local pass-and-play (2–4 players) and prototype solo AI game based on `RULES-v0.8.txt`.

## This release
- New island board and 84 illustrated cards: 15 Crew, 20 Treasure, 41 normal Missions and 8 Final Missions. Rules are live text above the artwork.
- Custom dice: SKULL / 0 / 0 / 1 / 2 / GOLD. Supply costs: 1 / 3 / 6 / 9.
- Shared zone progression, optional Final approaches, one Dice Control per Expedition, rewards, casualties, victory and shared defeat.
- Paid Expeditions and pending rewards are saved. Continue restores their phase without charging or rolling again.
- Large centered, scrollable menu dialogs with keyboard focus handling; custom New Game confirmation replaces the small native confirmation.
- Board fits the available screen; zoom and scrolling are available.

## Prototype defaults
The source leaves worker occupancy, Crew deck copy counts and some effect details open. This build uses one action per turn without occupancy blocking, four copies per Crew type, Elite qualifying as Veteran, a 2 Gold blessing price and Atlas high targets 4/6/10. Final checks use participating Crew and active Treasures; Crew exhausted during the approach contributes no Power. These defaults are exposed in the rules UI and engine DEFAULTS. Online multiplayer is not implemented.

The new save key is separate from the previous engine; old saves are preserved but not migrated. Board art is natively 1448×1086; zoom does not increase its native resolution.

## Run and publish
`npm install`, `npm run dev`, `npm test`, `npm run build`.
Vercel publishes the static `dist/` directory using `vercel.json`.
The alternate connector build uses `scripts/build-release.mjs <full commit SHA>` and `release-manifest.json` to retrieve and verify runtime files from that immutable GitHub commit.

## Validation
116 engine checks, including success and failure for all 49 Missions, payment atomicity, save/resume, Dice Control and Fortune bonuses. Browser checks cover menu setup, starting a voyage, payment, roll, casualty and end turn. Native iPad/Safari testing remains outstanding.
