import re

with open('src/App.tsx', 'r') as f:
    content = f.read()

find_effect = """  useEffect(() => {
    if (user) {
      fetchTrades();
    }
  }, [user]);"""

replace_effect = """  useEffect(() => {
    if (user) {
      fetchTrades();
      // Auto-refresh to get trades from Discord bot instantly
      const interval = setInterval(() => {
        fetchTrades();
      }, 5000);
      return () => clearInterval(interval);
    }
  }, [user]);"""

content = content.replace(find_effect, replace_effect)

with open('src/App.tsx', 'w') as f:
    f.write(content)
