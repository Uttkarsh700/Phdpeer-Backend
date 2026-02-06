import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Upload, ArrowLeft, CalendarIcon, FileText, Sparkles } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { format } from "date-fns";
import { cn } from "@/lib/utils";

const MILESTONE_TYPES = [
  { value: "proposal", label: "Proposal Draft" },
  { value: "chapter", label: "Chapter Draft" },
  { value: "revision", label: "Revision" },
  { value: "submission", label: "Journal/Conference Submission" }
];

const WritingEvolutionCheckpoint = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);

  const [file, setFile] = useState<File | null>(null);
  const [milestoneType, setMilestoneType] = useState("");
  const [date, setDate] = useState<Date>(new Date());
  const [aiAssisted, setAiAssisted] = useState(false);
  const [externalEditing, setExternalEditing] = useState(false);
  const [coauthorInput, setCoauthorInput] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const canSubmit = file && milestoneType;

  const handleSubmit = async () => {
    if (!canSubmit) return;
    
    setLoading(true);
    try {
      // TODO: Replace with your backend API call
      const userId = sessionStorage.getItem("userId");
      if (!userId) throw new Error("Not authenticated");

      // Generate mock evolution run results
      const mockScore = Math.floor(Math.random() * 30) + 70; // 70-100
      const mockTrend = mockScore >= 85 ? 'improving' : mockScore >= 75 ? 'stable' : 'volatile';
      
      const mockSignals = [
        mockScore < 80 && { type: 'watch', message: 'Moderate stylistic shift detected in sentence structure' },
        mockScore < 70 && { type: 'review', message: 'Abrupt discontinuity in vocabulary patterns' },
        mockScore >= 85 && { type: 'positive', message: 'Organic evolution, consistent with baseline' },
        aiAssisted && { type: 'info', message: 'AI assistance disclosed, accounted for in analysis' }
      ].filter(Boolean);

      const mockGuidance = [
        { action: 'Review recent changes to ensure they reflect your voice', priority: 'medium' },
        mockScore < 80 && { action: 'Consider documenting major stylistic decisions', priority: 'high' },
        { action: 'Schedule next checkpoint in 2-4 weeks', priority: 'low' }
      ].filter(Boolean);

      const mockChanges = {
        tone: { score: Math.floor(Math.random() * 20) + 80, label: 'Consistent' },
        structure: { score: Math.floor(Math.random() * 25) + 75, label: 'Minor shifts' },
        lexical: { score: Math.floor(Math.random() * 30) + 70, label: 'Evolving vocabulary' },
        complexity: { score: Math.floor(Math.random() * 20) + 80, label: 'Stable' },
        citation: { score: Math.floor(Math.random() * 15) + 85, label: 'Consistent style' }
      };

      // Create sample and run (storing in localStorage for now)
      const sample = {
        id: `sample_${Date.now()}`,
        user_id: userId,
        sample_type: 'checkpoint',
        file_url: file.name,
        milestone_type: milestoneType,
        ai_assisted: aiAssisted,
        external_editing: externalEditing,
        coauthor_input: coauthorInput,
        created_at: date.toISOString()
      };

      const run = {
        id: `run_${Date.now()}`,
        user_id: userId,
        checkpoint_sample_id: sample.id,
        continuity_score: mockScore,
        evolution_trend: mockTrend,
        signals_json: mockSignals,
        guidance_json: mockGuidance,
        changes_json: mockChanges,
        created_at: new Date().toISOString()
      };

      // Store in localStorage (replace with backend API)
      const storedSamples = localStorage.getItem("writing_samples");
      const samples = storedSamples ? JSON.parse(storedSamples) : [];
      samples.push(sample);
      localStorage.setItem("writing_samples", JSON.stringify(samples));

      const storedRuns = localStorage.getItem("evolution_runs");
      const runs = storedRuns ? JSON.parse(storedRuns) : [];
      runs.push(run);
      localStorage.setItem("evolution_runs", JSON.stringify(runs));

      toast({
        title: "Checkpoint Analyzed",
        description: `Continuity score: ${mockScore}/100`
      });

      navigate(`/writing-evolution/report/${run.id}`);
    } catch (error: any) {
      console.error('Error uploading checkpoint:', error);
      toast({
        title: "Error",
        description: error.message || "Failed to upload checkpoint. Please try again.",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-2xl mx-auto px-4 py-12">
        {/* Header */}
        <div className="mb-8">
          <Button
            variant="ghost"
            onClick={() => navigate('/writing-evolution')}
            className="mb-4 text-muted-foreground hover:text-foreground"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
          <h1 className="text-3xl font-bold text-foreground mb-2">
            Add Writing Submission
          </h1>
          <p className="text-muted-foreground">
            Submit a new writing sample to continue building your documented authorship trail
          </p>
        </div>

        <Card className="bg-card border-border/50">
          <CardHeader>
            <CardTitle className="text-xl text-foreground">Submission Details</CardTitle>
            <CardDescription>
              Upload your document and provide context for your documented writing trail
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* File Upload */}
            <div className="space-y-2">
              <Label className="text-foreground">Document</Label>
              <div className="border-2 border-dashed border-border rounded-lg p-8 text-center hover:border-primary/50 transition-colors">
                <input
                  id="checkpoint-file"
                  type="file"
                  accept=".pdf,.docx,.doc,.txt"
                  onChange={handleFileChange}
                  className="hidden"
                />
                <label htmlFor="checkpoint-file" className="cursor-pointer">
                  {file ? (
                    <div className="flex items-center justify-center gap-3">
                      <FileText className="w-8 h-8 text-primary" />
                      <div className="text-left">
                        <p className="text-foreground font-medium">{file.name}</p>
                        <p className="text-sm text-muted-foreground">
                          {(file.size / 1024).toFixed(1)} KB
                        </p>
                      </div>
                    </div>
                  ) : (
                    <>
                      <Upload className="w-10 h-10 text-muted-foreground mx-auto mb-3" />
                      <p className="text-foreground font-medium mb-1">
                        Click to upload or drag and drop
                      </p>
                      <p className="text-sm text-muted-foreground">
                        PDF, DOCX, or TXT (max 10MB)
                      </p>
                    </>
                  )}
                </label>
              </div>
            </div>

            {/* Milestone Type */}
            <div className="space-y-2">
              <Label htmlFor="milestone" className="text-foreground">Milestone Type</Label>
              <Select value={milestoneType} onValueChange={setMilestoneType}>
                <SelectTrigger className="bg-input border-border">
                  <SelectValue placeholder="What type of document is this?" />
                </SelectTrigger>
                <SelectContent className="bg-popover border-border">
                  {MILESTONE_TYPES.map((m) => (
                    <SelectItem key={m.value} value={m.value}>{m.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Date Picker */}
            <div className="space-y-2">
              <Label className="text-foreground">Document Date</Label>
              <Popover>
                <PopoverTrigger asChild>
                  <Button
                    variant="outline"
                    className={cn(
                      "w-full justify-start text-left font-normal bg-input border-border",
                      !date && "text-muted-foreground"
                    )}
                  >
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {date ? format(date, "PPP") : "Select date"}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0 bg-popover border-border" align="start">
                  <Calendar
                    mode="single"
                    selected={date}
                    onSelect={(d) => d && setDate(d)}
                    initialFocus
                  />
                </PopoverContent>
              </Popover>
            </div>

            {/* Disclosure Toggles */}
            <div className="space-y-4 pt-4 border-t border-border">
              <div className="flex items-center gap-2 mb-4">
                <Sparkles className="w-4 h-4 text-primary" />
                <h4 className="font-medium text-foreground">Optional Disclosures</h4>
              </div>
              <p className="text-sm text-muted-foreground mb-4">
                These help provide more accurate continuity analysis and strengthen your documented writing trail. All disclosures are private.
              </p>

              <div className="flex items-center justify-between p-3 bg-muted/20 rounded-lg">
                <div>
                  <Label htmlFor="ai-assisted" className="text-foreground">AI-Assisted Writing</Label>
                  <p className="text-xs text-muted-foreground">Used AI tools for drafting or editing</p>
                </div>
                <Switch
                  id="ai-assisted"
                  checked={aiAssisted}
                  onCheckedChange={setAiAssisted}
                />
              </div>

              <div className="flex items-center justify-between p-3 bg-muted/20 rounded-lg">
                <div>
                  <Label htmlFor="external-editing" className="text-foreground">External Editing</Label>
                  <p className="text-xs text-muted-foreground">Professional editing or proofreading</p>
                </div>
                <Switch
                  id="external-editing"
                  checked={externalEditing}
                  onCheckedChange={setExternalEditing}
                />
              </div>

              <div className="flex items-center justify-between p-3 bg-muted/20 rounded-lg">
                <div>
                  <Label htmlFor="coauthor-input" className="text-foreground">Co-Author Input</Label>
                  <p className="text-xs text-muted-foreground">Significant contributions from co-authors</p>
                </div>
                <Switch
                  id="coauthor-input"
                  checked={coauthorInput}
                  onCheckedChange={setCoauthorInput}
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Submit Button */}
        <div className="mt-8 flex justify-end">
          <Button
            onClick={handleSubmit}
            disabled={!canSubmit || loading}
            className="bg-primary hover:bg-primary/90"
          >
            {loading ? "Analyzing..." : "Submit for Documentation"}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default WritingEvolutionCheckpoint;