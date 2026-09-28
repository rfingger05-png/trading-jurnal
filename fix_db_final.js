import { createClient } from "@libsql/client";
import dotenv from "dotenv";
dotenv.config();
const db = createClient({ url: process.env.TURSO_DATABASE_URL || process.env.TURSO_URL, authToken: process.env.TURSO_AUTH_TOKEN });
async function run() {
  try {
    // Note: the column name for email is 'username' in this schema
    await db.execute("UPDATE users SET discord_id = '1540377868402692207', initial_balance = 1000, balance = 1000, prop_firm_balance = 1000 WHERE username = 'singgahrang@gmail.com'");
    const res = await db.execute("SELECT id, username, discord_id, initial_balance, balance, prop_firm_balance FROM users WHERE username = 'singgahrang@gmail.com'");
    console.log("Updated user:", res.rows);
    
    await db.execute("DELETE FROM trades");
    console.log("Trades table truncated.");
  } catch (e) {
    console.error(e);
  }
}
run();
