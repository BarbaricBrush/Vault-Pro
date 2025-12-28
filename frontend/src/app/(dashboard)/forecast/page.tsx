'use client';

import { useEffect, useState } from 'react';
import api from '@/lib/api';
import { 
  Loader2, 
  TrendingUp, 
  Calendar,
  AlertCircle
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

export default function ForecastPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState(30);

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      try {
        const res = await api.get(`/api/forecast?days=${days}`);
        setData(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [days]);

  if (loading && !data) {
    return (
      <div className="h-full flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  const startVal = data?.net_forecast?.[0]?.val || 0;
  const endVal = data?.net_forecast?.[data.net_forecast.length - 1]?.val || 0;
  const delta = endVal - startVal;
  const isPositive = delta >= 0;

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="flex flex-col md:flex-row gap-4 justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-white">Financial Forecast</h2>
          <p className="text-slate-400 text-sm">AI-driven projection of your future balance</p>
        </div>
        
        <div className="flex bg-[#1e212b] p-1 rounded-xl border border-white/10">
          {[30, 60, 90].map((d) => (
            <button
              key={d}
              onClick={() => setDays(d)}
              className={`px-4 py-2 text-sm font-medium rounded-lg transition-all ${
                days === d 
                  ? 'bg-blue-600 text-white shadow-lg' 
                  : 'text-slate-400 hover:text-white hover:bg-white/5'
              }`}
            >
              {d} Days
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-[#1e212b] p-6 rounded-2xl border border-white/5">
          <p className="text-sm text-slate-400 font-medium">Projected Change</p>
          <div className="flex items-end gap-2 mt-1">
            <h3 className={`text-3xl font-bold ${isPositive ? 'text-emerald-500' : 'text-red-500'}`}>
              {isPositive ? '+' : ''}£{Math.abs(delta).toLocaleString(undefined, { minimumFractionDigits: 2 })}
            </h3>
            <span className="text-sm text-slate-500 mb-1">over next {days} days</span>
          </div>
        </div>
        
        <div className="bg-[#1e212b] p-6 rounded-2xl border border-white/5">
          <p className="text-sm text-slate-400 font-medium">Predicted End Balance</p>
          <h3 className="text-3xl font-bold text-white mt-1">
            £{endVal.toLocaleString(undefined, { minimumFractionDigits: 2 })}
          </h3>
        </div>
      </div>

      <div className="bg-[#1e212b] p-8 rounded-2xl border border-white/5 h-[500px]">
        {data?.net_forecast ? (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data.net_forecast}>
              <defs>
                <linearGradient id="colorForecast" x1="0" y1="0" x2="0" y2="1">
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
                minTickGap={30}
              />
              <YAxis 
                stroke="#64748b"
                fontSize={12}
                tickLine={false}
                axisLine={false}
                tickFormatter={(val) => `£${val}`}
              />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1e212b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px' }}
                itemStyle={{ color: '#fff' }}
                labelStyle={{ color: '#64748b', marginBottom: '4px' }}
                labelFormatter={(label) => new Date(label).toLocaleDateString('en-GB', { day: 'numeric', month: 'long' })}
              />
              <Area 
                type="monotone" 
                dataKey="val" 
                stroke="#3b82f6" 
                strokeWidth={3}
                fillOpacity={1} 
                fill="url(#colorForecast)" 
                name="Projected Balance"
              />
            </AreaChart>
          </ResponsiveContainer>
        ) : (
          <div className="h-full flex flex-col items-center justify-center text-slate-500">
            <AlertCircle className="h-10 w-10 mb-4 opacity-50" />
            <p>Not enough data to generate a forecast yet.</p>
          </div>
        )}
      </div>
    </div>
  );
}
