import re

with open('src/components/Dashboard.tsx', 'r') as f:
    content = f.read()

find_dd = """  const tradesToday = trades.filter(t => t.result !== 'Pending' && isSameDay(parseDateStr(t.created_at), today));
  const totalPLToday = tradesToday.reduce((acc, t) => acc + (t.realized_pl || 0), 0);
  const startOfDayEquity = currentEquity - totalPLToday;
  
  // Fixed Daily Drawdown Limit = Initial Balance * 5% = $50.00
  const dailyDDAmount = startingBalance * ((user?.prop_firm_daily_dd || 5) / 100);
  const dailyDDViolationPoint = startOfDayEquity - dailyDDAmount;
  const dailyDDRemaining = currentEquity - dailyDDViolationPoint;
  
  // Fixed Max Drawdown Limit = Initial Balance * 10% = $100.00
  const maxDDAmount = startingBalance * ((user?.prop_firm_max_dd || 10) / 100);
  // User requested fixed max drawdown limit based on initial balance (not trailing peak)
  const maxDDViolationPoint = startingBalance - maxDDAmount;
  const maxDDRemaining = currentEquity - maxDDViolationPoint;"""

replace_dd = """  const tradesToday = trades.filter(t => t.result !== 'Pending' && isSameDay(parseDateStr(t.created_at), today));
  const totalPLToday = tradesToday.reduce((acc, t) => acc + (t.realized_pl || 0), 0);
  const startOfDayEquity = currentEquity - totalPLToday;
  
  // Find Peak Equity specifically for Today (for Daily Trailing DD)
  let peakToday = startOfDayEquity;
  let runningToday = startOfDayEquity;
  [...tradesToday]
    .sort((a, b) => parseDateStr(a.created_at).getTime() - parseDateStr(b.created_at).getTime())
    .forEach(t => {
      runningToday += (t.realized_pl || 0);
      if (runningToday > peakToday) peakToday = runningToday;
    });
  
  // Trailing Daily Drawdown Limit = Trails from Today's Peak Equity
  const dailyDDAmount = startingBalance * ((user?.prop_firm_daily_dd || 5) / 100);
  const dailyDDViolationPoint = peakToday - dailyDDAmount;
  const dailyDDRemaining = currentEquity - dailyDDViolationPoint;
  
  // Trailing Max Drawdown Limit = Trails from All-Time Peak Equity (High Watermark)
  const maxDDAmount = startingBalance * ((user?.prop_firm_max_dd || 10) / 100);
  const maxDDViolationPoint = peakEquity - maxDDAmount;
  const maxDDRemaining = currentEquity - maxDDViolationPoint;"""

content = content.replace(find_dd, replace_dd)

with open('src/components/Dashboard.tsx', 'w') as f:
    f.write(content)

