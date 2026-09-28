import re

with open('src/lib/telegram.ts', 'r') as f:
    content = f.read()

old_menu_text = "• /report - Export jurnal (CSV)`"
new_menu_text = "• /report - Export jurnal (CSV)\\n• /deposit [jml] - Catat Deposit\\n• /withdraw [jml] - Catat Withdraw\\n• /news - Kalender Ekonomi (USD)`"

if old_menu_text in content:
    content = content.replace(old_menu_text, new_menu_text)
    with open('src/lib/telegram.ts', 'w') as f:
        f.write(content)
        print("Menu updated.")
