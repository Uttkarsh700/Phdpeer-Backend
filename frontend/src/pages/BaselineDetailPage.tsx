/**
 * Baseline Detail Page
 * 
 * View baseline details and create draft timelines.
 */

import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { baselineService, timelineService } from '@/services';
import type { Baseline } from '@/types/api';

export function Component() {
  const { baselineId } = useParams<{ baselineId: string }>();
  const navigate = useNavigate();

  const [baseline, setBaseline] = useState<Baseline | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [creatingTimeline, setCreatingTimeline] = useState(false);

  useEffect(() => {
    loadBaseline();
  }, [baselineId]);

  const loadBaseline = async () => {
    if (!baselineId) return;

    setLoading(true);
    setError(null);

    try {
      const data = await baselineService.getById(baselineId);
      setBaseline(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load baseline');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTimeline = async () => {
    if (!baselineId) return;

    setCreatingTimeline(true);
    setError(null);

    try {
      const { draftTimelineId } = await timelineService.createDraft({
        baselineId,
        title: `${baseline?.programName} Timeline`,
        description: `Timeline generated from baseline`,
      });

      navigate(`/timelines/draft/${draftTimelineId}`);
    } catch (err: any) {
      setError(err.message || 'Failed to create timeline');
      setCreatingTimeline(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-4"></div>
          <p className="text-gray-600">Loading baseline...</p>
        </div>
      </div>
    );
  }

  if (error && !baseline) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-red-900 mb-2">Error</h3>
        <p className="text-red-800">{error}</p>
      </div>
    );
  }

  if (!baseline) {
    return <div className="text-center py-12"><p className="text-gray-600">Baseline not found</p></div>;
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Baseline Details</h1>
        <p className="mt-2 text-gray-600">View and manage your PhD program baseline</p>
      </div>

      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900">{baseline.programName}</h2>
            <button
              onClick={handleCreateTimeline}
              disabled={creatingTimeline}
              className="px-6 py-2 text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {creatingTimeline ? 'Creating...' : 'Create Timeline'}
            </button>
          </div>
        </div>

        <div className="px-6 py-4 space-y-4">
          <div className="grid grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700">Institution</label>
              <p className="mt-1 text-sm text-gray-900">{baseline.institution}</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Field of Study</label>
              <p className="mt-1 text-sm text-gray-900">{baseline.fieldOfStudy}</p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700">Start Date</label>
              <p className="mt-1 text-sm text-gray-900">
                {new Date(baseline.startDate).toLocaleDateString()}
              </p>
            </div>
            {baseline.expectedEndDate && (
              <div>
                <label className="block text-sm font-medium text-gray-700">Expected End Date</label>
                <p className="mt-1 text-sm text-gray-900">
                  {new Date(baseline.expectedEndDate).toLocaleDateString()}
                </p>
              </div>
            )}
          </div>

          {baseline.researchArea && (
            <div>
              <label className="block text-sm font-medium text-gray-700">Research Area</label>
              <p className="mt-1 text-sm text-gray-900">{baseline.researchArea}</p>
            </div>
          )}

          {baseline.requirementsSummary && (
            <div>
              <label className="block text-sm font-medium text-gray-700">Requirements Summary</label>
              <p className="mt-1 text-sm text-gray-900 whitespace-pre-wrap">{baseline.requirementsSummary}</p>
            </div>
          )}

          {baseline.notes && (
            <div>
              <label className="block text-sm font-medium text-gray-700">Notes</label>
              <p className="mt-1 text-sm text-gray-900 whitespace-pre-wrap">{baseline.notes}</p>
            </div>
          )}
        </div>

        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
          <div className="flex items-center justify-between text-sm text-gray-500">
            <span>Created: {new Date(baseline.createdAt).toLocaleDateString()}</span>
            <span>Updated: {new Date(baseline.updatedAt).toLocaleDateString()}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

Component.displayName = 'BaselineDetailPage';
