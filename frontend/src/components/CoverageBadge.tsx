import React from 'react';
import { CoverageStatus } from '../types/review';
import { Check, Minus, X, HelpCircle, AlertTriangle } from 'lucide-react';

interface CoverageBadgeProps {
  status: CoverageStatus | string;
  label?: string;
  size?: 'sm' | 'md';
}

export const CoverageBadge: React.FC<CoverageBadgeProps> = ({ status, label, size = 'md' }) => {
  const s = (status || 'UNKNOWN').toUpperCase();
  const sizeClasses = size === 'sm' ? 'px-1.5 py-0.5 text-[10px]' : 'px-2 py-0.5 text-xs';

  switch (s) {
    case 'MATCH':
      return (
        <span
          className={`inline-flex items-center gap-1 font-semibold rounded bg-emerald-100 text-emerald-900 border border-emerald-300 ${sizeClasses}`}
          title="Direct requirement match found in standard specifications"
        >
          <Check className="w-3 h-3 text-emerald-700 stroke-[2.5]" />
          <span>{label || 'MATCH'}</span>
        </span>
      );
    case 'PARTIAL_MATCH':
      return (
        <span
          className={`inline-flex items-center gap-1 font-semibold rounded bg-amber-100 text-amber-900 border border-amber-300 ${sizeClasses}`}
          title="Partial scope overlap or subset match"
        >
          <Minus className="w-3 h-3 text-amber-700 stroke-[2.5]" />
          <span>{label || 'PARTIAL MATCH'}</span>
        </span>
      );
    case 'CONFLICT':
      return (
        <span
          className={`inline-flex items-center gap-1 font-semibold rounded bg-rose-100 text-rose-900 border border-rose-300 ${sizeClasses}`}
          title="Direct contradiction between tender requirement and standard rating/scope"
        >
          <AlertTriangle className="w-3 h-3 text-rose-700 stroke-[2.5]" />
          <span>{label || 'CONFLICT'}</span>
        </span>
      );
    case 'NO_MATCH':
      return (
        <span
          className={`inline-flex items-center gap-1 font-semibold rounded bg-red-50 text-red-800 border border-red-200 ${sizeClasses}`}
          title="Requirement not satisfied by candidate standard"
        >
          <X className="w-3 h-3 text-red-600 stroke-[2.5]" />
          <span>{label || 'NO MATCH'}</span>
        </span>
      );
    case 'UNKNOWN':
    default:
      return (
        <span
          className={`inline-flex items-center gap-1 font-semibold rounded bg-slate-100 text-slate-700 border border-slate-300 ${sizeClasses}`}
          title="Specification parameter not explicitly verified in seed record"
        >
          <HelpCircle className="w-3 h-3 text-slate-500 stroke-[2]" />
          <span>{label || 'UNKNOWN'}</span>
        </span>
      );
  }
};
