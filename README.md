# Captain’s Dash: The Final Isle — v0.15.2

Playable local pass-and-play for 2–4 captains, plus prototype solo versus AI.

## This release
- Restores the illustrated worker spaces: transparent hit areas reveal the original location art. Gold outlines show legal placement; blue outlines show legal pickup.
- Compact serif header and player resource bar give the map more space. Card collection, history, zoom and menu are in the Captain’s table menu.
- Expedition preparation validates crew, supply and Final requirements before enabling payment, and previews both Final tests.
- AI saves for later-zone supply costs and players cannot spend resources or roll on the AI’s turn.
- Preserves v0.15 shared workers, 81 card types, three stats, three face-up recruitment cards, two-test Finals without Final Edge, and resumable saves.

## Play
Start a new voyage or Continue. Place a Pirate on a glowing empty Haven space, resolve its action, then take a Pirate from another occupied space and resolve that action. Dock opens Mission selection. Win both tests of a Final Mission to win immediately.

## Run
`npm install`, `npm run dev`, `npm test`, `npm run build`.
Vercel serves the static `dist` directory. `release-manifest.json` verifies files for immutable-commit deployments.

## Verification and limits
595 deterministic engine assertions passed; release build and local asset references checked. This release has not been visually tested in a browser or on native iPad Safari. AI remains a prototype, and online multiplayer is not implemented. Original artwork is preserved at its native resolution (board: 1448 × 1086); zoom does not add image detail.
