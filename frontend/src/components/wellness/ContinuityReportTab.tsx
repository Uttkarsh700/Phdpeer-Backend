import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { FileDown, Share2, Calendar, TrendingUp, AlertCircle, CheckCircle } from "lucide-react";
import { toast } from "sonner";
import { CalculationResults } from "@/lib/wellnessCalculations";
import { useNavigate } from "react-router-dom";

interface ContinuityReportTabProps {
  results: CalculationResults | null;
  autoData: {
    milestoneCompletion: number;
    avgDelay: number;
    supervisorResponseTime: number;
    meetingCadence?: number;
  };
}

export const ContinuityReportTab = ({ results, autoData }: ContinuityReportTabProps) => {
  const navigate = useNavigate();
  
  // Mock data (in real app, this would come from database/state)
  const studentData = {
    name: "Research Student",
    startDate: "September 2023",
    currentStage: "Year 2, Quarter 1",
    researchQuestions: [
      {
        question: "How does climate change affect coastal ecosystems?",
        timestamp: "Sep 2023",
        status: "Refined",
      },
      {
        question: "What are the adaptive mechanisms of marine species to rising ocean temperatures?",
        timestamp: "Mar 2024",
        status: "Current",
      },
    ],
    quarterlyMilestones: [
      {
        quarter: "Q1 2024",
        achievements: [
          "Completed literature review on marine adaptation",
          "Developed research methodology framework",
        ],
        blocks: [
          "Delayed ethics approval by 3 weeks",
        ],
      },
      {
        quarter: "Q2 2024",
        achievements: [
          "Collected field data from 3 coastal sites",
          "Presented preliminary findings at departmental seminar",
        ],
        blocks: [
          "Equipment malfunction delayed data collection",
        ],
      },
      {
        quarter: "Q3 2024",
        achievements: [
          "Completed initial data analysis",
          "Submitted conference abstract",
        ],
        blocks: [],
      },
    ],
    wellbeingTrend: [
      { quarter: "Q1 2024", rci: 58, band: "Vulnerable" as const },
      { quarter: "Q2 2024", rci: 62, band: "Vulnerable" as const },
      { quarter: "Q3 2024", rci: results?.RCI ?? 65, band: results?.band ?? "Vulnerable" as const },
    ],
  };

  const handleExportPDF = () => {
    toast.success("Exporting continuity report as PDF...", {
      description: "Your report will be downloaded shortly.",
    });
  };

  const handleShareWithSupervisor = () => {
    toast.success("Sharing with supervisor", {
      description: "Your supervisor will receive a notification with the report.",
    });
  };

  const handleAddToTimeline = () => {
    navigate("/collaboration-ledger"); // Navigate to Collaboration Tracker
  };

  return (
    <div className="space-y-6">
      {/* Action Buttons */}
      <div className="flex flex-wrap gap-3">
        <Button onClick={handleExportPDF} variant="default">
          <FileDown className="mr-2 h-4 w-4" />
          Export PDF
        </Button>
        <Button onClick={handleShareWithSupervisor} variant="secondary">
          <Share2 className="mr-2 h-4 w-4" />
          Share with Supervisor
        </Button>
        <Button onClick={handleAddToTimeline} variant="outline">
          <Calendar className="mr-2 h-4 w-4" />
          Add to Timeline
        </Button>
      </div>

      {/* Overview */}
      <Card>
        <CardHeader>
          <CardTitle>Research Overview</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-muted-foreground">Start Date</p>
              <p className="text-lg font-semibold">{studentData.startDate}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Current Stage</p>
              <p className="text-lg font-semibold">{studentData.currentStage}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Research Question History */}
      <Card>
        <CardHeader>
          <CardTitle>Research Question Evolution</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {studentData.researchQuestions.map((rq, index) => (
            <div key={index} className="space-y-2">
              <div className="flex items-start gap-3">
                <div className="mt-1">
                  {rq.status === "Current" ? (
                    <div className="h-3 w-3 rounded-full bg-primary animate-pulse" />
                  ) : (
                    <div className="h-3 w-3 rounded-full bg-muted" />
                  )}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <Badge variant={rq.status === "Current" ? "default" : "secondary"}>
                      {rq.status}
                    </Badge>
                    <span className="text-xs text-muted-foreground">{rq.timestamp}</span>
                  </div>
                  <p className="text-sm">{rq.question}</p>
                </div>
              </div>
              {index < studentData.researchQuestions.length - 1 && (
                <Separator className="my-3" />
              )}
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Quarterly Achievements & Blocks */}
      <Card>
        <CardHeader>
          <CardTitle>Key Milestones by Quarter</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {studentData.quarterlyMilestones.map((qm, index) => (
            <div key={index}>
              <h4 className="font-semibold mb-3">{qm.quarter}</h4>
              
              {qm.achievements.length > 0 && (
                <div className="mb-3">
                  <p className="text-sm text-muted-foreground mb-2 flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-success" />
                    Achievements
                  </p>
                  <ul className="space-y-1 ml-6">
                    {qm.achievements.map((achievement, i) => (
                      <li key={i} className="text-sm list-disc">{achievement}</li>
                    ))}
                  </ul>
                </div>
              )}

              {qm.blocks.length > 0 && (
                <div>
                  <p className="text-sm text-muted-foreground mb-2 flex items-center gap-2">
                    <AlertCircle className="h-4 w-4 text-warning" />
                    Blocks
                  </p>
                  <ul className="space-y-1 ml-6">
                    {qm.blocks.map((block, i) => (
                      <li key={i} className="text-sm list-disc text-warning">{block}</li>
                    ))}
                  </ul>
                </div>
              )}

              {index < studentData.quarterlyMilestones.length - 1 && (
                <Separator className="mt-4" />
              )}
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Supervision Interaction Summary */}
      <Card>
        <CardHeader>
          <CardTitle>Supervision Interaction Summary</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">Meeting Cadence</p>
              <p className="text-2xl font-bold">
                Every {autoData.meetingCadence ?? 14} days
              </p>
              <Badge variant={(autoData.meetingCadence ?? 14) <= 14 ? "default" : "secondary"}>
                {(autoData.meetingCadence ?? 14) <= 14 ? "Regular" : "Infrequent"}
              </Badge>
            </div>
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">Response Latency</p>
              <p className="text-2xl font-bold">
                {autoData.supervisorResponseTime} days
              </p>
              <Badge variant={autoData.supervisorResponseTime <= 3 ? "default" : "secondary"}>
                {autoData.supervisorResponseTime <= 3 ? "Responsive" : "Delayed"}
              </Badge>
            </div>
          </div>
          <p className="text-sm text-muted-foreground pt-2">
            Your supervisor maintains {(autoData.meetingCadence ?? 14) <= 14 ? "consistent" : "variable"} meeting 
            patterns with {autoData.supervisorResponseTime <= 3 ? "prompt" : "moderate"} response times. 
            This {(autoData.meetingCadence ?? 14) <= 14 && autoData.supervisorResponseTime <= 3 
              ? "supports steady research progress" 
              : "may benefit from increased interaction frequency"}.
          </p>
        </CardContent>
      </Card>

      {/* Well-being Trend */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Well-being Trend Analysis
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-3">
            {studentData.wellbeingTrend.map((trend, index) => {
              const isLatest = index === studentData.wellbeingTrend.length - 1;
              const previous = index > 0 ? studentData.wellbeingTrend[index - 1] : null;
              const delta = previous ? trend.rci - previous.rci : 0;

              return (
                <div key={index} className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                  <div className="flex items-center gap-3">
                    <span className="text-sm font-medium min-w-[80px]">{trend.quarter}</span>
                    <Badge variant={
                      trend.band === "Thriving" ? "default" : 
                      trend.band === "Vulnerable" ? "secondary" : 
                      "destructive"
                    }>
                      {trend.band}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-3">
                    {delta !== 0 && (
                      <span className={`text-xs ${delta > 0 ? "text-success" : "text-destructive"}`}>
                        {delta > 0 ? "↑" : "↓"} {Math.abs(Math.round(delta))} pts
                      </span>
                    )}
                    <span className="text-lg font-bold min-w-[60px] text-right">
                      {Math.round(trend.rci)}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
          
          <Separator />
          
          <div className="pt-2">
            <p className="text-sm text-muted-foreground">
              <strong>Summary:</strong> Your well-being scores show a {
                studentData.wellbeingTrend[studentData.wellbeingTrend.length - 1].rci > 
                studentData.wellbeingTrend[0].rci 
                  ? "positive upward trend"
                  : studentData.wellbeingTrend[studentData.wellbeingTrend.length - 1].rci < 
                    studentData.wellbeingTrend[0].rci
                  ? "declining trend that warrants attention"
                  : "stable pattern"
              } over the assessment period. {
                (results?.band === "Thriving" || results?.band === "Vulnerable")
                  ? "Continue monitoring and maintaining current support structures."
                  : "Consider discussing additional support options with your supervisor."
              }
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Privacy Note */}
      <Card className="border-muted bg-muted/30">
        <CardContent className="pt-6">
          <p className="text-sm text-muted-foreground italic">
            <strong>Privacy Note:</strong> This report contains aggregated well-being metrics and trends. 
            Individual question responses remain private and are not included in shared reports unless 
            you explicitly choose to include them.
          </p>
        </CardContent>
      </Card>
    </div>
  );
};
