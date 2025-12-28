'use client';

import { useState, useEffect, type FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';
import { Loader2, ArrowRight, Lightbulb } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import InteractiveBackground from '@/components/InteractiveBackground';
import BrandLogo from '@/components/BrandLogo';
import Link from 'next/link';

const FACTS = [
  "The £20,000 Shield: You can save up to £20,000 tax-free every year in an ISA. Use it or lose it before April 5th!",
  "LISA Bonus: Aged 18–39? Save up to £4,000/year in a Lifetime ISA and the government adds a 25% bonus (£1,000 free) for your first home.",
  "Pension Power: For every £80 a basic-rate taxpayer saves in a pension, the government adds £20 tax relief automatically.",
  "Free Money: Always max out your employer's pension match. Not doing so is like turning down a pay rise.",
  "The Loyalty Penalty: Switching insurance or broadband at the end of a contract saves the average UK household over £300/year.",
  "Credit Score Tip: Aim to use less than 30% of your credit limit to keep your score healthy.",
  "FSCS Protection: The first £85,000 of your savings in a UK-regulated bank is 100% protected if the bank goes bust.",
  "The 50/30/20 Rule: 50% Needs, 30% Wants, 20% Savings. A solid baseline for UK budgets.",
  "Inflation Reality: If inflation is 3% and your savings pay 1%, your money is losing value. Invest or find better rates.",
  "Council Tax: Live alone? Claim your 25% Single Person Discount.",
  "Zombie Subs: The average person can save £1,000+ a year just by cancelling unused subscriptions.",
  "Emergency Fund: 26% of UK adults can't pay an unexpected £850 bill without borrowing. Build your safety net."
];

export default function LoginPage() {
  const [loading, setLoading] = useState(false);
  const [factIndex, setFactIndex] = useState(0);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const router = useRouter();

  useEffect(() => {
    // Cycle facts every 30 seconds
    const interval = setInterval(() => {
      setFactIndex((prev) => (prev + 1) % FACTS.length);
    }, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleLogin = async (e?: FormEvent) => {
    e?.preventDefault();
    setLoading(true);
    setError('');
    try {
      const formData = new FormData();
      formData.append('username', email);
      formData.append('password', password);

      const resp = await api.post('/auth/token', formData);
      localStorage.setItem('token', resp.data.access_token);
      router.push('/');
    } catch (err) {
      console.error("Login failed", err);
      setError('Invalid email or password.');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center relative overflow-hidden">
      {/* Dynamic Background Elements */}
      <InteractiveBackground />

      <div className="relative z-10 w-full max-w-2xl px-6 flex flex-col items-center text-center">
        
        {/* Logo / Brand */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="mb-8 w-full flex flex-col items-center"
        >
          {/* Fixed height required for Next/Image fill */}
          <BrandLogo className="w-[400px] h-[220px] drop-shadow-[0_0_30px_rgba(59,130,246,0.2)]" />
          <p className="text-lg text-slate-400 max-w-lg mx-auto mt-4">
            Next-generation financial intelligence.
          </p>
        </motion.div>

        {/* Fact Card */}
        <div className="h-32 mb-12 w-full flex items-center justify-center">
          <AnimatePresence mode="wait">
            <motion.div
              key={factIndex}
              initial={{ opacity: 0, y: 10, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -10, scale: 0.95 }}
              transition={{ duration: 0.5 }}
              className="glass-panel p-6 rounded-2xl border border-white/10 max-w-lg w-full relative"
            >
              <div className="absolute -top-3 -left-3 bg-blue-600 rounded-full p-2 shadow-lg">
                <Lightbulb className="h-4 w-4 text-white" />
              </div>
              <p className="text-slate-200 font-medium text-lg leading-relaxed">
                "{FACTS[factIndex]}"
              </p>
            </motion.div>
          </AnimatePresence>
        </div>

        {/* Action */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1, duration: 1 }}
          className="w-full max-w-md"
        >
          <form onSubmit={handleLogin} className="space-y-4">
            {error && (
              <div className="bg-red-500/10 border border-red-500/20 text-red-500 p-3 rounded-xl text-sm text-center">
                {error}
              </div>
            )}
            <div className="space-y-3">
              <input
                type="email"
                required
                placeholder="Email address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-[#0f1116] border border-white/10 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-600"
              />
              <input
                type="password"
                required
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-[#0f1116] border border-white/10 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-600"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="group w-full relative px-8 py-4 bg-white text-black rounded-full font-bold text-lg hover:scale-[1.02] transition-all duration-300 shadow-[0_0_20px_rgba(255,255,255,0.2)] hover:shadow-[0_0_40px_rgba(255,255,255,0.4)] disabled:opacity-70 disabled:scale-100 flex items-center justify-center gap-3"
            >
              {loading ? (
                <>
                  <Loader2 className="animate-spin h-5 w-5" />
                  Accessing Vault...
                </>
              ) : (
                <>
                  Enter Dashboard
                  <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
                </>
              )}
            </button>

            <p className="text-sm text-slate-500 text-center">
              New here?{' '}
              <Link href="/register" className="text-blue-400 hover:text-blue-300">
                Create an account
              </Link>
            </p>
          </form>
        </motion.div>

      </div>
    </div>
  );
}
