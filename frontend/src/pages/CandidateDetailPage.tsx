import React, { useState } from 'react';
import { CandidateDTO } from '../types/review';
import { StatusBadge } from '../components/StatusBadge';
import { CoverageBadge } from '../components/CoverageBadge';
import {
  ArrowLeft,
  BookOpen,
  Scale,
  AlertTriangle,
  FileCheck,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  Shield,
  Layers,
  FileText,
} from 'lucide-react';

interface CandidateDetailPageProps {
  candidate: CandidateDTO;
  onBack: () => void;
}

export const CandidateDetailPage: React.FC<CandidateDetailPageProps> = ({ candidate, onBack }) => {
  const [openSections, setOpenSections] = useState<Record<string, boolean>>({
    overview: true,
    retrieval: true,
    coverage: true,
    regulatory: true,
    gaps: true,
    evidence: true,
  });

  const toggleSection = (key: string) => {
    setOpenSections((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const cov = candidate.requirement_coverage;

  return (
    <div className="max-w-5xl mx-auto space-y-6 pb-20">
      {/* Top Navigation */}
      <button
        type="button"
        onClick={onBack}
        className="flex items-center gap-1.5 text-xs font-semibold text-slate-600 hover:text-slate-900 bg-white border border-slate-200 px-3 py-1.5 rounded-lg shadow-sm transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Review Workspace</span>
      </button>

      {/* Standard Header Hero */}
      <div className="bg-slate-900 text-white rounded-xl p-6 border border-slate-800 shadow-md space-y-3">
        <div className="flex items-start justify-between gap-4 flex-wrap">
          <div>
            <div className="flex items-center gap-2.5 flex-wrap">
              <span className="font-mono text-xl font-bold text-blue-400">{candidate.is_number}</span>
              <span className="text-xs bg-slate-800 text-slate-300 font-mono px-2 py-0.5 rounded border border-slate-700">
                Rank #{candidate.retrieval_rank}
              </span>
              <StatusBadge status={candidate.ai_recommendation_state} type="ai" />
            </div>
            <h1 className="text-base sm:text-lg font-semibold text-slate-100 mt-1">
              {candidate.title}
            </h1>
          </div>

          <div className="text-right">
            <span className="text-xs text-slate-400 block">Sector</span>
            <span className="text-xs font-semibold text-slate-200">{candidate.sector || 'Unspecified'}</span>
          </div>
        </div>
      </div>

      {/* ================================================================= */}
      {/* SECTION A: Standard Overview & Scope                              */}
      {/* ================================================================= */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div
          onClick={() => toggleSection('overview')}
          className="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between cursor-pointer select-none hover:bg-slate-100/80 transition-colors"
        >
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800 flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-blue-600" />
            A. Standard Scope & Metadata
          </h3>
          {openSections.overview ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
        </div>

        {openSections.overview && (
          <div className="p-5 space-y-3 text-xs">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <span className="text-slate-500 font-semibold block mb-1">Application Scope:</span>
                <p className="text-slate-800 bg-slate-50 p-2.5 rounded border border-slate-200">
                  {candidate.application || 'General domain application scope'}
                </p>
              </div>
              <div>
                <span className="text-slate-500 font-semibold block mb-1">Materials Specified:</span>
                <div className="flex flex-wrap gap-1.5 mt-1">
                  {candidate.materials && candidate.materials.length > 0 ? (
                    candidate.materials.map((m, i) => (
                      <span key={i} className="bg-slate-100 text-slate-800 px-2 py-0.5 rounded border border-slate-200 font-mono text-[11px]">
                        {m}
                      </span>
                    ))
                  ) : (
                    <span className="text-slate-400 italic">Not explicitly enumerated</span>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* ================================================================= */}
      {/* SECTION B: Why Retrieved & Scoring Breakdown                      */}
      {/* ================================================================= */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div
          onClick={() => toggleSection('retrieval')}
          className="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between cursor-pointer select-none hover:bg-slate-100/80 transition-colors"
        >
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800 flex items-center gap-2">
            <Layers className="w-4 h-4 text-blue-600" />
            B. Why It Was Retrieved & Retrieval Signals
          </h3>
          {openSections.retrieval ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
        </div>

        {openSections.retrieval && (
          <div className="p-5 text-xs space-y-3">
            <p className="text-slate-600">
              Candidate was retrieved using a two-stage hybrid architecture (BM25 sparse query expansion + 384-d dense vector semantic matching), followed by Cross-Encoder neural reranking on the full procurement specification.
            </p>
            <div className="grid grid-cols-3 gap-3 text-center">
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
                <span className="text-slate-500 font-semibold text-[11px] block">Overall Rank</span>
                <span className="text-base font-bold text-slate-900 font-mono mt-0.5 block">#{candidate.retrieval_rank}</span>
              </div>
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
                <span className="text-slate-500 font-semibold text-[11px] block">Cross-Encoder Score</span>
                <span className="text-base font-bold text-blue-700 font-mono mt-0.5 block">
                  {candidate.reranker_score !== undefined && candidate.reranker_score !== null ? candidate.reranker_score.toFixed(4) : 'N/A'}
                </span>
              </div>
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
                <span className="text-slate-500 font-semibold text-[11px] block">RRF Hybrid Score</span>
                <span className="text-base font-bold text-slate-800 font-mono mt-0.5 block">
                  {candidate.rrf_score !== undefined && candidate.rrf_score !== null ? candidate.rrf_score.toFixed(4) : 'N/A'}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* ================================================================= */}
      {/* SECTION C: Requirement Coverage Matrix                            */}
      {/* ================================================================= */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div
          onClick={() => toggleSection('coverage')}
          className="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between cursor-pointer select-none hover:bg-slate-100/80 transition-colors"
        >
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800 flex items-center gap-2">
            <FileCheck className="w-4 h-4 text-blue-600" />
            C. Requirement Coverage Breakdown
          </h3>
          {openSections.coverage ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
        </div>

        {openSections.coverage && cov && (
          <div className="p-5 text-xs space-y-4">
            <div className="grid grid-cols-4 gap-2 text-center p-3 bg-slate-50 rounded-lg border border-slate-200">
              <div>
                <span className="text-lg font-bold text-emerald-700 font-mono block">{cov.direct_matches}</span>
                <span className="text-slate-600 font-medium">Direct Matches</span>
              </div>
              <div>
                <span className="text-lg font-bold text-amber-700 font-mono block">{cov.partial_matches}</span>
                <span className="text-slate-600 font-medium">Partial Matches</span>
              </div>
              <div>
                <span className="text-lg font-bold text-slate-700 font-mono block">{cov.unknown_count}</span>
                <span className="text-slate-600 font-medium">Unknown / Unverified</span>
              </div>
              <div>
                <span className="text-lg font-bold text-rose-700 font-mono block">{cov.conflicts_count}</span>
                <span className="text-slate-600 font-medium">Conflicts</span>
              </div>
            </div>

            <table className="w-full text-left border-collapse procurement-table">
              <thead>
                <tr>
                  <th className="w-32">Facet</th>
                  <th className="w-32">Status</th>
                  <th>Tender Value</th>
                  <th>Standard Specification / Explanation</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td className="font-semibold">Product</td>
                  <td><CoverageBadge status={cov.product?.status} /></td>
                  <td className="font-mono">{cov.product?.requirement_val || '—'}</td>
                  <td>{cov.product?.explanation}</td>
                </tr>
                <tr>
                  <td className="font-semibold">Sector</td>
                  <td><CoverageBadge status={cov.sector?.status} /></td>
                  <td className="font-mono">{cov.sector?.requirement_val || '—'}</td>
                  <td>{cov.sector?.explanation}</td>
                </tr>
                <tr>
                  <td className="font-semibold">Application</td>
                  <td><CoverageBadge status={cov.application?.status} /></td>
                  <td className="font-mono">{cov.application?.requirement_val || '—'}</td>
                  <td>{cov.application?.explanation}</td>
                </tr>
                <tr>
                  <td className="font-semibold">Materials</td>
                  <td><CoverageBadge status={cov.materials?.status} /></td>
                  <td className="font-mono">{Array.isArray(cov.materials?.requirement_val) ? cov.materials.requirement_val.join(', ') : '—'}</td>
                  <td>{cov.materials?.explanation}</td>
                </tr>
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* ================================================================= */}
      {/* SECTION D: Regulatory Status & Quality Control Orders             */}
      {/* ================================================================= */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div
          onClick={() => toggleSection('regulatory')}
          className="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between cursor-pointer select-none hover:bg-slate-100/80 transition-colors"
        >
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800 flex items-center gap-2">
            <Scale className="w-4 h-4 text-blue-600" />
            D. Regulatory Compliance & Quality Control Order Status
          </h3>
          {openSections.regulatory ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
        </div>

        {openSections.regulatory && (
          <div className="p-5 text-xs space-y-3">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                <span className="text-slate-500 font-semibold block">Standard Currency Status:</span>
                <span className="font-mono font-bold text-slate-800 text-sm mt-1 block">
                  {candidate.standard_status || 'NEEDS_VERIFICATION'}
                </span>
                <span className="text-[11px] text-slate-500 mt-1 block">
                  Requires confirmation against BIS active catalogue.
                </span>
              </div>

              <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                <span className="text-slate-500 font-semibold block">QCO Seed Association:</span>
                <span className="font-mono font-bold text-slate-800 text-sm mt-1 block">
                  {candidate.qco_status || 'NOT_FOUND_IN_SEED'}
                </span>
                <span className="text-[11px] text-slate-500 mt-1 block">
                  {candidate.order_names && candidate.order_names.length > 0 ? candidate.order_names.join(', ') : 'No associated seed order'}
                </span>
              </div>
            </div>

            <div className="p-3 bg-amber-50 rounded-lg border border-amber-200 text-amber-900 text-xs">
              <strong>Regulatory Integrity Notice:</strong> Quality Control Order enforcement dates and statutory mandates require authorized officer verification against the official DPIIT / Ministry Gazette register before procurement finalization.
            </div>
          </div>
        )}
      </div>

      {/* ================================================================= */}
      {/* SECTION E: Gaps Detected                                         */}
      {/* ================================================================= */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div
          onClick={() => toggleSection('gaps')}
          className="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between cursor-pointer select-none hover:bg-slate-100/80 transition-colors"
        >
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-600" />
            E. Detected Specification Gaps ({candidate.gaps?.length || 0})
          </h3>
          {openSections.gaps ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
        </div>

        {openSections.gaps && (
          <div className="p-5 text-xs space-y-3">
            {candidate.gaps && candidate.gaps.length > 0 ? (
              candidate.gaps.map((g, idx) => (
                <div key={idx} className="p-3 rounded-lg border bg-slate-50 border-slate-200 space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-slate-900">{g.title}</span>
                    <span className={`px-2 py-0.5 rounded font-mono font-bold text-[10px] ${
                      g.severity === 'HIGH' ? 'bg-rose-100 text-rose-800' : 'bg-amber-100 text-amber-800'
                    }`}>
                      {g.severity} SEVERITY
                    </span>
                  </div>
                  <p className="text-slate-600">{g.explanation}</p>
                  <div className="text-[11px] text-blue-800 bg-blue-50 p-1.5 rounded border border-blue-100 font-medium">
                    Required Action: {g.verification_requirement}
                  </div>
                </div>
              ))
            ) : (
              <div className="p-4 text-center text-slate-500 bg-slate-50 rounded">
                No major specification gaps identified for this candidate standard.
              </div>
            )}
          </div>
        )}
      </div>

      {/* ================================================================= */}
      {/* SECTION F: Evidence Items                                         */}
      {/* ================================================================= */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div
          onClick={() => toggleSection('evidence')}
          className="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between cursor-pointer select-none hover:bg-slate-100/80 transition-colors"
        >
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800 flex items-center gap-2">
            <FileText className="w-4 h-4 text-blue-600" />
            F. Authoritative Evidence Items ({candidate.evidence?.length || 0})
          </h3>
          {openSections.evidence ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
        </div>

        {openSections.evidence && (
          <div className="p-5 text-xs space-y-3">
            {candidate.evidence && candidate.evidence.length > 0 ? (
              candidate.evidence.map((ev, idx) => (
                <div key={idx} className="p-3 bg-slate-50 rounded-lg border border-slate-200 space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="font-mono font-semibold text-slate-700 bg-slate-200 px-1.5 py-0.5 rounded text-[11px]">
                      {ev.source_type} ({ev.source_id})
                    </span>
                    <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-slate-200 text-slate-800">
                      {ev.verification_status}
                    </span>
                  </div>
                  <p className="font-semibold text-slate-900">{ev.claim}</p>
                  <div className="text-slate-600 font-mono text-[11px] bg-white p-2 rounded border border-slate-200 whitespace-pre-wrap">
                    {ev.evidence_text}
                  </div>
                </div>
              ))
            ) : (
              <div className="p-4 text-center text-slate-500 bg-slate-50 rounded">
                No direct evidence items attached.
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
