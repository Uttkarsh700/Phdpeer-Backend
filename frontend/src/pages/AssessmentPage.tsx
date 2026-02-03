/**
 * PhD Doctor Questionnaire Page
 * 
 * Interactive questionnaire for assessing PhD journey health.
 * 
 * Behavior:
 * - Auto-save via POST /doctor/save-draft
 * - Submit via POST /doctor/submit
 * - Render JourneyAssessment summary
 * - Lock UI after submission
 * - No access to timeline data
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { assessmentService } from '@/services';
import { useGlobalStateActions } from '@/state/global';
import type { AssessmentSummary, QuestionnaireResponse } from '@/types/api';

interface Question {
  id: string;
  dimension: string;
  text: string;
  helpText?: string;
}

// Questionnaire structure - matches backend dimensions
const DIMENSIONS = [
  'RESEARCH_PROGRESS',
  'MENTAL_WELLBEING',
  'WORK_LIFE_BALANCE',
  'TIME_MANAGEMENT',
  'SUPERVISOR_RELATIONSHIP',
  'PEER_SUPPORT',
  'MOTIVATION',
  'WRITING_PROGRESS',
] as const;

const QUESTIONS: Question[] = [
  // Research Progress
  { id: 'rp1', dimension: 'RESEARCH_PROGRESS', text: 'How satisfied are you with your research progress?', helpText: '1 = Very dissatisfied, 5 = Very satisfied' },
  { id: 'rp2', dimension: 'RESEARCH_PROGRESS', text: 'How clear are your research objectives and methodology?', helpText: '1 = Very unclear, 5 = Very clear' },
  { id: 'rp3', dimension: 'RESEARCH_PROGRESS', text: 'How confident are you about achieving your research goals?', helpText: '1 = Not confident, 5 = Very confident' },
  { id: 'rp4', dimension: 'RESEARCH_PROGRESS', text: 'How often do you encounter significant research roadblocks?', helpText: '1 = Constantly, 5 = Rarely' },
  
  // Mental Wellbeing
  { id: 'mw1', dimension: 'MENTAL_WELLBEING', text: 'How would you rate your overall mental health?', helpText: '1 = Poor, 5 = Excellent' },
  { id: 'mw2', dimension: 'MENTAL_WELLBEING', text: 'How often do you feel overwhelmed by your PhD work?', helpText: '1 = Always, 5 = Never' },
  { id: 'mw3', dimension: 'MENTAL_WELLBEING', text: 'How well are you managing stress and anxiety?', helpText: '1 = Very poorly, 5 = Very well' },
  { id: 'mw4', dimension: 'MENTAL_WELLBEING', text: 'How motivated do you feel about your PhD?', helpText: '1 = Not motivated, 5 = Highly motivated' },
  
  // Work-Life Balance
  { id: 'wlb1', dimension: 'WORK_LIFE_BALANCE', text: 'How satisfied are you with your work-life balance?', helpText: '1 = Very dissatisfied, 5 = Very satisfied' },
  { id: 'wlb2', dimension: 'WORK_LIFE_BALANCE', text: 'How often do you take time for non-PhD activities?', helpText: '1 = Never, 5 = Regularly' },
  { id: 'wlb3', dimension: 'WORK_LIFE_BALANCE', text: 'How supported do you feel by family and friends?', helpText: '1 = Not supported, 5 = Very supported' },
  
  // Time Management
  { id: 'tm1', dimension: 'TIME_MANAGEMENT', text: 'How well do you manage your time and priorities?', helpText: '1 = Very poorly, 5 = Very well' },
  { id: 'tm2', dimension: 'TIME_MANAGEMENT', text: 'How often do you meet your own deadlines?', helpText: '1 = Never, 5 = Always' },
  { id: 'tm3', dimension: 'TIME_MANAGEMENT', text: 'How organized is your research workflow?', helpText: '1 = Very disorganized, 5 = Very organized' },
  
  // Supervisor Relationship
  { id: 'sr1', dimension: 'SUPERVISOR_RELATIONSHIP', text: 'How satisfied are you with your supervisor relationship?', helpText: '1 = Very dissatisfied, 5 = Very satisfied' },
  { id: 'sr2', dimension: 'SUPERVISOR_RELATIONSHIP', text: 'How often do you receive helpful feedback from your supervisor?', helpText: '1 = Never, 5 = Very frequently' },
  { id: 'sr3', dimension: 'SUPERVISOR_RELATIONSHIP', text: 'How accessible is your supervisor when you need guidance?', helpText: '1 = Not accessible, 5 = Very accessible' },
  { id: 'sr4', dimension: 'SUPERVISOR_RELATIONSHIP', text: 'How clear are expectations from your supervisor?', helpText: '1 = Very unclear, 5 = Very clear' },
  
  // Peer Support
  { id: 'ps1', dimension: 'PEER_SUPPORT', text: 'How connected do you feel with fellow PhD students?', helpText: '1 = Very isolated, 5 = Very connected' },
  { id: 'ps2', dimension: 'PEER_SUPPORT', text: 'How often do you receive support from peers?', helpText: '1 = Never, 5 = Very often' },
  { id: 'ps3', dimension: 'PEER_SUPPORT', text: 'How integrated do you feel in your academic community?', helpText: '1 = Not integrated, 5 = Very integrated' },
  
  // Motivation
  { id: 'm1', dimension: 'MOTIVATION', text: 'How motivated are you to continue your PhD journey?', helpText: '1 = Not motivated, 5 = Highly motivated' },
  { id: 'm2', dimension: 'MOTIVATION', text: 'How excited are you about your research topic?', helpText: '1 = Not excited, 5 = Very excited' },
  
  // Writing Progress
  { id: 'wp1', dimension: 'WRITING_PROGRESS', text: 'How satisfied are you with your writing progress?', helpText: '1 = Very dissatisfied, 5 = Very satisfied' },
  { id: 'wp2', dimension: 'WRITING_PROGRESS', text: 'How confident are you in your academic writing skills?', helpText: '1 = Not confident, 5 = Very confident' },
];

const DIMENSION_LABELS: Record<string, string> = {
  RESEARCH_PROGRESS: 'Research Progress',
  MENTAL_WELLBEING: 'Mental Wellbeing',
  WORK_LIFE_BALANCE: 'Work-Life Balance',
  TIME_MANAGEMENT: 'Time Management',
  SUPERVISOR_RELATIONSHIP: 'Supervisor Relationship',
  PEER_SUPPORT: 'Peer Support',
  MOTIVATION: 'Motivation',
  WRITING_PROGRESS: 'Writing Progress',
};

export function Component() {
  const navigate = useNavigate();
  const { setDoctorStatus } = useGlobalStateActions();

  // Form state
  const [responses, setResponses] = useState<Map<string, number>>(new Map());
  const [notes, setNotes] = useState('');
  const [currentDimension, setCurrentDimension] = useState(0);
  const [draftId, setDraftId] = useState<string | null>(null);

  // UI state
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saveMessage, setSaveMessage] = useState<string | null>(null);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [assessmentSummary, setAssessmentSummary] = useState<AssessmentSummary | null>(null);

  // Auto-save timer ref
  const autoSaveTimerRef = useRef<NodeJS.Timeout | null>(null);
  const lastSaveRef = useRef<Map<string, number>>(new Map());

  /**
   * Auto-save draft via POST /doctor/save-draft
   * 
   * Debounced to avoid excessive API calls.
   */
  const autoSaveDraft = useCallback(async () => {
    if (isSubmitted || responses.size === 0) return;

    // Check if responses have changed
    const hasChanges = Array.from(responses.entries()).some(
      ([id, value]) => lastSaveRef.current.get(id) !== value
    );

    if (!hasChanges) return;

    setSaving(true);
    setError(null);

    try {
      const questionnaireResponses = Array.from(responses.entries())
        .map(([questionId, value]) => {
          const question = QUESTIONS.find(q => q.id === questionId)!;
          return {
            dimension: question.dimension,
            question_id: questionId,
            response_value: value,
            question_text: question.text,
          };
        });

      const result = await assessmentService.saveDraft({
        responses: questionnaireResponses,
        notes: notes || undefined,
      });

      setDraftId(result.draftId);
      lastSaveRef.current = new Map(responses);
      setSaveMessage('Progress saved');
      setTimeout(() => setSaveMessage(null), 2000);
    } catch (err: any) {
      // Silent fail for auto-save - don't show error to user
      console.error('Auto-save failed:', err);
    } finally {
      setSaving(false);
    }
  }, [responses, notes, isSubmitted]);

  // Auto-save on response change (debounced)
  useEffect(() => {
    if (autoSaveTimerRef.current) {
      clearTimeout(autoSaveTimerRef.current);
    }

    autoSaveTimerRef.current = setTimeout(() => {
      autoSaveDraft();
    }, 2000); // 2 second debounce

    return () => {
      if (autoSaveTimerRef.current) {
        clearTimeout(autoSaveTimerRef.current);
      }
    };
  }, [responses, notes, autoSaveDraft]);

  const handleResponseChange = (questionId: string, value: number) => {
    if (isSubmitted) return; // Lock UI after submission

    const newResponses = new Map(responses);
    newResponses.set(questionId, value);
    setResponses(newResponses);
    setError(null);
  };

  const getCurrentDimensionQuestions = () => {
    const dimension = DIMENSIONS[currentDimension];
    return QUESTIONS.filter(q => q.dimension === dimension);
  };

  const isDimensionComplete = (dimIndex: number) => {
    const dimension = DIMENSIONS[dimIndex];
    const dimQuestions = QUESTIONS.filter(q => q.dimension === dimension);
    return dimQuestions.every(q => responses.has(q.id));
  };

  const getCompletionStats = () => {
    const answered = responses.size;
    const total = QUESTIONS.length;
    const percentage = Math.round((answered / total) * 100);
    return { answered, total, percentage };
  };

  const handleNext = () => {
    if (currentDimension < DIMENSIONS.length - 1) {
      setCurrentDimension(currentDimension + 1);
    }
  };

  const handlePrevious = () => {
    if (currentDimension > 0) {
      setCurrentDimension(currentDimension - 1);
    }
  };

  /**
   * Submit questionnaire via POST /doctor/submit
   * 
   * Locks UI and renders JourneyAssessment summary.
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validate minimum 5 responses
    if (responses.size < 5) {
      setError('Please answer at least 5 questions before submitting');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const questionnaireResponses: QuestionnaireResponse[] = Array.from(responses.entries()).map(([questionId, value]) => {
        const question = QUESTIONS.find(q => q.id === questionId)!;
        return {
          dimension: question.dimension,
          questionId,
          responseValue: value,
          questionText: question.text,
        };
      });

      // Call POST /doctor/submit
      const summary = await assessmentService.submitQuestionnaire({
        responses: questionnaireResponses,
        assessmentType: 'self_assessment',
        notes: notes || undefined,
        draftId: draftId || undefined,
      });

      // Lock UI after submission
      setIsSubmitted(true);
      setAssessmentSummary(summary);

      // Update global state - doctor status is now SUBMITTED
      setDoctorStatus('SUBMITTED');
    } catch (err: any) {
      setError(err.message || 'Failed to submit assessment');
    } finally {
      setLoading(false);
    }
  };

  const stats = getCompletionStats();
  const currentQuestions = getCurrentDimensionQuestions();
  const isLastDimension = currentDimension === DIMENSIONS.length - 1;
  const canProceed = isDimensionComplete(currentDimension);

  // Render assessment summary if submitted
  if (isSubmitted && assessmentSummary) {
    return (
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Assessment Submitted</h1>
          <p className="mt-2 text-gray-600">
            Your PhD journey health assessment has been submitted successfully.
          </p>
        </div>

        {/* Locked Notice */}
        <div className="mb-6 bg-green-50 border-2 border-green-300 rounded-lg p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-semibold text-green-800">Assessment Locked</h3>
              <p className="mt-1 text-sm text-green-700">
                This assessment has been submitted and cannot be modified. View your results below.
              </p>
            </div>
          </div>
        </div>

        {/* JourneyAssessment Summary */}
        <div className="space-y-6">
          {/* Overall Score */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Overall Assessment</h2>
            <div className="flex items-center justify-between">
              <div>
                <div className="text-4xl font-bold text-blue-600 mb-2">
                  {Math.round(assessmentSummary.overallScore)}/100
                </div>
                <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                  assessmentSummary.overallStatus === 'excellent' ? 'bg-green-100 text-green-800' :
                  assessmentSummary.overallStatus === 'good' ? 'bg-blue-100 text-blue-800' :
                  assessmentSummary.overallStatus === 'fair' ? 'bg-yellow-100 text-yellow-800' :
                  assessmentSummary.overallStatus === 'concerning' ? 'bg-orange-100 text-orange-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  {assessmentSummary.overallStatus.toUpperCase()}
                </div>
              </div>
              <div className="text-right text-sm text-gray-600">
                <div>Date: {new Date(assessmentSummary.assessmentDate).toLocaleDateString()}</div>
                <div>{assessmentSummary.totalResponses} responses</div>
              </div>
            </div>
          </div>

          {/* Summary Text */}
          {assessmentSummary.summary && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Summary</h2>
              <p className="text-gray-700 whitespace-pre-wrap">{assessmentSummary.summary}</p>
            </div>
          )}

          {/* Critical Areas */}
          {assessmentSummary.criticalAreas.length > 0 && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-6">
              <h2 className="text-xl font-semibold text-red-900 mb-4">Areas Needing Attention</h2>
              <div className="space-y-4">
                {assessmentSummary.criticalAreas.map((area, index) => (
                  <div key={index} className="bg-white rounded p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-semibold text-gray-900">{area.dimension}</h3>
                      <span className="text-sm font-medium text-red-600">Score: {Math.round(area.score)}/100</span>
                    </div>
                    {area.concerns.length > 0 && (
                      <ul className="list-disc list-inside text-sm text-gray-700 mt-2">
                        {area.concerns.map((concern, i) => (
                          <li key={i}>{concern}</li>
                        ))}
                      </ul>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Healthy Areas */}
          {assessmentSummary.healthyAreas.length > 0 && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-6">
              <h2 className="text-xl font-semibold text-green-900 mb-4">Strengths</h2>
              <div className="space-y-4">
                {assessmentSummary.healthyAreas.map((area, index) => (
                  <div key={index} className="bg-white rounded p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-semibold text-gray-900">{area.dimension}</h3>
                      <span className="text-sm font-medium text-green-600">Score: {Math.round(area.score)}/100</span>
                    </div>
                    {area.strengths.length > 0 && (
                      <ul className="list-disc list-inside text-sm text-gray-700 mt-2">
                        {area.strengths.map((strength, i) => (
                          <li key={i}>{strength}</li>
                        ))}
                      </ul>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recommendations */}
          {assessmentSummary.recommendations.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Recommendations</h2>
              <div className="space-y-4">
                {assessmentSummary.recommendations.map((rec, index) => (
                  <div key={index} className={`border-l-4 p-4 ${
                    rec.priority === 'high' ? 'border-red-500 bg-red-50' :
                    rec.priority === 'medium' ? 'border-yellow-500 bg-yellow-50' :
                    'border-blue-500 bg-blue-50'
                  }`}>
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-semibold text-gray-900">{rec.title}</h3>
                      <span className={`text-xs font-medium px-2 py-1 rounded ${
                        rec.priority === 'high' ? 'bg-red-100 text-red-800' :
                        rec.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-blue-100 text-blue-800'
                      }`}>
                        {rec.priority.toUpperCase()} PRIORITY
                      </span>
                    </div>
                    <p className="text-sm text-gray-700 mb-2">{rec.description}</p>
                    {rec.actionItems.length > 0 && (
                      <ul className="list-disc list-inside text-sm text-gray-600 mt-2">
                        {rec.actionItems.map((item, i) => (
                          <li key={i}>{item}</li>
                        ))}
                      </ul>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Dimension Scores */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Dimension Scores</h2>
            <div className="grid grid-cols-2 gap-4">
              {Object.entries(assessmentSummary.dimensions).map(([dimension, data]) => (
                <div key={dimension} className="border border-gray-200 rounded p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-medium text-gray-900">{DIMENSION_LABELS[dimension] || dimension}</h3>
                    <span className="text-sm font-semibold text-blue-600">{Math.round(data.score)}/100</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: `${data.score}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Render questionnaire form
  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">PhD Journey Health Assessment</h1>
        <p className="mt-2 text-gray-600">
          Answer questions across {DIMENSIONS.length} dimensions to assess your PhD journey health.
          Your progress is automatically saved.
        </p>
      </div>

      {/* Overall Progress */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-semibold text-gray-900">Overall Progress</h3>
          <div className="flex items-center space-x-3">
            {saving && (
              <span className="text-sm text-gray-500">Saving...</span>
            )}
            {saveMessage && (
              <span className="text-sm text-green-600">{saveMessage}</span>
            )}
            <span className="text-2xl font-bold text-blue-600">{stats.percentage}%</span>
          </div>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div
            className="bg-blue-600 h-3 rounded-full transition-all duration-300"
            style={{ width: `${stats.percentage}%` }}
          />
        </div>
        <p className="mt-2 text-sm text-gray-600">
          {stats.answered} of {stats.total} questions answered
        </p>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-3">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {/* Dimension Navigation */}
      <div className="bg-white rounded-lg shadow mb-6">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">
            {DIMENSION_LABELS[DIMENSIONS[currentDimension]]}
          </h2>
          <p className="mt-1 text-sm text-gray-600">
            Section {currentDimension + 1} of {DIMENSIONS.length}
          </p>
        </div>

        {/* Dimension Progress Dots */}
        <div className="px-6 py-3 bg-gray-50 border-b border-gray-200">
          <div className="flex items-center justify-center space-x-2">
            {DIMENSIONS.map((_, index) => (
              <button
                key={index}
                onClick={() => setCurrentDimension(index)}
                disabled={isSubmitted}
                className={`w-3 h-3 rounded-full transition-colors ${
                  index === currentDimension
                    ? 'bg-blue-600 ring-2 ring-blue-200'
                    : isDimensionComplete(index)
                    ? 'bg-green-600'
                    : 'bg-gray-300'
                } ${isSubmitted ? 'cursor-not-allowed opacity-50' : 'cursor-pointer'}`}
                title={DIMENSION_LABELS[DIMENSIONS[index]]}
              />
            ))}
          </div>
        </div>

        {/* Questions */}
        <form onSubmit={handleSubmit} className="px-6 py-6">
          <div className="space-y-6">
            {currentQuestions.map((question) => {
              const value = responses.get(question.id);
              
              return (
                <div key={question.id} className="pb-6 border-b border-gray-200 last:border-b-0">
                  <label className="block">
                    <span className="text-base font-medium text-gray-900">
                      {question.text}
                    </span>
                    {question.helpText && (
                      <span className="block mt-1 text-sm text-gray-500">{question.helpText}</span>
                    )}
                    
                    {/* Rating Scale */}
                    <div className="mt-4">
                      <div className="flex items-center justify-between space-x-2">
                        {[1, 2, 3, 4, 5].map((rating) => (
                          <button
                            key={rating}
                            type="button"
                            onClick={() => handleResponseChange(question.id, rating)}
                            disabled={isSubmitted}
                            className={`flex-1 py-3 px-4 rounded-lg border-2 text-center font-semibold transition-all ${
                              value === rating
                                ? 'border-blue-600 bg-blue-600 text-white'
                                : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400 hover:bg-gray-50'
                            } ${isSubmitted ? 'cursor-not-allowed opacity-50' : 'cursor-pointer'}`}
                          >
                            {rating}
                          </button>
                        ))}
                      </div>
                      <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
                        <span>Low</span>
                        <span>High</span>
                      </div>
                    </div>
                  </label>
                </div>
              );
            })}
          </div>

          {/* Additional Notes (Last Section Only) */}
          {isLastDimension && (
            <div className="mt-8 pt-6 border-t border-gray-200">
              <label className="block">
                <span className="text-base font-medium text-gray-900">
                  Additional Comments (Optional)
                </span>
                <span className="block mt-1 text-sm text-gray-500">
                  Share any additional context or concerns about your PhD journey
                </span>
                <textarea
                  value={notes}
                  onChange={(e) => !isSubmitted && setNotes(e.target.value)}
                  disabled={isSubmitted}
                  rows={4}
                  className="mt-3 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                  placeholder="Your comments here..."
                />
              </label>
            </div>
          )}

          {/* Navigation Buttons */}
          <div className="mt-8 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              {currentDimension > 0 && (
                <button
                  type="button"
                  onClick={handlePrevious}
                  disabled={isSubmitted}
                  className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  ← Previous
                </button>
              )}
            </div>

            <div>
              {!isLastDimension ? (
                <button
                  type="button"
                  onClick={handleNext}
                  disabled={!canProceed || isSubmitted}
                  className="px-6 py-2 text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next →
                </button>
              ) : (
                <button
                  type="submit"
                  disabled={loading || responses.size < 5 || isSubmitted}
                  className="px-8 py-2 text-white bg-green-600 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? 'Submitting...' : 'Submit Assessment'}
                </button>
              )}
            </div>
          </div>
        </form>
      </div>

      {/* Help Text */}
      <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <p className="text-sm text-blue-800">
              <strong>Your progress is automatically saved.</strong> You can close this page and return later 
              to continue from where you left off. Once you submit, you'll receive personalized recommendations.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

Component.displayName = 'AssessmentPage';
