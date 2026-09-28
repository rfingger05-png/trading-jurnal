import re

with open('src/components/Dashboard.tsx', 'r') as f:
    content = f.read()

find = """  const chartData = useMemo(() => {
    if (completedTrades.length === 0) return [];
    let runningPL = 0;
    return [
      {
        date: 'Start',
        fullDate: 'Initial Balance',
        pnl: 0
      },
      ...completedTrades.map(t => {
        runningPL += (t.realized_pl || 0);
        return {
          date: format(parseDateStr(t.created_at), 'MMM dd'),
          fullDate: format(parseDateStr(t.created_at), 'MMM dd, yyyy HH:mm'),
          pnl: runningPL
        };
      })
    ];
  }, [completedTrades]);"""

replace = """  const chartData = useMemo(() => {
    if (completedTrades.length === 0) return [];
    let runningPL = 0;
    const initialBal = user?.prop_firm_enabled ? (user.prop_firm_balance || 1000) : (user?.initial_balance || 1000);
    return [
      {
        date: 'Start',
        fullDate: 'Initial Balance',
        pnl: initialBal
      },
      ...completedTrades.map(t => {
        runningPL += (t.realized_pl || 0);
        return {
          date: format(parseDateStr(t.created_at), 'MMM dd'),
          fullDate: format(parseDateStr(t.created_at), 'MMM dd, yyyy HH:mm'),
          pnl: initialBal + runningPL
        };
      })
    ];
  }, [completedTrades, user]);"""

content = content.replace(find, replace)

# I should also fix the Tooltip formatting if it assumes it's PNL instead of equity.
find_tooltip = """const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white dark:bg-neutral-900 border border-slate-200 dark:border-neutral-800 p-3 shadow-lg text-xs">
          <p className="font-bold text-slate-800 dark:text-neutral-200 mb-1">{payload[0].payload.fullDate}</p>
          <p className={payload[0].value >= 0 ? "text-emerald-500 font-bold" : "text-red-500 font-bold"}>
            {payload[0].value >= 0 ? '+' : ''}{formatCurrency(payload[0].value, user?.currency)}
          </p>
        </div>
      );
    }
    return null;
  };"""

replace_tooltip = """const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const initialBal = user?.prop_firm_enabled ? (user.prop_firm_balance || 1000) : (user?.initial_balance || 1000);
      const isProfit = payload[0].value >= initialBal;
      return (
        <div className="bg-white dark:bg-neutral-900 border border-slate-200 dark:border-neutral-800 p-3 shadow-lg text-xs">
          <p className="font-bold text-slate-800 dark:text-neutral-200 mb-1">{payload[0].payload.fullDate}</p>
          <p className={isProfit ? "text-emerald-500 font-bold" : "text-red-500 font-bold"}>
            Equity: {formatCurrency(payload[0].value, user?.currency)}
          </p>
        </div>
      );
    }
    return null;
  };"""

content = content.replace(find_tooltip, replace_tooltip)

with open('src/components/Dashboard.tsx', 'w') as f:
    f.write(content)

