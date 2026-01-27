/**
 * Document Service
 * 
 * Handles document upload and management API calls.
 */

import { api } from './api.client';
import type { DocumentArtifact, ApiResponse } from '@/types/api';

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
    return api.upload('/api/v1/documents/upload', file, onProgress);
  },

  /**
   * Get document by ID
   */
  getById: async (documentId: string): Promise<DocumentArtifact> => {
    return api.get(`/api/v1/documents/${documentId}`);
  },

  /**
   * Get user's documents
   */
  getUserDocuments: async (skip?: number, limit?: number): Promise<DocumentArtifact[]> => {
    return api.get('/api/v1/documents', { skip, limit });
  },

  /**
   * Get extracted text from document
   */
  getExtractedText: async (documentId: string): Promise<{ text: string }> => {
    return api.get(`/api/v1/documents/${documentId}/text`);
  },

  /**
   * Delete document
   */
  delete: async (documentId: string): Promise<void> => {
    return api.delete(`/api/v1/documents/${documentId}`);
  },
};

export default documentService;
