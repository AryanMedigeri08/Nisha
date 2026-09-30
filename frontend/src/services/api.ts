/**
 * frontend/src/services/api.ts
 * REST client for communicating with PS26108 FastAPI backend.
 */

import {
  ReviewDetailDTO,
  CandidateComparisonResponse,
  DashboardStats,
  OfficerDecisionDTO,
  VerificationItemDTO,
  AuditEventDTO,
  OfficerDecisionState,
  VerificationState,
  RejectionReason,
} from '../types/review';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errorDetail = `HTTP ${res.status}: ${res.statusText}`;
    try {
      const errJson = await res.json();
      if (errJson.detail) {
        errorDetail = typeof errJson.detail === 'string' ? errJson.detail : JSON.stringify(errJson.detail);
      }
    } catch {
      // ignore
    }
    throw new Error(errorDetail);
  }
  return res.json();
}

export const api = {
  // Dashboard Metrics
  async getDashboardStats(): Promise<DashboardStats> {
    const res = await fetch(`${BASE_URL}/api/dashboard/stats`);
    return handleResponse<DashboardStats>(res);
  },

  // Review List
  async listReviews(params?: {
    status?: string;
    skip?: number;
    limit?: number;
  }): Promise<{ total: number; reviews: ReviewDetailDTO[] }> {
    const query = new URLSearchParams();
    if (params?.status) query.set('status', params.status);
    if (params?.skip !== undefined) query.set('skip', params.skip.toString());
    if (params?.limit !== undefined) query.set('limit', params.limit.toString());

    const res = await fetch(`${BASE_URL}/api/reviews?${query.toString()}`);
    return handleResponse<{ total: number; reviews: ReviewDetailDTO[] }>(res);
  },

  // Create Review from Query
  async createReview(queryText: string, inputType: string = 'text'): Promise<ReviewDetailDTO> {
    const res = await fetch(`${BASE_URL}/api/reviews`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query_text: queryText, input_type: inputType }),
    });
    return handleResponse<ReviewDetailDTO>(res);
  },

  // Get Review Detail
  async getReview(reviewId: string): Promise<ReviewDetailDTO> {
    const res = await fetch(`${BASE_URL}/api/reviews/${reviewId}`);
    return handleResponse<ReviewDetailDTO>(res);
  },

  // Update Verification Item
  async updateVerification(
    reviewId: string,
    data: {
      verification_item_id: number;
      officer_state: VerificationState;
      evidence_reference?: string;
      officer_note?: string;
      officer_id?: string;
    }
  ): Promise<VerificationItemDTO> {
    const res = await fetch(`${BASE_URL}/api/reviews/${reviewId}/verify`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse<VerificationItemDTO>(res);
  },

  // Submit Officer Decision
  async submitDecision(
    reviewId: string,
    data: {
      state: OfficerDecisionState;
      selected_candidate_id?: number;
      rejection_reason?: RejectionReason;
      rejection_note?: string;
      officer_id?: string;
      officer_role?: string;
      decision_summary?: string;
      supporting_evidence_references?: string[];
    }
  ): Promise<OfficerDecisionDTO> {
    const res = await fetch(`${BASE_URL}/api/reviews/${reviewId}/decision`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse<OfficerDecisionDTO>(res);
  },

  // Reopen Review
  async reopenReview(
    reviewId: string,
    data: {
      reason: string;
      officer_id?: string;
    }
  ): Promise<ReviewDetailDTO> {
    const res = await fetch(`${BASE_URL}/api/reviews/${reviewId}/reopen`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse<ReviewDetailDTO>(res);
  },

  // Candidate Comparison Matrix
  async getComparison(reviewId: string, candidateIds: number[]): Promise<CandidateComparisonResponse> {
    const res = await fetch(
      `${BASE_URL}/api/reviews/${reviewId}/comparison?candidate_ids=${candidateIds.join(',')}`
    );
    return handleResponse<CandidateComparisonResponse>(res);
  },

  // Audit Events
  async getAuditTrail(reviewId: string): Promise<AuditEventDTO[]> {
    const res = await fetch(`${BASE_URL}/api/reviews/${reviewId}/audit`);
    return handleResponse<AuditEventDTO[]>(res);
  },

  // Example Queries
  async getExampleQueries(): Promise<Array<{ title: string; query: string; target_is?: string }>> {
    const res = await fetch(`${BASE_URL}/api/examples`);
    return handleResponse<Array<{ title: string; query: string; target_is?: string }>>(res);
  },

  // System Health
  async getHealth(): Promise<{ status: string; database: string }> {
    const res = await fetch(`${BASE_URL}/health`);
    return handleResponse<{ status: string; database: string }>(res);
  },
};
