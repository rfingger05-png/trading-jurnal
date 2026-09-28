import re

with open('src/lib/discord.ts', 'r') as f:
    content = f.read()

# Fix handleJournalLog
find_hjl = """    // Get user's active mode and current balance
    const userRes = await db.execute({
      sql: "SELECT current_mode, prop_firm_enabled, prop_firm_balance, initial_balance FROM users WHERE id = ?",
      args: [userId]
    });
    
    let mode = 'backtest';
    let currentBalance = 10000;
    if (userRes.rows.length > 0) {
      mode = userRes.rows[0].current_mode;
      const isProp = userRes.rows[0].prop_firm_enabled;
      currentBalance = isProp ? (userRes.rows[0].prop_firm_balance || 10000) : (userRes.rows[0].initial_balance || 10000);
    }"""

replace_hjl = """    // Get user's active mode and current balance
    let actualUserId = userId;
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
    }
    
    let mode = userRes.rows[0].current_mode || 'backtest';
    const isProp = userRes.rows[0].prop_firm_enabled;
    let currentBalance = isProp ? (userRes.rows[0].prop_firm_balance || 10000) : (userRes.rows[0].initial_balance || 10000);
"""

content = content.replace(find_hjl, replace_hjl)

# Fix the INSERT target user
find_insert = """    if (userRes.rows.length > 0) {
        if (userRes.rows[0].prop_firm_enabled) {
            await db.execute({ sql: "UPDATE users SET prop_firm_balance = ? WHERE id = ?", args: [newBalance, userId] });
        } else {
            await db.execute({ sql: "UPDATE users SET initial_balance = ? WHERE id = ?", args: [newBalance, userId] });
        }
    }

    const created_at = new Date().toISOString();

    await db.execute({
      sql: `INSERT INTO trades (
        user_id, pair, direction, setup_name, entry_price, sl, tp, 
        account_balance, risk_percentage, position_size, nominal_risk, 
        notes, result, realized_pl, image, run_mode, created_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      args: [
        userId, tradeData.pair, tradeData.direction, 'Discord Import', tradeData.entry, tradeData.sl, tradeData.tp,"""

replace_insert = """    if (userRes.rows[0].prop_firm_enabled) {
        await db.execute({ sql: "UPDATE users SET prop_firm_balance = ? WHERE id = ?", args: [newBalance, actualUserId] });
    } else {
        await db.execute({ sql: "UPDATE users SET initial_balance = ? WHERE id = ?", args: [newBalance, actualUserId] });
    }

    const created_at = new Date().toISOString();

    await db.execute({
      sql: `INSERT INTO trades (
        user_id, pair, direction, setup_name, entry_price, sl, tp, 
        account_balance, risk_percentage, position_size, nominal_risk, 
        notes, result, realized_pl, image, run_mode, created_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      args: [
        actualUserId, tradeData.pair, tradeData.direction, 'Discord Import', tradeData.entry, tradeData.sl, tradeData.tp,"""

content = content.replace(find_insert, replace_insert)

# Fix updateLiveStats
find_uls = """    const tradesRes = await db.execute({
      sql: "SELECT * FROM trades WHERE user_id = ? ORDER BY created_at ASC",
      args: [userId]
    });
    
    const userRes = await db.execute({
      sql: "SELECT initial_balance, prop_firm_enabled, prop_firm_balance FROM users WHERE id = ?",
      args: [userId]
    });
    
    let equity = 10000;
    if (userRes.rows.length > 0) {
      equity = userRes.rows[0].prop_firm_enabled ? (userRes.rows[0].prop_firm_balance || 10000) : (userRes.rows[0].initial_balance || 10000);
    }"""

replace_uls = """    let actualUserId = userId;
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
"""

content = content.replace(find_uls, replace_uls)


# Fix sendWeeklyReview
find_swr = """    const tradesRes = await db.execute({
      sql: "SELECT * FROM trades WHERE user_id = ? AND created_at >= ?",
      args: [userId, sevenDaysAgo.toISOString()]
    });"""

replace_swr = """    let actualUserId = userId;
    const userRes = await db.execute({ sql: "SELECT id FROM users WHERE id = ?", args: [actualUserId] });
    if (userRes.rows.length === 0) {
       const firstUser = await db.execute("SELECT id FROM users LIMIT 1");
       if (firstUser.rows.length > 0) actualUserId = firstUser.rows[0].id;
       else return;
    }

    const tradesRes = await db.execute({
      sql: "SELECT * FROM trades WHERE user_id = ? AND created_at >= ?",
      args: [actualUserId, sevenDaysAgo.toISOString()]
    });"""

content = content.replace(find_swr, replace_swr)

# Fix the recursive trigger call param
content = content.replace("await updateLiveStats(client, db, channels.liveStats, userId);", "await updateLiveStats(client, db, channels.liveStats, actualUserId);")

with open('src/lib/discord.ts', 'w') as f:
    f.write(content)
