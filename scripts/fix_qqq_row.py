import re

with open('/home/ubuntu/swing-trader-daily/TEMPLATE.html') as f:
    t = f.read()

# Find the exact QQQ (NDX) row
idx = t.find('<td>QQQ (NDX)</td>')
if idx >= 0:
    end_idx = t.find('</tr>', idx) + len('</tr>')
    old_row = t[idx:end_idx]
    print("Found QQQ (NDX) row:")
    print(repr(old_row[:200]))
    
    new_row = '''<td>QQQ (NDX)</td>
      <td>${{QQQ_PRICE}}</td>
      <td class="{{QQQ_CHG_COLOR}}">{{QQQ_CHG}}%</td>
      <td>${{QQQ_MA20}}</td><td class="{{QQQ_20_COLOR}}">{{QQQ_VS_20MA}}%</td>
      <td>${{QQQ_MA50}}</td><td class="{{QQQ_50_COLOR}}">{{QQQ_VS_50MA}}%</td>
      <td>${{QQQ_MA200}}</td><td class="{{QQQ_200_COLOR}}">{{QQQ_VS_200MA}}%</td>
      <td class="{{QQQ_RSI_COLOR}}">{{QQQ_RSI}}</td>
      <td><span class="badge {{QQQ_BADGE}}">{{QQQ_SIGNAL}}</span></td>
    </tr>'''
    
    t = t[:idx] + new_row + t[end_idx:]
    print("Replaced QQQ (NDX) row.")
else:
    print("QQQ (NDX) row NOT found")

# Final verification
old_vals = ['655.38', '26.15', '19.44', '247.45', '588.00', '462.08']
print("\nFinal old value check:")
for v in old_vals:
    cnt = t.count(v)
    print(f"  {'OK' if cnt==0 else 'FAIL'}: {v} ({cnt}x)")

# Count total placeholders
placeholders = sorted(set(re.findall(r'\{\{[A-Z0-9_]+\}\}', t)))
print(f"\nTotal unique placeholders: {len(placeholders)}")

# Key structural checks
checks = [
    'BULL_BEAR_CONTENT', 'SECTOR5A_ROWS', 'SECTOR_ROWS', 'INDUSTRY_ROWS',
    'IMG_MARKETINOUT', 'IMG_STOCKBEE', 'FULLSTACK_IMG',
    'IMG_SPXA20R', 'IMG_NYA20R', 'T2108', 'NAAIM', 'FEAR_GREED',
    'MACRO_SUMMARY', 'TRADING_GUIDANCE', 'REGIME_TITLE'
]
print("\nKey placeholder check:")
for c in checks:
    present = '{{' + c + '}}' in t
    print(f"  {'OK' if present else 'MISSING'}: {c}")

with open('/home/ubuntu/swing-trader-daily/TEMPLATE.html', 'w') as f:
    f.write(t)
print(f"\nTemplate saved. Total chars: {len(t)}")
