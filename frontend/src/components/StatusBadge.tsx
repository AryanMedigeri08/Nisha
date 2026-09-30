import React from 'react';
import { OfficerDecisionState, VerificationState, AIRecommendationState } from '../types/review';
import { Clock, CheckCircle2, XCircle, AlertCircle, RefreshCw, HelpCircle } from 'lucide-react';

interface StatusBadgeProps {
  status: OfficerDecisionState | VerificationState | AIRecommendationState | string;
  type?: 'officer' | 'verification' | 'ai' | 'regulatory';
  size?: 'sm' | 'md';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, type = 'officer', size = 'md' }) => {
  const s = status ? status.toUpperCase() : 'UNKNOWN';
  const sizeClasses = size === 'sm' ? 'px-2 py-0.5 text-[10px]' : 'px-2.5 py-1 text-xs';

  if (type === 'officer') {
    switch (s) {
      case 'ACCEPTED':
        return (
          <span className={`inline-flex items-center gap-1 font-semibold rounded-full bg-emerald-100 text-emerald-800 border border-emerald-300 ${sizeClasses}`}>
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-700" />
            <span>ACCEPTED</span>
          </span>
        );
      case 'REJECTED':
        return (
          <span className={`inline-flex items-center gap-1 font-semibold rounded-full bg-rose-100 text-rose-800 border border-rose-300 ${sizeClasses}`}>
            <XCircle className="w-3.5 h-3.5 text-rose-700" />
            <span>REJECTED</span>
          </span>
        );
      case 'NEEDS_VERIFICATION':
        return (
          <span className={`inline-flex items-center gap-1 font-semibold rounded-full bg-amber-100 text-amber-900 border border-amber-300 ${sizeClasses}`}>
            <AlertCircle className="w-3.5 h-3.5 text-amber-700" />
            <span>NEEDS VERIFICATION</span>
          </span>
        );
      case 'REQUEST_REVISION':
        return (
          <span className={`inline-flex items-center gap-1 font-semibold rounded-full bg-purple-100 text-purple-900 border border-purple-300 ${sizeClasses}`}>
            <RefreshCw className="w-3.5 h-3.5 text-purple-700" />
            <span>REQUEST REVISION</span>
          </span>
        );
      case 'UNDER_REVIEW':
        return (
          <span className={`inline-flex items-center gap-1 font-semibold rounded-full bg-blue-100 text-blue-900 border border-blue-300 ${sizeClasses}`}>
            <Clock className="w-3.5 h-3.5 text-blue-700" />
            <span>UNDER REVIEW</span>
          </span>
        );
      case 'PENDING':
      default:
        return (
          <span className={`inline-flex items-center gap-1 font-semibold rounded-full bg-slate-100 text-slate-700 border border-slate-300 ${sizeClasses}`}>
            <Clock className="w-3.5 h-3.5 text-slate-500" />
            <span>PENDING</span>
          </span>
        );
    }
  }

  if (type === 'verification') {
    switch (s) {
      case 'VERIFIED':
        return (
          <span className={`inline-flex items-center gap-1 font-semibold rounded bg-emerald-50 text-emerald-800 border border-emerald-300 ${sizeClasses}`}>
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-700" />
            <span>VERIFIED</span>
          </span>
        );
      case 'CONFLICTING':
        return (
          <span className={`inline-flex items-center gap-1 font-semibold rounded bg-rose-50 text-rose-800 border border-rose-300 ${sizeClasses}`}>
            <XCircle className="w-3.5 h-3.5 text-rose-700" />
            <span>CONFLICTING</span>
          </span>
        );
      case 'NOT_APPLICABLE':
        return (
          <span className={`inline-flex items-center gap-1 font-semibold rounded bg-slate-100 text-slate-600 border border-slate-200 ${sizeClasses}`}>
            <span>N/A</span>
          </span>
        );
      case 'UNVERIFIED':
      default:
        return (
          <span className={`inline-flex items-center gap-1 font-semibold rounded bg-amber-50 text-amber-800 border border-amber-300 ${sizeClasses}`}>
            <HelpCircle className="w-3.5 h-3.5 text-amber-600" />
            <span>UNVERIFIED</span>
          </span>
        );
    }
  }

  // AI Recommendation States
  switch (s) {
    case 'HIGHLY_RECOMMENDED':
      return (
        <span className={`inline-flex items-center gap-1 font-medium rounded-full bg-blue-50 text-blue-800 border border-blue-200 ${sizeClasses}`}>
          <span>Highly Recommended</span>
        </span>
      );
    case 'RECOMMENDED_FOR_REVIEW':
      return (
        <span className={`inline-flex items-center gap-1 font-medium rounded-full bg-indigo-50 text-indigo-800 border border-indigo-200 ${sizeClasses}`}>
          <span>Recommended For Review</span>
        </span>
      );
    case 'REVIEW_REQUIRED':
      return (
        <span className={`inline-flex items-center gap-1 font-medium rounded-full bg-amber-50 text-amber-800 border border-amber-200 ${sizeClasses}`}>
          <span>Review Required</span>
        </span>
      );
    case 'INSUFFICIENT_COVERAGE':
      return (
        <span className={`inline-flex items-center gap-1 font-medium rounded-full bg-slate-100 text-slate-700 border border-slate-300 ${sizeClasses}`}>
          <span>Insufficient Coverage</span>
        </span>
      );
    case 'NOT_RECOMMENDED':
      return (
        <span className={`inline-flex items-center gap-1 font-medium rounded-full bg-rose-50 text-rose-800 border border-rose-200 ${sizeClasses}`}>
          <span>Not Recommended</span>
        </span>
      );
    default:
      return (
        <span className={`inline-flex items-center gap-1 font-medium rounded-full bg-slate-100 text-slate-700 border border-slate-200 ${sizeClasses}`}>
          <span>{s}</span>
        </span>
      );
  }
};
