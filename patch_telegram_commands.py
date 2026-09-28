import re

with open('src/lib/telegram.ts', 'r') as f:
    content = f.read()

# Add news command
news_command = """
  bot.command('news', async (ctx) => {
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
      
      await ctx.reply(`✅ <b>DEPOSIT BERHASIL</b>\\n━━━━━━━━━━━━━━━━━━━\\n💰 Jumlah: +$${amount.toFixed(2)}\\n<i>Data telah tersinkronisasi dengan Web Dashboard.</i>`, { parse_mode: 'HTML' });
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
      
      await ctx.reply(`✅ <b>WITHDRAWAL BERHASIL</b>\\n━━━━━━━━━━━━━━━━━━━\\n💸 Jumlah: -$${amount.toFixed(2)}\\n<i>Data telah tersinkronisasi dengan Web Dashboard.</i>`, { parse_mode: 'HTML' });
    } catch (e) {
      console.error(e);
      await ctx.reply('❌ Terjadi kesalahan.');
    }
  });
"""

# Insert commands right after bot.command('settarget'
anchor = "  bot.command('settarget', async (ctx) => {"
if anchor in content:
    content = content.replace(anchor, news_command + "\n" + anchor)

with open('src/lib/telegram.ts', 'w') as f:
    f.write(content)

