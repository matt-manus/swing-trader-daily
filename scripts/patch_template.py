"""Patch the remaining issues in TEMPLATE.html"""
import re

with open('/home/ubuntu/swing-trader-daily/TEMPLATE.html') as f:
    t = f.read()

# ── FIX: Replace the entire Step 7 section content ───────────────────────────
# The regex in make_template.py used wrong comment marker
t = re.sub(
    r'(<!-- STEP 7: DAILY COMMENTARY -->\n<div class="section" id="step7">.*?<div class="section-title">.*?</div>\n)(.*?)(</div>\n<!-- REGIME DETERMINATION)',
    r'\1{{BULL_BEAR_CONTENT}}\3',
    t,
    flags=re.DOTALL
)

# ── FIX: Replace Step 5A sector table (Finviz sector data) ───────────────────
# Also replace the 5A note
t = re.sub(
    r'(<div class="note">📌 板塊表現總結.*?</div>)',
    '<div class="note">📌 板塊表現總結: {{SECTOR5A_SUMMARY}}</div>',
    t,
    flags=re.DOTALL
)

# ── FIX: IWM MA columns in 4A (missing from make_template) ───────────────────
# These should already be replaced; check
# ── FIX: QQQ MA columns in 4A ────────────────────────────────────────────────
# Add QQQ MA placeholders
t = t.replace(
    '<td>${{QQQ_MA20}}</td>',
    '<td>${{QQQ_MA20}}</td>'
)

# ── FIX: SECTOR5A_ROWS placeholder ───────────────────────────────────────────
# Check if it exists, if not add it
if '{{SECTOR5A_ROWS}}' not in t:
    t = re.sub(
        r'(<tr><th>Rank</th><th>Sector</th><th>1D Chg</th><th>1W Chg</th><th>1M Chg</th><th>YTD Chg</th></tr>\n)(.*?)(</table>\n  <div class="source-label">Source: <a href="https://finviz\.com/groups\.ashx\?g=sector)',
        r'\1{{SECTOR5A_ROWS}}\3',
        t,
        flags=re.DOTALL
    )

# ── Save ──────────────────────────────────────────────────────────────────────
with open('/home/ubuntu/swing-trader-daily/TEMPLATE.html', 'w') as f:
    f.write(t)

# ── Verify ────────────────────────────────────────────────────────────────────
placeholders = sorted(set(re.findall(r'\{\{[A-Z0-9_]+\}\}', t)))
print(f"Total unique placeholders: {len(placeholders)}")

# Check BULL_BEAR_CONTENT was placed
print("BULL_BEAR_CONTENT present:", '{{BULL_BEAR_CONTENT}}' in t)
print("SECTOR5A_ROWS present:", '{{SECTOR5A_ROWS}}' in t)
print("SECTOR_ROWS present:", '{{SECTOR_ROWS}}' in t)
print("INDUSTRY_ROWS present:", '{{INDUSTRY_ROWS}}' in t)
print("IMG_MARKETINOUT present:", '{{IMG_MARKETINOUT}}' in t)
print("IMG_STOCKBEE present:", '{{IMG_STOCKBEE}}' in t)
print("FULLSTACK_IMG present:", '{{FULLSTACK_IMG}}' in t)

# Check old values
old_values = ['655.38', '26.15', '19.44', '247.45', '588.00', '462.08']
print("\nOld value check:")
for v in old_values:
    count = t.count(v)
    status = "✓ gone" if count == 0 else f"✗ still {count}x"
    print(f"  {status}: {v}")
