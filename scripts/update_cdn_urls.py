#!/usr/bin/env python3
"""
Replace old CDN URLs for Step 4C (9 StockCharts) and Step 5A (sector screenshot)
with the new wide-viewport versions.
"""

# Old -> New CDN URL mappings
REPLACEMENTS = {
    # Step 4C StockCharts (old small -> new wide)
    "TfwejioHODODjTJK": "RuAUnYxRnaAuoCBS",  # spxa20r
    "cdTeYwIeoYtAwfaB": "CQRYQqvcgMSyQWQy",  # spxa50r
    "KnvUmOboOhhruUfq": "OUCFYSEJIVTqYKlG",  # spxa200r
    "wfeZRFdGPEVBclpy": "UMdUxgfZPbAYZjic",  # ndxa20r
    "ZlyYGXaRzjvnCdRa": "vxFYZnXojYzBtiTr",  # ndxa50r
    "XEESDZTBHlHhhaEt": "DirehvhyGxojpBip",  # ndxa200r
    "szljItFRiXeSkCBy": "wxYUhpCHocZQnSTA",  # nya20r
    "FljSVFvpgriQaiNI": "iZqiqQltlzjVgmRI",  # nya50r
    "kQgRPcuCUmUwbouI": "aUCTguQxmdCqwReS",  # nya200r
    # Step 5A sector screenshot (old wrong-sort -> new sorted by 1D change)
    "raNhLrVienQWBLit": "RNDDUEwBMsDUzWZf",  # 5A sectors sorted
}

BASE = "https://files.manuscdn.com/user_upload_by_module/session_file/310519663437893849/"

with open('/home/ubuntu/swing-trader-daily/2026-03-24.html') as f:
    html = f.read()

count = 0
for old_id, new_id in REPLACEMENTS.items():
    old_url = BASE + old_id + ".png"
    new_url = BASE + new_id + ".png"
    if old_url in html:
        html = html.replace(old_url, new_url)
        print(f"✅ Replaced {old_id[:8]}... -> {new_id[:8]}...")
        count += 1
    else:
        print(f"⚠️  Not found: {old_id[:8]}...")

with open('/home/ubuntu/swing-trader-daily/2026-03-24.html', 'w') as f:
    f.write(html)

print(f"\n✅ Updated {count}/{len(REPLACEMENTS)} URLs in 2026-03-24.html")

# Verify
with open('/home/ubuntu/swing-trader-daily/2026-03-24.html') as f:
    check = f.read()
for old_id, new_id in REPLACEMENTS.items():
    new_url = BASE + new_id + ".png"
    present = new_url in check
    print(f"  {new_id[:8]}...: {'✅' if present else '❌ MISSING'}")
