import re

with open('src/components/Dashboard.tsx', 'r') as f:
    content = f.read()

pattern = r"  // Calculate Peak Equity for Trailing Drawdown.*?const profitTargetRemaining = profitTargetLimit - currentEquity;"
new_content = re.sub(pattern, "", content, flags=re.DOTALL)

with open('src/components/Dashboard.tsx', 'w') as f:
    f.write(new_content)
