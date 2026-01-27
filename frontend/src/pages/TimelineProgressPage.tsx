/**
 * Timeline Progress Dashboard
 * 
 * Comprehensive dashboard showing timeline progress with stages, milestones,
 * completion status, and delay indicators. Read-only view for committed timelines.
 */

import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { timelineService, progressService } from '@/services';
import type { CommittedTimeline, TimelineStage, TimelineMilestone } from '@/types/api';

interface StageWithMilestones {
  stage: TimelineStage;
  milestones: TimelineMilestone[];
}

interface StageProgress {
  stageId: string;
  stageTitle: string;
  stageOrder: number;
  totalMilestones: number;
  completedMilestones: number;
  pendingMilestones: number;
  completionPercentage: number;
  overdueMilestones: number;
  averageDelayDays: number;
  hasMilestones: boolean;
}

interface TimelineProgress {
  timelineId: string;
  timelineTitle: string;
  committedDate: string;
  targetCompletionDate?: string;
  durationProgressPercentage?: number;
  totalStages: number;
  completedStages: number;
  totalMilestones: number;
  completedMilestones: number;
  pendingMilestones: number;
  completionPercentage: number;
  criticalMilestones: number;
  completedCriticalMilestones: number;
  overdueMilestones: number;
  overdueCriticalMilestones: number;
  averageDelayDays: number;
  maxDelayDays: number;
  hasData: boolean;
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

  // Data state
  const [timeline, setTimeline] = useState<CommittedTimeline | null>(null);
  const [stages, setStages] = useState<StageWithMilestones[]>([]);
  const [timelineProgress, setTimelineProgress] = useState<TimelineProgress | null>(null);
  const [stageProgressMap, setStageProgressMap] = useState<Map<string, StageProgress>>(new Map());
  const [milestoneDelayMap, setMilestoneDelayMap] = useState<Map<string, MilestoneDelay>>(new Map());

