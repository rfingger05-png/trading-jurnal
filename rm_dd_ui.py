import re

with open('src/components/Dashboard.tsx', 'r') as f:
    content = f.read()

pattern = r"\{/\* Drawdown & Prop Firm Metrics \*/\}.*?(?=\{/\* Heat Map Section \(30 Days with Dates\) \*/\})"
new_content = re.sub(pattern, "", content, flags=re.DOTALL)

with open('src/components/Dashboard.tsx', 'w') as f:
    f.write(new_content)
