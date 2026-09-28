import { Telegraf } from 'telegraf';
import dotenv from 'dotenv';
dotenv.config();

const bot = new Telegraf(process.env.TELEGRAM_BOT_TOKEN!);
async function check() {
    const info = await bot.telegram.getWebhookInfo();
    console.log("Webhook info:", info);
}
check();
