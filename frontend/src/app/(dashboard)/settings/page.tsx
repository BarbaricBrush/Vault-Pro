'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import api from '@/lib/api';
import { 
  Loader2, 
  Plus, 
  Trash2, 
  CheckCircle2,
  AlertCircle,
  Banknote,
  Palette,
  User
} from 'lucide-react';
import ThemeToggle from '@/components/ThemeToggle';

interface Connection {
  id: number;
  provider: string;
  status: string;
  created_at: string;
}

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState('banks');
  const [connections, setConnections] = useState<Connection[]>([]);
  const [loading, setLoading] = useState(true);
  const searchParams = useSearchParams();
  const router = useRouter();
  const [successMsg, setSuccessMsg] = useState('');

  useEffect(() => {
    if (searchParams.get('success') === 'true') {
      setSuccessMsg('Bank connected successfully!');
      router.replace('/settings');
    }
    fetchConnections();
  }, [searchParams, router]);

  async function fetchConnections() {
    try {
      const res = await api.get('/api/connections');
      setConnections(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  async function handleConnect() {
    try {
      const res = await api.get('/auth/start');
      const startUrl = res.data?.url;
      if (startUrl) {
        window.location.href = startUrl;
      } else {
        throw new Error('Missing auth URL');
      }
    } catch (err) {
      console.error("Failed to start auth", err);
    }
  }

  async function handleRevoke(id: number) {
    if (!confirm("Are you sure you want to disconnect this bank? Data will be retained but sync will stop.")) return;
    try {
      await api.delete(`/api/connections/${id}`);
      fetchConnections();
    } catch (err) {
      alert("Failed to delete connection");
    }
  }

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  const tabs = [
    { id: 'banks', label: 'Connected Banks', icon: Banknote },
    { id: 'preferences', label: 'Preferences', icon: Palette },
    { id: 'profile', label: 'Profile', icon: User },
  ];

  return (
    <div className="space-y-8 animate-in fade-in duration-500 max-w-4xl mx-auto">
      <div>
        <h2 className="text-2xl font-bold text-foreground">Settings</h2>
        <p className="text-slate-400 text-sm">Manage your account and preferences</p>
      </div>

      {successMsg && (
        <div className="bg-emerald-500/10 border border-emerald-500/20 text-emerald-500 p-4 rounded-xl flex items-center gap-3">
          <CheckCircle2 className="h-5 w-5" />
          {successMsg}
        </div>
      )}

      {/* Tabs Header */}
      <div className="flex border-b border-white/10 space-x-6">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 pb-3 text-sm font-medium transition-colors relative ${
              activeTab === tab.id ? 'text-blue-500' : 'text-slate-400 hover:text-foreground'
            }`}
          >
            <tab.icon className="h-4 w-4" />
            {tab.label}
            {activeTab === tab.id && (
              <span className="absolute bottom-0 left-0 w-full h-0.5 bg-blue-500 rounded-t-full" />
            )}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="glass-panel rounded-2xl p-6">
        
        {/* BANKS TAB */}
        {activeTab === 'banks' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-foreground">Bank Connections</h3>
                <p className="text-sm text-slate-400">Connect your bank accounts securely via TrueLayer</p>
              </div>
              <button 
                onClick={handleConnect}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-sm font-medium transition-colors shadow-lg shadow-blue-600/20"
              >
                <Plus className="h-4 w-4" />
                Connect New Bank
              </button>
            </div>

            <div className="space-y-4">
              {connections.length === 0 ? (
                <div className="text-center py-12 text-slate-500 border-2 border-dashed border-white/5 rounded-xl">
                  <p>No banks connected yet.</p>
                </div>
              ) : (
                connections.map((conn) => (
                  <div key={conn.id} className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/5">
                    <div className="flex items-center gap-4">
                      <div className="h-10 w-10 bg-white/10 rounded-full flex items-center justify-center text-lg font-bold text-foreground">
                        {conn.provider?.charAt(0).toUpperCase() || 'B'}
                      </div>
                      <div>
                        <p className="text-foreground font-medium capitalize">
                          {conn.provider?.replace('uk-ob-', '').replace('-', ' ') || 'Unknown Bank'}
                        </p>
                        <p className="text-xs text-slate-500">
                          ID: {conn.id} • Added {new Date(conn.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-4">
                      <span className="px-2 py-1 bg-emerald-500/10 text-emerald-500 text-xs font-medium rounded-lg capitalize border border-emerald-500/20">
                        {conn.status}
                      </span>
                      <button 
                        onClick={() => handleRevoke(conn.id)}
                        className="p-2 text-slate-500 hover:text-red-500 hover:bg-red-500/10 rounded-lg transition-colors"
                        title="Revoke Access"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {/* PREFERENCES TAB */}
        {activeTab === 'preferences' && (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-foreground">Appearance</h3>
            <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/5">
              <div>
                <p className="text-foreground font-medium">Theme Mode</p>
                <p className="text-sm text-slate-400">Switch between dark and light appearance</p>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-sm text-slate-500 mr-2">Toggle:</span>
                <ThemeToggle />
              </div>
            </div>
          </div>
        )}

        {/* PROFILE TAB */}
        {activeTab === 'profile' && (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-foreground">Profile</h3>
            <div className="p-6 bg-white/5 rounded-xl border border-white/5 flex items-center gap-6">
              <div className="h-20 w-20 bg-blue-600 rounded-full flex items-center justify-center text-3xl font-bold text-white shadow-lg">
                A
              </div>
              <div>
                <h4 className="text-xl font-bold text-foreground">Admin User</h4>
                <p className="text-slate-400">admin@example.com</p>
                <span className="inline-block mt-2 px-2 py-1 bg-blue-500/10 text-blue-500 text-xs font-medium rounded-lg border border-blue-500/20">
                  Administrator
                </span>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
