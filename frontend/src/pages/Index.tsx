import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Calendar, HeartPulse, Users, BarChart3, FileCheck, Target, PenTool } from "lucide-react";
import { UniversityPasswordModal } from "@/components/auth/UniversityPasswordModal";
import { TypingAnimation } from "@/components/TypingAnimation";
import { useToast } from "@/hooks/use-toast";

const Index = () => {
  const navigate = useNavigate();
  const [universityPasswordOpen, setUniversityPasswordOpen] = useState(false);
  const [expandedCard, setExpandedCard] = useState<number | null>(null);
  const { toast } = useToast();

  const features = [
    {
      icon: Calendar,
      title: "Generate Full PhD Timeline",
      description: "Upload your proposal and instantly generate a structured timeline with milestones.",
      route: "/timeline"
    },
    {
      icon: FileCheck,
      title: "Collaboration Tracker",
      description: "Capture your research journey collaboratively. Log events, verify contributions, and maintain transparent records with supervisors and co-authors.",
      route: "/collaboration-ledger",
      highlight: true
    },
    {
      icon: PenTool,
      title: "Writing Evolution",
      description: "Track your authorship continuity over time. Build a writing baseline and monitor how your academic voice develops throughout your PhD.",
      route: "/writing-evolution",
      highlight: true
    },
    {
      icon: HeartPulse,
      title: "PhD Doctor",
      description: "Evaluate research health, supervision cadence, and risk level with recommendations.",
      route: "/wellbeing"
    },
    {
      icon: Users,
      title: "Peer Network",
      description: "Find co-founders, jobs, and industry projects matched to your research profile.",
      route: "/network"
    },
    {
      icon: BarChart3,
      title: "Institutional Dashboard",
      description: "Real-time institutional analytics, risk, funding, and performance tracking.",
      requiresPassword: true
    },
    {
      icon: Target,
      title: "Your PhD Dashboard",
      description: "Your command center. Track funding, opportunities, deadlines, wellness, and get personalized recommendations.",
      route: "/profile-strength",
      subtitle: "Manage your entire PhD journey"
    }
  ];

  const handleFeatureClick = (feature: typeof features[0]) => {
    if (feature.requiresPassword) {
      setUniversityPasswordOpen(true);
    } else if (feature.route) {
      navigate(feature.route);
    }
  };

  return (
    <div className="min-h-screen bg-[#000000]">
      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 pt-32 pb-16">
        <div className="grid md:grid-cols-2 gap-8 items-center">
          <div className="text-center md:text-left">
            <h1 className="text-4xl md:text-6xl font-bold text-white mb-2 animate-fade-in relative inline-block">
              Powered by Frensei's{" "}
              <span className="relative">
                Penguin AI Engine
                <span className="absolute bottom-0 left-0 w-full h-0.5 bg-gradient-to-r from-[#DB5614] to-[#E69219]"></span>
              </span>
            </h1>
          </div>
          <div className="animate-fade-in" style={{ animationDelay: '0.2s' }}>
            <TypingAnimation />
          </div>
        </div>
      </section>

      {/* Feature Cards Section */}
      <section className="max-w-7xl mx-auto px-4 py-16">
        <h2 className="text-2xl font-semibold text-white text-center mb-8">
          Your Research Journey, Connected.
        </h2>
        <div className="flex flex-wrap justify-center gap-6 mb-8">
          {features.map((feature, index) => {
            const IconComponent = feature.icon;
            return (
              <Card
                key={index}
                onClick={() => handleFeatureClick(feature)}
                className={`bg-[#1E1E1E] border-2 cursor-pointer transition-all duration-300 hover:scale-[1.03] group w-full md:w-[calc(50%-12px)] lg:w-[calc(25%-18px)] ${
                  feature.highlight 
                    ? 'border-primary hover:border-primary shadow-[0_0_25px_rgba(230,146,25,0.55)]' 
                    : 'border-primary/40 hover:border-primary hover:shadow-[0_0_25px_rgba(230,146,25,0.55)]'
                }`}
              >
                <CardContent className="p-6 text-center">
                  <div className="mb-4 flex justify-center">
                    <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
                      <IconComponent className="w-8 h-8 text-primary" />
                    </div>
                  </div>
                  <h3 className="text-xl font-semibold text-white mb-3">
                    {feature.title}
                  </h3>
                  <p className="text-sm text-white/70 leading-relaxed">
                    {feature.description}
                  </p>
                </CardContent>
              </Card>
            );
          })}
        </div>

        <p className="text-center text-white/70 text-sm max-w-3xl mx-auto">
          Together these modules form Frensei, the world's first AI-driven Research Continuity Platform.
        </p>
      </section>

      {/* Future Innovation Roadmap Section */}
      <section className="max-w-7xl mx-auto px-4 py-16">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-3">
            Future Innovation Roadmap, Powered by Frensei's Data Flywheel
          </h2>
          <p className="text-white/80 text-lg">
            The data produced by Frensei's current features will enable the following tools.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {[
            {
              title: "Multilingual Research Integrity Checker™",
              body: "Ensures conceptual fidelity and ethical consistency during translation and rewriting, detects drift, bias, or misrepresentation across languages.",
              footer: "→ Creates a premium QA layer for trust and accuracy.",
              details: "This system analyzes source and translated texts using semantic embeddings and cross-lingual knowledge graphs. It flags conceptual drift by comparing argument structures, checks citations for accuracy across languages, and monitors tone shifts that could introduce bias. The engine integrates with existing collaboration tracker data to track changes over time and alert users to unintentional meaning shifts.",
              timeline: "12-16 months"
            },
            {
              title: "Context-Aware Translation Engine (CATE™)",
              body: "Translates meaning, not just words, using Frensei's semantic context graphs to preserve disciplinary nuance and cross-domain terminology.",
              footer: "→ Reinvents translation workflows into research-grade, AI-enhanced products.",
              details: "CATE leverages the PhD timeline and collaboration tracker to understand research context, field-specific terminology, and author intent. It maintains a dynamic terminology database built from millions of research documents, learns from user corrections, and provides confidence scores for each translation. The system suggests domain-appropriate alternatives and preserves methodological precision across 40+ languages.",
              timeline: "14-18 months"
            },
            {
              title: "Adaptive Editing Intelligence (AEI™)",
              body: "Learns from author behavior, reviewer feedback, and journal outcomes to deliver real-time, field-specific editing suggestions.",
              footer: "→ Turns static editing into a continuously learning assistant, driving repeat use.",
              details: "AEI ingests data from the wellbeing check-ins, supervision cadence patterns, and writing sessions logged in the collaboration tracker. It identifies when authors are struggling, suggests structural improvements based on successful publication patterns in the field, and adapts its tone based on career stage. The system learns which suggestions users accept/reject and refines recommendations accordingly.",
              timeline: "10-14 months"
            },
            {
              title: "AI Research Twin™",
              body: "A personalized research companion that evolves with each scholar's style, project rhythm, and domain knowledge.",
              footer: "→ Converts one-off tools into an always-on ecosystem, increasing lifetime value.",
              details: "The Research Twin synthesizes data from all Frensei modules to create a digital representation of each researcher. It learns writing patterns from the tracker, anticipates stress points from wellbeing data, understands funding cycles from the dashboard, and proactively suggests actions. It can draft emails to supervisors, recommend paper structures, and identify collaboration opportunities based on the peer network graph.",
              timeline: "18-24 months"
            },
            {
              title: "Corporate Research Insights Hub™",
              body: "Aggregates anonymized global editing and translation data to forecast emerging research topics and corporate innovation trends.",
              footer: "→ Opens a new enterprise subscription line for pharma, tech, and ESG clients.",
              details: "This B2B analytics platform aggregates anonymized patterns from Frensei's user base to identify trending methodologies, emerging cross-disciplinary connections, and geographic research clusters. It provides pharmaceutical companies early signals on therapeutic approaches, helps tech firms spot emerging AI applications, and enables ESG investors to track sustainability research momentum. All data is anonymized and aggregated to protect individual privacy.",
              timeline: "16-20 months"
            },
            {
              title: "Publisher Readiness Index™",
              body: "Scores manuscripts for clarity, novelty, and language quality using Frensei's semantic + supervision-risk signals.",
              footer: "→ Creates a B2B analytics channel for publishers and institutional partners.",
              details: "This scoring engine analyzes manuscripts using multiple signals: language clarity from CATE, conceptual integrity from the Integrity Checker, supervision quality signals from the collaboration tracker, and novelty detection through cross-referencing existing literature. It generates a multi-dimensional readiness score that predicts publication success and provides actionable improvement recommendations. Publishers can license this as a pre-screening tool.",
              timeline: "12-15 months"
            }
          ].map((item, index) => (
            <Card
              key={index}
              className="bg-[#0B0B0C] border-[#2A2A2D] rounded-2xl shadow-inner hover:border-primary/40 transition-all duration-300"
            >
              <CardContent className="p-6">
                <div className="flex items-start justify-between mb-3">
                  <div 
                    className="w-10 h-10 rounded-lg flex items-center justify-center"
                    style={{
                      background: 'linear-gradient(135deg, #FF7A18 0%, #FFB800 100%)'
                    }}
                  >
                    <Target className="w-5 h-5 text-white" />
                  </div>
                  <Badge variant="outline" className="text-xs border-primary/50 text-primary">
                    Coming Soon
                  </Badge>
                </div>
                <h3 className="text-lg font-semibold text-white mb-3">
                  {item.title}
                </h3>
                <p className="text-sm text-[#E5E7EB] leading-relaxed mb-4">
                  {item.body}
                </p>
                <p className="text-xs text-white/60 mb-4 italic">
                  {item.footer}
                </p>
                
                {expandedCard === index && (
                  <div className="mt-4 pt-4 border-t border-[#2A2A2D] animate-fade-in">
                    <h4 className="text-sm font-semibold text-white mb-2">How It Works</h4>
                    <p className="text-xs text-[#E5E7EB] leading-relaxed mb-4">
                      {item.details}
                    </p>
                  </div>
                )}
                
                <button
                  onClick={() => setExpandedCard(expandedCard === index ? null : index)}
                  className="text-sm text-primary hover:text-primary/80 transition-colors ml-auto block"
                >
                  {expandedCard === index ? "Show less ↑" : "Learn more →"}
                </button>
              </CardContent>
            </Card>
          ))}
        </div>

        <p className="text-center text-[#B3B3B7] text-xs max-w-4xl mx-auto">
          All modules are powered by Frensei's patented Adaptive Workflow Engine, ensuring exclusive access to research continuity data.
        </p>
      </section>

      {/* Footer / Founder Credit */}
      <footer className="mt-24 animate-fade-in">
        <div className="h-0.5 bg-gradient-to-r from-[#DB5614] to-[#E69219]"></div>
        <div className="bg-[#0E0E0E] py-12">
          <div className="max-w-4xl mx-auto px-4 text-center">
            <h3 className="text-2xl font-bold text-white mb-3">
              Dr. Syed Ali Adnan Rizvi
            </h3>
            <p className="text-lg text-white/90 mb-4">
              PhD (Trinity College Dublin) · Associate Professor of Entrepreneurship
            </p>
            <p className="text-sm text-white/80 mb-4">
              Proprietary process patents: CETA™ · CPA™ · SAL™ · LBP™ · DTSP™ · CCC™
            </p>
            <p className="text-xs text-white/70">
              © 2025 Frensei Ltd · Patent-protected · Not a ChatGPT wrapper
            </p>
          </div>
        </div>
      </footer>

      {/* University Password Modal */}
      <UniversityPasswordModal 
        open={universityPasswordOpen} 
        onOpenChange={setUniversityPasswordOpen} 
      />
    </div>
  );
};

export default Index;
