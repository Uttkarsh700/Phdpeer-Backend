/**
 * Analytics Dashboard Page
 * 
 * Read-only dashboard displaying analytics summary.
 * 
 * Behavior:
 * - Fetch GET /analytics/summary
 * - Render:
 *   - timeline status
 *   - progress %
 *   - delay indicators
 *   - journey health summary
 * - Read-only dashboard
 * - No calculations (all data from backend)
 */

import { useState, useEffect } from 'react';
import { analyticsService } from '@/services';
import { useGlobalStateStore, useGlobalStateActions } from '@/state/global';
import { getDevUserId } from '@/utils/devHelpers';
import type { AnalyticsSummary } from '@/types/api';

type DashboardState = 
  | { type: 'loading' }
  | { type: 'error'; message: string }
  | { type: 'empty' }
  | { type: 'loaded'; summary: AnalyticsSummary };

export function Component() {
  const [state, setState] = useState<DashboardState>({ type: 'loading' });
  const globalState = useGlobalStateStore();
  const { setAnalyticsStatus } = useGlobalStateActions();

  useEffect(() => {
    loadAnalytics();
  }, []);

  /**
   * Fetch analytics summary from GET /analytics/summary
   * 
   * All data comes from backend - no frontend calculations.
   * 
   * States:
   * - loading: Waiting for backend response
   * - error: Backend returned error (use backend error message)
   * - empty: Backend returned successfully but no data
   * - loaded: Backend returned data successfully
   * 
   * Note: We check invariant as a guard, but let backend be the final validator.
   * If state is incorrect, backend will return appropriate error.
   */
  const loadAnalytics = async () => {
    // Invariant check: No analytics without committed timeline
    // This is a frontend guard, but backend is the source of truth
    // If state is incorrect, we still try to load and let backend validate
    const hasCommittedTimeline = globalState.timelineStatus === 'COMMITTED';
    
    if (!hasCommittedTimeline) {
      // Frontend guard: warn user but still try backend (in case state is stale)
      console.warn('Frontend state indicates no committed timeline, but attempting to load analytics anyway');
    }

    // Loading = waiting for backend
    setState({ type: 'loading' });

    try {
      // Fetch GET /analytics/summary
      // Backend will validate if committed timeline exists
      // Backend requires user_id - get from dev helper or localStorage
      const userId = getDevUserId();
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/4e161292-030e-4892-a887-f175fa552c2f',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'DashboardPage.tsx:70',message:'Got user ID from dev helper',data:{userId,hasUserId:!!userId,userIdType:typeof userId},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
      // #endregion
      
      if (!userId) {
        // #region agent log
        fetch('http://127.0.0.1:7242/ingest/4e161292-030e-4892-a887-f175fa552c2f',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'DashboardPage.tsx:73',message:'No user ID available',data:{},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
        // #endregion
        // No user_id available - show helpful error
        setState({ 
          type: 'error', 
          message: 'User ID is required to load analytics. Please ensure you are logged in or set a user_id in localStorage for development (e.g., localStorage.setItem("user_id", "your-user-id")).' 
        });
        return;
      }
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/4e161292-030e-4892-a887-f175fa552c2f',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'DashboardPage.tsx:81',message:'Calling analytics service',data:{userId},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
      // #endregion
      const data = await analyticsService.getSummary({ userId });
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/4e161292-030e-4892-a887-f175fa552c2f',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'DashboardPage.tsx:82',message:'Analytics service returned',data:{hasData:!!data,hasTimelineId:!!data?.timeline_id,dataKeys:Object.keys(data||{})},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'F'})}).catch(()=>{});
      // #endregion
      
      // If we get data, update state to reflect analytics are available
      if (data && data.timeline_id) {
        setAnalyticsStatus('AVAILABLE');
      }
      
      // Empty = backend returned no data (explicit check)
      // Check if summary is null, undefined, or has no meaningful data
      if (!data || !data.timeline_id) {
        setState({ type: 'empty' });
        return;
      }

      // Loaded = backend returned data
      setState({ type: 'loaded', summary: data });
    } catch (err: any) {
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/4e161292-030e-4892-a887-f175fa552c2f',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'DashboardPage.tsx:97',message:'Error caught in loadAnalytics',data:{errorType:err?.constructor?.name,errorMessage:err?.message,errorStatus:err?.status,errorResponse:err?.response?.data,hasDetail:!!err?.response?.data?.detail},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'ALL'})}).catch(()=>{});
      // #endregion
      // Error = backend error message (no guessing)
      // ApiClientError provides backend error message in err.message
      // FastAPI errors provide detail in err.response?.data?.detail
      const errorMessage = 
        err?.message || 
        err?.response?.data?.detail || 
        err?.detail || 
        'Failed to load analytics';
      
      // If backend says no committed timeline, update state
      if (errorMessage.toLowerCase().includes('committed timeline') || 
          errorMessage.toLowerCase().includes('timeline is required')) {
        setAnalyticsStatus('UNAVAILABLE');
      }
      
      setState({ type: 'error', message: errorMessage });
    }
  };

  /**
   * Get status badge color based on timeline status from backend
   */
  const getStatusBadgeColor = (status: string) => {
    switch (status) {
      case 'on_track':
        return 'bg-green-100 text-green-800';
      case 'delayed':
        return 'bg-yellow-100 text-yellow-800';
      case 'completed':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  /**
   * Get health score color
   */
  const getHealthScoreColor = (score: number | null) => {
    if (score === null) return 'text-gray-600';
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-blue-600';
    if (score >= 40) return 'text-yellow-600';
    return 'text-red-600';
  };

  // Loading = waiting for backend
  if (state.type === 'loading') {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-4"></div>
          <p className="text-gray-600">Loading analytics dashboard...</p>
          <p className="mt-2 text-sm text-gray-500">Fetching data from backend</p>
        </div>
      </div>
    );
  }

  // Error = backend error message (no guessing)
  if (state.type === 'error') {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3 flex-1">
              <h3 className="text-lg font-semibold text-red-900 mb-2">Error Loading Analytics</h3>
              <p className="text-red-800 mb-4">
                <strong>Backend Error:</strong> {state.message}
              </p>
              <button
                onClick={loadAnalytics}
                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500"
              >
                Retry
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Empty = backend returned no data (explicit check, no guessing)
  if (state.type === 'empty') {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-12 text-center">
          <div className="flex justify-center mb-4">
            <svg className="h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No Analytics Data Available</h3>
          <p className="text-gray-600 mb-4">
            The backend returned successfully but no analytics data was found.
          </p>
          <p className="text-sm text-gray-500 mb-6">
            This may occur if you haven't created a timeline yet or if analytics haven't been generated.
          </p>
          <button
            onClick={loadAnalytics}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Refresh
          </button>
        </div>
      </div>
    );
  }

  // Loaded = backend returned data successfully
  const summary = state.summary;

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
        <p className="mt-2 text-gray-600">
          Comprehensive overview of your PhD journey progress and health
        </p>
        <p className="mt-1 text-sm text-gray-500">
          Last updated: {new Date(summary.generated_at).toLocaleString()}
        </p>
      </div>

      {/* Timeline Status */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Timeline Status</h2>
        <div className="flex items-center space-x-4">
          <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStatusBadgeColor(summary.timeline_status)}`}>
            {summary.timeline_status.replace('_', ' ').toUpperCase()}
          </span>
          <span className="text-sm text-gray-600">
            Timeline ID: {summary.timeline_id}
          </span>
        </div>
      </div>

      {/* Progress Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        {/* Progress Percentage */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-600">Progress</span>
            <svg className="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="text-3xl font-bold text-gray-900 mb-1">
            {Math.round(summary.milestones.completion_percentage)}%
          </div>
          <p className="text-sm text-gray-600">
            {summary.milestones.completed} of {summary.milestones.total} milestones
          </p>
          <div className="mt-3 w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all"
              style={{ width: `${summary.milestones.completion_percentage}%` }}
            />
          </div>
        </div>

        {/* Pending Milestones */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-600">Pending</span>
            <svg className="w-5 h-5 text-yellow-600" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="text-3xl font-bold text-gray-900 mb-1">
            {summary.milestones.pending}
          </div>
          <p className="text-sm text-gray-600">Milestones remaining</p>
        </div>

        {/* Completed Milestones */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-600">Completed</span>
            <svg className="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="text-3xl font-bold text-green-600 mb-1">
            {summary.milestones.completed}
          </div>
          <p className="text-sm text-gray-600">Milestones finished</p>
        </div>

        {/* Total Milestones */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-600">Total</span>
            <svg className="w-5 h-5 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
              <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z" />
            </svg>
          </div>
          <div className="text-3xl font-bold text-gray-900 mb-1">
            {summary.milestones.total}
          </div>
          <p className="text-sm text-gray-600">Total milestones</p>
        </div>
      </div>

      {/* Delay Indicators */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Delay Indicators</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          {/* Total Delays */}
          <div className="border border-gray-200 rounded-lg p-4">
            <div className="text-sm font-medium text-gray-600 mb-1">Total Delays</div>
            <div className="text-2xl font-bold text-gray-900">{summary.delays.total_delays}</div>
          </div>

          {/* Overdue Milestones */}
          <div className="border border-red-200 rounded-lg p-4 bg-red-50">
            <div className="text-sm font-medium text-red-800 mb-1">Overdue</div>
            <div className="text-2xl font-bold text-red-600">{summary.delays.overdue_milestones}</div>
          </div>

          {/* Overdue Critical */}
          <div className="border border-red-300 rounded-lg p-4 bg-red-100">
            <div className="text-sm font-medium text-red-900 mb-1">Critical Overdue</div>
            <div className="text-2xl font-bold text-red-700">{summary.delays.overdue_critical_milestones}</div>
          </div>

          {/* Average Delay */}
          <div className="border border-yellow-200 rounded-lg p-4 bg-yellow-50">
            <div className="text-sm font-medium text-yellow-800 mb-1">Avg Delay</div>
            <div className="text-2xl font-bold text-yellow-600">
              {Math.round(summary.delays.average_delay_days)} days
            </div>
          </div>

          {/* Max Delay */}
          <div className="border border-orange-200 rounded-lg p-4 bg-orange-50">
            <div className="text-sm font-medium text-orange-800 mb-1">Max Delay</div>
            <div className="text-2xl font-bold text-orange-600">
              {summary.delays.max_delay_days} days
            </div>
          </div>
        </div>

        {/* Delay Warning */}
        {summary.delays.overdue_critical_milestones > 0 && (
          <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Critical Milestones Overdue</h3>
                <p className="mt-1 text-sm text-red-700">
                  {summary.delays.overdue_critical_milestones} critical milestone(s) are overdue. 
                  Please review and take action.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Journey Health Summary */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Journey Health Summary</h2>
        
        {/* Overall Health Score */}
        {summary.journey_health.latest_score !== null ? (
          <div className="mb-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-600">Overall Health Score</span>
              <span className={`text-3xl font-bold ${getHealthScoreColor(summary.journey_health.latest_score)}`}>
                {Math.round(summary.journey_health.latest_score)}/100
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className={`h-3 rounded-full ${
                  summary.journey_health.latest_score >= 80 ? 'bg-green-600' :
                  summary.journey_health.latest_score >= 60 ? 'bg-blue-600' :
                  summary.journey_health.latest_score >= 40 ? 'bg-yellow-600' :
                  'bg-red-600'
                }`}
                style={{ width: `${summary.journey_health.latest_score}%` }}
              />
            </div>
          </div>
        ) : (
          <div className="mb-6 p-4 bg-gray-50 border border-gray-200 rounded-lg">
            <p className="text-sm text-gray-600">No health assessment available yet</p>
          </div>
        )}

        {/* Health Dimensions */}
        {Object.keys(summary.journey_health.dimensions).length > 0 && (
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-4">Health Dimensions</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(summary.journey_health.dimensions).map(([dimension, score]) => (
                <div key={dimension} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-900">
                      {dimension.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </span>
                    <span className={`text-lg font-semibold ${getHealthScoreColor(score)}`}>
                      {Math.round(score)}/100
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        score >= 80 ? 'bg-green-600' :
                        score >= 60 ? 'bg-blue-600' :
                        score >= 40 ? 'bg-yellow-600' :
                        'bg-red-600'
                      }`}
                      style={{ width: `${score}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Longitudinal Summary */}
      {summary.longitudinal_summary && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Timeline Overview</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {summary.longitudinal_summary.timeline_committed_date && (
              <div className="border border-gray-200 rounded-lg p-4">
                <div className="text-sm font-medium text-gray-600 mb-1">Committed Date</div>
                <div className="text-base font-semibold text-gray-900">
                  {new Date(summary.longitudinal_summary.timeline_committed_date).toLocaleDateString()}
                </div>
              </div>
            )}
            {summary.longitudinal_summary.target_completion_date && (
              <div className="border border-gray-200 rounded-lg p-4">
                <div className="text-sm font-medium text-gray-600 mb-1">Target Completion</div>
                <div className="text-base font-semibold text-gray-900">
                  {new Date(summary.longitudinal_summary.target_completion_date).toLocaleDateString()}
                </div>
              </div>
            )}
            {summary.longitudinal_summary.duration_progress_percentage !== null && (
              <div className="border border-gray-200 rounded-lg p-4">
                <div className="text-sm font-medium text-gray-600 mb-1">Duration Progress</div>
                <div className="text-base font-semibold text-gray-900">
                  {Math.round(summary.longitudinal_summary.duration_progress_percentage)}%
                </div>
              </div>
            )}
            {summary.longitudinal_summary.total_progress_events !== undefined && (
              <div className="border border-gray-200 rounded-lg p-4">
                <div className="text-sm font-medium text-gray-600 mb-1">Progress Events</div>
                <div className="text-base font-semibold text-gray-900">
                  {summary.longitudinal_summary.total_progress_events}
                </div>
              </div>
            )}
            {summary.longitudinal_summary.latest_assessment && (
              <div className="border border-blue-200 rounded-lg p-4 bg-blue-50">
                <div className="text-sm font-medium text-blue-800 mb-1">Latest Assessment</div>
                <div className="text-base font-semibold text-blue-900">
                  {new Date(summary.longitudinal_summary.latest_assessment.assessment_date).toLocaleDateString()}
                </div>
                {summary.longitudinal_summary.latest_assessment.overall_rating && (
                  <div className="text-sm text-blue-700 mt-1">
                    Rating: {summary.longitudinal_summary.latest_assessment.overall_rating}/10
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

Component.displayName = 'DashboardPage';
