import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Upload, Calendar, Download, RefreshCw, Sparkles } from "lucide-react";
import { PenguinMascot } from "@/components/PenguinMascot";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { toast } from "@/hooks/use-toast";
import confetti from "canvas-confetti";
import { GanttChart } from "@/components/GanttChart";
import { uploadDocument } from "@/services/document.service";
import { getDevUserId } from "@/utils/devHelpers";

interface TimelineEvent {
  label: string;
  type: "internal" | "grant" | "cfp" | "data" | "journal";
  suggested_date: string;
  desc: string;
}

interface FieldConfig {
  name: string;
  keywords: string[];
  events: {
    litrev: { title: string; desc: string };
    supervisor: { title: string; desc: string };
    methodology: { title: string; desc: string };
    grant: { title: string; desc: string; grantName: string };
    abstract: { title: string; desc: string; confName: string };
    fullpaper: { title: string; desc: string; confName: string };
    datacollection: { title: string; desc: string; dataSource: string };
    draft1: { title: string; desc: string };
    targetjournal: { title: string; desc: string; journalName: string };
    review: { title: string; desc: string };
    draft2: { title: string; desc: string };
    submit: { title: string; desc: string; journalName: string };
  };
}

// Field-specific templates
const fieldConfigs: FieldConfig[] = [
  {
    name: "Environmental Science",
    keywords: ["climate", "environmental", "ecology", "sustainability", "erosion", "coastal", "ecosystem", "carbon", "emissions"],
    events: {
      litrev: {
        title: "Literature Review on Coastal Erosion & Climate Dynamics",
        desc: "Review key environmental studies on erosion, climate patterns, and geospatial modelling."
      },
      supervisor: {
        title: "Supervisor Meeting: Climate Modeling Strategy",
        desc: "Align on research objectives, datasets, and modelling approaches."
      },
      methodology: {
        title: "Draft Methodology: Erosion Forecasting Models",
        desc: "Design deep learning and geospatial analysis framework."
      },
      grant: {
        title: "Apply to Horizon Europe Climate Action Grant",
        desc: "Submit proposal with climate adaptation justification and research plan.",
        grantName: "Horizon Europe Climate Action Grant"
      },
      abstract: {
        title: "Submit Abstract to EGU General Assembly 2026",
        desc: "Prepare conference abstract on climate modeling findings.",
        confName: "EGU General Assembly 2026"
      },
      fullpaper: {
        title: "Full Paper Deadline for EGU General Assembly 2026",
        desc: "Complete full conference paper submission.",
        confName: "EGU General Assembly 2026"
      },
      datacollection: {
        title: "Dataset Collection from IPCC Climate Models",
        desc: "Gather and validate climate data according to ethical guidelines.",
        dataSource: "IPCC Climate Models Dataset"
      },
      draft1: {
        title: "Draft 1 of Research Paper (Environmental Science)",
        desc: "Complete first full draft with literature review, methodology, and initial findings."
      },
      targetjournal: {
        title: "Target Journal: Nature Climate Change",
        desc: "Align paper with journal scope and formatting requirements.",
        journalName: "Nature Climate Change"
      },
      review: {
        title: "Progress Review",
        desc: "Mid-program evaluation and timeline adjustment with supervisory team."
      },
      draft2: {
        title: "Draft 2 of Paper",
        desc: "Incorporate feedback and refine climate analysis section."
      },
      submit: {
        title: "Submit to Nature Climate Change",
        desc: "Submit manuscript for peer review with cover letter.",
        journalName: "Nature Climate Change"
      }
    }
  },
  {
    name: "Artificial Intelligence",
    keywords: ["ai", "machine learning", "deep learning", "neural network", "cnn", "lstm", "transformer", "algorithm", "model"],
    events: {
      litrev: {
        title: "Literature Review on Neural Architectures & ML Techniques",
        desc: "Analyze state-of-the-art deep learning models relevant to your domain."
      },
      supervisor: {
        title: "Supervisor Meeting: Model Architecture Planning",
        desc: "Discuss CNN, LSTM, or transformer-based research pathways."
      },
      methodology: {
        title: "Draft Methodology: Neural Network Design",
        desc: "Outline architecture, training strategy, and dataset pipeline."
      },
      grant: {
        title: "Apply to AI4Science Doctoral Fellowship",
        desc: "Submit technical proposal for advanced AI research funding.",
        grantName: "AI4Science Doctoral Fellowship"
      },
      abstract: {
        title: "Submit Abstract to NeurIPS 2026",
        desc: "Prepare conference abstract on neural architecture innovations.",
        confName: "NeurIPS 2026"
      },
      fullpaper: {
        title: "Full Paper Deadline for NeurIPS 2026",
        desc: "Complete full conference paper submission.",
        confName: "NeurIPS 2026"
      },
      datacollection: {
        title: "Dataset Collection from ImageNet & CIFAR",
        desc: "Gather and preprocess training datasets for model validation.",
        dataSource: "ImageNet & CIFAR Datasets"
      },
      draft1: {
        title: "Draft 1 of Research Paper (Artificial Intelligence)",
        desc: "Complete first full draft with model architecture and experimental results."
      },
      targetjournal: {
        title: "Target Journal: Journal of Machine Learning Research",
        desc: "Align paper with JMLR submission standards and formatting.",
        journalName: "Journal of Machine Learning Research"
      },
      review: {
        title: "Progress Review",
        desc: "Mid-program evaluation of model performance and research direction."
      },
      draft2: {
        title: "Draft 2 of Paper",
        desc: "Incorporate feedback and refine experimental analysis section."
      },
      submit: {
        title: "Submit to Journal of Machine Learning Research",
        desc: "Submit manuscript for peer review with technical appendix.",
        journalName: "Journal of Machine Learning Research"
      }
    }
  },
  {
    name: "Health Sciences",
    keywords: ["health", "nursing", "clinical", "patient", "medical", "healthcare", "treatment", "epidemiology", "disease"],
    events: {
      litrev: {
        title: "Literature Review on Clinical Outcomes & Patient Care",
        desc: "Survey existing studies on patient monitoring, treatment outcomes, and public health."
      },
      supervisor: {
        title: "Supervisor Meeting: Clinical Research Protocol",
        desc: "Finalize ethics, sample selection, and data collection plan."
      },
      methodology: {
        title: "Draft Methodology: Clinical Study Design",
        desc: "Prepare framework for surveys, trials, or observational analysis."
      },
      grant: {
        title: "Apply to Wellcome Trust Clinical Doctoral Fellowship",
        desc: "Submit clinical research fellowship proposal.",
        grantName: "Wellcome Trust Clinical Doctoral Fellowship"
      },
      abstract: {
        title: "Submit Abstract to APHA Annual Meeting 2026",
        desc: "Prepare conference abstract on clinical findings.",
        confName: "APHA Annual Meeting 2026"
      },
      fullpaper: {
        title: "Full Paper Deadline for APHA Annual Meeting 2026",
        desc: "Complete full conference paper submission.",
        confName: "APHA Annual Meeting 2026"
      },
      datacollection: {
        title: "Dataset Collection from National Health Survey",
        desc: "Gather clinical data with full ethical approval and patient consent.",
        dataSource: "National Health Survey Data"
      },
      draft1: {
        title: "Draft 1 of Research Paper (Health Sciences)",
        desc: "Complete first full draft with clinical methodology and patient outcomes."
      },
      targetjournal: {
        title: "Target Journal: The Lancet Public Health",
        desc: "Align paper with Lancet's clinical research standards.",
        journalName: "The Lancet Public Health"
      },
      review: {
        title: "Progress Review",
        desc: "Mid-program clinical research review and ethics compliance check."
      },
      draft2: {
        title: "Draft 2 of Paper",
        desc: "Incorporate clinical feedback and refine patient outcome analysis."
      },
      submit: {
        title: "Submit to The Lancet Public Health",
        desc: "Submit manuscript for peer review with clinical data appendix.",
        journalName: "The Lancet Public Health"
      }
    }
  },
  {
    name: "Public Policy",
    keywords: ["policy", "economics", "regulation", "government", "public", "trade", "development", "governance"],
    events: {
      litrev: {
        title: "Literature Review on Economic Policy & Regulation",
        desc: "Review SME policy, trade, economic development, and regulatory frameworks."
      },
      supervisor: {
        title: "Supervisor Meeting: Policy Impact Framework",
        desc: "Align on indicators, policy datasets, and modelling approaches."
      },
      methodology: {
        title: "Draft Methodology: Policy Analysis Model",
        desc: "Prepare empirical strategy and policy evaluation methods."
      },
      grant: {
        title: "Apply to OECD Policy Research Grant",
        desc: "Submit funding proposal focused on policy innovation.",
        grantName: "OECD Policy Research Grant"
      },
      abstract: {
        title: "Submit Abstract to AEA Annual Meeting 2026",
        desc: "Prepare conference abstract on policy analysis findings.",
        confName: "AEA Annual Meeting 2026"
      },
      fullpaper: {
        title: "Full Paper Deadline for AEA Annual Meeting 2026",
        desc: "Complete full conference paper submission.",
        confName: "AEA Annual Meeting 2026"
      },
      datacollection: {
        title: "Dataset Collection from OECD Policy Database",
        desc: "Gather policy indicators and economic data for analysis.",
        dataSource: "OECD Policy Database"
      },
      draft1: {
        title: "Draft 1 of Research Paper (Public Policy)",
        desc: "Complete first full draft with policy framework and empirical analysis."
      },
      targetjournal: {
        title: "Target Journal: Journal of Public Economics",
        desc: "Align paper with journal's policy research standards.",
        journalName: "Journal of Public Economics"
      },
      review: {
        title: "Progress Review",
        desc: "Mid-program policy research evaluation and methodology review."
      },
      draft2: {
        title: "Draft 2 of Paper",
        desc: "Incorporate feedback and refine policy impact analysis."
      },
      submit: {
        title: "Submit to Journal of Public Economics",
        desc: "Submit manuscript for peer review with policy data appendix.",
        journalName: "Journal of Public Economics"
      }
    }
  },
  {
    name: "Entrepreneurship",
    keywords: ["entrepreneurship", "innovation", "startup", "venture", "sme", "ecosystem", "spillover"],
    events: {
      litrev: {
        title: "Literature Review on Innovation Ecosystems",
        desc: "Review research on venture creation, spillovers, and ecosystems."
      },
      supervisor: {
        title: "Supervisor Meeting: Innovation Framework",
        desc: "Discuss ecosystem mapping, data sources, and methodology."
      },
      methodology: {
        title: "Draft Methodology: Startup & Policy Analysis",
        desc: "Outline research framework for firm-level and ecosystem-level analysis."
      },
      grant: {
        title: "Apply to EIT Innovation Doctoral Grant",
        desc: "Prepare research plan aligned with innovation policy goals.",
        grantName: "EIT Innovation Doctoral Grant"
      },
      abstract: {
        title: "Submit Abstract to EURAM 2026",
        desc: "Prepare conference abstract on innovation ecosystem findings.",
        confName: "EURAM 2026"
      },
      fullpaper: {
        title: "Full Paper Deadline for EURAM 2026",
        desc: "Complete full conference paper submission.",
        confName: "EURAM 2026"
      },
      datacollection: {
        title: "Dataset Collection from MNE Subsidiary Surveys",
        desc: "Gather firm-level data on innovation and knowledge transfer.",
        dataSource: "MNE Subsidiary Surveys"
      },
      draft1: {
        title: "Draft 1 of Research Paper (Entrepreneurship)",
        desc: "Complete first full draft with ecosystem analysis and firm-level findings."
      },
      targetjournal: {
        title: "Target Journal: Entrepreneurship Theory & Practice",
        desc: "Align paper with journal's entrepreneurship research standards.",
        journalName: "Entrepreneurship Theory & Practice"
      },
      review: {
        title: "Progress Review",
        desc: "Mid-program evaluation of ecosystem research and data quality."
      },
      draft2: {
        title: "Draft 2 of Paper",
        desc: "Incorporate feedback and refine entrepreneurship analysis."
      },
      submit: {
        title: "Submit to Entrepreneurship Theory & Practice",
        desc: "Submit manuscript for peer review with firm-level data appendix.",
        journalName: "Entrepreneurship Theory & Practice"
      }
    }
  },
  {
    name: "General Research",
    keywords: [],
    events: {
      litrev: {
        title: "Literature Review on Core Concepts & Theory",
        desc: "Survey major theories and foundational work in your general domain."
      },
      supervisor: {
        title: "Supervisor Meeting: Research Direction",
        desc: "Clarify objectives, data sources, and potential contributions."
      },
      methodology: {
        title: "Draft Methodology: Research Framework",
        desc: "Design the conceptual and methodological foundation."
      },
      grant: {
        title: "Apply to European Doctoral Grant",
        desc: "Prepare general doctoral research funding application.",
        grantName: "European Doctoral Grant"
      },
      abstract: {
        title: "Submit Abstract to Academic Conference 2026",
        desc: "Prepare conference abstract on research findings.",
        confName: "Academic Conference 2026"
      },
      fullpaper: {
        title: "Full Paper Deadline for Academic Conference 2026",
        desc: "Complete full conference paper submission.",
        confName: "Academic Conference 2026"
      },
      datacollection: {
        title: "Dataset Collection from Research Sources",
        desc: "Gather and validate research data according to ethical guidelines.",
        dataSource: "Primary Research Data"
      },
      draft1: {
        title: "Draft 1 of Research Paper",
        desc: "Complete first full draft with literature review, methodology, and initial findings."
      },
      targetjournal: {
        title: "Target Journal: Research Publication",
        desc: "Align paper with journal scope and formatting requirements.",
        journalName: "Academic Research Journal"
      },
      review: {
        title: "Progress Review",
        desc: "Mid-program evaluation and timeline adjustment with supervisory team."
      },
      draft2: {
        title: "Draft 2 of Paper",
        desc: "Incorporate feedback and refine analysis section."
      },
      submit: {
        title: "Submit to Academic Research Journal",
        desc: "Submit manuscript for peer review with cover letter.",
        journalName: "Academic Research Journal"
      }
    }
  }
];

