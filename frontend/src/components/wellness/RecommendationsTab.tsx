import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { 
  AlertTriangle, 
  Calendar, 
  CheckCircle2, 
  Target, 
  Users, 
  FileText,
  TrendingUp,
  Rocket,
  Lightbulb,
  Coffee,
  BookOpen,
  Briefcase
} from "lucide-react";
import { toast } from "sonner";
import { useNavigate } from "react-router-dom";
import { CalculationResults } from "@/lib/wellnessCalculations";

interface RecommendationsTabProps {
  results: CalculationResults | null;
}

interface Action {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  priority: "high" | "medium" | "low";
  category: string;
}

export const RecommendationsTab = ({ results }: RecommendationsTabProps) => {
  const navigate = useNavigate();
  
  if (!results) {
    return (
      <Card>
        <CardContent className="pt-6">
          <p className="text-muted-foreground text-center">
            Complete your well-being check-in to receive personalized recommendations.
          </p>
        </CardContent>
      </Card>
    );
  }

  const rci = results.RCI;

  // TODO: Replace with backend-provided recommendations from JourneyAssessment
  // REMOVED: All frontend decision-making logic
  // Recommendations should come from backend, not computed here
  // 
  // Example backend integration:
  // const assessment = await get<JourneyAssessment>('/doctor/latest');
  // const recommendations = assessment.action_items; // Backend-provided
  // const alert = assessment.challenges; // Backend-provided
  // const type = assessment.assessment_type; // Backend-provided
  
  // Placeholder - returns empty until backend integration
  // Backend should provide all recommendations, not frontend
  const getRecommendations = (): { type: string; actions: Action[]; alert?: { title: string; description: string } } => {
    // REMOVED: All frontend decision-making based on RCI score thresholds
    // Backend should provide recommendations, not frontend
    return {
      type: "Backend-provided recommendations", // Will come from JourneyAssessment
      actions: [], // Will come from JourneyAssessment.action_items
      alert: undefined, // Will come from JourneyAssessment.challenges
    };
  };

  const recommendations = getRecommendations();
  const topTwoActions = recommendations.actions.slice(0, 2);

  const handleSyncToCalendar = () => {
    toast.success("Creating calendar events...", {
      description: `Adding "${topTwoActions[0].title}" and "${topTwoActions[1].title}" to your Google Calendar.`,
    });
    
    // In a real implementation, this would:
    // 1. Authenticate with Google Calendar API (requires Cloud/backend)
    // 2. Create calendar events for the top 2 actions
    // 3. Set appropriate dates and reminders
    
    setTimeout(() => {
      toast.success("Calendar events created!", {
        description: "Check your Google Calendar for the scheduled actions.",
      });
    }, 1500);
  };

  return (
    <div className="space-y-6">
      {/* Header with Calendar Sync */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold">{recommendations.type}</h3>
          <p className="text-sm text-muted-foreground">
            RCI Score: {Math.round(rci)} - {results.band}
          </p>
        </div>
        <Button onClick={handleSyncToCalendar} variant="default" className="bg-gradient-to-r from-[#DB5614] to-[#E69219] hover:opacity-90">
          <Calendar className="mr-2 h-4 w-4" />
          Add All to Google Calendar
        </Button>
      </div>

      {/* Risk Alert (if applicable) */}
      {recommendations.alert && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>{recommendations.alert.title}</AlertTitle>
          <AlertDescription>{recommendations.alert.description}</AlertDescription>
        </Alert>
      )}

      {/* Top Priority Actions (top 2 for calendar sync) */}
      {topTwoActions.length > 0 && (
        <Card className="border-primary/50 bg-primary/5">
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <CheckCircle2 className="h-5 w-5 text-primary" />
              Priority Actions (Will be added to calendar)
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {topTwoActions.map((action, index) => (
              <div key={action.id} className="flex gap-4 p-4 rounded-lg bg-background border">
                <div className="mt-1" style={{ color: '#DB5614' }}>
                  {action.icon}
                </div>
                <div className="flex-1 space-y-2">
                  <div className="flex items-start justify-between gap-2">
                    <h4 className="font-semibold">{action.title}</h4>
                    <Badge variant={action.priority === "high" ? "destructive" : "default"}>
                      {action.priority}
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground">{action.description}</p>
                  <p className="text-xs text-muted-foreground">
                    Category: {action.category}
                  </p>
                  {action.id === "peer-support" && (
                    <div className="mt-3 space-y-2">
                      <Button 
                        onClick={() => navigate('/network')} 
                        className="w-full bg-gradient-to-r from-[#DB5614] to-[#E69219] hover:opacity-90"
                      >
                        Open Peer Network
                      </Button>
                      <p className="text-xs text-muted-foreground">
                        Find peers, mentors, and collaborators instantly via Frensei's AI-matched Peer Network.
                      </p>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Additional Actions */}
      {recommendations.actions.length > 2 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Additional Recommended Actions</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {recommendations.actions.slice(2).map((action) => (
              <div 
                key={action.id} 
                className={`flex gap-4 p-4 rounded-lg relative ${
                  action.id === "editage-manuscript" 
                    ? "bg-[#1C1C1C] border border-muted/30" 
                    : "bg-muted/50"
                }`}
              >
                {action.id === "editage-manuscript" && (
                  <span className="absolute top-3 right-3 text-[12px] text-[#AAAAAA]">
                    Verified Partner
                  </span>
                )}
                <div className="text-muted-foreground mt-1">
                  {action.icon}
                </div>
                <div className="flex-1 space-y-2">
                  <div className="flex items-start justify-between gap-2">
                    <h4 className="font-semibold">{action.title}</h4>
                    <Badge variant="outline">
                      {action.priority}
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground">{action.description}</p>
                  <p className="text-xs text-muted-foreground">
                    Category: {action.category}
                  </p>
                  {action.id === "editage-manuscript" && (
                    <Button 
                      variant="outline" 
                      size="sm" 
                      className="mt-2"
                      onClick={() => window.open('https://www.editage.com/', '_blank')}
                    >
                      Learn More
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Info Note */}
      <Card className="border-muted bg-muted/30">
        <CardContent className="pt-6">
          <div className="flex gap-3">
            <Coffee className="h-5 w-5 text-muted-foreground flex-shrink-0 mt-0.5" />
            <div className="space-y-2">
              <p className="text-sm font-medium">Taking Action</p>
              <p className="text-sm text-muted-foreground">
                These recommendations are personalized based on your current RCI score and research stage. 
                Start with the priority actions and adjust based on your specific circumstances. 
                The calendar sync feature will help you commit to these actions by scheduling them in your Google Calendar.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
