/**
 * Draft Timeline Page
 * 
 * View and edit a draft timeline with stages and milestones.
 * 
 * Behavior:
 * - Trigger POST /timeline/generate (if no draft exists)
 * - Render stages and milestones dynamically
 * - Allow local text edits only (no API calls for edits)
 * - Clearly mark status as DRAFT
 * - No auto-commit
 * 
 * Local edits are stored in component state only - not persisted to backend.
 */

import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { timelineService, baselineService } from '@/services';
import { useGlobalStateActions, useGlobalStateStore } from '@/state/global';
import { getRouteFromState } from '@/state/navigation';
import { CommitTimelineModal } from '@/components/CommitTimelineModal';
import { checkTimelineGenerationRequiresBaseline, checkCommitRequiresDraft } from '@/guards/invariants';
import type { TimelineGenerationResponse } from '@/types/timeline';
import type { Baseline } from '@/types/api';

/**
 * Local editable stage (for text edits only)
 */
interface EditableStage {
  id: string;
  title: string;
  description: string | null;
  stage_order: number;
  duration_months: number | null;
  status: string;
  milestones: Array<{
    id: string;
    title: string;
    description: string | null;
    milestone_order: number;
    is_critical: boolean;
    is_completed: boolean;
    deliverable_type: string | null;
    target_date: string | null;
  }>;
}

