import { Client, GatewayIntentBits, EmbedBuilder, Message } from 'discord.js';
import cron from 'node-cron';

export function initDiscordBot(db: any) {
  const token = process.env.DISCORD_BOT_TOKEN;
  if (!token) {
    console.log('Discord Bot Token not found. Skipping Discord integration.');
    return;
  }

  const client = new Client({
    intents: [
      GatewayIntentBits.Guilds,
      GatewayIntentBits.GuildMessages,
      GatewayIntentBits.MessageContent,
    ],
  });

  const channels = {
    journalLog: process.env.DISCORD_CHANNEL_JOURNAL_LOG,
    liveStats: process.env.DISCORD_CHANNEL_LIVE_STATS,
    compounding: process.env.DISCORD_CHANNEL_COMPOUNDING,
    weeklyReview: process.env.DISCORD_CHANNEL_WEEKLY_REVIEW,
  };

  const primaryUserId = process.env.DISCORD_PRIMARY_USER_ID || '1540377868402692207';

  client.once('ready', () => {
    console.log(`Discord Bot logged in as ${client.user?.tag}`);

    // Cron job for weekly review: Every Saturday at 12:00
    cron.schedule('0 12 * * 6', async () => {
      if (channels.weeklyReview) {
        await sendWeeklyReview(client, db, channels.weeklyReview, primaryUserId);
      }
    });
    
    // Auto-update live stats on startup if needed
    // updateLiveStats(client, db, channels.liveStats, primaryUserId);
  });

  client.on('messageCreate', async (message) => {
    if (message.author.bot) return;

    // Handler for #journal-log
    if (channels.journalLog && message.channel.id === channels.journalLog) {
       await handleJournalLog(message, db, primaryUserId, client, channels);
    }
  });

  client.login(token).catch(console.error);
}

function splitCsv(str: string): string[] {
  const result: string[] = [];
  let current = '';
  let inQuotes = false;
  for (let i = 0; i < str.length; i++) {
    const char = str[i];
    if (char === '"' && str[i + 1] === '"') {
      current += '"';
      i++;
    } else if (char === '"') {
      inQuotes = !inQuotes;
    } else if (char === ',' && !inQuotes) {
      result.push(current);
      current = '';
    } else {
      current += char;
    }
  }
  result.push(current);
  return result.map(s => s.trim());
}

