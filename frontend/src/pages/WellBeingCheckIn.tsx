import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { SectionForm } from "@/components/wellness/SectionForm";
import { ResultsCard } from "@/components/wellness/ResultsCard";
import { SignalsTab } from "@/components/wellness/SignalsTab";
import { ContinuityReportTab } from "@/components/wellness/ContinuityReportTab";
import { RecommendationsTab } from "@/components/wellness/RecommendationsTab";
import { wellnessSections } from "@/data/wellnessQuestions";
import {
  calculateWellnessIndices,
  SectionScores,
  AutoData,
  CalculationResults,
} from "@/lib/wellnessCalculations";
import { ChevronLeft, ChevronRight, Check, RefreshCw } from "lucide-react";
import { toast } from "sonner";

const WellBeingCheckIn = () => {
  const [currentSection, setCurrentSection] = useState(0);
  const [responses, setResponses] = useState<Record<string, number>>({});
  const [results, setResults] = useState<CalculationResults | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // TODO: Replace with backend data from AnalyticsSummary
  // Progress data should come from backend, not computed here
  // const analyticsSummary = await get<AnalyticsSummary>('/analytics/summary');
  // const autoData = {
  //   milestoneCompletion: analyticsSummary.milestone_completion_percentage,
  //   avgDelay: analyticsSummary.average_delay_days,
  //   // ... other fields from backend
  // };
  
  // Placeholder - will be replaced with backend data
  const mockAutoData = {
    milestoneCompletion: 0, // Backend-provided from AnalyticsSummary
    avgDelay: 0, // Backend-provided from AnalyticsSummary
    supervisorResponseTime: 0, // Backend-provided
    meetingCadence: 0, // Backend-provided
    opportunitiesAdded: 0, // Backend-provided
  };

  // TODO: Replace with backend data from JourneyAssessment
  // const previousAssessment = await get<JourneyAssessment>('/doctor/latest');
  // const mockPreviousRCI = previousAssessment?.overall_progress_rating || 0;
  const mockPreviousRCI = 0; // Backend-provided

  const handleResponseChange = (questionId: string, value: number) => {
    setResponses((prev) => ({ ...prev, [questionId]: value }));
  };

  const getCurrentSectionProgress = () => {
    const section = wellnessSections[currentSection];
    const answeredCount = section.questions.filter(
      (q) => responses[q.id] !== undefined
    ).length;
    return (answeredCount / section.questions.length) * 100;
  };

  const isCurrentSectionComplete = () => {
    const section = wellnessSections[currentSection];
    return section.questions.every((q) => responses[q.id] !== undefined);
  };

  const getTotalProgress = () => {
    const totalQuestions = wellnessSections.reduce(
      (sum, s) => sum + s.questions.length,
      0
    );
    const answeredQuestions = Object.keys(responses).length;
    return (answeredQuestions / totalQuestions) * 100;
  };

  const handleNext = () => {
    if (currentSection < wellnessSections.length - 1) {
      setCurrentSection(currentSection + 1);
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  };

  const handlePrevious = () => {
    if (currentSection > 0) {
      setCurrentSection(currentSection - 1);
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    
    // Simulate processing delay
    await new Promise((resolve) => setTimeout(resolve, 1500));

    // Organize responses by section
    const sectionScores: SectionScores = {
      supervision: [],
      progress: [],
      clarity: [],
      workload: [],
      funding: [],
      support: [],
      wellbeing: [],
      career: [],
    };

    wellnessSections.forEach((section) => {
      const scores = section.questions
        .map((q) => responses[q.id])
        .filter((r) => r !== undefined);
      sectionScores[section.id as keyof SectionScores] = scores;
    });

    // Calculate indices
    const calculatedResults = calculateWellnessIndices(
      sectionScores,
      mockAutoData,
      mockPreviousRCI
    );

    setResults(calculatedResults);
    setIsSubmitting(false);
    
    toast.success("Assessment completed!", {
      description: `Your RCI score is ${Math.round(calculatedResults.RCI)} - ${calculatedResults.band}`,
    });

    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleReset = () => {
    setCurrentSection(0);
    setResponses({});
    setResults(null);
    toast.info("Assessment reset. You can start fresh.");
  };

  const canSubmit = getTotalProgress() === 100;

  if (results) {
    return (
      <div className="min-h-screen bg-background py-8 px-4">
        <div className="max-w-5xl mx-auto space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold">Well-Being Check-in Results</h1>
              <p className="text-muted-foreground mt-1">
                Quarterly assessment completed
              </p>
            </div>
            <Button onClick={handleReset} variant="outline">
              <RefreshCw className="mr-2 h-4 w-4" />
              New Assessment
            </Button>
          </div>

          <Tabs defaultValue="results" className="w-full">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="results">Results</TabsTrigger>
              <TabsTrigger value="signals">Signals</TabsTrigger>
              <TabsTrigger value="continuity">Continuity Report</TabsTrigger>
              <TabsTrigger value="recommendations">Recommendations</TabsTrigger>
            </TabsList>
            <TabsContent value="results" className="mt-6">
              <ResultsCard results={results} />
            </TabsContent>
            <TabsContent value="signals" className="mt-6">
              <SignalsTab results={results} autoData={mockAutoData} />
            </TabsContent>
            <TabsContent value="continuity" className="mt-6">
              <ContinuityReportTab results={results} autoData={mockAutoData} />
            </TabsContent>
            <TabsContent value="recommendations" className="mt-6">
              <RecommendationsTab results={results} />
            </TabsContent>
          </Tabs>
        </div>
      </div>
    );
  }

  const section = wellnessSections[currentSection];

  return (
    <div className="min-h-screen bg-background py-8 px-4">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="space-y-4">
          <div>
            <h1 className="text-3xl font-bold">Well-Being Check-in</h1>
            <p className="text-muted-foreground mt-1">
              Quarterly assessment • {wellnessSections.length} sections
            </p>
          </div>

          {/* Overall progress */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Overall progress</span>
              <span className="font-medium">{Math.round(getTotalProgress())}%</span>
            </div>
            <Progress value={getTotalProgress()} className="h-2" />
          </div>
        </div>

        {/* Section indicator */}
        <div className="flex gap-2 overflow-x-auto pb-2">
          {wellnessSections.map((s, idx) => {
            const sectionProgress = s.questions.filter(
              (q) => responses[q.id] !== undefined
            ).length;
            const sectionTotal = s.questions.length;
            const isComplete = sectionProgress === sectionTotal;

            return (
              <button
                key={s.id}
                onClick={() => setCurrentSection(idx)}
                className={`flex flex-col items-center gap-1 p-3 rounded-lg min-w-[100px] transition-all ${
                  idx === currentSection
                    ? "bg-primary text-primary-foreground"
                    : isComplete
                    ? "bg-success/10 text-success hover:bg-success/20"
                    : "bg-muted hover:bg-muted/80"
                }`}
              >
                <span className="text-xs font-medium whitespace-nowrap">
                  {s.title}
                </span>
                <span className="text-[10px] opacity-80">
                  {isComplete ? (
                    <Check className="w-3 h-3" />
                  ) : (
                    `${sectionProgress}/${sectionTotal}`
                  )}
                </span>
              </button>
            );
          })}
        </div>

        {/* Current section */}
        <SectionForm
          section={section}
          responses={responses}
          onResponseChange={handleResponseChange}
        />

        {/* Navigation */}
        <div className="flex items-center justify-between pt-4">
          <Button
            variant="outline"
            onClick={handlePrevious}
            disabled={currentSection === 0}
          >
            <ChevronLeft className="mr-2 h-4 w-4" />
            Previous
          </Button>

          <div className="text-sm text-muted-foreground">
            Section {currentSection + 1} of {wellnessSections.length}
          </div>

          {currentSection === wellnessSections.length - 1 ? (
            <Button
              onClick={handleSubmit}
              disabled={!canSubmit || isSubmitting}
              className="min-w-[120px]"
            >
              {isSubmitting ? (
                <>
                  <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  Submit
                  <Check className="ml-2 h-4 w-4" />
                </>
              )}
            </Button>
          ) : (
            <Button
              onClick={handleNext}
              disabled={!isCurrentSectionComplete()}
            >
              Next
              <ChevronRight className="ml-2 h-4 w-4" />
            </Button>
          )}
        </div>
      </div>
    </div>
  );
};

export default WellBeingCheckIn;
