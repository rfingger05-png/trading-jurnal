import React, { useMemo } from 'react';
import { Trade, User, Transaction } from '../types';
import { cn } from '../lib/utils';
import { format, subDays, startOfDay, isSameDay, differenceInDays } from 'date-fns';
import { formatCurrency } from '../utils';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

export default function Dashboard({ trades, user, transactions = [] }: { trades: Trade[], user?: User | null, transactions?: Transaction[] }) {

  const wins = trades.filter(t => t.result && t.result.toLowerCase() === 'win').length;
  const totalCompleted = trades.length;
  const winRate = totalCompleted > 0 
    ? Math.round((wins / totalCompleted) * 100) 
    : 0;

  const totalPL = trades.reduce((acc, t) => acc + (t.realized_pl || 0), 0);

  const today = startOfDay(new Date());
  
  const parseDateStr = (dateStr: string) => {
    if (!dateStr) return new Date();
    let d = new Date(dateStr);
    if (!isNaN(d.getTime())) return d;
    
    // Fallback for MT4/MT5 format: "YYYY.MM.DD HH:mm:ss"
    const cleanStr = dateStr.replace(/\./g, '-').replace(' ', 'T') + 'Z';
    d = new Date(cleanStr);
    if (!isNaN(d.getTime())) return d;
    
    return new Date();
  };

  const heatMapDays = useMemo(() => {
    const daysSinceStart = 29; // 30 days total
    const days = [];
    for (let i = 0; i <= daysSinceStart; i++) {
      const d = subDays(today, daysSinceStart - i);
      const dayTrades = trades.filter(t => {
        const tDate = startOfDay(parseDateStr(t.created_at));
        return isSameDay(tDate, d) && t.result !== 'Pending';
      });
      let wr = -1;
      if (dayTrades.length > 0) {
        const dWins = dayTrades.filter(t => t.result && t.result.toLowerCase() === 'win').length;
        wr = dWins / dayTrades.length;
      }
      days.push({ date: d, wr, count: dayTrades.length });
    }
    return days;
  }, [trades, today]);

  const getHeatMapColor = (wr: number) => {
    if (wr === -1) return 'bg-slate-100 dark:bg-neutral-950 text-slate-400 dark:text-neutral-600 border-slate-200 dark:border-neutral-800';
    if (wr === 0) return 'bg-red-500 text-white border-red-600';
    if (wr < 0.5) return 'bg-orange-400 text-white border-orange-500';
    if (wr === 0.5) return 'bg-yellow-400 text-neutral-900 border-yellow-500';
    if (wr < 1) return 'bg-emerald-400 text-neutral-900 border-emerald-500';
    return 'bg-emerald-700 text-white border-emerald-800'; // 100% wr dark green
  };

  const completedTrades = useMemo(() => trades.filter(t => t.result !== 'Pending').sort((a, b) => parseDateStr(a.created_at).getTime() - parseDateStr(b.created_at).getTime()), [trades]);

  const chartData = useMemo(() => {
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
  }, [completedTrades, user]);

  const pairStats = useMemo(() => {
     const stats: Record<string, { trades: number, wins: number, pnl: number }> = {};
     trades.forEach(t => {
       if (t.result === 'Pending') return;
       if (!stats[t.pair]) stats[t.pair] = { trades: 0, wins: 0, pnl: 0 };
       stats[t.pair].trades += 1;
       if (t.result && t.result.toLowerCase() === 'win') stats[t.pair].wins += 1;
       stats[t.pair].pnl += (t.realized_pl || 0);
     });
     return Object.entries(stats).map(([pair, data]) => ({
       pair,
       ...data,
       winRate: Math.round((data.wins / data.trades) * 100)
     })).sort((a, b) => b.pnl - a.pnl);
  }, [trades]);

  const setupStats = useMemo(() => {
     const stats: Record<string, { trades: number, wins: number, pnl: number }> = {};
     trades.forEach(t => {
       if (t.result === 'Pending') return;
       const setup = t.setup_name || 'Other';
       if (!stats[setup]) stats[setup] = { trades: 0, wins: 0, pnl: 0 };
       stats[setup].trades += 1;
       if (t.result && t.result.toLowerCase() === 'win') stats[setup].wins += 1;
       stats[setup].pnl += (t.realized_pl || 0);
     });
     return Object.entries(stats).map(([setup, data]) => ({
       setup,
       ...data,
       winRate: Math.round((data.wins / data.trades) * 100)
     })).sort((a, b) => b.pnl - a.pnl);
  }, [trades]);


  const { grossProfit, grossLoss, profitFactor, maxWinStreak, maxLossStreak, currentWinStreak, currentLossStreak } = useMemo(() => {
    let grossProfit = 0;
    let grossLoss = 0;
    let peak = 0;
    let maxDrawdown = 0;
    let runningPL = 0;
    let winCount = 0;
    let lossCount = 0;
    let currentWinStreak = 0;
    let currentLossStreak = 0;
    let maxWinStreak = 0;
    let maxLossStreak = 0;

    const sortedTrades = [...trades]
      .filter(t => t.result !== 'Pending')
      .sort((a, b) => parseDateStr(a.created_at).getTime() - parseDateStr(b.created_at).getTime());

    sortedTrades.forEach(t => {
      if (t.result && t.result.toLowerCase() === 'win') {
        grossProfit += (t.realized_pl || 0);
        winCount++;
        currentWinStreak++;
        currentLossStreak = 0;
        if (currentWinStreak > maxWinStreak) maxWinStreak = currentWinStreak;
      } else if (t.result && t.result.toLowerCase() === 'loss') {
        grossLoss += Math.abs(t.realized_pl || 0);
        lossCount++;
        currentLossStreak++;
        currentWinStreak = 0;
        if (currentLossStreak > maxLossStreak) maxLossStreak = currentLossStreak;
      } else {
        currentWinStreak = 0;
        currentLossStreak = 0;
      }
      
      runningPL += (t.realized_pl || 0);
      if (runningPL > peak) peak = runningPL;
      const drawdown = peak - runningPL;
      if (drawdown > maxDrawdown) maxDrawdown = drawdown;
    });

    const profitFactor = grossLoss > 0 ? (grossProfit / grossLoss).toFixed(2) : (grossProfit > 0 ? '∞' : '0.00');

    return { grossProfit, grossLoss, profitFactor, maxWinStreak, maxLossStreak, currentWinStreak, currentLossStreak };
  }, [trades]);

  const startingBalance = user?.prop_firm_enabled ? (user.prop_firm_balance || 1000) : (user?.initial_balance || 1000);
  const currentEquity = startingBalance + totalPL;




  // Day of Week Performance
  const dayStats = useMemo(() => {
    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    const acc: Record<string, { trades: number, wins: number, pnl: number }> = {};
    
    trades.forEach(t => {
      const date = parseDateStr(t.created_at);
      const dayName = days[date.getDay()];
      if (!acc[dayName]) acc[dayName] = { trades: 0, wins: 0, pnl: 0 };
      acc[dayName].trades += 1;
      if (t.result && t.result.toLowerCase() === 'win') acc[dayName].wins += 1;
      acc[dayName].pnl += (t.realized_pl || 0);
    });
    
    return ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'].map(day => {
      const data = acc[day] || { trades: 0, wins: 0, pnl: 0 };
      return {
        day,
        trades: data.trades,
        winRate: data.trades > 0 ? Math.round((data.wins / data.trades) * 100) : 0,
        pnl: data.pnl
      };
    });
  }, [trades]);

  // Session Performance (Asian 00-08, London 08-14, NY 14-22 UTC approx)
  const sessionStats = useMemo(() => {
    const acc: Record<string, { trades: number, wins: number, pnl: number }> = {
      'Asian (00:00 - 08:00)': { trades: 0, wins: 0, pnl: 0 },
      'London (08:00 - 13:00)': { trades: 0, wins: 0, pnl: 0 },
      'New York (13:00 - 22:00)': { trades: 0, wins: 0, pnl: 0 }
    };
    
    trades.forEach(t => {
      const date = parseDateStr(t.created_at);
      const hour = date.getHours();
      let session = 'Asian (00:00 - 08:00)';
      if (hour >= 8 && hour < 13) session = 'London (08:00 - 13:00)';
      else if (hour >= 13 && hour <= 22) session = 'New York (13:00 - 22:00)';
      
      acc[session].trades += 1;
      if (t.result && t.result.toLowerCase() === 'win') acc[session].wins += 1;
      acc[session].pnl += (t.realized_pl || 0);
    });
    
    return Object.entries(acc).map(([session, data]) => ({
      session,
      trades: data.trades,
      winRate: data.trades > 0 ? Math.round((data.wins / data.trades) * 100) : 0,
      pnl: data.pnl
    }));
  }, [trades]);

  return (
    <div className="flex-1 overflow-y-auto p-4 md:p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Top Stats */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className={cn("bg-white dark:bg-neutral-900 border p-4 shadow-sm relative overflow-hidden transition-colors", currentLossStreak >= 3 ? "border-red-500 bg-red-50/50 dark:bg-red-950/20" : "border-slate-200 dark:border-neutral-800")}>
            <div className={cn("text-[10px] uppercase font-bold tracking-widest mb-1", currentLossStreak >= 3 ? "text-red-600 dark:text-red-400" : "text-slate-400")}>Streak Tracker</div>
            {currentLossStreak >= 3 && <div className="absolute top-0 right-0 bg-red-500 text-white text-[8px] font-bold uppercase tracking-widest px-2 py-1">High Risk</div>}
            <div className="text-xl font-black tracking-tighter text-slate-900 dark:text-neutral-100 mt-1">
              {currentWinStreak > 0 ? `${currentWinStreak} W` : currentLossStreak > 0 ? `${currentLossStreak} L` : 'None'}
            </div>
            <div className="text-[9px] uppercase tracking-widest text-slate-500 mt-2 flex gap-2">
               <span title="Max Win Streak">Max W: {maxWinStreak}</span>
               <span title="Max Loss Streak">Max L: {maxLossStreak}</span>
            </div>
          </div>
          <div className="bg-white dark:bg-neutral-900 border border-slate-200 dark:border-neutral-800 p-4 shadow-sm relative overflow-hidden group">
            <div className="text-[10px] uppercase font-bold tracking-widest text-slate-400 mb-1">Win Rate</div>
            <div className="text-2xl font-black tracking-tighter text-slate-900 dark:text-neutral-100">{winRate}%</div>
          </div>
          <div className="bg-white dark:bg-neutral-900 border border-slate-200 dark:border-neutral-800 p-4 shadow-sm">
            <div className="text-[10px] uppercase font-bold tracking-widest text-slate-400 mb-1">Total P/L</div>
            <div className={cn("text-2xl font-black tracking-tighter", totalPL >= 0 ? "text-emerald-600" : "text-red-500")}>
              {totalPL > 0 ? '+' : ''}{formatCurrency(totalPL, user?.currency)}
            </div>
          </div>
          <div className="bg-white dark:bg-neutral-900 border border-slate-200 dark:border-neutral-800 p-4 shadow-sm">
            <div className="text-[10px] uppercase font-bold tracking-widest text-slate-400 mb-1">Total Trades</div>
            <div className="text-2xl font-black tracking-tighter text-slate-900 dark:text-neutral-100">{totalCompleted}</div>
          </div>
          <div className="bg-white dark:bg-neutral-900 border border-slate-200 dark:border-neutral-800 p-4 shadow-sm">
            <div className="text-[10px] uppercase font-bold tracking-widest text-slate-400 mb-1">Profit Factor</div>
            <div className="text-2xl font-black tracking-tighter text-slate-900 dark:text-neutral-100">{profitFactor}</div>
          </div>
        </div>

        {/* Heat Map Section (30 Days with Dates) */}
        <div className="bg-white dark:bg-neutral-900 border border-slate-200 dark:border-neutral-800 p-6 flex flex-col gap-4 shadow-sm w-full overflow-hidden">
          <h3 className="text-[10px] font-bold uppercase tracking-widest text-slate-400">Consistency (Last 30 Days)</h3>
          <div className="grid grid-cols-7 sm:grid-cols-10 md:grid-cols-12 lg:grid-cols-[repeat(15,minmax(0,1fr))] gap-2 w-full">
            {heatMapDays.map((d, i) => (
              <div 
                key={i} 
                className={cn("h-10 sm:h-12 rounded-sm border flex items-center justify-center text-xs font-mono font-bold hover:opacity-80 transition-opacity cursor-crosshair shadow-sm", getHeatMapColor(d.wr))}
                title={`${format(d.date, 'MMM dd, yyyy')}: ${d.count} trades, ${d.wr >= 0 ? (d.wr * 100).toFixed(0) + '% WR' : 'No trades'}`}
              >
                {format(d.date, 'd')}
              </div>
            ))}
          </div>
          <div className="flex flex-wrap items-center gap-3 md:gap-4 text-[9px] uppercase font-bold tracking-widest text-slate-400 mt-2">
             <div className="flex items-center gap-1.5"><div className="w-3 h-3 bg-slate-100 dark:bg-neutral-950 border border-slate-200 dark:border-neutral-800 rounded-sm"></div> No Trades</div>
             <div className="flex items-center gap-1.5"><div className="w-3 h-3 bg-red-500 border border-red-600 rounded-sm"></div> 0% WR</div>
             <div className="flex items-center gap-1.5"><div className="w-3 h-3 bg-orange-400 border border-orange-500 rounded-sm"></div> &lt; 50%</div>
             <div className="flex items-center gap-1.5"><div className="w-3 h-3 bg-yellow-400 border border-yellow-500 rounded-sm"></div> 50% WR</div>
             <div className="flex items-center gap-1.5"><div className="w-3 h-3 bg-emerald-400 border border-emerald-500 rounded-sm"></div> &gt; 50%</div>
             <div className="flex items-center gap-1.5"><div className="w-3 h-3 bg-emerald-700 border border-emerald-800 rounded-sm"></div> 100% WR</div>
          </div>
        </div>

        {/* Chart Section */}
        <div className="bg-white dark:bg-neutral-900 border border-slate-200 dark:border-neutral-800 p-6 flex flex-col gap-4 shadow-sm w-full h-[300px]">
          <h3 className="text-[10px] font-bold uppercase tracking-widest text-slate-400">Equity Curve</h3>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData} margin={{ top: 10, right: 0, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="colorPnl" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="currentColor" stopOpacity={0.1}/>
                  <stop offset="95%" stopColor="currentColor" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <XAxis dataKey="date" hide />
              <YAxis hide domain={['dataMin', 'dataMax']} />
              <Tooltip 
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    return (
                      <div className="bg-black dark:bg-neutral-800 text-white dark:text-neutral-100 border dark:border-neutral-700 p-3 rounded-sm text-xs font-mono shadow-xl relative z-50">
                        <div className="text-slate-400 mb-1">{payload[0].payload.fullDate}</div>
                        <div className="font-bold whitespace-nowrap">{formatCurrency(payload[0].value as number, user?.currency)}</div>
                      </div>
                    );
                  }
                  return null;
                }}
                isAnimationActive={false}
              />
              <Area type="monotone" dataKey="pnl" stroke="currentColor" className="text-slate-900 dark:text-neutral-400" strokeWidth={2} fillOpacity={1} fill="url(#colorPnl)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Day of Week Performance */}
        <div className="bg-white dark:bg-neutral-900 border border-slate-200 dark:border-neutral-800 p-6 flex flex-col gap-4 shadow-sm w-full">
          <h3 className="text-[10px] font-bold uppercase tracking-widest text-slate-400">Day of Week Performance</h3>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[600px] text-left text-xs">
              <thead className="bg-slate-50 dark:bg-neutral-950 uppercase font-bold text-slate-400 text-[9px] tracking-widest">
                <tr>
                  <th className="px-4 py-3 border-b border-slate-200 dark:border-neutral-800">Day</th>
                  <th className="px-4 py-3 border-b border-slate-200 dark:border-neutral-800 text-center">Trades</th>
                  <th className="px-4 py-3 border-b border-slate-200 dark:border-neutral-800 text-center">Win Rate</th>
                  <th className="px-4 py-3 border-b border-slate-200 dark:border-neutral-800 text-right">Net P/L</th>
                </tr>
              </thead>
              <tbody>
                {dayStats.map(s => (
                  <tr key={s.day} className="border-b border-slate-100 dark:border-neutral-800 last:border-0 hover:bg-slate-50 dark:bg-neutral-950/50">
                    <td className="px-4 py-3 font-bold text-slate-700 dark:text-neutral-400">{s.day}</td>
                    <td className="px-4 py-3 text-center text-slate-500 dark:text-neutral-500">{s.trades}</td>
                    <td className="px-4 py-3 text-center">
                      {s.trades > 0 ? <span className={cn("px-2 py-1 rounded-sm text-[10px] font-bold text-white dark:text-neutral-900", s.winRate >= 50 ? "bg-emerald-500" : "bg-orange-400")}>{s.winRate}%</span> : '-'}
                    </td>
                    <td className={cn("px-4 py-3 text-right font-mono font-bold", s.pnl >= 0 ? "text-emerald-600" : "text-red-500")}>
                      {s.pnl > 0 ? '+' : ''}{formatCurrency(s.pnl, user?.currency)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Session Performance */}
        <div className="bg-white dark:bg-neutral-900 border border-slate-200 dark:border-neutral-800 p-6 flex flex-col gap-4 shadow-sm w-full">
          <h3 className="text-[10px] font-bold uppercase tracking-widest text-slate-400">Session Performance</h3>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[600px] text-left text-xs">
              <thead className="bg-slate-50 dark:bg-neutral-950 uppercase font-bold text-slate-400 text-[9px] tracking-widest">
                <tr>
                  <th className="px-4 py-3 border-b border-slate-200 dark:border-neutral-800">Session</th>
                  <th className="px-4 py-3 border-b border-slate-200 dark:border-neutral-800 text-center">Trades</th>
                  <th className="px-4 py-3 border-b border-slate-200 dark:border-neutral-800 text-center">Win Rate</th>
                  <th className="px-4 py-3 border-b border-slate-200 dark:border-neutral-800 text-right">Net P/L</th>
                </tr>
              </thead>
              <tbody>
                {sessionStats.map(s => (
                  <tr key={s.session} className="border-b border-slate-100 dark:border-neutral-800 last:border-0 hover:bg-slate-50 dark:bg-neutral-950/50">
                    <td className="px-4 py-3 font-bold text-slate-700 dark:text-neutral-400">{s.session}</td>
                    <td className="px-4 py-3 text-center text-slate-500 dark:text-neutral-500">{s.trades}</td>
                    <td className="px-4 py-3 text-center">
                      {s.trades > 0 ? <span className={cn("px-2 py-1 rounded-sm text-[10px] font-bold text-white dark:text-neutral-900", s.winRate >= 50 ? "bg-emerald-500" : "bg-orange-400")}>{s.winRate}%</span> : '-'}
                    </td>
                    <td className={cn("px-4 py-3 text-right font-mono font-bold", s.pnl >= 0 ? "text-emerald-600" : "text-red-500")}>
                      {s.pnl > 0 ? '+' : ''}{formatCurrency(s.pnl, user?.currency)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        </div>
    </div>
  );
}
