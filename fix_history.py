import re

with open('src/components/History.tsx', 'r') as f:
    content = f.read()

content = content.replace("trade.result === 'Win'", "trade.result && trade.result.toLowerCase() === 'win'")
content = content.replace("trade.result === 'Loss'", "trade.result && trade.result.toLowerCase() === 'loss'")

with open('src/components/History.tsx', 'w') as f:
    f.write(content)

