/**
 * Timeline Progress Tracking Page
 * 
 * Interactive progress tracking for committed timelines.
 * 
 * Behavior:
 * - Render committed milestones
 * - Allow marking completion
 * - Call POST /progress/complete
 * - Render delay indicators from backend only (no frontend delay calculation)
 */

import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { timelineService, progressService } from '@/services';
import { useGlobalStateStore } from '@/state/global';
import { checkProgressRequiresCommittedTimeline } from '@/guards/invariants';
import type { CommittedTimeline, TimelineStage, TimelineMilestone } from '@/types/api';

interface StageWithMilestones {
  stage: TimelineStage;
  milestones: TimelineMilestone[];
}

interface MilestoneDelay {
  milestoneId: string;
  milestoneTitle: string;
  isCompleted: boolean;
  isCritical: boolean;
  targetDate?: string;
  actualCompletionDate?: string;
  comparisonDate: string;
  delayDays: number;
  status: string;
  hasTargetDate: boolean;
}

export function Component() {
  const { timelineId } = useParams<{ timelineId: string }>();
  const navigate = useNavigate();
  const state = useGlobalStateStore();

  // Data state
  const [timeline, setTimeline] = useState<CommittedTimeline | null>(null);
  const [stages, setStages] = useState<StageWithMilestones[]>([]);
  const [milestoneDelayMap, setMilestoneDelayMap] = useState<Map<string, MilestoneDelay>>(new Map());

  // UI state
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedStages, setExpandedStages] = useState<Set<string>>(new Set());
  const [completingMilestones, setCompletingMilestones] = useState<Set<string>>(new Set());

  useEffect(() => {
    loadTimeline();
  }, [timelineId]);

  /**
   * Load timeline and delay information
   * 
   * Invariant: No progress without committed timeline
   */
  const loadTimeline = async () => {
    if (!timelineId) return;

    // Invariant check: No progress without committed timeline
    // Guard relies only on backend state
    try {
      checkProgressRequiresCommittedTimeline(state);
    } catch (error: any) {
      if (error.name === 'InvariantViolationError') {
        setError(error.message);
      } else {
        setError('Cannot track progress: Committed timeline is required.');
      }
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Load committed timeline with stages and milestones
      const timelineData = await timelineService.getCommittedWithDetails(timelineId);
      setTimeline(timelineData.timeline);
      setStages(timelineData.stages);

      // Expand all stages by default
      const allStageIds = new Set(timelineData.stages.map(s => s.stage.id));
      setExpandedStages(allStageIds);

      // Load delay information for each milestone from backend
      // Frontend does NOT calculate delays - backend provides all delay indicators
      const allMilestones = timelineData.stages.flatMap(({ milestones }) => milestones);
      const milestoneDelayPromises = allMilestones.map(milestone =>
        progressService.getMilestoneDelay(milestone.id)
      );
      const milestoneDelayResults = await Promise.all(milestoneDelayPromises);
      const delayMap = new Map(
        milestoneDelayResults.map(md => [md.milestoneId, md])
      );
      setMilestoneDelayMap(delayMap);
    } catch (err: any) {
      setError(err.message || 'Failed to load timeline');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Mark milestone as completed
   * 
   * Calls POST /progress/complete via progressService
   */
  const handleCompleteMilestone = async (milestoneId: string) => {
    if (completingMilestones.has(milestoneId)) return;

    setCompletingMilestones(prev => new Set(prev).add(milestoneId));
    setError(null);

    try {
      // Call POST /progress/complete
      // Frontend passes data through - no delay calculation
      await progressService.completeMilestone(milestoneId);

      // Reload timeline to get updated completion status and delay indicators from backend
      await loadTimeline();
    } catch (err: any) {
      setError(err.message || 'Failed to mark milestone as completed');
    } finally {
      setCompletingMilestones(prev => {
        const next = new Set(prev);
        next.delete(milestoneId);
        return next;
      });
    }
  };

  const toggleStage = (stageId: string) => {
    const newExpanded = new Set(expandedStages);
    if (newExpanded.has(stageId)) {
      newExpanded.delete(stageId);
    } else {
      newExpanded.add(stageId);
    }
    setExpandedStages(newExpanded);
  };

  /**
   * Get delay badge from backend delay data
   * 
   * Frontend does NOT calculate delays - only renders what backend provides.
   */
  const getDelayBadge = (delay: MilestoneDelay | undefined) => {
    if (!delay) return null;

    // Render delay indicators from backend only
    if (delay.isCompleted) {
      if (delay.status === 'completed_delayed') {
        return (
          <span className="px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
            Completed {delay.delayDays > 0 ? `${delay.delayDays} days late` : 'on time'}
          </span>
        );
      }
      return (
        <span className="px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
          Completed
        </span>
      );
    }

    // Backend provides status: 'overdue', 'due_today', 'on_track', 'no_target_date'
    if (delay.status === 'overdue') {
      return (
        <span className="px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
          {delay.delayDays} days overdue
        </span>
      );
    }

    if (delay.status === 'due_today') {
      return (
        <span className="px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
          Due today
        </span>
      );
    }

    if (delay.status === 'on_track') {
      // Backend may provide negative delayDays for early milestones
      if (delay.delayDays < 0) {
        return (
          <span className="px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
            {Math.abs(delay.delayDays)} days ahead
          </span>
        );
      }
      return (
        <span className="px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
          On track
        </span>
      );
    }

    if (delay.status === 'no_target_date') {
      return (
        <span className="px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
          No target date
        </span>
      );
    }

    return null;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-4"></div>
          <p className="text-gray-600">Loading timeline progress...</p>
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
          <button
            onClick={() => navigate('/timelines')}
            className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
          >
            Back to Timelines
          </button>
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
  const completedMilestones = stages.reduce(
    (sum, s) => sum + s.milestones.filter(m => m.isCompleted).length,
    0
  );

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Progress Tracking</h1>
            <p className="mt-2 text-gray-600">{timeline.title}</p>
            <div className="mt-3 flex items-center space-x-4 text-sm text-gray-500">
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                COMMITTED
              </span>
              <span>{completedMilestones} of {totalMilestones} milestones completed</span>
            </div>
          </div>
          <button
            onClick={() => navigate(`/timelines/committed/${timelineId}`)}
            className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            View Timeline
          </button>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {/* Progress Notice */}
      <div className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <p className="text-sm text-blue-800">
              <strong>Progress Tracking:</strong> Mark milestones as completed to track your progress. 
              Delay indicators are calculated by the backend based on target dates.
            </p>
          </div>
        </div>
      </div>

      {/* Stages and Milestones */}
      <div className="space-y-4">
        {stages.length === 0 ? (
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
            <p className="text-gray-600">No stages found in this timeline</p>
          </div>
        ) : (
          stages.map(({ stage, milestones }) => {
            const isExpanded = expandedStages.has(stage.id);
            const stageCompleted = milestones.filter(m => m.isCompleted).length;
            const stageTotal = milestones.length;

            return (
              <div key={stage.id} className="bg-white rounded-lg shadow">
                {/* Stage Header */}
                <div
                  className="px-6 py-4 border-b border-gray-200 cursor-pointer hover:bg-gray-50 transition-colors"
                  onClick={() => toggleStage(stage.id)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4 flex-1">
                      <span className="flex items-center justify-center w-10 h-10 rounded-full bg-blue-600 text-white text-sm font-semibold">
                        {stage.stageOrder}
                      </span>
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-900">{stage.title}</h3>
                        {stage.description && (
                          <p className="mt-1 text-sm text-gray-600">{stage.description}</p>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-6">
                      {/* Stage Progress */}
                      <div className="text-right">
                        <div className="text-sm font-semibold text-gray-900">
                          {stageCompleted} / {stageTotal} completed
                        </div>
                        <div className="text-xs text-gray-600">
                          {stageTotal > 0 ? Math.round((stageCompleted / stageTotal) * 100) : 0}% complete
                        </div>
                      </div>
                      
                      {/* Expand/Collapse Icon */}
                      <svg
                        className={`w-5 h-5 text-gray-400 transition-transform ${
                          isExpanded ? 'transform rotate-180' : ''
                        }`}
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                      </svg>
                    </div>
                  </div>
                </div>

                {/* Milestones */}
                {isExpanded && (
                  <div className="px-6 py-4">
                    {milestones.length === 0 ? (
                      <p className="text-sm text-gray-500 italic">No milestones in this stage</p>
                    ) : (
                      <div className="space-y-3">
                        {milestones.map((milestone) => {
                          const delay = milestoneDelayMap.get(milestone.id);
                          const isCompleting = completingMilestones.has(milestone.id);
                          
                          return (
                            <div
                              key={milestone.id}
                              className={`flex items-start space-x-3 p-4 rounded-lg border-2 transition-colors ${
                                delay?.status === 'overdue' && milestone.isCritical
                                  ? 'border-red-300 bg-red-50'
                                  : delay?.status === 'overdue'
                                  ? 'border-red-200 bg-red-50'
                                  : delay?.status === 'due_today'
                                  ? 'border-yellow-200 bg-yellow-50'
                                  : milestone.isCompleted
                                  ? 'border-green-200 bg-green-50'
                                  : 'border-gray-200 bg-white'
                              }`}
                            >
                              {/* Completion Checkbox - Interactive */}
                              <div className="flex-shrink-0 mt-1">
                                <button
                                  onClick={() => !milestone.isCompleted && !isCompleting && handleCompleteMilestone(milestone.id)}
                                  disabled={milestone.isCompleted || isCompleting}
                                  className={`w-6 h-6 rounded border-2 flex items-center justify-center transition-colors ${
                                    milestone.isCompleted
                                      ? 'bg-green-500 border-green-500 cursor-default'
                                      : milestone.isCritical
                                      ? 'border-red-500 hover:bg-red-50 cursor-pointer'
                                      : 'border-gray-300 hover:bg-gray-50 cursor-pointer'
                                  } ${isCompleting ? 'opacity-50 cursor-not-allowed' : ''}`}
                                  title={milestone.isCompleted ? 'Completed' : 'Mark as completed'}
                                >
                                  {milestone.isCompleted && (
                                    <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                    </svg>
                                  )}
                                  {isCompleting && (
                                    <div className="w-3 h-3 border-2 border-gray-400 border-t-transparent rounded-full animate-spin"></div>
                                  )}
                                </button>
                              </div>

                              {/* Milestone Content */}
                              <div className="flex-1 min-w-0">
                                <div className="flex items-start justify-between">
                                  <div className="flex-1">
                                    <div className="flex items-center space-x-2">
                                      <h4 className="text-sm font-medium text-gray-900">
                                        {milestone.title}
                                      </h4>
                                      {milestone.isCritical && (
                                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800">
                                          Critical
                                        </span>
                                      )}
                                    </div>
                                    {milestone.description && (
                                      <p className="mt-1 text-sm text-gray-600">{milestone.description}</p>
                                    )}
                                    
                                    {/* Dates */}
                                    <div className="mt-2 flex items-center space-x-4 text-xs text-gray-500">
                                      {milestone.targetDate && (
                                        <span>Target: {new Date(milestone.targetDate).toLocaleDateString()}</span>
                                      )}
                                      {milestone.actualCompletionDate && (
                                        <span className="text-green-600 font-medium">
                                          Completed: {new Date(milestone.actualCompletionDate).toLocaleDateString()}
                                        </span>
                                      )}
                                    </div>
                                  </div>

                                  {/* Delay Badge - From Backend Only */}
                                  <div className="ml-4 flex-shrink-0">
                                    {getDelayBadge(delay)}
                                  </div>
                                </div>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}

Component.displayName = 'TimelineProgressPage';
