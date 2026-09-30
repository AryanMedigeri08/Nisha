import React from 'react';
import { CandidateDTO } from '../types/review';
import { StatusBadge } from './StatusBadge';
import { CoverageBadge } from './CoverageBadge';
import {
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  FileText,
  Scale,
  Eye,
  CheckCircle2,
} from 'lucide-react';

interface CandidateCardProps {
  candidate: CandidateDTO;
  isSelected?: boolean;
  onSelect: (candidate: CandidateDTO) => void;
  onCompareToggle?: (candidateId: number) => void;
  isCompareSelected?: boolean;
  onViewDetails: (candidate: CandidateDTO) => void;
}

export const CandidateCard: React.FC<CandidateCardProps> = ({
  candidate,
  isSelected,
  onSelect,
  onCompareToggle,
  isCompareSelected,
  onViewDetails,
}) => {
  const cov = candidate.requirement_coverage;
  const numGaps = candidate.gaps?.length || 0;
  const highGaps = candidate.gaps?.filter((g) => g.severity === 'HIGH').length || 0;
  const evidenceCount = candidate.evidence?.length || 0;

  return (
    <div
      className={`p-4 rounded-xl border transition-all ${
        isSelected
          ? 'bg-blue-50/40 border-blue-500 shadow-md ring-1 ring-blue-500'
          : 'bg-white border-slate-200 hover:border-slate-300 hover:shadow-sm'
      }`}
    >
      {/* Header with Rank and Badges */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-2.5">
          <div className="w-7 h-7 rounded bg-slate-900 text-white font-mono font-bold text-xs flex items-center justify-center shrink-0">
            #{candidate.retrieval_rank}
          </div>
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <h4 className="text-sm font-bold text-slate-900 font-mono">
                {candidate.is_number}
              </h4>
              <StatusBadge status={candidate.ai_recommendation_state} type="ai" size="sm" />
            </div>
            <p className="text-xs text-slate-600 mt-0.5 line-clamp-2 leading-snug">
              {candidate.title}
            </p>
          </div>
        </div>

        {onCompareToggle && (
          <label className="flex items-center gap-1.5 text-xs text-slate-600 cursor-pointer select-none bg-slate-50 hover:bg-slate-100 px-2 py-1 rounded border border-slate-200">
            <input
              type="checkbox"
              checked={isCompareSelected}
              onChange={() => onCompareToggle(candidate.id)}
              className="rounded text-blue-600 focus:ring-blue-500 w-3.5 h-3.5"
            />
            <span className="text-[11px] font-medium">Compare</span>
          </label>
        )}
      </div>

      {/* Requirement Coverage Breakdown */}
      {cov && (
        <div className="mt-3 p-2.5 bg-slate-50 rounded-lg border border-slate-200/80">
          <div className="text-[11px] font-semibold text-slate-600 uppercase tracking-wider mb-1.5 flex items-center justify-between">
            <span>Requirement Coverage:</span>
            <span className="font-mono text-[10px] text-slate-500">
              Rerank: {candidate.reranker_score !== null && candidate.reranker_score !== undefined ? candidate.reranker_score.toFixed(3) : 'N/A'}
            </span>
          </div>

          <div className="grid grid-cols-4 gap-1.5 text-center">
            <div className="p-1 rounded bg-emerald-50 border border-emerald-200">
              <span className="block text-xs font-bold text-emerald-800 font-mono">
                {cov.direct_matches}
              </span>
              <span className="text-[9px] text-emerald-700 font-medium">Direct</span>
            </div>
            <div className="p-1 rounded bg-amber-50 border border-amber-200">
              <span className="block text-xs font-bold text-amber-800 font-mono">
                {cov.partial_matches}
              </span>
              <span className="text-[9px] text-amber-700 font-medium">Partial</span>
            </div>
            <div className="p-1 rounded bg-slate-100 border border-slate-200">
              <span className="block text-xs font-bold text-slate-700 font-mono">
                {cov.unknown_count}
              </span>
              <span className="text-[9px] text-slate-600 font-medium">Unknown</span>
            </div>
            <div className="p-1 rounded bg-rose-50 border border-rose-200">
              <span className="block text-xs font-bold text-rose-800 font-mono">
                {cov.conflicts_count}
              </span>
              <span className="text-[9px] text-rose-700 font-medium">Conflict</span>
            </div>
          </div>
        </div>
      )}

      {/* Regulatory & Gaps Signals */}
      <div className="mt-3 space-y-1.5">
        {/* Regulatory Status */}
        <div className="flex items-center justify-between text-xs p-1.5 rounded bg-slate-100/70 border border-slate-200 text-slate-700">
          <span className="flex items-center gap-1.5 font-medium text-slate-600">
            <Scale className="w-3.5 h-3.5 text-slate-500" />
            Regulatory (QCO):
          </span>
          <span className="font-mono text-[11px] font-semibold text-slate-800 truncate max-w-[170px]" title={candidate.qco_status}>
            {candidate.qco_status || 'NOT_FOUND_IN_SEED'}
          </span>
        </div>

        {/* Gaps Alert */}
        {numGaps > 0 && (
          <div className="flex items-center justify-between text-xs p-1.5 rounded bg-amber-50/70 border border-amber-200/80 text-amber-900">
            <span className="flex items-center gap-1.5 font-medium text-amber-800">
              <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
              Gaps Detected:
            </span>
            <span className="font-mono text-[11px] font-semibold">
              {numGaps} total {highGaps > 0 ? `(${highGaps} High)` : ''}
            </span>
          </div>
        )}
      </div>

      {/* Card Actions */}
      <div className="mt-3.5 pt-2.5 border-t border-slate-100 flex items-center justify-between">
        <span className="text-[11px] text-slate-500 flex items-center gap-1 font-mono">
          <FileText className="w-3 h-3 text-slate-400" />
          {evidenceCount} evidence items
        </span>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => onViewDetails(candidate)}
            className="px-2.5 py-1 text-xs font-medium text-slate-700 hover:text-slate-900 bg-slate-100 hover:bg-slate-200 rounded transition-colors flex items-center gap-1"
          >
            <Eye className="w-3.5 h-3.5" />
            <span>Details</span>
          </button>

          <button
            type="button"
            onClick={() => onSelect(candidate)}
            className={`px-3 py-1 text-xs font-medium rounded shadow-sm transition-colors flex items-center gap-1 ${
              isSelected
                ? 'bg-blue-600 text-white hover:bg-blue-700'
                : 'bg-slate-800 text-white hover:bg-slate-900'
            }`}
          >
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>{isSelected ? 'Active Selection' : 'Select for Review'}</span>
          </button>
        </div>
      </div>
    </div>
  );
};
