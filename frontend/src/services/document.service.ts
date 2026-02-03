/**
 * Document Service
 * 
 * Handles document upload and management API calls.
 * 
 * IMPORTANT: All API calls go through @/api/client (apiClient)
 */

import { apiClient } from '@/api/client';
import { ENDPOINTS } from '@/api/endpoints';
import type { DocumentArtifact } from '@/types/api';

export const documentService = {
  /**
   * Upload a document
   */
  upload: async (
    file: File,
    title?: string,
    description?: string,
    documentType?: string,
    onProgress?: (progress: number) => void
  ): Promise<{ documentId: string }> => {
    return apiClient.upload<{ documentId: string }>(
      ENDPOINTS.DOCUMENTS.UPLOAD,
      file,
      { onProgress }
    );
  },

  /**
   * Get document by ID
   */
  getById: async (documentId: string): Promise<DocumentArtifact> => {
    return apiClient.get<DocumentArtifact>(ENDPOINTS.DOCUMENTS.GET_BY_ID(documentId));
  },

  /**
   * Get user's documents
   */
  getUserDocuments: async (skip?: number, limit?: number): Promise<DocumentArtifact[]> => {
    return apiClient.get<DocumentArtifact[]>(ENDPOINTS.DOCUMENTS.LIST, { skip, limit });
  },

  /**
   * Get extracted text from document
   */
  getExtractedText: async (documentId: string): Promise<{ text: string }> => {
    return apiClient.get<{ text: string }>(`${ENDPOINTS.DOCUMENTS.GET_BY_ID(documentId)}/text`);
  },

  /**
   * Delete document
   */
  delete: async (documentId: string): Promise<void> => {
    return apiClient.delete<void>(ENDPOINTS.DOCUMENTS.DELETE(documentId));
  },
};

export default documentService;
