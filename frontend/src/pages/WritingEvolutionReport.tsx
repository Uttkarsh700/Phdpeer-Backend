import { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { 
  ArrowLeft, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle, 
  Info, 
  Download, 
  HelpCircle,
  FileText,
  Sparkles,
  ArrowUpRight,
  ArrowDownRight,
  Minus
} from "lucide-react";
import { format } from "date-fns";

interface EvolutionRun {
  id: string;
  continuity_score: number | null;
  evolution_trend: string | null;
  signals_json: any;
  guidance_json: any;
  changes_json: any;
  created_at: string;
  checkpoint_sample_id: string;
}

interface WritingSample {
  id: string;
  milestone_type: string;
  created_at: string;
  ai_assisted: boolean;
  external_editing: boolean;
  coauthor_input: boolean;
}

const WritingEvolutionReport = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const [run, setRun] = useState<EvolutionRun | null>(null);
  const [sample, setSample] = useState<WritingSample | null>(null);
  const [allRuns, setAllRuns] = useState<EvolutionRun[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) fetchData();
  }, [id]);

  const fetchData = async () => {
    try {
      // TODO: Replace with your backend API call
      // For now, load from localStorage or set mock data
      const storedRuns = localStorage.getItem("evolution_runs");
      const allRunsData = storedRuns ? JSON.parse(storedRuns) : [];
      
      const runData = allRunsData.find((r: any) => r.id === id);
      if (runData) {
        setRun(runData);
        
        // Fetch the associated sample
        const storedSamples = localStorage.getItem("writing_samples");
        const samples = storedSamples ? JSON.parse(storedSamples) : [];
        const sampleData = samples.find((s: any) => s.id === runData.checkpoint_sample_id);
        setSample(sampleData || null);
      }
      
      setAllRuns(allRunsData);
    } catch (error) {
      console.error('Error fetching report data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-secondary';
    if (score >= 60) return 'text-warning';
    return 'text-destructive';
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'improving': return <ArrowUpRight className="w-4 h-4 text-secondary" />;
      case 'volatile': return <ArrowDownRight className="w-4 h-4 text-warning" />;
      default: return <Minus className="w-4 h-4 text-primary" />;
    }
  };

  const getSignalIcon = (type: string) => {
    switch (type) {
      case 'review': return <AlertTriangle className="w-4 h-4 text-destructive" />;
      case 'watch': return <Info className="w-4 h-4 text-warning" />;
      case 'positive': return <CheckCircle className="w-4 h-4 text-secondary" />;
      default: return <Info className="w-4 h-4 text-info" />;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-foreground">Loading report...</div>
      </div>
    );
  }

  if (!run) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <p className="text-foreground mb-4">Report not found</p>
          <Button onClick={() => navigate('/writing-evolution')}>Go Back</Button>
        </div>
      </div>
    );
  }

  const signals = run.signals_json || [];
  const guidance = run.guidance_json || [];
  const changes = run.changes_json || {};

  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-5xl mx-auto px-4 py-12">
        {/* Header */}
        <div className="mb-8">
          <Button
            variant="ghost"
            onClick={() => navigate('/writing-evolution')}
            className="mb-4 text-muted-foreground hover:text-foreground"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Overview
          </Button>
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold text-foreground mb-2">
                Authorship Continuity Report
              </h1>
              <p className="text-muted-foreground">
                {sample?.milestone_type && (
                  <span className="capitalize">{sample.milestone_type} submission</span>
                )}
                {' · '}
                {format(new Date(run.created_at), 'MMMM d, yyyy')}
              </p>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" className="border-border">
                <Download className="w-4 h-4 mr-2" />
                Export PDF
              </Button>
            </div>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid md:grid-cols-3 gap-6 mb-10">
          {/* Continuity Score */}
          <Card className="bg-card border-border/50">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                Continuity Score
                <Tooltip>
                  <TooltipTrigger>
                    <HelpCircle className="w-3.5 h-3.5 text-muted-foreground/60" />
                  </TooltipTrigger>
                  <TooltipContent className="max-w-xs bg-popover border-border">
                    <p className="text-sm">
                      Measures how closely this submission aligns with your established writing baseline. 
                      Higher scores indicate stronger authorship continuity and documented stylistic consistency.
                    </p>
                  </TooltipContent>
                </Tooltip>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-baseline gap-2">
                <span className={`text-4xl font-bold ${getScoreColor(run.continuity_score)}`}>
                  {run.continuity_score}
                </span>
                <span className="text-muted-foreground">/100</span>
              </div>
              <Progress value={run.continuity_score} className="mt-3 h-2" />
            </CardContent>
          </Card>

          {/* Evolution Trend */}
          <Card className="bg-card border-border/50">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Evolution Trend
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                {getTrendIcon(run.evolution_trend)}
                <span className="text-2xl font-semibold text-foreground capitalize">
                  {run.evolution_trend}
                </span>
              </div>
              <p className="text-sm text-muted-foreground mt-2">
                {run.evolution_trend === 'improving' && 'Documented natural writing development'}
                {run.evolution_trend === 'stable' && 'Consistent authorship patterns over time'}
                {run.evolution_trend === 'volatile' && 'Notable stylistic changes observed'}
              </p>
            </CardContent>
          </Card>

          {/* Signals Count */}
          <Card className="bg-card border-border/50">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                Signals
                <Tooltip>
                  <TooltipTrigger>
                    <HelpCircle className="w-3.5 h-3.5 text-muted-foreground/60" />
                  </TooltipTrigger>
                  <TooltipContent className="max-w-xs bg-popover border-border">
                    <p className="text-sm">
                      Signals are observations about your documented writing development, not judgments. 
                      They help track how your academic voice evolves over time.
                    </p>
                  </TooltipContent>
                </Tooltip>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <span className="text-4xl font-bold text-foreground">{signals.length}</span>
              <p className="text-sm text-muted-foreground mt-2">
                Observations from this checkpoint
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Documented Writing Trail */}
        <Card className="bg-card border-border/50 mb-8">
          <CardHeader>
            <CardTitle className="text-lg text-foreground">Documented Writing Trail</CardTitle>
            <CardDescription>Your verified authorship journey across submissions</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="relative">
              <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-border" />
              <div className="space-y-6">
                {allRuns.map((r, index) => (
                  <div key={r.id} className="relative flex items-start gap-4 pl-10">
                    <div className={`absolute left-2.5 w-3 h-3 rounded-full ${
                      r.id === id ? 'bg-primary ring-4 ring-primary/20' : 'bg-muted-foreground'
                    }`} />
                    <div className="flex-1">
                      <div className="flex items-center gap-3">
                      <span className="text-sm font-medium text-foreground">
                        Submission {index + 1}
                      </span>
                        <Badge 
                          variant="outline" 
                          className={`text-xs ${getScoreColor(r.continuity_score)} border-current`}
                        >
                          {r.continuity_score}/100
                        </Badge>
                        {r.id === id && (
                          <Badge className="bg-primary/20 text-primary text-xs">Current</Badge>
                        )}
                      </div>
                      <p className="text-xs text-muted-foreground mt-1">
                        {format(new Date(r.created_at), 'MMM d, yyyy')}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* What Changed */}
        <Accordion type="single" collapsible className="mb-8">
          <AccordionItem value="changes" className="bg-card border border-border/50 rounded-lg px-6">
            <AccordionTrigger className="text-lg font-semibold text-foreground hover:no-underline">
              <div className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-primary" />
                What Changed
              </div>
            </AccordionTrigger>
            <AccordionContent>
              <div className="space-y-4 pt-2">
                {Object.entries(changes).map(([key, val]) => {
                  const change = val as { score: number; label: string };
                  return (
                    <div key={key} className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <span className="text-foreground capitalize font-medium">{key}</span>
                        <span className="text-sm text-muted-foreground">{change.label}</span>
                      </div>
                      <div className="flex items-center gap-3 w-48">
                        <Progress value={change.score} className="h-2 flex-1" />
                        <span className={`text-sm font-medium ${getScoreColor(change.score)}`}>
                          {change.score}%
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </AccordionContent>
          </AccordionItem>
        </Accordion>

        {/* Signals */}
        <Card className="bg-card border-border/50 mb-8">
          <CardHeader>
            <CardTitle className="text-lg text-foreground flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-primary" />
              Development Signals
            </CardTitle>
            <CardDescription>
              Non-judgmental observations about your documented writing development
            </CardDescription>
          </CardHeader>
          <CardContent>
            {signals.length === 0 ? (
              <p className="text-muted-foreground text-center py-6">
                No significant signals for this submission
              </p>
            ) : (
              <div className="space-y-3">
                {signals.map((signal: any, index: number) => (
                  <div 
                    key={index} 
                    className="flex items-start gap-3 p-3 bg-muted/20 rounded-lg"
                  >
                    {getSignalIcon(signal.type)}
                    <p className="text-foreground text-sm">{signal.message}</p>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Guidance */}
        <Card className="bg-card border-border/50 mb-8">
          <CardHeader>
            <CardTitle className="text-lg text-foreground flex items-center gap-2">
              <FileText className="w-5 h-5 text-primary" />
              Development Guidance
            </CardTitle>
            <CardDescription>
              Suggested next steps to continue building your authorship trail
            </CardDescription>
          </CardHeader>
          <CardContent>
            {guidance.length === 0 ? (
              <p className="text-muted-foreground text-center py-6">
                No specific guidance for this submission
              </p>
            ) : (
              <div className="space-y-3">
                {guidance.map((item: any, index: number) => (
                  <div 
                    key={index} 
                    className="flex items-start gap-3 p-3 border border-border/50 rounded-lg"
                  >
                    <div className={`w-2 h-2 rounded-full mt-2 ${
                      item.priority === 'high' ? 'bg-destructive' :
                      item.priority === 'medium' ? 'bg-warning' : 'bg-secondary'
                    }`} />
                    <div>
                      <p className="text-foreground text-sm">{item.action}</p>
                      <span className="text-xs text-muted-foreground capitalize">
                        {item.priority} priority
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Disclosures */}
        {sample && (sample.ai_assisted || sample.external_editing || sample.coauthor_input) && (
          <Card className="bg-muted/20 border-border/50">
            <CardContent className="py-4">
              <div className="flex items-center gap-2 mb-2">
                <Info className="w-4 h-4 text-muted-foreground" />
                <span className="text-sm font-medium text-muted-foreground">Disclosures for this submission</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {sample.ai_assisted && (
                  <Badge variant="outline" className="text-xs">AI-Assisted</Badge>
                )}
                {sample.external_editing && (
                  <Badge variant="outline" className="text-xs">External Editing</Badge>
                )}
                {sample.coauthor_input && (
                  <Badge variant="outline" className="text-xs">Co-Author Input</Badge>
                )}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default WritingEvolutionReport;