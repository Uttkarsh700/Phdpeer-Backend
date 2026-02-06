import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { 
  Plus, 
  Eye, 
  HelpCircle, 
  Award, 
  TrendingUp, 
  FileText,
  Target,
  Sparkles,
  ArrowUpRight,
  ArrowDownRight,
  Minus
} from "lucide-react";
import { format } from "date-fns";
import { 
  loadProfile, 
  WRITING_ASPECTS, 
  MATURITY_LEVELS,
  type WritingProfile,
  type AspectEvaluation
} from "@/lib/writingEvolutionTypes";
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid } from "recharts";

const WritingEvolution = () => {
  const navigate = useNavigate();
  const [profile, setProfile] = useState<WritingProfile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loaded = loadProfile();
    setProfile(loaded);
    setLoading(false);
  }, []);

  const hasBaseline = profile?.baseline !== null;
  const submissionCount = profile?.submissions?.length || 0;
  const latestSubmission = profile?.submissions?.[profile.submissions.length - 1];
  
  // Get current aspects (from latest submission or baseline)
  const currentAspects = latestSubmission?.aspects || profile?.baseline?.aspects || [];
  const baselineAspects = profile?.baseline?.aspects || [];
  
  // Calculate overall level
  const currentOverallLevel = currentAspects.length > 0 
    ? Math.round(currentAspects.reduce((sum, a) => sum + a.level, 0) / currentAspects.length)
    : 0;

  // Prepare radar chart data
  const radarData = WRITING_ASPECTS.map(aspect => {
    const current = currentAspects.find(a => a.aspectId === aspect.id);
    const baseline = baselineAspects.find(a => a.aspectId === aspect.id);
    return {
      aspect: aspect.name.split(' ')[0], // First word only for chart
      fullName: aspect.name,
      current: current?.level || 0,
      baseline: baseline?.level || 0,
      max: 5
    };
  });

  // Prepare timeline data
  const timelineData = [
    ...(profile?.baseline ? [{ 
      name: 'Baseline', 
      date: format(new Date(profile.baseline.createdAt), 'MMM d'),
      level: profile.baseline.overallLevel 
    }] : []),
    ...(profile?.submissions?.map((s, i) => ({
      name: `Submission ${i + 1}`,
      date: format(new Date(s.createdAt), 'MMM d'),
      level: s.overallLevel
    })) || [])
  ];

  // Calculate top improvements and weaknesses
  const getTopChanges = () => {
    if (!latestSubmission || !profile?.baseline) return { improvements: [], weaknesses: [] };
    
    const changes = currentAspects.map(current => {
      const baseline = baselineAspects.find(b => b.aspectId === current.aspectId);
      const aspectInfo = WRITING_ASPECTS.find(a => a.id === current.aspectId);
      return {
        name: aspectInfo?.name || current.aspectId,
        change: current.level - (baseline?.level || 0),
        currentLevel: current.level
      };
    }).sort((a, b) => b.change - a.change);

    return {
      improvements: changes.filter(c => c.change > 0).slice(0, 2),
      weaknesses: changes.filter(c => c.change <= 0).slice(-2).reverse()
    };
  };

  const { improvements, weaknesses } = getTopChanges();

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-foreground">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-7xl mx-auto px-4 py-12">
        {/* Header */}
        <div className="mb-10">
          <h1 className="text-3xl md:text-4xl font-bold text-foreground mb-2">
            Writing Baseline & Authorship Continuity
          </h1>
          <p className="text-muted-foreground text-lg">
            Document your academic writing development and build a verified writing trail
          </p>
        </div>

        {!hasBaseline ? (
          /* No Baseline State */
          <Card className="bg-card border-border/50 max-w-2xl mx-auto">
            <CardContent className="p-12 text-center">
              <div className="w-20 h-20 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-6">
                <Target className="w-10 h-10 text-primary" />
              </div>
              <h2 className="text-2xl font-semibold text-foreground mb-3">
                Establish Your Writing Baseline
              </h2>
              <p className="text-muted-foreground mb-8 max-w-md mx-auto">
                Create a verified authorship profile using existing writing samples or by writing directly in-app. 
                Build a documented writing trail throughout your research journey.
              </p>
              <Button 
                onClick={() => navigate('/writing-evolution/baseline')}
                size="lg"
                className="bg-primary hover:bg-primary/90"
              >
                <Plus className="w-5 h-5 mr-2" />
                Create Baseline
              </Button>
            </CardContent>
          </Card>
        ) : (
          <>
            {/* Top Summary Row */}
            <div className="grid md:grid-cols-4 gap-6 mb-8">
              {/* Overall Maturity Level */}
              <Card className="bg-card border-border/50">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                    <Sparkles className="w-4 h-4" />
                    Writing Maturity
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-3">
                    <span className="text-3xl font-bold text-foreground">
                      {MATURITY_LEVELS[currentOverallLevel - 1]?.name || 'N/A'}
                    </span>
                  </div>
                  <p className="text-xs text-muted-foreground mt-2">
                    Level {currentOverallLevel} of 5
                  </p>
                </CardContent>
              </Card>

              {/* Submissions Count */}
              <Card className="bg-card border-border/50">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                    <FileText className="w-4 h-4" />
                    Submissions
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <span className="text-3xl font-bold text-foreground">{submissionCount + 1}</span>
                  <p className="text-xs text-muted-foreground mt-2">
                    Including baseline
                  </p>
                </CardContent>
              </Card>

              {/* Badges Earned */}
              <Card className="bg-card border-border/50">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                    <Award className="w-4 h-4" />
                    Badges Earned
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <span className="text-3xl font-bold text-foreground">
                    {currentAspects.reduce((sum, a) => sum + a.badges.filter(b => b.level > 0).length, 0)}
                  </span>
                  <p className="text-xs text-muted-foreground mt-2">
                    of {WRITING_ASPECTS.reduce((sum, a) => sum + a.badges.length, 0)} total
                  </p>
                </CardContent>
              </Card>

              {/* Continuity Record Status */}
              <Card className="bg-card border-border/50">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                    <TrendingUp className="w-4 h-4" />
                    Continuity Record
                    <Tooltip>
                      <TooltipTrigger>
                        <HelpCircle className="w-3.5 h-3.5 text-muted-foreground/60" />
                      </TooltipTrigger>
                      <TooltipContent className="max-w-xs bg-popover border-border">
                        <p className="text-sm">
                          Complete at least 5 submissions to generate your Authorship Continuity & Writing Evolution Record — 
                          a documented trail of your academic writing development.
                        </p>
                      </TooltipContent>
                    </Tooltip>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {submissionCount >= 4 ? (
                    <Badge className="bg-emerald-500/20 text-emerald-500 border-emerald-500/30">
                      Eligible
                    </Badge>
                  ) : (
                    <>
                      <span className="text-sm text-muted-foreground">
                        {5 - submissionCount - 1} more submissions needed
                      </span>
                      <Progress value={(submissionCount + 1) / 5 * 100} className="h-2 mt-2" />
                    </>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* Main Content Grid */}
            <div className="grid lg:grid-cols-3 gap-8 mb-8">
              {/* Radar Chart */}
              <Card className="bg-card border-border/50 lg:col-span-2">
                <CardHeader>
                  <CardTitle className="text-lg font-semibold text-foreground">
                    7-Aspect Writing Profile
                  </CardTitle>
                  <CardDescription>
                    {submissionCount > 0 ? 'Current vs Baseline comparison' : 'Your baseline profile'}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <RadarChart data={radarData}>
                        <PolarGrid stroke="hsl(var(--border))" />
                        <PolarAngleAxis 
                          dataKey="aspect" 
                          tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 11 }}
                        />
                        <PolarRadiusAxis 
                          angle={30} 
                          domain={[0, 5]} 
                          tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 10 }}
                        />
                        {submissionCount > 0 && (
                          <Radar
                            name="Baseline"
                            dataKey="baseline"
                            stroke="hsl(var(--muted-foreground))"
                            fill="hsl(var(--muted-foreground))"
                            fillOpacity={0.1}
                            strokeDasharray="5 5"
                          />
                        )}
                        <Radar
                          name="Current"
                          dataKey="current"
                          stroke="hsl(var(--primary))"
                          fill="hsl(var(--primary))"
                          fillOpacity={0.3}
                        />
                      </RadarChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>

              {/* Changes Summary */}
              <Card className="bg-card border-border/50">
                <CardHeader>
                  <CardTitle className="text-lg font-semibold text-foreground">
                    {submissionCount > 0 ? 'Evolution Summary' : 'Next Steps'}
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  {submissionCount > 0 ? (
                    <>
                      {/* Top Improvements */}
                      <div>
                        <h4 className="text-sm font-medium text-muted-foreground mb-3 flex items-center gap-2">
                          <ArrowUpRight className="w-4 h-4 text-emerald-500" />
                          Top Improvements
                        </h4>
                        <div className="space-y-2">
                          {improvements.length > 0 ? improvements.map((imp, i) => (
                            <div key={i} className="flex items-center justify-between text-sm">
                              <span className="text-foreground">{imp.name}</span>
                              <Badge variant="outline" className="text-emerald-500 border-emerald-500/30">
                                +{imp.change} level
                              </Badge>
                            </div>
                          )) : (
                            <p className="text-sm text-muted-foreground">Submit more to see trends</p>
                          )}
                        </div>
                      </div>

                      {/* Areas to Focus */}
                      <div>
                        <h4 className="text-sm font-medium text-muted-foreground mb-3 flex items-center gap-2">
                          <ArrowDownRight className="w-4 h-4 text-amber-500" />
                          Areas to Focus
                        </h4>
                        <div className="space-y-2">
                          {weaknesses.length > 0 ? weaknesses.map((weak, i) => (
                            <div key={i} className="flex items-center justify-between text-sm">
                              <span className="text-foreground">{weak.name}</span>
                              <Badge variant="outline" className="text-amber-500 border-amber-500/30">
                                {weak.change === 0 ? 'Stable' : `${weak.change} level`}
                              </Badge>
                            </div>
                          )) : (
                            <p className="text-sm text-muted-foreground">All areas improving</p>
                          )}
                        </div>
                      </div>
                    </>
                  ) : (
                    <div className="space-y-4">
                      <p className="text-sm text-muted-foreground">
                        Submit your writing regularly to build a documented authorship trail.
                      </p>
                      <ul className="text-sm space-y-2">
                        <li className="flex items-start gap-2">
                          <Minus className="w-4 h-4 text-primary mt-0.5" />
                          <span className="text-muted-foreground">Submit weekly or at milestones</span>
                        </li>
                        <li className="flex items-start gap-2">
                          <Minus className="w-4 h-4 text-primary mt-0.5" />
                          <span className="text-muted-foreground">Build longitudinal evidence of authorship</span>
                        </li>
                        <li className="flex items-start gap-2">
                          <Minus className="w-4 h-4 text-primary mt-0.5" />
                          <span className="text-muted-foreground">Generate your continuity record</span>
                        </li>
                      </ul>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* Timeline */}
            {timelineData.length > 1 && (
              <Card className="bg-card border-border/50 mb-8">
                <CardHeader>
                  <CardTitle className="text-lg font-semibold text-foreground">
                    Writing Development Timeline
                  </CardTitle>
                  <CardDescription>
                    Documented evolution of your writing maturity over time
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="h-48">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={timelineData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                        <XAxis 
                          dataKey="date" 
                          tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }}
                        />
                        <YAxis 
                          domain={[1, 5]} 
                          ticks={[1, 2, 3, 4, 5]}
                          tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }}
                        />
                        <Line 
                          type="monotone" 
                          dataKey="level" 
                          stroke="hsl(var(--primary))" 
                          strokeWidth={2}
                          dot={{ fill: 'hsl(var(--primary))', strokeWidth: 2 }}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* 7 Aspects Detail Grid */}
            <div className="mb-8">
              <h2 className="text-xl font-semibold text-foreground mb-4">Aspect Details</h2>
              <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {WRITING_ASPECTS.map(aspect => {
                  const evaluation = currentAspects.find(a => a.aspectId === aspect.id);
                  const level = evaluation?.level || 0;
                  const maturityInfo = MATURITY_LEVELS[level - 1];
                  const earnedBadges = evaluation?.badges.filter(b => b.level > 0).length || 0;

                  return (
                    <Card key={aspect.id} className="bg-card border-border/50 hover:border-primary/50 transition-colors">
                      <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium text-foreground">
                          {aspect.name}
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="flex items-center justify-between mb-2">
                          <Badge 
                            variant="outline" 
                            className={maturityInfo?.color || 'text-muted-foreground'}
                          >
                            {maturityInfo?.name || 'Not assessed'}
                          </Badge>
                          <span className="text-xs text-muted-foreground">
                            {earnedBadges}/{aspect.badges.length} badges
                          </span>
                        </div>
                        <Progress value={level * 20} className="h-2" />
                        {evaluation && (
                          <p className="text-xs text-muted-foreground mt-3">
                            {evaluation.strengths[0]}
                          </p>
                        )}
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-wrap gap-4">
              <Button 
                onClick={() => navigate('/writing-evolution/checkpoint')}
                className="bg-primary hover:bg-primary/90"
              >
                <Plus className="w-4 h-4 mr-2" />
                New Submission
              </Button>
              {submissionCount > 0 && (
                <Button 
                  variant="outline"
                  onClick={() => navigate(`/writing-evolution/report/${latestSubmission?.id}`)}
                  className="border-border hover:border-primary"
                >
                  <Eye className="w-4 h-4 mr-2" />
                  View Latest Report
                </Button>
              )}
              {submissionCount >= 4 && (
                <Button 
                  variant="outline"
                  onClick={() => navigate('/writing-evolution/certificate')}
                  className="border-emerald-500/50 text-emerald-500 hover:bg-emerald-500/10"
                >
                  <Award className="w-4 h-4 mr-2" />
                  View Continuity Record
                </Button>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default WritingEvolution;
