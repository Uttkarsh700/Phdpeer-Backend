// Writing Evolution & Authorship Continuity Types

// 7 Core Aspects of Academic Writing Maturity
export const WRITING_ASPECTS = [
  {
    id: 'research_question',
    name: 'Research Question Precision',
    description: 'Clarity, scope, and feasibility of your research questions',
    badges: [
      { id: 'scope_clarity', name: 'Scope Clarity', description: 'Defines clear boundaries and scope' },
      { id: 'feasibility_awareness', name: 'Feasibility Awareness', description: 'Demonstrates practical research awareness' },
      { id: 'gap_articulation', name: 'Gap Articulation', description: 'Clearly articulates research gaps' },
      { id: 'question_refinement', name: 'Question Refinement', description: 'Shows progressive question improvement' }
    ]
  },
  {
    id: 'argumentation_spine',
    name: 'Argumentation Spine',
    description: 'Logical structure and flow of your central argument',
    badges: [
      { id: 'claim_evidence', name: 'Claim–Evidence Alignment', description: 'Evidence directly supports claims' },
      { id: 'logical_flow', name: 'Logical Flow', description: 'Arguments progress coherently' },
      { id: 'counter_handling', name: 'Counter-Argument Handling', description: 'Addresses opposing viewpoints' },
      { id: 'thesis_consistency', name: 'Thesis Consistency', description: 'Maintains consistent central argument' }
    ]
  },
  {
    id: 'evidence_integration',
    name: 'Evidence Integration',
    description: 'How well you incorporate and synthesize sources',
    badges: [
      { id: 'source_quality', name: 'Source Quality', description: 'Uses authoritative, relevant sources' },
      { id: 'synthesis_over_summary', name: 'Synthesis over Summary', description: 'Synthesizes rather than summarizes' },
      { id: 'critical_engagement', name: 'Critical Engagement', description: 'Critically evaluates sources' },
      { id: 'citation_integration', name: 'Citation Integration', description: 'Integrates citations smoothly' }
    ]
  },
  {
    id: 'method_result_coherence',
    name: 'Method-Result Coherence',
    description: 'Alignment between methodology and findings presentation',
    badges: [
      { id: 'method_justification', name: 'Method Justification', description: 'Justifies methodological choices' },
      { id: 'result_alignment', name: 'Result Alignment', description: 'Results align with stated methods' },
      { id: 'limitation_awareness', name: 'Limitation Awareness', description: 'Acknowledges methodological limits' },
      { id: 'replicability', name: 'Replicability Clarity', description: 'Provides reproducible descriptions' }
    ]
  },
  {
    id: 'contribution_positioning',
    name: 'Contribution & Positioning',
    description: 'How you articulate and position your research contribution',
    badges: [
      { id: 'contribution_clarity', name: 'Contribution Clarity', description: 'Clearly states contributions' },
      { id: 'field_positioning', name: 'Field Positioning', description: 'Positions work within field' },
      { id: 'significance_framing', name: 'Significance Framing', description: 'Frames importance effectively' },
      { id: 'originality_marking', name: 'Originality Marking', description: 'Highlights novel elements' }
    ]
  },
  {
    id: 'academic_style',
    name: 'Academic Style Control',
    description: 'Consistency and appropriateness of academic tone and language',
    badges: [
      { id: 'tone_consistency', name: 'Tone Consistency', description: 'Maintains consistent academic voice' },
      { id: 'precision_language', name: 'Precision Language', description: 'Uses precise terminology' },
      { id: 'hedging_mastery', name: 'Hedging Mastery', description: 'Appropriate use of hedging' },
      { id: 'discipline_conventions', name: 'Discipline Conventions', description: 'Follows field-specific norms' }
    ]
  },
  {
    id: 'structure_signposting',
    name: 'Structure & Signposting',
    description: 'Organization and reader guidance throughout the text',
    badges: [
      { id: 'macro_structure', name: 'Macro Structure', description: 'Clear overall organization' },
      { id: 'paragraph_coherence', name: 'Paragraph Coherence', description: 'Well-structured paragraphs' },
      { id: 'transition_mastery', name: 'Transition Mastery', description: 'Smooth transitions between sections' },
      { id: 'reader_guidance', name: 'Reader Guidance', description: 'Effective signposting for readers' }
    ]
  }
] as const;

