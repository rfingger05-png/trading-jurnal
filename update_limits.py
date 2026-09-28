import re

with open('src/components/Dashboard.tsx', 'r') as f:
    content = f.read()

find_daily = """<span className="text-[9px] uppercase tracking-widest font-bold text-slate-400">Limit: {user?.prop_firm_daily_dd || 5}%</span>"""
replace_daily = """<span className="text-[9px] uppercase tracking-widest font-bold text-slate-400">Limit: {user?.prop_firm_daily_dd || 5}% ({formatCurrency(dailyDDAmount, user?.currency)})</span>"""
content = content.replace(find_daily, replace_daily)

find_max = """<span className="text-[9px] uppercase tracking-widest font-bold text-slate-400">Limit: {user?.prop_firm_max_dd || 10}%</span>"""
replace_max = """<span className="text-[9px] uppercase tracking-widest font-bold text-slate-400">Limit: {user?.prop_firm_max_dd || 10}% ({formatCurrency(maxDDAmount, user?.currency)})</span>"""
content = content.replace(find_max, replace_max)

with open('src/components/Dashboard.tsx', 'w') as f:
    f.write(content)

