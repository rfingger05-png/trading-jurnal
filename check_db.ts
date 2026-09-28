import { createClient } from "@libsql/client";
import dotenv from "dotenv";
dotenv.config();

const dbUrl = process.env.TURSO_URL || "https://jurnal-tryout-lancarkoreaa.aws-ap-northeast-1.turso.io";
const dbAuthToken = process.env.TURSO_AUTH_TOKEN || "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3NzcyMDMwMDksImlkIjoiMDE5ZDM4MmItZjAwMS03MjlhLTliZjctODQzMGE5NjNjZGY2IiwicmlkIjoiYzRlYzU4MzctOGNhOC00NzBiLTliM2UtYjIwNDkwMDAzNmVhIn0.Ir8xBR4mR7fYLnj6HbSzsHptQjAbfygNHzY6rIRVd3t1qMa7Ktn7dXOklnNDwWg-_nom1XinUpauQRGkciWeAQ";
let url = dbUrl;
if (url.startsWith('libsql://')) url = url.replace('libsql://', 'https://');
const db = createClient({ url, authToken: dbAuthToken });

async function run() {
  try {
    const res = await db.execute("PRAGMA table_info(users)");
    console.log(res.rows);
  } catch (e) {
    console.error(e);
  }
}
run();
