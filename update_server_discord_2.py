import re

with open('server.ts', 'r') as f:
    content = f.read()

db_init_str = "const db = createClient(dbConfig);"
if 'initDiscordBot(db)' not in content:
    content = content.replace(db_init_str, db_init_str + "\n// Initialize Discord Bot\ninitDiscordBot(db);\n")

with open('server.ts', 'w') as f:
    f.write(content)
