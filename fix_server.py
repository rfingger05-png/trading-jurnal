with open('server.ts', 'r') as f:
    server_content = f.read()

if "initTelegramBot(db);" in server_content:
    server_content = server_content.replace(
        "initTelegramBot(db);",
        """const bot = initTelegramBot(db);

// Webhook config for Vercel/Serverless
app.use(bot.webhookCallback('/api/webhook'));

// Local development fallback
if (process.env.NODE_ENV !== 'production' || process.env.RENDER || process.env.VITE_DEV_SERVER) {
  bot.launch().then(() => console.log('🚀 Telegram Bot is running (Long Polling)!'));
} else {
  console.log('🚀 Telegram Bot Webhook endpoint ready at /api/webhook');
}"""
    )

with open('server.ts', 'w') as f:
    f.write(server_content)
