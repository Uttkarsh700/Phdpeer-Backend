import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowUp, ArrowDown, Minus, TrendingUp, TrendingDown } from "lucide-react";
import { CalculationResults, getBandColor } from "@/lib/wellnessCalculations";
import { cn } from "@/lib/utils";

interface ResultsCardProps {
  results: CalculationResults;
}

export const ResultsCard = ({ results }: ResultsCardProps) => {
  const bandColor = getBandColor(results.band);
  const trendIcon = results.rciDelta
    ? results.rciDelta > 5
      ? TrendingUp
      : results.rciDelta < -5
      ? TrendingDown
      : Minus
    : null;

  const TrendIcon = trendIcon;

  return (
    <div className="space-y-6">
      {/* Main RCI Score Card */}
      <Card className="border-2" style={{ borderColor: bandColor }}>
        <CardHeader>
          <CardTitle className="text-2xl">Research Climate Index (RCI)</CardTitle>
          <CardDescription>
            Your overall well-being assessment based on this quarter's responses
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="space-y-2">
              <div className="flex items-baseline gap-3">
                <span className="text-6xl font-bold" style={{ color: bandColor }}>
                  {Math.round(results.RCI)}
                </span>
                <span className="text-2xl text-muted-foreground">/100</span>
              </div>
              <div className="flex items-center gap-2">
                <div
                  className="px-4 py-2 rounded-full font-semibold text-sm"
                  style={{ backgroundColor: bandColor, color: "white" }}
                >
                  {results.band}
                </div>
                {results.rciDelta !== undefined && TrendIcon && (
                  <div
                    className={cn(
                      "flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium",
                      results.rciDelta > 0 ? "bg-success/10 text-success" : 
                      results.rciDelta < 0 ? "bg-destructive/10 text-destructive" :
                      "bg-muted text-muted-foreground"
                    )}
                  >
                    <TrendIcon className="w-4 h-4" />
                    <span>
                      {results.rciDelta > 0 ? "+" : ""}
                      {Math.round(results.rciDelta)} vs last quarter
                    </span>
                  </div>
                )}
              </div>
            </div>
            
            {/* Ring visualization */}
            <div className="relative w-32 h-32">
              <svg width="128" height="128" className="transform -rotate-90">
                <circle
                  cx="64"
                  cy="64"
                  r="56"
                  fill="none"
                  stroke="hsl(var(--muted))"
                  strokeWidth="12"
                />
                <circle
                  cx="64"
                  cy="64"
                  r="56"
                  fill="none"
                  stroke={bandColor}
                  strokeWidth="12"
                  strokeDasharray={2 * Math.PI * 56}
                  strokeDashoffset={2 * Math.PI * 56 * (1 - results.RCI / 100)}
                  strokeLinecap="round"
                  className="transition-all duration-1000"
                />
              </svg>
            </div>
          </div>

          {/* Band descriptions */}
          <div className="space-y-2 text-sm">
            <p className="font-medium">Understanding your score:</p>
            <ul className="space-y-1 text-muted-foreground">
              <li className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-success" />
                <span><strong>Thriving (70-100):</strong> Excellent research climate and well-being</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-warning" />
                <span><strong>Vulnerable (40-69):</strong> Some challenges present, support recommended</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-destructive" />
                <span><strong>At-Risk (0-39):</strong> Significant concerns, immediate support needed</span>
              </li>
            </ul>
          </div>
        </CardContent>
      </Card>

      {/* Component Indices */}
      <div className="grid md:grid-cols-2 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg">Research Index (RI)</CardTitle>
            <CardDescription>Research-focused dimensions</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-baseline gap-2">
              <span className="text-4xl font-bold text-primary">
                {Math.round(results.RI)}
              </span>
              <span className="text-lg text-muted-foreground">/100</span>
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              Supervision, Progress, Clarity, Workload
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg">Development Index (DI)</CardTitle>
            <CardDescription>Personal development dimensions</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-baseline gap-2">
              <span className="text-4xl font-bold text-accent">
                {Math.round(results.DI)}
              </span>
              <span className="text-lg text-muted-foreground">/100</span>
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              Funding, Support, Well-being, Career
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Dimensional Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Dimensional Breakdown</CardTitle>
          <CardDescription>Individual dimension scores (0-100)</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: "Supervision", value: results.D1, color: "hsl(var(--wellness-supervision))" },
              { label: "Progress", value: results.D2, color: "hsl(var(--wellness-progress))" },
              { label: "Clarity", value: results.D3, color: "hsl(var(--wellness-clarity))" },
              { label: "Workload", value: results.D4, color: "hsl(var(--wellness-workload))" },
              { label: "Funding", value: results.D5, color: "hsl(var(--wellness-funding))" },
              { label: "Support", value: results.D6, color: "hsl(var(--wellness-support))" },
              { label: "Well-being", value: results.D7, color: "hsl(var(--wellness-wellbeing))" },
              { label: "Career", value: results.D8, color: "hsl(var(--wellness-career))" },
            ].map((dim) => (
              <div key={dim.label} className="flex flex-col items-center gap-2">
                <div className="relative w-16 h-16">
                  <svg width="64" height="64" className="transform -rotate-90">
                    <circle
                      cx="32"
                      cy="32"
                      r="28"
                      fill="none"
                      stroke="hsl(var(--muted))"
                      strokeWidth="6"
                    />
                    <circle
                      cx="32"
                      cy="32"
                      r="28"
                      fill="none"
                      stroke={dim.color}
                      strokeWidth="6"
                      strokeDasharray={2 * Math.PI * 28}
                      strokeDashoffset={2 * Math.PI * 28 * (1 - dim.value / 100)}
                      strokeLinecap="round"
                      className="transition-all duration-1000"
                    />
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-xs font-semibold">{Math.round(dim.value)}</span>
                  </div>
                </div>
                <span className="text-xs font-medium text-center">{dim.label}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
