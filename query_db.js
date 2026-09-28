import { createClient } from '@libsql/client';

const db = createClient({ url: "file:local.db" });

async function run() {
  const res = await db.execute("SELECT id, created_at FROM trades LIMIT 5;");
  console.log(res.rows);
}
run();
