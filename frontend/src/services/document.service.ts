/**
 * Document Service
 * 
 * Handles document upload operations.
 * Maps to: POST /api/v1/documents/upload
 * Uses: DocumentService (backend)
 */

import { post } from '@/api/client';

/**
 * Document upload response
 * Backend DocumentService.upload_document() returns UUID directly
 * API endpoint should wrap it in a response object
 */
export interface DocumentUploadResponse {
  document_id: string; // UUID - returned by DocumentService.upload_document()
}

/**
 * Upload a document file
 * 
 * One user action → one orchestrator call
 * UI waits for backend response (no optimistic success)
 * 
 * @param file - File to upload (PDF or DOCX)
 * @param userId - User ID (UUID string)
 * @param title - Optional document title (defaults to filename)
 * @param description - Optional document description
 * @param documentType - Optional document type (e.g., 'research_proposal')
 * @returns Document upload response with document ID
 * @throws ApiError if upload fails
 */
export async function uploadDocument(
  file: File,
  userId: string,
  title?: string,
  description?: string,
  documentType?: string
): Promise<DocumentUploadResponse> {
  // Create FormData for file upload
  // Backend expects: file_content (bytes), filename, user_id, title, description, document_type
  const formData = new FormData();
  formData.append('file', file); // File object - backend will read as bytes
  formData.append('filename', file.name);
  formData.append('user_id', userId);
  
  if (title) {
    formData.append('title', title);
  }
  if (description) {
    formData.append('description', description);
  }
  if (documentType) {
    formData.append('document_type', documentType);
  }

  // Call backend endpoint - wait for response (no optimistic success)
  const response = await post<DocumentUploadResponse>(
    '/documents/upload',
    formData,
    {
      // Don't set Content-Type header - browser will set it with boundary for FormData
      headers: {},
    }
  );

  // Backend returns document_id (UUID)
  return response.data;
}
