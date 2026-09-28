import React, { useState } from 'react';
import { User } from '../types';
import { motion, AnimatePresence } from 'motion/react';
import { ArrowRight, Lock, User as UserIcon, Key } from 'lucide-react';

export default function Auth({ onLogin }: { onLogin: (user: User) => void }) {
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [inviteCode, setInviteCode] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const endpoint = mode === 'login' ? '/api/auth/login' : '/api/auth/register';
      const body = mode === 'login' 
        ? { username, password } 
        : { username, password, inviteCode };
      
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      let data;
      try {
        data = await res.json();
      } catch (e) {
        throw new Error('Server returned an unexpected response. Checking server logs on Vercel.');
      }

      if (!res.ok) throw new Error(data?.error || 'Failed to authenticate');

      onLogin(data.user);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const isFormValid = username.length >= 3 && password.length >= 6 && (mode === 'login' || inviteCode.trim() !== '');

  return (
    <div className="bg-slate-50 dark:bg-neutral-950 min-h-screen flex items-center justify-center p-4 font-sans selection:bg-red-200 dark:selection:bg-red-900/30 overflow-hidden relative">
      
      {/* Decorative background elements */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none z-0">
        <div className="absolute -top-[20%] -left-[10%] w-[50%] h-[50%] rounded-full bg-red-600/5 blur-[120px] dark:bg-red-600/10" />
        <div className="absolute top-[60%] -right-[10%] w-[40%] h-[40%] rounded-full bg-red-600/5 blur-[100px] dark:bg-red-600/10" />
      </div>

      <motion.div 
        initial={{ opacity: 0, y: 20, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
        className="bg-white/80 dark:bg-neutral-900/80 backdrop-blur-xl w-full max-w-md border border-slate-200/50 dark:border-neutral-800/50 p-8 sm:p-10 shadow-2xl dark:shadow-red-900/10 rounded-3xl relative z-10"
      >
        <div className="flex flex-col items-center mb-10 text-center">
          <motion.div 
            initial={{ rotate: -90, opacity: 0 }}
            animate={{ rotate: 45, opacity: 1 }}
            transition={{ duration: 0.8, type: "spring" }}
            className="w-10 h-10 border-4 border-red-600 dark:border-red-500 mb-6 relative shadow-lg shadow-red-600/20"
          >
            <div className="absolute inset-1 bg-red-600 dark:bg-red-500 opacity-20" />
          </motion.div>
          <h1 className="text-2xl font-black tracking-tight uppercase"><span className="text-red-600 dark:text-red-500">Journal</span>Tradingku</h1>
          <p className="text-slate-500 dark:text-neutral-400 text-sm mt-2 font-medium">
            Welcome back, trader. Access your terminal.
          </p>
        </div>

        <div className="flex relative bg-slate-100 dark:bg-neutral-950 p-1 rounded-xl mb-8">
          <motion.div
            className="absolute top-1 bottom-1 left-1 bg-white dark:bg-neutral-800 rounded-lg shadow-sm z-0"
            animate={{ 
              x: mode === 'login' ? 0 : '100%',
              width: 'calc(50% - 4px)'
            }}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
          />
          <button 
            type="button"
            className={`flex-1 py-2 text-sm font-bold z-10 transition-colors ${mode === 'login' ? 'text-black dark:text-neutral-100' : 'text-slate-500 hover:text-slate-700 dark:hover:text-neutral-300'}`}
            onClick={() => { setMode('login'); setError(''); }}
          >
            Login
          </button>
          <button 
            type="button"
            className={`flex-1 py-2 text-sm font-bold z-10 transition-colors ${mode === 'register' ? 'text-black dark:text-neutral-100' : 'text-slate-500 hover:text-slate-700 dark:hover:text-neutral-300'}`}
            onClick={() => { setMode('register'); setError(''); }}
          >
            Register
          </button>
        </div>

        <AnimatePresence mode="wait">
          {error && (
            <motion.div 
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="overflow-hidden"
            >
              <div className="bg-red-50 dark:bg-red-500/10 text-red-600 dark:text-red-400 border border-red-200 dark:border-red-500/20 text-sm p-4 mb-6 rounded-xl flex items-center gap-3 font-medium">
                <div className="w-1.5 h-1.5 rounded-full bg-red-600 dark:bg-red-400 shrink-0" />
                {error}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="space-y-2">
            <label className="text-xs font-bold text-slate-700 dark:text-neutral-300 ml-1">Username</label>
            <div className="relative group">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-400 group-focus-within:text-red-600 dark:group-focus-within:text-red-500 transition-colors">
                <UserIcon size={18} />
              </div>
              <input 
                type="text" 
                value={username}
                onChange={e => setUsername(e.target.value)}
                placeholder="Enter username"
                className="w-full bg-slate-50 dark:bg-neutral-950/50 border border-slate-200 dark:border-neutral-800 py-3 pl-11 pr-4 text-sm focus:outline-none focus:border-red-500 focus:ring-1 focus:ring-red-500 rounded-xl transition-all shadow-sm"
                required
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-xs font-bold text-slate-700 dark:text-neutral-300 ml-1">Password</label>
            <div className="relative group">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-400 group-focus-within:text-red-600 dark:group-focus-within:text-red-500 transition-colors">
                <Lock size={18} />
              </div>
              <input 
                type="password" 
                value={password}
                onChange={e => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-slate-50 dark:bg-neutral-950/50 border border-slate-200 dark:border-neutral-800 py-3 pl-11 pr-4 text-sm focus:outline-none focus:border-red-500 focus:ring-1 focus:ring-red-500 rounded-xl transition-all shadow-sm"
                required
              />
            </div>
            <AnimatePresence>
              {mode === 'register' && (
                <motion.p 
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="text-[10px] text-slate-500 ml-1 font-medium"
                >
                  Minimum 6 characters required
                </motion.p>
              )}
            </AnimatePresence>
          </div>

          <AnimatePresence>
            {mode === 'register' && (
              <motion.div 
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="overflow-hidden"
              >
                <div className="space-y-2 pt-1">
                  <label className="text-xs font-bold text-slate-700 dark:text-neutral-300 ml-1">Invite Code</label>
                  <div className="relative group">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-400 group-focus-within:text-red-600 dark:group-focus-within:text-red-500 transition-colors">
                      <Key size={18} />
                    </div>
                    <input 
                      type="text" 
                      value={inviteCode}
                      onChange={e => setInviteCode(e.target.value)}
                      placeholder="Enter invite code"
                      className="w-full bg-slate-50 dark:bg-neutral-950/50 border border-slate-200 dark:border-neutral-800 py-3 pl-11 pr-4 text-sm focus:outline-none focus:border-red-500 focus:ring-1 focus:ring-red-500 rounded-xl transition-all shadow-sm font-mono tracking-widest"
                      required
                    />
                  </div>
                  <p className="text-[10px] text-slate-500 ml-1 font-medium">Required for new accounts</p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          <motion.button 
            whileHover={{ scale: isFormValid && !loading ? 1.02 : 1 }}
            whileTap={{ scale: isFormValid && !loading ? 0.98 : 1 }}
            type="submit" 
            disabled={loading || !isFormValid}
            className="w-full py-4 mt-6 bg-red-600 hover:bg-red-700 text-white text-sm font-bold rounded-xl flex items-center justify-center gap-2 shadow-lg shadow-red-600/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed group"
          >
            {loading ? (
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : (
              <>
                {mode === 'login' ? 'Enter Terminal' : 'Create Account'}
                <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
              </>
            )}
          </motion.button>
        </form>
      </motion.div>
    </div>
  );
}
