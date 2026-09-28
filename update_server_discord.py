import re

with open('server.ts', 'r') as f:
    content = f.read()

# Import the discord bot initializer
if 'import { initDiscordBot }' not in content:
    content = content.replace(
        'import cookieParser from "cookie-parser";',
        'import cookieParser from "cookie-parser";\nimport { initDiscordBot } from "./src/lib/discord.js";'
    )

# Call it after DB init
init_db_marker = 'const dbConfig: any = { url: dbUrl };'
if 'initDiscordBot(db)' not in content:
    # Need to find the exact place `export const db = createClient(dbConfig);` happens
    db_init_str = "export const db = createClient(dbConfig);\n"
    if db_init_str in content:
        content = content.replace(db_init_str, db_init_str + "\n// Initialize Discord Bot\ninitDiscordBot(db);\n")
    else:
        # Just in case
        db_init_str = "export const db = createClient(dbConfig);"
        content = content.replace(db_init_str, db_init_str + "\n// Initialize Discord Bot\ninitDiscordBot(db);\n")

with open('server.ts', 'w') as f:
    f.write(content)
