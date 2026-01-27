/**
 * PhD Doctor Assessment Page
 * 
 * Questionnaire for assessing PhD journey health across multiple dimensions.
 * Features: Save/resume progress, single submission, clear validation.
 */

import { useState, useEffect, FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { assessmentService } from '@/services';
import type { QuestionnaireResponse } from '@/types/api';

interface Question {
  id: string;
  dimension: string;
  text: string;
  helpText?: string;
}

// Questionnaire structure
const DIMENSIONS = [
  'RESEARCH_PROGRESS',
  'MENTAL_WELLBEING',
  'SUPERVISOR_RELATIONSHIP',
  'TIME_MANAGEMENT',
  'WORK_LIFE_BALANCE',
  'ACADEMIC_SKILLS',
  'FUNDING_STATUS',
  'PEER_SUPPORT',
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
  
  // Supervisor Relationship
  { id: 'sr1', dimension: 'SUPERVISOR_RELATIONSHIP', text: 'How satisfied are you with your supervisor relationship?', helpText: '1 = Very dissatisfied, 5 = Very satisfied' },
  { id: 'sr2', dimension: 'SUPERVISOR_RELATIONSHIP', text: 'How often do you receive helpful feedback from your supervisor?', helpText: '1 = Never, 5 = Very frequently' },
  { id: 'sr3', dimension: 'SUPERVISOR_RELATIONSHIP', text: 'How accessible is your supervisor when you need guidance?', helpText: '1 = Not accessible, 5 = Very accessible' },
  { id: 'sr4', dimension: 'SUPERVISOR_RELATIONSHIP', text: 'How clear are expectations from your supervisor?', helpText: '1 = Very unclear, 5 = Very clear' },
  
  // Time Management
  { id: 'tm1', dimension: 'TIME_MANAGEMENT', text: 'How well do you manage your time and priorities?', helpText: '1 = Very poorly, 5 = Very well' },
  { id: 'tm2', dimension: 'TIME_MANAGEMENT', text: 'How often do you meet your own deadlines?', helpText: '1 = Never, 5 = Always' },
  { id: 'tm3', dimension: 'TIME_MANAGEMENT', text: 'How organized is your research workflow?', helpText: '1 = Very disorganized, 5 = Very organized' },
  
  // Work-Life Balance
  { id: 'wlb1', dimension: 'WORK_LIFE_BALANCE', text: 'How satisfied are you with your work-life balance?', helpText: '1 = Very dissatisfied, 5 = Very satisfied' },
  { id: 'wlb2', dimension: 'WORK_LIFE_BALANCE', text: 'How often do you take time for non-PhD activities?', helpText: '1 = Never, 5 = Regularly' },
  { id: 'wlb3', dimension: 'WORK_LIFE_BALANCE', text: 'How supported do you feel by family and friends?', helpText: '1 = Not supported, 5 = Very supported' },
  
  // Academic Skills
  { id: 'as1', dimension: 'ACADEMIC_SKILLS', text: 'How confident are you in your research methods and skills?', helpText: '1 = Not confident, 5 = Very confident' },
  { id: 'as2', dimension: 'ACADEMIC_SKILLS', text: 'How comfortable are you with academic writing?', helpText: '1 = Very uncomfortable, 5 = Very comfortable' },
  { id: 'as3', dimension: 'ACADEMIC_SKILLS', text: 'How prepared do you feel for presenting your research?', helpText: '1 = Not prepared, 5 = Very prepared' },
  
  // Funding Status
  { id: 'fs1', dimension: 'FUNDING_STATUS', text: 'How secure is your current funding situation?', helpText: '1 = Very insecure, 5 = Very secure' },
  { id: 'fs2', dimension: 'FUNDING_STATUS', text: 'How concerned are you about financial matters?', helpText: '1 = Extremely concerned, 5 = Not concerned' },
  
  // Peer Support
  { id: 'ps1', dimension: 'PEER_SUPPORT', text: 'How connected do you feel with fellow PhD students?', helpText: '1 = Very isolated, 5 = Very connected' },
  { id: 'ps2', dimension: 'PEER_SUPPORT', text: 'How often do you receive support from peers?', helpText: '1 = Never, 5 = Very often' },
  { id: 'ps3', dimension: 'PEER_SUPPORT', text: 'How integrated do you feel in your academic community?', helpText: '1 = Not integrated, 5 = Very integrated' },
];

const DIMENSION_LABELS: Record<string, string> = {
  RESEARCH_PROGRESS: 'Research Progress',
  MENTAL_WELLBEING: 'Mental Wellbeing',
  SUPERVISOR_RELATIONSHIP: 'Supervisor Relationship',
  TIME_MANAGEMENT: 'Time Management',
  WORK_LIFE_BALANCE: 'Work-Life Balance',
  ACADEMIC_SKILLS: 'Academic Skills',
  FUNDING_STATUS: 'Funding Status',
  PEER_SUPPORT: 'Peer Support',
};

const STORAGE_KEY = 'phd_doctor_draft';

export function Component() {
  const navigate = useNavigate();

  // Form state
  const [responses, setResponses] = useState<Map<string, number>>(new Map());
  const [notes, setNotes] = useState('');
  const [currentDimension, setCurrentDimension] = useState(0);

  // UI state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saveMessage, setSaveMessage] = useState<string | null>(null);
  const [hasLoadedDraft, setHasLoadedDraft] = useState(false);

  // Load saved draft on mount
  useEffect(() => {
    const savedDraft = localStorage.getItem(STORAGE_KEY);
    if (savedDraft) {
      try {
        const draft = JSON.parse(savedDraft);
        const loadedResponses = new Map(Object.entries(draft.responses).map(([k, v]) => [k, Number(v)]));
        setResponses(loadedResponses);
        setNotes(draft.notes || '');
        setCurrentDimension(draft.currentDimension || 0);
        setHasLoadedDraft(true);
        setSaveMessage('Draft loaded. Continue where you left off!');
        setTimeout(() => setSaveMessage(null), 3000);
      } catch (err) {
        console.error('Failed to load draft:', err);
      }
    }
  }, []);

  // Save draft to localStorage
  const saveDraft = () => {
    try {
      const draft = {
        responses: Object.fromEntries(responses),
        notes,
        currentDimension,
        savedAt: new Date().toISOString(),
      };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(draft));
      setSaveMessage('Progress saved!');
      setTimeout(() => setSaveMessage(null), 2000);
    } catch (err) {
      console.error('Failed to save draft:', err);
      setError('Failed to save progress');
    }
  };

  // Clear draft from localStorage
  const clearDraft = () => {
    localStorage.removeItem(STORAGE_KEY);
  };

  const handleResponseChange = (questionId: string, value: number) => {
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
      saveDraft();
    }
  };

  const handlePrevious = () => {
    if (currentDimension > 0) {
      setCurrentDimension(currentDimension - 1);
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    // Validate all questions answered
    if (responses.size < QUESTIONS.length) {
      setError('Please answer all questions before submitting');
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

      const summary = await assessmentService.submitQuestionnaire({
        responses: questionnaireResponses,
        assessmentType: 'self_assessment',
        notes: notes || undefined,
      });

      // Clear draft after successful submission
      clearDraft();

      // Navigate to results page
      navigate(`/health/${summary.assessmentId}`);
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
          <span className="text-2xl font-bold text-blue-600">{stats.percentage}%</span>
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

      {/* Save Message */}
      {saveMessage && (
        <div className="mb-4 bg-green-50 border border-green-200 rounded-lg p-3">
          <p className="text-sm text-green-800">{saveMessage}</p>
        </div>
      )}

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
                className={`w-3 h-3 rounded-full transition-colors ${
                  index === currentDimension
                    ? 'bg-blue-600 ring-2 ring-blue-200'
                    : isDimensionComplete(index)
                    ? 'bg-green-600'
                    : 'bg-gray-300'
                }`}
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
                            className={`flex-1 py-3 px-4 rounded-lg border-2 text-center font-semibold transition-all ${
                              value === rating
                                ? 'border-blue-600 bg-blue-600 text-white'
                                : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400 hover:bg-gray-50'
                            }`}
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
                  onChange={(e) => setNotes(e.target.value)}
                  rows={4}
                  className="mt-3 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
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
                  className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  ← Previous
                </button>
              )}
              <button
                type="button"
                onClick={saveDraft}
                className="px-4 py-2 text-blue-700 bg-blue-50 border border-blue-200 rounded-md hover:bg-blue-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                💾 Save Progress
              </button>
            </div>

            <div>
              {!isLastDimension ? (
                <button
                  type="button"
                  onClick={handleNext}
                  disabled={!canProceed}
                  className="px-6 py-2 text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next →
                </button>
              ) : (
                <button
                  type="submit"
                  disabled={loading || responses.size < QUESTIONS.length}
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