// 5-Tier Maturity Scale
export const MATURITY_LEVELS = [
  { level: 1, name: 'Descriptive', description: 'Presents information without analysis', color: 'text-muted-foreground' },
  { level: 2, name: 'Analytical', description: 'Shows analysis but lacks argumentation', color: 'text-yellow-500' },
  { level: 3, name: 'Argumentative', description: 'Builds coherent arguments with evidence', color: 'text-blue-500' },
  { level: 4, name: 'Scholarly', description: 'Demonstrates disciplinary expertise', color: 'text-purple-500' },
  { level: 5, name: 'Publication-Ready', description: 'Meets peer-review publication standards', color: 'text-emerald-500' }
] as const;

export const DISCIPLINES = [
  'Social Sciences',
  'Humanities',
  'STEM',
  'Health Sciences',
  'Business & Management',
  'Education',
  'Law',
  'Arts & Design',
  'Interdisciplinary'
] as const;

export const RESEARCH_TYPES = [
  { value: 'qualitative', label: 'Qualitative' },
  { value: 'quantitative', label: 'Quantitative' },
  { value: 'mixed_methods', label: 'Mixed Methods' },
  { value: 'conceptual', label: 'Conceptual/Theoretical' }
] as const;

export const STAGES = [
  { value: 'early', label: 'Early PhD (Year 1-2)' },
  { value: 'mid', label: 'Mid PhD (Year 2-3)' },
  { value: 'late', label: 'Late PhD (Year 3+)' }
] as const;

export const LANGUAGES = [
  { value: 'en', label: 'English' },
  { value: 'es', label: 'Spanish' },
  { value: 'fr', label: 'French' },
  { value: 'de', label: 'German' },
  { value: 'zh', label: 'Chinese' },
  { value: 'pt', label: 'Portuguese' },
  { value: 'other', label: 'Other' }
] as const;

export const MILESTONE_TYPES = [
  { value: 'proposal', label: 'Research Proposal' },
  { value: 'chapter_draft', label: 'Chapter Draft' },
  { value: 'revision', label: 'Revision' },
  { value: 'conference_paper', label: 'Conference Paper' },
  { value: 'journal_submission', label: 'Journal Submission' },
  { value: 'thesis_section', label: 'Thesis Section' }
] as const;

// Types
export interface Badge {
  id: string;
  name: string;
  description: string;
  level: number; // 0-5, 0 = not earned
  earnedAt?: string;
}

export interface AspectEvaluation {
  aspectId: string;
  level: number; // 1-5 maturity level
  score: number; // 0-100 for progress bar
  strengths: string[];
  improvements: string[];
  badges: Badge[];
}

export interface WritingBaseline {
  id: string;
  createdAt: string;
  method: 'upload' | 'write';
  discipline: string;
  researchType: string;
  stage: string;
  language: string;
  wordCount: number;
  consentGiven: boolean;
  supervisorViewEnabled: boolean;
  institutionViewEnabled: boolean;
  aspects: AspectEvaluation[];
  overallLevel: number;
}

export interface Submission {
  id: string;
  createdAt: string;
  milestoneType: string;
  wordCount: number;
  aiAssisted: boolean;
  externalEditing: boolean;
  coauthorInput: boolean;
  aspects: AspectEvaluation[];
  overallLevel: number;
  reflectionAnswers?: Record<string, string>;
}

export interface WritingProfile {
  baseline: WritingBaseline | null;
  submissions: Submission[];
  certificateEligible: boolean;
}

export interface ReflectionQuestion {
  id: string;
  aspectId: string;
  question: string;
  followUp: string;
}

