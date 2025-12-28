'use client';

import { useEffect, useState } from 'react';
import api from '@/lib/api';
import BentoCard from '@/components/BentoCard';
import { 
  TrendingDown, 
  TrendingUp, 
  Wallet, 
  ArrowUpRight, 
  ArrowDownRight,
  Loader2,
  Clock,
  MoreHorizontal
} from 'lucide-react';
import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer 
} from 'recharts';

export default function OverviewPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [balances, forecast, transactions] = await Promise.all([
          api.get('/api/balances'),
          api.get('/api/forecast?days=30'),
          api.get('/api/transactions')
        ]);
        setData({ 
          balances: balances.data, 
          forecast: forecast.data,
          recentTxns: transactions.data.slice(0, 5)
        });
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  const totalBalance = data?.balances?.reduce((acc: number, b: any) => acc + b.current, 0) || 0;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-2">
        <div>
          <h2 className="text-2xl font-bold text-white tracking-tight">Overview</h2>
          <p className="text-slate-400 text-sm">Your financial command center</p>
        </div>
      </div>

      {/* BENTO GRID */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6 auto-rows-[minmax(180px,auto)]">
        
        {/* Metric 1: Net Worth */}
        <BentoCard className="md:col-span-1 lg:col-span-1 p-6 flex flex-col justify-between" delay={0.1}>
          <div className="flex items-start justify-between relative z-10">
            <div className="p-3 bg-blue-500/10 border border-blue-500/20 rounded-2xl">
              <Wallet className="h-6 w-6 text-blue-500" />
            </div>
            <span className="text-xs font-medium text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2 py-1 rounded-full flex items-center gap-1">
              <ArrowUpRight className="h-3 w-3" /> Live
            </span>
          </div>
          <div className="relative z-10">
            <p className="text-sm text-slate-400 font-medium">Net Worth</p>
            <h3 className="text-3xl font-bold text-white mt-1 tracking-tight">£{totalBalance.toLocaleString(undefined, { minimumFractionDigits: 2 })}</h3>
          </div>
          <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
            <Wallet className="h-32 w-32 text-blue-500" />
          </div>
        </BentoCard>

        {/* Metric 2: Monthly Spend */}
        <BentoCard className="md:col-span-1 lg:col-span-1 p-6 flex flex-col justify-between" delay={0.2}>
          <div className="flex items-start justify-between relative z-10">
            <div className="p-3 bg-orange-500/10 border border-orange-500/20 rounded-2xl">
              <TrendingDown className="h-6 w-6 text-orange-500" />
            </div>
            <span className="text-xs font-medium text-orange-400 bg-orange-500/10 border border-orange-500/20 px-2 py-1 rounded-full flex items-center gap-1">
              <ArrowUpRight className="h-3 w-3" /> +12%
            </span>
          </div>
          <div className="relative z-10">
            <p className="text-sm text-slate-400 font-medium">Monthly Spend</p>
            <h3 className="text-3xl font-bold text-white mt-1 tracking-tight">£1,420.50</h3>
          </div>
          <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
            <TrendingDown className="h-32 w-32 text-orange-500" />
          </div>
        </BentoCard>

        {/* Metric 3: Runway */}
        <BentoCard className="md:col-span-1 lg:col-span-2 p-6 flex flex-col justify-between" delay={0.3}>
          <div className="flex items-start justify-between relative z-10">
            <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-2xl">
              <TrendingUp className="h-6 w-6 text-emerald-500" />
            </div>
            <div className="bg-white/5 rounded-full p-2 hover:bg-white/10 transition-colors cursor-pointer">
              <MoreHorizontal className="h-5 w-5 text-slate-400" />
            </div>
          </div>
          <div className="relative z-10 grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-slate-400 font-medium">Runway</p>
              <h3 className="text-3xl font-bold text-white mt-1 tracking-tight">4.2 Months</h3>
            </div>
            <div className="border-l border-white/5 pl-6">
              <p className="text-sm text-slate-400 font-medium">Safety Net</p>
              <h3 className="text-3xl font-bold text-white mt-1 tracking-tight">£5,000</h3>
            </div>
          </div>
          <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
            <TrendingUp className="h-48 w-48 text-emerald-500" />
          </div>
        </BentoCard>

        {/* Main Chart: AI Forecast */}
        <BentoCard className="md:col-span-2 lg:col-span-3 row-span-2 p-8" delay={0.4}>
          <div className="flex items-center justify-between mb-8">
            <div>
              <h3 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
                AI Projection
              </h3>
              <p className="text-sm text-slate-400">30-day balance forecast based on spending habits</p>
            </div>
          </div>
          
          <div className="h-[320px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data?.forecast?.net_forecast}>
                <defs>
                  <linearGradient id="colorVal" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
                <XAxis 
                  dataKey="ds" 
                  tickFormatter={(str) => new Date(str).toLocaleDateString('en-GB', { day: 'numeric', month: 'short' })}
                  stroke="#64748b"
                  fontSize={12}
                  tickLine={false}
                  axisLine={false}
                />
                <YAxis 
                  stroke="#64748b"
                  fontSize={12}
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={(val) => `£${val}`}
                />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#151921', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', boxShadow: '0 4px 20px rgba(0,0,0,0.5)' }}
                  itemStyle={{ color: '#fff' }}
                  labelStyle={{ color: '#94a3b8', marginBottom: '4px', fontSize: '12px' }}
                  labelFormatter={(label) => new Date(label).toLocaleDateString('en-GB', { day: 'numeric', month: 'long' })}
                />
                <Area 
                  type="monotone" 
                  dataKey="val" 
                  stroke="#3b82f6" 
                  strokeWidth={3}
                  fillOpacity={1} 
                  fill="url(#colorVal)" 
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </BentoCard>

        {/* Recent Transactions List */}
        <BentoCard className="md:col-span-1 lg:col-span-1 row-span-2 p-6 flex flex-col" delay={0.5}>
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-bold text-white tracking-tight">Recent</h3>
            <Clock className="h-4 w-4 text-slate-500" />
          </div>
          
          <div className="space-y-3 overflow-y-auto pr-2 custom-scrollbar">
            {data?.recentTxns?.map((txn: any) => {
               const isIncome = txn.amount > 0;
               return (
                <div key={txn.txn_id} className="flex items-center justify-between p-3 rounded-2xl hover:bg-white/5 transition-colors border border-transparent hover:border-white/5 group">
                  <div className="flex items-center gap-3">
                    <div className={`h-10 w-10 rounded-xl flex items-center justify-center text-xs font-bold transition-transform group-hover:scale-105 ${
                      isIncome 
                        ? 'bg-emerald-500/10 text-emerald-500 border border-emerald-500/20' 
                        : 'bg-slate-700/30 text-slate-300 border border-white/5'
                    }`}>
                      {txn.merchant ? txn.merchant.charAt(0) : '?'}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-white truncate max-w-[100px]">
                        {txn.merchant || txn.description}
                      </p>
                      <p className="text-xs text-slate-500">
                        {new Date(txn.booked_at).toLocaleDateString('en-GB', { day: 'numeric', month: 'short' })}
                      </p>
                    </div>
                  </div>
                  <span className={`text-sm font-bold ${isIncome ? 'text-emerald-400' : 'text-white'}`}>
                    {isIncome ? '+' : ''}£{Math.abs(txn.amount).toFixed(0)}
                  </span>
                </div>
               );
            })}
            
            {(!data?.recentTxns || data.recentTxns.length === 0) && (
              <p className="text-sm text-slate-500 text-center py-4">No recent activity</p>
            )}
          </div>
        </BentoCard>

      </div>
    </div>
  );
}
