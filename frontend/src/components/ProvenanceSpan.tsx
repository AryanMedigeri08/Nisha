import React from 'react';
import { Tag, Quote } from 'lucide-react';

interface ProvenanceSpanProps {
  label: string;
  value?: string | string[] | null;
  evidence?: string | null;
  confidence?: number;
}

export const ProvenanceSpan: React.FC<ProvenanceSpanProps> = ({
  label,
  value,
  evidence,
  confidence,
}) => {
  const displayVal = Array.isArray(value) ? value.join(', ') : value;

  if (!displayVal) {
    return (
      <div className="py-2 border-b border-slate-100 last:border-b-0 flex items-start justify-between">
        <span className="text-xs text-slate-500 font-medium">{label}:</span>
        <span className="text-xs text-slate-400 italic">Not specified</span>
      </div>
    );
  }

  return (
    <div className="py-2.5 border-b border-slate-100 last:border-b-0">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-slate-700 flex items-center gap-1">
          <Tag className="w-3 h-3 text-slate-400" />
          {label}
        </span>
        {confidence !== undefined && (
          <span className="text-[10px] font-mono bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded">
            conf: {(confidence * 100).toFixed(0)}%
          </span>
        )}
      </div>

      <div className="mt-1 text-sm font-medium text-slate-900 bg-slate-50 p-2 rounded border border-slate-200/80">
        {displayVal}
      </div>

      {evidence && (
        <div className="mt-1.5 flex items-start gap-1.5 text-xs text-slate-600 bg-amber-50/70 border border-amber-200/60 p-1.5 rounded">
          <Quote className="w-3 h-3 text-amber-600 shrink-0 mt-0.5" />
          <span className="font-mono text-[11px] text-amber-900 leading-tight">
            "{evidence}"
          </span>
        </div>
      )}
    </div>
  );
};
