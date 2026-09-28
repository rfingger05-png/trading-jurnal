import fs from 'fs';
let content = fs.readFileSync('src/lib/telegram.ts', 'utf-8');
const anchor2 = `         userRes = await db.execute({
           sql: "SELECT id, current_mode, prop_firm_enabled, prop_firm_balance, initial_balance, balance FROM users WHERE telegram_id = 'PLACEHOLDER_TELEGRAM_ID' OR username = 'jal'"
         });`;
const newAnchor2 = `         userRes = await db.execute({
           sql: "SELECT id, current_mode, prop_firm_enabled, prop_firm_balance, initial_balance, balance FROM users WHERE telegram_id = 'PLACEHOLDER_TELEGRAM_ID' OR username = 'singgahrang@gmail.com'"
         });`;

if (content.includes(anchor2)) {
  content = content.replace(anchor2, newAnchor2);
  fs.writeFileSync('src/lib/telegram.ts', content);
  console.log("Patched bottom fallback too!");
} else {
  console.log("Could not find bottom anchor!");
}
