import fs from 'fs';

let content = fs.readFileSync('src/lib/telegram.ts', 'utf8');

const regex = /bot\.command\('news', async \(ctx\) => \{([\s\S]*?)\}\);/m;

const replacement = `bot.command('news', async (ctx) => {
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
        return ctx.reply(\`📅 Jadwal High-Impact USD News (\${currentMonthYear})\\n───────────────────────────\\n\\nTidak ada High Impact News (USD) untuk minggu ini.\`);
      }

      let msg = \`📅 Jadwal High-Impact USD News (\${currentMonthYear})\\n───────────────────────────\\n\`;

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
         
         msg += \`\${icon} \${dayStr} | \${timeStr} WIB - \${item.title}\\n\`;
      });
      
      msg += \`\\n⚠️ Perhatian: Hindari entry M5 pada zona waktu ⏳!\`;
      
      await ctx.reply(msg, { parse_mode: 'HTML' });
      
    } catch (e) {
      console.error(e);
      await ctx.reply('❌ Gagal mengambil data berita ekonomi.');
    }
  });`;

if (content.match(regex)) {
   content = content.replace(regex, replacement);
   fs.writeFileSync('src/lib/telegram.ts', content);
   console.log("Successfully replaced /news command");
} else {
   console.log("Regex match failed");
}
