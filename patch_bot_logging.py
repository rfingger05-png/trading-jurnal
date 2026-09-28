import re

with open('src/lib/telegram.ts', 'r') as f:
    content = f.read()

# Add an else block to the if (parts.length >= 11)
old_code = """          if (tvUrl) {
            msg += `🖼️ Chart: ${tvUrl}\\n`;
          }
          
          await ctx.reply(msg, { disable_web_page_preview: false });
          return;
        }
      }
    } catch (e) {"""

new_code = """          if (tvUrl) {
            msg += `🖼️ Chart: ${tvUrl}\\n`;
          }
          
          await ctx.reply(msg, { disable_web_page_preview: false });
          return;
        } else {
          await ctx.reply(`⚠️ Format CSV tidak valid atau gagal dibaca.\\nJumlah kolom: ${parts.length} (Dibutuhkan minimal 11).\\nKolom Direction (BUY/SELL): ${parts[3] ? parts[3].toUpperCase() : 'Kosong'}\\n\\nPastikan mengikuti format:\\nDate, Time, Pair, Direction, Setup, Entry, SL, TP, Size, Result, PL, Emotion, Notes`);
        }
      } else {
        await ctx.reply(`⚠️ Pesan tidak mengandung koma. Harap kirim dalam format CSV:\\nDate, Time, Pair, Direction, Setup, Entry, SL, TP, Size, Result, PL, Emotion, Notes`);
      }
    } catch (e) {"""

content = content.replace(old_code, new_code)

with open('src/lib/telegram.ts', 'w') as f:
    f.write(content)
