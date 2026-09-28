import re

with open('src/lib/telegram.ts', 'r') as f:
    lines = f.readlines()

start_idx = -1
for i, line in enumerate(lines):
    if "bot.on(message('text')" in line:
        start_idx = i
        break

end_idx = -1
for i in range(start_idx + 1, len(lines)):
    if "bot.on(message('photo')" in lines[i]:
        end_idx = i
        break

new_handler = """  bot.on(message('text'), async (ctx) => {
    try {
      const text = ctx.message.text;
      if (text.startsWith('/')) return; // Ignore other commands

      const tvRegex = /(https?:\\/\\/(?:www\\.)?tradingview\\.com\\/x\\/[\\w-]+\\/?)/i;
      const tvMatch = text.match(tvRegex);
      const tvUrl = tvMatch ? tvMatch[1] : null;
      let hasImage = 0;
      if (tvUrl) {
        hasImage = 1;
      }

      const cleanedText = text.replace(tvRegex, '').trim();

      // Check if looks like a CSV (at least 10 fields expected)
      if (cleanedText.includes(',')) {
        const parts = parseCSVLine(cleanedText);
        
        if (parts.length >= 11 && ['BUY', 'SELL'].includes(parts[3].toUpperCase())) {
          // Parse fields
          const [dateStr, timeStr, pair, type, setup, entry, sl, tp, lot, status, pnl, emosi, ...notesArr] = parts;
          const notes = notesArr.join(', ');

          // Validate user
          const telegramId = ctx.from?.id?.toString();
          let userRes = await db.execute({
            sql: "SELECT id, current_mode, prop_firm_enabled, prop_firm_balance, initial_balance FROM users WHERE telegram_id = ?",
            args: [telegramId]
          });
          
          if (userRes.rows.length === 0 && process.env.TELEGRAM_USER_ID === telegramId) {
            userRes = await db.execute({
              sql: "SELECT id, current_mode, prop_firm_enabled, prop_firm_balance, initial_balance FROM users WHERE telegram_id = 'PLACEHOLDER_TELEGRAM_ID' OR username = 'singgahrang@gmail.com'"
            });
            
            if (userRes.rows.length > 0) {
              await db.execute({
                sql: "UPDATE users SET telegram_id = ? WHERE id = ?",
                args: [telegramId, userRes.rows[0].id]
              });
            }
          }
          
          if (userRes.rows.length === 0) {
            await ctx.reply('❌ Akun Telegram belum terhubung dengan akun Web.');
            return;
          }
          
          const userData = userRes.rows[0];
          const actualUserId = userData.id;
          const mode = userData.current_mode || 'backtest';
          
          // Compute Balance
          const existingTrades = await db.execute({
            sql: "SELECT realized_pl FROM trades WHERE user_id = ?",
            args: [actualUserId]
          });
          const totalPastPL = existingTrades.rows.reduce((acc, t: any) => acc + (t.realized_pl || 0), 0);
          
          const isProp = userData.prop_firm_enabled;
          const initialBal = isProp ? (userData.prop_firm_balance || 1000) : (userData.initial_balance || 1000);
          const oldBalance = initialBal + totalPastPL;
          const realizedPl = parseFloat(pnl) || 0;
          const newBalance = oldBalance + realizedPl;
          
          // Format date if needed
          let created_at = new Date().toISOString();
          try {
             // e.g. 2026-08-25 10:00 -> Date object
             const parsedDate = new Date(`${dateStr} ${timeStr}`);
             if (!isNaN(parsedDate.getTime())) {
                created_at = parsedDate.toISOString();
             }
          } catch(e) {}
          
          await db.execute({
            sql: `INSERT INTO trades (
              user_id, pair, direction, setup_name, entry_price, sl, tp, 
              account_balance, position_size, result, realized_pl, 
              anxiety_level, notes, image_url, has_image, run_mode, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
            args: [
              actualUserId, pair, type.toUpperCase(), setup, parseFloat(entry)||0, parseFloat(sl)||0, parseFloat(tp)||0,
              newBalance, parseFloat(lot)||0, status.toUpperCase(), realizedPl,
              emosi, notes, tvUrl, hasImage, mode, created_at
            ]
          });
          
          const sign = realizedPl >= 0 ? '+' : '';
          let msg = `✅ TRADE LOGGED SUCCESSFULLY (CSV)\\n----------------------------------\\n` +
                    `📊 Pair: ${pair} (${type.toUpperCase()})\\n` +
                    `💰 P/L Realized: ${sign}${realizedPl} (${status.toUpperCase()})\\n`;
          if (tvUrl) {
            msg += `🖼️ Chart: ${tvUrl}\\n`;
          }
          
          await ctx.reply(msg, { disable_web_page_preview: false });
          return;
        }
      }
    } catch (e) {
      console.error("Text parsing error:", e);
      await ctx.reply('❌ Terjadi kesalahan saat memproses data CSV.');
    }
  });\n\n"""

if start_idx != -1 and end_idx != -1:
    lines[start_idx:end_idx] = [new_handler]
    with open('src/lib/telegram.ts', 'w') as f:
        f.writelines(lines)
    print("CSV handler replaced.")
else:
    print(f"Could not find blocks. start: {start_idx}, end: {end_idx}")

