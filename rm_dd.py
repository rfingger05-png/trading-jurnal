import re

with open('src/components/Dashboard.tsx', 'r') as f:
    content = f.read()

find = """        {/* Drawdown & Prop Firm Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className={cn("bg-white dark:bg-neutral-900 border p-6 flex flex-col gap-4 shadow-sm transition-colors", dailyDDRemaining <= 0 ? "border-red-500 bg-red-50/50 dark:bg-red-950/20 shadow-red-500/20" : "border-slate-200 dark:border-neutral-800")}>
             <div className="flex justify-between items-center">
               <h3 className={cn("text-[10px] font-bold uppercase tracking-widest", dailyDDRemaining <= 0 ? "text-red-600 dark:text-red-400" : "text-slate-400")}>Daily Drawdown</h3>
               <span className="text-[9px] uppercase tracking-widest font-bold text-slate-400">Limit: {user?.prop_firm_daily_dd || 5}% ({formatCurrency(dailyDDAmount, user?.currency)})</span>
             </div>
             <div className="flex justify-between items-end">
               <div>
                 <div className={cn("text-2xl font-black tracking-tighter", dailyDDRemaining <= 0 ? "text-red-600 dark:text-red-400" : "text-slate-900 dark:text-neutral-100")}>
                   {formatCurrency(dailyDDRemaining, user?.currency)}
                 </div>
                 <div className={cn("text-xs font-bold mt-1", dailyDDRemaining <= 0 ? "text-red-500" : "text-slate-500")}>{dailyDDRemaining <= 0 ? "Account Violated" : "Remaining until violation"}</div>
               </div>
               <div className="text-right">
                 <div className={cn("text-sm font-bold", totalPLToday >= 0 ? "text-emerald-500" : "text-red-500")}>
                   {totalPLToday > 0 ? '+' : ''}{formatCurrency(totalPLToday, user?.currency)}
                 </div>
                 <div className="text-[10px] text-slate-400 uppercase tracking-widest">Today's P/L</div>
               </div>
             </div>
             <div className="w-full bg-slate-100 dark:bg-neutral-800 h-2 mt-2 rounded-full overflow-hidden">
                <div 
                  className={cn("h-full transition-all duration-500", totalPLToday < 0 && Math.abs(totalPLToday) > dailyDDAmount * 0.8 ? "bg-red-500" : "bg-emerald-500")} 
                  style={{ width: `${Math.min(100, Math.max(0, (totalPLToday < 0 ? Math.abs(totalPLToday) : 0) / dailyDDAmount * 100))}%` }}
                ></div>
             </div>
          </div>
          
          <div className={cn("bg-white dark:bg-neutral-900 border p-6 flex flex-col gap-4 shadow-sm transition-colors", maxDDRemaining <= 0 ? "border-red-500 bg-red-50/50 dark:bg-red-950/20 shadow-red-500/20" : "border-slate-200 dark:border-neutral-800")}>
             <div className="flex justify-between items-center">
               <h3 className={cn("text-[10px] font-bold uppercase tracking-widest", maxDDRemaining <= 0 ? "text-red-600 dark:text-red-400" : "text-slate-400")}>Max Drawdown</h3>
               <span className="text-[9px] uppercase tracking-widest font-bold text-slate-400">Limit: {user?.prop_firm_max_dd || 10}% ({formatCurrency(maxDDAmount, user?.currency)})</span>
             </div>
             <div className="flex justify-between items-end">
               <div>
                 <div className={cn("text-2xl font-black tracking-tighter", maxDDRemaining <= 0 ? "text-red-600 dark:text-red-400" : "text-slate-900 dark:text-neutral-100")}>
                   {formatCurrency(maxDDRemaining, user?.currency)}
                 </div>
                 <div className={cn("text-xs font-bold mt-1", maxDDRemaining <= 0 ? "text-red-500" : "text-slate-500")}>{maxDDRemaining <= 0 ? "Account Violated" : "Remaining until violation"}</div>
               </div>
               <div className="text-right">
                 <div className={cn("text-sm font-bold text-slate-700 dark:text-neutral-300")}>
                   {formatCurrency(maxDrawdown, user?.currency)}
                 </div>
                 <div className="text-[10px] text-slate-400 uppercase tracking-widest" title="The maximum actual drawdown your account has experienced so far">Actual Max DD</div>
               </div>
             </div>
             <div className="w-full bg-slate-100 dark:bg-neutral-800 h-2 mt-2 rounded-full overflow-hidden">
                <div 
                  className={cn("h-full transition-all duration-500", (maxDrawdown / maxDDAmount) > 0.8 ? "bg-red-500" : "bg-emerald-500")}
                  style={{ width: `${Math.min(100, (maxDrawdown / maxDDAmount) * 100)}%` }}
                ></div>
             </div>
          </div>
        </div>"""

replace = ""
content = content.replace(find, replace)

with open('src/components/Dashboard.tsx', 'w') as f:
    f.write(content)
