'use client';

import { useEffect, useState, type ReactNode } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  CreditCard,
  Settings,
  LogOut,
  TrendingUp,
  Menu,
  X,
} from 'lucide-react';
import Link from 'next/link';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import ThemeToggle from '@/components/ThemeToggle';
import BrandLogo from '@/components/BrandLogo';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

const navItems = [
  { name: 'Overview', href: '/', icon: LayoutDashboard },
  { name: 'Transactions', href: '/transactions', icon: CreditCard },
  { name: 'Forecast', href: '/forecast', icon: TrendingUp },
];

export default function DashboardLayout({ children }: { children: ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [isAuthed, setIsAuthed] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.replace('/login');
      return;
    }
    setIsAuthed(true);
  }, [router]);

  useEffect(() => {
    setSidebarOpen(false);
  }, [pathname]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    router.push('/login');
  };

  if (!isAuthed) {
    return (
      <div className="min-h-screen flex items-center justify-center text-slate-400">
        Loading...
      </div>
    );
  }

  return (
    <div className="min-h-screen flex bg-background text-foreground">
      {sidebarOpen && (
        <button
          aria-label="Close sidebar"
          className="fixed inset-0 bg-black/40 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          'fixed inset-y-0 left-0 w-64 glass-sidebar z-50 transition-transform lg:translate-x-0 lg:sticky lg:top-0 lg:h-screen',
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className="h-full flex flex-col p-6">
          <div className="flex items-center justify-between mb-10 px-2">
            <div className="flex items-center gap-3">
              <BrandLogo
                className="h-10 w-10 drop-shadow-[0_0_10px_rgba(59,130,246,0.3)]"
                showText={false}
              />
              <span className="text-xl font-bold text-foreground tracking-tight">
                Vault
              </span>
            </div>
            <div className="flex items-center gap-2">
              <ThemeToggle />
              <button
                className="lg:hidden p-2 text-slate-400 hover:text-white hover:bg-white/5 rounded-xl"
                onClick={() => setSidebarOpen(false)}
                aria-label="Close menu"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          </div>

          <nav className="flex-1 space-y-1">
            {navItems.map((item) => {
              const active = pathname === item.href;
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  onClick={() => setSidebarOpen(false)}
                  className={cn(
                    'flex items-center gap-3 px-4 py-3 rounded-xl transition-all group duration-200',
                    active
                      ? 'bg-blue-600/10 text-blue-500 shadow-[0_0_20px_rgba(59,130,246,0.1)] border border-blue-500/10'
                      : 'text-slate-400 hover:bg-white/5 hover:text-white'
                  )}
                >
                  <item.icon
                    className={cn(
                      'h-5 w-5 transition-colors',
                      active
                        ? 'text-blue-500'
                        : 'text-slate-500 group-hover:text-white'
                    )}
                  />
                  <span className="font-medium text-sm">{item.name}</span>
                </Link>
              );
            })}
          </nav>

          <div className="mt-auto pt-6 border-t border-white/5 space-y-1">
            <Link
              href="/settings"
              className={cn(
                'flex items-center gap-3 px-4 py-3 rounded-xl transition-all group duration-200',
                pathname === '/settings'
                  ? 'bg-blue-600/10 text-blue-500 shadow-[0_0_20px_rgba(59,130,246,0.1)] border border-blue-500/10'
                  : 'text-slate-400 hover:bg-white/5 hover:text-white'
              )}
            >
              <Settings
                className={cn(
                  'h-5 w-5 transition-colors',
                  pathname === '/settings'
                    ? 'text-blue-500'
                    : 'text-slate-500 group-hover:text-white'
                )}
              />
              <span className="font-medium text-sm">Settings</span>
            </Link>

            <button
              onClick={handleLogout}
              className="flex items-center gap-3 px-4 py-3 w-full rounded-xl text-slate-400 hover:bg-red-500/10 hover:text-red-500 transition-all group"
            >
              <LogOut className="h-5 w-5 text-slate-500 group-hover:text-red-500" />
              <span className="font-medium text-sm">Sign Out</span>
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden relative">
        <header className="h-16 border-b border-white/5 flex items-center justify-between px-6 lg:px-10 bg-[#0B0E14]/50 backdrop-blur-md sticky top-0 z-30">
          <button
            className="lg:hidden p-2 text-slate-400 hover:text-white"
            onClick={() => setSidebarOpen(true)}
            aria-label="Open menu"
          >
            <Menu className="h-6 w-6" />
          </button>

          <div className="flex-1 lg:flex-none">
            <h1 className="text-lg font-semibold text-white truncate">
              {navItems.find((item) => item.href === pathname)?.name || 'Dashboard'}
            </h1>
          </div>

          <div className="flex items-center gap-4 text-slate-400 text-sm">
            <div className="px-3 py-1 rounded-full bg-white/5 border border-white/5 text-xs font-medium">
              {new Date().toLocaleDateString('en-GB', {
                weekday: 'short',
                day: 'numeric',
                month: 'short',
              })}
            </div>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-6 lg:p-10">{children}</div>
      </main>
    </div>
  );
}
