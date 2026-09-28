import { Telegraf, Markup } from 'telegraf';
import { message } from 'telegraf/filters';

const sendOrEdit = async (ctx: any, msg: string, useBackButton: boolean = false) => {
  try {
    const extra: any = { parse_mode: 'HTML' };
    if (useBackButton) {
      extra.reply_markup = {
        inline_keyboard: [[{ text: '🔙 Kembali ke Menu Utama', callback_data: 'cmd_menu' }]]
      };
    }
    
    if (ctx.callbackQuery) {
       await ctx.editMessageText(msg, extra).catch(() => {});
    } else {
       await ctx.reply(msg, extra);
    }
  } catch (err) {
    console.error("sendOrEdit error:", err);
  }
};

export function parseTradeData(content: string) {
  try {
    const isJson = content.trim().startsWith('{');
    if (isJson) {
      const json = JSON.parse(content);
      return {
        dateStr: json.date ? `${json.date}T${json.time || '00:00'}:00` : '',
        pair: json.pair || 'XAUUSD',
        direction: json.direction || 'Buy',
        setup_name: json.setup_name || json.setup || 'Import',
        entry: parseFloat(json.entry_price || json.entry) || 0,
        sl: parseFloat(json.sl) || 0,
        tp: parseFloat(json.tp) || 0,
        size: parseFloat(json.position_size || json.size) || 0,
        result: json.result || 'Pending',
        pl: parseFloat(json.pl || json.realized_pl) || 0,
        emotionScore: 0,
        notes: json.notes || json.reason || 'No reason provided.'
      };
    } else {
      const parts = content.split(',').map(s => s.trim());
      if (parts.length >= 11) {
        // Schema: 0:Date, 1:Time, 2:Pair, 3:Direction, 4:Setup, 5:Entry, 6:SL, 7:TP, 8:Size, 9:Result, 10:PL, 11:Emotion, 12:Notes
        const date = parts[0] || '';
        const time = parts[1] || '';
        let combinedDate = '';
        if (date && time) {
          const cleanDate = date.replace(/\//g, '-').replace(/\./g, '-');
          combinedDate = `${cleanDate}T${time}:00`;
        }

        let emotionScore = 0;
        let emotionStr = parts[11]?.toLowerCase() || '';
        if (emotionStr.includes('anxious') || emotionStr.includes('cemas') || emotionStr.includes('takut')) {
           emotionScore = 3;
        } else if (emotionStr.includes('confident') || emotionStr.includes('yakin')) {
           emotionScore = 1;
        } else if (emotionStr) {
           emotionScore = 2; // neutral
        }

        const rawNotes = parts.length > 12 ? parts.slice(12).join(', ').trim() : '';

        return {
          dateStr: combinedDate,
          pair: parts[2]?.toUpperCase() || 'XAUUSD',
          direction: parts[3]?.toUpperCase().includes('SELL') ? 'Sell' : 'Buy',
          setup_name: parts[4] || 'Telegram Import',
          entry: parseFloat(parts[5]) || 0,
          sl: parseFloat(parts[6]) || 0,
          tp: parseFloat(parts[7]) || 0,
          size: parseFloat(parts[8]) || 0,
          result: parts[9] || 'Pending',
          pl: parseFloat(parts[10]) || 0,
          emotionScore: emotionScore,
          notes: rawNotes || 'No reason provided.'
        };
      }
    }
  } catch (e) {
    console.error("Failed to parse trade data:", e);
  }
  return null;
}

export function initTelegramBot(db: any) {
  const token = process.env.TELEGRAM_BOT_TOKEN;
  if (!token) {
    console.log('TELEGRAM_BOT_TOKEN is not set. Telegram bot will not start.');
    return;
  }

  const bot = new Telegraf(token);
  
  // Auto-set commands
  bot.telegram.setMyCommands([
    { command: 'menu', description: 'Menampilkan menu utama & tombol navigasi' },
    { command: 'lot', description: 'Kalkulator lot otomatis (Risk 2.5%)' },
    { command: 'today', description: 'Statistik & P/L hari ini' },
    { command: 'weekly', description: 'Statistik & P/L mingguan' },
    { command: 'monthly', description: 'Statistik & P/L bulanan' },
    { command: 'compound', description: 'Milestone target 10 hari (Compound 5%)' },
    { command: 'dailydd', description: 'Cek sisa batas Trailing Daily Drawdown (5%)' },
    { command: 'monthlydd', description: 'Cek batas Trailing Monthly Drawdown (50%)' },
    { command: 'undo', description: 'Hapus trade terakhir' }
  ]).catch(console.error);

  // Basic start command
  const handleStart = async (ctx: any) => {
    await ctx.reply('Halo! Kirimkan jurnal tradingmu (CSV + Foto) ke sini.\n\nFormat CSV: Date, Time, Pair, Direction, Setup, Entry, SL, TP, Size, Result, PL, Emotion, Notes');
  };
  bot.start(handleStart);

  // Stats command
  const getStatsBalance = async (ctx: any) => {
    try {
      const telegramId = ctx.from?.id?.toString();
      let userRes = await db.execute({
        sql: "SELECT id, initial_balance, prop_firm_enabled, prop_firm_balance FROM users WHERE telegram_id = ?",
        args: [telegramId]
      });
      
      // Fallback
      if (userRes.rows.length === 0 && process.env.TELEGRAM_USER_ID === telegramId) {
         userRes = await db.execute({
           sql: "SELECT id, initial_balance, prop_firm_enabled, prop_firm_balance FROM users WHERE telegram_id = 'PLACEHOLDER_TELEGRAM_ID' OR username = 'jal'"
         });
      }
      
      if (userRes.rows.length === 0) {
        await ctx.reply('❌ Akun belum terhubung. Gunakan /link');
        return;
      }
      
      const userData = userRes.rows[0];
      const actualUserId = userData.id;
      const isProp = userData.prop_firm_enabled;
      const targetBalance = userData.target_balance || 1000000;
      const compoundRisk = userData.compound_risk || 2.5;
      
      const tradesRes = await db.execute({
        sql: "SELECT realized_pl, result FROM trades WHERE user_id = ? AND result != 'Pending'",
        args: [actualUserId]
      });
      
      const trades = tradesRes.rows;
      let totalPL = 0;
      let wins = 0;
      
      trades.forEach((t: any) => {
         totalPL += (t.realized_pl || 0);
         if (t.result === 'Win' || t.result === 'WIN') wins++;
      });
      
      const txRes = await db.execute({
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
      const pureEquity = initialBal + totalDeposit - totalWithdraw + totalPL;
      
      const winRate = trades.length > 0 ? ((wins / trades.length) * 100).toFixed(1) : '0.0';
      const signPL = totalPL >= 0 ? '+' : '';
      
      const msg = `📊 <b>STATISTIK JURNAL TRADING</b>
` +
                  `━━━━━━━━━━━━━━━━━━━
` +
                  `- Current Equity: <b>$${pureEquity.toFixed(2)}</b>
` +
                  `- Total Trades: ${trades.length}
` +
                  `- Win Rate: ${winRate}%
` +
                  `- Total P/L: ${signPL}$${totalPL.toFixed(2)}`;
      
      await sendOrEdit(ctx, msg, true);
    } catch (e) {
      console.error(e);
      await sendOrEdit(ctx, 'Terjadi kesalahan.', true);
    }
  };
  bot.command(['stats', 'balance'], getStatsBalance);
  

  // Filter helper for Telegram commands
  const getStatsByTimeframe = async (ctx: any, timeframe: string) => {
    try {
      const telegramId = ctx.from?.id?.toString();
      let userRes = await db.execute({
        sql: "SELECT id, initial_balance, prop_firm_enabled, prop_firm_balance, prop_firm_daily_dd, target_balance, compound_risk FROM users WHERE telegram_id = ?",
        args: [telegramId]
      });
      
      if (userRes.rows.length === 0 && process.env.TELEGRAM_USER_ID === telegramId) {
         userRes = await db.execute({
           sql: "SELECT id, initial_balance, prop_firm_enabled, prop_firm_balance, prop_firm_daily_dd, target_balance, compound_risk FROM users WHERE telegram_id = 'PLACEHOLDER_TELEGRAM_ID' OR username = 'jal'"
         });
      }
      
      if (userRes.rows.length === 0) {
        await ctx.reply('❌ Akun belum terhubung. Gunakan /link');
        return;
      }
      
      const userData = userRes.rows[0];
      const actualUserId = userData.id;
      const isProp = userData.prop_firm_enabled;
      const targetBalance = userData.target_balance || 1000000;
      const compoundRisk = userData.compound_risk || 2.5;
      const dailyDDPct = userData.prop_firm_daily_dd || 5;
      
      // Get all non-pending trades
      const tradesRes = await db.execute({
        sql: "SELECT realized_pl, result, created_at FROM trades WHERE user_id = ? AND result != 'Pending' ORDER BY created_at ASC",
        args: [actualUserId]
      });
      
      const allTrades = tradesRes.rows;
      const txRes = await db.execute({
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
      });
      
      let filteredTrades: any[] = [];
      const now = new Date();
      let label = "";
      
      if (timeframe === 'dailydd') {
         const dailyDDAmount = peakEquity * (dailyDDPct / 100);
         const dailyDDViolationPoint = peakEquity - dailyDDAmount;
         const dailyDDRemaining = currentEquity - dailyDDViolationPoint;
         
         let msg = `🛡️ <b>TRAILING DAILY DRAWDOWN</b>\n<i>(Limit ${dailyDDPct}% dari High Watermark)</i>\n━━━━━━━━━━━━━━━━━━━\n`;
         msg += `High Watermark: <b>$${peakEquity.toFixed(2)}</b>\n`;
         msg += `Max Daily Loss: $${dailyDDAmount.toFixed(2)}\n`;
         msg += `Violation Point: $${dailyDDViolationPoint.toFixed(2)}\n\n`;
         msg += `Current Equity: <b>$${currentEquity.toFixed(2)}</b>\n`;
         if (dailyDDRemaining <= 0) {
            msg += `❌ <b>Sisa Limit: $0.00 (VIOLATED)</b>`;
         } else {
            msg += `✅ <b>Sisa Limit: $${dailyDDRemaining.toFixed(2)}</b>`;
         }
         await sendOrEdit(ctx, msg, true);
         return;
      } else if (timeframe === 'monthlydd') {
         const monthlyDDAmount = peakEquity * 0.50; // 50%
         const monthlyDDViolationPoint = peakEquity - monthlyDDAmount;
         const monthlyDDRemaining = currentEquity - monthlyDDViolationPoint;
         
         let msg = `🛡️ <b>TRAILING MONTHLY DRAWDOWN</b>\n<i>(Limit 50% dari High Watermark)</i>\n━━━━━━━━━━━━━━━━━━━\n`;
         msg += `High Watermark: <b>$${peakEquity.toFixed(2)}</b>\n`;
         msg += `Max Monthly Loss: $${monthlyDDAmount.toFixed(2)}\n`;
         msg += `Violation Point: $${monthlyDDViolationPoint.toFixed(2)}\n\n`;
         msg += `Current Equity: <b>$${currentEquity.toFixed(2)}</b>\n`;
         if (monthlyDDRemaining <= 0) {
            msg += `❌ <b>Sisa Limit: $0.00 (VIOLATED)</b>`;
         } else {
            msg += `✅ <b>Sisa Limit: $${monthlyDDRemaining.toFixed(2)}</b>`;
         }
         await sendOrEdit(ctx, msg, true);
         return;
      } else if (timeframe === 'today') {
        label = "HARI INI";
        const todayStr = now.toISOString().split('T')[0];
        filteredTrades = allTrades.filter((t: any) => {
           let d = t.created_at;
           if (!d.includes('Z')) d += 'Z';
           return new Date(d).toISOString().split('T')[0] === todayStr;
        });
      } else if (timeframe === 'weekly') {
        label = "7 HARI TERAKHIR";
        const sevenDaysAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
        filteredTrades = allTrades.filter((t: any) => {
           let d = t.created_at;
           if (!d.includes('Z')) d += 'Z';
           return new Date(d) >= sevenDaysAgo;
        });
      } else if (timeframe === 'monthly') {
        label = "BULAN INI";
        const currentMonth = now.getMonth();
        const currentYear = now.getFullYear();
        filteredTrades = allTrades.filter((t: any) => {
           let d = t.created_at;
           if (!d.includes('Z')) d += 'Z';
           const tDate = new Date(d);
           return tDate.getMonth() === currentMonth && tDate.getFullYear() === currentYear;
        });
      } else if (timeframe === 'compound') {
        try {
          // 1. SAFE GUARD DATA & NULL CHECK
          let safeBalance = currentEquity && currentEquity > 0 ? currentEquity : 1000;
          let safeTarget = targetBalance && targetBalance > 0 ? targetBalance : 1000000;

          // Cegah division by zero
          if (safeTarget <= 0) safeTarget = 1000000;

          const sisaTarget = safeTarget - safeBalance;
          
          // 2. PENANGANAN MATH LOGIC COMPOUNDING
          const rawProgress = (safeBalance / safeTarget) * 100;
          const progressPercent = Math.min(100, Math.max(0, rawProgress));
          const progressPercentStr = progressPercent.toFixed(1);
          
          // Buat Progress Bar 10 blok
          const filledBlocks = Math.floor(progressPercent / 10);
          const emptyBlocks = 10 - filledBlocks;
          const progressBar = '🟩'.repeat(filledBlocks) + '⬜'.repeat(emptyBlocks);
          
          let estimasiHari = 0;
          if (safeTarget > safeBalance) {
              estimasiHari = Math.ceil(Math.log(safeTarget / safeBalance) / Math.log(1.05));
          }

          let msg = `📈 <b>COMPOUNDING PROGRESS & PLAN</b>\n━━━━━━━━━━━━━━━━━━━\n`;
          msg += `💰 <b>Balance Saat Ini:</b> ${safeBalance.toLocaleString('en-US', {minimumFractionDigits:0, maximumFractionDigits:2})} USC\n`;
          msg += `🎯 <b>Target Akhir:</b> ${safeTarget.toLocaleString('en-US', {minimumFractionDigits:0, maximumFractionDigits:2})} USC\n`;
          msg += `📊 <b>Progres Total:</b> [${progressBar}] ${progressPercentStr}%\n`;
          msg += `🚀 <b>Sisa Target:</b> ${sisaTarget > 0 ? sisaTarget.toLocaleString('en-US', {minimumFractionDigits:0, maximumFractionDigits:2}) : 0} USC\n`;
          msg += `⏳ <b>Estimasi Sisa:</b> ~${estimasiHari} Hari Trading\n\n`;
          msg += `🗓️ <b>Proyeksi Target 10 Hari Ke Depan (Net 5%/Hari):</b>\n`;

          let projEquity = safeBalance;
          for (let i = 1; i <= 10; i++) {
             // Loop 10 hari ke depan
             projEquity = projEquity * 1.05;
             let risk = projEquity * (compoundRisk / 100); // Dynamic risk
             let lot = Math.max(0.01, risk / 300); // SL 30 pips
             
             msg += `• <b>Hari ${i}:</b> Balance ${projEquity.toLocaleString('en-US', {minimumFractionDigits:0, maximumFractionDigits:2})} USC | Lot: ${lot.toFixed(2)} | Risk: ${risk.toLocaleString('en-US', {minimumFractionDigits:0, maximumFractionDigits:2})} USC\n`;
          }
          
          msg += `━━━━━━━━━━━━━━━━━━━\n<i>*Gunakan command \`/settarget [jumlah]\` untuk mengubah target.</i>`;
          await sendOrEdit(ctx, msg, true);
          return;
        } catch (err) {
          console.error(err);
          await ctx.reply('❌ Gagal memuat data compounding.');
          return;
        }
      }
      
      let totalPL = 0;
      let wins = 0;
      
      filteredTrades.forEach((t: any) => {
         totalPL += (t.realized_pl || 0);
         if (t.result && t.result.toLowerCase() === 'win') wins++;
      });
      
      const winRate = filteredTrades.length > 0 ? ((wins / filteredTrades.length) * 100).toFixed(1) : '0.0';
      const signPL = totalPL >= 0 ? '+' : '';
      
      const msg = `📊 <b>RINGKASAN ${label}</b>\n` +
                  `━━━━━━━━━━━━━━━━━━━\n` +
                  `- Total Trades: ${filteredTrades.length}\n` +
                  `- Win Rate: ${winRate}%\n` +
                  `- Net P/L: ${signPL}$${totalPL.toFixed(2)}`;
                  
      await sendOrEdit(ctx, msg, true);
    } catch (e) {
      console.error(e);
      await sendOrEdit(ctx, 'Terjadi kesalahan.', true);
    }
  };

  bot.command('today', async (ctx) => getStatsByTimeframe(ctx, 'today'));
  bot.command('weekly', async (ctx) => getStatsByTimeframe(ctx, 'weekly'));
  bot.command('monthly', async (ctx) => getStatsByTimeframe(ctx, 'monthly'));
  bot.command('compound', async (ctx) => getStatsByTimeframe(ctx, 'compound'));
  bot.command('dailydd', async (ctx) => getStatsByTimeframe(ctx, 'dailydd'));
  bot.command('monthlydd', async (ctx) => getStatsByTimeframe(ctx, 'monthlydd'));

  const getLotRecommendation = async (ctx: any, customPips?: number) => {
    try {
      const telegramId = ctx.from?.id?.toString();
      if (!telegramId) return;

      let userRes = await db.execute({
        sql: "SELECT id, initial_balance, prop_firm_enabled, prop_firm_balance FROM users WHERE telegram_id = ?",
        args: [telegramId]
      });
      
      if (userRes.rows.length === 0 && process.env.TELEGRAM_USER_ID === telegramId) {
         userRes = await db.execute({
           sql: "SELECT id, initial_balance, prop_firm_enabled, prop_firm_balance FROM users WHERE telegram_id = 'PLACEHOLDER_TELEGRAM_ID' OR username = 'jal'"
         });
      }
      
      if (userRes.rows.length === 0) {
        await ctx.reply('❌ Akun belum terhubung. Gunakan /link');
        return;
      }
      
      const userData = userRes.rows[0];
      const actualUserId = userData.id;
      const isProp = userData.prop_firm_enabled;
      const targetBalance = userData.target_balance || 1000000;
      const compoundRisk = userData.compound_risk || 2.5;
      const initialBal = isProp ? (userData.prop_firm_balance || 1000) : (userData.initial_balance || 1000);

      const tradesRes = await db.execute({
        sql: "SELECT realized_pl FROM trades WHERE user_id = ? AND result != 'Pending'",
        args: [actualUserId]
      });

      let totalPastPL = 0;
      tradesRes.rows.forEach((t: any) => totalPastPL += (t.realized_pl || 0));
      const currentEquity = initialBal + totalPastPL;

      const riskPct = 0.025; // 2.5%
      const nominalRisk = currentEquity * riskPct;

      if (customPips && !isNaN(customPips)) {
         const lotSize = nominalRisk / (customPips * 10);
         let msg = `🧮 <b>KALKULATOR LOT (XAUUSD)</b>\n━━━━━━━━━━━━━━━━━━━\n`;
         msg += `Current Equity: <b>$${currentEquity.toFixed(2)}</b>\n`;
         msg += `Risk Amount (2.5%): <b>$${nominalRisk.toFixed(2)}</b>\n\n`;
         msg += `🎯 <b>Stop Loss: ${customPips} pips</b>\n`;
         msg += `👉 Rekomendasi Lot: <b>${lotSize.toFixed(2)} Lot</b>\n`;
         await sendOrEdit(ctx, msg, true);
         return;
      }

      const defaultPips = [15, 20, 25, 30, 35, 40, 50];
      let msg = `🧮 <b>MATRIKS LOT (XAUUSD)</b>\n<i>(Berdasarkan Risk 2.5%)</i>\n━━━━━━━━━━━━━━━━━━━\n`;
      msg += `Current Equity: <b>$${currentEquity.toFixed(2)}</b>\n`;
      msg += `Risk Amount: <b>$${nominalRisk.toFixed(2)}</b>\n\n`;
      msg += `📏 <b>Rekomendasi Berdasarkan SL:</b>\n`;
      
      defaultPips.forEach(pips => {
         const lotSize = nominalRisk / (pips * 10);
         msg += `• SL <b>${pips}</b> pips ➡️ <b>${lotSize.toFixed(2)}</b> Lot\n`;
      });

      msg += `\n<i>Gunakan /lot [pips] untuk hitung custom (contoh: /lot 18)</i>`;
      await sendOrEdit(ctx, msg, true);
    } catch (e) {
      console.error(e);
      await sendOrEdit(ctx, 'Terjadi kesalahan saat menghitung lot.', true);
    }
  };

  bot.command('lot', async (ctx) => {
    const args = ctx.message.text.split(' ').slice(1);
    const pips = args.length > 0 ? parseFloat(args[0]) : undefined;
    await getLotRecommendation(ctx, pips);
  });

  const renderMenu = async (ctx: any) => {
    const msg = `🏛️ <b>JOURNAL TRADING DASHBOARD</b>\n━━━━━━━━━━━━━━━━━━━\n<i>Pilih menu di bawah untuk statistik & alat trading:</i>\n\n💡 <b>Perintah Tambahan:</b>\n• /settarget [angka] - Set target (USC)\n• /setrisk [persen] - Set % risk compound (cth: 2.5)\n• /report - Export jurnal (CSV)\n• /deposit [jml] - Catat Deposit\n• /withdraw [jml] - Catat Withdraw\n• /news - Kalender Ekonomi (USD)`;
    const keyboard = Markup.inlineKeyboard([
      [Markup.button.callback('📊 Today', 'cmd_today'), Markup.button.callback('🗓️ Weekly', 'cmd_weekly')],
      [Markup.button.callback('📅 Monthly', 'cmd_monthly'), Markup.button.callback('📈 Compound', 'cmd_compound')],
      [Markup.button.callback('🛡️ Daily DD', 'cmd_dailydd'), Markup.button.callback('🛡️ Monthly DD', 'cmd_monthlydd')],
      [Markup.button.callback('🧮 Lot Calculator', 'cmd_lot'), Markup.button.callback('💰 Balance', 'cmd_balance')],
      [Markup.button.callback('↩️ Undo Trade', 'cmd_undo'), Markup.button.callback('⚡ Help / Start', 'cmd_start')]
    ]);
    
    if (ctx.callbackQuery) {
      await ctx.editMessageText(msg, { parse_mode: 'HTML', ...keyboard }).catch(() => {});
    } else {
      await ctx.reply(msg, { parse_mode: 'HTML', ...keyboard });
    }
  };

  bot.command('menu', renderMenu);
  
  bot.command('setrisk', async (ctx) => {
    try {
      const text = ctx.message.text.split(' ');
      if (text.length < 2) {
        return ctx.reply('❌ Format salah.\nContoh: /setrisk 2.5');
      }
      
      const risk = parseFloat(text[1]);
      if (isNaN(risk) || risk <= 0 || risk > 100) {
        return ctx.reply('❌ Angka risk tidak valid (harus 0.1 - 100).');
      }
      
      const telegramId = ctx.from?.id?.toString();
      let userRes = await db.execute({
        sql: "SELECT id FROM users WHERE telegram_id = ?",
        args: [telegramId]
      });
      
      if (userRes.rows.length === 0 && process.env.TELEGRAM_USER_ID === telegramId) {
         userRes = await db.execute({
           sql: "SELECT id FROM users WHERE telegram_id = 'PLACEHOLDER_TELEGRAM_ID' OR username = 'jal'"
         });
      }
      
      if (userRes.rows.length === 0) {
        return ctx.reply('❌ Akun belum terhubung. Gunakan /link');
      }
      
      const actualUserId = userRes.rows[0].id;
      
      await db.execute({
        sql: "UPDATE users SET compound_risk = ? WHERE id = ?",
        args: [risk, actualUserId]
      });
      
      await ctx.reply(`✅ <b>RISK COMPOUNDING DIPERBARUI</b>\n━━━━━━━━━━━━━━━━━━━\nRisk baru: <b>${risk}%</b> per hari.\nProyeksi compounding sekarang akan menggunakan angka ini.`, { parse_mode: 'HTML' });
      
    } catch (e) {
      console.error(e);
      await ctx.reply('Terjadi kesalahan.');
    }
  });

  bot.command('report', async (ctx) => {
    try {
      const telegramId = ctx.from?.id?.toString();
      let userRes = await db.execute({
        sql: "SELECT id FROM users WHERE telegram_id = ?",
        args: [telegramId]
      });
      
      if (userRes.rows.length === 0 && process.env.TELEGRAM_USER_ID === telegramId) {
         userRes = await db.execute({
           sql: "SELECT id FROM users WHERE telegram_id = 'PLACEHOLDER_TELEGRAM_ID' OR username = 'jal'"
         });
      }
      
      if (userRes.rows.length === 0) {
        return ctx.reply('❌ Akun belum terhubung. Gunakan /link');
      }
      
      const actualUserId = userRes.rows[0].id;
      
      const tradesRes = await db.execute({
        sql: "SELECT * FROM trades WHERE user_id = ? ORDER BY created_at DESC",
        args: [actualUserId]
      });
      
      const trades = tradesRes.rows;
      if (trades.length === 0) {
        return ctx.reply('❌ Belum ada trade yang dicatat.');
      }
      
      // Build CSV
      let csv = 'ID,Pair,Direction,Setup,Entry,SL,TP,Result,Realized_PL,Checklist,Notes,Date\n';
      trades.forEach((t) => {
        const row = [
          t.id,
          t.pair || '',
          t.direction || '',
          t.setup_name || '',
          t.entry_price || '',
          t.sl || '',
          t.tp || '',
          t.result || '',
          t.realized_pl || 0,
          `"${(t.checklist || '').replace(/"/g, '""')}"`,
          `"${(t.notes || '').replace(/"/g, '""')}"`,
          t.created_at || ''
        ];
        csv += row.join(',') + '\n';
      });
      
      const buffer = Buffer.from(csv, 'utf8');
      
      await ctx.replyWithDocument(
        { source: buffer, filename: 'Trading_Journal_Report.csv' },
        { caption: `✅ Laporan Jurnal Trading\nTotal: ${trades.length} trades` }
      );
      
    } catch (e) {
      console.error(e);
      await ctx.reply('❌ Gagal menghasilkan laporan.');
    }
  });


  bot.command('news', async (ctx) => {
    try {
      await ctx.reply('⏳ Mengambil data Kalender Ekonomi...');
      const res = await fetch('https://nfs.faireconomy.media/ff_calendar_thisweek.json');
      const data = await res.json();
      
      const highImpact = data.filter((item: any) => 
        item.country === 'USD' && item.impact === 'High'
      );
      
      const now = new Date();
      // To get current month and year in Asia/Jakarta
      const formatterMonth = new Intl.DateTimeFormat('id-ID', { timeZone: 'Asia/Jakarta', month: 'long', year: 'numeric' });
      const currentMonthYear = formatterMonth.format(now);
      
      if (highImpact.length === 0) {
        return ctx.reply(`📅 Jadwal High-Impact USD News (${currentMonthYear})\n───────────────────────────\n\nTidak ada High Impact News (USD) untuk minggu ini.`);
      }

      let msg = `📅 Jadwal High-Impact USD News (${currentMonthYear})\n───────────────────────────\n`;

      highImpact.forEach((item: any) => {
         const eventTime = new Date(item.date);
         
         // Formatting 07 Aug
         const dayFormatter = new Intl.DateTimeFormat('en-GB', { timeZone: 'Asia/Jakarta', day: '2-digit', month: 'short' });
         const dayStr = dayFormatter.format(eventTime); // "28 Aug"
         
         // Formatting 19:30 WIB
         const timeFormatter = new Intl.DateTimeFormat('id-ID', { timeZone: 'Asia/Jakarta', hour: '2-digit', minute: '2-digit', hour12: false });
         const timeStr = timeFormatter.format(eventTime).replace('.', ':');
         
         // Status indicator
         const isPast = eventTime.getTime() < now.getTime();
         const icon = isPast ? '✅' : '⏳';
         
         msg += `${icon} ${dayStr} | ${timeStr} WIB - ${item.title}\n`;
      });
      
      msg += `\n⚠️ Perhatian: Hindari entry M5 pada zona waktu ⏳!`;
      
      await ctx.reply(msg, { parse_mode: 'HTML' });
      
    } catch (e) {
      console.error(e);
      await ctx.reply('❌ Gagal mengambil data berita ekonomi.');
    }
  });

  bot.command('deposit', async (ctx) => {
    try {
      const text = ctx.message.text.split(' ');
      if (text.length < 2) return ctx.reply('❌ Format: /deposit [jumlah]');
      const amount = parseFloat(text[1]);
      if (isNaN(amount) || amount <= 0) return ctx.reply('❌ Jumlah tidak valid.');
      
      const telegramId = ctx.from?.id?.toString();
      let userRes = await db.execute({
        sql: "SELECT id FROM users WHERE telegram_id = ?",
        args: [telegramId]
      });
      if (userRes.rows.length === 0) {
        userRes = await db.execute({
          sql: "SELECT id FROM users WHERE telegram_id = 'PLACEHOLDER_TELEGRAM_ID' OR username = 'jal'"
        });
      }
      if (userRes.rows.length === 0) return ctx.reply('❌ Akun belum terhubung.');
      
      const actualUserId = userRes.rows[0].id;
      await db.execute({
        sql: "INSERT INTO transactions (user_id, type, amount) VALUES (?, 'deposit', ?)",
        args: [actualUserId, amount]
      });
      
      await ctx.reply(`✅ <b>DEPOSIT BERHASIL</b>\n━━━━━━━━━━━━━━━━━━━\n💰 Jumlah: +$${amount.toFixed(2)}\n<i>Data telah tersinkronisasi dengan Web Dashboard.</i>`, { parse_mode: 'HTML' });
    } catch (e) {
      console.error(e);
      await ctx.reply('❌ Terjadi kesalahan.');
    }
  });

  bot.command('withdraw', async (ctx) => {
    try {
      const text = ctx.message.text.split(' ');
      if (text.length < 2) return ctx.reply('❌ Format: /withdraw [jumlah]');
      const amount = parseFloat(text[1]);
      if (isNaN(amount) || amount <= 0) return ctx.reply('❌ Jumlah tidak valid.');
      
      const telegramId = ctx.from?.id?.toString();
      let userRes = await db.execute({
        sql: "SELECT id FROM users WHERE telegram_id = ?",
        args: [telegramId]
      });
      if (userRes.rows.length === 0) {
        userRes = await db.execute({
          sql: "SELECT id FROM users WHERE telegram_id = 'PLACEHOLDER_TELEGRAM_ID' OR username = 'jal'"
        });
      }
      if (userRes.rows.length === 0) return ctx.reply('❌ Akun belum terhubung.');
      
      const actualUserId = userRes.rows[0].id;
      await db.execute({
        sql: "INSERT INTO transactions (user_id, type, amount) VALUES (?, 'withdrawal', ?)",
        args: [actualUserId, amount]
      });
      
      await ctx.reply(`✅ <b>WITHDRAWAL BERHASIL</b>\n━━━━━━━━━━━━━━━━━━━\n💸 Jumlah: -$${amount.toFixed(2)}\n<i>Data telah tersinkronisasi dengan Web Dashboard.</i>`, { parse_mode: 'HTML' });
    } catch (e) {
      console.error(e);
      await ctx.reply('❌ Terjadi kesalahan.');
    }
  });

  bot.command('settarget', async (ctx) => {
    try {
      const text = ctx.message.text.split(' ');
      if (text.length < 2) {
        return ctx.reply('❌ Format salah.\nContoh: /settarget 1000000');
      }
      
      const target = parseFloat(text[1]);
      if (isNaN(target) || target <= 0) {
        return ctx.reply('❌ Angka target tidak valid.');
      }
      
      const telegramId = ctx.from?.id?.toString();
      let userRes = await db.execute({
        sql: "SELECT id FROM users WHERE telegram_id = ?",
        args: [telegramId]
      });
      
      if (userRes.rows.length === 0 && process.env.TELEGRAM_USER_ID === telegramId) {
         userRes = await db.execute({
           sql: "SELECT id FROM users WHERE telegram_id = 'PLACEHOLDER_TELEGRAM_ID' OR username = 'jal'"
         });
      }
      
      if (userRes.rows.length === 0) {
        return ctx.reply('❌ Akun belum terhubung. Gunakan /link');
      }
      
      const actualUserId = userRes.rows[0].id;
      
      await db.execute({
        sql: "UPDATE users SET target_balance = ? WHERE id = ?",
        args: [target, actualUserId]
      });
      
      const usdEquiv = target / 100;
      let msg = `🎯 <b>TARGET BALANCED DIPERBARUI!</b>\n━━━━━━━━━━━━━━━━━━━\n`;
      msg += `Target Baru: ${target.toLocaleString('en-US')} USC ($${usdEquiv.toLocaleString('en-US')} USD)\n`;
      msg += `<i>*Semua kalkulasi proyeksi compounding otomatis menggunakan acuan ini.</i>`;
      
      await ctx.reply(msg, { parse_mode: 'HTML' });
      
    } catch (e) {
      console.error(e);
      await ctx.reply('Terjadi kesalahan.');
    }
  });

  bot.action('cmd_menu', async (ctx) => { await ctx.answerCbQuery().catch(()=>{}); await renderMenu(ctx); });

  bot.action('cmd_today', async (ctx) => { await ctx.answerCbQuery().catch(()=>{}); await getStatsByTimeframe(ctx, 'today'); });
  bot.action('cmd_weekly', async (ctx) => { await ctx.answerCbQuery().catch(()=>{}); await getStatsByTimeframe(ctx, 'weekly'); });
  bot.action('cmd_monthly', async (ctx) => { await ctx.answerCbQuery().catch(()=>{}); await getStatsByTimeframe(ctx, 'monthly'); });
  bot.action('cmd_compound', async (ctx) => { await ctx.answerCbQuery().catch(()=>{}); await getStatsByTimeframe(ctx, 'compound'); });
  bot.action('cmd_dailydd', async (ctx) => { await ctx.answerCbQuery().catch(()=>{}); await getStatsByTimeframe(ctx, 'dailydd'); });
  bot.action('cmd_monthlydd', async (ctx) => { await ctx.answerCbQuery().catch(()=>{}); await getStatsByTimeframe(ctx, 'monthlydd'); });
  bot.action('cmd_lot', async (ctx) => { await ctx.answerCbQuery().catch(()=>{}); await getLotRecommendation(ctx); });
  bot.action('cmd_balance', async (ctx) => { await ctx.answerCbQuery().catch(()=>{}); await getStatsBalance(ctx); });
  bot.action('cmd_undo', async (ctx) => { await ctx.answerCbQuery().catch(()=>{}); await handleUndo(ctx); });
  bot.action('cmd_start', async (ctx) => { await ctx.answerCbQuery().catch(()=>{}); await handleStart(ctx); });


  // Undo command
  const handleUndo = async (ctx: any) => {
    try {
      const telegramId = ctx.from?.id?.toString();
      let userRes = await db.execute({
        sql: "SELECT id FROM users WHERE telegram_id = ?",
        args: [telegramId]
      });
      
      if (userRes.rows.length === 0 && process.env.TELEGRAM_USER_ID === telegramId) {
         userRes = await db.execute({
           sql: "SELECT id FROM users WHERE telegram_id = 'PLACEHOLDER_TELEGRAM_ID' OR username = 'jal'"
         });
      }
      
      if (userRes.rows.length === 0) {
        await ctx.reply('❌ Akun belum terhubung.');
        return;
      }
      
      const actualUserId = userRes.rows[0].id;
      
      // Get the last trade
      const lastTradeRes = await db.execute({
        sql: "SELECT id FROM trades WHERE user_id = ? ORDER BY id DESC LIMIT 1",
        args: [actualUserId]
      });
      
      if (lastTradeRes.rows.length === 0) {
        await sendOrEdit(ctx, 'Tidak ada trade untuk dihapus.', true);
        return;
      }
      
      const lastTrade = lastTradeRes.rows[0];
      
      // Delete the trade
      await db.execute({
        sql: "DELETE FROM trades WHERE id = ?",
        args: [lastTrade.id]
      });
      
      await sendOrEdit(ctx, '🗑️ Trade terakhir berhasil dihapus dari jurnal!', true);
      
    } catch (e) {
      console.error(e);
      await sendOrEdit(ctx, 'Terjadi kesalahan saat menghapus trade.', true);
    }
  };
  bot.command('undo', handleUndo);

  
  // Linking command
  bot.command('link', async (ctx) => {
    const parts = ctx.message.text.split(' ');
    const email = parts[1];
    
    if (!email) {
      await ctx.reply('Format salah. Gunakan: /link emailkamu@gmail.com');
      return;
    }
    
    try {
      const res = await db.execute({
        sql: "SELECT id FROM users WHERE username = ?",
        args: [email]
      });
      
      if (res.rows.length === 0) {
        await ctx.reply('Email tidak ditemukan di database Web.');
        return;
      }
      
      const userId = res.rows[0].id;
      const telId = ctx.from?.id?.toString();
      
      await db.execute({
        sql: "UPDATE users SET telegram_id = ? WHERE id = ?",
        args: [telId, userId]
      });
      
      await ctx.reply(`✅ Berhasil! Akun Telegram (ID: ${telId}) telah ditautkan ke akun Web (${email}).`);
    } catch (e) {
      console.error(e);
      await ctx.reply('Terjadi kesalahan saat menghubungkan akun.');
    }
  });

  // Handle messages with photos (for trading journal)
  
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

      const tvRegex = /(https?:\/\/(?:www\.)?tradingview\.com\/x\/[\w-]+\/?)/i;
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
          let msg = `✅ TRADE LOGGED SUCCESSFULLY (CSV)\n----------------------------------\n` +
                    `📊 Pair: ${pair} (${type.toUpperCase()})\n` +
                    `💰 P/L Realized: ${sign}${realizedPl} (${status.toUpperCase()})\n`;
          if (tvUrl) {
            msg += `🖼️ Chart: ${tvUrl}\n`;
          }
          
          await ctx.reply(msg, { link_preview_options: { is_disabled: false } });
          return;
        } else {
          await ctx.reply(`⚠️ Format CSV tidak valid atau gagal dibaca.\nJumlah kolom: ${parts.length} (Dibutuhkan minimal 11).\nKolom Direction (BUY/SELL): ${parts[3] ? parts[3].toUpperCase() : 'Kosong'}\n\nPastikan mengikuti format:\nDate, Time, Pair, Direction, Setup, Entry, SL, TP, Size, Result, PL, Emotion, Notes`);
        }
      } else {
        await ctx.reply(`⚠️ Pesan tidak mengandung koma. Harap kirim dalam format CSV:\nDate, Time, Pair, Direction, Setup, Entry, SL, TP, Size, Result, PL, Emotion, Notes`);
      }
    } catch (e) {
      console.error("Text parsing error:", e);
      await ctx.reply('❌ Terjadi kesalahan saat memproses data CSV.');
    }
  });

  bot.on(message('photo'), async (ctx) => {
    try {
      const caption = (ctx.message as any).caption;
      if (!caption) {
        // No caption, maybe just a photo
        return;
      }

      const tradeData = parseTradeData(caption);
      if (!tradeData) {
        await ctx.reply('⚠️ Format CSV gagal dibaca. Pastikan formatnya benar:\nDate, Time, Pair, Direction, Setup, Entry, SL, TP, Size, Result, PL, Emotion, Notes');
        return;
      }
      
      // Attempt to resolve user
      const telegramId = ctx.from?.id?.toString();
      const expectedEnvTelegramId = process.env.TELEGRAM_USER_ID;
      
      let userRes = await db.execute({
        sql: "SELECT id, current_mode, prop_firm_enabled, prop_firm_balance, initial_balance, balance FROM users WHERE telegram_id = ?",
        args: [telegramId]
      });
      
      // If not linked by /link, fallback to ENV linking if they match
      if (userRes.rows.length === 0 && expectedEnvTelegramId === telegramId) {
         userRes = await db.execute({
           sql: "SELECT id, current_mode, prop_firm_enabled, prop_firm_balance, initial_balance, balance FROM users WHERE telegram_id = 'PLACEHOLDER_TELEGRAM_ID' OR username = 'singgahrang@gmail.com'"
         });
         
         if (userRes.rows.length > 0) {
           // Auto-update to correct ID
           await db.execute({
             sql: "UPDATE users SET telegram_id = ? WHERE id = ?",
             args: [telegramId, userRes.rows[0].id]
           });
         }
      }
      
      if (userRes.rows.length === 0) {
        await ctx.reply('❌ Akun Telegram kamu belum terhubung dengan akun Web. Gunakan `/link emailmu@gmail.com` terlebih dahulu.');
        return;
      }
      
      const userData = userRes.rows[0];
      const actualUserId = userData.id;
      const isProp = userData.prop_firm_enabled;
      const targetBalance = userData.target_balance || 1000000;
      const compoundRisk = userData.compound_risk || 2.5;
      
      // Get all existing trades to calculate pure equity
      const existingTrades = await db.execute({
        sql: "SELECT realized_pl FROM trades WHERE user_id = ?",
        args: [actualUserId]
      });
      const totalPastPL = existingTrades.rows.reduce((acc, t: any) => acc + (t.realized_pl || 0), 0);
      
      const initialBal = isProp ? (userData.prop_firm_balance || 1000) : (userData.initial_balance || 1000);
      const oldBalance = initialBal + totalPastPL;
      const newBalance = oldBalance + tradeData.pl;
      // Note: We DO NOT update initial_balance in DB. We let it stay purely 1000.

      // Get highest resolution photo URL
      const fileId = ctx.message.photo[ctx.message.photo.length - 1].file_id;
      const fileLink = await ctx.telegram.getFileLink(fileId);
      const imageUrl = fileLink.href;

      let created_at = new Date().toISOString();
      if (tradeData.dateStr) {
        const testDate = new Date(tradeData.dateStr);
        if (!isNaN(testDate.getTime())) {
          created_at = tradeData.dateStr; 
        }
      }

      let mode = userData.current_mode || 'backtest';

      await db.execute({
        sql: `INSERT INTO trades (
          user_id, pair, direction, setup_name, entry_price, sl, tp, 
          account_balance, risk_percentage, position_size, nominal_risk, 
          anxiety_level, notes, result, realized_pl, image, run_mode, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
        args: [
          actualUserId, tradeData.pair, tradeData.direction, tradeData.setup_name, tradeData.entry, tradeData.sl, tradeData.tp,
          newBalance, 0, tradeData.size, 0,
          tradeData.emotionScore, tradeData.notes, tradeData.result, tradeData.pl, imageUrl, mode, created_at
        ]
      });

      const sign = tradeData.pl >= 0 ? '+' : '';
      const msg = `✅ <b>TRADE LOGGED SUCCESSFULLY</b>
` +
                  `━━━━━━━━━━━━━━━━━━━
` +
                  `📊 <b>Pair:</b> ${tradeData.pair} (${tradeData.direction.toUpperCase()})
` +
                  `🎯 <b>Setup:</b> ${tradeData.setup_name}
` +
                  `💵 <b>P/L Realized:</b> ${sign}$${tradeData.pl.toFixed(2)} (${tradeData.result.toUpperCase()})
` +
                  `📈 <b>New Equity:</b> $${newBalance.toFixed(2)}

` +
                  `<i>Data berhasil disinkronkan ke Web Dashboard!</i>`;
      await sendOrEdit(ctx, msg, true);
      
    } catch (e) {
      console.error("Telegram bot error:", e);
      await ctx.reply('Terjadi kesalahan saat memproses jurnalmu.');
    }
  });

  bot.catch((err: any, ctx: any) => {
    console.error(`Ooops, encountered an error for ${ctx.updateType}`, err);
  });

  // bot.launch(); // Moved to server.ts
  
  
  
  return bot;
}
