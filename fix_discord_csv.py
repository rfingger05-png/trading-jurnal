import re

with open('src/lib/discord.ts', 'r') as f:
    content = f.read()

split_csv_fn = """function splitCsv(str: string): string[] {
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

function parseTradeData(content: string) {"""

content = content.replace("function parseTradeData(content: string) {", split_csv_fn)

parse_trade_find = """      const json = JSON.parse(content);
      return {
        pair: json.pair?.toUpperCase() || 'XAUUSD',
        direction: json.direction || 'Buy',
        size: parseFloat(json.size || json.position_size) || 0.01,
        entry: parseFloat(json.entry || json.entry_price) || 0,
        sl: parseFloat(json.sl) || 0,
        tp: parseFloat(json.tp) || 0,
        result: json.result || 'Pending',
        pl: parseFloat(json.pl || json.realized_pl) || 0,
        notes: json.notes || json.reason || 'No reason provided.'
      };
    }
  } catch (e) {}

  const lines = content.split('\\n');
  for (const line of lines) {
    if (line.includes(',')) {
      const parts = line.split(',').map(s => s.trim());
      if (parts.length >= 6) {
        return {
          pair: parts[0].toUpperCase(),
          direction: parts[1],
          size: parseFloat(parts[2]) || 0,
          entry: parseFloat(parts[3]) || 0,
          sl: parseFloat(parts[4]) || 0,
          tp: parseFloat(parts[5]) || 0,
          result: parts[6] || 'Pending',
          pl: parseFloat(parts[7] || '0') || 0,
          notes: parts.slice(8).join(', ').trim() || 'No reason provided.'
        };
      }
    }
  }
  return null;
}"""

parse_trade_replace = """      const json = JSON.parse(content);
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
        notes: json.notes || json.reason || 'No reason provided.'
      };
    }
  } catch (e) {}

  const lines = content.split('\\n');
  for (const line of lines) {
    if (line.includes(',')) {
      const parts = splitCsv(line);
      if (parts.length >= 10) {
        // Schema: 0:Date, 1:Time, 2:Pair, 3:Direction, 4:Setup, 5:Entry, 6:SL, 7:TP, 8:Size, 9:Result, 10:PL, 11:Emotion, 12:Notes
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
        };
      }
    }
  }
  return null;
}"""

content = content.replace(parse_trade_find, parse_trade_replace)


insert_find = """    const created_at = new Date().toISOString();

    await db.execute({
      sql: `INSERT INTO trades (
        user_id, pair, direction, setup_name, entry_price, sl, tp, 
        account_balance, risk_percentage, position_size, nominal_risk, 
        notes, result, realized_pl, image, run_mode, created_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      args: [
        actualUserId, tradeData.pair, tradeData.direction, 'Discord Import', tradeData.entry, tradeData.sl, tradeData.tp,
        oldBalance, 0, tradeData.size, 0,
        tradeData.notes, tradeData.result, tradeData.pl, base64Image, mode, created_at
      ]
    });"""

insert_replace = """    let created_at = new Date().toISOString();
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
        notes, result, realized_pl, image, run_mode, created_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      args: [
        actualUserId, tradeData.pair, tradeData.direction, tradeData.setup_name, tradeData.entry, tradeData.sl, tradeData.tp,
        oldBalance, 0, tradeData.size, 0,
        tradeData.notes, tradeData.result, tradeData.pl, base64Image, mode, created_at
      ]
    });"""

content = content.replace(insert_find, insert_replace)


embed_find = """      .addFields(
        { name: 'Entry', value: String(tradeData.entry), inline: true },
        { name: 'SL', value: String(tradeData.sl), inline: true },
        { name: 'TP', value: String(tradeData.tp), inline: true },
        { name: 'Size', value: String(tradeData.size), inline: true },
        { name: 'New Balance', value: `$${newBalance.toFixed(2)}`, inline: true }
      )"""

embed_replace = """      .addFields(
        { name: 'Setup', value: tradeData.setup_name || '-', inline: true },
        { name: 'Size', value: String(tradeData.size), inline: true },
        { name: 'New Balance', value: `$${newBalance.toFixed(2)}`, inline: true },
        { name: 'Entry', value: String(tradeData.entry), inline: true },
        { name: 'SL', value: String(tradeData.sl), inline: true },
        { name: 'TP', value: String(tradeData.tp), inline: true }
      )"""

content = content.replace(embed_find, embed_replace)

msg_reply_find = """await message.reply('Please provide trade data in JSON or CSV format (Pair, Direction, Size, Entry, SL, TP, Result, PL, Reason)');"""
msg_reply_replace = """await message.reply('Please provide trade data in JSON or CSV format (Date, Time, Pair, Direction, Setup, Entry, SL, TP, Size, Result, PL, Emotion, Notes)');"""

content = content.replace(msg_reply_find, msg_reply_replace)

with open('src/lib/discord.ts', 'w') as f:
    f.write(content)
