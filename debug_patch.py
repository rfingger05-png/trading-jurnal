import re

with open('src/lib/telegram.ts', 'r') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "bot.on(message(" in line:
        print(i, line.strip())
