import React, { useState } from 'react';
import {
  OfficerDecisionState,
  RejectionReason,
  CandidateDTO,
} from '../types/review';
import {
  CheckCircle2,
  XCircle,
  AlertCircle,
  RefreshCw,
  AlertTriangle,
  FileCheck2,
  X,
} from 'lucide-react';

interface DecisionModalProps {
  isOpen: boolean;
  onClose: () => void;
  reviewId: string;
  candidates: CandidateDTO[];
  selectedCandidateId?: number;
  aiRecommendationState?: string;
  onSubmitDecision: (data: {
    state: OfficerDecisionState;
    selected_candidate_id?: number;
    rejection_reason?: RejectionReason;
    rejection_note?: string;
    officer_id: string;
    officer_role: string;
    decision_summary: string;
    supporting_evidence_references: string[];
  }) => Promise<void>;
}

export const DecisionModal: React.FC<DecisionModalProps> = ({
  isOpen,
  onClose,
  reviewId,
  candidates,
  selectedCandidateId,
  aiRecommendationState,
  onSubmitDecision,
}) => {
  const [decisionState, setDecisionState] = useState<OfficerDecisionState>('ACCEPTED');
  const [targetCandidateId, setTargetCandidateId] = useState<number | undefined>(
    selectedCandidateId || (candidates[0] ? candidates[0].id : undefined)
  );
  const [rejectionReason, setRejectionReason] = useState<RejectionReason>('INSUFFICIENT_TECHNICAL_COVERAGE');
  const [rejectionNote, setRejectionNote] = useState('');
  const [officerId, setOfficerId] = useState('officer_001');
  const [officerRole, setOfficerRole] = useState('Procurement Technical Officer');
  const [decisionSummary, setDecisionSummary] = useState('');
  const [evidenceCitations, setEvidenceCitations] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  if (!isOpen) return null;

  // Selected candidate record
  const selectedCandidate = candidates.find((c) => c.id === targetCandidateId);

  // Check if this decision is an override
  const isOverride =
    (decisionState === 'ACCEPTED' && aiRecommendationState === 'NOT_RECOMMENDED') ||
    (decisionState === 'REJECTED' &&
      (aiRecommendationState === 'HIGHLY_RECOMMENDED' ||
        aiRecommendationState === 'RECOMMENDED_FOR_REVIEW'));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);

    if (decisionState === 'REJECTED' && !rejectionReason) {
      setErrorMsg('Please select a structured rejection reason.');
      return;
    }

    if (!decisionSummary.trim()) {
      setErrorMsg('Please enter a brief decision summary explanation.');
      return;
    }

    const citations = evidenceCitations
      .split('\n')
      .map((s) => s.trim())
      .filter(Boolean);

    try {
      setIsSubmitting(true);
      await onSubmitDecision({
        state: decisionState,
        selected_candidate_id: targetCandidateId,
        rejection_reason: decisionState === 'REJECTED' ? rejectionReason : undefined,
        rejection_note: decisionState === 'REJECTED' ? rejectionNote : undefined,
        officer_id: officerId,
        officer_role: officerRole,
        decision_summary: decisionSummary,
        supporting_evidence_references: citations,
      });
      onClose();
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to submit officer decision.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full border border-slate-200 overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 bg-slate-900 text-white flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <FileCheck2 className="w-5 h-5 text-blue-400" />
            <div>
              <h3 className="text-sm font-semibold">Record Authorized Officer Decision</h3>
              <p className="text-xs text-slate-400">Review ID: {reviewId}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1 rounded-md transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Override Warning Banner */}
        {isOverride && (
          <div className="bg-amber-50 border-b border-amber-200 px-6 py-3 flex items-start gap-2.5 text-amber-900 text-xs">
            <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
            <div>
              <span className="font-semibold">HUMAN OVERRIDE DETECTED: </span>
              Your decision ({decisionState}) diverges from the algorithmic recommendation (
              {aiRecommendationState}). This override and its justification will be permanently
              logged in the immutable audit trail.
            </div>
          </div>
        )}

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4 max-h-[78vh] overflow-y-auto">
          {/* Decision State Selection */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">
              Officer Decision State <span className="text-rose-600">*</span>
            </label>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
              <button
                type="button"
                onClick={() => setDecisionState('ACCEPTED')}
                className={`flex flex-col items-center justify-center p-3 rounded-lg border text-xs font-medium transition-all ${
                  decisionState === 'ACCEPTED'
                    ? 'bg-emerald-50 border-emerald-500 text-emerald-800 ring-2 ring-emerald-400'
                    : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50'
                }`}
              >
                <CheckCircle2 className="w-5 h-5 text-emerald-600 mb-1" />
                <span>ACCEPT</span>
              </button>

              <button
                type="button"
                onClick={() => setDecisionState('REJECTED')}
                className={`flex flex-col items-center justify-center p-3 rounded-lg border text-xs font-medium transition-all ${
                  decisionState === 'REJECTED'
                    ? 'bg-rose-50 border-rose-500 text-rose-800 ring-2 ring-rose-400'
                    : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50'
                }`}
              >
                <XCircle className="w-5 h-5 text-rose-600 mb-1" />
                <span>REJECT</span>
              </button>

              <button
                type="button"
                onClick={() => setDecisionState('NEEDS_VERIFICATION')}
                className={`flex flex-col items-center justify-center p-3 rounded-lg border text-xs font-medium transition-all ${
                  decisionState === 'NEEDS_VERIFICATION'
                    ? 'bg-amber-50 border-amber-500 text-amber-800 ring-2 ring-amber-400'
                    : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50'
                }`}
              >
                <AlertCircle className="w-5 h-5 text-amber-600 mb-1" />
                <span>VERIFY FIRST</span>
              </button>

              <button
                type="button"
                onClick={() => setDecisionState('REQUEST_REVISION')}
                className={`flex flex-col items-center justify-center p-3 rounded-lg border text-xs font-medium transition-all ${
                  decisionState === 'REQUEST_REVISION'
                    ? 'bg-purple-50 border-purple-500 text-purple-800 ring-2 ring-purple-400'
                    : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50'
                }`}
              >
                <RefreshCw className="w-5 h-5 text-purple-600 mb-1" />
                <span>REVISION</span>
              </button>
            </div>
          </div>

          {/* Target Candidate Standard Selection */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Candidate Standard Under Decision:
            </label>
            <select
              value={targetCandidateId}
              onChange={(e) => setTargetCandidateId(Number(e.target.value))}
              className="w-full text-xs bg-white border border-slate-300 rounded-md p-2 text-slate-900 focus:ring-1 focus:ring-blue-500"
            >
              {candidates.map((cand) => (
                <option key={cand.id} value={cand.id}>
                  #{cand.retrieval_rank} — {cand.is_number}: {cand.title.slice(0, 60)}...
                </option>
              ))}
            </select>
            {selectedCandidate && (
              <div className="mt-1.5 p-2 bg-slate-50 rounded border border-slate-200 text-xs flex items-center justify-between text-slate-700">
                <span>AI Baseline: <strong className="font-mono">{selectedCandidate.ai_recommendation_state}</strong></span>
                <span>Coverage: <strong className="font-mono">{selectedCandidate.requirement_coverage?.direct_matches || 0} Match / {selectedCandidate.requirement_coverage?.partial_matches || 0} Partial</strong></span>
              </div>
            )}
          </div>

          {/* Rejection Reason (Required if REJECTED) */}
          {decisionState === 'REJECTED' && (
            <div className="p-3 bg-rose-50/60 border border-rose-200 rounded-lg space-y-2">
              <label className="block text-xs font-semibold text-rose-900">
                Structured Rejection Reason Code <span className="text-rose-600">*</span>
              </label>
              <select
                value={rejectionReason}
                onChange={(e) => setRejectionReason(e.target.value as RejectionReason)}
                className="w-full text-xs bg-white border border-rose-300 rounded p-2 text-rose-900 focus:ring-1 focus:ring-rose-500"
              >
                <option value="INSUFFICIENT_TECHNICAL_COVERAGE">INSUFFICIENT_TECHNICAL_COVERAGE — Technical parameters unfulfilled</option>
                <option value="WRONG_PRODUCT">WRONG_PRODUCT — Standard covers a different product class</option>
                <option value="WRONG_SECTOR">WRONG_SECTOR — Sector or industry scope mismatch</option>
                <option value="PARAMETER_CONFLICT">PARAMETER_CONFLICT — Voltage, pressure, or dimension conflict</option>
                <option value="OUTDATED_STANDARD">OUTDATED_STANDARD — Superseded or withdrawn standard</option>
                <option value="REGULATORY_MISMATCH">REGULATORY_MISMATCH — QCO or statutory mandate discrepancy</option>
                <option value="INSUFFICIENT_EVIDENCE">INSUFFICIENT_EVIDENCE — Lack of authoritative gazette evidence</option>
                <option value="DUPLICATE_STANDARD">DUPLICATE_STANDARD — Overlaps with primary standard</option>
                <option value="OTHER">OTHER — Specify below</option>
              </select>

              <div>
                <label className="block text-xs font-medium text-rose-800 mb-1">
                  Detailed Rejection Note (Optional):
                </label>
                <textarea
                  rows={2}
                  value={rejectionNote}
                  onChange={(e) => setRejectionNote(e.target.value)}
                  placeholder="Explain the technical or regulatory discrepancy in detail..."
                  className="w-full text-xs bg-white border border-rose-300 rounded p-2 text-slate-900 focus:ring-1 focus:ring-rose-500"
                />
              </div>
            </div>
          )}

          {/* Decision Summary */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Decision Summary / Reasoning <span className="text-rose-600">*</span>:
            </label>
            <textarea
              rows={3}
              value={decisionSummary}
              onChange={(e) => setDecisionSummary(e.target.value)}
              placeholder="State the formal basis for this decision (e.g. Standard IS 269 matches cement 43-grade requirements and QCO verified via Gazette S.O. 1234(E))..."
              className="w-full text-xs bg-white border border-slate-300 rounded p-2 text-slate-900 focus:ring-1 focus:ring-blue-500"
              required
            />
          </div>

          {/* Supporting Evidence References */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Supporting Evidence Citations (one per line):
            </label>
            <textarea
              rows={2}
              value={evidenceCitations}
              onChange={(e) => setEvidenceCitations(e.target.value)}
              placeholder="e.g.&#10;DPIIT Gazette Notification S.O. 1234(E)&#10;Tender Schedule Technical Specification Clause 4.1"
              className="w-full text-xs font-mono bg-white border border-slate-300 rounded p-2 text-slate-900 focus:ring-1 focus:ring-blue-500"
            />
          </div>

          {/* Officer Details */}
          <div className="grid grid-cols-2 gap-3 pt-1">
            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1">Officer ID:</label>
              <input
                type="text"
                value={officerId}
                onChange={(e) => setOfficerId(e.target.value)}
                className="w-full text-xs bg-white border border-slate-300 rounded p-1.5 text-slate-900"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1">Officer Role:</label>
              <input
                type="text"
                value={officerRole}
                onChange={(e) => setOfficerRole(e.target.value)}
                className="w-full text-xs bg-white border border-slate-300 rounded p-1.5 text-slate-900"
                required
              />
            </div>
          </div>

          {/* Error Message */}
          {errorMsg && (
            <div className="p-2.5 bg-rose-50 border border-rose-200 rounded text-xs text-rose-800 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0 text-rose-600" />
              <span>{errorMsg}</span>
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-200">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-xs font-medium text-slate-700 hover:bg-slate-100 rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-5 py-2 text-xs font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow-sm disabled:opacity-50 transition-colors"
            >
              {isSubmitting ? 'Recording Decision...' : 'Commit Officer Decision'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
