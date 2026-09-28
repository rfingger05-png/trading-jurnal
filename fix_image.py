import re

with open('src/lib/discord.ts', 'r') as f:
    content = f.read()

find = """    // Download image
    const res = await fetch(attachment.url);
    const buffer = await res.arrayBuffer();
    const base64Image = `data:${attachment.contentType};base64,${Buffer.from(buffer).toString('base64')}`;"""

replace = """    // Get image URL directly
    const imageUrl = attachment.url;"""

content = content.replace(find, replace)

find_insert = """        tradeData.emotionScore, tradeData.notes, tradeData.result, tradeData.pl, base64Image, mode, created_at"""
replace_insert = """        tradeData.emotionScore, tradeData.notes, tradeData.result, tradeData.pl, imageUrl, mode, created_at"""

content = content.replace(find_insert, replace_insert)

with open('src/lib/discord.ts', 'w') as f:
    f.write(content)

