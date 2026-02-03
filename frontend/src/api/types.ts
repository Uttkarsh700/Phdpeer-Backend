/**
 * API Type Utilities
 * 
 * Type helpers for API requests and responses.
 */

/**
 * Extract response data type from a service method
 * 
 * @example
 * ```ts
 * type AssessmentResponse = ExtractResponse<typeof assessmentService.getLatest>;
 * ```
 */
export type ExtractResponse<T> = T extends (...args: any[]) => Promise<infer R>
  ? R
  : never;

/**
 * Extract request data type from a service method
 * 
 * @example
 * ```ts
 * type SubmitRequest = ExtractRequest<typeof assessmentService.submitQuestionnaire>;
 * ```
 */
export type ExtractRequest<T> = T extends (data: infer D, ...args: any[]) => Promise<any>
  ? D
  : T extends (...args: any[]) => Promise<any>
  ? never
  : never;

/**
 * Paginated request parameters
 */
export interface PaginatedRequest {
  skip?: number;
  limit?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

/**
 * Standard paginated response
 */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
  hasNext: boolean;
  hasPrev: boolean;
}

/**
 * Request with query parameters
 */
export interface QueryParams {
  [key: string]: string | number | boolean | undefined | null;
}

/**
 * Request with path parameters
 */
export interface PathParams {
  [key: string]: string | number;
}
