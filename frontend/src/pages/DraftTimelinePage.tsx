/**
 * Draft Timeline Page
 * 
 * View and edit a draft timeline with stages and milestones.
 * Includes ability to commit the timeline.
 */

import { useState, useEffect, FormEvent } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { timelineService } from '@/services';
import type { DraftTimeline, TimelineStage, TimelineMilestone } from '@/types/api';

interface StageWithMilestones {
  stage: TimelineStage;
  milestones: TimelineMilestone[];
}

export function Component() {
  const { draftId } = useParams<{ draftId: string }>();
  const navigate = useNavigate();

  // Data state
  const [timeline, setTimeline] = useState<DraftTimeline | null>(null);
  const [stages, setStages] = useState<StageWithMilestones[]>([]);
  const [baseline, setBaseline] = useState<any>(null);

  // UI state
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editMode, setEditMode] = useState(false);

  // Commit modal state
  const [showCommitModal, setShowCommitModal] = useState(false);
  const [commitTitle, setCommitTitle] = useState('');
  const [commitDescription, setCommitDescription] = useState('');
  const [committing, setCommitting] = useState(false);

  // Load timeline data
  useEffect(() => {
    loadTimeline();
  }, [draftId]);

  const loadTimeline = async () => {
    if (!draftId) return;

    setLoading(true);
    setError(null);

    try {
      const data = await timelineService.getDraftWithDetails(draftId);
      setTimeline(data.timeline);
      setStages(data.stages);
      setBaseline(data.baseline);
      setCommitTitle(data.timeline.title);
      setCommitDescription(data.timeline.description || '');
    } catch (err: any) {
      setError(err.message || 'Failed to load timeline');
    } finally {
      setLoading(false);
    }
  };

  const handleCommit = async (e: FormEvent) => {
    e.preventDefault();
    if (!draftId) return;

    setCommitting(true);
    setError(null);

    try {
      const { committedTimelineId } = await timelineService.commit({
        draftTimelineId: draftId,
        title: commitTitle,
        description: commitDescription || undefined,
      });

      // Navigate to committed timeline
      navigate(`/timelines/committed/${committedTimelineId}`);
    } catch (err: any) {
      setError(err.message || 'Failed to commit timeline');
      setCommitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-4"></div>
          <p className="text-gray-600">Loading timeline...</p>
        </div>
      </div>
    );
  }

  if (error && !timeline) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-red-900 mb-2">Error</h3>
        <p className="text-red-800">{error}</p>
        <button
          onClick={() => navigate('/timelines')}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
        >
          Back to Timelines
        </button>
      </div>
    );
  }

  if (!timeline) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Timeline not found</p>
      </div>
    );
  }

  const totalMilestones = stages.reduce((sum, s) => sum + s.milestones.length, 0);

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{timeline.title}</h1>
            <p className="mt-2 text-gray-600">{timeline.description || 'No description'}</p>
            <div className="mt-2 flex items-center space-x-4 text-sm text-gray-500">
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                DRAFT
              </span>
              <span>Version: {timeline.versionNumber || '1.0'}</span>
              <span>•</span>
              <span>{stages.length} stages</span>
              <span>•</span>
              <span>{totalMilestones} milestones</span>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setEditMode(!editMode)}
              className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {editMode ? 'View Mode' : 'Edit Mode'}
            </button>
            <button
              onClick={() => setShowCommitModal(true)}
              className="px-6 py-2 text-white bg-green-600 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500"
            >
              Commit Timeline
            </button>
          </div>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {/* Baseline Info */}
      {baseline && (
        <div className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-blue-900 mb-2">Baseline Information</h3>
          <div className="grid grid-cols-3 gap-4 text-sm text-blue-800">
            <div>
              <span className="font-medium">Program:</span> {baseline.programName}
            </div>
            <div>
              <span className="font-medium">Institution:</span> {baseline.institution}
            </div>
            <div>
              <span className="font-medium">Field:</span> {baseline.fieldOfStudy}
            </div>
          </div>
        </div>
      )}

      {/* Edit Mode Notice */}
      {editMode && (
        <div className="mb-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-sm text-yellow-800">
            <strong>Edit Mode:</strong> Changes are shown here but not saved. Full editing functionality would include API endpoints for updates.
          </p>
        </div>
      )}

      {/* Stages and Milestones */}
      <div className="space-y-6">
        {stages.length === 0 ? (
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
            <p className="text-gray-600">No stages found in this timeline</p>
          </div>
        ) : (
          stages.map(({ stage, milestones }) => (
            <div key={stage.id} className="bg-white rounded-lg shadow">
              {/* Stage Header */}
              <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3">
                      <span className="flex items-center justify-center w-8 h-8 rounded-full bg-blue-600 text-white text-sm font-semibold">
                        {stage.stageOrder}
                      </span>
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">
                          {stage.title}
                        </h3>
                        {stage.description && (
                          <p className="mt-1 text-sm text-gray-600">{stage.description}</p>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4 text-sm text-gray-600">
                    {stage.durationMonths && (
                      <span className="px-3 py-1 bg-white rounded-full border border-gray-300">
                        {stage.durationMonths} months
                      </span>
                    )}
                    <span className={`px-3 py-1 rounded-full ${
                      stage.status === 'COMPLETED' ? 'bg-green-100 text-green-800' :
                      stage.status === 'IN_PROGRESS' ? 'bg-blue-100 text-blue-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {stage.status || 'PENDING'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Milestones */}
              <div className="px-6 py-4">
                {milestones.length === 0 ? (
                  <p className="text-sm text-gray-500 italic">No milestones in this stage</p>
                ) : (
                  <div className="space-y-3">
                    {milestones.map((milestone) => (
                      <div
                        key={milestone.id}
                        className="flex items-start space-x-3 p-3 rounded-lg border border-gray-200 hover:border-gray-300 transition-colors"
                      >
                        <div className="flex-shrink-0 mt-1">
                          <div className={`w-5 h-5 rounded border-2 flex items-center justify-center ${
                            milestone.isCompleted 
                              ? 'bg-green-500 border-green-500'
                              : milestone.isCritical
                              ? 'border-red-500'
                              : 'border-gray-300'
                          }`}>
                            {milestone.isCompleted && (
                              <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                              </svg>
                            )}
                          </div>
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <h4 className="text-sm font-medium text-gray-900 flex items-center">
                                {milestone.title}
                                {milestone.isCritical && (
                                  <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800">
                                    Critical
                                  </span>
                                )}
                              </h4>
                              {milestone.description && (
                                <p className="mt-1 text-sm text-gray-600">{milestone.description}</p>
                              )}
                            </div>
                            {milestone.targetDate && (
                              <div className="ml-4 flex-shrink-0 text-sm text-gray-500">
                                Target: {new Date(milestone.targetDate).toLocaleDateString()}
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Commit Modal */}
      {showCommitModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-lg w-full">
            <form onSubmit={handleCommit}>
              <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-xl font-semibold text-gray-900">Commit Timeline</h2>
                <p className="mt-1 text-sm text-gray-600">
                  Committing will create an immutable version of this timeline.
                </p>
              </div>

              <div className="px-6 py-4 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Timeline Title *
                  </label>
                  <input
                    type="text"
                    value={commitTitle}
                    onChange={(e) => setCommitTitle(e.target.value)}
                    placeholder="e.g., PhD Timeline v1.0"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                    required
                    disabled={committing}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description
                  </label>
                  <textarea
                    value={commitDescription}
                    onChange={(e) => setCommitDescription(e.target.value)}
                    placeholder="Optional description of this version..."
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                    disabled={committing}
                  />
                </div>

                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                  <div className="flex">
                    <div className="flex-shrink-0">
                      <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div className="ml-3">
                      <p className="text-sm text-yellow-800">
                        <strong>Warning:</strong> Once committed, this timeline cannot be modified. 
                        You can create new versions, but this version will be locked.
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => setShowCommitModal(false)}
                  className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
                  disabled={committing}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-6 py-2 text-white bg-green-600 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50"
                  disabled={committing}
                >
                  {committing ? 'Committing...' : 'Commit Timeline'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

Component.displayName = 'DraftTimelinePage';
