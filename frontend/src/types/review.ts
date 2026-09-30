/**
 * frontend/src/types/review.ts
 * Type definitions matching PS26108 Phase 7 Backend API schemas.
 */

export type OfficerDecisionState =
  | 'PENDING'
  | 'UNDER_REVIEW'
  | 'ACCEPTED'
  | 'REJECTED'
  | 'NEEDS_VERIFICATION'
  | 'REQUEST_REVISION';

export type VerificationState =
  | 'UNVERIFIED'
  | 'VERIFIED'
  | 'CONFLICTING'
  | 'NOT_APPLICABLE';

export type CoverageStatus =
  | 'MATCH'
  | 'PARTIAL_MATCH'
  | 'NO_MATCH'
  | 'UNKNOWN'
  | 'CONFLICT';

export type RejectionReason =
  | 'WRONG_PRODUCT'
  | 'WRONG_SECTOR'
  | 'INSUFFICIENT_TECHNICAL_COVERAGE'
  | 'PARAMETER_CONFLICT'
  | 'OUTDATED_STANDARD'
  | 'REGULATORY_MISMATCH'
  | 'INSUFFICIENT_EVIDENCE'
  | 'DUPLICATE_STANDARD'
  | 'OTHER';

export type AIRecommendationState =
  | 'HIGHLY_RECOMMENDED'
  | 'RECOMMENDED_FOR_REVIEW'
  | 'REVIEW_REQUIRED'
  | 'INSUFFICIENT_COVERAGE'
  | 'NOT_RECOMMENDED';

export interface CoverageItem {
  status: CoverageStatus;
  requirement_val?: any;
  standard_val?: any;
  explanation: string;
  evidence?: string;
  confidence: number;
}

export interface RequirementCoverage {
  product: CoverageItem;
  sector: CoverageItem;
  application: CoverageItem;
  materials: CoverageItem;
  parameters: Record<string, CoverageItem>;
  direct_matches: number;
  partial_matches: number;
  unknown_count: number;
  conflicts_count: number;
  no_match_count: number;
  summary: string;
}

export interface SpecificationGap {
  category: string;
  severity: 'HIGH' | 'MEDIUM' | 'LOW';
  title: string;
  explanation: string;
  evidence?: string;
  verification_requirement: string;
}

export interface VerificationItemDTO {
  id: number;
  review_id: number;
  candidate_id?: number;
  standard_id?: string;
  item_key: string;
  title: string;
  category: string;
  system_state: string;
  officer_state: VerificationState;
  is_regulatory: boolean;
  system_evidence?: any;
  officer_evidence_reference?: string;
  officer_note?: string;
  verified_at?: string;
  verified_by?: string;
  created_at?: string;
}

export interface EvidenceItem {
  source_type: string;
  source_id: string;
  source_url?: string;
  claim: string;
  evidence_text: string;
  verification_status: string;
}

export interface CandidateDTO {
  id: number;
  review_id: number;
  standard_id: string;
  is_number: string;
  title: string;
  sector?: string;
  application?: string;
  materials: string[];
  technical_parameters: string[];
  retrieval_rank: number;
  reranker_score?: number;
  rrf_score?: number;
  retrieval_method: string;
  requirement_coverage?: RequirementCoverage;
  gaps?: SpecificationGap[];
  standard_status?: string;
  qco_status?: string;
  qco_ids: string[];
  order_names: string[];
  effective_date?: string;
  authority?: string;
  ai_recommendation_state: AIRecommendationState;
  notes?: string;
  evidence?: EvidenceItem[];
  normative_references?: Array<Record<string, any>>;
  verification_items: VerificationItemDTO[];
}

export interface OfficerDecisionDTO {
  state: OfficerDecisionState;
  selected_candidate_id?: number;
  selected_standard_id?: string;
  selected_is_number?: string;
  ai_recommendation_state?: string;
  is_override: boolean;
  rejection_reason?: RejectionReason;
  rejection_note?: string;
  officer_id?: string;
  officer_role?: string;
  decision_summary?: string;
  supporting_evidence_references?: string[];
  timestamp?: string;
}

export interface AuditEventDTO {
  id: number;
  review_id: number;
  event_type: string;
  previous_state?: string;
  new_state?: string;
  actor_id: string;
  actor_role: string;
  details?: Record<string, any>;
  timestamp: string;
}

export interface ReviewDetailDTO {
  id: number;
  review_id: string;
  raw_text: string;
  input_type: string;
  procurement_requirements?: Record<string, any>;
  status: OfficerDecisionState;
  selected_candidate_id?: number;
  candidates: CandidateDTO[];
  verification_items: VerificationItemDTO[];
  officer_decision?: OfficerDecisionDTO;
  audit_events: AuditEventDTO[];
  created_at?: string;
  updated_at?: string;
}

export interface DashboardStats {
  total_reviews: number;
  pending_reviews: number;
  under_review: number;
  accepted_reviews: number;
  rejected_reviews: number;
  needs_verification_reviews: number;
  request_revision_reviews: number;
  total_standards_indexed: number;
  total_qco_orders_indexed: number;
  recent_reviews: ReviewDetailDTO[];
}

export interface CandidateComparisonResponse {
  review_id: string;
  candidates: CandidateDTO[];
  facet_comparison: Array<{ dimension: string; values: Record<string, any> }>;
  regulatory_comparison: Array<{ dimension: string; values: Record<string, any> }>;
  gaps_comparison: Array<{ dimension: string; values: Record<string, any> }>;
}
