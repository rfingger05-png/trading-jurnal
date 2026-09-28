import { createClient } from "@libsql/client";
import dotenv from "dotenv";
dotenv.config();
const db = createClient({
  url: process.env.TURSO_DATABASE_URL || "https://jurnal-tryout-lancarkoreaa.aws-ap-northeast-1.turso.io",
  authToken: process.env.TURSO_AUTH_TOKEN
});
const parseCSVLine = (line) => {
    const arr = [];
    let current = '';
    let inQuotes = false;
    for (let i = 0; i < line.length; i++) {
      const char = line[i];
      if (char === '"') {
        inQuotes = !inQuotes;
      } else if (char === ',' && !inQuotes) {
        arr.push(current);
        current = '';
      } else {
        current += char;
      }
    }
    arr.push(current);
    return arr.map(str => str.trim());
};

async function run() {
  try {
    const text = "2026-08-28, 09:08, XAUUSD, BUY, PC, 4579.850, 4575.973, 4589.125, 0.09, WIN, 92.10, Calm";
    const cleanedText = text;
    if (cleanedText.includes(',')) {
        const parts = parseCSVLine(cleanedText);
        if (parts.length >= 11 && ['BUY', 'SELL'].includes(parts[3].toUpperCase())) {
          const [dateStr, timeStr, pair, type, setup, entry, sl, tp, lot, status, pnl, emosi, ...notesArr] = parts;
          const notes = notesArr.join(', ');
          
          let userRes = await db.execute({
              sql: "SELECT id, current_mode, prop_firm_enabled, prop_firm_balance, initial_balance FROM users WHERE username = 'jal'"
          });
          const userData = userRes.rows[0];
          if (!userData) { console.log("User not found!"); return; }
          const actualUserId = userData.id;
          const mode = userData.current_mode || 'backtest';
          
          const existingTrades = await db.execute({
            sql: "SELECT realized_pl FROM trades WHERE user_id = ?",
            args: [actualUserId]
          });
          const totalPastPL = existingTrades.rows.reduce((acc, t) => acc + (t.realized_pl || 0), 0);
          
          const isProp = userData.prop_firm_enabled;
          const initialBal = isProp ? (userData.prop_firm_balance || 1000) : (userData.initial_balance || 1000);
          const oldBalance = initialBal + totalPastPL;
          const realizedPl = parseFloat(pnl) || 0;
          const newBalance = oldBalance + realizedPl;
          
          let created_at = new Date().toISOString();
          try {
             const parsedDate = new Date(`${dateStr} ${timeStr}`);
             if (!isNaN(parsedDate.getTime())) {
                created_at = parsedDate.toISOString();
             }
          } catch(e) {}
          
          const tvUrl = null;
          const hasImage = 0;
          
          await db.execute({
            sql: `INSERT INTO trades (
              user_id, pair, direction, setup_name, entry_price, sl, tp, 
              account_balance, position_size, result, realized_pl, 
              anxiety_level, notes, image_url, has_image, run_mode, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
            args: [
              actualUserId, pair, type.toUpperCase(), setup, parseFloat(entry)||0, parseFloat(sl)||0, parseFloat(tp)||0,
              newBalance, parseFloat(lot)||0, status.toUpperCase(), realizedPl,
              emosi, notes, tvUrl, hasImage, mode, created_at
            ]
          });
          console.log("Success!");
        }
    }
  } catch(e) {
    console.log("Error:", e);
  }
}
run();
