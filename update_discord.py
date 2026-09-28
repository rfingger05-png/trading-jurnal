import re

with open('src/lib/discord.ts', 'r') as f:
    content = f.read()

# Replace the event listener 'messageCreate'
find_listener = """  client.on('messageCreate', async (message) => {
    if (message.author.bot) return;

    if (message.channelId === channels.journalLog) {
      await handleJournalLog(message, db, primaryUserId, client, channels);
    }
  });"""

replace_listener = """  client.on('messageCreate', async (message) => {
    if (message.author.bot) return;
    
    // Command: !link <email>
    if (message.content.startsWith('!link')) {
      const email = message.content.split(' ')[1];
      if (!email) {
        await message.reply('Format: `!link <email>`');
        return;
      }
      try {
        const res = await db.execute({
          sql: "SELECT id FROM users WHERE username = ?",
          args: [email]
        });
        if (res.rows.length === 0) {
          await message.reply('User tidak ditemukan. Pastikan email sama dengan di Web Dashboard.');
          return;
        }
        const userId = res.rows[0].id;
        await db.execute({
          sql: "UPDATE users SET discord_id = ? WHERE id = ?",
          args: [message.author.id, userId]
        });
        await message.reply(`✅ Berhasil menghubungkan Discord dengan akun Web (ID: ${userId}).`);
      } catch (err) {
        console.error(err);
        await message.reply('Terjadi kesalahan saat linking.');
      }
      return;
    }
    
    // Mention handler for "ringkasan"
    if (message.mentions.has(client.user?.id || '') && message.content.toLowerCase().includes('ringkasan')) {
      try {
        // Find user by discord_id
        let userRes = await db.execute({
          sql: "SELECT id FROM users WHERE discord_id = ?",
          args: [message.author.id]
        });
        let userId = userRes.rows.length > 0 ? userRes.rows[0].id : primaryUserId;
        
        const tradesRes = await db.execute({
          sql: "SELECT * FROM trades WHERE user_id = ? ORDER BY created_at DESC LIMIT 5",
          args: [userId]
        });
        
        let summary = "📊 **5 Trade Terakhir Anda:**\\n";
        tradesRes.rows.forEach((t: any) => {
          summary += `- ${t.pair} (${t.direction}) | Result: ${t.result} | P/L: $${t.realized_pl}\\n`;
        });
        
        summary += `\\n🔗 Buka Dashboard: ${process.env.APP_URL || 'http://localhost:3000'}`;
        await message.reply(summary);
      } catch (err) {
        console.error(err);
      }
      return;
    }

    if (message.channelId === channels.journalLog) {
      await handleJournalLog(message, db, primaryUserId, client, channels);
    }
  });"""

content = content.replace(find_listener, replace_listener)

# Now fix the CSV schema
# Schema: 0:Date, 1:Time, 2:Pair, 3:Direction, 4:Setup, 5:Entry, 6:SL, 7:TP, 8:Size, 9:Result, 10:PL, 11:Emotion, 12:Notes
# Actually, the user's prompt says:
# [date, time, pair, direction, setup_name, entry_price, sl_price, tp_price, lot_size, result, profit_loss, emotion_tag, notes]
find_schema = """        // Schema: 0:Date, 1:Time, 2:Pair, 3:Direction, 4:Setup, 5:Entry, 6:SL, 7:TP, 8:Size, 9:Result, 10:PL, 11:Emotion, 12:Notes
        const date = parts[0] || '';
        const time = parts[1] || '';
        let combinedDate = '';
        if (date && time) {
          const cleanDate = date.replace(/\\//g, '-').replace(/\\./g, '-');
          combinedDate = `${cleanDate}T${time}:00`;
        }

        const emotion = parts[11] ? `[Emotion: ${parts[11]}] ` : '';
        const rawNotes = parts.length > 12 ? parts.slice(12).join(', ').trim() : '';

        return {
          dateStr: combinedDate,
          pair: parts[2]?.toUpperCase() || 'XAUUSD',
          direction: parts[3]?.toUpperCase().includes('SELL') ? 'Sell' : 'Buy',
          setup_name: parts[4] || 'Discord Import',
          entry: parseFloat(parts[5]) || 0,
          sl: parseFloat(parts[6]) || 0,
          tp: parseFloat(parts[7]) || 0,
          size: parseFloat(parts[8]) || 0,
          result: parts[9] || 'Pending',
          pl: parseFloat(parts[10]) || 0,
          notes: emotion + (rawNotes || 'No reason provided.')
        };"""

