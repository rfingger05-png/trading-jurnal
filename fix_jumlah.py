with open('src/lib/telegram.ts', 'r') as f:
    content = f.read()

content = content.replace("`/settarget <jumlah>`", "`/settarget [jumlah]`")

with open('src/lib/telegram.ts', 'w') as f:
    f.write(content)