function parseTradeData(content: string) {
  try {
    if (content.trim().startsWith('{')) {
      const json = JSON.parse(content);
      return {
        dateStr: '',
        pair: json.pair?.toUpperCase() || 'XAUUSD',
        direction: json.direction || 'Buy',
        setup_name: json.setup_name || json.setup || 'Discord Import',
        size: parseFloat(json.size || json.position_size) || 0.01,
        entry: parseFloat(json.entry || json.entry_price) || 0,
        sl: parseFloat(json.sl) || 0,
        tp: parseFloat(json.tp) || 0,
        result: json.result || 'Pending',
        pl: parseFloat(json.pl || json.realized_pl) || 0,
        emotionScore: 0,
        notes: json.notes || json.reason || 'No reason provided.'
      };
    }
  } catch (e) {}

  const lines = content.split('\n');
  for (const line of lines) {
    if (line.includes(',')) {
      const parts = splitCsv(line);
      if (parts.length >= 10) {
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
          setup_name: parts[4] || 'Discord Import',
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
  }
  return null;
}

async function handleJournalLog(message: Message, db: any, userId: string, client: Client, channels: any) {
  const attachment = message.attachments.first();
  if (!attachment) {
    return; // No chart image
  }

  const tradeData = parseTradeData(message.content);
  if (!tradeData) {
    await message.reply('Please provide trade data in JSON or CSV format (Date, Time, Pair, Direction, Setup, Entry, SL, TP, Size, Result, PL, Emotion, Notes)');
    return;
  }

  try {
    // Get image URL directly
    const imageUrl = attachment.url;

    // Get user's active mode and current balance
    let actualUserId = userId;
    
    // Check if Discord ID is linked
    let discordLookup = await db.execute({
      sql: "SELECT id, current_mode, prop_firm_enabled, prop_firm_balance, initial_balance, balance FROM users WHERE discord_id = ?",
      args: [message.author.id]
    });
    
    let userRes = discordLookup;
    
    if (userRes.rows.length > 0) {
       actualUserId = userRes.rows[0].id;
    } else {
       // Fallback to primaryUserId
       userRes = await db.execute({
         sql: "SELECT id, current_mode, prop_firm_enabled, prop_firm_balance, initial_balance, balance FROM users WHERE id = ?",
         args: [actualUserId]
       });
       
       if (userRes.rows.length === 0) {
         // Fallback to the first available user
         userRes = await db.execute("SELECT id, current_mode, prop_firm_enabled, prop_firm_balance, initial_balance, balance FROM users LIMIT 1");
         if (userRes.rows.length > 0) {
            actualUserId = userRes.rows[0].id;
         } else {
            await message.reply('No users found in the database. Please log in to the web app to initialize your account first. Use `!link <email>` to link your Discord account.');
            return;
         }
       }
    }
    
    let mode = userRes.rows[0].current_mode || 'backtest';
    const isProp = userRes.rows[0].prop_firm_enabled;
    let currentBalance = isProp ? (userRes.rows[0].prop_firm_balance || 10000) : (userRes.rows[0].initial_balance || userRes.rows[0].balance || 10000);

    
    // Add PL to balance to check for compounding milestones
    const oldBalance = currentBalance;
    const newBalance = oldBalance + tradeData.pl;
    
    // Update balance in DB
    if (userRes.rows[0].prop_firm_enabled) {
        await db.execute({ sql: "UPDATE users SET prop_firm_balance = ? WHERE id = ?", args: [newBalance, actualUserId] });
    } else {
        await db.execute({ sql: "UPDATE users SET initial_balance = ? WHERE id = ?", args: [newBalance, actualUserId] });
    }

    let created_at = new Date().toISOString();
    if (tradeData.dateStr) {
      const testDate = new Date(tradeData.dateStr);
      if (!isNaN(testDate.getTime())) {
        created_at = tradeData.dateStr; // Use the exact local time string from CSV
      }
    }

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

    const embed = new EmbedBuilder()
      .setColor(tradeData.result === 'Win' ? '#10B981' : tradeData.result === 'Loss' ? '#EF4444' : '#64748B')
      .setTitle(`Trade Logged: ${tradeData.pair} ${tradeData.direction}`)
      .setDescription(`**Result**: ${tradeData.result} | **P/L**: $${tradeData.pl}\n**Reason**: ${tradeData.notes}`)
      .addFields(
        { name: 'Setup', value: tradeData.setup_name || '-', inline: true },
        { name: 'Size', value: String(tradeData.size), inline: true },
        { name: 'New Balance', value: `$${newBalance.toFixed(2)}`, inline: true },
        { name: 'Entry', value: String(tradeData.entry), inline: true },
        { name: 'SL', value: String(tradeData.sl), inline: true },
        { name: 'TP', value: String(tradeData.tp), inline: true }
      )
      .setImage(attachment.url)
      .setTimestamp();

    await message.reply({ embeds: [embed] });
    
    // Trigger updates
    if (channels.liveStats) {
       await updateLiveStats(client, db, channels.liveStats, actualUserId);
    }
    
    if (channels.compounding) {
       await checkMilestones(client, channels.compounding, oldBalance, newBalance);
    }

  } catch (error) {
    console.error('Error handling journal log:', error);
    await message.reply('Failed to save trade.');
  }
}

async function updateLiveStats(client: Client, db: any, channelId: string, userId: string) {
  try {
    const channel = await client.channels.fetch(channelId);
    if (!channel || !channel.isTextBased()) return;

    // Calculate stats
    let actualUserId = userId;
    let userRes = await db.execute({
      sql: "SELECT id, initial_balance, prop_firm_enabled, prop_firm_balance FROM users WHERE id = ?",
      args: [actualUserId]
    });
    
    if (userRes.rows.length === 0) {
       userRes = await db.execute("SELECT id, initial_balance, prop_firm_enabled, prop_firm_balance FROM users LIMIT 1");
       if (userRes.rows.length > 0) {
          actualUserId = userRes.rows[0].id;
       } else {
          return; // No users
       }
    }
    
    const tradesRes = await db.execute({
      sql: "SELECT * FROM trades WHERE user_id = ? ORDER BY created_at ASC",
      args: [actualUserId]
    });
    
    let equity = userRes.rows[0].prop_firm_enabled ? (userRes.rows[0].prop_firm_balance || 10000) : (userRes.rows[0].initial_balance || 10000);


    const trades = tradesRes.rows;
    const totalTrades = trades.length;
    const wins = trades.filter((t: any) => t.result === 'Win').length;
    const winRate = totalTrades > 0 ? ((wins / totalTrades) * 100).toFixed(1) : '0.0';
    
    // Calculate streak
    let streak = 0;
    let isWinStreak = true;
    for (let i = trades.length - 1; i >= 0; i--) {
      const res = trades[i].result;
      if (res === 'Pending' || res === 'Breakeven') continue;
      if (streak === 0) {
        isWinStreak = res === 'Win';
        streak++;
      } else {
        if ((isWinStreak && res === 'Win') || (!isWinStreak && res === 'Loss')) {
          streak++;
        } else {
          break;
        }
      }
    }
    
    const streakStr = streak > 0 ? `${streak} ${isWinStreak ? 'Wins 🔥' : 'Losses 🧊'}` : 'None';

    const embed = new EmbedBuilder()
      .setColor('#3B82F6')
      .setTitle('📊 Live Trading Stats')
      .addFields(
        { name: 'Current Equity', value: `$${equity.toFixed(2)}`, inline: true },
        { name: 'Win Rate', value: `${winRate}%`, inline: true },
        { name: 'Total Trades', value: `${totalTrades}`, inline: true },
        { name: 'Current Streak', value: streakStr, inline: true }
      )
      .setTimestamp();

    // Check for a pinned message from this bot
    const pinnedMessages = await (channel as any).messages.fetchPinned();
    const botPinned = pinnedMessages.find(m => m.author.id === client.user?.id);

    if (botPinned) {
      await botPinned.edit({ embeds: [embed] });
    } else {
      const msg = await (channel as any).send({ embeds: [embed] });
      await msg.pin();
    }
  } catch (error) {
    console.error('Error updating live stats:', error);
  }
}

async function checkMilestones(client: Client, channelId: string, oldEquity: number, newEquity: number) {
  try {
    const channel = await client.channels.fetch(channelId);
    if (!channel || !channel.isTextBased()) return;

    // Check $100 milestones
    const oldLevel = Math.floor(oldEquity / 100) * 100;
    const newLevel = Math.floor(newEquity / 100) * 100;

    if (newLevel > oldLevel) {
      const embed = new EmbedBuilder()
        .setColor('#10B981')
        .setTitle('🎉 Milestone Reached!')
        .setDescription(`Congratulations! The account equity has passed **$${newLevel}**!\nCurrent Equity: **$${newEquity.toFixed(2)}**`)
        .setThumbnail('https://cdn-icons-png.flaticon.com/512/3176/3176294.png');
      
      await (channel as any).send({ embeds: [embed] });
    }
  } catch (error) {
    console.error('Error checking milestones:', error);
  }
}

async function sendWeeklyReview(client: Client, db: any, channelId: string, userId: string) {
  try {
    const channel = await client.channels.fetch(channelId);
    if (!channel || !channel.isTextBased()) return;

    const sevenDaysAgo = new Date();
    sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);

    let actualUserId = userId;
    const userRes = await db.execute({ sql: "SELECT id FROM users WHERE id = ?", args: [actualUserId] });
    if (userRes.rows.length === 0) {
       const firstUser = await db.execute("SELECT id FROM users LIMIT 1");
       if (firstUser.rows.length > 0) actualUserId = firstUser.rows[0].id;
       else return;
    }

    const tradesRes = await db.execute({
      sql: "SELECT * FROM trades WHERE user_id = ? AND created_at >= ?",
      args: [actualUserId, sevenDaysAgo.toISOString()]
    });

    const trades = tradesRes.rows;
    const total = trades.length;
    let weeklyPL = 0;
    let wins = 0;
    
    trades.forEach((t: any) => {
      if (t.realized_pl) weeklyPL += t.realized_pl;
      if (t.result === 'Win') wins++;
    });
    
    const winRate = total > 0 ? ((wins / total) * 100).toFixed(1) : '0.0';

    const embed = new EmbedBuilder()
      .setColor('#8B5CF6')
      .setTitle('📅 Weekly Review Summary')
      .setDescription('Here is how we did over the last 7 days.')
      .addFields(
        { name: 'Trades Taken', value: `${total}`, inline: true },
        { name: 'Win Rate', value: `${winRate}%`, inline: true },
        { name: 'Weekly P/L', value: `$${weeklyPL.toFixed(2)}`, inline: true }
      )
      .setFooter({ text: 'Stay disciplined!' })
      .setTimestamp();

    await (channel as any).send({ embeds: [embed] });
  } catch (error) {
    console.error('Error sending weekly review:', error);
  }
}
