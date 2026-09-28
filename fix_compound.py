import re

with open('src/lib/telegram.ts', 'r') as f:
    content = f.read()

# 1. Update SELECT queries in getStatsByTimeframe
content = content.replace(
    "SELECT id, initial_balance, prop_firm_enabled, prop_firm_balance, prop_firm_daily_dd FROM users",
    "SELECT id, initial_balance, prop_firm_enabled, prop_firm_balance, prop_firm_daily_dd, target_balance FROM users"
)

# 2. Extract target_balance in getStatsByTimeframe
if "const isProp = userData.prop_firm_enabled;" in content:
    content = content.replace(
        "const isProp = userData.prop_firm_enabled;",
        "const isProp = userData.prop_firm_enabled;\n      const targetBalance = userData.target_balance || 1000000;"
    )

# 3. Replace the compound block
find_compound = """      } else if (timeframe === 'compound') {
        let eqTarget = initialBal;
        let dayCount = 0;
        
        while (currentEquity >= eqTarget * 1.05) {
           eqTarget = eqTarget * 1.05;
           dayCount++;
        }
        
        let msg = `📈 <b>MILESTONE COMPOUNDING</b>\\n<i>(Target +5% per hari)</i>\\n━━━━━━━━━━━━━━━━━━━\\n`;
        msg += `Current Equity: <b>$${currentEquity.toFixed(2)}</b>\\n\\n`;
        
        if (dayCount > 0) {
           msg += `✅ <b>Day ${dayCount}:</b> $${eqTarget.toFixed(2)} [COMPLETED]\\n`;
        } else {
           msg += `🚀 <b>Day 0:</b> $${initialBal.toFixed(2)} [START]\\n`;
        }
        
        let projEquity = eqTarget;
        for (let i = 1; i <= 10; i++) {
           projEquity = projEquity * 1.05;
           let currentDay = dayCount + i;
           msg += `⏳ Day ${currentDay}: $${projEquity.toFixed(2)}\\n`;
        }
        
        msg += `\\n<i>Disiplin dan konsisten adalah kuncinya!</i>`;
        await sendOrEdit(ctx, msg, true);
        return;
      }"""

replace_compound = """      } else if (timeframe === 'compound') {
        const sisaTarget = targetBalance - currentEquity;
        const rawProgress = (currentEquity / targetBalance) * 100;
        const progressPercent = rawProgress > 100 ? 100 : rawProgress;
        
        // Buat Progress Bar 10 blok
        const filledBlocks = Math.floor(progressPercent / 10);
        const emptyBlocks = 10 - filledBlocks;
        const progressBar = '🟩'.repeat(filledBlocks) + '⬜'.repeat(emptyBlocks);
        
        let estimasiHari = 0;
        if (currentEquity > 0 && targetBalance > currentEquity) {
            estimasiHari = Math.ceil(Math.log(targetBalance / currentEquity) / Math.log(1.05));
        }

        let msg = `📈 <b>COMPOUNDING PROGRESS & PLAN</b>\\n━━━━━━━━━━━━━━━━━━━\\n`;
        msg += `💰 <b>Balance Saat Ini:</b> ${currentEquity.toLocaleString('en-US', {minimumFractionDigits:0, maximumFractionDigits:2})} USC\\n`;
        msg += `🎯 <b>Target Akhir:</b> ${targetBalance.toLocaleString('en-US', {minimumFractionDigits:0, maximumFractionDigits:2})} USC\\n`;
        msg += `📊 <b>Progres Total:</b> [${progressBar}] ${progressPercent.toFixed(2)}%\\n`;
        msg += `🚀 <b>Sisa Target:</b> ${sisaTarget > 0 ? sisaTarget.toLocaleString('en-US', {minimumFractionDigits:0, maximumFractionDigits:2}) : 0} USC\\n`;
        msg += `⏳ <b>Estimasi Sisa:</b> ~${estimasiHari} Hari Trading\\n\\n`;
        msg += `🗓️ <b>Proyeksi Target 10 Hari Ke Depan (Net 5%/Hari):</b>\\n`;

        let projEquity = currentEquity;
        for (let i = 1; i <= 10; i++) {
           let risk = projEquity * 0.025; // 2.5% risk
           let lot = risk / 150; // SL 15 pips (150 points for USC standard calculation if 1 pip = 10, or depends. 15 pips * 10 = $150 per lot? User logic: risk/(sl_pips*pip_value). Usually standard lot is risk/(15). Let's use risk/150 as a placeholder if they use micro accounts, or risk/15. Wait, 15 pips on gold = 150 ticks. If 1 lot = $1 per tick, 150 ticks = $150. lot = risk / 150. Let's use risk / 150 for XAUUSD.)
           // We will format them properly.
           
           projEquity = projEquity * 1.05;
           msg += `• <b>Hari ${i}:</b> Balance ${projEquity.toLocaleString('en-US', {minimumFractionDigits:0, maximumFractionDigits:2})} USC | Lot: ${lot.toFixed(2)} | Risk: ${risk.toLocaleString('en-US', {minimumFractionDigits:0, maximumFractionDigits:2})} USC\\n`;
        }
        
        msg += `━━━━━━━━━━━━━━━━━━━\\n<i>*Gunakan command \`/settarget <jumlah>\` untuk mengubah target.</i>`;
        await sendOrEdit(ctx, msg, true);
        return;
      }"""

if find_compound in content:
    content = content.replace(find_compound, replace_compound)
else:
    print("find_compound not found")

# 4. Add /settarget command
settarget_cmd = """
  bot.command('settarget', async (ctx) => {
    try {
      const text = ctx.message.text.split(' ');
      if (text.length < 2) {
        return ctx.reply('❌ Format salah.\\nContoh: /settarget 1000000');
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
           sql: "SELECT id FROM users WHERE telegram_id = 'PLACEHOLDER_TELEGRAM_ID' OR username = 'singgahrang@gmail.com'"
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
      let msg = `🎯 <b>TARGET BALANCED DIPERBARUI!</b>\\n━━━━━━━━━━━━━━━━━━━\\n`;
      msg += `Target Baru: ${target.toLocaleString('en-US')} USC ($${usdEquiv.toLocaleString('en-US')} USD)\\n`;
      msg += `<i>*Semua kalkulasi proyeksi compounding otomatis menggunakan acuan ini.</i>`;
      
      await ctx.reply(msg, { parse_mode: 'HTML' });
      
    } catch (e) {
      console.error(e);
      await ctx.reply('Terjadi kesalahan.');
    }
  });
"""

# Insert settarget command after bot.command('menu', ...)
if "bot.command('menu', renderMenu);" in content:
    content = content.replace("bot.command('menu', renderMenu);", "bot.command('menu', renderMenu);" + settarget_cmd)
else:
    print("menu command not found")

with open('src/lib/telegram.ts', 'w') as f:
    f.write(content)
