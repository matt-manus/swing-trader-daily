#!/usr/bin/env python3
"""
Replace Step 5A, 5B, and 6B table sections with screenshot-only versions.
CDN URLs for Mar 24:
  5A: https://files.manuscdn.com/user_upload_by_module/session_file/310519663437893849/raNhLrVienQWBLit.png
  5B: https://files.manuscdn.com/user_upload_by_module/session_file/310519663437893849/GwsfqgnCFfMvkSsb.png
  6B: https://files.manuscdn.com/user_upload_by_module/session_file/310519663437893849/cbxjArvVoMGPljpk.png
"""

CDN_5A = "https://files.manuscdn.com/user_upload_by_module/session_file/310519663437893849/raNhLrVienQWBLit.png"
CDN_5B = "https://files.manuscdn.com/user_upload_by_module/session_file/310519663437893849/GwsfqgnCFfMvkSsb.png"
CDN_6B = "https://files.manuscdn.com/user_upload_by_module/session_file/310519663437893849/cbxjArvVoMGPljpk.png"

IMG_STYLE = 'style="width:100%;border-radius:8px;margin:8px 0;box-shadow:0 2px 8px rgba(0,0,0,0.3);"'

with open('/home/ubuntu/swing-trader-daily/2026-03-24.html') as f:
    html = f.read()

def find_section_end(html, start_pos):
    """Find the end of a section by finding the next h3 tag."""
    next_h3 = html.find('<h3', start_pos + 10)
    if next_h3 == -1:
        next_h3 = html.find('</section>', start_pos)
    return next_h3

# ---- Replace Step 5A ----
h3_5a = html.rfind('<h3', 0, html.find('5A.'))
end_5a = find_section_end(html, h3_5a)
old_5a = html[h3_5a:end_5a]
new_5a = f'''<h3 class="sub">5A. Sector Performance (Finviz — Mar 24 EOD) <span class="live-badge">✅ LIVE</span></h3>
  <div style="text-align:center;">
    <img src="{CDN_5A}" alt="Finviz Sector Performance Mar 24" {IMG_STYLE}>
  </div>
'''
html = html[:h3_5a] + new_5a + html[end_5a:]
print("✅ Replaced Step 5A with screenshot")

# ---- Replace Step 5B ----
h3_5b = html.rfind('<h3', 0, html.find('5B.'))
end_5b = find_section_end(html, h3_5b)
old_5b = html[h3_5b:end_5b]
new_5b = f'''<h3 class="sub">5B. Industry Leaders — Top 10 (Finviz — Mar 24, sorted by 1D Change) <span class="live-badge">✅ LIVE</span></h3>
  <div style="text-align:center;">
    <img src="{CDN_5B}" alt="Finviz Industry Leaders Mar 24" {IMG_STYLE}>
  </div>
'''
html = html[:h3_5b] + new_5b + html[end_5b:]
print("✅ Replaced Step 5B with screenshot")

# ---- Replace Step 6B ----
h3_6b = html.rfind('<h3', 0, html.find('6B.'))
end_6b = find_section_end(html, h3_6b)
if end_6b == -1:
    # 6B might be the last section before </section> or </div>
    end_6b = html.find('\n  <h3', h3_6b + 10)
    if end_6b == -1:
        end_6b = html.find('</section>', h3_6b)
        if end_6b == -1:
            end_6b = html.find('<!-- Step 7', h3_6b)
old_6b = html[h3_6b:end_6b]
new_6b = f'''<h3 class="sub">6B. Stockbee Market Monitor (T2108 &amp; 4% Movers) <span class="live-badge">✅ LIVE</span></h3>
  <div style="text-align:center;">
    <img src="{CDN_6B}" alt="Stockbee Market Monitor Mar 24" {IMG_STYLE}>
  </div>
'''
html = html[:h3_6b] + new_6b + html[end_6b:]
print("✅ Replaced Step 6B with screenshot")

with open('/home/ubuntu/swing-trader-daily/2026-03-24.html', 'w') as f:
    f.write(html)
print("\n✅ Saved 2026-03-24.html")

# Verify
with open('/home/ubuntu/swing-trader-daily/2026-03-24.html') as f:
    check = f.read()
print(f"\nVerification:")
print(f"  5A CDN URL present: {CDN_5A[:50]} -> {'✅' if CDN_5A in check else '❌'}")
print(f"  5B CDN URL present: {CDN_5B[:50]} -> {'✅' if CDN_5B in check else '❌'}")
print(f"  6B CDN URL present: {CDN_6B[:50]} -> {'✅' if CDN_6B in check else '❌'}")
print(f"  Old 5A table gone: {'✅' if '<th>Rank</th><th>Sector</th>' not in check else '❌ STILL PRESENT'}")
print(f"  Old 6B table gone: {'✅' if '<th>Up 4%+</th>' not in check else '❌ STILL PRESENT'}")
