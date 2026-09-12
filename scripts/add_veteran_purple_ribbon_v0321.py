from pathlib import Path

js_path = Path('voyage-v014.js')
css_path = Path('voyage-table.css')

js = js_path.read_text()
old = 'class="vCard physicalCard ${c.kind}"'
new = 'class="vCard physicalCard ${c.kind} ${c.kind===\'crew\'?c.tier.toLowerCase():\'\'}"'
if new not in js:
    if old not in js:
        raise SystemExit('Card class anchor not found')
    js = js.replace(old, new, 1)
    js_path.write_text(js)

css = css_path.read_text()
marker = '/* v0.32.1 — Veteran Crew ribbon */'
block = '''\n\n/* v0.32.1 — Veteran Crew ribbon */\n.physicalCard.crew.veteran .cardRibbon{\n  background:linear-gradient(#74458f,#4a285f);\n  border-block-color:#c7a2d7;\n  color:#fff0ff;\n  box-shadow:inset 0 0 0 1px #e4c9ee22;\n}\n'''
if marker not in css:
    css_path.write_text(css.rstrip() + block)
