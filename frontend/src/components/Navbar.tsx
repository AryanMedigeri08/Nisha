import React from 'react';
import { ShieldCheck, PlusCircle, LayoutDashboard, History, Info, ExternalLink } from 'lucide-react';

interface NavbarProps {
  currentTab: string;
  onNavigate: (tab: string, reviewId?: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ currentTab, onNavigate }) => {
  return (
    <header className="bg-slate-900 border-b border-slate-800 text-white sticky top-0 z-40">
      {/* Disclaimer Bar */}
      <div className="bg-amber-950/60 border-b border-amber-900/40 px-4 py-1 text-center text-xs text-amber-200/90 flex items-center justify-center gap-1.5 font-medium">
        <Info className="w-3.5 h-3.5 text-amber-400 shrink-0" />
        <span>
          Decision-support prototype. Regulatory applicability and final procurement decisions require authorized human officer verification.
        </span>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-14">
          {/* Brand & Project Info */}
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => onNavigate('dashboard')}>
            <div className="w-8 h-8 rounded bg-blue-600 flex items-center justify-center font-bold text-white shadow-sm">
              PS
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-semibold text-sm tracking-tight text-white">
                  PS26108 — Indian Standards Engine
                </span>
                <span className="text-[10px] bg-slate-800 text-slate-300 font-mono px-1.5 py-0.5 rounded border border-slate-700">
                  Phase 7 HITL
                </span>
              </div>
              <p className="text-[11px] text-slate-400 leading-none">
                Evidence-Backed Procurement Decision Support
              </p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="flex items-center gap-1 sm:gap-2">
            <button
              onClick={() => onNavigate('dashboard')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
                currentTab === 'dashboard'
                  ? 'bg-blue-600 text-white'
                  : 'text-slate-300 hover:text-white hover:bg-slate-800'
              }`}
            >
              <LayoutDashboard className="w-4 h-4" />
              <span>Dashboard</span>
            </button>

            <button
              onClick={() => onNavigate('new-query')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
                currentTab === 'new-query'
                  ? 'bg-blue-600 text-white'
                  : 'text-slate-300 hover:text-white hover:bg-slate-800'
              }`}
            >
              <PlusCircle className="w-4 h-4" />
              <span>New Tender Query</span>
            </button>

            <button
              onClick={() => onNavigate('reviews')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
                currentTab === 'reviews'
                  ? 'bg-blue-600 text-white'
                  : 'text-slate-300 hover:text-white hover:bg-slate-800'
              }`}
            >
              <History className="w-4 h-4" />
              <span>Review Queue</span>
            </button>

            <a
              href="/docs"
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-1 px-2.5 py-1.5 rounded-md text-xs font-medium text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
              title="FastAPI OpenAPI Documentation"
            >
              <span>API Docs</span>
              <ExternalLink className="w-3 h-3" />
            </a>
          </nav>
        </div>
      </div>
    </header>
  );
};
