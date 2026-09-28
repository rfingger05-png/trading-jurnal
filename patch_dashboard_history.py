import re

with open('src/components/Dashboard.tsx', 'r') as f:
    content = f.read()

# I will add a Recent Transactions table below the financial summary
old_ui = """        {/* Financial Sync Info */}
        <div className="grid grid-cols-2 gap-4">
           <div className="bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-100 dark:border-emerald-800 p-4 shadow-sm flex flex-col items-center justify-center">
              <h3 className="text-[10px] font-bold uppercase tracking-widest text-emerald-600 dark:text-emerald-500 mb-1">Total Deposits</h3>
              <p className="text-xl font-light text-emerald-700 dark:text-emerald-400">{formatCurrency(totalDeposits, user?.currency)}</p>
           </div>
           <div className="bg-red-50 dark:bg-red-900/20 border border-red-100 dark:border-red-800 p-4 shadow-sm flex flex-col items-center justify-center">
              <h3 className="text-[10px] font-bold uppercase tracking-widest text-red-600 dark:text-red-500 mb-1">Total Withdrawals</h3>
              <p className="text-xl font-light text-red-700 dark:text-red-400">{formatCurrency(totalWithdrawals, user?.currency)}</p>
           </div>
        </div>"""

new_ui = """        {/* Financial Sync Info */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
           <div className="flex flex-col space-y-4">
             <div className="bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-100 dark:border-emerald-800 p-4 shadow-sm flex flex-col items-center justify-center h-24">
                <h3 className="text-[10px] font-bold uppercase tracking-widest text-emerald-600 dark:text-emerald-500 mb-1">Total Deposits</h3>
                <p className="text-xl font-light text-emerald-700 dark:text-emerald-400">{formatCurrency(totalDeposits, user?.currency)}</p>
             </div>
             <div className="bg-red-50 dark:bg-red-900/20 border border-red-100 dark:border-red-800 p-4 shadow-sm flex flex-col items-center justify-center h-24">
                <h3 className="text-[10px] font-bold uppercase tracking-widest text-red-600 dark:text-red-500 mb-1">Total Withdrawals</h3>
                <p className="text-xl font-light text-red-700 dark:text-red-400">{formatCurrency(totalWithdrawals, user?.currency)}</p>
             </div>
           </div>
           
           <div className="bg-white dark:bg-neutral-900 border border-slate-200 dark:border-neutral-800 p-4 shadow-sm flex flex-col h-52">
              <h3 className="text-[10px] font-bold uppercase tracking-widest text-slate-400 mb-3">Recent Transactions</h3>
              <div className="flex-1 overflow-y-auto pr-2">
                {transactions.length === 0 ? (
                   <p className="text-xs text-slate-400 text-center mt-8">No transactions yet.</p>
                ) : (
                   <ul className="space-y-3">
                     {[...transactions].reverse().map(tx => (
                        <li key={tx.id} className="flex justify-between items-center text-xs border-b border-slate-100 dark:border-neutral-800 pb-2">
                          <div>
                            <span className={tx.type === 'deposit' ? 'text-emerald-600 font-bold uppercase' : 'text-red-500 font-bold uppercase'}>{tx.type}</span>
                            <span className="text-[9px] text-slate-400 ml-2">{format(new Date(tx.created_at), 'dd MMM yyyy')}</span>
                          </div>
                          <span className={tx.type === 'deposit' ? 'text-emerald-700' : 'text-red-600'}>
                            {tx.type === 'deposit' ? '+' : '-'}{formatCurrency(tx.amount, user?.currency)}
                          </span>
                        </li>
                     ))}
                   </ul>
                )}
              </div>
           </div>
        </div>"""

content = content.replace(old_ui, new_ui)

with open('src/components/Dashboard.tsx', 'w') as f:
    f.write(content)

