import re

with open('src/lib/telegram.ts', 'r') as f:
    content = f.read()

pattern = r"const msg = `📊 <b>STATISTIK.*?await ctx\.reply\('Terjadi kesalahan\.'\);\n\s*\}\n\s*\}\);"

replace = """const msg = `📊 <b>STATISTIK JURNAL TRADING</b>\\n` +
                  `━━━━━━━━━━━━━━━━━━━\\n` +
                  `- Current Equity: <b>$${pureEquity.toFixed(2)}</b>\\n` +
                  `- Total Trades: ${trades.length}\\n` +
                  `- Win Rate: ${winRate}%\\n` +
                  `- Total P/L: ${signPL}$${totalPL.toFixed(2)}`;
      
      await ctx.reply(msg, { parse_mode: 'HTML' });
    } catch (e) {
      console.error(e);
      await ctx.reply('Terjadi kesalahan.');
    }
  };
  bot.command(['stats', 'balance'], getStatsBalance);"""

content = re.sub(pattern, replace, content, flags=re.DOTALL)

with open('src/lib/telegram.ts', 'w') as f:
    f.write(content)
