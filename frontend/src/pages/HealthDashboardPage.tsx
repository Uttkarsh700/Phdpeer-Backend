/**
 * Health Dashboard Page
 * 
 * Main dashboard for PhD journey health assessments.
 * Shows latest assessment, history, and option to start new assessment.
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { assessmentService } from '@/services';
import type { JourneyAssessment } from '@/types/api';

export function Component() {
  const navigate = useNavigate();

  const [latestAssessment, setLatestAssessment] = useState<JourneyAssessment | null>(null);
  const [assessmentHistory, setAssessmentHistory] = useState<JourneyAssessment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    setLoading(true);
    setError(null);

    try {
      const [latest, history] = await Promise.all([
        assessmentService.getLatest(),
        assessmentService.getHistory('self_assessment', 5),
      ]);

      setLatestAssessment(latest);
      setAssessmentHistory(history);
    } catch (err: any) {
      setError(err.message || 'Failed to load dashboard');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (rating?: number) => {
    if (!rating) return 'bg-gray-100 text-gray-800';
    if (rating >= 4) return 'bg-green-100 text-green-800';
    if (rating >= 3) return 'bg-blue-100 text-blue-800';
    if (rating >= 2) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  const getStatusLabel = (rating?: number) => {
    if (!rating) return 'Unknown';
    if (rating >= 4.5) return 'Excellent';
    if (rating >= 3.5) return 'Good';
    if (rating >= 2.5) return 'Fair';
    if (rating >= 1.5) return 'Concerning';
    return 'Critical';
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

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">PhD Journey Health</h1>
        <p className="mt-2 text-gray-600">
          Monitor your wellbeing and progress through regular self-assessments
        </p>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {/* Latest Assessment */}
      {latestAssessment ? (
        <div className="bg-white rounded-lg shadow mb-6">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold text-gray-900">Latest Assessment</h2>
              <button
                onClick={() => navigate('/health/assessment')}
                className="px-4 py-2 text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                Take New Assessment
              </button>
            </div>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-4 gap-6 mb-6">
              <div className="text-center">
                <div className="text-4xl font-bold text-gray-900 mb-1">
                  {latestAssessment.overallProgressRating?.toFixed(1) || 'N/A'}
                </div>
                <div className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(latestAssessment.overallProgressRating)}`}>
                  {getStatusLabel(latestAssessment.overallProgressRating)}
                </div>
                <div className="mt-2 text-sm text-gray-600">Overall Progress</div>
              </div>
              <div className="text-center">
                <div className="text-4xl font-bold text-gray-900 mb-1">
                  {latestAssessment.researchQualityRating?.toFixed(1) || 'N/A'}
                </div>
                <div className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(latestAssessment.researchQualityRating)}`}>
                  {getStatusLabel(latestAssessment.researchQualityRating)}
                </div>
                <div className="mt-2 text-sm text-gray-600">Research Quality</div>
              </div>
              <div className="text-center">
                <div className="text-4xl font-bold text-gray-900 mb-1">
                  {latestAssessment.timelineAdherenceRating?.toFixed(1) || 'N/A'}
                </div>
                <div className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(latestAssessment.timelineAdherenceRating)}`}>
                  {getStatusLabel(latestAssessment.timelineAdherenceRating)}
                </div>
                <div className="mt-2 text-sm text-gray-600">Timeline Adherence</div>
              </div>
              <div className="text-center">
                <div className="text-sm text-gray-600 mb-2">Assessed</div>
                <div className="text-base font-semibold text-gray-900">
                  {new Date(latestAssessment.assessmentDate).toLocaleDateString()}
                </div>
                <div className="text-sm text-gray-500">
                  {new Date(latestAssessment.assessmentDate).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
              </div>
            </div>

            {/* Key Insights */}
            <div className="grid grid-cols-3 gap-4 pt-4 border-t border-gray-200">
              {latestAssessment.strengths && (
                <div className="bg-green-50 rounded-lg p-4 border border-green-200">
                  <h3 className="text-sm font-semibold text-green-900 mb-2">✓ Strengths</h3>
                  <p className="text-sm text-green-800 line-clamp-3">{latestAssessment.strengths}</p>
                </div>
              )}
              {latestAssessment.challenges && (
                <div className="bg-yellow-50 rounded-lg p-4 border border-yellow-200">
                  <h3 className="text-sm font-semibold text-yellow-900 mb-2">⚠ Challenges</h3>
                  <p className="text-sm text-yellow-800 line-clamp-3">{latestAssessment.challenges}</p>
                </div>
              )}
              {latestAssessment.actionItems && (
                <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                  <h3 className="text-sm font-semibold text-blue-900 mb-2">→ Action Items</h3>
                  <p className="text-sm text-blue-800 line-clamp-3">{latestAssessment.actionItems}</p>
                </div>
              )}
            </div>

            <div className="mt-4 flex items-center justify-center">
              <button
                onClick={() => navigate(`/health/${latestAssessment.id}`)}
                className="px-6 py-2 text-blue-700 bg-blue-50 border border-blue-200 rounded-md hover:bg-blue-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                View Full Report
              </button>
            </div>
          </div>
        </div>
      ) : (
        /* No Assessment Yet */
        <div className="bg-white rounded-lg shadow mb-6 p-12 text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-blue-100 mb-4">
            <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Welcome to PhD Journey Health</h2>
          <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
            Take your first assessment to get personalized insights about your PhD journey. 
            The questionnaire covers mental wellbeing, research progress, supervisor relationship, 
            and more. Your responses are confidential and help identify areas for support.
          </p>
          <button
            onClick={() => navigate('/health/assessment')}
            className="px-8 py-3 text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 text-lg font-semibold"
          >
            Take Your First Assessment
          </button>
        </div>
      )}

      {/* Quick Stats */}
      {assessmentHistory.length > 0 && (
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-6 text-center">
            <div className="text-3xl font-bold text-blue-600 mb-2">
              {assessmentHistory.length}
            </div>
            <div className="text-sm text-gray-600">Total Assessments</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6 text-center">
            <div className="text-3xl font-bold text-green-600 mb-2">
              {assessmentHistory.filter(a => (a.overallProgressRating || 0) >= 3.5).length}
            </div>
            <div className="text-sm text-gray-600">Good or Better</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6 text-center">
            <div className="text-3xl font-bold text-purple-600 mb-2">
              {latestAssessment ? Math.ceil((new Date().getTime() - new Date(latestAssessment.assessmentDate).getTime()) / (1000 * 3600 * 24)) : 0}
            </div>
            <div className="text-sm text-gray-600">Days Since Last</div>
          </div>
        </div>
      )}

      {/* Assessment History */}
      {assessmentHistory.length > 0 && (
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold text-gray-900">Assessment History</h2>
              <button
                onClick={() => navigate('/health/history')}
                className="text-blue-600 hover:text-blue-700 text-sm font-medium"
              >
                View All →
              </button>
            </div>
          </div>
          <div className="divide-y divide-gray-200">
            {assessmentHistory.slice(0, 5).map((assessment) => (
              <div
                key={assessment.id}
                className="px-6 py-4 hover:bg-gray-50 cursor-pointer transition-colors"
                onClick={() => navigate(`/health/${assessment.id}`)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(assessment.overallProgressRating)}`}>
                        {getStatusLabel(assessment.overallProgressRating)}
                      </span>
                      <span className="text-sm text-gray-600">
                        {new Date(assessment.assessmentDate).toLocaleDateString()} at{' '}
                        {new Date(assessment.assessmentDate).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                    <div className="mt-2 flex items-center space-x-6 text-sm">
                      <div>
                        <span className="text-gray-600">Overall: </span>
                        <span className="font-semibold text-gray-900">
                          {assessment.overallProgressRating?.toFixed(1) || 'N/A'}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-600">Research: </span>
                        <span className="font-semibold text-gray-900">
                          {assessment.researchQualityRating?.toFixed(1) || 'N/A'}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-600">Timeline: </span>
                        <span className="font-semibold text-gray-900">
                          {assessment.timelineAdherenceRating?.toFixed(1) || 'N/A'}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div>
                    <svg className="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Help Section */}
      <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-2">About PhD Journey Health</h3>
        <div className="space-y-2 text-sm text-blue-800">
          <p>
            <strong>Regular check-ins</strong> help you monitor your wellbeing and progress throughout your PhD journey.
          </p>
          <p>
            <strong>Assessments cover:</strong> Research progress, mental wellbeing, supervisor relationship, 
            time management, work-life balance, academic skills, funding security, and peer support.
          </p>
          <p>
            <strong>Your data is private</strong> and used only to provide personalized recommendations and track your progress over time.
          </p>
          <p>
            <strong>Recommendation:</strong> Complete an assessment monthly to track trends and identify issues early.
          </p>
        </div>
      </div>
    </div>
  );
}

Component.displayName = 'HealthDashboardPage';
