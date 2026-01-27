/**
 * Timelines Page
 * 
 * List all draft and committed timelines.
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { timelineService } from '@/services';
import type { DraftTimeline, CommittedTimeline } from '@/types/api';

export function Component() {
  const navigate = useNavigate();

  const [draftTimelines, setDraftTimelines] = useState<DraftTimeline[]>([]);
  const [committedTimelines, setCommittedTimelines] = useState<CommittedTimeline[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'drafts' | 'committed'>('drafts');

  useEffect(() => {
    loadTimelines();
  }, []);

  const loadTimelines = async () => {
    setLoading(true);
    setError(null);

    try {
      const [drafts, committed] = await Promise.all([
        timelineService.getUserDrafts(),
        timelineService.getUserCommitted(),
      ]);

      setDraftTimelines(drafts);
      setCommittedTimelines(committed);
    } catch (err: any) {
      setError(err.message || 'Failed to load timelines');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-4"></div>
          <p className="text-gray-600">Loading timelines...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">My Timelines</h1>
        <p className="mt-2 text-gray-600">Manage your PhD timelines</p>
      </div>

      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {/* Tabs */}
      <div className="mb-6 border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('drafts')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'drafts'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Draft Timelines ({draftTimelines.length})
          </button>
          <button
            onClick={() => setActiveTab('committed')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'committed'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Committed Timelines ({committedTimelines.length})
          </button>
        </nav>
      </div>

      {/* Draft Timelines */}
      {activeTab === 'drafts' && (
        <div className="space-y-4">
          {draftTimelines.length === 0 ? (
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
              <p className="text-gray-600">No draft timelines found</p>
              <button
                onClick={() => navigate('/baselines')}
                className="mt-4 px-4 py-2 text-white bg-blue-600 rounded-md hover:bg-blue-700"
              >
                Create from Baseline
              </button>
            </div>
          ) : (
            draftTimelines.map((timeline) => (
              <div
                key={timeline.id}
                className="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => navigate(`/timelines/draft/${timeline.id}`)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3">
                      <h3 className="text-lg font-semibold text-gray-900">{timeline.title}</h3>
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                        DRAFT
                      </span>
                      {timeline.isActive && (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          ACTIVE
                        </span>
                      )}
                    </div>
                    {timeline.description && (
                      <p className="mt-2 text-sm text-gray-600">{timeline.description}</p>
                    )}
                    <div className="mt-3 flex items-center space-x-4 text-sm text-gray-500">
                      <span>Version: {timeline.versionNumber || '1.0'}</span>
                      <span>•</span>
                      <span>Created: {new Date(timeline.createdAt).toLocaleDateString()}</span>
                    </div>
                  </div>
                  <div>
                    <svg className="h-5 w-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* Committed Timelines */}
      {activeTab === 'committed' && (
        <div className="space-y-4">
          {committedTimelines.length === 0 ? (
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
              <p className="text-gray-600">No committed timelines found</p>
              <p className="mt-2 text-sm text-gray-500">
                Commit a draft timeline to create an immutable version
              </p>
            </div>
          ) : (
            committedTimelines.map((timeline) => (
              <div
                key={timeline.id}
                className="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => navigate(`/timelines/committed/${timeline.id}`)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3">
                      <h3 className="text-lg font-semibold text-gray-900">{timeline.title}</h3>
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        COMMITTED
                      </span>
                    </div>
                    {timeline.description && (
                      <p className="mt-2 text-sm text-gray-600">{timeline.description}</p>
                    )}
                    <div className="mt-3 flex items-center space-x-4 text-sm text-gray-500">
                      <span>Committed: {new Date(timeline.committedDate).toLocaleDateString()}</span>
                      {timeline.targetCompletionDate && (
                        <>
                          <span>•</span>
                          <span>Target: {new Date(timeline.targetCompletionDate).toLocaleDateString()}</span>
                        </>
                      )}
                    </div>
                  </div>
                  <div>
                    <svg className="h-5 w-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}

Component.displayName = 'TimelinesPage';
