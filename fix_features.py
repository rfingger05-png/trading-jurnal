import re

with open('src/lib/telegram.ts', 'r') as f:
    content = f.read()

# 1. Update SELECT queries in getStatsByTimeframe
content = content.replace(
    "prop_firm_daily_dd, target_balance FROM users",
    "prop_firm_daily_dd, target_balance, compound_risk FROM users"
)

# 2. Extract compound_risk in getStatsByTimeframe
content = content.replace(
    "const targetBalance = userData.target_balance || 1000000;",
    "const targetBalance = userData.target_balance || 1000000;\n      const compoundRisk = userData.compound_risk || 2.5;"
)

# 3. Use compoundRisk in compound projection
content = content.replace(
    "let risk = projEquity * 0.025; // 2.5% risk",
    "let risk = projEquity * (compoundRisk / 100); // Dynamic risk"
)

# 4. Add /setrisk and /report commands
new_commands = """
  bot.command('setrisk', async (ctx) => {
    try {
      const text = ctx.message.text.split(' ');
      if (text.length < 2) {
        return ctx.reply('❌ Format salah.\\nContoh: /setrisk 2.5');
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
           sql: "SELECT id FROM users WHERE telegram_id = 'PLACEHOLDER_TELEGRAM_ID' OR username = 'singgahrang@gmail.com'"
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
      
      await ctx.reply(`✅ <b>RISK COMPOUNDING DIPERBARUI</b>\\n━━━━━━━━━━━━━━━━━━━\\nRisk baru: <b>${risk}%</b> per hari.\\nProyeksi compounding sekarang akan menggunakan angka ini.`, { parse_mode: 'HTML' });
      
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
           sql: "SELECT id FROM users WHERE telegram_id = 'PLACEHOLDER_TELEGRAM_ID' OR username = 'singgahrang@gmail.com'"
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
      let csv = 'ID,Pair,Direction,Setup,Entry,SL,TP,Result,Realized_PL,Checklist,Notes,Date\\n';
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
        csv += row.join(',') + '\\n';
      });
      
      const buffer = Buffer.from(csv, 'utf8');
      
      await ctx.replyWithDocument(
        { source: buffer, filename: 'Trading_Journal_Report.csv' },
        { caption: `✅ Laporan Jurnal Trading\\nTotal: ${trades.length} trades` }
      );
      
    } catch (e) {
      console.error(e);
      await ctx.reply('❌ Gagal menghasilkan laporan.');
    }
  });
"""

# Insert commands right after bot.command('settarget', ...)
if "bot.command('settarget'" in content:
    # We will inject new commands after the 'settarget' block. We can just inject it before the last handleUndo
    # Wait, the best place is before bot.action
    pass

# Alternatively, just append to the file before the export ends?
# telegram.ts exports initTelegramBot. We need to put it inside initTelegramBot.
# Let's inject after bot.command('settarget'.... ) ends.
# I will use replace with a known anchor.
anchor = "bot.command('settarget', async (ctx) => {"
if anchor in content:
    content = content.replace(anchor, new_commands + "\\n  " + anchor)

# 5. Update renderMenu text
old_menu = "`🏛️ <b>JOURNAL TRADING DASHBOARD</b>\\n━━━━━━━━━━━━━━━━━━━\\n<i>Pilih menu di bawah untuk statistik & alat trading:</i>`"
new_menu = "`🏛️ <b>JOURNAL TRADING DASHBOARD</b>\\n━━━━━━━━━━━━━━━━━━━\\n<i>Pilih menu di bawah untuk statistik & alat trading:</i>\\n\\n💡 <b>Perintah Tambahan:</b>\\n• /settarget [angka] - Set target (USC)\\n• /setrisk [persen] - Set % risk compound (cth: 2.5)\\n• /report - Export jurnal (CSV)`"

content = content.replace(old_menu, new_menu)

with open('src/lib/telegram.ts', 'w') as f:
    f.write(content)