// Reflection questions by aspect
export const REFLECTION_QUESTIONS: Record<string, ReflectionQuestion[]> = {
  research_question: [
    { id: 'rq1', aspectId: 'research_question', question: 'How has your research question evolved since your last submission?', followUp: 'Consider what new insights have shaped your focus.' },
    { id: 'rq2', aspectId: 'research_question', question: 'What boundaries have you set for your research scope?', followUp: 'Reflect on what you chose to include and exclude.' }
  ],
  argumentation_spine: [
    { id: 'as1', aspectId: 'argumentation_spine', question: 'What is the central claim of this submission?', followUp: 'State it in one sentence.' },
    { id: 'as2', aspectId: 'argumentation_spine', question: 'How did you address potential counter-arguments?', followUp: 'Consider opposing viewpoints you acknowledged.' }
  ],
  evidence_integration: [
    { id: 'ei1', aspectId: 'evidence_integration', question: 'Which sources were most influential in this section?', followUp: 'Reflect on why these sources shaped your thinking.' },
    { id: 'ei2', aspectId: 'evidence_integration', question: 'Where did you synthesize multiple sources together?', followUp: 'Identify moments of integration rather than listing.' }
  ],
  method_result_coherence: [
    { id: 'mr1', aspectId: 'method_result_coherence', question: 'How do your methods directly inform your findings?', followUp: 'Trace the connection from approach to outcome.' },
    { id: 'mr2', aspectId: 'method_result_coherence', question: 'What methodological limitations did you acknowledge?', followUp: 'Consider what constraints affected your work.' }
  ],
  contribution_positioning: [
    { id: 'cp1', aspectId: 'contribution_positioning', question: 'What does this work add to existing knowledge?', followUp: 'Be specific about your contribution.' },
    { id: 'cp2', aspectId: 'contribution_positioning', question: 'How does your work relate to the broader field?', followUp: 'Consider the conversation you are joining.' }
  ],
  academic_style: [
    { id: 'st1', aspectId: 'academic_style', question: 'What stylistic choices did you make consciously?', followUp: 'Reflect on tone, hedging, and terminology.' },
    { id: 'st2', aspectId: 'academic_style', question: 'Where did you struggle with academic voice?', followUp: 'Identify challenging passages.' }
  ],
  structure_signposting: [
    { id: 'ss1', aspectId: 'structure_signposting', question: 'How did you guide the reader through your argument?', followUp: 'Consider your use of transitions and signposts.' },
    { id: 'ss2', aspectId: 'structure_signposting', question: 'What organizational changes did you make from earlier drafts?', followUp: 'Reflect on structural evolution.' }
  ]
};

// Mock evaluation function (simulates analysis without AI)
export function generateMockEvaluation(): AspectEvaluation[] {
  return WRITING_ASPECTS.map(aspect => {
    const level = Math.floor(Math.random() * 3) + 2; // 2-4 range
    const score = level * 20 + Math.floor(Math.random() * 15);
    
    const strengthOptions = [
      'Shows consistent improvement in this area',
      'Demonstrates clear understanding of conventions',
      'Strong foundation for further development',
      'Above average for current stage'
    ];
    
    const improvementOptions = [
      'Consider more explicit signposting',
      'Strengthen the connection between claims and evidence',
      'Work on synthesizing sources more effectively',
      'Develop more nuanced hedging strategies'
    ];
    
    return {
      aspectId: aspect.id,
      level,
      score: Math.min(score, 95),
      strengths: [strengthOptions[Math.floor(Math.random() * strengthOptions.length)]],
      improvements: [improvementOptions[Math.floor(Math.random() * improvementOptions.length)]],
      badges: aspect.badges.map(b => ({
        ...b,
        level: Math.floor(Math.random() * 4), // 0-3
        earnedAt: Math.random() > 0.5 ? new Date().toISOString() : undefined
      }))
    };
  });
}

// Storage helpers
const STORAGE_KEY = 'frensei_writing_profile';

export function saveProfile(profile: WritingProfile): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(profile));
}

export function loadProfile(): WritingProfile {
  const stored = localStorage.getItem(STORAGE_KEY);
  if (stored) {
    return JSON.parse(stored);
  }
  return {
    baseline: null,
    submissions: [],
    certificateEligible: false
  };
}

export function clearProfile(): void {
  localStorage.removeItem(STORAGE_KEY);
}
