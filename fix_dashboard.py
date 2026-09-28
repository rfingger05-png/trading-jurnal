import re

with open('src/components/Dashboard.tsx', 'r') as f:
    content = f.read()

# Fix Total Trades & Win Rate
find_stats = """  const wins = trades.filter(t => t.result === 'Win').length;
  const losses = trades.filter(t => t.result === 'Loss').length;
  const totalCompleted = wins + losses;
  const winRate = totalCompleted > 0 
    ? Math.round((wins / totalCompleted) * 100) 
    : 0;"""

replace_stats = """  const wins = trades.filter(t => t.result && t.result.toLowerCase() === 'win').length;
  const totalCompleted = trades.length;
  const winRate = totalCompleted > 0 
    ? Math.round((wins / totalCompleted) * 100) 
    : 0;"""
content = content.replace(find_stats, replace_stats)

# Fix HeatMap Day logic to include 'WIN' uppercase
find_heatmap = """      if (dayTrades.length > 0) {
        const dWins = dayTrades.filter(t => t.result === 'Win').length;
        wr = dWins / dayTrades.length;
      }"""
replace_heatmap = """      if (dayTrades.length > 0) {
        const dWins = dayTrades.filter(t => t.result && t.result.toLowerCase() === 'win').length;
        wr = dWins / dayTrades.length;
      }"""
content = content.replace(find_heatmap, replace_heatmap)

# Fix Drawdowns
find_dd = """  // Prop Firm Daily DD is usually X% of starting balance OR start of day balance. 
  // We use X% of starting balance as the max loss amount for the day.
  const dailyDDAmount = startingBalance * ((user?.prop_firm_daily_dd || 5) / 100);
  const dailyDDViolationPoint = startOfDayEquity - dailyDDAmount;
  const dailyDDRemaining = currentEquity - dailyDDViolationPoint;
  
  // Trailing Max Drawdown: Trails the peak equity by X% of starting balance
  const maxDDAmount = startingBalance * ((user?.prop_firm_max_dd || 10) / 100);
  const maxDDViolationPoint = peakEquity - maxDDAmount;
  
  // If it's a fixed max drawdown (not trailing), it would just be startingBalance - maxDDAmount.
  // We will use trailing since the user specifically requested trailing DD logic.
  const maxDDRemaining = currentEquity - maxDDViolationPoint;"""

replace_dd = """  // Fixed Daily Drawdown Limit = Initial Balance * 5% = $50.00
  const dailyDDAmount = startingBalance * ((user?.prop_firm_daily_dd || 5) / 100);
  const dailyDDViolationPoint = startOfDayEquity - dailyDDAmount;
  const dailyDDRemaining = currentEquity - dailyDDViolationPoint;
  
  // Fixed Max Drawdown Limit = Initial Balance * 10% = $100.00
  const maxDDAmount = startingBalance * ((user?.prop_firm_max_dd || 10) / 100);
  // User requested fixed max drawdown limit based on initial balance (not trailing peak)
  const maxDDViolationPoint = startingBalance - maxDDAmount;
  const maxDDRemaining = currentEquity - maxDDViolationPoint;"""
content = content.replace(find_dd, replace_dd)

# Replace other occurrences of 'Win' for robustness
content = content.replace("t.result === 'Win'", "t.result && t.result.toLowerCase() === 'win'")
content = content.replace("t.result === 'Loss'", "t.result && t.result.toLowerCase() === 'loss'")

with open('src/components/Dashboard.tsx', 'w') as f:
    f.write(content)

