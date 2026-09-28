import React from 'react';
import { useForm, Controller } from 'react-hook-form';
import { cn } from '../lib/utils';
import { Check, Info } from 'lucide-react';
import { formatCurrency, resizeImage } from '../utils';
import { User } from '../types';

type FormValues = {
  pair: string;
  direction: 'Buy' | 'Sell';
  setup_name: string;
  entry_price: number;
  sl: number;
  tp: number;
  account_balance: number;
  risk_percentage: number;
  position_size: number;
  realized_pl: number | null;
  notes: string;
  result: 'Pending' | 'Win' | 'Loss' | 'Breakeven';
  image: string | null;
};


export const Input = React.forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(({ className, ...props }, ref) => (
  <input
    ref={ref}
    className={cn(
      "border border-slate-300 dark:border-neutral-700 p-2 text-sm focus:outline-none focus:border-black dark:border-neutral-500 w-full rounded-sm placeholder:text-slate-400 bg-white dark:bg-neutral-900 shadow-sm",
      className
    )}
    {...props}
  />
));
Input.displayName = "Input";

export const Label = ({ children, className }: { children: React.ReactNode, className?: string }) => (
  <label className={cn("text-[9px] uppercase font-bold text-slate-900 dark:text-neutral-100 block", className)}>
    {children}
  </label>
);