  // UI state
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedStages, setExpandedStages] = useState<Set<string>>(new Set());

  useEffect(() => {
    loadDashboard();
  }, [timelineId]);

  const loadDashboard = async () => {
    if (!timelineId) return;

    setLoading(true);
    setError(null);

    try {
      // Load timeline details
      const timelineData = await timelineService.getCommittedWithDetails(timelineId);
      setTimeline(timelineData.timeline);
      setStages(timelineData.stages);

      // Expand all stages by default
      const allStageIds = new Set(timelineData.stages.map(s => s.stage.id));
      setExpandedStages(allStageIds);

      // Load overall timeline progress
      const progress = await progressService.getTimelineProgress(timelineId);
      setTimelineProgress(progress);

      // Load stage progress for each stage
      const stageProgressPromises = timelineData.stages.map(({ stage }) =>
        progressService.getStageProgress(stage.id)
      );
      const stageProgressResults = await Promise.all(stageProgressPromises);
      const stageProgressMap = new Map(
        stageProgressResults.map(sp => [sp.stageId, sp])
      );
      setStageProgressMap(stageProgressMap);

      // Load delay information for each milestone
      const allMilestones = timelineData.stages.flatMap(({ milestones }) => milestones);
      const milestoneDelayPromises = allMilestones.map(milestone =>
        progressService.getMilestoneDelay(milestone.id)
      );
      const milestoneDelayResults = await Promise.all(milestoneDelayPromises);
      const milestoneDelayMap = new Map(
        milestoneDelayResults.map(md => [md.milestoneId, md])
      );
      setMilestoneDelayMap(milestoneDelayMap);

    } catch (err: any) {
      setError(err.message || 'Failed to load dashboard');
    } finally {
      setLoading(false);
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

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ON_TRACK': return 'text-green-600 bg-green-50';
      case 'DELAYED': return 'text-yellow-600 bg-yellow-50';
      case 'OVERDUE': return 'text-red-600 bg-red-50';
      case 'COMPLETED': return 'text-green-600 bg-green-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getDelayBadge = (delayDays: number, status: string) => {
    if (status === 'COMPLETED') {
      return (
        <span className="px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
          Completed
        </span>
      );
    }
    if (status === 'OVERDUE') {
      return (
        <span className="px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
          {delayDays} days overdue
        </span>
      );
    }
    if (status === 'DELAYED') {
      return (
        <span className="px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
          {delayDays} days behind
        </span>
      );
    }
    if (status === 'ON_TRACK') {
      return (
        <span className="px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
          On track
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
          <p className="text-gray-600">Loading dashboard...</p>
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

  if (!timeline || !timelineProgress) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Timeline not found</p>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Timeline Progress Dashboard</h1>
            <p className="mt-2 text-gray-600">{timeline.title}</p>
          </div>
          <button
            onClick={() => navigate(`/timelines/committed/${timelineId}`)}
            className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            View Timeline
          </button>
        </div>
      </div>

      {/* Overall Progress Summary */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        {/* Overall Completion */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-600">Overall Progress</span>
            <svg className="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="text-3xl font-bold text-gray-900 mb-1">
            {Math.round(timelineProgress.completionPercentage)}%
          </div>
          <p className="text-sm text-gray-600">
            {timelineProgress.completedMilestones} of {timelineProgress.totalMilestones} milestones
          </p>
        </div>

        {/* Stages Progress */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-600">Stages</span>
            <svg className="w-5 h-5 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
              <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z" />
            </svg>
          </div>
          <div className="text-3xl font-bold text-gray-900 mb-1">
            {timelineProgress.completedStages} / {timelineProgress.totalStages}
          </div>
          <p className="text-sm text-gray-600">Stages completed</p>
        </div>

        {/* Overdue Milestones */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-600">Overdue</span>
            <svg className="w-5 h-5 text-red-600" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="text-3xl font-bold text-red-600 mb-1">
            {timelineProgress.overdueMilestones}
          </div>
          <p className="text-sm text-gray-600">
            {timelineProgress.overdueCriticalMilestones > 0 && (
              <span className="text-red-600 font-medium">
                {timelineProgress.overdueCriticalMilestones} critical
              </span>
            )}
            {timelineProgress.overdueCriticalMilestones === 0 && 'No critical overdue'}
          </p>
        </div>

        {/* Average Delay */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-600">Avg Delay</span>
            <svg className="w-5 h-5 text-yellow-600" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="text-3xl font-bold text-gray-900 mb-1">
            {Math.round(timelineProgress.averageDelayDays)} days
          </div>
          <p className="text-sm text-gray-600">
            Max: {Math.round(timelineProgress.maxDelayDays)} days
          </p>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-semibold text-gray-900">Timeline Completion</h3>
          <span className="text-2xl font-bold text-blue-600">
            {Math.round(timelineProgress.completionPercentage)}%
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-4">
          <div
            className="bg-blue-600 h-4 rounded-full transition-all duration-500"
            style={{ width: `${timelineProgress.completionPercentage}%` }}
          />
        </div>
        <div className="mt-3 flex items-center justify-between text-sm text-gray-600">
          <span>Started: {new Date(timeline.committedDate).toLocaleDateString()}</span>
          {timeline.targetCompletionDate && (
            <span>Target: {new Date(timeline.targetCompletionDate).toLocaleDateString()}</span>
          )}
        </div>
      </div>

      {/* Critical Milestones Alert */}
      {timelineProgress.overdueCriticalMilestones > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Critical Milestones Overdue</h3>
              <p className="mt-1 text-sm text-red-700">
                You have {timelineProgress.overdueCriticalMilestones} critical milestone(s) that are overdue. 
                Please review and take action immediately.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Stages and Milestones */}
      <div className="space-y-4">
        {stages.map(({ stage, milestones }) => {
          const stageProgress = stageProgressMap.get(stage.id);
          const isExpanded = expandedStages.has(stage.id);

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
                    {stageProgress && (
                      <div className="flex items-center space-x-3">
                        <div className="text-right">
                          <div className="text-sm font-semibold text-gray-900">
                            {Math.round(stageProgress.completionPercentage)}% Complete
                          </div>
                          <div className="text-xs text-gray-600">
                            {stageProgress.completedMilestones} / {stageProgress.totalMilestones} milestones
                          </div>
                        </div>
                        <div className="w-32">
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div
                              className={`h-2 rounded-full ${
                                stageProgress.completionPercentage === 100
                                  ? 'bg-green-600'
                                  : stageProgress.overdueMilestones > 0
                                  ? 'bg-red-600'
                                  : 'bg-blue-600'
                              }`}
                              style={{ width: `${stageProgress.completionPercentage}%` }}
                            />
                          </div>
                        </div>
                      </div>
                    )}
                    
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

                {/* Stage Metrics */}
                {stageProgress && stageProgress.overdueMilestones > 0 && (
                  <div className="mt-3 flex items-center space-x-4 text-sm">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                      {stageProgress.overdueMilestones} overdue
                    </span>
                    {stageProgress.averageDelayDays > 0 && (
                      <span className="text-gray-600">
                        Avg delay: {Math.round(stageProgress.averageDelayDays)} days
                      </span>
                    )}
                  </div>
                )}
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
                        
                        return (
                          <div
                            key={milestone.id}
                            className={`flex items-start space-x-3 p-4 rounded-lg border-2 transition-colors ${
                              delay?.status === 'OVERDUE' && milestone.isCritical
                                ? 'border-red-300 bg-red-50'
                                : delay?.status === 'OVERDUE'
                                ? 'border-red-200 bg-red-50'
                                : delay?.status === 'DELAYED'
                                ? 'border-yellow-200 bg-yellow-50'
                                : milestone.isCompleted
                                ? 'border-green-200 bg-green-50'
                                : 'border-gray-200 bg-white'
                            }`}
                          >
                            {/* Completion Checkbox */}
                            <div className="flex-shrink-0 mt-1">
                              <div className={`w-6 h-6 rounded border-2 flex items-center justify-center ${
                                milestone.isCompleted 
                                  ? 'bg-green-500 border-green-500'
                                  : milestone.isCritical
                                  ? 'border-red-500'
                                  : 'border-gray-300'
                              }`}>
                                {milestone.isCompleted && (
                                  <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                  </svg>
                                )}
                              </div>
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

                                {/* Delay Badge */}
                                {delay && (
                                  <div className="ml-4 flex-shrink-0">
                                    {getDelayBadge(delay.delayDays, delay.status)}
                                  </div>
                                )}
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
        })}
      </div>

      {/* Footer Stats */}
      <div className="mt-6 bg-gray-50 rounded-lg p-4">
        <div className="grid grid-cols-4 gap-4 text-center text-sm">
          <div>
            <div className="font-semibold text-gray-900">{timelineProgress.totalMilestones}</div>
            <div className="text-gray-600">Total Milestones</div>
          </div>
          <div>
            <div className="font-semibold text-green-600">{timelineProgress.completedMilestones}</div>
            <div className="text-gray-600">Completed</div>
          </div>
          <div>
            <div className="font-semibold text-yellow-600">{timelineProgress.pendingMilestones}</div>
            <div className="text-gray-600">Pending</div>
          </div>
          <div>
            <div className="font-semibold text-red-600">{timelineProgress.overdueMilestones}</div>
            <div className="text-gray-600">Overdue</div>
          </div>
        </div>
      </div>
    </div>
  );
}

Component.displayName = 'TimelineProgressPage';
