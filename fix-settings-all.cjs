const fs = require('fs');
let code = fs.readFileSync('src/components/Settings.tsx', 'utf8');

const propFirmState = `
  const [propFirmEnabled, setPropFirmEnabled] = useState(user?.prop_firm_enabled || false);
  const [propFirmBalance, setPropFirmBalance] = useState(String(user?.prop_firm_balance || 10000));
  const [propFirmDailyDD, setPropFirmDailyDD] = useState(String(user?.prop_firm_daily_dd || 5));
  const [propFirmMaxDD, setPropFirmMaxDD] = useState(String(user?.prop_firm_max_dd || 10));
  const [propFirmTarget, setPropFirmTarget] = useState(String(user?.prop_firm_target || 10));
  const [propFirmSaving, setPropFirmSaving] = useState(false);
  const [propFirmSuccess, setPropFirmSuccess] = useState(false);

  const savePropFirm = async () => {
    setPropFirmSaving(true);
    setPropFirmSuccess(false);
    try {
      await fetch('/api/auth/prop-firm', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prop_firm_enabled: propFirmEnabled,
          prop_firm_balance: Number(propFirmBalance),
          prop_firm_daily_dd: Number(propFirmDailyDD),
          prop_firm_max_dd: Number(propFirmMaxDD),
          prop_firm_target: Number(propFirmTarget),
        })
      });
      setPropFirmSuccess(true);
      onUserUpdate();
      setTimeout(() => setPropFirmSuccess(false), 3000);
    } catch (e) {
      console.error(e);
    } finally {
      setPropFirmSaving(false);
    }
  };

  const [currency, setCurrency] = useState(user?.currency || 'USD');
  const [currencySaving, setCurrencySaving] = useState(false);
  const [currencySuccess, setCurrencySuccess] = useState(false);

  const saveCurrency = async () => {
    setCurrencySaving(true);
    setCurrencySuccess(false);
    try {
      await fetch('/api/auth/currency', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ currency })
      });
      setCurrencySuccess(true);
      onUserUpdate();
      setTimeout(() => setCurrencySuccess(false), 3000);
    } catch (e) {
      console.error(e);
    } finally {
      setCurrencySaving(false);
    }
  };
`;

