import { createClient } from "@libsql/client";
import dotenv from "dotenv";
dotenv.config();
const db = createClient({ url: process.env.TURSO_DATABASE_URL || process.env.TURSO_URL, authToken: process.env.TURSO_AUTH_TOKEN });
async function run() {
  try {
    // Clean zombie trades
    await db.execute("DELETE FROM trades WHERE user_id IS NULL OR pair IS NULL;");
    console.log("Deleted zombie trades.");
    
    // Set balance back to 1000
    await db.execute("UPDATE users SET initial_balance = 1000, balance = 1000, prop_firm_balance = 1000 WHERE username = 'singgahrang@gmail.com';");
    console.log("Reset balance for user to 1000.");
  } catch(e) {
    console.error(e);
  }
}
run();
