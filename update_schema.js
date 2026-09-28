import { createClient } from "@libsql/client";
import dotenv from "dotenv";
dotenv.config();
const db = createClient({ url: process.env.TURSO_DATABASE_URL || process.env.TURSO_URL, authToken: process.env.TURSO_AUTH_TOKEN });
async function run() {
  try {
    await db.execute("ALTER TABLE users ADD COLUMN discord_id TEXT");
    console.log("Added discord_id to users");
  } catch (e) {
    console.log("Column may already exist:", e.message);
  }
}
run();
