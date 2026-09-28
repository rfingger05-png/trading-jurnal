import { createClient } from "@libsql/client";
import dotenv from "dotenv";
dotenv.config();
const db = createClient({ url: process.env.TURSO_DATABASE_URL || process.env.TURSO_URL, authToken: process.env.TURSO_AUTH_TOKEN });
async function run() {
  try {
    // Add telegram_id column if it doesn't exist
    try {
      await db.execute("ALTER TABLE users ADD COLUMN telegram_id TEXT");
      console.log("Added telegram_id column.");
    } catch(e) {
      console.log("telegram_id column might already exist.");
    }
    
    // For mapping, we will rely on TELEGRAM_USER_ID from env, but let's pre-map a placeholder or if it's already provided.
    const telId = process.env.TELEGRAM_USER_ID || 'PLACEHOLDER_TELEGRAM_ID';
    await db.execute({
        sql: "UPDATE users SET telegram_id = ?, initial_balance = 1000, balance = 1000, prop_firm_balance = 1000 WHERE username = 'singgahrang@gmail.com'",
        args: [telId]
    });
    
    console.log("Balance reset and mapped to " + telId);
    
    await db.execute("DELETE FROM trades");
    console.log("Trades table truncated.");
    
  } catch (e) {
    console.error(e);
  }
}
run();
