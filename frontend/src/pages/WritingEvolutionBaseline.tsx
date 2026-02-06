import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Checkbox } from "@/components/ui/checkbox";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Progress } from "@/components/ui/progress";
import { Upload, FileText, Pen, ArrowLeft, ArrowRight, Check, Shield, Sparkles } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { 
  DISCIPLINES, 
  RESEARCH_TYPES, 
  STAGES, 
  LANGUAGES,
  generateMockEvaluation,
  loadProfile,
  saveProfile,
  type WritingBaseline
} from "@/lib/writingEvolutionTypes";

const WritingEvolutionBaseline = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);

  // Step 1: Method choice
  const [method, setMethod] = useState<'upload' | 'write' | null>(null);
  const [files, setFiles] = useState<File[]>([]);
  const [writtenText, setWrittenText] = useState("");

  // Step 2: Research context
  const [discipline, setDiscipline] = useState("");
  const [researchType, setResearchType] = useState("");
  const [stage, setStage] = useState("");
  const [language, setLanguage] = useState("en");

  // Step 3: Consent
  const [consentGiven, setConsentGiven] = useState(false);
  const [supervisorView, setSupervisorView] = useState(false);
  const [institutionView, setInstitutionView] = useState(false);

  const progress = (step / 4) * 100;
  const wordCount = writtenText.split(/\s+/).filter(Boolean).length;

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const fileList = Array.from(e.target.files).slice(0, 3);
      setFiles(fileList);
    }
  };

  const canProceedStep1 = method === 'upload' ? files.length > 0 : wordCount >= 500;
  const canProceedStep2 = discipline && researchType && stage && language;
  const canProceedStep3 = consentGiven;

  const handleNext = () => {
    if (step < 4) setStep(step + 1);
  };

  const handleBack = () => {
    if (step > 1) setStep(step - 1);
  };

  const handleCreateBaseline = async () => {
    setLoading(true);
    
    // Simulate processing time
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    try {
      const profile = loadProfile();
      
      // Generate mock evaluation for all 7 aspects
      const aspects = generateMockEvaluation();
      const overallLevel = Math.round(aspects.reduce((sum, a) => sum + a.level, 0) / aspects.length);
      
      const baseline: WritingBaseline = {
        id: crypto.randomUUID(),
        createdAt: new Date().toISOString(),
        method: method!,
        discipline,
        researchType,
        stage,
        language,
        wordCount: method === 'write' ? wordCount : 0,
        consentGiven,
        supervisorViewEnabled: supervisorView,
        institutionViewEnabled: institutionView,
        aspects,
        overallLevel
      };
      
      profile.baseline = baseline;
      saveProfile(profile);

      toast({
        title: "Baseline Created",
        description: "Your writing baseline has been established. View your profile to see your initial assessment."
      });

      navigate('/writing-evolution');
    } catch (error: any) {
      console.error('Error creating baseline:', error);
      toast({
        title: "Error",
        description: "Failed to create baseline. Please try again.",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-3xl mx-auto px-4 py-12">
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
            Create Your Writing Baseline
          </h1>
          <p className="text-muted-foreground">
            Establish your authorship profile across 7 dimensions of academic writing
          </p>
        </div>

        {/* Progress */}
        <div className="mb-8">
          <div className="flex justify-between text-sm text-muted-foreground mb-2">
            <span>Step {step} of 4</span>
            <span>{Math.round(progress)}% complete</span>
          </div>
          <Progress value={progress} className="h-2" />
          <div className="flex justify-between mt-2">
            <span className={`text-xs ${step >= 1 ? 'text-primary' : 'text-muted-foreground'}`}>Method</span>
            <span className={`text-xs ${step >= 2 ? 'text-primary' : 'text-muted-foreground'}`}>Context</span>
            <span className={`text-xs ${step >= 3 ? 'text-primary' : 'text-muted-foreground'}`}>Consent</span>
            <span className={`text-xs ${step >= 4 ? 'text-primary' : 'text-muted-foreground'}`}>Create</span>
          </div>
        </div>

        {/* Step 1: Choose Method */}
        {step === 1 && (
          <Card className="bg-card border-border/50">
            <CardHeader>
              <CardTitle className="text-xl text-foreground">Choose Your Baseline Method</CardTitle>
              <CardDescription>
                Provide a writing sample to establish your authorship profile
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid md:grid-cols-2 gap-4">
                <Card 
                  className={`cursor-pointer transition-all border-2 ${
                    method === 'upload' 
                      ? 'border-primary bg-primary/5' 
                      : 'border-border hover:border-primary/50'
                  }`}
                  onClick={() => setMethod('upload')}
                >
                  <CardContent className="p-6 text-center">
                    <Upload className="w-10 h-10 text-primary mx-auto mb-3" />
                    <h3 className="font-semibold text-foreground mb-2">Upload Files</h3>
                    <p className="text-sm text-muted-foreground">
                      Upload 1-3 existing documents (PDF, DOCX, TXT)
                    </p>
                  </CardContent>
                </Card>

                <Card 
                  className={`cursor-pointer transition-all border-2 ${
                    method === 'write' 
                      ? 'border-primary bg-primary/5' 
                      : 'border-border hover:border-primary/50'
                  }`}
                  onClick={() => setMethod('write')}
                >
                  <CardContent className="p-6 text-center">
                    <Pen className="w-10 h-10 text-primary mx-auto mb-3" />
                    <h3 className="font-semibold text-foreground mb-2">Write In-App</h3>
                    <p className="text-sm text-muted-foreground">
                      Write 500-800 words directly here
                    </p>
                  </CardContent>
                </Card>
              </div>

              {method === 'upload' && (
                <div className="space-y-4">
                  <Label htmlFor="file-upload" className="text-foreground">
                    Select files (max 3)
                  </Label>
                  <input
                    id="file-upload"
                    type="file"
                    multiple
                    accept=".pdf,.docx,.doc,.txt"
                    onChange={handleFileChange}
                    className="block w-full text-sm text-muted-foreground
                      file:mr-4 file:py-2 file:px-4
                      file:rounded-lg file:border-0
                      file:text-sm file:font-medium
                      file:bg-primary file:text-primary-foreground
                      hover:file:bg-primary/90"
                  />
                  {files.length > 0 && (
                    <div className="space-y-2">
                      {files.map((file, i) => (
                        <div key={i} className="flex items-center gap-2 text-sm text-muted-foreground">
                          <FileText className="w-4 h-4" />
                          {file.name}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {method === 'write' && (
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <Label htmlFor="writing" className="text-foreground">
                      Your Writing Sample
                    </Label>
                    <span className={`text-sm ${
                      wordCount >= 500 
                        ? 'text-emerald-500' 
                        : 'text-muted-foreground'
                    }`}>
                      {wordCount} / 500-800 words
                    </span>
                  </div>
                  <Textarea
                    id="writing"
                    placeholder="Write about your research interests, methodology, or a section from your current work. This helps establish your unique writing patterns and academic voice."
                    value={writtenText}
                    onChange={(e) => setWrittenText(e.target.value)}
                    className="min-h-[300px] bg-input border-border text-foreground"
                  />
                  <p className="text-xs text-muted-foreground">
                    Write naturally about your research. Include technical terms and your typical sentence structures.
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Step 2: Research Context */}
        {step === 2 && (
          <Card className="bg-card border-border/50">
            <CardHeader>
              <CardTitle className="text-xl text-foreground">Research Context</CardTitle>
              <CardDescription>
                This helps calibrate the evaluation to your discipline and stage
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="discipline" className="text-foreground">Discipline</Label>
                <Select value={discipline} onValueChange={setDiscipline}>
                  <SelectTrigger className="bg-input border-border">
                    <SelectValue placeholder="Select your field" />
                  </SelectTrigger>
                  <SelectContent className="bg-popover border-border">
                    {DISCIPLINES.map((d) => (
                      <SelectItem key={d} value={d}>{d}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="researchType" className="text-foreground">Research Type</Label>
                <Select value={researchType} onValueChange={setResearchType}>
                  <SelectTrigger className="bg-input border-border">
                    <SelectValue placeholder="Select research approach" />
                  </SelectTrigger>
                  <SelectContent className="bg-popover border-border">
                    {RESEARCH_TYPES.map((r) => (
                      <SelectItem key={r.value} value={r.value}>{r.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="stage" className="text-foreground">PhD Stage</Label>
                <Select value={stage} onValueChange={setStage}>
                  <SelectTrigger className="bg-input border-border">
                    <SelectValue placeholder="Select your stage" />
                  </SelectTrigger>
                  <SelectContent className="bg-popover border-border">
                    {STAGES.map((s) => (
                      <SelectItem key={s.value} value={s.value}>{s.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="language" className="text-foreground">Primary Writing Language</Label>
                <Select value={language} onValueChange={setLanguage}>
                  <SelectTrigger className="bg-input border-border">
                    <SelectValue placeholder="Select language" />
                  </SelectTrigger>
                  <SelectContent className="bg-popover border-border">
                    {LANGUAGES.map((l) => (
                      <SelectItem key={l.value} value={l.value}>{l.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Step 3: Consent */}
        {step === 3 && (
          <Card className="bg-card border-border/50">
            <CardHeader>
              <CardTitle className="text-xl text-foreground flex items-center gap-2">
                <Shield className="w-5 h-5 text-primary" />
                Privacy & Consent
              </CardTitle>
              <CardDescription>
                Your data remains yours. Configure visibility preferences.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-start space-x-3 p-4 bg-muted/30 rounded-lg">
                <Checkbox 
                  id="consent"
                  checked={consentGiven}
                  onCheckedChange={(checked) => setConsentGiven(checked as boolean)}
                />
                <div className="space-y-1">
                  <Label htmlFor="consent" className="text-foreground cursor-pointer">
                    I consent to baseline analysis
                  </Label>
                  <p className="text-sm text-muted-foreground">
                    I understand that my writing sample will be analyzed to create an authorship baseline. 
                    This data is used solely to track my own writing development over time.
                  </p>
                </div>
              </div>

              <div className="space-y-4">
                <h4 className="font-medium text-foreground">Optional Visibility Settings</h4>
                
                <div className="flex items-center justify-between p-4 bg-muted/20 rounded-lg">
                  <div className="space-y-0.5">
                    <Label htmlFor="supervisor" className="text-foreground">Allow Supervisor View</Label>
                    <p className="text-sm text-muted-foreground">
                      Your supervisor can view progress reports
                    </p>
                  </div>
                  <Switch
                    id="supervisor"
                    checked={supervisorView}
                    onCheckedChange={setSupervisorView}
                  />
                </div>

                <div className="flex items-center justify-between p-4 bg-muted/20 rounded-lg">
                  <div className="space-y-0.5">
                    <Label htmlFor="institution" className="text-foreground">Allow Institutional View</Label>
                    <p className="text-sm text-muted-foreground">
                      Anonymous aggregate data for institutional analytics
                    </p>
                  </div>
                  <Switch
                    id="institution"
                    checked={institutionView}
                    onCheckedChange={setInstitutionView}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Step 4: Confirmation */}
        {step === 4 && (
          <Card className="bg-card border-border/50">
            <CardHeader>
              <CardTitle className="text-xl text-foreground flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-primary" />
                Ready to Create Baseline
              </CardTitle>
              <CardDescription>
                Your profile will be analyzed across 7 dimensions of academic writing
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex justify-between py-2 border-b border-border/50">
                  <span className="text-muted-foreground">Method</span>
                  <span className="text-foreground capitalize">{method}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-border/50">
                  <span className="text-muted-foreground">Discipline</span>
                  <span className="text-foreground">{discipline}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-border/50">
                  <span className="text-muted-foreground">Research Type</span>
                  <span className="text-foreground capitalize">
                    {RESEARCH_TYPES.find(r => r.value === researchType)?.label}
                  </span>
                </div>
                <div className="flex justify-between py-2 border-b border-border/50">
                  <span className="text-muted-foreground">Stage</span>
                  <span className="text-foreground">
                    {STAGES.find(s => s.value === stage)?.label}
                  </span>
                </div>
                <div className="flex justify-between py-2 border-b border-border/50">
                  <span className="text-muted-foreground">Language</span>
                  <span className="text-foreground">
                    {LANGUAGES.find(l => l.value === language)?.label}
                  </span>
                </div>
              </div>

              <div className="p-4 bg-primary/10 rounded-lg border border-primary/20">
                <h4 className="font-medium text-foreground mb-2">What happens next</h4>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>• Your writing will be analyzed across 7 academic dimensions</li>
                  <li>• You'll receive an initial maturity level (1-5 scale)</li>
                  <li>• Strengths and areas for growth will be identified</li>
                  <li>• Badges will be awarded based on demonstrated skills</li>
                </ul>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Navigation */}
        <div className="flex justify-between mt-8">
          <Button
            variant="outline"
            onClick={handleBack}
            disabled={step === 1}
            className="border-border"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>

          {step < 4 ? (
            <Button
              onClick={handleNext}
              disabled={
                (step === 1 && !canProceedStep1) ||
                (step === 2 && !canProceedStep2) ||
                (step === 3 && !canProceedStep3)
              }
              className="bg-primary hover:bg-primary/90"
            >
              Continue
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          ) : (
            <Button
              onClick={handleCreateBaseline}
              disabled={loading}
              className="bg-primary hover:bg-primary/90"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Check className="w-4 h-4 mr-2" />
                  Create Baseline
                </>
              )}
            </Button>
          )}
        </div>
      </div>
    </div>
  );
};

export default WritingEvolutionBaseline;
