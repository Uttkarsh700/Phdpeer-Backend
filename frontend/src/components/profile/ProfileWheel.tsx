import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { TrendingUp, AlertCircle, CheckCircle, AlertTriangle, Target, Sparkles } from "lucide-react";
import { Progress } from "@/components/ui/progress";
import { toast } from "sonner";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

interface WheelSegment {
  id: string;
  name: string;
  score: number;
  color: string;
}

interface ProfileWheelProps {
  data: WheelSegment[];
  onSegmentClick?: (id: string) => void;
}

export const ProfileWheel = ({ data, onSegmentClick }: ProfileWheelProps) => {
  const [selectedSegment, setSelectedSegment] = useState<WheelSegment | null>(null);
  const [hoveredSegment, setHoveredSegment] = useState<string | null>(null);

  // Calculate overall score
  const overallScore = Math.round(data.reduce((sum, seg) => sum + seg.score, 0) / data.length);

  const getScoreColor = (score: number) => {
    if (score >= 75) return "hsl(var(--success))";
    if (score >= 50) return "hsl(var(--warning))";
    return "hsl(var(--destructive))";
  };

  const getScoreGradient = (score: number) => {
    if (score >= 75) return "from-success/20 to-success/5";
    if (score >= 50) return "from-warning/20 to-warning/5";
    return "from-destructive/20 to-destructive/5";
  };

  const getScoreIcon = (score: number) => {
    if (score >= 75) return <CheckCircle className="w-5 h-5" />;
    if (score >= 50) return <AlertCircle className="w-5 h-5" />;
    return <TrendingUp className="w-5 h-5" />;
  };

  const getScoreLabel = (score: number) => {
    if (score >= 75) return "Strong";
    if (score >= 50) return "Moderate";
    return "Needs Focus";
  };

  const getPriority = (score: number): "urgent" | "attention" | "good" => {
    if (score < 50) return "urgent";
    if (score < 75) return "attention";
    return "good";
  };

  const getPriorityBadge = (priority: "urgent" | "attention" | "good") => {
    const config = {
      urgent: { label: "Urgent", color: "border-destructive/50 text-destructive", icon: AlertTriangle },
      attention: { label: "Needs Attention", color: "border-warning/50 text-warning", icon: AlertCircle },
      good: { label: "On Track", color: "border-success/50 text-success", icon: CheckCircle }
    };
    return config[priority];
  };

  const getDetailedRecommendations = (id: string, score: number): string[] => {
    const recommendations: Record<string, { good: string[], attention: string[], urgent: string[] }> = {
      academic: {
        good: [
          "Continue regular meetings with your supervisor",
          "Document your progress in weekly reports",
          "Present your work at internal seminars"
        ],
        attention: [
          "Schedule bi-weekly check-ins with supervisor",
          "Create a detailed progress timeline",
          "Identify and address any knowledge gaps"
        ],
        urgent: [
          "Book an urgent meeting with your supervisor",
          "Create a recovery plan for delayed milestones",
          "Consider adjusting your research scope"
        ]
      },
      publication: {
        good: [
          "Continue writing daily",
          "Submit to high-impact venues",
          "Collaborate on review papers"
        ],
        attention: [
          "Set daily writing goals (400-500 words)",
          "Join a writing accountability group",
          "Identify target journals for your work"
        ],
        urgent: [
          "Block dedicated writing time daily",
          "Consider splitting work into multiple papers",
          "Seek co-authors to accelerate progress"
        ]
      },
      collaboration: {
        good: [
          "Maintain regular communication",
          "Share knowledge with peers",
          "Attend departmental events"
        ],
        attention: [
          "Reach out to collaborators this week",
          "Schedule regular team meetings",
          "Document shared decisions clearly"
        ],
        urgent: [
          "Immediately address communication gaps",
          "Set up weekly sync meetings",
          "Clarify roles and expectations"
        ]
      },
      grants: {
        good: [
          "Monitor new funding opportunities",
          "Build relationships with funding bodies",
          "Track application deadlines"
        ],
        attention: [
          "Review 3-5 grant opportunities this month",
          "Attend grant writing workshops",
          "Connect with successful grant recipients"
        ],
        urgent: [
          "Apply to emergency funding options",
          "Explore teaching assistantships",
          "Consider part-time research positions"
        ]
      },
      wellbeing: {
        good: [
          "Maintain work-life balance",
          "Continue self-care practices",
          "Stay connected with support network"
        ],
        attention: [
          "Schedule regular breaks and exercise",
          "Set boundaries on work hours",
          "Talk to peers about challenges"
        ],
        urgent: [
          "Take immediate time off to recover",
          "Seek counseling or mental health support",
          "Discuss workload reduction with supervisor"
        ]
      },
      continuity: {
        good: [
          "Keep up your consistent progress",
          "Celebrate small wins regularly",
          "Share your momentum with others"
        ],
        attention: [
          "Break large tasks into weekly goals",
          "Track progress visually",
          "Identify and remove blockers"
        ],
        urgent: [
          "Restart with small, achievable tasks",
          "Create a structured daily routine",
          "Seek accountability from peers"
        ]
      }
    };

    const priority = getPriority(score);
    const priorityMap = { good: "good", attention: "attention", urgent: "urgent" } as const;
    return recommendations[id]?.[priorityMap[priority]] || [];
  };

  const handleSegmentClick = (segment: WheelSegment) => {
    setSelectedSegment(segment);
    onSegmentClick?.(segment.id);
  };

  const handleAddToTimeline = async () => {
    if (!selectedSegment) return;

    try {
      const userId = sessionStorage.getItem("userId");
      if (!userId) {
        toast.error("Please log in to add to timeline");
        return;
      }

      const priority = getPriority(selectedSegment.score);
      const recommendations = getDetailedRecommendations(selectedSegment.id, selectedSegment.score);
      const priorityConfig = getPriorityBadge(priority);

      // TODO: Replace with your backend API call
      const newEvent = {
        id: `event_${Date.now()}`,
        created_by: userId,
        event_type: 'general_note',
        summary: `${selectedSegment.name}: ${priorityConfig.label} - ${recommendations[0]}`,
        event_date: new Date().toISOString().split('T')[0],
        status: 'pending',
        created_at: new Date().toISOString(),
        participants: [],
        verifications: []
      };

      // Store in localStorage (replace with backend API)
      const storedEvents = localStorage.getItem("collaboration_events");
      const events = storedEvents ? JSON.parse(storedEvents) : [];
      events.push(newEvent);
      localStorage.setItem("collaboration_events", JSON.stringify(events));

      toast.success("Added to timeline successfully");
      setSelectedSegment(null);
      // Don't navigate - stay on current page
    } catch (error) {
      console.error('Error adding to timeline:', error);
      toast.error("Failed to add to timeline");
    }
  };

  return (
    <>
      <div className="relative">
        {/* Central Circle with Enhanced Design */}
        <div className="flex justify-center items-center mb-8">
          <div className="relative w-96 h-96">
            {/* Glow effect background */}
            <div className="absolute inset-0 rounded-full bg-gradient-to-br from-primary/10 to-accent/5 blur-2xl"></div>
            
            {/* Outer Ring - SVG-based wheel */}
            <TooltipProvider>
            <svg viewBox="0 0 200 200" className="w-full h-full relative z-10">
              {/* Outer decorative circle */}
              <circle
                cx="100"
                cy="100"
                r="95"
                fill="none"
                stroke="hsl(var(--border))"
                strokeWidth="0.5"
                opacity="0.3"
              />
              
              {/* Main wheel segments */}
              {data.map((segment, index) => {
                const angle = (360 / data.length) * index - 90;
                const nextAngle = (360 / data.length) * (index + 1) - 90;
                const startRad = (angle * Math.PI) / 180;
                const endRad = (nextAngle * Math.PI) / 180;
                
                const innerRadius = 55;
                const outerRadius = 92;
                
                const x1 = 100 + innerRadius * Math.cos(startRad);
                const y1 = 100 + innerRadius * Math.sin(startRad);
                const x2 = 100 + outerRadius * Math.cos(startRad);
                const y2 = 100 + outerRadius * Math.sin(startRad);
                const x3 = 100 + outerRadius * Math.cos(endRad);
                const y3 = 100 + outerRadius * Math.sin(endRad);
                const x4 = 100 + innerRadius * Math.cos(endRad);
                const y4 = 100 + innerRadius * Math.sin(endRad);
                
                const largeArc = 0;
                const isHovered = hoveredSegment === segment.id;
                
                return (
                  <Tooltip key={segment.id}>
                    <TooltipTrigger asChild>
                  <g>
                    {/* Segment glow on hover */}
                    {isHovered && (
                      <path
                        d={`M ${x1} ${y1} L ${x2} ${y2} A ${outerRadius + 3} ${outerRadius + 3} 0 ${largeArc} 1 ${x3} ${y3} L ${x4} ${y4} A ${innerRadius - 3} ${innerRadius - 3} 0 ${largeArc} 0 ${x1} ${y1} Z`}
                        fill={getScoreColor(segment.score)}
                        opacity="0.3"
                        filter="blur(4px)"
                      />
                    )}
                    
                    {/* Main segment */}
                    <path
                      d={`M ${x1} ${y1} L ${x2} ${y2} A ${outerRadius} ${outerRadius} 0 ${largeArc} 1 ${x3} ${y3} L ${x4} ${y4} A ${innerRadius} ${innerRadius} 0 ${largeArc} 0 ${x1} ${y1} Z`}
                      fill={getScoreColor(segment.score)}
                      opacity={isHovered ? "1" : "0.85"}
                      className="cursor-pointer transition-all duration-300"
                      onClick={() => handleSegmentClick(segment)}
                      onMouseEnter={() => setHoveredSegment(segment.id)}
                      onMouseLeave={() => setHoveredSegment(null)}
                      style={{
                        transform: isHovered ? 'scale(1.05)' : 'scale(1)',
                        transformOrigin: '100px 100px'
                      }}
                    />
                    
                    {/* Score text */}
                    <text
                      x={100 + 73 * Math.cos((angle + nextAngle) / 2 * Math.PI / 180)}
                      y={100 + 73 * Math.sin((angle + nextAngle) / 2 * Math.PI / 180)}
                      textAnchor="middle"
                      dominantBaseline="middle"
                      fill="white"
                      fontSize={isHovered ? "18" : "16"}
                      fontWeight="bold"
                      className="pointer-events-none select-none transition-all duration-300"
                      style={{ filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.5))' }}
                    >
                      {segment.score}
                    </text>
                  </g>
                  </TooltipTrigger>
                  <TooltipContent>
                    <div className="text-center">
                      <p className="font-semibold">{segment.name}</p>
                      <p className="text-xs text-muted-foreground">Score: {segment.score} - {getScoreLabel(segment.score)}</p>
                    </div>
                  </TooltipContent>
                  </Tooltip>
                );
              })}
              
              {/* Center Circle with gradient */}
              <defs>
                <linearGradient id="centerGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="hsl(var(--card))" />
                  <stop offset="100%" stopColor="hsl(var(--background))" />
                </linearGradient>
              </defs>
              <circle
                cx="100"
                cy="100"
                r="52"
                fill="url(#centerGradient)"
                stroke="hsl(var(--primary))"
                strokeWidth="2"
                opacity="0.8"
              />
              
              {/* Overall score display */}
              <text
                x="100"
                y="90"
                textAnchor="middle"
                fill="hsl(var(--foreground))"
                fontSize="32"
                fontWeight="bold"
                style={{ filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.3))' }}
              >
                {overallScore}
              </text>
              <text
                x="100"
                y="105"
                textAnchor="middle"
                fill="hsl(var(--muted-foreground))"
                fontSize="12"
                fontWeight="500"
              >
                Overall Score
              </text>
              <text
                x="100"
                y="120"
                textAnchor="middle"
                fill={getScoreColor(overallScore)}
                fontSize="11"
                fontWeight="600"
              >
                {getScoreLabel(overallScore)}
              </text>
            </svg>
            </TooltipProvider>
          </div>
        </div>

        {/* Priority Recommendations Section */}
        <div className="space-y-4">
          <div className="flex items-center gap-2 mb-4">
            <Target className="w-5 h-5 text-primary" />
            <h3 className="text-lg font-semibold text-foreground">Recommended Focus Areas</h3>
          </div>
          
          <div className="space-y-3">
            {data
              .sort((a, b) => a.score - b.score)
              .slice(0, 3)
              .map((segment) => {
                const priority = getPriority(segment.score);
                const badge = getPriorityBadge(priority);
                const Icon = badge.icon;
                
                return (
                  <Card 
                    key={segment.id}
                    className="p-4 bg-card/50 border-border/50 hover:border-primary/50 transition-all duration-300 cursor-pointer group"
                    onClick={() => handleSegmentClick(segment)}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex-1 space-y-2">
                        <div className="flex items-center gap-2">
                          <div 
                            className="w-3 h-3 rounded-full" 
                            style={{ backgroundColor: getScoreColor(segment.score) }}
                          />
                          <span className="font-medium text-foreground">{segment.name}</span>
                          <Badge variant="outline" className={badge.color}>
                            <Icon className="w-3 h-3 mr-1" />
                            {badge.label}
                          </Badge>
                        </div>
                        <div className="flex items-center gap-2">
                          <Progress value={segment.score} className="h-1.5 flex-1" />
                          <span className="text-sm font-semibold text-muted-foreground min-w-[3rem]">
                            {segment.score}/100
                          </span>
                        </div>
                        <p className="text-sm text-muted-foreground">
                          {getDetailedRecommendations(segment.id, segment.score)[0]}
                        </p>
                      </div>
                      <Sparkles className="w-4 h-4 text-primary opacity-0 group-hover:opacity-100 transition-opacity" />
                    </div>
                  </Card>
                );
              })}
          </div>
        </div>
      </div>

      {/* Enhanced Segment Detail Modal */}
      <Dialog open={!!selectedSegment} onOpenChange={() => setSelectedSegment(null)}>
        <DialogContent className="bg-card border-border max-w-lg">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-3 text-foreground">
              {selectedSegment && (
                <>
                  <div className="relative">
                    <div 
                      className="w-5 h-5 rounded-full" 
                      style={{ backgroundColor: getScoreColor(selectedSegment.score) }}
                    />
                    <div 
                      className="absolute inset-0 w-5 h-5 rounded-full animate-pulse"
                      style={{ backgroundColor: getScoreColor(selectedSegment.score), opacity: 0.3 }}
                    />
                  </div>
                  <span className="text-xl">{selectedSegment.name}</span>
                </>
              )}
            </DialogTitle>
            <DialogDescription className="text-muted-foreground">
              Detailed analysis and recommendations
            </DialogDescription>
          </DialogHeader>
          {selectedSegment && (
            <div className="space-y-5 pt-4">
              {/* Score display with priority badge */}
              <div className={`p-5 bg-gradient-to-br ${getScoreGradient(selectedSegment.score)} rounded-xl border border-border/50`}>
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div style={{ color: getScoreColor(selectedSegment.score) }}>
                      {getScoreIcon(selectedSegment.score)}
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground mb-1">Current Score</p>
                      <p className="text-3xl font-bold text-foreground">{selectedSegment.score}</p>
                    </div>
                  </div>
                  <Badge 
                    variant="outline" 
                    className={getPriorityBadge(getPriority(selectedSegment.score)).color}
                  >
                    {(() => {
                      const badge = getPriorityBadge(getPriority(selectedSegment.score));
                      const Icon = badge.icon;
                      return (
                        <>
                          <Icon className="w-3 h-3 mr-1" />
                          {badge.label}
                        </>
                      );
                    })()}
                  </Badge>
                </div>
                <Progress value={selectedSegment.score} className="h-2" />
              </div>
              
              {/* Detailed recommendations */}
              <div className="space-y-3">
                <p className="text-sm font-semibold text-foreground flex items-center gap-2">
                  <Target className="w-4 h-4 text-primary" />
                  Action Plan
                </p>
                <div className="space-y-2">
                  {getDetailedRecommendations(selectedSegment.id, selectedSegment.score).map((rec, idx) => (
                    <div 
                      key={idx}
                      className="flex items-start gap-2 p-3 bg-background/50 rounded-lg border border-border/30 hover:border-primary/50 transition-colors"
                    >
                      <div className="mt-0.5">
                        <div className="w-1.5 h-1.5 rounded-full bg-primary" />
                      </div>
                      <p className="text-sm text-foreground leading-relaxed flex-1">
                        {rec}
                      </p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Action button */}
              <Button 
                onClick={handleAddToTimeline}
                className="w-full bg-gradient-to-r from-[#FF7A18] to-[#FFB800] hover:opacity-90 text-white shadow-lg hover:shadow-xl transition-all duration-300"
              >
                Add to Timeline
              </Button>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </>
  );
};
