import React, { useState, useEffect } from 'react';
import { Trade, User, Transaction } from './types';
import TradeForm from './components/TradeForm';
import Dashboard from './components/Dashboard';
import History from './components/History';
import Auth from './components/Auth';
import AdminPanel from './components/AdminPanel';
import Settings from './components/Settings';
import Calculators from './components/Calculators';
import PropFirm from './components/PropFirm';
import PublicProfile from './components/PublicProfile';
import BankingModal from './components/BankingModal';
import { Menu, X, Moon, Sun, Wallet } from 'lucide-react';
import { formatCurrency } from './utils';

export default function App() {
  const [isPublicRoute, setIsPublicRoute] = useState(false);
  const [publicUsername, setPublicUsername] = useState('');

  useEffect(() => {
    const path = window.location.pathname;
    if (path.startsWith('/p/')) {
      const parts = path.split('/');
      if (parts.length >= 3 && parts[2]) {
        setIsPublicRoute(true);
        setPublicUsername(parts[2]);
      }
    }
  }, []);

  const [trades, setTrades] = useState<Trade[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [userLoading, setUserLoading] = useState(true);
  const [user, setUser] = useState<User | null>(null);
  const [activeTab, setActiveTab] = useState<'dashboard' | 'log' | 'history' | 'gallery' | 'calculators' | 'admin' | 'settings' | 'propfirm'>('dashboard');
  const [menuOpen, setMenuOpen] = useState(false);
  const [showBankingModal, setShowBankingModal] = useState(false);
  const [darkMode, setDarkMode] = useState(() => {
    return localStorage.getItem('darkMode') === 'true';
  });

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('darkMode', 'true');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('darkMode', 'false');
    }
  }, [darkMode]);

  const fetchUser = async () => {
    try {
      const res = await fetch('/api/auth/me?t=' + Date.now());
      if (res.ok) {
        const data = await res.json();
        setUser(data.user);
      }
    } catch(e) {
      // Not logged in
    } finally {
      setUserLoading(false);
    }
  };

  useEffect(() => {
    if (!isPublicRoute) {
      fetchUser();
    }
  }, [isPublicRoute]);

  const fetchTrades = async () => {
    try {
      const [tradesRes, transactionsRes] = await Promise.all([
        fetch('/api/trades?t=' + Date.now()),
        fetch('/api/transactions?t=' + Date.now())
      ]);
      if (tradesRes.ok) {
        setTrades(await tradesRes.json());
      }
      if (transactionsRes.ok) {
        setTransactions(await transactionsRes.json());
      }
    } catch (error) {
      console.error("Failed to fetch data", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user) {
      fetchTrades();
      // Auto-refresh to get trades from Discord bot instantly
      const interval = setInterval(() => {
        fetchTrades();
      }, 5000);
      return () => clearInterval(interval);
    }
  }, [user]);

  const handleTradeAdded = () => {
    fetchTrades();
    setActiveTab('history');
  };

  const handleLogout = async () => {
    try {
      await fetch('/api/auth/logout', { method: 'POST' });
      setUser(null);
      setTrades([]);
    } catch(e) {
      console.error("Failed to logout");
    }
  };

  if (isPublicRoute) {
    return <PublicProfile username={publicUsername} />;
  }

  if (userLoading) {
    return (
      <div className="bg-slate-100 dark:bg-neutral-950 min-h-screen flex items-center justify-center font-sans">
        <div className="text-[10px] font-bold uppercase tracking-widest text-slate-400">Restoring terminal session...</div>
      </div>
    );
  }

  const handleUserLocalUpdate = (updates: Partial<User>) => {
    if (user) setUser({ ...user, ...updates });
  };

  if (!user) {
    return <Auth onLogin={setUser} />;
  }

  // Calculate current equity
  // Default to 10000 if no trades, otherwise use the oldest trade's account_balance as base + all realized_pl
  const baseEquity = user?.prop_firm_enabled ? (user.prop_firm_balance || 10000) : (user?.initial_balance ?? (trades.length > 0 ? trades[trades.length - 1].account_balance : 10000));
  
  const totalDeposits = transactions.filter(t => t.type === 'deposit').reduce((acc, t) => acc + t.amount, 0);
  const totalWithdrawals = transactions.filter(t => t.type === 'withdrawal').reduce((acc, t) => acc + t.amount, 0);

  let currentEquity = trades.length > 0
    ? trades.reduce((acc, t) => acc + (t.realized_pl || 0), baseEquity)
    : baseEquity;
  
  currentEquity = currentEquity + totalDeposits - totalWithdrawals;

  if (user?.prop_firm_enabled) {
    currentEquity -= (user.prop_firm_payout_total || 0);
  }

  return (
    <div className="bg-slate-100 dark:bg-neutral-950 min-h-screen flex items-center justify-center lg:p-8 font-sans">
      <div className="bg-white dark:bg-neutral-900 text-slate-900 dark:text-neutral-100 font-sans w-full lg:max-w-[1280px] lg:h-[800px] min-h-screen lg:min-h-0 lg:border-8 border-slate-100 dark:border-neutral-800 flex flex-col overflow-hidden select-none lg:shadow-xl relative">
        
        {/* Sidebar Overlay */}
        {menuOpen && (
          <div className="absolute inset-0 z-50 flex justify-end">
            <div className="absolute inset-0 bg-black/50 dark:bg-black/80 backdrop-blur-sm" onClick={() => setMenuOpen(false)}></div>
            <div className="w-64 bg-white dark:bg-neutral-900 h-full relative z-50 border-l border-slate-200 dark:border-neutral-800 flex flex-col shadow-2xl">
              <div className="h-16 border-b border-slate-200 dark:border-neutral-800 flex items-center justify-between px-6 shrink-0">
                <span className="font-bold tracking-tighter uppercase">Menu</span>
                <button onClick={() => setMenuOpen(false)} className="opacity-50 hover:opacity-100 p-2 -mr-2"><X size={18} /></button>
              </div>
              <div className="flex flex-col p-4 gap-1 text-[11px] font-bold tracking-widest uppercase text-slate-500 dark:text-neutral-500 overflow-y-auto">
                <button 
                  onClick={() => { setActiveTab('dashboard'); setMenuOpen(false); }}
                  className={`text-left px-4 py-3 rounded-sm hover:bg-slate-50 dark:bg-neutral-950 hover:text-black dark:hover:text-neutral-100 transition-colors ${activeTab === 'dashboard' ? 'text-black dark:text-neutral-100 bg-slate-50 dark:bg-neutral-950 shadow-sm border border-slate-100 dark:border-neutral-800' : ''}`}
                >Dashboard</button>
                <button 
                  onClick={() => { setActiveTab('log'); setMenuOpen(false); }}
                  className={`text-left px-4 py-3 rounded-sm hover:bg-slate-50 dark:bg-neutral-950 hover:text-black dark:hover:text-neutral-100 transition-colors ${activeTab === 'log' ? 'text-black dark:text-neutral-100 bg-slate-50 dark:bg-neutral-950 shadow-sm border border-slate-100 dark:border-neutral-800' : ''}`}
                >Log Trade</button>
                <button 
                  onClick={() => { setActiveTab('history'); setMenuOpen(false); }}
                  className={`text-left px-4 py-3 rounded-sm hover:bg-slate-50 dark:bg-neutral-950 hover:text-black dark:hover:text-neutral-100 transition-colors ${activeTab === 'history' ? 'text-black dark:text-neutral-100 bg-slate-50 dark:bg-neutral-950 shadow-sm border border-slate-100 dark:border-neutral-800' : ''}`}
                >History</button>

                <button 
                  onClick={() => { setActiveTab('calculators'); setMenuOpen(false); }}
                  className={`text-left px-4 py-3 rounded-sm hover:bg-slate-50 dark:bg-neutral-950 hover:text-black dark:hover:text-neutral-100 transition-colors ${activeTab === 'calculators' ? 'text-black dark:text-neutral-100 bg-slate-50 dark:bg-neutral-950 shadow-sm border border-slate-100 dark:border-neutral-800' : ''}`}
                >Calculators</button>
                <button 
                  onClick={() => { setActiveTab('propfirm'); setMenuOpen(false); }}
                  className={`text-left px-4 py-3 rounded-sm hover:bg-slate-50 dark:bg-neutral-950 hover:text-black dark:hover:text-neutral-100 transition-colors ${activeTab === 'propfirm' ? 'text-black dark:text-neutral-100 bg-slate-50 dark:bg-neutral-950 shadow-sm border border-slate-100 dark:border-neutral-800' : ''}`}
                >Prop Firm</button>
                <button 
                  onClick={() => { setActiveTab('settings'); setMenuOpen(false); }}
                  className={`text-left px-4 py-3 rounded-sm hover:bg-slate-50 dark:bg-neutral-950 hover:text-black dark:hover:text-neutral-100 transition-colors ${activeTab === 'settings' ? 'text-black dark:text-neutral-100 bg-slate-50 dark:bg-neutral-950 shadow-sm border border-slate-100 dark:border-neutral-800' : ''}`}
                >Settings</button>
                {user?.role === 'admin' && (
                  <button 
                    onClick={() => { setActiveTab('admin'); setMenuOpen(false); }}
                    className={`text-left px-4 py-3 rounded-sm mt-4 hover:bg-blue-50 transition-colors ${activeTab === 'admin' ? 'text-blue-600 bg-blue-50 shadow-sm border border-blue-100' : 'text-blue-400 hover:text-blue-600 border border-transparent'}`}
                  >Admin Shield</button>
                )}
              </div>
              <div className="mt-auto p-6 border-t border-slate-100 dark:border-neutral-800 text-[10px] uppercase tracking-widest font-bold shrink-0 bg-slate-50 dark:bg-neutral-950">
                 <div className="mb-4 text-slate-500 dark:text-neutral-500">Equity: <span className="text-black dark:text-neutral-100 text-xs">{formatCurrency(currentEquity, user?.currency)}</span></div>
                 <div className="flex items-center gap-2 mb-2 text-slate-500 dark:text-neutral-500">
                   <span className="w-2 h-2 rounded-full bg-emerald-400 shrink-0"></span>
                   <span className="truncate">{user?.username} ({user?.role})</span>
                 </div>
              </div>
            </div>
          </div>
        )}

        <header className="h-16 shrink-0 border-b border-slate-200 dark:border-neutral-800 flex items-center justify-between px-6 lg:px-8 bg-white dark:bg-neutral-900 relative z-30">
          <div className="flex items-center gap-3 shrink-0">
            <div className="w-5 h-5 border-2 border-black dark:border-neutral-500 rotate-45 shrink-0 hidden sm:block"></div>
            <h1 className="text-lg font-bold tracking-tighter uppercase whitespace-nowrap sm:ml-2"><span className="text-red-600">Journal</span>Tradingku <span className="font-normal text-slate-400 text-sm hidden sm:inline">/ v1.1</span></h1>
          </div>

          <div className="flex items-center text-[10px] gap-2 md:gap-4 font-bold tracking-widest uppercase shrink-0 text-slate-400">
            <button 
              onClick={() => setShowBankingModal(true)}
              className="bg-slate-50 dark:bg-neutral-950 px-3 py-1.5 border border-slate-200 dark:border-neutral-800 text-slate-900 dark:text-neutral-100 hover:bg-slate-100 dark:hover:bg-neutral-800 transition-colors rounded-sm shadow-sm hidden sm:flex items-center gap-2"
              title="Deposit or Withdraw"
            >
              <Wallet size={12} className="text-slate-500" />
              Equity: <span className="text-black dark:text-neutral-100 font-bold">{formatCurrency(currentEquity, user?.currency)}</span>
            </button>
            <button onClick={() => setDarkMode(!darkMode)} className="p-2 text-slate-400 hover:text-black dark:hover:text-neutral-100 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-sm transition-colors border border-slate-200 dark:border-neutral-800 flex items-center justify-center">
              {darkMode ? <Sun size={18} /> : <Moon size={18} />}
            </button>
            <button onClick={() => setMenuOpen(true)} className="p-2 text-slate-400 hover:text-black dark:hover:text-neutral-100 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-sm transition-colors border border-slate-200 dark:border-neutral-800 ml-1">
              <Menu size={18} />
            </button>
          </div>
        </header>

        <main className="flex-1 flex overflow-hidden min-h-0 bg-slate-50 dark:bg-neutral-950/50">
          {loading ? (
             <div className="flex-1 flex items-center justify-center text-slate-400 text-[10px] font-bold uppercase tracking-widest">
               Loading journal...
             </div>
          ) : (
            <>
              {activeTab === 'dashboard' && <Dashboard trades={trades} user={user} transactions={transactions} />}
              {activeTab === 'log' && (
                <div className="flex-1 flex justify-center p-8 overflow-y-auto">
                  <div className="w-full max-w-2xl bg-white dark:bg-neutral-900 border border-slate-200 dark:border-neutral-800 p-8 shadow-sm">
                    <TradeForm onTradeAdded={handleTradeAdded} currentEquity={currentEquity} user={user} />
                  </div>
                </div>
              )}
              {activeTab === 'history' && <History trades={trades} onTradeUpdated={fetchTrades} user={user} />}
              
              {activeTab === 'calculators' && <Calculators currentEquity={currentEquity} user={user} />}
              {activeTab === 'propfirm' && <PropFirm trades={trades} user={user} onLocalUpdate={handleUserLocalUpdate} onTradeAdded={fetchTrades} />}
              {activeTab === 'admin' && <AdminPanel />}
              {activeTab === 'settings' && <Settings user={user} onUserUpdate={fetchUser} onLocalUpdate={handleUserLocalUpdate} onModeChange={fetchTrades} onLogout={handleLogout} />}
            </>
          )}
        </main>

        <footer className="h-8 shrink-0 bg-slate-900 text-slate-400 px-6 flex items-center justify-between text-[10px] tracking-wide font-mono">
          <div>Connected to: Turso Edge</div>
          <div className="flex gap-4">
            <span className="text-emerald-500 font-bold">● LIVE</span>
          </div>
        </footer>
      </div>
      
      {showBankingModal && (
        <BankingModal
          onClose={() => setShowBankingModal(false)}
          onTransactionComplete={() => {
            setShowBankingModal(false);
            fetchTrades();
          }}
        />
      )}
    </div>
  );
}
