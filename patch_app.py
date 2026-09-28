import re

with open('src/App.tsx', 'r') as f:
    content = f.read()

content = content.replace(
    "<Dashboard trades={trades} user={user} />",
    "<Dashboard trades={trades} user={user} transactions={transactions} />"
)

with open('src/App.tsx', 'w') as f:
    f.write(content)