export default function TradeForm({ onTradeAdded, currentEquity = 10000, user }: { onTradeAdded: () => void, currentEquity?: number, user?: User | null }) {
  const { register, handleSubmit, watch, control, reset, setValue, formState: { errors, isValid } } = useForm<FormValues>({
    defaultValues: {
      direction: 'Buy',
      account_balance: currentEquity,
      risk_percentage: 1,
      position_size: 0,
      realized_pl: null,
      result: 'Pending',
      image: null
    },
    mode: 'onChange'
  });

  // Keep account_balance in sync with currentEquity if it changes externally
  React.useEffect(() => {
    setValue('account_balance', currentEquity);
  }, [currentEquity, setValue]);

  const accountBalance = watch('account_balance') || 0;
  const riskPercentage = watch('risk_percentage') || 0;
  const entryPrice = watch('entry_price') || 0;
  const sl = watch('sl') || 0;
  const tp = watch('tp') || 0;

  const nominalRisk = (accountBalance * riskPercentage) / 100;
  
  // Position Size calculation (simplified logic: Risk / |Entry - SL|)
  let positionSize = 0;
  if (entryPrice > 0 && sl > 0 && Math.abs(entryPrice - sl) > 0) {
    positionSize = nominalRisk / Math.abs(entryPrice - sl);
  }


  const onSubmit = async (data: FormValues) => {

    let realized_pl = data.realized_pl !== null && String(data.realized_pl) !== '' && !isNaN(Number(data.realized_pl)) ? Number(data.realized_pl) : null;
    if (data.result === 'Pending') {
      realized_pl = null;
    } else if (data.result === 'Breakeven') {
      realized_pl = 0;
    }

    const payload = {
      pair: data.pair,
      direction: data.direction,
      setup_name: data.setup_name,
      entry_price: Number(data.entry_price),
      sl: Number(data.sl),
      tp: Number(data.tp),
      account_balance: Number(data.account_balance),
      risk_percentage: Number(data.risk_percentage),
      position_size: positionSize,
      nominal_risk: nominalRisk,
      notes: data.notes,
      result: data.result,
      realized_pl,
      image: data.image
    };

    try {
      const res = await fetch('/api/trades', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        reset();
        onTradeAdded();
      } else {
        console.error("Failed to save. Server responded with:", await res.text());
      }
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6 flex flex-col h-full">
      <div className="space-y-4 shrink-0">
        <h2 className="text-xs font-bold uppercase tracking-widest text-slate-400">1. Trade Parameters</h2>
        
        <div className="grid grid-cols-2 gap-3">
          <div className="flex flex-col gap-1">
            <Label>Pair</Label>
            <Input {...register('pair', { required: true })} placeholder="XAUUSD" />
          </div>
          <div className="flex flex-col gap-1">
            <Label>Direction</Label>
            <select
              {...register('direction', { required: true })}
              className="border border-slate-300 dark:border-neutral-700 p-2 text-sm focus:outline-none focus:border-black dark:border-neutral-500 w-full rounded-sm bg-white dark:bg-neutral-900 shadow-sm cursor-pointer"
            >
              <option value="Buy">Buy (Long)</option>
              <option value="Sell">Sell (Short)</option>
            </select>
          </div>
          <div className="flex flex-col gap-1 col-span-2">
            <Label>Setup Name</Label>
            <Input {...register('setup_name', { required: true })} placeholder="FVG + OB" />
          </div>
          <div className="flex flex-col gap-1">
            <Label>Entry Price</Label>
            <Input type="number" step="any" {...register('entry_price', { required: true })} placeholder="2034.50" />
          </div>
          <div className="flex flex-col gap-1">
            <Label>Risk %</Label>
            <Input type="number" step="0.1" {...register('risk_percentage', { required: true, min: 0.1, max: 100 })} placeholder="1.0" />
          </div>
          <div className="flex flex-col gap-1">
            <Label>Stop Loss</Label>
            <Input type="number" step="any" {...register('sl', { required: true })} placeholder="0.00" />
          </div>
          <div className="flex flex-col gap-1">
            <Label>Take Profit</Label>
            <Input type="number" step="any" {...register('tp', { required: true })} placeholder="0.00" />
          </div>
          <div className="flex flex-col gap-1">
            <Label>Account Balance</Label>
            <Input type="number" step="any" {...register('account_balance', { required: true, min: 1 })} placeholder="10000" />
          </div>
          <div className="flex flex-col gap-1 mt-1 col-span-2">
            <Label>Trade Result</Label>
            <select
              {...register('result')}
              className="border border-slate-300 dark:border-neutral-700 p-2 text-sm focus:outline-none focus:border-black dark:border-neutral-500 w-full rounded-sm placeholder:text-slate-400 bg-white dark:bg-neutral-900 shadow-sm cursor-pointer"
            >
              <option value="Pending">Pending (Log & Wait)</option>
              <option value="Win">Win</option>
              <option value="Loss">Loss</option>
              <option value="Breakeven">Breakeven</option>
            </select>
          </div>
        </div>
      </div>

      <div className="space-y-4 bg-slate-50 dark:bg-neutral-950 p-4 border border-dashed border-slate-300 dark:border-neutral-700 shrink-0">
        <h2 className="text-[9px] font-bold uppercase tracking-widest text-slate-400">Position Details</h2>
        <div className="grid grid-cols-2 gap-4">
          <div className="flex flex-col gap-1">
            <Label>Lot Size</Label>
            <Input type="number" step="any" {...register('position_size')} placeholder="0.01" />
          </div>
          <div className="flex flex-col gap-1">
            <Label>Profit / Loss (if closed)</Label>
            <Input type="number" step="any" {...register('realized_pl')} placeholder="0.00" />
          </div>
        </div>
      </div>

      <div className="space-y-4 shrink-0">
         <div className="pt-2">
            <Label className="mb-1">Notes / Reasons</Label>
            <textarea
              {...register('notes')}
              className="w-full border border-slate-300 dark:border-neutral-700 p-2 text-sm focus:outline-none focus:border-black dark:border-neutral-500 rounded-sm placeholder:text-slate-400 min-h-[60px] resize-none"
              placeholder="Why are you taking this trade?"
            />
         </div>

         <div className="pt-2">
            <div className="flex flex-col gap-1">
               <Label>Trade Image (Chart/Result)</Label>
               <input 
                 type="file" 
                 accept="image/*"
                 className="text-[10px] text-slate-500 dark:text-neutral-500 file:mr-2 file:py-1 file:px-2 file:border-0 file:text-[9px] file:font-bold file:uppercase file:bg-slate-100 dark:bg-neutral-950 file:text-slate-700 dark:text-neutral-400 hover:file:bg-slate-200"
                 onChange={async (e) => {
                   const file = e.target.files?.[0];
                   if (file) {
                     const compressed = await resizeImage(file);
                     setValue('image', compressed, { shouldValidate: true });
                   } else {
                     setValue('image', null);
                   }
                 }}
               />
               {watch('image') && <span className="text-[8px] text-emerald-600 font-bold uppercase mt-1 inline-block">Image Loaded</span>}
            </div>
         </div>
      </div>

      <button
        type="submit"
        disabled={!isValid}
        className="w-full py-4 mt-auto bg-black dark:bg-neutral-200 text-white dark:text-neutral-900 text-xs font-bold uppercase tracking-widest hover:bg-slate-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed shrink-0"
      >
        Log Backtest Entry
      </button>
    </form>
  )
}
