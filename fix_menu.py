import re

with open('src/lib/telegram.ts', 'r') as f:
    content = f.read()

find_menu_cmd = """  bot.command('menu', async (ctx) => {
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
  bot.action('menu_monthlydd', async (ctx) => { await getStatsByTimeframe(ctx, 'monthlydd'); await ctx.answerCbQuery(); });"""

replace_menu_cmd = """  bot.command('menu', async (ctx) => {
    const msg = `🎛️ <b>JURNAL TRADING COMMAND CENTER</b>\\nPilih menu di bawah ini untuk akses cepat:`;
    await ctx.reply(msg, {
      parse_mode: 'HTML',
      ...Markup.inlineKeyboard([
        [Markup.button.callback('📊 Today', 'cmd_today'), Markup.button.callback('🗓️ Weekly', 'cmd_weekly')],
        [Markup.button.callback('📅 Monthly', 'cmd_monthly'), Markup.button.callback('📈 Compound', 'cmd_compound')],
        [Markup.button.callback('🛡️ Daily DD', 'cmd_dailydd'), Markup.button.callback('🛡️ Monthly DD', 'cmd_monthlydd')],
        [Markup.button.callback('🧮 Lot Calc', 'cmd_lot'), Markup.button.callback('💰 Balance', 'cmd_balance')],
        [Markup.button.callback('↩️ Undo Trade', 'cmd_undo'), Markup.button.callback('🚀 Start / Help', 'cmd_start')]
      ])
    });
  });

  bot.action('cmd_today', async (ctx) => { await ctx.answerCbQuery().catch(()=>{}); await getStatsByTimeframe(ctx, 'today'); });
  bot.action('cmd_weekly', async (ctx) => { await ctx.answerCbQuery().catch(()=>{}); await getStatsByTimeframe(ctx, 'weekly'); });
  bot.action('cmd_monthly', async (ctx) => { await ctx.answerCbQuery().catch(()=>{}); await getStatsByTimeframe(ctx, 'monthly'); });
  bot.action('cmd_compound', async (ctx) => { await ctx.answerCbQuery().catch(()=>{}); await getStatsByTimeframe(ctx, 'compound'); });
  bot.action('cmd_dailydd', async (ctx) => { await ctx.answerCbQuery().catch(()=>{}); await getStatsByTimeframe(ctx, 'dailydd'); });
  bot.action('cmd_monthlydd', async (ctx) => { await ctx.answerCbQuery().catch(()=>{}); await getStatsByTimeframe(ctx, 'monthlydd'); });
  bot.action('cmd_lot', async (ctx) => { await ctx.answerCbQuery().catch(()=>{}); await getLotRecommendation(ctx); });
  bot.action('cmd_balance', async (ctx) => { await ctx.answerCbQuery().catch(()=>{}); await getStatsBalance(ctx); });
  bot.action('cmd_undo', async (ctx) => { await ctx.answerCbQuery().catch(()=>{}); await handleUndo(ctx); });
  bot.action('cmd_start', async (ctx) => { await ctx.answerCbQuery().catch(()=>{}); await handleStart(ctx); });"""

content = content.replace(find_menu_cmd, replace_menu_cmd)

with open('src/lib/telegram.ts', 'w') as f:
    f.write(content)
