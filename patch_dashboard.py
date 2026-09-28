import re

with open('src/components/Dashboard.tsx', 'r') as f:
    content = f.read()

# Update import
content = content.replace("import { Trade, User } from '../types';", "import { Trade, User, Transaction } from '../types';")

# Update component signature
content = content.replace(
    "export default function Dashboard({ trades, user }: { trades: Trade[], user?: User | null }) {",
    "export default function Dashboard({ trades, user, transactions = [] }: { trades: Trade[], user?: User | null, transactions?: Transaction[] }) {"
)

# Insert transaction total UI below the main stats or near them
# Let's find a good spot.
# There is a block for "Net P/L". I'll add "Total Deposit" and "Total Withdrawal" next to it.
old_stats = """        <div className="bg-white dark:bg-neutral-900 border border-slate-200 dark:border-neutral-800 p-5 shadow-sm">
          <h3 className="text-[10px] font-bold uppercase tracking-widest text-slate-400 mb-1">Net P/L</h3>"""

new_stats = """        <div className="bg-white dark:bg-neutral-900 border border-slate-200 dark:border-neutral-800 p-5 shadow-sm">
          <h3 className="text-[10px] font-bold uppercase tracking-widest text-slate-400 mb-1">Net P/L</h3>"""

# Wait, let's just add it as a new grid element or within the same grid.
grid_start = """      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">"""

# Better to add a small section at the bottom for "Financial History"
old_return = """  return (
    <div className="flex-1 flex flex-col h-full min-h-0 bg-white dark:bg-neutral-900 border border-slate-200 dark:border-neutral-800">
      <div className="p-4 border-b border-slate-100 dark:border-neutral-800 flex justify-between items-center shrink-0">
        <h3 className="text-[10px] font-bold uppercase tracking-widest text-slate-400">Trading Overview</h3>
      </div>
      
      <div className="flex-1 overflow-auto p-4 md:p-6 bg-slate-50 dark:bg-neutral-950/50 space-y-6">"""

content = content.replace(old_return, """  const totalDeposits = transactions.filter(t => t.type === 'deposit').reduce((acc, t) => acc + t.amount, 0);
  const totalWithdrawals = transactions.filter(t => t.type === 'withdrawal').reduce((acc, t) => acc + t.amount, 0);

  return (
    <div className="flex-1 flex flex-col h-full min-h-0 bg-white dark:bg-neutral-900 border border-slate-200 dark:border-neutral-800">
      <div className="p-4 border-b border-slate-100 dark:border-neutral-800 flex justify-between items-center shrink-0">
        <h3 className="text-[10px] font-bold uppercase tracking-widest text-slate-400">Trading Overview</h3>
      </div>
      
      <div className="flex-1 overflow-auto p-4 md:p-6 bg-slate-50 dark:bg-neutral-950/50 space-y-6">
        
        {/* Financial Sync Info */}
        <div className="grid grid-cols-2 gap-4">
           <div className="bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-100 dark:border-emerald-800 p-4 shadow-sm flex flex-col items-center justify-center">
              <h3 className="text-[10px] font-bold uppercase tracking-widest text-emerald-600 dark:text-emerald-500 mb-1">Total Deposits</h3>
              <p className="text-xl font-light text-emerald-700 dark:text-emerald-400">{formatCurrency(totalDeposits, user?.currency)}</p>
           </div>
           <div className="bg-red-50 dark:bg-red-900/20 border border-red-100 dark:border-red-800 p-4 shadow-sm flex flex-col items-center justify-center">
              <h3 className="text-[10px] font-bold uppercase tracking-widest text-red-600 dark:text-red-500 mb-1">Total Withdrawals</h3>
              <p className="text-xl font-light text-red-700 dark:text-red-400">{formatCurrency(totalWithdrawals, user?.currency)}</p>
           </div>
        </div>
""")

with open('src/components/Dashboard.tsx', 'w') as f:
    f.write(content)

