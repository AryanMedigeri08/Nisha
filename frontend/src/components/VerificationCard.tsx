import React, { useState } from 'react';
import { VerificationItemDTO, VerificationState } from '../types/review';
import { StatusBadge } from './StatusBadge';
import { Shield, FileCheck, AlertCircle, Save, Check } from 'lucide-react';

interface VerificationCardProps {
  item: VerificationItemDTO;
  onUpdate: (
    itemId: number,
    state: VerificationState,
    evidenceReference?: string,
    note?: string
  ) => Promise<void>;
}

export const VerificationCard: React.FC<VerificationCardProps> = ({ item, onUpdate }) => {
  const [selectedState, setSelectedState] = useState<VerificationState>(item.officer_state);
  const [evidenceRef, setEvidenceRef] = useState(item.officer_evidence_reference || '');
  const [note, setNote] = useState(item.officer_note || '');
  const [isSaving, setIsSaving] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState(false);

  const handleSave = async () => {
    setErrorMsg(null);
    setSuccessMsg(false);

    // Frontend validation for regulatory claims
    if (item.is_regulatory && selectedState === 'VERIFIED') {
      if (!evidenceRef.trim()) {
        setErrorMsg('Mandatory: Authoritative Gazette Notification or Order reference is required for regulatory verification.');
        return;
      }
      if (!note.trim()) {
        setErrorMsg('Mandatory: Please provide an officer explanation note for regulatory verification.');
        return;
      }
    }

    try {
      setIsSaving(true);
      await onUpdate(item.id, selectedState, evidenceRef, note);
      setSuccessMsg(true);
      setTimeout(() => setSuccessMsg(false), 2500);
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to update verification item.');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className={`p-4 rounded-lg border transition-all ${
      item.is_regulatory
        ? 'bg-amber-50/40 border-amber-300 shadow-sm'
        : 'bg-white border-slate-200'
    }`}>
      {/* Header */}
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-start gap-2">
          {item.is_regulatory ? (
            <Shield className="w-4 h-4 text-amber-600 mt-0.5 shrink-0" />
          ) : (
            <FileCheck className="w-4 h-4 text-blue-600 mt-0.5 shrink-0" />
          )}
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-slate-900">{item.title}</span>
              {item.is_regulatory && (
                <span className="text-[10px] uppercase tracking-wider font-bold bg-amber-200 text-amber-900 px-1.5 py-0.2 rounded border border-amber-300">
                  Regulatory Mandate
                </span>
              )}
            </div>
            <span className="text-[11px] text-slate-500 font-mono">{item.item_key}</span>
          </div>
        </div>

        <StatusBadge status={item.officer_state} type="verification" size="sm" />
      </div>

      {/* System Evidence Section */}
      {item.system_evidence && (
        <div className="mt-2.5 p-2 bg-slate-50 border border-slate-200 rounded text-xs text-slate-700">
          <div className="font-medium text-[11px] text-slate-500 mb-0.5">System Evidence & Findings:</div>
          <div className="font-mono text-[11px] text-slate-800 break-words whitespace-pre-wrap">
            {typeof item.system_evidence === 'string'
              ? item.system_evidence
              : JSON.stringify(item.system_evidence, null, 2)}
          </div>
        </div>
      )}

      {/* Officer Verification Form */}
      <div className="mt-3 pt-3 border-t border-slate-200/80 space-y-2.5">
        <div className="flex items-center gap-2">
          <label className="text-xs font-medium text-slate-700 w-28 shrink-0">Officer Status:</label>
          <select
            value={selectedState}
            onChange={(e) => setSelectedState(e.target.value as VerificationState)}
            className="flex-1 text-xs bg-white border border-slate-300 rounded px-2.5 py-1 text-slate-900 focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <option value="UNVERIFIED">UNVERIFIED (Requires Inspection)</option>
            <option value="VERIFIED">VERIFIED (Evidence Confirmed)</option>
            <option value="CONFLICTING">CONFLICTING (Contradicts Tender)</option>
            <option value="NOT_APPLICABLE">NOT APPLICABLE</option>
          </select>
        </div>

        {/* Evidence Reference Input (Mandatory for Regulatory) */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <label className="text-xs font-medium text-slate-700">
              Evidence Reference {item.is_regulatory && selectedState === 'VERIFIED' ? <span className="text-rose-600 font-bold">*</span> : ''}:
            </label>
            <span className="text-[10px] text-slate-400">e.g. Gazette Order No., Manakonline URL, Clause No.</span>
          </div>
          <input
            type="text"
            value={evidenceRef}
            onChange={(e) => setEvidenceRef(e.target.value)}
            placeholder={item.is_regulatory ? "e.g. Gazette S.O. 1234(E), DPIIT Scheme-1" : "e.g. Standard Clause 3.2"}
            className="w-full text-xs bg-white border border-slate-300 rounded px-2.5 py-1 text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>

        {/* Officer Note */}
        <div>
          <label className="block text-xs font-medium text-slate-700 mb-1">
            Officer Verification Note {item.is_regulatory && selectedState === 'VERIFIED' ? <span className="text-rose-600 font-bold">*</span> : ''}:
          </label>
          <textarea
            rows={2}
            value={note}
            onChange={(e) => setNote(e.target.value)}
            placeholder="Document basis for verification or reasons for discrepancy..."
            className="w-full text-xs bg-white border border-slate-300 rounded px-2.5 py-1 text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-1 focus:ring-blue-500 resize-none"
          />
        </div>

        {/* Error message */}
        {errorMsg && (
          <div className="flex items-center gap-1.5 text-xs text-rose-700 bg-rose-50 border border-rose-200 p-2 rounded">
            <AlertCircle className="w-3.5 h-3.5 shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}

        {/* Action Button */}
        <div className="flex items-center justify-between pt-1">
          <span className="text-[10px] text-slate-400">
            {item.verified_at ? `Last verified: ${new Date(item.verified_at).toLocaleTimeString()}` : 'Not yet verified'}
          </span>

          <div className="flex items-center gap-2">
            {successMsg && (
              <span className="flex items-center gap-1 text-xs text-emerald-700 font-medium">
                <Check className="w-3.5 h-3.5" /> Saved
              </span>
            )}
            <button
              type="button"
              onClick={handleSave}
              disabled={isSaving}
              className="flex items-center gap-1 px-3 py-1 bg-slate-800 hover:bg-slate-900 text-white text-xs font-medium rounded shadow-sm disabled:opacity-50 transition-colors"
            >
              <Save className="w-3.5 h-3.5" />
              <span>{isSaving ? 'Saving...' : 'Save Verification'}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
