with open('server.ts', 'r') as f:
    content = f.read()

target = "bot.launch().then(() => console.log('🚀 Telegram Bot is running (Long Polling)!'));"
replacement = """bot.launch().then(() => console.log('🚀 Telegram Bot is running (Long Polling)!')).catch((err) => {
    console.warn('⚠️ Telegram Bot long polling disabled. A webhook is likely active on Telegram for this bot token.');
  });"""

if target in content:
    with open('server.ts', 'w') as f:
        f.write(content.replace(target, replacement))
        print("Fixed bot.launch()")
else:
    print("Target not found")
