import re

with open('src/lib/discord.ts', 'r') as f:
    content = f.read()

find = "let currentBalance = isProp ? (userRes.rows[0].prop_firm_balance || 10000) : (userRes.rows[0].initial_balance || 10000);"
replace = "let currentBalance = isProp ? (userRes.rows[0].prop_firm_balance || 10000) : (userRes.rows[0].initial_balance || userRes.rows[0].balance || 10000);"
content = content.replace(find, replace)

# also fix the select to include `balance`
find_select = "SELECT id, current_mode, prop_firm_enabled, prop_firm_balance, initial_balance FROM users"
replace_select = "SELECT id, current_mode, prop_firm_enabled, prop_firm_balance, initial_balance, balance FROM users"
content = content.replace(find_select, replace_select)

with open('src/lib/discord.ts', 'w') as f:
    f.write(content)
