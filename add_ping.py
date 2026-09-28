import re

with open('server.ts', 'r') as f:
    content = f.read()

find = """  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server running on http://localhost:${PORT}`);
  });"""

replace = """  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server running on http://localhost:${PORT}`);
    
    // Telegram Keep-Alive / Anti-Cold Start
    setInterval(() => {
      try {
        fetch(`http://localhost:${PORT}/api/health`).catch(() => {});
      } catch (e) {}
    }, 4 * 60 * 1000); // ping every 4 mins
  });"""

content = content.replace(find, replace)

find2 = """const PORT = 3000;"""
replace2 = """const PORT = 3000;
app.get("/api/health", (req, res) => res.json({ status: "ok" }));"""
content = content.replace(find2, replace2)

with open('server.ts', 'w') as f:
    f.write(content)
