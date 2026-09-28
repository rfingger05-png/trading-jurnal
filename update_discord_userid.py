import re

with open('src/lib/discord.ts', 'r') as f:
    content = f.read()

# Replace parseInt logic
content = content.replace(
    "const primaryUserId = parseInt(process.env.DISCORD_PRIMARY_USER_ID || '1', 10);",
    "const primaryUserId = process.env.DISCORD_PRIMARY_USER_ID || '1540377868402692207';"
)

# Replace function signatures to accept string
content = content.replace(
    "async function handleJournalLog(message: Message, db: any, userId: number, client: Client, channels: any)",
    "async function handleJournalLog(message: Message, db: any, userId: string, client: Client, channels: any)"
)

content = content.replace(
    "async function updateLiveStats(client: Client, db: any, channelId: string, userId: number)",
    "async function updateLiveStats(client: Client, db: any, channelId: string, userId: string)"
)

content = content.replace(
    "async function sendWeeklyReview(client: Client, db: any, channelId: string, userId: number)",
    "async function sendWeeklyReview(client: Client, db: any, channelId: string, userId: string)"
)

with open('src/lib/discord.ts', 'w') as f:
    f.write(content)
