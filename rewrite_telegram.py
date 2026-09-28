import re

with open('src/lib/telegram.ts', 'r') as f:
    content = f.read()

# Replace ctx.message.from.id.toString() with ctx.from?.id?.toString()
content = content.replace("ctx.message.from.id.toString()", "ctx.from?.id?.toString()")

with open('src/lib/telegram.ts', 'w') as f:
    f.write(content)
