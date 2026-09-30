import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { ReviewDetailDTO } from '../types/review';
import { StatusBadge } from '../components/StatusBadge';
import { History, Search, Filter, RefreshCw, ArrowRight } from 'lucide-react';

interface ReviewListPageProps {
  onNavigate: (tab: string, reviewId?: string) => void;
}

export const ReviewListPage: React.FC<ReviewListPageProps> = ({ onNavigate }) => {
  const [reviews, setReviews] = useState<ReviewDetailDTO[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadReviews();
  }, [statusFilter]);

  const loadReviews = async () => {
    try {
      setIsLoading(true);
      const params = statusFilter !== 'ALL' ? { status: statusFilter } : undefined;
      const res = await api.listReviews(params);
      setReviews(res.reviews);
      setTotalCount(res.total);
    } catch (err) {
      console.error('Failed to load reviews:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const filteredReviews = reviews.filter((r) => {
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase();
    return (
      r.review_id.toLowerCase().includes(q) ||
      r.raw_text.toLowerCase().includes(q) ||
      (r.candidates && r.candidates.some((c) => c.is_number.toLowerCase().includes(q) || c.title.toLowerCase().includes(q)))
    );
  });

  return (
    <div className="space-y-6 pb-20">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <History className="w-5 h-5 text-blue-600" />
            Procurement Review Queue & History
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-0.5">
            Audit history, active review sessions, and finalized officer decisions
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={loadReviews}
            disabled={isLoading}
            className="p-2 text-slate-600 hover:text-slate-900 bg-white border border-slate-200 rounded-lg shadow-sm hover:bg-slate-50 transition-colors"
            title="Refresh list"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col sm:flex-row items-center justify-between gap-3">
        {/* Search */}
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search review ID, keywords, or IS number..."
            className="w-full pl-9 pr-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg text-slate-900 focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>

        {/* Status Filter Tabs */}
        <div className="flex items-center gap-1.5 overflow-x-auto w-full sm:w-auto pb-1 sm:pb-0">
          {['ALL', 'PENDING', 'UNDER_REVIEW', 'ACCEPTED', 'REJECTED', 'NEEDS_VERIFICATION'].map((st) => (
            <button
              key={st}
              onClick={() => setStatusFilter(st)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors shrink-0 ${
                statusFilter === st
                  ? 'bg-slate-900 text-white'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {st.replace('_', ' ')}
            </button>
          ))}
        </div>
      </div>

      {/* Reviews Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse procurement-table">
            <thead>
              <tr>
                <th className="w-28">Review ID</th>
                <th>Procurement Query</th>
                <th className="w-36">Top Candidate</th>
                <th className="w-32">Status</th>
                <th className="w-28">Verifications</th>
                <th className="w-28">Created</th>
                <th className="w-20 text-right">Action</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr>
                  <td colSpan={7} className="text-center py-12 text-xs text-slate-400 font-mono">
                    Loading review queue...
                  </td>
                </tr>
              ) : filteredReviews.length > 0 ? (
                filteredReviews.map((rev) => {
                  const topCand = rev.candidates && rev.candidates.length > 0 ? rev.candidates[0] : null;
                  const unresolvedV = rev.verification_items.filter((v) => v.officer_state === 'UNVERIFIED').length;

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
                      <td className="text-xs font-mono">
                        {unresolvedV > 0 ? (
                          <span className="text-amber-700 font-semibold">{unresolvedV} pending</span>
                        ) : (
                          <span className="text-emerald-700 font-medium">All cleared</span>
                        )}
                      </td>
                      <td className="text-[11px] text-slate-500 font-mono">
                        {rev.created_at ? new Date(rev.created_at).toLocaleDateString() : '—'}
                      </td>
                      <td className="text-right">
                        <button
                          onClick={() => onNavigate('workspace', rev.review_id)}
                          className="px-2.5 py-1 text-xs font-semibold bg-slate-900 hover:bg-blue-600 text-white rounded transition-colors"
                        >
                          Open
                        </button>
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={7} className="text-center py-12 text-xs text-slate-500">
                    No reviews found matching filter criteria.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
