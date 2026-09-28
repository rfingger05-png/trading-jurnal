import re

with open('src/lib/telegram.ts', 'r') as f:
    content = f.read()

# 1. Add Markup to import
content = content.replace("import { Telegraf } from 'telegraf';", "import { Telegraf, Markup } from 'telegraf';")

# 2. Update setMyCommands
find_menu = """  bot.telegram.setMyCommands([
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

replace_menu = """  bot.telegram.setMyCommands([
    { command: 'menu', description: 'Menampilkan menu utama & tombol navigasi' },
    { command: 'lot', description: 'Kalkulator lot otomatis (Risk 2.5%)' },
    { command: 'today', description: 'Statistik & P/L hari ini' },
    { command: 'weekly', description: 'Statistik & P/L mingguan' },
    { command: 'monthly', description: 'Statistik & P/L bulanan' },
    { command: 'compound', description: 'Milestone target 10 hari (Compound 5%)' },
    { command: 'dailydd', description: 'Cek sisa batas Trailing Daily Drawdown (5%)' },
    { command: 'monthlydd', description: 'Cek batas Trailing Monthly Drawdown (50%)' },
    { command: 'undo', description: 'Hapus trade terakhir' }
  ]).catch(console.error);"""
content = content.replace(find_menu, replace_menu)

# 3. Add getLotRecommendation and menu handlers
find_commands = """  bot.command('today', async (ctx) => getStatsByTimeframe(ctx, 'today'));
  bot.command('weekly', async (ctx) => getStatsByTimeframe(ctx, 'weekly'));
  bot.command('monthly', async (ctx) => getStatsByTimeframe(ctx, 'monthly'));
  bot.command('compound', async (ctx) => getStatsByTimeframe(ctx, 'compound'));
  bot.command('dailydd', async (ctx) => getStatsByTimeframe(ctx, 'dailydd'));
  bot.command('monthlydd', async (ctx) => getStatsByTimeframe(ctx, 'monthlydd'));"""

replace_commands = """  bot.command('today', async (ctx) => getStatsByTimeframe(ctx, 'today'));
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
           sql: "SELECT id, initial_balance, prop_firm_enabled, prop_firm_balance FROM users WHERE telegram_id = 'PLACEHOLDER_TELEGRAM_ID' OR username = 'singgahrang@gmail.com'"
         });
      }
      
      if (userRes.rows.length === 0) {
        await ctx.reply('❌ Akun belum terhubung. Gunakan /link');
        return;
      }
      
      const userData = userRes.rows[0];
      const actualUserId = userData.id;
      const isProp = userData.prop_firm_enabled;
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
         let msg = `🧮 <b>KALKULATOR LOT (XAUUSD)</b>\\n━━━━━━━━━━━━━━━━━━━\\n`;
         msg += `Current Equity: <b>$${currentEquity.toFixed(2)}</b>\\n`;
         msg += `Risk Amount (2.5%): <b>$${nominalRisk.toFixed(2)}</b>\\n\\n`;
         msg += `🎯 <b>Stop Loss: ${customPips} pips</b>\\n`;
         msg += `👉 Rekomendasi Lot: <b>${lotSize.toFixed(2)} Lot</b>\\n`;
         await ctx.reply(msg, { parse_mode: 'HTML' });
         return;
      }

      const defaultPips = [15, 20, 25, 30, 35, 40, 50];
      let msg = `🧮 <b>MATRIKS LOT (XAUUSD)</b>\\n<i>(Berdasarkan Risk 2.5%)</i>\\n━━━━━━━━━━━━━━━━━━━\\n`;
      msg += `Current Equity: <b>$${currentEquity.toFixed(2)}</b>\\n`;
      msg += `Risk Amount: <b>$${nominalRisk.toFixed(2)}</b>\\n\\n`;
      msg += `📏 <b>Rekomendasi Berdasarkan SL:</b>\\n`;
      
      defaultPips.forEach(pips => {
         const lotSize = nominalRisk / (pips * 10);
         msg += `• SL <b>${pips}</b> pips ➡️ <b>${lotSize.toFixed(2)}</b> Lot\\n`;
      });

      msg += `\\n<i>Gunakan /lot [pips] untuk hitung custom (contoh: /lot 18)</i>`;
      await ctx.reply(msg, { parse_mode: 'HTML' });
    } catch (e) {
      console.error(e);
      await ctx.reply('Terjadi kesalahan saat menghitung lot.');
    }
  };

  bot.command('lot', async (ctx) => {
    const args = ctx.message.text.split(' ').slice(1);
    const pips = args.length > 0 ? parseFloat(args[0]) : undefined;
    await getLotRecommendation(ctx, pips);
  });

  bot.command('menu', async (ctx) => {
    const msg = `🎛 <b>MENU UTAMA BOT JURNAL</b>\\nSilakan pilih menu di bawah ini:`;
    await ctx.reply(msg, {
      parse_mode: 'HTML',
      ...Markup.inlineKeyboard([
        [Markup.button.callback('🧮 Calculator Lot', 'menu_lot')],
        [Markup.button.callback('📅 Today', 'menu_today'), Markup.button.callback('📅 Weekly', 'menu_weekly')],
        [Markup.button.callback('📅 Monthly', 'menu_monthly'), Markup.button.callback('📈 Compound', 'menu_compound')],
        [Markup.button.callback('🛡 Daily DD', 'menu_dailydd'), Markup.button.callback('🛡 Monthly DD', 'menu_monthlydd')]
      ])
    });
  });

  bot.action('menu_lot', async (ctx) => { await getLotRecommendation(ctx); await ctx.answerCbQuery(); });
  bot.action('menu_today', async (ctx) => { await getStatsByTimeframe(ctx, 'today'); await ctx.answerCbQuery(); });
  bot.action('menu_weekly', async (ctx) => { await getStatsByTimeframe(ctx, 'weekly'); await ctx.answerCbQuery(); });
  bot.action('menu_monthly', async (ctx) => { await getStatsByTimeframe(ctx, 'monthly'); await ctx.answerCbQuery(); });
  bot.action('menu_compound', async (ctx) => { await getStatsByTimeframe(ctx, 'compound'); await ctx.answerCbQuery(); });
  bot.action('menu_dailydd', async (ctx) => { await getStatsByTimeframe(ctx, 'dailydd'); await ctx.answerCbQuery(); });
  bot.action('menu_monthlydd', async (ctx) => { await getStatsByTimeframe(ctx, 'monthlydd'); await ctx.answerCbQuery(); });
"""
content = content.replace(find_commands, replace_commands)

with open('src/lib/telegram.ts', 'w') as f:
    f.write(content)
