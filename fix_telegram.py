import re

with open('src/lib/telegram.ts', 'r') as f:
    content = f.read()

# 1. Update /news command
old_news = """  bot.command('news', async (ctx) => {
    try {
      await ctx.reply('⏳ Mengambil data Kalender Ekonomi...');
      const res = await fetch('https://nfs.faireconomy.media/ff_calendar_thisweek.json');
      const data = await res.json();
      
      const highImpact = data.filter((item: any) => 
        (item.country === 'USD' || item.country === 'XAU') && item.impact === 'High'
      );
      
      if (highImpact.length === 0) {
        return ctx.reply('🗓️ Tidak ada High Impact News (USD) untuk minggu ini.');
      }
      
      // Group by date
      const grouped: any = {};
      highImpact.forEach((item: any) => {
         const date = new Date(item.date);
         // Format as YYYY-MM-DD
         const dateStr = date.toISOString().split('T')[0];
         if (!grouped[dateStr]) grouped[dateStr] = [];
         grouped[dateStr].push(item);
      });
      
      let msg = `📅 <b>HIGH IMPACT NEWS (USD) MINGGU INI</b>\\n━━━━━━━━━━━━━━━━━━━\\n`;
      
      for (const dateStr of Object.keys(grouped).sort()) {
         const d = new Date(dateStr);
         const dayName = d.toLocaleDateString('id-ID', { weekday: 'long' });
         const formattedDate = d.toLocaleDateString('id-ID', { day: '2-digit', month: 'long', year: 'numeric' });
         
         msg += `\\n📆 <b>${dayName}, ${formattedDate}</b>\\n`;
         
         grouped[dateStr].forEach((item: any) => {
            const timeDate = new Date(item.date);
            const timeStr = timeDate.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' }) + ' WIB';
            msg += `⏰ ${timeStr} | 🔴 ${item.title}\\n`;
         });
      }
      
      await ctx.reply(msg, { parse_mode: 'HTML' });
      
    } catch (e) {
      console.error(e);
      await ctx.reply('❌ Gagal mengambil data berita ekonomi.');
    }
  });"""

new_news = """  bot.command('news', async (ctx) => {
    try {
      await ctx.reply('⏳ Mengambil data Kalender Ekonomi...');
      const res = await fetch('https://nfs.faireconomy.media/ff_calendar_thisweek.json');
      const data = await res.json();
      
      const highImpact = data.filter((item: any) => 
        (item.country === 'USD' || item.country === 'XAU') && item.impact === 'High'
      );
      
      if (highImpact.length === 0) {
        return ctx.reply('🗓️ Tidak ada High Impact News (USD) untuk minggu ini.');
      }
      
      // Group by date
      const grouped: any = {};
      highImpact.forEach((item: any) => {
         const date = new Date(item.date);
         
         // Format as YYYY-MM-DD in Asia/Jakarta timezone
         const dateFormatter = new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Jakarta', year: 'numeric', month: '2-digit', day: '2-digit' });
         const dateStr = dateFormatter.format(date); // YYYY-MM-DD
         
         if (!grouped[dateStr]) grouped[dateStr] = [];
         grouped[dateStr].push(item);
      });
      
      let msg = `📅 <b>HIGH IMPACT NEWS (USD) - MINGGU INI</b>\\n\\n`;
      
      for (const dateStr of Object.keys(grouped).sort()) {
         const d = new Date(dateStr + "T12:00:00Z"); // Parse just the date to avoid UTC shifts
         const dayName = d.toLocaleDateString('id-ID', { weekday: 'long', timeZone: 'Asia/Jakarta' });
         const formattedDate = d.toLocaleDateString('id-ID', { day: '2-digit', month: 'long', year: 'numeric', timeZone: 'Asia/Jakarta' });
         
         msg += `🗓 <b>${dayName}, ${formattedDate}</b>\\n`;
         
         grouped[dateStr].forEach((item: any) => {
            const timeDate = new Date(item.date);
            const timeFormatter = new Intl.DateTimeFormat('id-ID', { timeZone: 'Asia/Jakarta', hour: '2-digit', minute: '2-digit' });
            const timeStr = timeFormatter.format(timeDate).replace('.', ':');
            msg += `• ${timeStr} WIB 🔴 ${item.title}\\n`;
         });
         msg += `\\n`;
      }
      
      await ctx.reply(msg.trimEnd(), { parse_mode: 'HTML' });
      
    } catch (e) {
      console.error(e);
      await ctx.reply('❌ Gagal mengambil data berita ekonomi.');
    }
  });"""

content = content.replace(old_news, new_news)

# 2. Update getStatsBalance
old_stats_balance = """      const initialBal = isProp ? (userData.prop_firm_balance || 1000) : (userData.initial_balance || 1000);
      const pureEquity = initialBal + totalPL;"""

new_stats_balance = """      const txRes = await db.execute({
        sql: "SELECT type, amount FROM transactions WHERE user_id = ?",
        args: [actualUserId]
      });
      
      let totalDeposit = 0;
      let totalWithdraw = 0;
      txRes.rows.forEach((tx: any) => {
         if (tx.type === 'deposit') totalDeposit += (tx.amount || 0);
         if (tx.type === 'withdrawal') totalWithdraw += (tx.amount || 0);
      });

      const initialBal = isProp ? (userData.prop_firm_balance || 1000) : (userData.initial_balance || 1000);
      const pureEquity = initialBal + totalDeposit - totalWithdraw + totalPL;"""

content = content.replace(old_stats_balance, new_stats_balance)

# 3. Update getStatsByTimeframe equity calculation
old_timeframe_equity = """      const initialBal = isProp ? (userData.prop_firm_balance || 1000) : (userData.initial_balance || 1000);
      let totalPastPL = 0;
      allTrades.forEach((t: any) => totalPastPL += (t.realized_pl || 0));
      const currentEquity = initialBal + totalPastPL;
      
      let peakEquity = initialBal;
      let runningEq = initialBal;
      allTrades.forEach((t: any) => {
         runningEq += (t.realized_pl || 0);
         if (runningEq > peakEquity) peakEquity = runningEq;
      });"""

new_timeframe_equity = """      const txRes = await db.execute({
        sql: "SELECT type, amount FROM transactions WHERE user_id = ?",
        args: [actualUserId]
      });
      
      let totalDeposit = 0;
      let totalWithdraw = 0;
      txRes.rows.forEach((tx: any) => {
         if (tx.type === 'deposit') totalDeposit += (tx.amount || 0);
         if (tx.type === 'withdrawal') totalWithdraw += (tx.amount || 0);
      });

      const initialBal = isProp ? (userData.prop_firm_balance || 1000) : (userData.initial_balance || 1000);
      let totalPastPL = 0;
      allTrades.forEach((t: any) => totalPastPL += (t.realized_pl || 0));
      const currentEquity = initialBal + totalDeposit - totalWithdraw + totalPastPL;
      
      const baselineEq = initialBal + totalDeposit - totalWithdraw;
      let peakEquity = baselineEq;
      let runningEq = baselineEq;
      allTrades.forEach((t: any) => {
         runningEq += (t.realized_pl || 0);
         if (runningEq > peakEquity) peakEquity = runningEq;
      });"""

content = content.replace(old_timeframe_equity, new_timeframe_equity)

with open('src/lib/telegram.ts', 'w') as f:
    f.write(content)

