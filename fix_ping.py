import re

with open('server.ts', 'r') as f:
    content = f.read()

content = content.replace(
    'app.get("/ping", (req, res) => res.json({ status: "alive" }));',
    "app.get('/ping', (req, res) => res.status(200).send('OK'));"
)

with open('server.ts', 'w') as f:
    f.write(content)
