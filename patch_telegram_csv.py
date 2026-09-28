import re

with open('src/lib/telegram.ts', 'r') as f:
    content = f.read()

csv_handler = """
  // Helper to parse CSV securely
  const parseCSVLine = (line: string) => {
    const arr = [];
    let current = '';
    let inQuotes = false;
    for (let i = 0; i < line.length; i++) {
      const char = line[i];
      if (char === '"') {
        inQuotes = !inQuotes;
      } else if (char === ',' && !inQuotes) {
        arr.push(current.trim());
        current = '';
      } else {
        current += char;
      }
    }
    arr.push(current.trim());
    return arr.map(str => str.replace(/^"|"$/g, '').trim());
  };

  bot.on(message('text'), async (ctx) => {
    try {
      const text = ctx.message.text;
      if (text.startsWith('/')) return; // Ignore other commands

      const tvRegex = /(https?:\\/\\/(?:www\\.)?tradingview\\.com\\/x\\/[\\w-]+\\/?)/i;
      const tvMatch = text.match(tvRegex);
      const tvUrl = tvMatch ? tvMatch[1] : null;

      const cleanedText = text.replace(tvRegex, '').trim();

      // Check if looks like a CSV (at least 10 fields expected: Date, Time, Pair, Type, Setup, Entry, SL, TP, Lot, Status, PnL, Emotion, Notes)
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
              anxiety_level, notes, image_url, run_mode, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
            args: [
              actualUserId, pair, type.toUpperCase(), setup, parseFloat(entry)||0, parseFloat(sl)||0, parseFloat(tp)||0,
              newBalance, parseFloat(lot)||0, status.toUpperCase(), realizedPl,
              emosi, notes, tvUrl, mode, created_at
            ]
          });
          
          const sign = realizedPl >= 0 ? '+' : '';
          let msg = `✅ <b>TRADE LOGGED SUCCESSFULLY (CSV)</b>\n━━━━━━━━━━━━━━━━━━━\n` +
                    `📊 <b>Pair:</b> ${pair} (${type.toUpperCase()})\n` +
                    `💵 <b>P/L Realized:</b> ${sign}$${realizedPl.toFixed(2)} (${status.toUpperCase()})\n`;
          if (tvUrl) {
            msg += `🖼️ <b>Chart:</b> <a href="${tvUrl}">TradingView Link</a>\n`;
          }
          
          await ctx.reply(msg, { parse_mode: 'HTML', disable_web_page_preview: false });
          return;
        }
      }
    } catch (e) {
      console.error("Text parsing error:", e);
      await ctx.reply('❌ Terjadi kesalahan saat memproses data CSV.');
    }
  });
"""

# Replace "bot.on(message('photo')" with csv_handler + "bot.on(message('photo')"
anchor = "bot.on(message('photo'), async (ctx) => {"
if anchor in content:
    content = content.replace(anchor, csv_handler + "\n  " + anchor)
    with open('src/lib/telegram.ts', 'w') as f:
        f.write(content)
    print("CSV handler injected.")
else:
    print("Anchor not found.")

