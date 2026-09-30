import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Navbar } from './components/Navbar';
import { DashboardPage } from './pages/DashboardPage';
import { NewQueryPage } from './pages/NewQueryPage';
import { ReviewWorkspacePage } from './pages/ReviewWorkspacePage';
import { CandidateDetailPage } from './pages/CandidateDetailPage';
import { ComparisonPage } from './pages/ComparisonPage';
import { ReviewListPage } from './pages/ReviewListPage';
import { CandidateDTO } from './types/review';

const queryClient = new QueryClient();

export function App() {
  const [currentTab, setCurrentTab] = useState<string>('dashboard');
  const [activeReviewId, setActiveReviewId] = useState<string>('');
  const [activeCandidate, setActiveCandidate] = useState<CandidateDTO | null>(null);
  const [comparisonCandidateIds, setComparisonCandidateIds] = useState<number[]>([]);

  const handleNavigate = (tab: string, reviewId?: string) => {
    setCurrentTab(tab);
    if (reviewId) {
      setActiveReviewId(reviewId);
    }
  };

  const handleReviewCreated = (reviewId: string) => {
    setActiveReviewId(reviewId);
    setCurrentTab('workspace');
  };

  const handleLaunchComparison = (candidateIds: number[]) => {
    setComparisonCandidateIds(candidateIds);
    setCurrentTab('comparison');
  };

  const handleViewCandidateDetail = (candidate: CandidateDTO) => {
    setActiveCandidate(candidate);
    setCurrentTab('candidate-detail');
  };

  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans">
        <Navbar currentTab={currentTab} onNavigate={handleNavigate} />

        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 pt-6">
          {currentTab === 'dashboard' && (
            <DashboardPage onNavigate={handleNavigate} />
          )}

          {currentTab === 'new-query' && (
            <NewQueryPage onReviewCreated={handleReviewCreated} />
          )}

          {currentTab === 'workspace' && activeReviewId && (
            <ReviewWorkspacePage
              reviewId={activeReviewId}
              onNavigate={handleNavigate}
              onCompare={handleLaunchComparison}
              onViewCandidateDetail={handleViewCandidateDetail}
            />
          )}

          {currentTab === 'candidate-detail' && activeCandidate && (
            <CandidateDetailPage
              candidate={activeCandidate}
              onBack={() => setCurrentTab('workspace')}
            />
          )}

          {currentTab === 'comparison' && activeReviewId && (
            <ComparisonPage
              reviewId={activeReviewId}
              candidateIds={comparisonCandidateIds}
              onBack={() => setCurrentTab('workspace')}
            />
          )}

          {currentTab === 'reviews' && (
            <ReviewListPage onNavigate={handleNavigate} />
          )}
        </main>

        {/* Footer */}
        <footer className="bg-white border-t border-slate-200 py-6 text-center text-xs text-slate-500">
          <div className="max-w-7xl mx-auto px-4 space-y-1">
            <p className="font-semibold text-slate-700">
              PS26108 — AI-Powered Indian Standards Recommendation Engine (Phase 7 Production Prototype)
            </p>
            <p className="text-[11px] text-slate-400">
              Hybrid Retrieval (BM25 + all-MiniLM-L6-v2) • Cross-Encoder Reranking • Knowledge Graph & QCO Resolution • Human-in-the-Loop Decision Support
            </p>
          </div>
        </footer>
      </div>
    </QueryClientProvider>
  );
}

export default App;
