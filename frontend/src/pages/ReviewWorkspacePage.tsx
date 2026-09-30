import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import {
  ReviewDetailDTO,
  CandidateDTO,
  VerificationState,
  OfficerDecisionState,
  RejectionReason,
} from '../types/review';
import { StatusBadge } from '../components/StatusBadge';
import { ProvenanceSpan } from '../components/ProvenanceSpan';
import { CandidateCard } from '../components/CandidateCard';
import { VerificationCard } from '../components/VerificationCard';
import { DecisionModal } from '../components/DecisionModal';
import { AuditTimeline } from '../components/AuditTimeline';
import {
  FileText,
  Layers,
  ShieldCheck,
  CheckCircle2,
  XCircle,
  AlertCircle,
  RefreshCw,
  Scale,
  History,
  Columns3,
  ExternalLink,
  ChevronRight,
} from 'lucide-react';

interface ReviewWorkspacePageProps {
  reviewId: string;
  onNavigate: (tab: string, reviewId?: string) => void;
  onCompare: (candidateIds: number[]) => void;
  onViewCandidateDetail: (candidate: CandidateDTO) => void;
}

export const ReviewWorkspacePage: React.FC<ReviewWorkspacePageProps> = ({
  reviewId,
  onNavigate,
  onCompare,
  onViewCandidateDetail,
}) => {
  const [review, setReview] = useState<ReviewDetailDTO | null>(null);
  const [selectedCandidate, setSelectedCandidate] = useState<CandidateDTO | null>(null);
  const [compareIds, setCompareIds] = useState<number[]>([]);
  const [isDecisionModalOpen, setIsDecisionModalOpen] = useState(false);
  const [activeRightTab, setActiveRightTab] = useState<'verification' | 'evidence' | 'audit'>('verification');
  const [isLoading, setIsLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [isReopening, setIsReopening] = useState(false);

  useEffect(() => {
    loadReview();
  }, [reviewId]);

  const loadReview = async () => {
    try {
      setIsLoading(true);
      setErrorMsg(null);
      const data = await api.getReview(reviewId);
      setReview(data);
      if (data.candidates && data.candidates.length > 0) {
        // Set selected candidate to either the saved candidate or top candidate
        const activeCand = data.selected_candidate_id
          ? data.candidates.find((c) => c.id === data.selected_candidate_id) || data.candidates[0]
          : data.candidates[0];
        setSelectedCandidate(activeCand);
      }
    } catch (err: any) {
      setErrorMsg(err.message || `Failed to load review ${reviewId}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerificationUpdate = async (
    itemId: number,
    state: VerificationState,
    evidenceReference?: string,
    note?: string
  ) => {
    if (!review) return;
    await api.updateVerification(review.review_id, {
      verification_item_id: itemId,
      officer_state: state,
      evidence_reference: evidenceReference,
      officer_note: note,
    });
    // Reload review to sync state machine updates
    await loadReview();
  };

  const handleSubmitDecision = async (data: {
    state: OfficerDecisionState;
    selected_candidate_id?: number;
    rejection_reason?: RejectionReason;
    rejection_note?: string;
    officer_id: string;
    officer_role: string;
    decision_summary: string;
    supporting_evidence_references: string[];
  }) => {
    if (!review) return;
    await api.submitDecision(review.review_id, data);
    await loadReview();
  };

  const handleReopen = async () => {
    const reason = window.prompt('Enter reason for reopening finalized review:');
    if (!reason || !reason.trim()) return;

    try {
      setIsReopening(true);
      await api.reopenReview(reviewId, { reason: reason.trim() });
      await loadReview();
    } catch (err: any) {
      alert(err.message || 'Failed to reopen review.');
    } finally {
      setIsReopening(false);
    }
  };

  const handleCompareToggle = (candidateId: number) => {
    setCompareIds((prev) => {
      if (prev.includes(candidateId)) {
        return prev.filter((id) => id !== candidateId);
      }
      if (prev.length >= 3) {
        alert('You can compare a maximum of 3 candidates simultaneously.');
        return prev;
      }
      return [...prev, candidateId];
    });
  };

  if (isLoading) {
    return (
      <div className="py-24 text-center space-y-3">
        <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto" />
        <p className="text-xs text-slate-500 font-mono">Loading review package {reviewId}...</p>
      </div>
    );
  }

  if (errorMsg || !review) {
    return (
      <div className="p-8 max-w-2xl mx-auto bg-rose-50 border border-rose-200 rounded-xl text-center space-y-4">
        <AlertCircle className="w-8 h-8 text-rose-600 mx-auto" />
        <div>
          <h2 className="text-base font-bold text-rose-900">Unable to Load Review</h2>
          <p className="text-xs text-rose-700 mt-1">{errorMsg}</p>
        </div>
        <button
          onClick={() => onNavigate('reviews')}
          className="px-4 py-2 bg-slate-800 text-white text-xs font-semibold rounded-lg"
        >
          Back to Review Queue
        </button>
      </div>
    );
  }

  const reqs = review.procurement_requirements || {};
  const isFinalized = review.status === 'ACCEPTED' || review.status === 'REJECTED';

  // Filter verification items for the selected candidate
  const candidateVerifications = selectedCandidate
    ? review.verification_items.filter(
        (v) => v.candidate_id === selectedCandidate.id || v.standard_id === selectedCandidate.standard_id
      )
    : review.verification_items;

  return (
    <div className="space-y-6 pb-20">
      {/* Top Header Bar */}
      <div className="bg-white p-4 sm:p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2.5 flex-wrap">
            <span className="font-mono text-sm font-bold text-blue-600">{review.review_id}</span>
            <StatusBadge status={review.status} type="officer" />
            <span className="text-xs text-slate-400 font-mono">
              Created: {review.created_at ? new Date(review.created_at).toLocaleString() : '—'}
            </span>
          </div>
          <p className="text-xs text-slate-600 mt-1 line-clamp-1 max-w-3xl">
            Tender: <span className="font-medium text-slate-900 font-sans">{review.raw_text}</span>
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2 flex-wrap">
          {isFinalized ? (
            <button
              onClick={handleReopen}
              disabled={isReopening}
              className="px-3.5 py-1.5 bg-slate-800 hover:bg-slate-900 text-white text-xs font-semibold rounded-lg shadow-sm flex items-center gap-1.5 transition-colors"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>{isReopening ? 'Reopening...' : 'Reopen Review'}</span>
            </button>
          ) : (
            <button
              onClick={() => setIsDecisionModalOpen(true)}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg shadow-sm flex items-center gap-1.5 transition-colors"
            >
              <CheckCircle2 className="w-4 h-4" />
              <span>Record Officer Decision</span>
            </button>
          )}
        </div>
      </div>

      {/* Comparison Floating Bar */}
      {compareIds.length >= 2 && (
        <div className="bg-slate-900 text-white p-3.5 rounded-xl shadow-lg border border-slate-700 flex items-center justify-between gap-4 animate-in slide-in-from-bottom-2">
          <div className="flex items-center gap-2 text-xs">
            <Columns3 className="w-4 h-4 text-blue-400" />
            <span>
              <strong>{compareIds.length} standards selected</strong> for side-by-side evaluation.
            </span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setCompareIds([])}
              className="px-2.5 py-1 text-xs text-slate-400 hover:text-white"
            >
              Clear
            </button>
            <button
              onClick={() => onCompare(compareIds)}
              className="px-4 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg shadow-sm transition-colors"
            >
              Launch Side-by-Side Matrix
            </button>
          </div>
        </div>
      )}

      {/* 3-COLUMN WORKSPACE GRID */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* ================================================================= */}
        {/* COLUMN 1: LEFT — Extracted Procurement Requirements & Provenance */}
        {/* ================================================================= */}
        <div className="lg:col-span-3 space-y-4">
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-4 space-y-3">
            <div className="flex items-center justify-between border-b border-slate-100 pb-2">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-1.5">
                <FileText className="w-3.5 h-3.5 text-slate-500" />
                Phase 3 Requirements
              </h3>
              <span className="text-[10px] font-mono bg-blue-50 text-blue-700 px-1.5 py-0.5 rounded">
                Grounded Spans
              </span>
            </div>

            {/* Extracted Fields */}
            <div className="space-y-1">
              <ProvenanceSpan
                label="Product"
                value={reqs.product?.value}
                evidence={reqs.product?.evidence}
                confidence={reqs.product?.confidence}
              />
              <ProvenanceSpan
                label="Sector"
                value={reqs.sector?.value}
                evidence={reqs.sector?.evidence}
                confidence={reqs.sector?.confidence}
              />
              <ProvenanceSpan
                label="Application Scope"
                value={reqs.application?.value}
                evidence={reqs.application?.evidence}
                confidence={reqs.application?.confidence}
              />
              <ProvenanceSpan
                label="Materials"
                value={reqs.materials?.map((m: any) => m.value)}
                evidence={reqs.materials?.[0]?.evidence}
              />
            </div>

            {/* Parameters list */}
            {reqs.parameters && reqs.parameters.length > 0 && (
              <div className="pt-2 border-t border-slate-100">
                <span className="text-xs font-semibold text-slate-700 block mb-1.5">
                  Technical Parameters:
                </span>
                <div className="space-y-1.5">
                  {reqs.parameters.map((p: any, idx: number) => (
                    <div
                      key={idx}
                      className="p-2 bg-slate-50 rounded border border-slate-200 text-xs font-mono"
                    >
                      <div className="flex items-center justify-between font-semibold text-slate-800">
                        <span>{p.name}</span>
                        <span>{p.value} {p.unit || ''}</span>
                      </div>
                      {p.evidence && (
                        <div className="text-[10px] text-amber-800 mt-1 italic">
                          "{p.evidence}"
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* ================================================================= */}
        {/* COLUMN 2: CENTER — Retrieved Candidate Standards (Top-10)         */}
        {/* ================================================================= */}
        <div className="lg:col-span-5 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-1.5">
              <Layers className="w-3.5 h-3.5 text-slate-500" />
              Retrieved Candidates ({review.candidates.length})
            </h3>
            <span className="text-[11px] text-slate-500">
              Sorted by Cross-Encoder Rank
            </span>
          </div>

          <div className="space-y-3">
            {review.candidates.map((cand) => (
              <CandidateCard
                key={cand.id}
                candidate={cand}
                isSelected={selectedCandidate?.id === cand.id}
                onSelect={(c) => setSelectedCandidate(c)}
                onCompareToggle={handleCompareToggle}
                isCompareSelected={compareIds.includes(cand.id)}
                onViewDetails={(c) => onViewCandidateDetail(c)}
              />
            ))}
          </div>
        </div>

        {/* ================================================================= */}
        {/* COLUMN 3: RIGHT — Evidence Inspection & Verification Checklist     */}
        {/* ================================================================= */}
        <div className="lg:col-span-4 space-y-4">
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-4 space-y-4 sticky top-20">
            {/* Tab Selector */}
            <div className="flex items-center gap-1 p-1 bg-slate-100 rounded-lg text-xs font-medium">
              <button
                type="button"
                onClick={() => setActiveRightTab('verification')}
                className={`flex-1 py-1.5 text-center rounded-md transition-colors ${
                  activeRightTab === 'verification'
                    ? 'bg-white text-slate-900 shadow-sm font-semibold'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Verification ({candidateVerifications.length})
              </button>

              <button
                type="button"
                onClick={() => setActiveRightTab('evidence')}
                className={`flex-1 py-1.5 text-center rounded-md transition-colors ${
                  activeRightTab === 'evidence'
                    ? 'bg-white text-slate-900 shadow-sm font-semibold'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Evidence ({selectedCandidate?.evidence?.length || 0})
              </button>

              <button
                type="button"
                onClick={() => setActiveRightTab('audit')}
                className={`flex-1 py-1.5 text-center rounded-md transition-colors ${
                  activeRightTab === 'audit'
                    ? 'bg-white text-slate-900 shadow-sm font-semibold'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Audit Trail ({review.audit_events.length})
              </button>
            </div>

            {/* Content: Verification Checklist */}
            {activeRightTab === 'verification' && (
              <div className="space-y-3 max-h-[70vh] overflow-y-auto pr-1">
                <div className="flex items-center justify-between text-xs text-slate-600 pb-1 border-b border-slate-100">
                  <span>
                    Focus Standard: <strong>{selectedCandidate?.is_number || 'All'}</strong>
                  </span>
                  <span className="text-[11px] text-amber-800 bg-amber-50 px-1.5 py-0.5 rounded border border-amber-200">
                    Mandatory Evidence for QCO
                  </span>
                </div>

                {candidateVerifications.length === 0 ? (
                  <div className="p-6 text-center text-xs text-slate-500 bg-slate-50 rounded-lg">
                    No open verification gaps for this candidate.
                  </div>
                ) : (
                  candidateVerifications.map((item) => (
                    <VerificationCard
                      key={item.id}
                      item={item}
                      onUpdate={handleVerificationUpdate}
                    />
                  ))
                )}
              </div>
            )}

            {/* Content: Evidence Panel */}
            {activeRightTab === 'evidence' && (
              <div className="space-y-3 max-h-[70vh] overflow-y-auto pr-1">
                <div className="text-xs text-slate-600 pb-1 border-b border-slate-100 font-medium">
                  Authoritative Evidence & Retrieval Signals for {selectedCandidate?.is_number}:
                </div>

                {selectedCandidate?.evidence && selectedCandidate.evidence.length > 0 ? (
                  selectedCandidate.evidence.map((ev, idx) => (
                    <div key={idx} className="p-3 bg-slate-50 rounded-lg border border-slate-200 text-xs space-y-1.5">
                      <div className="flex items-center justify-between">
                        <span className="font-mono font-semibold text-[11px] text-slate-700 bg-slate-200 px-1.5 py-0.5 rounded">
                          {ev.source_type} ({ev.source_id})
                        </span>
                        <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                          ev.verification_status === 'VERIFIED'
                            ? 'bg-emerald-100 text-emerald-800'
                            : 'bg-amber-100 text-amber-800'
                        }`}>
                          {ev.verification_status}
                        </span>
                      </div>
                      <p className="font-semibold text-slate-900">{ev.claim}</p>
                      <div className="text-slate-600 font-mono text-[11px] bg-white p-2 rounded border border-slate-100 whitespace-pre-wrap">
                        {ev.evidence_text}
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="p-6 text-center text-xs text-slate-500 bg-slate-50 rounded-lg">
                    No direct seed evidence records attached.
                  </div>
                )}
              </div>
            )}

            {/* Content: Audit Trail */}
            {activeRightTab === 'audit' && (
              <div className="max-h-[70vh] overflow-y-auto pr-1">
                <AuditTimeline events={review.audit_events} />
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Decision Recording Modal */}
      <DecisionModal
        isOpen={isDecisionModalOpen}
        onClose={() => setIsDecisionModalOpen(false)}
        reviewId={review.review_id}
        candidates={review.candidates}
        selectedCandidateId={selectedCandidate?.id}
        aiRecommendationState={selectedCandidate?.ai_recommendation_state}
        onSubmitDecision={handleSubmitDecision}
      />
    </div>
  );
};
