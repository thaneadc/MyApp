from pathlib import Path
p=Path('voyage-v014.js')
s=p.read_text()
old="else if(l==='quarters'){const tired=p.crew.filter(c=>c.exhausted).length;if(tired){aiDelayOverride=2200;a={type:'ready',rested:tired}}else a={type:'skip'}};else if(l==='dock')"
new="else if(l==='quarters'){const tired=p.crew.filter(c=>c.exhausted).length;if(tired){aiDelayOverride=2200;a={type:'ready',rested:tired}}else a={type:'skip'}}else if(l==='dock')"
if old not in s:
    raise SystemExit('v0.25 syntax marker missing')
p.write_text(s.replace(old,new,1))
print('v0.25 AI quarters syntax corrected')