const newPanels = `
           <div className="flex flex-col gap-4 border-t border-slate-100 dark:border-neutral-800 pt-8 mt-4">
              <h3 className="text-xs font-bold uppercase tracking-widest text-slate-600 dark:text-neutral-400">Base Currency</h3>
              <div className="flex flex-col gap-4 max-w-sm">
                <select 
                  value={currency} 
                  onChange={(e) => setCurrency(e.target.value)}
                  className="border border-slate-300 dark:border-neutral-700 p-2 text-sm focus:outline-none focus:border-black dark:border-neutral-500 rounded-sm bg-slate-50 dark:bg-neutral-950"
                >
                  <option value="USD">USD ($)</option>
                  <option value="USC">USC (¢)</option>
                  <option value="IDR">IDR (Rp)</option>
                </select>
                
                <div className="flex items-center gap-3">
                  <button 
                    onClick={saveCurrency}
                    disabled={currencySaving}
                    className="px-4 py-2 bg-black dark:bg-neutral-200 text-white dark:text-neutral-900 text-[10px] font-bold uppercase tracking-widest hover:bg-slate-800 transition-colors disabled:opacity-50"
                  >
                    {currencySaving ? 'Saving...' : 'Save Currency'}
                  </button>
                  {currencySuccess && <span className="text-xs text-emerald-600 font-bold flex items-center gap-1"><Check size={14}/> Saved</span>}
                </div>
              </div>
           </div>

           <div className="flex flex-col gap-4 border-t border-slate-100 dark:border-neutral-800 pt-8 mt-4">
              <h3 className="text-xs font-bold uppercase tracking-widest text-slate-600 dark:text-neutral-400">Prop-Firm Challenge</h3>
              <div className="flex flex-col gap-4 max-w-md">
                <label className="flex items-center gap-2 text-sm cursor-pointer">
                  <input 
                    type="checkbox" 
                    checked={propFirmEnabled}
                    onChange={(e) => setPropFirmEnabled(e.target.checked)}
                    className="w-4 h-4 rounded border-slate-300 text-black focus:ring-black"
                  />
                  <span className="font-bold">Enable Prop-Firm Tracking</span>
                </label>

                {propFirmEnabled && (
                  <div className="grid grid-cols-2 gap-4 pt-2">
                    <div className="flex flex-col gap-1">
                      <span className="text-[10px] uppercase font-bold text-slate-500">Starting Balance</span>
                      <input 
                        type="number" 
                        value={propFirmBalance}
                        onChange={(e) => setPropFirmBalance(e.target.value)}
                        className="border border-slate-300 dark:border-neutral-700 p-2 text-sm focus:outline-none focus:border-black dark:border-neutral-500 rounded-sm bg-slate-50 dark:bg-neutral-950" 
                      />
                    </div>
                    <div className="flex flex-col gap-1">
                      <span className="text-[10px] uppercase font-bold text-slate-500">Profit Target (%)</span>
                      <input 
                        type="number" 
                        value={propFirmTarget}
                        onChange={(e) => setPropFirmTarget(e.target.value)}
                        className="border border-slate-300 dark:border-neutral-700 p-2 text-sm focus:outline-none focus:border-black dark:border-neutral-500 rounded-sm bg-slate-50 dark:bg-neutral-950" 
                      />
                    </div>
                    <div className="flex flex-col gap-1">
                      <span className="text-[10px] uppercase font-bold text-slate-500">Daily Drawdown (%)</span>
                      <input 
                        type="number" 
                        value={propFirmDailyDD}
                        onChange={(e) => setPropFirmDailyDD(e.target.value)}
                        className="border border-slate-300 dark:border-neutral-700 p-2 text-sm focus:outline-none focus:border-black dark:border-neutral-500 rounded-sm bg-slate-50 dark:bg-neutral-950" 
                      />
                    </div>
                    <div className="flex flex-col gap-1">
                      <span className="text-[10px] uppercase font-bold text-slate-500">Max Drawdown (%)</span>
                      <input 
                        type="number" 
                        value={propFirmMaxDD}
                        onChange={(e) => setPropFirmMaxDD(e.target.value)}
                        className="border border-slate-300 dark:border-neutral-700 p-2 text-sm focus:outline-none focus:border-black dark:border-neutral-500 rounded-sm bg-slate-50 dark:bg-neutral-950" 
                      />
                    </div>
                  </div>
                )}

                <div className="flex items-center gap-3">
                  <button 
                    onClick={savePropFirm}
                    disabled={propFirmSaving}
                    className="px-4 py-2 bg-black dark:bg-neutral-200 text-white dark:text-neutral-900 text-[10px] font-bold uppercase tracking-widest hover:bg-slate-800 transition-colors disabled:opacity-50"
                  >
                    {propFirmSaving ? 'Saving...' : 'Save Settings'}
                  </button>
                  {propFirmSuccess && <span className="text-xs text-emerald-600 font-bold flex items-center gap-1"><Check size={14}/> Saved</span>}
                </div>
              </div>
           </div>

           <div className="flex flex-col gap-4 border-t border-slate-100 dark:border-neutral-800 pt-8 mt-4">
              <h3 className="text-xs font-bold uppercase tracking-widest text-slate-600 dark:text-neutral-400">Public Profile</h3>
`;

code = code.replace(/const \[error, setError\] = useState<string \| null>\(null\);/, `const [error, setError] = useState<string | null>(null);\n` + propFirmState);
code = code.replace(/<div className="flex flex-col gap-4 border-t border-slate-100 dark:border-neutral-800 pt-8 mt-4">\s*<h3 className="text-xs font-bold uppercase tracking-widest text-slate-600 dark:text-neutral-400">Public Profile<\/h3>/, newPanels);

fs.writeFileSync('src/components/Settings.tsx', code);
