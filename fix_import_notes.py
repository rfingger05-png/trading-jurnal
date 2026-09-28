import re

with open('src/components/ImportTradesModal.tsx', 'r') as f:
    content = f.read()

# 1. Add notes? to ImportTrade
content = content.replace("  risk_percentage?: number;\n};", "  risk_percentage?: number;\n  notes?: string;\n};")

# 2. Add `let notes = '';` to `processData` variables
content = content.replace(
    "let openTime = '';\n          let image = null;",
    "let openTime = '';\n          let image = null;\n          let notes = '';"
)

# 3. Add notes extraction condition
extract_find = """            else if (kl.includes('image') || kl.includes('gallery')) {
               image = val;
            }"""
extract_replace = """            else if (kl.includes('image') || kl.includes('gallery')) {
               image = val;
            }
            else if (kl.includes('reason') || kl.includes('note') || kl.includes('desc')) {
               notes = val;
            }"""
content = content.replace(extract_find, extract_replace)

# 4. Push notes to trades.push()
push_find = """          trades.push({
            pair,
            created_at: dateStr,
            direction,
            position_size: size,
            entry_price: entry,
            sl,
            tp,
            realized_pl: profit,
            result,
            setup_name: 'BRG',
            nominal_risk: nominalRisk,
            risk_percentage: riskPercentage,
            account_balance: accountBalance,
            image: image || importImage
          });"""
push_replace = """          trades.push({
            pair,
            created_at: dateStr,
            direction,
            position_size: size,
            entry_price: entry,
            sl,
            tp,
            realized_pl: profit,
            result,
            setup_name: 'BRG',
            nominal_risk: nominalRisk,
            risk_percentage: riskPercentage,
            account_balance: accountBalance,
            image: image || importImage,
            notes: notes || 'No reason provided.'
          });"""
content = content.replace(push_find, push_replace)

with open('src/components/ImportTradesModal.tsx', 'w') as f:
    f.write(content)
