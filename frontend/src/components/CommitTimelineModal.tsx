/**
 * Commit Timeline Modal
 * 
 * Explicit confirmation dialog for committing a draft timeline.
 * 
 * Behavior:
 * - Shows confirmation dialog with timeline preview
 * - Allows optional title/description override
 * - Calls POST /timeline/commit on confirmation
 * - No business rule validation (frontend passes data through)
 */

import { useState, FormEvent } from 'react';

export interface CommitTimelineModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (data: { title?: string; description?: string }) => Promise<void>;
  currentTitle: string;
  currentDescription?: string | null;
  isLoading?: boolean;
}

export function CommitTimelineModal({
  isOpen,
  onClose,
  onConfirm,
  currentTitle,
  currentDescription,
  isLoading = false,
}: CommitTimelineModalProps) {
  const [title, setTitle] = useState(currentTitle);
  const [description, setDescription] = useState(currentDescription || '');
  const [error, setError] = useState<string | null>(null);

  // Reset form when modal opens/closes
  const handleClose = () => {
    setTitle(currentTitle);
    setDescription(currentDescription || '');
    setError(null);
    onClose();
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);

    try {
      await onConfirm({
        title: title.trim() || undefined,
        description: description.trim() || undefined,
      });
      // Modal will be closed by parent after successful commit
    } catch (err: any) {
      setError(err.message || 'Failed to commit timeline');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-lg w-full">
        <form onSubmit={handleSubmit}>
          {/* Header */}
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">Commit Timeline</h2>
            <p className="mt-1 text-sm text-gray-600">
              Create an immutable version of this timeline. This action cannot be undone.
            </p>
          </div>

          {/* Content */}
          <div className="px-6 py-4 space-y-4">
            {/* Warning */}
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-yellow-800">
                    <strong>Warning:</strong> Once committed, this timeline becomes immutable and cannot be modified. 
                    The draft will be frozen and you'll be redirected to the committed timeline view.
                  </p>
                </div>
              </div>
            </div>

            {/* Title */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Timeline Title
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g., PhD Timeline v1.0"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                disabled={isLoading}
              />
              <p className="mt-1 text-xs text-gray-500">
                Leave empty to use current title: "{currentTitle}"
              </p>
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Description (Optional)
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Optional description of this committed version..."
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                disabled={isLoading}
              />
            </div>

            {/* Error Message */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                <p className="text-sm text-red-800">{error}</p>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-end space-x-3">
            <button
              type="button"
              onClick={handleClose}
              className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500"
              disabled={isLoading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-6 py-2 text-white bg-green-600 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={isLoading}
            >
              {isLoading ? 'Committing...' : 'Commit Timeline'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