replace_schema = """        // Schema: 0:Date, 1:Time, 2:Pair, 3:Direction, 4:Setup, 5:Entry, 6:SL, 7:TP, 8:Size, 9:Result, 10:PL, 11:Emotion, 12:Notes
        const date = parts[0] || '';
        const time = parts[1] || '';
        let combinedDate = '';
        if (date && time) {
          const cleanDate = date.replace(/\\//g, '-').replace(/\\./g, '-');
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
          setup_name: parts[4] || 'Discord Import',
          entry: parseFloat(parts[5]) || 0,
          sl: parseFloat(parts[6]) || 0,
          tp: parseFloat(parts[7]) || 0,
          size: parseFloat(parts[8]) || 0,
          result: parts[9] || 'Pending',
          pl: parseFloat(parts[10]) || 0,
          emotionScore: emotionScore,
          notes: rawNotes || 'No reason provided.'
        };"""
        
content = content.replace(find_schema, replace_schema)

# And the fallback json parsing:
find_json = """        pl: parseFloat(json.pl || json.realized_pl) || 0,
        notes: json.notes || json.reason || 'No reason provided.'
      };"""

replace_json = """        pl: parseFloat(json.pl || json.realized_pl) || 0,
        emotionScore: 0,
        notes: json.notes || json.reason || 'No reason provided.'
      };"""
      
content = content.replace(find_json, replace_json)

# Now fix handleJournalLog lookup logic
find_lookup = """    let actualUserId = userId;
    let userRes = await db.execute({
      sql: "SELECT id, current_mode, prop_firm_enabled, prop_firm_balance, initial_balance FROM users WHERE id = ?",
      args: [actualUserId]
    });
    
    if (userRes.rows.length === 0) {
       // Fallback to the first available user
       userRes = await db.execute("SELECT id, current_mode, prop_firm_enabled, prop_firm_balance, initial_balance FROM users LIMIT 1");
       if (userRes.rows.length > 0) {
          actualUserId = userRes.rows[0].id;
       } else {
          await message.reply('No users found in the database. Please log in to the web app to initialize your account first.');
          return;
       }
    }"""

replace_lookup = """    let actualUserId = userId;
    
    // Check if Discord ID is linked
    let discordLookup = await db.execute({
      sql: "SELECT id, current_mode, prop_firm_enabled, prop_firm_balance, initial_balance FROM users WHERE discord_id = ?",
      args: [message.author.id]
    });
    
    let userRes = discordLookup;
    
    if (userRes.rows.length > 0) {
       actualUserId = userRes.rows[0].id;
    } else {
       // Fallback to primaryUserId
       userRes = await db.execute({
         sql: "SELECT id, current_mode, prop_firm_enabled, prop_firm_balance, initial_balance FROM users WHERE id = ?",
         args: [actualUserId]
       });
       
       if (userRes.rows.length === 0) {
         // Fallback to the first available user
         userRes = await db.execute("SELECT id, current_mode, prop_firm_enabled, prop_firm_balance, initial_balance FROM users LIMIT 1");
         if (userRes.rows.length > 0) {
            actualUserId = userRes.rows[0].id;
         } else {
            await message.reply('No users found in the database. Please log in to the web app to initialize your account first. Use `!link <email>` to link your Discord account.');
            return;
         }
       }
    }"""
    
content = content.replace(find_lookup, replace_lookup)

# Fix insert
find_insert = """    await db.execute({
      sql: `INSERT INTO trades (
        user_id, pair, direction, setup_name, entry_price, sl, tp, 
        account_balance, risk_percentage, position_size, nominal_risk, 
        notes, result, realized_pl, image, run_mode, created_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      args: [
        actualUserId, tradeData.pair, tradeData.direction, tradeData.setup_name, tradeData.entry, tradeData.sl, tradeData.tp,
        oldBalance, 0, tradeData.size, 0,
        tradeData.notes, tradeData.result, tradeData.pl, base64Image, mode, created_at
      ]
    });"""

replace_insert = """    await db.execute({
      sql: `INSERT INTO trades (
        user_id, pair, direction, setup_name, entry_price, sl, tp, 
        account_balance, risk_percentage, position_size, nominal_risk, 
        anxiety_level, notes, result, realized_pl, image, run_mode, created_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      args: [
        actualUserId, tradeData.pair, tradeData.direction, tradeData.setup_name, tradeData.entry, tradeData.sl, tradeData.tp,
        newBalance, 0, tradeData.size, 0,
        tradeData.emotionScore, tradeData.notes, tradeData.result, tradeData.pl, base64Image, mode, created_at
      ]
    });"""

content = content.replace(find_insert, replace_insert)

with open('src/lib/discord.ts', 'w') as f:
    f.write(content)

