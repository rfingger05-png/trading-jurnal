import { createClient } from "@libsql/client";
import dotenv from "dotenv";
dotenv.config();
const db = createClient({ url: process.env.TURSO_DATABASE_URL || process.env.TURSO_URL, authToken: process.env.TURSO_AUTH_TOKEN });
async function run() {
  try {
    const check = await db.execute("SELECT * FROM users WHERE username = 'singgahrang@gmail.com'");
    if (check.rows.length === 0) {
      await db.execute("INSERT INTO users (username, password, role, discord_id) VALUES ('singgahrang@gmail.com', 'dummy_hash', 'user', '1540377868402692207')");
      console.log("Inserted singgahrang@gmail.com with discord_id");
    } else {
      await db.execute("UPDATE users SET discord_id = '1540377868402692207' WHERE username = 'singgahrang@gmail.com'");
      console.log("Updated singgahrang@gmail.com with discord_id");
    }
    const res = await db.execute("SELECT id, username, discord_id FROM users");
    console.log("Users:", res.rows);
  } catch (e) {
    console.error(e);
  }
}
run();
