from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

old = '''      <div class="opp-card-row"><span class="opp-card-label">Estágio:</span> <span style="font-size:11px">${Object.values(STAGES).flat().find(s=>s.id===c.stage)?.label||c.stage}</span></div>'''
new = '''      <div class="opp-card-row"><span class="opp-card-label">${isEzMoney ? 'Estágio:' : 'Origem:'}</span> <span style="font-size:11px">${isEzMoney ? (Object.values(STAGES).flat().find(s=>s.id===c.stage)?.label||c.stage) : (c.origin || 'Não informado')}</span></div>'''

if old not in s:
    raise SystemExit('Target card line not found')

s = s.replace(old, new, 1)
p.write_text(s, encoding='utf-8')
print('Opportunity card now shows Origem for Alliance and Estágio for Ez Money.')
