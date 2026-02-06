import { useNavigate } from "react-router-dom";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { TrendingUp, Calendar, DollarSign, Sparkles, Users, FileText, Clock } from "lucide-react";
import { useEffect, useState } from "react";
import { toast } from "sonner";

interface NudgeItem {
  id: string;
  icon: any;
  title: string;
  message: string;
  action: string;
  route: string;
  color: string;
}

export const AINudgePanel = () => {
  const navigate = useNavigate();
  const [nudges, setNudges] = useState<NudgeItem[]>([]);

  useEffect(() => {
    const loadNudges = async () => {
      // TODO: Replace with your backend API call
      const storedEvents = localStorage.getItem("collaboration_events");
      const events = storedEvents ? JSON.parse(storedEvents) : [];

      if (events && events.length > 0) {
        // Extract keywords and themes from event summaries
        const allText = events.map(e => `${e.summary} ${e.event_type}`).join(" ").toLowerCase();
        const keywords = extractKeywords(allText);

        // Generate nudges based on extracted keywords
        const dynamicNudges: NudgeItem[] = [];

        // Check for draft/submission mentions
        if (keywords.includes("draft") || keywords.includes("submit") || keywords.includes("paper")) {
          dynamicNudges.push({
            id: "paper",
            icon: FileText,
            title: "Paper Progress",
            message: "You've been working on drafts. Consider finalizing submissions soon.",
            action: "Update Collaboration Tracker",
            route: "/collaboration-ledger",
            color: "text-info"
          });
        }

        // Check for deadline/delay mentions
        if (keywords.includes("delay") || keywords.includes("deadline") || keywords.includes("revision")) {
          dynamicNudges.push({
            id: "deadline",
            icon: Clock,
            title: "Timeline Alert",
            message: "Recent delays noted. Review your timeline to stay on track.",
            action: "Update Collaboration Tracker",
            route: "/collaboration-ledger",
            color: "text-warning"
          });
        }

        // Check for collaboration mentions
        if (keywords.includes("meeting") || keywords.includes("discussion") || keywords.includes("coauthor")) {
          dynamicNudges.push({
            id: "collaboration",
            icon: Users,
            title: "Collaboration Update",
            message: "Active discussions detected. Keep momentum with your co-authors.",
            action: "View Network",
            route: "/peer-network",
            color: "text-success"
          });
        }

        // Check for feedback mentions
        if (keywords.includes("feedback") || keywords.includes("review")) {
          dynamicNudges.push({
            id: "feedback",
            icon: TrendingUp,
            title: "Feedback Received",
            message: "Recent feedback in your journey. Address key points soon.",
            action: "Update Collaboration Tracker",
            route: "/collaboration-ledger",
            color: "text-info"
          });
        }

        // Add funding nudge if few events (might need support)
        if (events.length < 5) {
          dynamicNudges.push({
            id: "funding",
            icon: DollarSign,
            title: "Build Your Journey",
            message: "Document more milestones to strengthen grant applications.",
            action: "Update Collaboration Tracker",
            route: "/collaboration-ledger",
            color: "text-warning"
          });
        }

        setNudges(dynamicNudges.slice(0, 5)); // Limit to 5 nudges
      } else {
        // Default nudges if no events
        setNudges([
          {
            id: "start",
            icon: Sparkles,
            title: "Get Started",
            message: "Upload your research journey to receive personalized insights.",
            action: "Upload Journey",
            route: "/timeline",
            color: "text-primary"
          }
        ]);
      }
    };

    loadNudges();
  }, []);

  const extractKeywords = (text: string): string[] => {
    const commonWords = ["the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"];
    return text
      .split(/\s+/)
      .filter(word => word.length > 3 && !commonWords.includes(word))
      .filter((word, index, self) => self.indexOf(word) === index);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 mb-4">
        <Sparkles className="w-5 h-5 text-primary" />
        <h3 className="text-lg font-semibold text-foreground">AI Nudges</h3>
      </div>
      
      {nudges.map((nudge) => {
        const IconComponent = nudge.icon;
        return (
          <Card
            key={nudge.id}
            className="bg-card/50 border-border/50 hover:bg-card/70 transition-all duration-300 hover:shadow-[0_0_15px_rgba(230,146,25,0.2)] group"
          >
            <CardContent className="p-4">
              <div className="flex items-start gap-3 mb-3">
                <div className={`${nudge.color} group-hover:scale-110 transition-transform`}>
                  <IconComponent className="w-5 h-5" />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-semibold text-foreground mb-1">{nudge.title}</p>
                  <p className="text-xs text-muted-foreground">{nudge.message}</p>
                </div>
              </div>
              <Button
                onClick={() => {
                  if (nudge.route === "/collaboration-ledger" || nudge.route === "/timeline" || nudge.route === "/wellbeing") {
                    navigate(nudge.route);
                  } else {
                    toast.error("Database disconnected temporarily");
                  }
                }}
                size="sm"
                variant="outline"
                className="w-full border-primary/50 text-primary hover:bg-primary/10 text-xs"
              >
                {nudge.action}
              </Button>
            </CardContent>
          </Card>
        );
      })}

      <Card className="bg-gradient-to-br from-primary/10 to-accent/10 border-primary/30">
        <CardContent className="p-4 text-center">
          <Sparkles className="w-8 h-8 text-primary mx-auto mb-2" />
          <p className="text-xs text-muted-foreground mb-3">
            Get personalized insights based on your PhD journey
          </p>
          <Button
            onClick={() => navigate("/wellbeing")}
            size="sm"
            className="w-full bg-gradient-to-r from-[#FF7A18] to-[#FFB800] hover:opacity-90 text-white text-xs"
          >
            Run PhD Health Check
          </Button>
        </CardContent>
      </Card>
    </div>
  );
};
