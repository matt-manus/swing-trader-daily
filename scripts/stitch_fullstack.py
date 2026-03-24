#!/usr/bin/env python3
"""Stitch Fullstack Investor screenshots into one full-page image"""
from PIL import Image
import os

top = Image.open('/home/ubuntu/eod_data/fullstack_top.png')
bottom = Image.open('/home/ubuntu/eod_data/fullstack_bottom.png')

# Get dimensions
w1, h1 = top.size
w2, h2 = bottom.size

# Use max width
width = max(w1, w2)

# Create combined image
combined = Image.new('RGB', (width, h1 + h2), (13, 17, 23))
combined.paste(top, (0, 0))
combined.paste(bottom, (0, h1))

output_path = '/home/ubuntu/eod_data/fullstack_combined.png'
combined.save(output_path, 'PNG')
print(f"Saved combined image: {output_path} ({width}x{h1+h2})")
