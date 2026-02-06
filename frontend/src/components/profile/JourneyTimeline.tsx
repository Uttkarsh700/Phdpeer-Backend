import { CheckCircle, Circle, ChevronDown } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";

interface JourneyTimelineProps {
  currentStage: string;
}

const stages = [
  { id: "proposal", name: "Proposal" },
  { id: "literature", name: "Literature Review" },
  { id: "data-collection", name: "Data Collection" },
  { id: "analysis", name: "Analysis" },
  { id: "writing", name: "Writing" },
  { id: "submission", name: "Submission" }
];

const mockPapers = [
  {
    id: "paper1",
    title: "Machine Learning in Healthcare",
    stages: [
      { id: "proposal", name: "Proposal", status: "completed" },
      { id: "literature", name: "Literature Review", status: "completed" },
      { id: "data-collection", name: "Data Collection", status: "current" },
      { id: "analysis", name: "Analysis", status: "pending" },
      { id: "writing", name: "Writing", status: "pending" },
      { id: "submission", name: "Submission", status: "pending" }
    ]
  },
  {
    id: "paper2",
    title: "Neural Networks for Image Recognition",
    stages: [
      { id: "proposal", name: "Proposal", status: "completed" },
      { id: "literature", name: "Literature Review", status: "current" },
      { id: "data-collection", name: "Data Collection", status: "pending" },
      { id: "analysis", name: "Analysis", status: "pending" },
      { id: "writing", name: "Writing", status: "pending" },
      { id: "submission", name: "Submission", status: "pending" }
    ]
  },
  {
    id: "paper3",
    title: "AI Ethics and Governance",
    stages: [
      { id: "proposal", name: "Proposal", status: "current" },
      { id: "literature", name: "Literature Review", status: "pending" },
      { id: "data-collection", name: "Data Collection", status: "pending" },
      { id: "analysis", name: "Analysis", status: "pending" },
      { id: "writing", name: "Writing", status: "pending" },
      { id: "submission", name: "Submission", status: "pending" }
    ]
  }
];

export const JourneyTimeline = ({ currentStage }: JourneyTimelineProps) => {
  const [viewMode, setViewMode] = useState<"overview" | "paperwise">("overview");
  const [expandedPaper, setExpandedPaper] = useState<string | null>(null);
  
  const normalizeStage = (stage: string) => {
    return stage.toLowerCase().replace(/\s+/g, "-");
  };

  const currentIndex = stages.findIndex(
    (s) => normalizeStage(s.name) === normalizeStage(currentStage)
  );

  return (
    <div className="relative space-y-4">
      {/* Toggle Button */}
      <div className="flex justify-end">
        <Button
          variant="outline"
          size="sm"
          onClick={() => setViewMode(viewMode === "overview" ? "paperwise" : "overview")}
          className="gap-2"
        >
          {viewMode === "overview" ? "View by Paper" : "View Overview"}
          <ChevronDown className={`w-4 h-4 transition-transform ${viewMode === "paperwise" ? "rotate-180" : ""}`} />
        </Button>
      </div>

      {viewMode === "overview" ? (
        /* Overview Timeline */
        <div className="flex items-center justify-between">
          {stages.map((stage, index) => {
            const isCompleted = index < currentIndex;
            const isCurrent = index === currentIndex;
            const isPast = index < currentIndex;
            
            return (
              <div key={stage.id} className="flex flex-col items-center flex-1 relative">
                {/* Connector Line */}
                {index < stages.length - 1 && (
                  <div className="absolute top-6 left-1/2 w-full h-0.5 -z-10">
                    <div
                      className={`h-full transition-all duration-300 ${
                        isPast ? "bg-primary" : "bg-border/30"
                      }`}
                    />
                  </div>
                )}
                
                {/* Stage Circle */}
                <div
                  className={`w-12 h-12 rounded-full flex items-center justify-center transition-all duration-300 ${
                    isCurrent
                      ? "bg-gradient-to-r from-[#FF7A18] to-[#FFB800] shadow-[0_0_20px_rgba(255,122,24,0.6)] scale-110"
                      : isCompleted
                      ? "bg-gradient-to-r from-[#FF7A18] to-[#FFB800] opacity-80"
                      : "bg-card border-2 border-border/50"
                  }`}
                >
                  {isCompleted ? (
                    <CheckCircle className="w-6 h-6 text-white" />
                  ) : (
                    <Circle 
                      className={`w-6 h-6 ${
                        isCurrent ? "text-white" : "text-muted-foreground"
                      }`} 
                    />
                  )}
                </div>
                
                {/* Stage Label */}
                <p
                  className={`text-xs mt-2 text-center font-medium transition-colors ${
                    isCurrent
                      ? "text-primary"
                      : isCompleted
                      ? "text-foreground"
                      : "text-muted-foreground"
                  }`}
                >
                  {stage.name}
                </p>
              </div>
            );
          })}
        </div>
      ) : (
        /* Paper-wise Timeline */
        <div className="space-y-3">
          {mockPapers.map((paper) => (
            <div key={paper.id} className="border border-border rounded-lg overflow-hidden bg-card">
              <button
                onClick={() => setExpandedPaper(expandedPaper === paper.id ? null : paper.id)}
                className="w-full px-4 py-3 flex items-center justify-between hover:bg-accent/50 transition-colors"
              >
                <span className="font-medium text-sm">{paper.title}</span>
                <ChevronDown 
                  className={`w-4 h-4 transition-transform ${
                    expandedPaper === paper.id ? "rotate-180" : ""
                  }`} 
                />
              </button>
              
              {expandedPaper === paper.id && (
                <div className="px-4 pb-4 pt-2">
                  <div className="flex items-center justify-between">
                    {paper.stages.map((stage, index) => {
                      const isCompleted = stage.status === "completed";
                      const isCurrent = stage.status === "current";
                      const isPast = stage.status === "completed";
                      
                      return (
                        <div key={stage.id} className="flex flex-col items-center flex-1 relative">
                          {index < paper.stages.length - 1 && (
                            <div className="absolute top-4 left-1/2 w-full h-0.5 -z-10">
                              <div
                                className={`h-full transition-all duration-300 ${
                                  isPast ? "bg-primary" : "bg-border/30"
                                }`}
                              />
                            </div>
                          )}
                          
                          <div
                            className={`w-8 h-8 rounded-full flex items-center justify-center transition-all duration-300 ${
                              isCurrent
                                ? "bg-gradient-to-r from-[#FF7A18] to-[#FFB800] shadow-[0_0_15px_rgba(255,122,24,0.5)] scale-110"
                                : isCompleted
                                ? "bg-gradient-to-r from-[#FF7A18] to-[#FFB800] opacity-80"
                                : "bg-card border-2 border-border/50"
                            }`}
                          >
                            {isCompleted ? (
                              <CheckCircle className="w-4 h-4 text-white" />
                            ) : (
                              <Circle 
                                className={`w-4 h-4 ${
                                  isCurrent ? "text-white" : "text-muted-foreground"
                                }`} 
                              />
                            )}
                          </div>
                          
                          <p
                            className={`text-[10px] mt-1 text-center font-medium transition-colors ${
                              isCurrent
                                ? "text-primary"
                                : isCompleted
                                ? "text-foreground"
                                : "text-muted-foreground"
                            }`}
                          >
                            {stage.name}
                          </p>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
