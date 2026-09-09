# v0.15 Final implementation

Source of truth: `RULES-v0.15.txt`, supplied by the designer, with the subsequently confirmed shared-token clarification. The 81 card types in `cards-v014.js` are imported by `scripts/import-v014.mjs` (15 Crew, 20 Treasure, 18/14/9 zone Missions, 5 Finals).

Operational decisions where the TXT is unspecified:

- Shared workers: Tavern and Dock each start occupied by one neutral Pirate. Every player places on an empty unlocked location, resolves it, takes a Pirate from another occupied location, then resolves that action. No ownership or colors restrict taking. The just-placed Pirate cannot be taken. Two Pirates remain on the board after every complete turn.
- An action may be declined after worker movement, allowing an unaffordable action or empty recovery location to resolve without trapping the turn.
- Four copies of each Crew type, with starting Deckhands removed from that pool. Crew/Veteran rewards draw from their separate decks; empty pools do not create extra copies.
- Over-cap recruitment/rewards require a discard choice before another action. Unchosen Treasure goes to discard; only an empty Treasure deck reshuffles its discard.
- Final supply is paid once per Expedition. Each Final test rolls three dice independently; both must succeed in the same Expedition. Step 1 does not grant Final Edge: the new four Guide pages and TXT both omit it. F3 payment and F4/F5 conditions are mandatory and checked on participating ready Crew and owned Treasure before payment.
- Each eligible Crew reroll and Loaded Bones is available once per test, Fortune once per Expedition. There is no old v0.8 shared one-control limit. Skull always ends the test immediately.
- Black Powder Horn is selected and paid before the Expedition, giving its Combat bonus to a Combat test in that Expedition. All owned Treasure passives are active.
- Veteran Pirate readies the first exhausted owned Crew automatically. New blessings replace the current blessing. Surgeon protection does not exhaust its Crew because v0.15 does not instruct it to do so.
- A failed Final is discarded only when another Final remains. There is no shared-loss ending.
- Local saves use a separate v0.15 key; v0.8 saves remain untouched and are not migrated across incompatible card IDs.

Guide pages are the four supplied original JPEGs, displayed in order, with full-size links. Artwork is reused from the existing game; readable card data is rendered from v0.15 rather than baked into images.

Validation: `npm test` for deterministic rules; `npm run build` for the complete static release.
