import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { CandidateComparisonResponse } from '../types/review';
import { CoverageBadge } from '../components/CoverageBadge';
import { StatusBadge } from '../components/StatusBadge';
import { ArrowLeft, Columns3, Scale, AlertTriangle, Layers, AlertCircle } from 'lucide-react';

interface ComparisonPageProps {
  reviewId: string;
  candidateIds: number[];
  onBack: () => void;
}

export const ComparisonPage: React.FC<ComparisonPageProps> = ({
  reviewId,
  candidateIds,
  onBack,
}) => {
  const [data, setData] = useState<CandidateComparisonResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    loadComparison();
  }, [reviewId, candidateIds]);

  const loadComparison = async () => {
    try {
      setIsLoading(true);
      setErrorMsg(null);
      const res = await api.getComparison(reviewId, candidateIds);
      setData(res);
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to load side-by-side comparison');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="py-24 text-center space-y-3">
        <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto" />
        <p className="text-xs text-slate-500 font-mono">Building side-by-side comparative matrix...</p>
      </div>
    );
  }

  if (errorMsg || !data) {
    return (
      <div className="p-8 max-w-2xl mx-auto bg-rose-50 border border-rose-200 rounded-xl text-center space-y-4">
        <AlertCircle className="w-8 h-8 text-rose-600 mx-auto" />
        <h2 className="text-base font-bold text-rose-900">Comparison Failed</h2>
        <p className="text-xs text-rose-700">{errorMsg}</p>
        <button
          onClick={onBack}
          className="px-4 py-2 bg-slate-800 text-white text-xs font-semibold rounded-lg"
        >
          Back to Review
        </button>
      </div>
    );
  }

  const standards = data.candidates.map((c) => c.is_number);

  return (
    <div className="max-w-6xl mx-auto space-y-6 pb-20">
      {/* Top Header */}
      <div className="flex items-center justify-between">
        <button
          type="button"
          onClick={onBack}
          className="flex items-center gap-1.5 text-xs font-semibold text-slate-600 hover:text-slate-900 bg-white border border-slate-200 px-3 py-1.5 rounded-lg shadow-sm transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Workspace</span>
        </button>

        <span className="text-xs text-slate-500 font-mono">
          Comparing {data.candidates.length} Candidate Standards for Review {reviewId}
        </span>
      </div>

      <div className="bg-slate-900 text-white p-6 rounded-xl border border-slate-800 shadow-md">
        <div className="flex items-center gap-2 text-blue-400 font-bold uppercase tracking-wider text-xs mb-1">
          <Columns3 className="w-4 h-4" />
          <span>Factual Comparative Analysis</span>
        </div>
        <h1 className="text-lg font-bold text-slate-100">
          Side-by-Side Candidate Standards Comparison
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Evaluates dimension alignment, regulatory Quality Control Orders, and gap profiles without synthetic aggregate scoring.
        </p>
      </div>

      {/* 1. FACET COMPARISON TABLE */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
          <h2 className="text-xs font-bold uppercase tracking-wider text-slate-800 flex items-center gap-2">
            <Layers className="w-4 h-4 text-blue-600" />
            1. Requirement & Retrieval Dimensions
          </h2>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse procurement-table">
            <thead>
              <tr>
                <th className="w-1/4">Dimension</th>
                {data.candidates.map((c) => (
                  <th key={c.id} className="text-center font-mono">
                    <span className="font-bold text-sm text-slate-900">{c.is_number}</span>
                    <span className="block text-[10px] text-slate-500 font-normal">Rank #{c.retrieval_rank}</span>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.facet_comparison.map((row, idx) => (
                <tr key={idx} className="hover:bg-slate-50/60">
                  <td className="font-semibold text-slate-700">{row.dimension}</td>
                  {standards.map((isNum) => {
                    const val = row.values[isNum];
                    if (row.dimension === 'Product Match Status') {
                      return (
                        <td key={isNum} className="text-center">
                          <CoverageBadge status={val} />
                        </td>
                      );
                    }
                    if (row.dimension === 'AI Recommendation') {
                      return (
                        <td key={isNum} className="text-center">
                          <StatusBadge status={val} type="ai" size="sm" />
                        </td>
                      );
                    }
                    return (
                      <td key={isNum} className="text-center font-mono text-xs text-slate-800">
                        {val !== undefined && val !== null ? String(val) : '—'}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 2. REGULATORY COMPARISON TABLE */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
          <h2 className="text-xs font-bold uppercase tracking-wider text-slate-800 flex items-center gap-2">
            <Scale className="w-4 h-4 text-blue-600" />
            2. Regulatory & Quality Control Orders
          </h2>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse procurement-table">
            <thead>
              <tr>
                <th className="w-1/4">Regulatory Dimension</th>
                {data.candidates.map((c) => (
                  <th key={c.id} className="text-center font-mono">
                    <span className="font-bold text-xs text-slate-900">{c.is_number}</span>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.regulatory_comparison.map((row, idx) => (
                <tr key={idx} className="hover:bg-slate-50/60">
                  <td className="font-semibold text-slate-700">{row.dimension}</td>
                  {standards.map((isNum) => {
                    const val = row.values[isNum];
                    return (
                      <td key={isNum} className="text-center font-mono text-xs text-slate-800">
                        {val || '—'}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 3. GAPS & VERIFICATION BURDEN */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
          <h2 className="text-xs font-bold uppercase tracking-wider text-slate-800 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-600" />
            3. Specification Gaps & Officer Verification Burden
          </h2>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse procurement-table">
            <thead>
              <tr>
                <th className="w-1/4">Gap Metric</th>
                {data.candidates.map((c) => (
                  <th key={c.id} className="text-center font-mono">
                    <span className="font-bold text-xs text-slate-900">{c.is_number}</span>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.gaps_comparison.map((row, idx) => (
                <tr key={idx} className="hover:bg-slate-50/60">
                  <td className="font-semibold text-slate-700">{row.dimension}</td>
                  {standards.map((isNum) => {
                    const val = row.values[isNum];
                    return (
                      <td key={isNum} className="text-center font-mono text-xs font-bold text-slate-900">
                        {val}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
