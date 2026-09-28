import fs from 'fs';

let content = fs.readFileSync('src/lib/telegram.ts', 'utf-8');

const anchor = `          if (userRes.rows.length === 0 && process.env.TELEGRAM_USER_ID === telegramId) {
            userRes = await db.execute({
              sql: "SELECT id, current_mode, prop_firm_enabled, prop_firm_balance, initial_balance FROM users WHERE telegram_id = 'PLACEHOLDER_TELEGRAM_ID' OR username = 'jal'"
            });`;
const newAnchor = `          if (userRes.rows.length === 0 && process.env.TELEGRAM_USER_ID === telegramId) {
            userRes = await db.execute({
              sql: "SELECT id, current_mode, prop_firm_enabled, prop_firm_balance, initial_balance FROM users WHERE telegram_id = 'PLACEHOLDER_TELEGRAM_ID' OR username = 'singgahrang@gmail.com'"
            });`;

if (content.includes(anchor)) {
  content = content.replace(anchor, newAnchor);
  fs.writeFileSync('src/lib/telegram.ts', content);
  console.log("Patched username fallback to singgahrang@gmail.com!");
} else {
  console.log("Could not find anchor!");
}