export function Component() {
  const { draftId } = useParams<{ draftId: string }>();
  const navigate = useNavigate();
  const { setTimelineStatus, setAnalyticsStatus } = useGlobalStateActions();
  const state = useGlobalStateStore();

  // Data state
  const [timeline, setTimeline] = useState<TimelineGenerationResponse['timeline'] | null>(null);
  const [stages, setStages] = useState<EditableStage[]>([]);
  const [baseline, setBaseline] = useState<Baseline | null>(null);
  const [metadata, setMetadata] = useState<TimelineGenerationResponse['metadata'] | null>(null);

  // UI state
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [editMode, setEditMode] = useState(false);
  const [editingStageId, setEditingStageId] = useState<string | null>(null);
  const [editingMilestoneId, setEditingMilestoneId] = useState<string | null>(null);

  // Load timeline data
  useEffect(() => {
    if (draftId) {
      loadTimeline();
    } else {
      // No draft ID - check if we need to generate
      checkAndGenerate();
    }
  }, [draftId]);

  /**
   * Check if baseline exists and generate timeline if needed
   * 
   * Invariant: No timeline generation without baseline
   */
  const checkAndGenerate = async () => {
    try {
      // Invariant check: No timeline generation without baseline
      // Guard relies only on backend state
      checkTimelineGenerationRequiresBaseline(state);
    } catch (error: any) {
      if (error.name === 'InvariantViolationError') {
        setError(error.message);
      } else {
        setError('Cannot generate timeline: Baseline is required.');
      }
      setLoading(false);
      return;
    }

    // Get baseline to generate timeline
    try {
      const baselines = await baselineService.getUserBaselines();
      if (baselines.length === 0) {
        setError('No baseline found. Please create a baseline first.');
        setLoading(false);
        return;
      }

      // Generate timeline from first baseline
      await generateTimeline(baselines[0].id);
    } catch (err: any) {
      setError(err.message || 'Failed to generate timeline');
      setLoading(false);
    }
  };

  /**
   * Generate timeline from baseline
   * 
   * Invariant: No timeline generation without baseline
   */
  const generateTimeline = async (baselineId: string) => {
    // Invariant check: No timeline generation without baseline
    // Guard relies only on backend state
    try {
      checkTimelineGenerationRequiresBaseline(state);
    } catch (error: any) {
      if (error.name === 'InvariantViolationError') {
        setError(error.message);
      } else {
        setError('Cannot generate timeline: Baseline is required.');
      }
      return;
    }

    setGenerating(true);
    setError(null);

    try {
      // Trigger POST /timeline/generate
      const response = await timelineService.generate({
        baselineId,
        title: 'PhD Timeline',
        description: 'Generated timeline from baseline',
        versionNumber: '1.0',
      });

      // Set timeline data from API response
      setTimeline(response.timeline);
      setStages(response.stages.map(stage => ({
        ...stage,
        // Make editable copies
        title: stage.title,
        description: stage.description,
      })));
      setMetadata(response.metadata);

      // Load baseline info
      const baselineData = await baselineService.getById(baselineId);
      setBaseline(baselineData);

      // Update global state - timeline is now DRAFT
      setTimelineStatus('DRAFT');

      // Navigate to draft timeline page
      navigate(`/timelines/draft/${response.timeline.id}`, { replace: true });
    } catch (err: any) {
      setError(err.message || 'Failed to generate timeline');
    } finally {
      setGenerating(false);
      setLoading(false);
    }
  };

  /**
   * Load existing draft timeline
   */
  const loadTimeline = async () => {
    if (!draftId) return;

    setLoading(true);
    setError(null);

    try {
      const data = await timelineService.getDraftWithDetails(draftId);
      
      // Transform to match generation response format
      setTimeline({
        id: data.timeline.id,
        baseline_id: data.timeline.baseline_id,
        user_id: data.timeline.user_id,
        title: data.timeline.title,
        description: data.timeline.description,
        version_number: data.timeline.version_number,
        is_active: data.timeline.is_active,
        status: 'DRAFT',
        created_at: data.timeline.created_at,
      });

      // Transform stages to editable format
      setStages(data.stages.map(({ stage, milestones }) => ({
        id: stage.id,
        title: stage.title,
        description: stage.description || null,
        stage_order: stage.stageOrder,
        duration_months: stage.durationMonths || null,
        status: stage.status,
        milestones: milestones.map(m => ({
          id: m.id,
          title: m.title,
          description: m.description || null,
          milestone_order: m.milestoneOrder,
          is_critical: m.isCritical,
          is_completed: m.isCompleted,
          deliverable_type: m.deliverableType || null,
          target_date: m.targetDate || null,
        })),
      })));

      // Load baseline if available
      if (data.baseline) {
        setBaseline(data.baseline);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load timeline');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle local text edits (no API calls)
   */
  const handleStageTitleEdit = (stageId: string, newTitle: string) => {
    setStages(prev => prev.map(stage =>
      stage.id === stageId ? { ...stage, title: newTitle } : stage
    ));
  };

  const handleStageDescriptionEdit = (stageId: string, newDescription: string) => {
    setStages(prev => prev.map(stage =>
      stage.id === stageId ? { ...stage, description: newDescription } : stage
    ));
  };

  const handleMilestoneTitleEdit = (stageId: string, milestoneId: string, newTitle: string) => {
    setStages(prev => prev.map(stage =>
      stage.id === stageId
        ? {
            ...stage,
            milestones: stage.milestones.map(m =>
              m.id === milestoneId ? { ...m, title: newTitle } : m
            ),
          }
        : stage
    ));
  };

  const handleMilestoneDescriptionEdit = (
    stageId: string,
    milestoneId: string,
    newDescription: string
  ) => {
    setStages(prev => prev.map(stage =>
      stage.id === stageId
        ? {
            ...stage,
            milestones: stage.milestones.map(m =>
              m.id === milestoneId ? { ...m, description: newDescription } : m
            ),
          }
        : stage
    ));
  };

  // Commit modal state
  const [showCommitModal, setShowCommitModal] = useState(false);
  const [committing, setCommitting] = useState(false);

  /**
   * Handle commit confirmation
   * 
   * Calls POST /timeline/commit and navigates to committed timeline.
   * Frontend does not validate business rules - passes data through to backend.
   * 
   * Invariant: No commit without draft
   */
  const handleCommit = async (data: { title?: string; description?: string }) => {
    if (!draftId) return;

    // Invariant check: No commit without draft
    // Guard relies only on backend state
    try {
      checkCommitRequiresDraft(state);
    } catch (error: any) {
      if (error.name === 'InvariantViolationError') {
        setError(error.message);
      } else {
        setError('Cannot commit timeline: Draft timeline is required.');
      }
      return;
    }

    setCommitting(true);
    setError(null);

    try {
      // Call POST /timeline/commit
      // Frontend passes data through without validation
      const result = await timelineService.commit({
        draftTimelineId: draftId,
        title: data.title,
        description: data.description,
      });

      // Update global state - timeline is now COMMITTED
      // Analytics become available when timeline is committed
      setTimelineStatus('COMMITTED');
      setAnalyticsStatus('AVAILABLE');

      // Navigate to committed timeline (read-only view)
      navigate(`/timelines/committed/${result.committedTimelineId}`, { replace: true });
    } catch (err: any) {
      setError(err.message || 'Failed to commit timeline');
      setCommitting(false);
      // Don't close modal on error - let user retry or cancel
    }
  };

  if (loading || generating) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-4"></div>
          <p className="text-gray-600">
            {generating ? 'Generating timeline...' : 'Loading timeline...'}
          </p>
          {generating && (
            <p className="mt-2 text-sm text-gray-500">
              This may take a few moments
            </p>
          )}
        </div>
      </div>
    );
  }

  if (error && !timeline) {
    return (
      <div className="max-w-3xl mx-auto">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-red-900 mb-2">Error</h3>
          <p className="text-red-800 mb-4">{error}</p>
          <div className="flex space-x-3">
            <button
              onClick={() => {
                const route = getRouteFromState(state);
                navigate(route);
              }}
              className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
            >
              Go Back
            </button>
            {state.baselineStatus === 'EXISTS' && (
              <button
                onClick={async () => {
                  try {
                    const baselines = await baselineService.getUserBaselines();
                    if (baselines.length > 0) {
                      await generateTimeline(baselines[0].id);
                    }
                  } catch (err) {
                    setError('Failed to retry generation');
                  }
                }}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Retry Generation
              </button>
            )}
          </div>
        </div>
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
      {/* Header with DRAFT status */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center space-x-3 mb-2">
              <h1 className="text-3xl font-bold text-gray-900">{timeline.title}</h1>
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold bg-yellow-100 text-yellow-800 border-2 border-yellow-300">
                DRAFT
              </span>
            </div>
            <p className="mt-2 text-gray-600">{timeline.description || 'No description'}</p>
            <div className="mt-3 flex items-center space-x-4 text-sm text-gray-500">
              <span>Version: {timeline.version_number || '1.0'}</span>
              <span>•</span>
              <span>{stages.length} stages</span>
              <span>•</span>
              <span>{totalMilestones} milestones</span>
              {metadata && (
                <>
                  <span>•</span>
                  <span>
                    Duration: {metadata.total_duration_months_min}-{metadata.total_duration_months_max} months
                  </span>
                </>
              )}
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setEditMode(!editMode)}
              className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {editMode ? 'View Mode' : 'Edit Mode'}
            </button>
            {draftId && (
              <button
                onClick={() => {
                  // Invariant check: No commit without draft
                  // Guard relies only on backend state
                  try {
                    checkCommitRequiresDraft(state);
                    setShowCommitModal(true);
                  } catch (error: any) {
                    if (error.name === 'InvariantViolationError') {
                      setError(error.message);
                    } else {
                      setError('Cannot commit timeline: Draft timeline is required.');
                    }
                  }
                }}
                className="px-6 py-2 text-white bg-green-600 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                Commit Timeline
              </button>
            )}
          </div>
        </div>
      </div>

      {/* DRAFT Status Banner */}
      <div className="mb-6 bg-yellow-50 border-2 border-yellow-300 rounded-lg p-4">
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-yellow-600" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-semibold text-yellow-800">Draft Timeline</h3>
            <p className="mt-1 text-sm text-yellow-700">
              This timeline is in <strong>DRAFT</strong> status. You can edit text locally, but changes are not saved until you commit the timeline.
            </p>
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
              <span className="font-medium">Program:</span> {baseline.program_name}
            </div>
            <div>
              <span className="font-medium">Institution:</span> {baseline.institution}
            </div>
            <div>
              <span className="font-medium">Field:</span> {baseline.field_of_study}
            </div>
          </div>
        </div>
      )}

      {/* Edit Mode Notice */}
      {editMode && (
        <div className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-sm text-blue-800">
            <strong>Edit Mode:</strong> Changes are local only and not saved to the backend. 
            Use the commit button to create an immutable version of this timeline.
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
          stages.map((stage) => (
            <div key={stage.id} className="bg-white rounded-lg shadow">
              {/* Stage Header */}
              <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3">
                      <span className="flex items-center justify-center w-8 h-8 rounded-full bg-blue-600 text-white text-sm font-semibold">
                        {stage.stage_order}
                      </span>
                      <div className="flex-1">
                        {editMode && editingStageId === stage.id ? (
                          <input
                            type="text"
                            value={stage.title}
                            onChange={(e) => handleStageTitleEdit(stage.id, e.target.value)}
                            onBlur={() => setEditingStageId(null)}
                            className="text-lg font-semibold text-gray-900 bg-white border border-blue-300 rounded px-2 py-1 w-full"
                            autoFocus
                          />
                        ) : (
                          <h3
                            className="text-lg font-semibold text-gray-900 cursor-pointer hover:text-blue-600"
                            onClick={() => editMode && setEditingStageId(stage.id)}
                          >
                            {stage.title}
                          </h3>
                        )}
                        {editMode && editingStageId === stage.id ? (
                          <textarea
                            value={stage.description || ''}
                            onChange={(e) => handleStageDescriptionEdit(stage.id, e.target.value)}
                            onBlur={() => setEditingStageId(null)}
                            className="mt-1 text-sm text-gray-600 bg-white border border-blue-300 rounded px-2 py-1 w-full"
                            rows={2}
                          />
                        ) : (
                          stage.description && (
                            <p
                              className="mt-1 text-sm text-gray-600 cursor-pointer hover:text-blue-600"
                              onClick={() => editMode && setEditingStageId(stage.id)}
                            >
                              {stage.description}
                            </p>
                          )
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4 text-sm text-gray-600">
                    {stage.duration_months && (
                      <span className="px-3 py-1 bg-white rounded-full border border-gray-300">
                        {stage.duration_months} months
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
                {stage.milestones.length === 0 ? (
                  <p className="text-sm text-gray-500 italic">No milestones in this stage</p>
                ) : (
                  <div className="space-y-3">
                    {stage.milestones.map((milestone) => (
                      <div
                        key={milestone.id}
                        className="flex items-start space-x-3 p-3 rounded-lg border border-gray-200 hover:border-gray-300 transition-colors"
                      >
                        <div className="flex-shrink-0 mt-1">
                          <div className={`w-5 h-5 rounded border-2 flex items-center justify-center ${
                            milestone.is_completed
                              ? 'bg-green-500 border-green-500'
                              : milestone.is_critical
                              ? 'border-red-500'
                              : 'border-gray-300'
                          }`}>
                            {milestone.is_completed && (
                              <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                              </svg>
                            )}
                          </div>
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              {editMode && editingMilestoneId === milestone.id ? (
                                <div className="space-y-2">
                                  <input
                                    type="text"
                                    value={milestone.title}
                                    onChange={(e) => handleMilestoneTitleEdit(stage.id, milestone.id, e.target.value)}
                                    onBlur={() => setEditingMilestoneId(null)}
                                    className="text-sm font-medium text-gray-900 bg-white border border-blue-300 rounded px-2 py-1 w-full"
                                    autoFocus
                                  />
                                  <textarea
                                    value={milestone.description || ''}
                                    onChange={(e) => handleMilestoneDescriptionEdit(stage.id, milestone.id, e.target.value)}
                                    onBlur={() => setEditingMilestoneId(null)}
                                    className="text-sm text-gray-600 bg-white border border-blue-300 rounded px-2 py-1 w-full"
                                    rows={2}
                                  />
                                </div>
                              ) : (
                                <>
                                  <h4
                                    className="text-sm font-medium text-gray-900 flex items-center cursor-pointer hover:text-blue-600"
                                    onClick={() => editMode && setEditingMilestoneId(milestone.id)}
                                  >
                                    {milestone.title}
                                    {milestone.is_critical && (
                                      <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800">
                                        Critical
                                      </span>
                                    )}
                                  </h4>
                                  {milestone.description && (
                                    <p
                                      className="mt-1 text-sm text-gray-600 cursor-pointer hover:text-blue-600"
                                      onClick={() => editMode && setEditingMilestoneId(milestone.id)}
                                    >
                                      {milestone.description}
                                    </p>
                                  )}
                                </>
                              )}
                            </div>
                            {milestone.target_date && (
                              <div className="ml-4 flex-shrink-0 text-sm text-gray-500">
                                Target: {new Date(milestone.target_date).toLocaleDateString()}
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

      {/* Commit Confirmation Modal */}
      <CommitTimelineModal
        isOpen={showCommitModal}
        onClose={() => {
          setShowCommitModal(false);
          setError(null);
        }}
        onConfirm={handleCommit}
        currentTitle={timeline.title}
        currentDescription={timeline.description}
        isLoading={committing}
      />
    </div>
  );
}

Component.displayName = 'DraftTimelinePage';
