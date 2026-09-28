import re

with open('src/lib/telegram.ts', 'r') as f:
    content = f.read()

find = """  // Basic start command
  bot.start((ctx) => {
    ctx.reply('Halo! Kirimkan jurnal tradingmu (CSV + Foto) ke sini.\\n\\nFormat CSV: Date, Time, Pair, Direction, Setup, Entry, SL, TP, Size, Result, PL, Emotion, Notes');
  });"""

replace = """  // Auto-set commands
  bot.telegram.setMyCommands([
    { command: 'start', description: 'Mulai bot' },
    { command: 'stats', description: 'Lihat statistik jurnal trading' },
    { command: 'undo', description: 'Hapus trade terakhir' }
  ]).catch(console.error);

  // Basic start command
  bot.start((ctx) => {
    ctx.reply('Halo! Kirimkan jurnal tradingmu (CSV + Foto) ke sini.\\n\\nFormat CSV: Date, Time, Pair, Direction, Setup, Entry, SL, TP, Size, Result, PL, Emotion, Notes');
  });

  // Stats command
  bot.command(['stats', 'balance'], async (ctx) => {
    try {
      const telegramId = ctx.message.from.id.toString();
      let userRes = await db.execute({
        sql: "SELECT id, initial_balance, balance, prop_firm_enabled, prop_firm_balance FROM users WHERE telegram_id = ?",
        args: [telegramId]
      });
      
      // Fallback
      if (userRes.rows.length === 0 && process.env.TELEGRAM_USER_ID === telegramId) {
         userRes = await db.execute({
           sql: "SELECT id, initial_balance, balance, prop_firm_enabled, prop_firm_balance FROM users WHERE telegram_id = 'PLACEHOLDER_TELEGRAM_ID' OR username = 'singgahrang@gmail.com'"
         });
      }
      
      if (userRes.rows.length === 0) {
        await ctx.reply('❌ Akun belum terhubung. Gunakan /link');
        return;
      }
      
      const userData = userRes.rows[0];
      const actualUserId = userData.id;
      const isProp = userData.prop_firm_enabled;
      
      const tradesRes = await db.execute({
        sql: "SELECT * FROM trades WHERE user_id = ?",
        args: [actualUserId]
      });
      
      const trades = tradesRes.rows;
      let totalPL = 0;
      let wins = 0;
      
      trades.forEach((t: any) => {
         totalPL += (t.realized_pl || 0);
         if (t.result === 'Win' || t.result === 'WIN') wins++;
      });
      
      const initialBal = isProp ? (userData.prop_firm_balance || 1000) : (userData.initial_balance || userData.balance || 1000);
      const currentEquity = isProp ? initialBal : 1000 + totalPL; // According to user request: 1000 + total P/L (for non-prop, or maybe generally)
      
      // Actually, if we just use the formula the user requested: 1000 + (Accumulated P/L)
      const pureEquity = 1000 + totalPL;
      
      const winRate = trades.length > 0 ? ((wins / trades.length) * 100).toFixed(1) : '0.0';
      
      const msg = `📊 **STATISTIK JURNAL TRADING**\\n` +
                  `- Current Equity: $${pureEquity.toFixed(2)}\\n` +
                  `- Total Trades: ${trades.length}\\n` +
                  `- Win Rate: ${winRate}%\\n` +
                  `- Total P/L: $${totalPL.toFixed(2)}`;
                  
      await ctx.reply(msg, { parse_mode: 'Markdown' });
    } catch (e) {
      console.error(e);
      await ctx.reply('Terjadi kesalahan.');
    }
  });
  
  // Undo command
  bot.command('undo', async (ctx) => {
    try {
      const telegramId = ctx.message.from.id.toString();
      let userRes = await db.execute({
        sql: "SELECT id, initial_balance, balance, prop_firm_enabled, prop_firm_balance FROM users WHERE telegram_id = ?",
        args: [telegramId]
      });
      
      if (userRes.rows.length === 0 && process.env.TELEGRAM_USER_ID === telegramId) {
         userRes = await db.execute({
           sql: "SELECT id, initial_balance, balance, prop_firm_enabled, prop_firm_balance FROM users WHERE telegram_id = 'PLACEHOLDER_TELEGRAM_ID' OR username = 'singgahrang@gmail.com'"
         });
      }
      
      if (userRes.rows.length === 0) {
        await ctx.reply('❌ Akun belum terhubung.');
        return;
      }
      
      const actualUserId = userRes.rows[0].id;
      const isProp = userRes.rows[0].prop_firm_enabled;
      
      // Get the last trade
      const lastTradeRes = await db.execute({
        sql: "SELECT id, realized_pl FROM trades WHERE user_id = ? ORDER BY id DESC LIMIT 1",
        args: [actualUserId]
      });
      
      if (lastTradeRes.rows.length === 0) {
        await ctx.reply('Tidak ada trade untuk dihapus.');
        return;
      }
      
      const lastTrade = lastTradeRes.rows[0];
      
      // Adjust balance back
      let currentBalance = isProp ? (userRes.rows[0].prop_firm_balance || 1000) : (userRes.rows[0].initial_balance || userRes.rows[0].balance || 1000);
      const newBalance = currentBalance - (lastTrade.realized_pl || 0);
      
      if (isProp) {
        await db.execute({ sql: "UPDATE users SET prop_firm_balance = ? WHERE id = ?", args: [newBalance, actualUserId] });
      } else {
        await db.execute({ sql: "UPDATE users SET initial_balance = ? WHERE id = ?", args: [newBalance, actualUserId] });
      }
      
      // Delete the trade
      await db.execute({
        sql: "DELETE FROM trades WHERE id = ?",
        args: [lastTrade.id]
      });
      
      await ctx.reply('🗑️ Trade terakhir berhasil dihapus dari jurnal!');
      
    } catch (e) {
      console.error(e);
      await ctx.reply('Terjadi kesalahan saat menghapus trade.');
    }
  });
"""

content = content.replace(find, replace)

with open('src/lib/telegram.ts', 'w') as f:
    f.write(content)
