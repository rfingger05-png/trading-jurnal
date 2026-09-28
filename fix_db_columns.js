import { createClient } from "@libsql/client";
import dotenv from "dotenv";
dotenv.config();

const db = createClient({
  url: process.env.TURSO_DATABASE_URL || "https://jurnal-tryout-lancarkoreaa.aws-ap-northeast-1.turso.io",
  authToken: process.env.TURSO_AUTH_TOKEN || "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3NzcyMDMwMDksImlkIjoiMDE5ZDM4MmItZjAwMS03MjlhLTliZjctODQzMGE5NjNjZGY2IiwicmlkIjoiYzRlYzU4MzctOGNhOC00NzBiLTliM2UtYjIwNDkwMDAzNmVhIn0.Ir8xBR4mR7fYLnj6HbSzsHptQjAbfygNHzY6rIRVd3t1qMa7Ktn7dXOklnNDwWg-_nom1XinUpauQRGkciWeAQ"
});

async function run() {
  try {
    await db.execute("ALTER TABLE trades ADD COLUMN image_url TEXT");
    console.log("Added image_url column");
  } catch (e) {
    console.log("image_url might exist:", e.message);
  }
  
  try {
    await db.execute("ALTER TABLE trades ADD COLUMN has_image INTEGER DEFAULT 0");
    console.log("Added has_image column");
  } catch (e) {
    console.log("has_image might exist:", e.message);
  }
}
run();
