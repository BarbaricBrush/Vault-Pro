'use client';

import { useEffect, useState } from 'react';
import api from '@/lib/api';
import { 
  Loader2, 
  Search, 
  ArrowUp, 
  ArrowDown,
  Download
} from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface Transaction {
  txn_id: string;
  booked_at: string;
  amount: number;
  description: string;
  merchant?: string;
  category: string;
  classification: 'bill' | 'income' | 'variable';
  provider_id?: string;
}

type SortField = 'date' | 'amount';
type SortOrder = 'asc' | 'desc';

export default function TransactionsPage() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('all'); // all, bill, income, variable
  const [sortField, setSortField] = useState<SortField>('date');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');

  useEffect(() => {
    async function fetchTxns() {
      try {
        const res = await api.get('/api/transactions');
        setTransactions(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    fetchTxns();
  }, []);

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('desc');
    }
  };

  const filteredTxns = transactions
    .filter(t => {
      const matchesSearch = t.description.toLowerCase().includes(search.toLowerCase()) || 
                            (t.merchant && t.merchant.toLowerCase().includes(search.toLowerCase()));
      const matchesFilter = filter === 'all' || t.classification === filter;
      return matchesSearch && matchesFilter;
    })
    .sort((a, b) => {
      const multiplier = sortOrder === 'asc' ? 1 : -1;
      
      if (sortField === 'date') {
        return multiplier * (new Date(a.booked_at).getTime() - new Date(b.booked_at).getTime());
      }
      
      if (sortField === 'amount') {
        return multiplier * (a.amount - b.amount);
      }
      
      return 0;
    });

  const handleDownloadCSV = () => {
    const headers = ['Date', 'Description', 'Merchant', 'Category', 'Type', 'Amount'];
    const rows = filteredTxns.map(t => [
      new Date(t.booked_at).toLocaleDateString('en-GB'),
      `"${t.description.replace(/"/g, '""')}"`, // Escape quotes
      `"${(t.merchant || '').replace(/"/g, '""')}"`,
      t.category,
      t.classification,
      t.amount.toFixed(2)
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `transactions_export_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex flex-col md:flex-row gap-4 justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-white">Transactions</h2>
          <p className="text-slate-400 text-sm">Review your spending activity</p>
        </div>
        
        <div className="flex flex-wrap gap-2 w-full md:w-auto">
          <div className="relative flex-1 min-w-[200px] md:w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
            <input 
              type="text" 
              placeholder="Search..." 
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-[#1e212b] border border-white/10 rounded-xl pl-10 pr-4 py-2 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-600 text-sm"
            />
          </div>
          
          <select 
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="bg-[#1e212b] border border-white/10 rounded-xl px-4 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
          >
            <option value="all">All Types</option>
            <option value="bill">Bills</option>
            <option value="income">Income</option>
            <option value="variable">Variable</option>
          </select>

          <button 
            onClick={() => handleSort('date')}
            className={cn(
              "flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium border transition-colors",
              sortField === 'date' 
                ? "bg-blue-600/10 border-blue-600/20 text-blue-500" 
                : "bg-[#1e212b] border-white/10 text-slate-400 hover:text-white"
            )}
          >
            Date
            {sortField === 'date' && (sortOrder === 'asc' ? <ArrowUp className="h-3 w-3" /> : <ArrowDown className="h-3 w-3" />)}
          </button>

          <button 
            onClick={() => handleSort('amount')}
            className={cn(
              "flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium border transition-colors",
              sortField === 'amount' 
                ? "bg-blue-600/10 border-blue-600/20 text-blue-500" 
                : "bg-[#1e212b] border-white/10 text-slate-400 hover:text-white"
            )}
          >
            Amount
            {sortField === 'amount' && (sortOrder === 'asc' ? <ArrowUp className="h-3 w-3" /> : <ArrowDown className="h-3 w-3" />)}
          </button>

          <button 
            onClick={handleDownloadCSV}
            className="flex items-center gap-2 px-4 py-2 bg-[#1e212b] border border-white/10 hover:bg-white/5 text-slate-400 hover:text-white rounded-xl text-sm font-medium transition-colors"
            title="Download CSV"
          >
            <Download className="h-4 w-4" />
          </button>
        </div>
      </div>

      <div className="bg-[#1e212b] rounded-2xl border border-white/5 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-white/5 text-slate-400 text-xs uppercase tracking-wider">
                <th 
                  className="px-6 py-4 font-medium cursor-pointer hover:text-white transition-colors"
                  onClick={() => handleSort('date')}
                >
                  <div className="flex items-center gap-1">
                    Date
                    {sortField === 'date' && (sortOrder === 'asc' ? <ArrowUp className="h-3 w-3" /> : <ArrowDown className="h-3 w-3" />)}
                  </div>
                </th>
                <th className="px-6 py-4 font-medium">Description</th>
                <th className="px-6 py-4 font-medium">Category</th>
                <th className="px-6 py-4 font-medium">AI Type</th>
                <th 
                  className="px-6 py-4 font-medium text-right cursor-pointer hover:text-white transition-colors"
                  onClick={() => handleSort('amount')}
                >
                  <div className="flex items-center gap-1 justify-end">
                    Amount
                    {sortField === 'amount' && (sortOrder === 'asc' ? <ArrowUp className="h-3 w-3" /> : <ArrowDown className="h-3 w-3" />)}
                  </div>
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {filteredTxns.map((txn) => {
                const isIncome = txn.amount > 0;
                
                // Row Styling based on AI Classification
                let rowClass = "hover:bg-white/5 transition-colors";
                let badgeClass = "bg-slate-500/10 text-slate-400";
                
                if (txn.classification === 'bill') {
                  rowClass = "bg-red-500/5 hover:bg-red-500/10";
                  badgeClass = "bg-red-500/10 text-red-400 border border-red-500/20";
                } else if (txn.classification === 'income') {
                  rowClass = "bg-emerald-500/5 hover:bg-emerald-500/10";
                  badgeClass = "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20";
                } else {
                  badgeClass = "bg-blue-500/10 text-blue-400 border border-blue-500/20";
                }

                return (
                  <tr key={txn.txn_id} className={rowClass}>
                    <td className="px-6 py-4 text-sm text-slate-300 whitespace-nowrap">
                      {new Date(txn.booked_at).toLocaleDateString('en-GB', { day: '2-digit', month: 'short' })}
                    </td>
                    <td className="px-6 py-4 text-sm text-white font-medium">
                      <div className="flex flex-col">
                        <span>{txn.merchant || txn.description}</span>
                        {txn.merchant && <span className="text-xs text-slate-500 font-normal">{txn.description}</span>}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-slate-400">
                      {txn.category}
                    </td>
                    <td className="px-6 py-4">
                      <span className={cn("px-2 py-1 rounded-full text-xs font-medium capitalize", badgeClass)}>
                        {txn.classification}
                      </span>
                    </td>
                    <td className={cn(
                      "px-6 py-4 text-sm font-bold text-right",
                      isIncome ? "text-emerald-500" : "text-white"
                    )}>
                      {isIncome ? '+' : ''}£{Math.abs(txn.amount).toFixed(2)}
                    </td>
                  </tr>
                );
              })}
              {filteredTxns.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center text-slate-500">
                    <p>No transactions found.</p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
