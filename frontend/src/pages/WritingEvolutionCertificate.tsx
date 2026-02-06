import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { 
  ArrowLeft, 
  Download, 
  Shield, 
  FileCheck,
  CalendarDays,
  TrendingUp,
  Award,
  Info,
  ChevronDown,
  CheckCircle2,
  Clock,
  Layers
} from "lucide-react";
import { format, differenceInDays } from "date-fns";
import { 
  loadProfile, 
  WRITING_ASPECTS, 
  MATURITY_LEVELS,
  type WritingProfile
} from "@/lib/writingEvolutionTypes";
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer } from "recharts";

const WritingEvolutionCertificate = () => {
  const navigate = useNavigate();
  const [profile, setProfile] = useState<WritingProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [infoOpen, setInfoOpen] = useState(false);

  useEffect(() => {
    const loaded = loadProfile();
    setProfile(loaded);
    setLoading(false);
  }, []);

  const submissionCount = (profile?.submissions?.length || 0) + 1; // +1 for baseline
  const isEligible = submissionCount >= 5;

  // Calculate time span
  const getTimeSpan = () => {
    if (!profile?.baseline || !profile?.submissions?.length) return null;
    const startDate = new Date(profile.baseline.createdAt);
    const endDate = new Date(profile.submissions[profile.submissions.length - 1].createdAt);
    const days = differenceInDays(endDate, startDate);
    
    if (days < 30) return `${days} days`;
    if (days < 365) return `${Math.floor(days / 30)} months`;
    return `${Math.floor(days / 365)} year${Math.floor(days / 365) > 1 ? 's' : ''} ${Math.floor((days % 365) / 30)} months`;
  };

  // Get current and baseline aspects
  const latestSubmission = profile?.submissions?.[profile.submissions.length - 1];
  const currentAspects = latestSubmission?.aspects || profile?.baseline?.aspects || [];
  const baselineAspects = profile?.baseline?.aspects || [];

  // Calculate overall levels
  const currentOverallLevel = currentAspects.length > 0 
    ? Math.round(currentAspects.reduce((sum, a) => sum + a.level, 0) / currentAspects.length)
    : 0;
  const baselineOverallLevel = baselineAspects.length > 0 
    ? Math.round(baselineAspects.reduce((sum, a) => sum + a.level, 0) / baselineAspects.length)
    : 0;

  // Calculate stability indicator
  const getStabilityIndicator = () => {
    if (!profile?.submissions || profile.submissions.length < 2) return 'Insufficient data';
    
    // Calculate variance in overall levels across submissions
    const levels = [
      profile.baseline?.overallLevel || 0,
      ...profile.submissions.map(s => s.overallLevel)
    ];
    const avg = levels.reduce((a, b) => a + b, 0) / levels.length;
    const variance = levels.reduce((sum, l) => sum + Math.pow(l - avg, 2), 0) / levels.length;
    
    if (variance < 0.5) return 'High Stability';
    if (variance < 1) return 'Moderate Stability';
    return 'Evolving Pattern';
  };

  // Prepare radar chart data
  const radarData = WRITING_ASPECTS.map(aspect => {
    const current = currentAspects.find(a => a.aspectId === aspect.id);
    const baseline = baselineAspects.find(a => a.aspectId === aspect.id);
    return {
      aspect: aspect.name.split(' ')[0],
      fullName: aspect.name,
      current: current?.level || 0,
      baseline: baseline?.level || 0,
      max: 5
    };
  });

  // Calculate aspect evolution summary
  const getEvolutionSummary = () => {
    return WRITING_ASPECTS.map(aspect => {
      const current = currentAspects.find(a => a.aspectId === aspect.id);
      const baseline = baselineAspects.find(a => a.aspectId === aspect.id);
      const change = (current?.level || 0) - (baseline?.level || 0);
      return {
        name: aspect.name,
        baselineLevel: baseline?.level || 0,
        currentLevel: current?.level || 0,
        change,
        baselineMaturity: MATURITY_LEVELS[(baseline?.level || 1) - 1]?.name || 'N/A',
        currentMaturity: MATURITY_LEVELS[(current?.level || 1) - 1]?.name || 'N/A'
      };
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-foreground">Loading...</div>
      </div>
    );
  }

  if (!isEligible) {
    return (
      <div className="min-h-screen bg-background">
        <div className="max-w-2xl mx-auto px-4 py-12 text-center">
          <Button
            variant="ghost"
            onClick={() => navigate('/writing-evolution')}
            className="mb-8 text-muted-foreground hover:text-foreground"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Dashboard
          </Button>
          <div className="w-20 h-20 rounded-full bg-muted/20 flex items-center justify-center mx-auto mb-6">
            <Shield className="w-10 h-10 text-muted-foreground" />
          </div>
          <h1 className="text-2xl font-bold text-foreground mb-3">
            Record Not Yet Available
          </h1>
          <p className="text-muted-foreground mb-6">
            Complete at least 5 writing submissions to generate your Authorship Continuity & Writing Evolution Record.
          </p>
          <p className="text-sm text-muted-foreground">
            Current submissions: {submissionCount} / 5
          </p>
        </div>
      </div>
    );
  }

  const evolutionSummary = getEvolutionSummary();

  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-4xl mx-auto px-4 py-12">
        {/* Header */}
        <div className="mb-8">
          <Button
            variant="ghost"
            onClick={() => navigate('/writing-evolution')}
            className="mb-4 text-muted-foreground hover:text-foreground"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Dashboard
          </Button>
        </div>

        {/* Certificate Card */}
        <Card className="bg-card border-2 border-primary/30 shadow-lg mb-8">
          {/* Certificate Header */}
          <div className="bg-gradient-to-r from-primary/10 via-primary/5 to-transparent p-8 border-b border-border/50">
            <div className="flex items-start justify-between">
              <div>
                <div className="flex items-center gap-3 mb-2">
                  <Shield className="w-8 h-8 text-primary" />
                  <Badge variant="outline" className="text-primary border-primary/50">
                    Longitudinal Record
                  </Badge>
                </div>
                <h1 className="text-2xl md:text-3xl font-bold text-foreground mb-2">
                  Authorship Continuity & Writing Evolution Record
                </h1>
                <p className="text-muted-foreground">
                  Documented writing development across the academic research journey
                </p>
              </div>
            </div>
          </div>

          <CardContent className="p-8">
            {/* Key Metrics Row */}
            <div className="grid md:grid-cols-4 gap-6 mb-8">
              <div className="text-center p-4 bg-muted/10 rounded-lg">
                <FileCheck className="w-6 h-6 text-primary mx-auto mb-2" />
                <p className="text-2xl font-bold text-foreground">{submissionCount}</p>
                <p className="text-xs text-muted-foreground">Verified Submissions</p>
              </div>
              <div className="text-center p-4 bg-muted/10 rounded-lg">
                <CalendarDays className="w-6 h-6 text-primary mx-auto mb-2" />
                <p className="text-2xl font-bold text-foreground">{getTimeSpan() || 'N/A'}</p>
                <p className="text-xs text-muted-foreground">Time Span Covered</p>
              </div>
              <div className="text-center p-4 bg-muted/10 rounded-lg">
                <Layers className="w-6 h-6 text-primary mx-auto mb-2" />
                <p className="text-2xl font-bold text-foreground">{getStabilityIndicator()}</p>
                <p className="text-xs text-muted-foreground">Continuity Pattern</p>
              </div>
              <div className="text-center p-4 bg-muted/10 rounded-lg">
                <TrendingUp className="w-6 h-6 text-primary mx-auto mb-2" />
                <p className="text-2xl font-bold text-foreground">
                  {MATURITY_LEVELS[currentOverallLevel - 1]?.name || 'N/A'}
                </p>
                <p className="text-xs text-muted-foreground">Current Maturity Level</p>
              </div>
            </div>

            <Separator className="my-8" />

            {/* Profile Visualization */}
            <div className="grid lg:grid-cols-2 gap-8 mb-8">
              {/* Radar Chart */}
              <div>
                <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
                  <Award className="w-5 h-5 text-primary" />
                  Writing Profile Evolution
                </h3>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <RadarChart data={radarData}>
                      <PolarGrid stroke="hsl(var(--border))" />
                      <PolarAngleAxis 
                        dataKey="aspect" 
                        tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 10 }}
                      />
                      <PolarRadiusAxis 
                        angle={30} 
                        domain={[0, 5]} 
                        tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 9 }}
                      />
                      <Radar
                        name="Baseline"
                        dataKey="baseline"
                        stroke="hsl(var(--muted-foreground))"
                        fill="hsl(var(--muted-foreground))"
                        fillOpacity={0.1}
                        strokeDasharray="5 5"
                      />
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
                <div className="flex justify-center gap-6 mt-4 text-xs text-muted-foreground">
                  <span className="flex items-center gap-2">
                    <span className="w-3 h-0.5 bg-muted-foreground opacity-50" style={{ borderStyle: 'dashed' }} />
                    Baseline
                  </span>
                  <span className="flex items-center gap-2">
                    <span className="w-3 h-0.5 bg-primary" />
                    Current
                  </span>
                </div>
              </div>

              {/* Aspect Evolution Summary */}
              <div>
                <h3 className="text-lg font-semibold text-foreground mb-4">
                  Maturity Progression by Aspect
                </h3>
                <div className="space-y-3">
                  {evolutionSummary.map((aspect) => (
                    <div key={aspect.name} className="flex items-center justify-between text-sm">
                      <span className="text-foreground truncate flex-1 mr-4">{aspect.name}</span>
                      <div className="flex items-center gap-2">
                        <Badge variant="outline" className="text-muted-foreground text-xs">
                          {aspect.baselineMaturity}
                        </Badge>
                        <span className="text-muted-foreground">→</span>
                        <Badge 
                          variant="outline" 
                          className={`text-xs ${
                            aspect.change > 0 ? 'text-emerald-500 border-emerald-500/30' :
                            aspect.change < 0 ? 'text-amber-500 border-amber-500/30' :
                            'text-muted-foreground'
                          }`}
                        >
                          {aspect.currentMaturity}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <Separator className="my-8" />

            {/* Verification Statement */}
            <div className="bg-muted/10 rounded-lg p-6 mb-8">
              <div className="flex items-start gap-4">
                <CheckCircle2 className="w-6 h-6 text-emerald-500 flex-shrink-0 mt-1" />
                <div>
                  <h4 className="font-semibold text-foreground mb-2">Authorship Continuity Verification</h4>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    This record documents a verified writing trail spanning {submissionCount} submissions over {getTimeSpan() || 'the recorded period'}. 
                    The longitudinal analysis indicates <strong>{getStabilityIndicator().toLowerCase()}</strong> in writing patterns, 
                    with documented development across all 7 core academic writing dimensions. 
                    This record serves as supporting evidence of authorship continuity based on repeated, timestamped submissions 
                    and structural analysis of writing development over time.
                  </p>
                </div>
              </div>
            </div>

            {/* Generation Info */}
            <div className="flex items-center justify-between text-xs text-muted-foreground">
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4" />
                <span>Generated on {format(new Date(), 'MMMM d, yyyy')}</span>
              </div>
              <span>
                Baseline established: {profile?.baseline ? format(new Date(profile.baseline.createdAt), 'MMM d, yyyy') : 'N/A'}
              </span>
            </div>
          </CardContent>
        </Card>

        {/* Originality Evidence Explanation */}
        <Collapsible open={infoOpen} onOpenChange={setInfoOpen}>
          <Card className="bg-card border-border/50">
            <CollapsibleTrigger asChild>
              <CardHeader className="cursor-pointer hover:bg-muted/10 transition-colors">
                <CardTitle className="text-base font-medium text-foreground flex items-center justify-between">
                  <span className="flex items-center gap-2">
                    <Info className="w-5 h-5 text-info" />
                    About This Record & Originality Evidence
                  </span>
                  <ChevronDown className={`w-4 h-4 text-muted-foreground transition-transform ${infoOpen ? 'rotate-180' : ''}`} />
                </CardTitle>
              </CardHeader>
            </CollapsibleTrigger>
            <CollapsibleContent>
              <CardContent className="pt-0">
                <div className="bg-muted/10 rounded-lg p-5">
                  <p className="text-sm text-muted-foreground leading-relaxed mb-4">
                    <strong className="text-foreground">This record does not judge originality or detect plagiarism.</strong>{' '}
                    Instead, it documents authorship continuity over time by tracking repeated writing submissions, 
                    stylistic stability, and academic development across structured dimensions.
                  </p>
                  <p className="text-sm text-muted-foreground leading-relaxed mb-4">
                    The longitudinal nature of this record creates a verified writing trail that can be used as 
                    <strong className="text-foreground"> supporting evidence of original authorship</strong> in environments 
                    where AI-generated or outsourced writing is a concern. By demonstrating consistent development and 
                    documented evolution over time, researchers establish trust in their academic voice.
                  </p>
                  <div className="flex flex-wrap gap-2 mt-4">
                    <Badge variant="outline" className="text-xs text-muted-foreground">
                      Documented Writing Trail
                    </Badge>
                    <Badge variant="outline" className="text-xs text-muted-foreground">
                      Longitudinal Evidence
                    </Badge>
                    <Badge variant="outline" className="text-xs text-muted-foreground">
                      Process-Oriented
                    </Badge>
                    <Badge variant="outline" className="text-xs text-muted-foreground">
                      Trust-Supporting
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </CollapsibleContent>
          </Card>
        </Collapsible>

        {/* Actions */}
        <div className="flex flex-wrap gap-4 mt-8">
          <Button className="bg-primary hover:bg-primary/90">
            <Download className="w-4 h-4 mr-2" />
            Export as PDF
          </Button>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="outline" className="border-border">
                Share Record
              </Button>
            </TooltipTrigger>
            <TooltipContent className="bg-popover border-border">
              <p className="text-sm">Generate a shareable link for institutions or supervisors</p>
            </TooltipContent>
          </Tooltip>
        </div>
      </div>
    </div>
  );
};

export default WritingEvolutionCertificate;
