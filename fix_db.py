with open('server.ts', 'r') as f:
    content = f.read()

# Add target_balance to users table
target = "discord_id TEXT,"
replacement = "discord_id TEXT,\\n        target_balance REAL DEFAULT 1000000,"

if target in content and "target_balance" not in content:
    content = content.replace(target, replacement)
    
    # also add ALTER TABLE just in case
    alter_sql = """
    // Add target_balance column if it doesn't exist
    try {
      await db.execute('ALTER TABLE users ADD COLUMN target_balance REAL DEFAULT 1000000');
    } catch (e) { /* ignore if exists */ }
"""
    content = content.replace("async function initDb() {\\n  try {", "async function initDb() {\\n  try {" + alter_sql)
    
    with open('server.ts', 'w') as f:
        f.write(content)
        print("Updated server.ts DB schema")
else:
    print("Already updated or target not found")
