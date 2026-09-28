import { createClient } from "@libsql/client";
import dotenv from "dotenv";
dotenv.config();
const db = createClient({ url: process.env.TURSO_DATABASE_URL || process.env.TURSO_URL, authToken: process.env.TURSO_AUTH_TOKEN });
async function run() {
  try {
    await db.execute("UPDATE users SET discord_id = '1540377868402692207' WHERE username = 'singgahrang@gmail.com'");
    const res = await db.execute("SELECT id, username, discord_id FROM users");
    console.log("Users:", res.rows);
    
    await db.execute("DELETE FROM trades");
    console.log("Trades table truncated.");
  } catch (e) {
    console.error(e);
  }
}
run();
