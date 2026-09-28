import re

with open('src/components/History.tsx', 'r') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "window.open(trade.image" in line:
        lines[i] = line.replace("window.open(trade.image, '_blank')", "window.open(formatImageUrl(trade.image || trade.image_url), '_blank')")
    if "{trade.image ? (" in line:
        lines[i] = line.replace("{trade.image ? (", "{(trade.image || trade.image_url) ? (")

with open('src/components/History.tsx', 'w') as f:
    f.writelines(lines)
