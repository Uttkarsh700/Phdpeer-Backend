/**
 * API type definitions
 * 
 * Defines types for API requests and responses.
 */

// Common API response wrapper
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  errors?: string[];
}

// Pagination
export interface PaginationParams {
  skip?: number;
  limit?: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
  hasNext: boolean;
  hasPrev: boolean;
}

// User types
export interface User {
  id: string;
  email: string;
  fullName: string;
  institution?: string;
  fieldOfStudy?: string;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

// Document types
export interface DocumentArtifact {
  id: string;
  userId: string;
  title: string;
  description?: string;
  fileType: string;
  filePath: string;
  fileSizeBytes: number;
  documentType?: string;
  createdAt: string;
  updatedAt: string;
}

// Baseline types
export interface Baseline {
  id: string;
  userId: string;
  documentArtifactId?: string;
  programName: string;
  institution: string;
  fieldOfStudy: string;
  startDate: string;
  expectedEndDate?: string;
  totalDurationMonths?: number;
  requirementsSummary?: string;
  researchArea?: string;
  advisorInfo?: string;
  fundingStatus?: string;
  notes?: string;
  createdAt: string;
  updatedAt: string;
}

// Timeline types
export interface DraftTimeline {
  id: string;
  userId: string;
  baselineId: string;
  title: string;
  description?: string;
  versionNumber?: string;
  isActive: boolean;
  notes?: string;
  createdAt: string;
  updatedAt: string;
}

export interface CommittedTimeline {
  id: string;
  userId: string;
  baselineId?: string;
  draftTimelineId?: string;
  title: string;
  description?: string;
  committedDate: string;
  targetCompletionDate?: string;
  notes?: string;
  createdAt: string;
  updatedAt: string;
}

export interface TimelineStage {
  id: string;
  draftTimelineId?: string;
  committedTimelineId?: string;
  title: string;
  description?: string;
  stageOrder: number;
  startDate?: string;
  endDate?: string;
  durationMonths?: number;
  status: string;
  notes?: string;
  createdAt: string;
  updatedAt: string;
}

export interface TimelineMilestone {
  id: string;
  timelineStageId: string;
  title: string;
  description?: string;
  milestoneOrder: number;
  targetDate?: string;
  actualCompletionDate?: string;
  isCompleted: boolean;
  isCritical: boolean;
  deliverableType?: string;
  notes?: string;
  createdAt: string;
  updatedAt: string;
}

// Progress types
export interface ProgressEvent {
  id: string;
  userId: string;
  milestoneId?: string;
  eventType: string;
  title: string;
  description: string;
  eventDate: string;
  impactLevel?: string;
  tags?: string;
  notes?: string;
  createdAt: string;
  updatedAt: string;
}

// Assessment types
export interface JourneyAssessment {
  id: string;
  userId: string;
  assessmentDate: string;
  assessmentType: string;
  overallProgressRating?: number;
  researchQualityRating?: number;
  timelineAdherenceRating?: number;
  strengths?: string;
  challenges?: string;
  actionItems?: string;
  advisorFeedback?: string;
  notes?: string;
  createdAt: string;
  updatedAt: string;
}

export interface AssessmentSummary {
  assessmentId: string;
  overallScore: number;
  overallStatus: 'excellent' | 'good' | 'fair' | 'concerning' | 'critical';
  assessmentDate: string;
  totalResponses: number;
  dimensions: Record<string, {
    score: number;
    status: string;
    strengths: string[];
    concerns: string[];
  }>;
  criticalAreas: Array<{
    dimension: string;
    score: number;
    concerns: string[];
  }>;
  healthyAreas: Array<{
    dimension: string;
    score: number;
    strengths: string[];
  }>;
  recommendations: Array<{
    priority: 'high' | 'medium' | 'low';
    title: string;
    description: string;
    dimension: string;
    actionItems: string[];
  }>;
  summary: string;
}

// Request types
export interface CreateBaselineRequest {
  documentId?: string;
  programName: string;
  institution: string;
  fieldOfStudy: string;
  startDate: string;
  expectedEndDate?: string;
  totalDurationMonths?: number;
  requirementsSummary?: string;
  researchArea?: string;
  advisorInfo?: string;
  fundingStatus?: string;
  notes?: string;
}

export interface CreateTimelineRequest {
  baselineId: string;
  title?: string;
  description?: string;
  versionNumber?: string;
}

export interface CommitTimelineRequest {
  draftTimelineId: string;
  title?: string;
  description?: string;
}

export interface QuestionnaireResponse {
  dimension: string;
  questionId: string;
  responseValue: number;
  questionText?: string;
}

export interface SubmitQuestionnaireRequest {
  responses: QuestionnaireResponse[];
  assessmentType?: string;
  notes?: string;
}

// Error types
export interface ApiError {
  message: string;
  code?: string;
  details?: any;
}
