import re

with open('src/lib/telegram.ts', 'r') as f:
    content = f.read()

content = content.replace("const dailyDDAmount = initialBal * (dailyDDPct / 100);", "const dailyDDAmount = peakToday * (dailyDDPct / 100);")

with open('src/lib/telegram.ts', 'w') as f:
    f.write(content)
