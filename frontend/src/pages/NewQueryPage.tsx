import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import {
  Sparkles,
  Send,
  RotateCcw,
  BookOpen,
  CheckCircle2,
  Clock,
  Layers,
  Search,
  Scale,
  FileCheck2,
  AlertCircle,
} from 'lucide-react';

interface NewQueryPageProps {
  onReviewCreated: (reviewId: string) => void;
}

export const NewQueryPage: React.FC<NewQueryPageProps> = ({ onReviewCreated }) => {
  const [queryText, setQueryText] = useState('');
  const [examples, setExamples] = useState<Array<{ title: string; query: string; target_is?: string }>>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [activeStep, setActiveStep] = useState<number>(0);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    loadExamples();
  }, []);

  const loadExamples = async () => {
    try {
      const data = await api.getExampleQueries();
      setExamples(data);
    } catch {
      // Fallback default examples if API fails
      setExamples([
        {
          title: 'Domestic LPG Gas Stoves',
          query: 'Procurement of domestic LPG gas stoves for institutional kitchens with stainless steel body and dual burner.',
          target_is: 'IS 4246',
        },
        {
          title: 'Ordinary Portland Cement 43 Grade',
          query: 'Supply of ordinary portland cement 43 grade in 50kg bags for highway bridge pier construction.',
          target_is: 'IS 269',
        },
        {
          title: 'Submersible Pumpsets',
          query: 'Procurement of agricultural submersible pump sets and single-phase electric motors for rural irrigation.',
          target_is: 'IS 8034',
        },
        {
          title: 'Distribution Transformers',
          query: 'Outdoor type three phase oil immersed distribution transformers 11kV/433V 100kVA with copper winding.',
          target_is: 'IS 1180',
        },
      ]);
    }
  };

  const pipelineStages = [
    { title: 'Requirement Extraction', desc: 'Parsing product, sector, materials, and technical parameters' },
    { title: 'Hybrid Retrieval', desc: 'Sparse BM25 + Dense all-MiniLM-L6-v2 vector indexing' },
    { title: 'Cross-Encoder Reranking', desc: 'ms-marco-MiniLM-L-6-v2 neural reranking' },
    { title: 'Regulatory Resolution', desc: 'Evaluating DPIIT Scheme-1 QCO and Gazette enforcement' },
    { title: 'Recommendation & Review Package', desc: 'Constructing coverage matrix, gaps, and verification checklist' },
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!queryText.trim()) {
      setErrorMsg('Please enter a procurement requirement or specification.');
      return;
    }

    setErrorMsg(null);
    setIsLoading(true);
    setActiveStep(1);

    // Simulate incremental stage feedback while backend executes
    const timer1 = setTimeout(() => setActiveStep(2), 600);
    const timer2 = setTimeout(() => setActiveStep(3), 1200);
    const timer3 = setTimeout(() => setActiveStep(4), 1800);
    const timer4 = setTimeout(() => setActiveStep(5), 2400);

    try {
      const review = await api.createReview(queryText.trim(), 'text');
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
      clearTimeout(timer4);
      setActiveStep(5);
      setTimeout(() => {
        onReviewCreated(review.review_id);
      }, 500);
    } catch (err: any) {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
      clearTimeout(timer4);
      setErrorMsg(err.message || 'Failed to process procurement query.');
      setIsLoading(false);
      setActiveStep(0);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-12">
      {/* Header */}
      <div>
        <h1 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
          New Procurement Tender Specification Review
        </h1>
        <p className="text-xs sm:text-sm text-slate-500 mt-1">
          Input your raw tender technical schedule or procurement description. The system will extract
          specifications, search 91 indexed standards, evaluate QCO regulatory orders, and prepare a decision-support package.
        </p>
      </div>

      {/* Main Input Card */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 space-y-4">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-2">
              Procurement Requirement Description <span className="text-rose-600">*</span>
            </label>
            <textarea
              rows={5}
              value={queryText}
              onChange={(e) => setQueryText(e.target.value)}
              disabled={isLoading}
              placeholder="e.g. Procurement of domestic LPG gas stoves for institutional kitchens with stainless steel body and dual burner..."
              className="w-full text-sm bg-white border border-slate-300 rounded-lg p-3.5 text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all font-sans"
              required
            />
          </div>

          {/* Form Actions */}
          <div className="flex items-center justify-between pt-2">
            <button
              type="button"
              onClick={() => {
                setQueryText('');
                setErrorMsg(null);
              }}
              disabled={isLoading || !queryText}
              className="px-3 py-1.5 text-xs font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-md transition-colors flex items-center gap-1.5 disabled:opacity-40"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Clear</span>
            </button>

            <button
              type="submit"
              disabled={isLoading || !queryText.trim()}
              className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg shadow-sm disabled:opacity-50 transition-colors flex items-center gap-2"
            >
              <Send className="w-4 h-4" />
              <span>{isLoading ? 'Processing Pipeline...' : 'Submit Tender Query'}</span>
            </button>
          </div>
        </form>

        {/* Error Alert */}
        {errorMsg && (
          <div className="p-3 bg-rose-50 border border-rose-200 rounded-lg text-xs text-rose-800 flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}
      </div>

      {/* Loading Progress Stages */}
      {isLoading && (
        <div className="bg-slate-900 text-white rounded-xl p-6 shadow-xl border border-slate-800 space-y-4 animate-in fade-in duration-300">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-blue-400 flex items-center gap-2">
              <Sparkles className="w-4 h-4" />
              Executing Decision Support Pipeline
            </span>
            <span className="text-xs font-mono text-slate-400">Stage {activeStep} of 5</span>
          </div>

          <div className="space-y-3">
            {pipelineStages.map((stage, idx) => {
              const stepNum = idx + 1;
              const isDone = activeStep > stepNum;
              const isCurrent = activeStep === stepNum;

              return (
                <div
                  key={stage.title}
                  className={`p-3 rounded-lg border transition-all flex items-center justify-between ${
                    isDone
                      ? 'bg-emerald-950/40 border-emerald-800 text-emerald-300'
                      : isCurrent
                      ? 'bg-blue-950/60 border-blue-600 text-white ring-1 ring-blue-500'
                      : 'bg-slate-800/40 border-slate-800 text-slate-500'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div
                      className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold font-mono ${
                        isDone
                          ? 'bg-emerald-600 text-white'
                          : isCurrent
                          ? 'bg-blue-600 text-white animate-pulse'
                          : 'bg-slate-700 text-slate-400'
                      }`}
                    >
                      {isDone ? <CheckCircle2 className="w-4 h-4" /> : stepNum}
                    </div>
                    <div>
                      <div className="text-xs font-semibold">{stage.title}</div>
                      <div className="text-[11px] opacity-80">{stage.desc}</div>
                    </div>
                  </div>

                  {isCurrent && (
                    <span className="text-[10px] uppercase tracking-wider font-mono text-blue-400 bg-blue-900/60 px-2 py-0.5 rounded border border-blue-700">
                      Running...
                    </span>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Example Queries Section */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-slate-500" />
            Example Procurement Specifications (Synthetic / Seed Ground Truth)
          </h3>
          <span className="text-[10px] bg-slate-100 text-slate-600 px-2 py-0.5 rounded font-mono">
            Click to fill
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {examples.map((ex, idx) => (
            <div
              key={idx}
              onClick={() => {
                setQueryText(ex.query);
                setErrorMsg(null);
              }}
              className="p-3.5 rounded-lg border border-slate-200 hover:border-blue-400 hover:bg-blue-50/30 cursor-pointer transition-all text-xs space-y-1 group"
            >
              <div className="flex items-center justify-between font-semibold text-slate-900 group-hover:text-blue-700">
                <span>{ex.title}</span>
                {ex.target_is && (
                  <span className="text-[10px] font-mono bg-slate-100 text-slate-700 px-1.5 py-0.5 rounded border border-slate-200">
                    Target: {ex.target_is}
                  </span>
                )}
              </div>
              <p className="text-slate-600 text-[11px] line-clamp-2">{ex.query}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