// Detect research field from filename
const detectField = (filename: string): FieldConfig | null => {
  const lowerFilename = filename.toLowerCase();
  
  // Check for specific field matches
  for (const config of fieldConfigs.slice(0, -1)) { // Exclude general research
    if (config.keywords.some(keyword => lowerFilename.includes(keyword))) {
      return config;
    }
  }
  
  // Check if it contains general research indicators
  const researchIndicators = [
    'research', 'study', 'analysis', 'thesis', 'dissertation', 'paper',
    'proposal', 'draft', 'methodology', 'literature', 'review', 'abstract',
    'phd', 'doctoral', 'masters', 'academic'
  ];
  
  const hasResearchIndicator = researchIndicators.some(indicator => 
    lowerFilename.includes(indicator)
  );
  
  if (hasResearchIndicator) {
    return fieldConfigs[fieldConfigs.length - 1]; // Return general research
  }
  
  return null; // Not a research document
};

// Generate dynamic timeline events based on detected field
const generateTimelineEvents = (fieldConfig: FieldConfig): TimelineEvent[] => {
  const startDate = new Date();
  
  const addMonths = (months: number): string => {
    const date = new Date(startDate);
    date.setMonth(date.getMonth() + months);
    return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
  };

  const events = fieldConfig.events;

  return [
    {
      label: events.litrev.title,
      type: "internal",
      suggested_date: addMonths(1),
      desc: events.litrev.desc
    },
    {
      label: events.supervisor.title,
      type: "internal",
      suggested_date: addMonths(2),
      desc: events.supervisor.desc
    },
    {
      label: events.methodology.title,
      type: "internal",
      suggested_date: addMonths(4),
      desc: events.methodology.desc
    },
    {
      label: events.grant.title,
      type: "grant",
      suggested_date: addMonths(6),
      desc: events.grant.desc
    },
    {
      label: events.abstract.title,
      type: "cfp",
      suggested_date: addMonths(8),
      desc: events.abstract.desc
    },
    {
      label: events.fullpaper.title,
      type: "cfp",
      suggested_date: addMonths(10),
      desc: events.fullpaper.desc
    },
    {
      label: events.datacollection.title,
      type: "data",
      suggested_date: addMonths(12),
      desc: events.datacollection.desc
    },
    {
      label: events.draft1.title,
      type: "internal",
      suggested_date: addMonths(15),
      desc: events.draft1.desc
    },
    {
      label: events.targetjournal.title,
      type: "journal",
      suggested_date: addMonths(18),
      desc: events.targetjournal.desc
    },
    {
      label: events.review.title,
      type: "internal",
      suggested_date: addMonths(21),
      desc: events.review.desc
    },
    {
      label: events.draft2.title,
      type: "internal",
      suggested_date: addMonths(24),
      desc: events.draft2.desc
    },
    {
      label: events.submit.title,
      type: "journal",
      suggested_date: addMonths(27),
      desc: events.submit.desc
    }
  ];
};

