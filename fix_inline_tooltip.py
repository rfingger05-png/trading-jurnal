import re

with open('src/components/Dashboard.tsx', 'r') as f:
    content = f.read()

find = """              <Tooltip 
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    return (
                      <div className="bg-black dark:bg-neutral-800 text-white dark:text-neutral-100 border dark:border-neutral-700 p-3 rounded-sm text-xs font-mono shadow-xl relative z-50">
                        <div className="text-slate-400 mb-1">{payload[0].payload.fullDate}</div>
                        <div className={payload[0].value >= 0 ? 'text-emerald-400' : 'text-red-400'}>
                          {payload[0].value >= 0 ? '+' : ''}{formatCurrency(payload[0].value, user?.currency)}
                        </div>
                      </div>
                    );
                  }
                  return null;
                }}
              />"""

replace = """              <Tooltip 
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const eq = payload[0].value;
                    const initialBal = user?.prop_firm_enabled ? (user.prop_firm_balance || 1000) : (user?.initial_balance || 1000);
                    return (
                      <div className="bg-black dark:bg-neutral-800 text-white dark:text-neutral-100 border dark:border-neutral-700 p-3 rounded-sm text-xs font-mono shadow-xl relative z-50">
                        <div className="text-slate-400 mb-1">{payload[0].payload.fullDate}</div>
                        <div className={eq >= initialBal ? 'text-emerald-400' : 'text-red-400'}>
                          Equity: {formatCurrency(eq, user?.currency)}
                        </div>
                      </div>
                    );
                  }
                  return null;
                }}
              />"""

content = content.replace(find, replace)

with open('src/components/Dashboard.tsx', 'w') as f:
    f.write(content)
