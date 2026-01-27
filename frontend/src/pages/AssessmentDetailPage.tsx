/**
 * Assessment Detail Page
 * 
 * Display detailed results from a PhD journey health assessment.
 * Shows overall status, dimension scores, and recommendations.
 */

import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { assessmentService } from '@/services';
import type { JourneyAssessment, AssessmentSummary } from '@/types/api';

export function Component() {
  const { assessmentId } = useParams<{ assessmentId: string }>();
  const navigate = useNavigate();

  const [assessment, setAssessment] = useState<JourneyAssessment | null>(null);
  const [summary, setSummary] = useState<AssessmentSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadAssessment();
  }, [assessmentId]);

  const loadAssessment = async () => {
    if (!assessmentId) return;

    setLoading(true);
    setError(null);

    try {
      const data = await assessmentService.getById(assessmentId);
      setAssessment(data);

      // Parse assessment data if stored in notes field
      if (data.notes) {
        try {
          const parsed = JSON.parse(data.notes);
          if (parsed.summary) {
            setSummary(parsed.summary);
          }
        } catch (err) {
          console.error('Failed to parse assessment data:', err);
        }
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load assessment');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'excellent': return 'bg-green-100 text-green-800 border-green-200';
      case 'good': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'fair': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'concerning': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'critical': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'excellent':
      case 'good':
        return (
          <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
          </svg>
        );
      case 'fair':
        return (
          <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
        );
      case 'concerning':
      case 'critical':
        return (
          <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
        );
      default:
        return null;
    }
  };

  const getPriorityBadge = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'high':
        return <span className="px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">High Priority</span>;
      case 'medium':
        return <span className="px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">Medium Priority</span>;
      case 'low':
        return <span className="px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">Low Priority</span>;
      default:
        return null;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-4"></div>
          <p className="text-gray-600">Loading assessment...</p>
        </div>
      </div>
    );
  }

  if (error && !assessment) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-red-900 mb-2">Error</h3>
        <p className="text-red-800">{error}</p>
        <button
          onClick={() => navigate('/health')}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
        >
          Back to Health Dashboard
        </button>
      </div>
    );
  }

  if (!assessment) {
    return <div className="text-center py-12"><p className="text-gray-600">Assessment not found</p></div>;
  }

  return (
    <div className="max-w-5xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Assessment Results</h1>
            <p className="mt-2 text-gray-600">
              Completed on {new Date(assessment.assessmentDate).toLocaleDateString()} at{' '}
              {new Date(assessment.assessmentDate).toLocaleTimeString()}
            </p>
          </div>
          <button
            onClick={() => navigate('/health')}
            className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Back to Health
          </button>
        </div>
      </div>

      {/* Overall Status */}
      {summary && (
        <div className={`rounded-lg border-2 p-6 mb-6 ${getStatusColor(summary.overallStatus)}`}>
          <div className="flex items-center space-x-4">
            {getStatusIcon(summary.overallStatus)}
            <div className="flex-1">
              <h2 className="text-2xl font-bold capitalize">{summary.overallStatus} Status</h2>
              <p className="mt-1 text-base">Overall Score: {summary.overallScore}/5</p>
            </div>
            <div className="text-5xl font-bold">
              {summary.overallScore.toFixed(1)}
            </div>
          </div>
          {summary.summary && (
            <p className="mt-4 text-base">{summary.summary}</p>
          )}
        </div>
      )}

      {/* Dimensions Overview */}
      {summary && Object.keys(summary.dimensions).length > 0 && (
        <div className="bg-white rounded-lg shadow mb-6">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">Dimensions Overview</h2>
            <p className="mt-1 text-sm text-gray-600">Your scores across different areas</p>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-2 gap-4">
              {Object.entries(summary.dimensions).map(([dimension, data]) => (
                <div key={dimension} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-semibold text-gray-900">
                      {dimension.replace(/_/g, ' ').toLowerCase().replace(/\b\w/g, l => l.toUpperCase())}
                    </h3>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(data.status)}`}>
                      {data.status}
                    </span>
                  </div>
                  <div className="mb-3">
                    <div className="flex items-center justify-between text-sm text-gray-600 mb-1">
                      <span>Score</span>
                      <span className="font-semibold">{data.score}/5</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${
                          data.score >= 4 ? 'bg-green-600' :
                          data.score >= 3 ? 'bg-blue-600' :
                          data.score >= 2 ? 'bg-yellow-600' :
                          'bg-red-600'
                        }`}
                        style={{ width: `${(data.score / 5) * 100}%` }}
                      />
                    </div>
                  </div>
                  {data.strengths && data.strengths.length > 0 && (
                    <div className="text-xs text-green-700 mb-1">
                      ✓ {data.strengths.length} strength{data.strengths.length !== 1 ? 's' : ''}
                    </div>
                  )}
                  {data.concerns && data.concerns.length > 0 && (
                    <div className="text-xs text-red-700">
                      ⚠ {data.concerns.length} concern{data.concerns.length !== 1 ? 's' : ''}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Critical Areas */}
      {summary && summary.criticalAreas && summary.criticalAreas.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 mb-6">
          <h2 className="text-xl font-semibold text-red-900 mb-4">⚠️ Areas Needing Attention</h2>
          <div className="space-y-4">
            {summary.criticalAreas.map((area, index) => (
              <div key={index} className="bg-white rounded-lg p-4 border border-red-200">
                <div className="flex items-start justify-between mb-2">
                  <h3 className="font-semibold text-gray-900">
                    {area.dimension.replace(/_/g, ' ').toLowerCase().replace(/\b\w/g, l => l.toUpperCase())}
                  </h3>
                  <span className="text-lg font-bold text-red-600">{area.score}/5</span>
                </div>
                {area.concerns && area.concerns.length > 0 && (
                  <ul className="space-y-1">
                    {area.concerns.map((concern, i) => (
                      <li key={i} className="text-sm text-gray-700 flex items-start">
                        <span className="text-red-500 mr-2">•</span>
                        <span>{concern}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Healthy Areas */}
      {summary && summary.healthyAreas && summary.healthyAreas.length > 0 && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-6 mb-6">
          <h2 className="text-xl font-semibold text-green-900 mb-4">✓ Your Strengths</h2>
          <div className="space-y-4">
            {summary.healthyAreas.map((area, index) => (
              <div key={index} className="bg-white rounded-lg p-4 border border-green-200">
                <div className="flex items-start justify-between mb-2">
                  <h3 className="font-semibold text-gray-900">
                    {area.dimension.replace(/_/g, ' ').toLowerCase().replace(/\b\w/g, l => l.toUpperCase())}
                  </h3>
                  <span className="text-lg font-bold text-green-600">{area.score}/5</span>
                </div>
                {area.strengths && area.strengths.length > 0 && (
                  <ul className="space-y-1">
                    {area.strengths.map((strength, i) => (
                      <li key={i} className="text-sm text-gray-700 flex items-start">
                        <span className="text-green-500 mr-2">•</span>
                        <span>{strength}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {summary && summary.recommendations && summary.recommendations.length > 0 && (
        <div className="bg-white rounded-lg shadow mb-6">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">💡 Recommendations</h2>
            <p className="mt-1 text-sm text-gray-600">Personalized action items for improvement</p>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {summary.recommendations.map((rec, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="font-semibold text-gray-900">{rec.title}</h3>
                    {getPriorityBadge(rec.priority)}
                  </div>
                  <p className="text-sm text-gray-700 mb-3">{rec.description}</p>
                  {rec.actionItems && rec.actionItems.length > 0 && (
                    <div>
                      <p className="text-xs font-medium text-gray-600 mb-2">Action Items:</p>
                      <ul className="space-y-1">
                        {rec.actionItems.map((action, i) => (
                          <li key={i} className="text-sm text-gray-700 flex items-start">
                            <span className="text-blue-500 mr-2">→</span>
                            <span>{action}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  <p className="mt-2 text-xs text-gray-500">
                    Related to: {rec.dimension.replace(/_/g, ' ').toLowerCase().replace(/\b\w/g, l => l.toUpperCase())}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Additional Notes */}
      {assessment.notes && !summary && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Additional Notes</h3>
          <p className="text-sm text-gray-700 whitespace-pre-wrap">{assessment.notes}</p>
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center justify-center space-x-4 mt-8">
        <button
          onClick={() => navigate('/health/history')}
          className="px-6 py-2 text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          View History
        </button>
        <button
          onClick={() => navigate('/health/assessment')}
          className="px-6 py-2 text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          Take New Assessment
        </button>
      </div>
    </div>
  );
}

Component.displayName = 'AssessmentDetailPage';
