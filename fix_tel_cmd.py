import re

with open('src/lib/telegram.ts', 'r') as f:
    content = f.read()

find_menu = """  // Auto-set commands
  bot.telegram.setMyCommands([
    { command: 'start', description: 'Mulai bot' },
    { command: 'stats', description: 'Lihat statistik jurnal trading' },
    { command: 'today', description: 'Ringkasan trade hari ini' },
    { command: 'weekly', description: 'Ringkasan performa 7 hari terakhir' },
    { command: 'monthly', description: 'Ringkasan performa bulan berjalan' },
    { command: 'compound', description: 'Proyeksi pertumbuhan modal 30 hari' },
    { command: 'undo', description: 'Hapus trade terakhir' }
  ]).catch(console.error);"""

replace_menu = """  // Auto-set commands
  bot.telegram.setMyCommands([
    { command: 'start', description: 'Mulai bot' },
    { command: 'stats', description: 'Lihat statistik jurnal trading' },
    { command: 'today', description: 'Ringkasan trade hari ini' },
    { command: 'weekly', description: 'Ringkasan performa 7 hari terakhir' },
    { command: 'monthly', description: 'Ringkasan performa bulan berjalan' },
    { command: 'compound', description: 'Proyeksi pertumbuhan modal dinamis' },
    { command: 'dailydd', description: 'Pantau sisa Trailing Daily Drawdown' },
    { command: 'monthlydd', description: 'Pantau status Trailing Monthly Drawdown' },
    { command: 'undo', description: 'Hapus trade terakhir' }
  ]).catch(console.error);"""
content = content.replace(find_menu, replace_menu)

find_logic = """      let filteredTrades: any[] = [];
      const now = new Date();
      let label = "";
      
      if (timeframe === 'today') {"""

replace_logic = """      let peakEquity = initialBal;
      let runningEq = initialBal;
      allTrades.forEach((t: any) => {
         runningEq += (t.realized_pl || 0);
         if (runningEq > peakEquity) peakEquity = runningEq;
      });
      
      let filteredTrades: any[] = [];
      const now = new Date();
      let label = "";
      
      if (timeframe === 'dailydd') {
         const dailyDDAmount = peakEquity * (dailyDDPct / 100);
         const dailyDDViolationPoint = peakEquity - dailyDDAmount;
         const dailyDDRemaining = currentEquity - dailyDDViolationPoint;
         
         let msg = `🛡️ <b>TRAILING DAILY DRAWDOWN</b>\\n<i>(Limit ${dailyDDPct}% dari High Watermark)</i>\\n━━━━━━━━━━━━━━━━━━━\\n`;
         msg += `High Watermark: <b>$${peakEquity.toFixed(2)}</b>\\n`;
         msg += `Max Daily Loss: $${dailyDDAmount.toFixed(2)}\\n`;
         msg += `Violation Point: $${dailyDDViolationPoint.toFixed(2)}\\n\\n`;
         msg += `Current Equity: <b>$${currentEquity.toFixed(2)}</b>\\n`;
         if (dailyDDRemaining <= 0) {
            msg += `❌ <b>Sisa Limit: $0.00 (VIOLATED)</b>`;
         } else {
            msg += `✅ <b>Sisa Limit: $${dailyDDRemaining.toFixed(2)}</b>`;
         }
         await ctx.reply(msg, { parse_mode: 'HTML' });
         return;
      } else if (timeframe === 'monthlydd') {
         const monthlyDDAmount = peakEquity * 0.50; // 50%
         const monthlyDDViolationPoint = peakEquity - monthlyDDAmount;
         const monthlyDDRemaining = currentEquity - monthlyDDViolationPoint;
         
         let msg = `🛡️ <b>TRAILING MONTHLY DRAWDOWN</b>\\n<i>(Limit 50% dari High Watermark)</i>\\n━━━━━━━━━━━━━━━━━━━\\n`;
         msg += `High Watermark: <b>$${peakEquity.toFixed(2)}</b>\\n`;
         msg += `Max Monthly Loss: $${monthlyDDAmount.toFixed(2)}\\n`;
         msg += `Violation Point: $${monthlyDDViolationPoint.toFixed(2)}\\n\\n`;
         msg += `Current Equity: <b>$${currentEquity.toFixed(2)}</b>\\n`;
         if (monthlyDDRemaining <= 0) {
            msg += `❌ <b>Sisa Limit: $0.00 (VIOLATED)</b>`;
         } else {
            msg += `✅ <b>Sisa Limit: $${monthlyDDRemaining.toFixed(2)}</b>`;
         }
         await ctx.reply(msg, { parse_mode: 'HTML' });
         return;
      } else if (timeframe === 'today') {"""

content = content.replace(find_logic, replace_logic)

find_extra = """      let extraInfo = '';
      if (timeframe === 'today') {
         // Calculate Trailing Daily DD Remaining
         const totalPLToday = totalPL;
         const startOfDayEquity = currentEquity - totalPLToday;
         let peakToday = startOfDayEquity;
         let runningToday = startOfDayEquity;
         filteredTrades.forEach(t => {
            runningToday += (t.realized_pl || 0);
            if (runningToday > peakToday) peakToday = runningToday;
         });
         const dailyDDAmount = peakToday * (dailyDDPct / 100);
         const dailyDDViolationPoint = peakToday - dailyDDAmount;
         const dailyDDRemaining = currentEquity - dailyDDViolationPoint;
         extraInfo = `\\n- Sisa Daily DD: $${dailyDDRemaining.toFixed(2)}`;
      }
      
      const msg = `📊 <b>RINGKASAN ${label}</b>\\n` +
                  `━━━━━━━━━━━━━━━━━━━\\n` +
                  `- Total Trades: ${filteredTrades.length}\\n` +
                  `- Win Rate: ${winRate}%\\n` +
                  `- Net P/L: ${signPL}$${totalPL.toFixed(2)}${extraInfo}`;"""

replace_extra = """      const msg = `📊 <b>RINGKASAN ${label}</b>\\n` +
                  `━━━━━━━━━━━━━━━━━━━\\n` +
                  `- Total Trades: ${filteredTrades.length}\\n` +
                  `- Win Rate: ${winRate}%\\n` +
                  `- Net P/L: ${signPL}$${totalPL.toFixed(2)}`;"""

content = content.replace(find_extra, replace_extra)


find_register = """  bot.command('compound', async (ctx) => getStatsByTimeframe(ctx, 'compound'));"""

replace_register = """  bot.command('compound', async (ctx) => getStatsByTimeframe(ctx, 'compound'));
  bot.command('dailydd', async (ctx) => getStatsByTimeframe(ctx, 'dailydd'));
  bot.command('monthlydd', async (ctx) => getStatsByTimeframe(ctx, 'monthlydd'));"""

content = content.replace(find_register, replace_register)

with open('src/lib/telegram.ts', 'w') as f:
    f.write(content)

