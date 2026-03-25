from PIL import Image

top = Image.open('/home/ubuntu/eod_data/fullstack_top_v2.png')
bottom = Image.open('/home/ubuntu/eod_data/fullstack_bottom_v2.png')

w = max(top.width, bottom.width)
total_h = top.height + bottom.height

combined = Image.new('RGB', (w, total_h), (255, 255, 255))
combined.paste(top, (0, 0))
combined.paste(bottom, (0, top.height))
combined.save('/home/ubuntu/eod_data/fullstack_v2_combined.png')
print(f"Saved: {w}x{total_h}")
