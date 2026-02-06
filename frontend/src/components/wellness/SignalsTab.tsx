import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Clock, Target, TrendingUp } from "lucide-react";
import { CalculationResults } from "@/lib/wellnessCalculations";

interface SignalsTabProps {
  results: CalculationResults | null;
  autoData: {
    milestoneCompletion: number;
    avgDelay: number;
    supervisorResponseTime: number;
    meetingCadence?: number;
    opportunitiesAdded?: number;
  };
}

export const SignalsTab = ({ results, autoData }: SignalsTabProps) => {
  const meetingCadence = autoData.meetingCadence ?? 14; // days between meetings
  const opportunitiesAdded = autoData.opportunitiesAdded ?? 8; // last 90 days

  return (
    <div className="space-y-6">
      {/* Milestone Velocity */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5 text-wellness-progress" />
            Milestone Velocity
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">Completion Rate</span>
            <div className="flex items-center gap-2">
              <span className="text-2xl font-bold">{autoData.milestoneCompletion}%</span>
              {/* TODO: Replace with backend-provided status from AnalyticsSummary */}
              {/* Status should come from backend, not computed here */}
              <Badge variant="default">
                {/* Backend-provided status indicator */}
                Status
              </Badge>
            </div>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">Mean Lateness</span>
            <div className="flex items-center gap-2">
              <span className="text-2xl font-bold">{autoData.avgDelay} days</span>
              {/* TODO: Replace with backend-provided status from AnalyticsSummary */}
              {/* Status should come from backend, not computed here */}
              <Badge variant="default">
                {/* Backend-provided status indicator */}
                Status
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Supervisor Latency */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5 text-wellness-supervision" />
            Supervisor Latency
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">Median Response Time</span>
            <div className="flex items-center gap-2">
              <span className="text-2xl font-bold">{autoData.supervisorResponseTime} days</span>
              {/* TODO: Replace with backend-provided status from AnalyticsSummary */}
              {/* Status should come from backend, not computed here */}
              <Badge variant="default">
                {/* Backend-provided status indicator */}
                Status
              </Badge>
            </div>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">Meeting Cadence</span>
            <div className="flex items-center gap-2">
              <span className="text-2xl font-bold">Every {meetingCadence} days</span>
              {/* TODO: Replace with backend-provided status from AnalyticsSummary */}
              {/* Status should come from backend, not computed here */}
              <Badge variant="default">
                {/* Backend-provided status indicator */}
                Status
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Opportunity Flow */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-wellness-career" />
            Opportunity Flow
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">CFPs/Conferences/Grants (90d)</span>
            <div className="flex items-center gap-2">
              <span className="text-2xl font-bold">{opportunitiesAdded}</span>
              {/* TODO: Replace with backend-provided status from AnalyticsSummary */}
              {/* Status should come from backend, not computed here */}
              <Badge variant="default">
                {/* Backend-provided status indicator */}
                Status
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* JD-R Bar: RI vs DI */}
      {results && (
        <Card>
          <CardHeader>
            <CardTitle>Job Demands-Resources Balance</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-muted-foreground">Research Index (RI)</span>
                  <span className="font-medium">{Math.round(results.RI)}</span>
                </div>
                <div className="h-8 bg-muted rounded-lg overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-info to-info/80 flex items-center justify-end px-3 transition-all"
                    style={{ width: `${results.RI}%` }}
                  >
                    <span className="text-xs font-medium text-info-foreground">
                      {Math.round(results.RI)}
                    </span>
                  </div>
                </div>
              </div>

              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-muted-foreground">Development Index (DI)</span>
                  <span className="font-medium">{Math.round(results.DI)}</span>
                </div>
                <div className="h-8 bg-muted rounded-lg overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-success to-success/80 flex items-center justify-end px-3 transition-all"
                    style={{ width: `${results.DI}%` }}
                  >
                    <span className="text-xs font-medium text-success-foreground">
                      {Math.round(results.DI)}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <div className="pt-2 text-sm text-muted-foreground">
              {results.RI > results.DI ? (
                <p>Research demands slightly exceed development resources.</p>
              ) : results.DI > results.RI ? (
                <p>Development resources support your research demands well.</p>
              ) : (
                <p>Research demands and development resources are balanced.</p>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
