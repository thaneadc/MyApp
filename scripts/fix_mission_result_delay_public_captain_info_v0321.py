from pathlib import Path

js_path = Path('voyage-v014.js')
css_path = Path('voyage-table.css')
js = js_path.read_text()
css = css_path.read_text()

repls = [
    (
        "if(e.phase==='loss'&&old?.phase!=='loss'){resultFlash(dlg,false);if(isAITurn()&&isFinal)aiDelayOverride=2000}",
        "if(e.phase==='loss'&&old?.phase!=='loss'){resultFlash(dlg,false);if(isAITurn())aiDelayOverride=isFinal?4000:3050}"
    ),
    (
        "else if(e.success===true&&old?.success!==true)resultFlash(dlg,true);",
        "else if(e.success===true&&old?.success!==true){resultFlash(dlg,true);if(isAITurn())aiDelayOverride=3050}"
    ),
    (
        "else if(a.type==='roll'&&isAITurn()&&isFinal&&e.step===1&&e.phase==='dice')aiDelayOverride=1800",
        "else if(a.type==='roll'&&isAITurn()&&isFinal&&e.step===1&&e.phase==='dice')aiDelayOverride=3800"
    ),
    (
        "aria-label=\"${i===state.turn?'View your captain':'Private captain'} ${esc(p.name)}\" ${i!==state.turn||isAITurn()||handoff?'disabled':''}",
        "aria-label=\"View captain ${esc(p.name)}\""
    ),
    (
        "${i===state.turn?(state.mode==='ai'&&p.isAI?'AI TURN':'YOUR TURN'):'PRIVATE'}",
        "${i===state.turn?(state.mode==='ai'&&p.isAI?'AI TURN':'YOUR TURN'):'VIEW'}"
    ),
    (
        "if((name==='player'&&+d.index!==state.turn)||(['player','crew'].includes(name)&&(handoff||isAITurn())))return toast('This captain’s cards are private.');",
        ""
    ),
    (
        "if(handoff&&!isAITurn()&&b.dataset.action!=='readyCaptain')return;",
        "if(handoff&&!isAITurn()&&!['readyCaptain','player'].includes(b.dataset.action))return;"
    ),
]

for old, new in repls:
    if old not in js:
        raise SystemExit(f'Missing expected JS pattern: {old[:100]}')
    js = js.replace(old, new, 1)

css_rule = ".expDiscardGrid .physicalCard h3{color:#000!important}\n"
if css_rule.strip() not in css:
    css += "\n/* v0.32.1 — keep Crew names readable on the failure discard screen. */\n" + css_rule

js_path.write_text(js)
css_path.write_text(css)
