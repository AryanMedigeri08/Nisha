import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { DashboardStats, ReviewDetailDTO } from '../types/review';
import { StatusBadge } from '../components/StatusBadge';
import {
  FilePlus,
  History,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Clock,
  RefreshCw,
  Search,
  Database,
  ShieldAlert,
  ArrowRight,
} from 'lucide-react';

interface DashboardPageProps {
  onNavigate: (tab: string, reviewId?: string) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({ onNavigate }) => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      setIsLoading(true);
      const data = await api.getDashboardStats();
      setStats(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load dashboard metrics');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-8 pb-12">
      {/* Hero Banner */}
      <section className="bg-slate-900 text-white rounded-2xl p-8 border border-slate-800 shadow-xl relative overflow-hidden">
        <div className="relative z-10 max-w-3xl space-y-4">
          <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-blue-900/60 border border-blue-700 text-blue-300 text-xs font-medium">
            <Database className="w-3.5 h-3.5" />
            <span>91 Scheme-1 Standards • 35 QCO Orders Indexed</span>
          </div>

          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white">
            AI-Powered Indian Standards Recommendation Engine
          </h1>

          <p className="text-sm sm:text-base text-slate-300 leading-relaxed">
            Evidence-backed decision support for procurement standard identification.
            Extracts tender parameters, retrieves candidate BIS standards, verifies regulatory
            Quality Control Orders, and facilitates authorized human officer review.
          </p>

          <div className="flex items-center gap-3 pt-2 flex-wrap">
            <button
              onClick={() => onNavigate('new-query')}
              className="flex items-center gap-2 px-5 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-medium text-sm shadow-md transition-colors"
            >
              <FilePlus className="w-4 h-4" />
              <span>Start New Procurement Review</span>
            </button>

            <button
              onClick={() => onNavigate('reviews')}
              className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium text-sm border border-slate-700 transition-colors"
            >
              <History className="w-4 h-4" />
              <span>View Review Queue</span>
            </button>
          </div>
        </div>

        {/* Decorative background grid */}
        <div className="absolute right-0 top-0 bottom-0 w-1/3 opacity-10 bg-[radial-gradient(#3b82f6_1px,transparent_1px)] [background-size:16px_16px] pointer-events-none" />
      </section>

      {/* Operational Metrics Cards */}
      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-700 flex items-center gap-2">
            <Clock className="w-4 h-4 text-slate-500" />
            Operational Review Queue Metrics
          </h2>
          <span className="text-xs text-slate-500">Live system counters</span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          {/* Total Reviews */}
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <span className="text-xs font-semibold text-slate-500 block">Total Reviews</span>
            <span className="text-2xl font-bold text-slate-900 font-mono mt-1 block">
              {isLoading ? '...' : stats?.total_reviews || 0}
            </span>
            <span className="text-[10px] text-slate-400 mt-1 block">Tender sessions</span>
          </div>

          {/* Pending */}
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <span className="text-xs font-semibold text-slate-600 block flex items-center gap-1">
              <Clock className="w-3 h-3 text-slate-400" /> Pending
            </span>
            <span className="text-2xl font-bold text-slate-800 font-mono mt-1 block">
              {isLoading ? '...' : stats?.pending_reviews || 0}
            </span>
            <span className="text-[10px] text-slate-400 mt-1 block">Awaiting officer</span>
          </div>

          {/* Under Review */}
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <span className="text-xs font-semibold text-blue-700 block flex items-center gap-1">
              <RefreshCw className="w-3 h-3 text-blue-500" /> In Progress
            </span>
            <span className="text-2xl font-bold text-blue-800 font-mono mt-1 block">
              {isLoading ? '...' : stats?.under_review || 0}
            </span>
            <span className="text-[10px] text-blue-600 mt-1 block">Under examination</span>
          </div>

          {/* Accepted */}
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <span className="text-xs font-semibold text-emerald-700 block flex items-center gap-1">
              <CheckCircle2 className="w-3 h-3 text-emerald-500" /> Accepted
            </span>
            <span className="text-2xl font-bold text-emerald-800 font-mono mt-1 block">
              {isLoading ? '...' : stats?.accepted_reviews || 0}
            </span>
            <span className="text-[10px] text-emerald-600 mt-1 block">Standard approved</span>
          </div>

          {/* Rejected */}
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <span className="text-xs font-semibold text-rose-700 block flex items-center gap-1">
              <XCircle className="w-3 h-3 text-rose-500" /> Rejected
            </span>
            <span className="text-2xl font-bold text-rose-800 font-mono mt-1 block">
              {isLoading ? '...' : stats?.rejected_reviews || 0}
            </span>
            <span className="text-[10px] text-rose-600 mt-1 block">With reason codes</span>
          </div>

          {/* Needs Verification */}
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <span className="text-xs font-semibold text-amber-700 block flex items-center gap-1">
              <AlertCircle className="w-3 h-3 text-amber-500" /> Verification Req.
            </span>
            <span className="text-2xl font-bold text-amber-800 font-mono mt-1 block">
              {isLoading ? '...' : stats?.needs_verification_reviews || 0}
            </span>
            <span className="text-[10px] text-amber-600 mt-1 block">Action required</span>
          </div>
        </div>
      </section>

      {/* Recent Reviews Table */}
      <section className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-4 sm:p-5 border-b border-slate-200 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-900">Recent Procurement Reviews</h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Active decision support sessions and latest officer actions
            </p>
          </div>
          <button
            onClick={() => onNavigate('reviews')}
            className="text-xs font-semibold text-blue-600 hover:text-blue-800 flex items-center gap-1"
          >
            <span>View All</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse procurement-table">
            <thead>
              <tr>
                <th className="w-28">Review ID</th>
                <th>Procurement Query Summary</th>
                <th className="w-36">Top Candidate</th>
                <th className="w-32">Status</th>
                <th className="w-28">Created</th>
                <th className="w-20 text-right">Action</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr>
                  <td colSpan={6} className="text-center py-8 text-xs text-slate-400">
                    Loading recent reviews...
                  </td>
                </tr>
              ) : stats?.recent_reviews && stats.recent_reviews.length > 0 ? (
                stats.recent_reviews.map((rev) => {
                  const topCand = rev.candidates && rev.candidates.length > 0 ? rev.candidates[0] : null;
                  return (
                    <tr key={rev.review_id} className="hover:bg-slate-50/80 transition-colors">
                      <td className="font-mono text-xs font-semibold text-blue-600">
                        {rev.review_id}
                      </td>
                      <td className="max-w-md">
                        <p className="text-xs text-slate-900 font-medium line-clamp-1">
                          {rev.raw_text}
                        </p>
                      </td>
                      <td>
                        {topCand ? (
                          <span className="font-mono text-xs font-semibold text-slate-800 bg-slate-100 px-1.5 py-0.5 rounded border border-slate-200">
                            {topCand.is_number}
                          </span>
                        ) : (
                          <span className="text-xs text-slate-400 italic">None</span>
                        )}
                      </td>
                      <td>
                        <StatusBadge status={rev.status} type="officer" size="sm" />
                      </td>
                      <td className="text-[11px] text-slate-500 font-mono">
                        {rev.created_at ? new Date(rev.created_at).toLocaleDateString() : '—'}
                      </td>
                      <td className="text-right">
                        <button
                          onClick={() => onNavigate('workspace', rev.review_id)}
                          className="px-2.5 py-1 text-xs font-semibold bg-slate-900 hover:bg-blue-600 text-white rounded transition-colors"
                        >
                          Review
                        </button>
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={6} className="text-center py-8 text-xs text-slate-500">
                    No reviews yet. Start by entering a new procurement query above!
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
};
