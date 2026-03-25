"""Replace yesterday's CDN URLs with today's new CDN URLs in 2026-03-24.html"""

# Mapping: yesterday's URL -> today's URL
# Order from the 2026-03-23.html:
# 1. SPXA20R  -> CTUzxaAqcpaevTvi -> UchRzbLnXZOVLOSM
# 2. SPXA50R  -> DQlweCCLSHauCyBn -> YqYbgMkyHTAGMyOI
# 3. SPXA200R -> ivuLkuZeqNkFruSD -> OorOwtUUTFeAnXGC
# 4. NDXA20R  -> DqtUSvHOzZlOnbym -> XgbOeCnQgvgjZLQq
# 5. NDXA50R  -> FrnJGRHehDeBfSSu -> FUQmBjmrmqhvGXWj
# 6. NDXA200R -> VzGlsCvOlYrYArzm -> EeMHzWdZygXoXVnk
# 7. NYA20R   -> aLRUwqWnnOAkVUsE -> LqnzwjnmCuLSIiIJ
# 8. NYA50R   -> dwSNMinuFLvRFcBl -> WoTOuricVLNOZrjA
# 9. NYA200R  -> DWVaHZsujoNKTGFB -> SXjAwlrLhQpDobVl
# 10. MarketInOut A/D -> rhOaquSPLXjAmwcG -> atToNJzyXaRJbfPN (using Stockbee instead)
# 11. Stockbee MM -> brlBogwNeKchEFhK -> atToNJzyXaRJbfPN

BASE = "https://files.manuscdn.com/user_upload_by_module/session_file/310519663437893849/"

replacements = {
    "CTUzxaAqcpaevTvi.png": "UchRzbLnXZOVLOSM.png",   # SPXA20R
    "DQlweCCLSHauCyBn.png": "YqYbgMkyHTAGMyOI.png",   # SPXA50R
    "ivuLkuZeqNkFruSD.png": "OorOwtUUTFeAnXGC.png",   # SPXA200R
    "DqtUSvHOzZlOnbym.png": "XgbOeCnQgvgjZLQq.png",   # NDXA20R
    "FrnJGRHehDeBfSSu.png": "FUQmBjmrmqhvGXWj.png",   # NDXA50R
    "VzGlsCvOlYrYArzm.png": "EeMHzWdZygXoXVnk.png",   # NDXA200R
    "aLRUwqWnnOAkVUsE.png": "LqnzwjnmCuLSIiIJ.png",   # NYA20R
    "dwSNMinuFLvRFcBl.png": "WoTOuricVLNOZrjA.png",   # NYA50R
    "DWVaHZsujoNKTGFB.png": "SXjAwlrLhQpDobVl.png",   # NYA200R
    "rhOaquSPLXjAmwcG.png": "atToNJzyXaRJbfPN.png",   # Stockbee (replacing MarketInOut slot)
    "brlBogwNeKchEFhK.png": "atToNJzyXaRJbfPN.png",   # Stockbee MM
}

with open('/home/ubuntu/swing-trader-daily/2026-03-24.html', 'r', encoding='utf-8') as f:
    html = f.read()

count = 0
for old_file, new_file in replacements.items():
    old_url = BASE + old_file
    new_url = BASE + new_file
    if old_url in html:
        html = html.replace(old_url, new_url)
        count += 1
        print(f"✓ Replaced {old_file[:20]}... -> {new_file[:20]}...")
    else:
        print(f"✗ NOT FOUND: {old_file}")

# Also replace Fullstack URL - need to find it in the HTML
# The fullstack image was the first one in the original template (before the breadth charts)
# Let's check what other CDN URLs might be in the file
import re
all_cdn = re.findall(r'https://files\.manuscdn\.com/[^\s"]+\.png', html)
print(f"\nRemaining CDN URLs in HTML: {len(set(all_cdn))}")
for url in set(all_cdn):
    print(f"  {url[-40:]}")

with open('/home/ubuntu/swing-trader-daily/2026-03-24.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"\n✓ Done. Replaced {count} URLs.")
