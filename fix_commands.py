import re

with open('src/lib/telegram.ts', 'r') as f:
    content = f.read()

# 1. Start command
find_start = """  bot.start((ctx) => {
    ctx.reply('Halo! Kirimkan jurnal tradingmu (CSV + Foto) ke sini.\\n\\nFormat CSV: Date, Time, Pair, Direction, Setup, Entry, SL, TP, Size, Result, PL, Emotion, Notes');
  });"""
replace_start = """  const handleStart = async (ctx: any) => {
    await ctx.reply('Halo! Kirimkan jurnal tradingmu (CSV + Foto) ke sini.\\n\\nFormat CSV: Date, Time, Pair, Direction, Setup, Entry, SL, TP, Size, Result, PL, Emotion, Notes');
  };
  bot.start(handleStart);"""
content = content.replace(find_start, replace_start)

# 2. Stats/Balance command
find_stats = """  bot.command(['stats', 'balance'], async (ctx) => {
    try {"""
replace_stats = """  const getStatsBalance = async (ctx: any) => {
    try {"""
content = content.replace(find_stats, replace_stats)

find_stats_end = """      const msg = `📊 <b>STATISTIK AKUN</b>\\n` +
                  `━━━━━━━━━━━━━━━━━━━\\n` +
                  `Account Type: ${isProp ? 'Prop Firm' : 'Personal'}\\n` +
                  `Initial Balance: $${initialBal.toFixed(2)}\\n` +
                  `Current Equity: <b>$${pureEquity.toFixed(2)}</b>\\n\\n` +
                  `Total Trades: ${trades.length}\\n` +
                  `Win Rate: ${winRate}%\\n` +
                  `Net P/L: ${signPL}$${totalPL.toFixed(2)}\\n\\n` +
                  `<i>Untuk melihat statistik detail per timeframe, gunakan /today, /weekly, /monthly.</i>`;
      
      await ctx.reply(msg, { parse_mode: 'HTML' });
    } catch (e) {
      console.error(e);
      await ctx.reply('Terjadi kesalahan.');
    }
  });"""
replace_stats_end = """      const msg = `📊 <b>STATISTIK AKUN</b>\\n` +
                  `━━━━━━━━━━━━━━━━━━━\\n` +
                  `Account Type: ${isProp ? 'Prop Firm' : 'Personal'}\\n` +
                  `Initial Balance: $${initialBal.toFixed(2)}\\n` +
                  `Current Equity: <b>$${pureEquity.toFixed(2)}</b>\\n\\n` +
                  `Total Trades: ${trades.length}\\n` +
                  `Win Rate: ${winRate}%\\n` +
                  `Net P/L: ${signPL}$${totalPL.toFixed(2)}\\n\\n` +
                  `<i>Untuk melihat statistik detail per timeframe, gunakan /today, /weekly, /monthly.</i>`;
      
      await ctx.reply(msg, { parse_mode: 'HTML' });
    } catch (e) {
      console.error(e);
      await ctx.reply('Terjadi kesalahan.');
    }
  };
  bot.command(['stats', 'balance'], getStatsBalance);"""
content = content.replace(find_stats_end, replace_stats_end)

# 3. Undo command
find_undo = """  bot.command('undo', async (ctx) => {
    try {"""
replace_undo = """  const handleUndo = async (ctx: any) => {
    try {"""
content = content.replace(find_undo, replace_undo)

find_undo_end = """      await ctx.reply('🗑️ Trade terakhir berhasil dihapus dari jurnal!');
      
    } catch (e) {
      console.error(e);
      await ctx.reply('Terjadi kesalahan saat menghapus trade.');
    }
  });"""
replace_undo_end = """      await ctx.reply('🗑️ Trade terakhir berhasil dihapus dari jurnal!');
      
    } catch (e) {
      console.error(e);
      await ctx.reply('Terjadi kesalahan saat menghapus trade.');
    }
  };
  bot.command('undo', handleUndo);"""
content = content.replace(find_undo_end, replace_undo_end)

with open('src/lib/telegram.ts', 'w') as f:
    f.write(content)