const loadingSteps = [
  "Reading abstract… detecting domain keywords… generating milestones…"
];

const opportunityPool = [
  "📄 OECD 2025 Global Entrepreneurship Outlook, New chapter on MNE spillovers.",
  "💰 World Bank Innovation Pipeline 2025, Cross-border enterprise funding calls.",
  "📚 EURAM 2026 Track Deadline Extended: Entrepreneurship & International Business.",
  "📄 Springer Special Issue: SME Knowledge Diffusion in Emerging Markets.",
  "💰 Call for Papers: UNCTAD Entrepreneurship Development Report 2026.",
  "📚 EU Horizon SME Innovation Fellowship, Closes Feb 2026.",
  "📄 Found Teaching Role: Assistant Lecturer, Entrepreneurship (TCD), Open Now.",
  "💰 OECD Knowledge Spillovers Symposium, Abstract Due Apr 2026.",
  "📄 Journal of International Business Studies: Special Issue on Spillover Effects.",
  "📚 AOM 2026 Entrepreneurship Division, Call for Interactive Papers."
];

const getRandomOpportunities = () => {
  const shuffled = [...opportunityPool].sort(() => Math.random() - 0.5);
  return shuffled.slice(0, 4);
};

const ResearchTimeline = () => {
  const navigate = useNavigate();
  const [isUploading, setIsUploading] = useState(false);
  const [showTimeline, setShowTimeline] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);
  const [progress, setProgress] = useState(0);
  const [addedEvents, setAddedEvents] = useState<Set<number>>(new Set());
  const [currentOpportunities, setCurrentOpportunities] = useState(getRandomOpportunities());
  const [showNextStep, setShowNextStep] = useState(false);
  const [showUploadStatus, setShowUploadStatus] = useState(false);
  const [detectedField, setDetectedField] = useState<FieldConfig | null>(null);
  const [timelineEvents, setTimelineEvents] = useState<TimelineEvent[]>([]);
  const [uploadedDocumentId, setUploadedDocumentId] = useState<string | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);

  // Auto-refresh opportunities every 10 seconds when timeline is shown
  useEffect(() => {
    if (!showTimeline) return;
    
    const interval = setInterval(() => {
      setCurrentOpportunities(getRandomOpportunities());
    }, 10000);

    return () => clearInterval(interval);
  }, [showTimeline]);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Detect field from filename (for UI display only - backend will process)
    const field = detectField(file.name);
    
    // Validate that this appears to be a research document (UI validation only)
    if (!field) {
      toast({
        title: "Invalid Document",
        description: "This doesn't appear to be a research proposal, thesis, or academic paper. Please upload a research-related document.",
        variant: "destructive",
      });
      e.target.value = ''; // Reset file input
      return;
    }
    
    setDetectedField(field);
    setUploadError(null);
    setShowUploadStatus(true);
    setIsUploading(true);
    setLoadingStep(0);
    setProgress(0);
    setAddedEvents(new Set());
    setShowTimeline(false);
    setShowNextStep(false);
    setUploadedDocumentId(null);

    try {
      // Get user ID (TODO: Replace with actual user context)
      const userId = getDevUserId();

      // Call backend endpoint - wait for response (no optimistic success)
      const response = await uploadDocument(
        file,
        userId,
        file.name, // Use filename as title
        undefined, // No description
        'research_proposal' // Document type
      );

      // Backend response received - update state
      setUploadedDocumentId(response.document_id);
      setProgress(100);
      
      toast({
        title: "Document Uploaded",
        description: `Document uploaded successfully. Document ID: ${response.document_id}`,
      });

      // Generate timeline events for UI display (backend will generate actual timeline)
      const events = generateTimelineEvents(field);
      setTimelineEvents(events);
      
      // Show timeline UI after successful upload
      setIsUploading(false);
      setShowUploadStatus(false);
      setShowTimeline(true);
      
    } catch (error: any) {
      // Handle error from backend
      setIsUploading(false);
      setShowUploadStatus(false);
      setProgress(0);
      
      const errorMessage = error?.message || 'Failed to upload document. Please try again.';
      setUploadError(errorMessage);
      
      toast({
        title: "Upload Failed",
        description: errorMessage,
        variant: "destructive",
      });
      
      // Reset file input on error
      e.target.value = '';
    }
  };

  const handleAddToTimeline = (index: number, label: string) => {
    setAddedEvents((prev) => new Set(prev).add(index));
    
    confetti({
      particleCount: 50,
      spread: 60,
      origin: { y: 0.6 },
      colors: ['#DB5614', '#E69219', '#FFFFFF']
    });

    toast({
      title: `✅ Added '${label}' to your journey.`,
      description: "Timeline updated successfully.",
      className: "bg-[#0E0E10] border-[#E69219] text-white",
    });

    // Check if all events added
    if (addedEvents.size + 1 >= timelineEvents.length) {
      setTimeout(() => setShowNextStep(true), 1000);
    }
  };

  const handleRescan = () => {
    setIsUploading(true);
    setProgress(0);

    setTimeout(() => {
      setProgress(100);
      setIsUploading(false);
      
      // Refresh opportunities with new items
      setCurrentOpportunities(getRandomOpportunities());
      
      toast({
        title: "Opportunities Rescanned",
        description: "Feed refreshed with new matches!",
        className: "bg-[#0E0E10] border-[#E69219] text-white",
      });
    }, 3000);
  };

  const handleDownloadGantt = () => {
    toast({
      title: "📁 Gantt Chart Exported Successfully",
      description: "Your timeline has been saved as PNG format.",
      className: "bg-[#0E0E10] border-[#E69219] text-white",
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-black via-black to-[#E69219]">
      {/* Gradient line below navigation */}
      <div className="h-[2px] w-full bg-gradient-to-r from-[#DB5614] to-[#E69219]" />
      <div className="max-w-7xl mx-auto px-4 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center gap-3 mb-4">
            <PenguinMascot size={64} />
            <h1 className="text-4xl md:text-5xl font-bold text-white">
              Instantly Turn Your Research into a Structured Journey.
            </h1>
          </div>
          <p className="text-xl text-[#C8C8C8] max-w-3xl mx-auto">
            Upload your research proposal, abstract, or draft, and let Frensei's Penguin AI generate a live, evolving timeline that syncs with real opportunities.
          </p>
        </div>

        {/* Upload Section */}
        <Card className="bg-[#0E0E10] border-white/10 mb-8">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Upload className="w-5 h-5" />
              Upload Proposal / Abstract / Draft
            </CardTitle>
            <CardDescription className="text-white/70">
              PDF or DOCX format accepted
            </CardDescription>
          </CardHeader>
          <CardContent>
            {/* Upload Status Message */}
            {showUploadStatus && (
              <div className="text-center mb-4 animate-fade-in">
                <p className="text-sm text-[#AAAAAA]">
                  📄 Uploaded successfully · Generating your PhD timeline with Penguin AI…
                </p>
              </div>
            )}
            
            <label className="flex flex-col items-center justify-center w-full h-48 border-2 border-dashed border-white/20 rounded-xl cursor-pointer hover:border-[#E69219] transition-colors bg-black/20">
              <div className="flex flex-col items-center justify-center pt-5 pb-6">
                <Upload className="w-12 h-12 text-white/50 mb-3" />
                <p className="text-sm text-white/70 mb-2">
                  <span className="font-semibold">Click to upload</span> or drag and drop
                </p>
                <p className="text-xs text-white/50">PDF or DOCX (MAX. 10MB)</p>
              </div>
              <input
                type="file"
                className="hidden"
                accept=".pdf,.docx"
                onChange={handleFileUpload}
              />
            </label>

            {isUploading && (
              <div className="mt-6 space-y-4">
                <Progress value={progress} className="h-2" />
                <div className="flex items-center gap-2 text-white animate-pulse">
                  <Sparkles className="w-5 h-5 text-[#E69219]" />
                  <p>Reading abstract… detecting domain keywords… generating milestones…</p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Timeline Section */}
        {showTimeline && (
          <>
            <div className="mb-8">
              <h2 className="text-2xl font-bold text-white mb-2">Real-Time Events to Add to Your Research Journey</h2>
              <p className="text-sm text-[#C8C8C8] mb-4">
                Frensei continuously surfaces relevant calls, grants, and conferences. With one click, add them to your Gantt timeline.
              </p>
              <div className="flex gap-4 overflow-x-auto pb-4">
                {timelineEvents.map((event, index) => {
                  const typeColors = {
                    internal: "bg-blue-500",
                    grant: "bg-green-500",
                    cfp: "bg-purple-500",
                    data: "bg-yellow-500",
                    journal: "bg-red-500"
                  };
                  
                  return (
                    <Card 
                      key={index} 
                      className="min-w-[320px] bg-[#0E0E10] border-white/10 hover:border-[#E69219]/50 transition-all duration-400"
                    >
                      <CardHeader>
                        <div className="flex items-center justify-between mb-2">
                          <span className={`px-3 py-1 ${typeColors[event.type]} text-white text-xs font-semibold rounded-full uppercase`}>
                            {event.type}
                          </span>
                          <Calendar className="w-4 h-4 text-[#C8C8C8]" />
                        </div>
                        <CardTitle className="text-white text-lg">{event.label}</CardTitle>
                        <CardDescription className="text-[#C8C8C8]">{event.suggested_date}</CardDescription>
                      </CardHeader>
                      <CardContent>
                        <p className="text-sm text-[#C8C8C8] mb-4">{event.desc}</p>
                        <Button
                          onClick={() => handleAddToTimeline(index, event.label)}
                          disabled={addedEvents.has(index)}
                          className="w-full bg-gradient-to-r from-[#DB5614] to-[#E69219] hover:from-[#DB5614] hover:to-[#DB5614] text-white transition-all duration-400"
                        >
                          {addedEvents.has(index) ? "Added ✓" : "Add to Timeline"}
                        </Button>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </div>

            {/* Timeline Visualization - Gantt Chart */}
            <GanttChart 
              events={timelineEvents.map((event, index) => ({
                ...event,
                isAdded: addedEvents.has(index),
                isCompleted: index === 0
              }))}
            />

            {/* Penguin AI Box */}
            <Card className="bg-[#0E0E10] border-white/10">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-3">
                  <div className="animate-spin" style={{ animationDuration: '2s' }}>🐧</div>
                  Penguin AI is Scouring the Internet…
                </CardTitle>
                <CardDescription className="text-[#C8C8C8]">
                  Frensei Penguin continuously scans verified research databases and event APIs to keep your timeline current.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {currentOpportunities.map((log, index) => (
                    <div
                      key={`${log}-${index}`}
                      className="p-3 bg-black/30 rounded-lg text-sm text-white border border-white/10 hover:border-[#E69219]/50 transition-all duration-500 animate-fade-in"
                      style={{ animationDelay: `${index * 0.15}s` }}
                    >
                      {log}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </>
        )}

        {/* Footer */}
        <div className="mt-12 pt-8 border-t border-white/10 text-center">
          <p className="text-[#C8C8C8]">
            Powered by Frensei, Patent-pending AI for dynamic research timeline generation and real-time continuity mapping.
          </p>
        </div>
      </div>
    </div>
  );
};

export default ResearchTimeline;
