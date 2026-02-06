import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ProfileWheel } from "@/components/profile/ProfileWheel";
import { JourneyTimeline } from "@/components/profile/JourneyTimeline";
import { QuickStatsGrid } from "@/components/profile/QuickStatsGrid";
import { GoalsModule } from "@/components/profile/GoalsModule";
import { UniversityPolicyModule } from "@/components/profile/UniversityPolicyModule";
import { AINudgePanel } from "@/components/profile/AINudgePanel";
import { Clock, TrendingUp, AlertCircle } from "lucide-react";
import { toast } from "sonner";

const ProfileStrength = () => {
  const navigate = useNavigate();
  const [selectedSegment, setSelectedSegment] = useState<string | null>(null);

  // Mock data - replace with real data from your backend
  const userData = {
    name: "Research Student",
    program: "PhD in Data Science",
    year: "Year 2 – Data Analysis Phase",
    academicStage: "Data Collection",
    continuityStatus: "Stable",
    lastMeeting: "12 days ago",
    fundingRemaining: 8500,
    monthlyBurn: 1800,
    isBurnedOut: false,
    upcomingGrants: [
      { name: "NSF Graduate Research Fellowship", deadline: "Oct 18, 2024", match: 92 },
      { name: "Google PhD Fellowship", deadline: "Dec 1, 2024", match: 85 }
    ],
    upcomingConferences: [
      { name: "NeurIPS 2024", deadline: "May 22, 2024", type: "paper" },
      { name: "ICML 2024", deadline: "Feb 2, 2024", type: "paper" }
    ],
    needsCoAuthor: false,
    recommendedSkills: []
  };

  const wheelData = [
    { id: "academic", name: "Academic Progress", score: 75, color: "hsl(var(--success))" },
    { id: "publication", name: "Publication Activity", score: 72, color: "hsl(var(--success))" },
    { id: "collaboration", name: "Collaboration Health", score: 85, color: "hsl(var(--success))" },
    { id: "grants", name: "Grants & Opportunities", score: 45, color: "hsl(var(--destructive))" },
    { id: "wellbeing", name: "Well-being & Balance", score: 70, color: "hsl(var(--success))" },
    { id: "continuity", name: "Continuity", score: 80, color: "hsl(var(--success))" }
  ];

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case "stable": return "bg-success/20 text-success border-success/30";
      case "rising": return "bg-info/20 text-info border-info/30";
      case "needs attention": return "bg-warning/20 text-warning border-warning/30";
      default: return "bg-muted/20 text-muted-foreground border-muted/30";
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Main Content Container */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        
        {/* SECTION 1: HEADER */}
        <Card className="bg-card border-border/50 mb-8 overflow-hidden">
          <div className="bg-gradient-to-r from-[#FF7A18] to-[#FFB800] h-2"></div>
          <CardContent className="p-6">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
              <div className="flex-1">
                <h1 className="text-3xl font-bold text-foreground mb-2">Your PhD Dashboard</h1>
                <p className="text-muted-foreground text-lg mb-3">{userData.program} • {userData.year}</p>
                <div className="flex flex-wrap gap-2">
                  <Badge variant="outline" className="border-primary/50 text-primary">
                    {userData.academicStage}
                  </Badge>
                  <Badge variant="outline" className={getStatusColor(userData.continuityStatus)}>
                    <TrendingUp className="w-3 h-3 mr-1" />
                    {userData.continuityStatus}
                  </Badge>
                  <Badge variant="outline" className="border-border text-foreground">
                    <Clock className="w-3 h-3 mr-1" />
                    Last meeting: {userData.lastMeeting}
                  </Badge>
                </div>
              </div>
              <Button 
                onClick={() => {
                  toast.error("Database disconnected temporarily");
                }}
                className="bg-gradient-to-r from-[#FF7A18] to-[#FFB800] hover:opacity-90 text-white"
              >
                Open PhD Doctor
              </Button>
            </div>
          </CardContent>
        </Card>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Left Column - Main Content */}
          <div className="lg:col-span-2 space-y-8">
            
            {/* SECTION 2: CENTRAL PROFILE WHEEL */}
            <Card className="bg-card border-border/50">
              <CardContent className="p-6">
                <h2 className="text-2xl font-bold text-foreground mb-6">Your PhD Profile Wheel</h2>
                <ProfileWheel 
                  data={wheelData} 
                  onSegmentClick={setSelectedSegment}
                />
              </CardContent>
            </Card>

            {/* SECTION 3: JOURNEY TIMELINE STRIP */}
            <Card className="bg-card border-border/50">
              <CardContent className="p-6">
                <h2 className="text-2xl font-bold text-foreground mb-6">PhD Journey Timeline</h2>
                <JourneyTimeline currentStage="Data Collection" />
                <div className="mt-6 text-center">
                  <Button 
                    onClick={() => navigate("/collaboration-ledger")}
                    variant="outline"
                    className="border-primary text-primary hover:bg-primary/10"
                  >
                    Update Collaboration Tracker
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* SECTION 4: MONTHLY STIPEND */}
            <Card className="bg-card border-border/50">
              <CardContent className="p-6">
                <h2 className="text-2xl font-bold text-foreground mb-4">Monthly Stipend</h2>
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="p-4 bg-background/50 rounded-lg">
                    <p className="text-sm text-muted-foreground mb-1">Current Stipend</p>
                    <p className="text-3xl font-bold text-foreground">${userData.monthlyBurn.toLocaleString()}/month</p>
                  </div>
                  <div className="p-4 bg-background/50 rounded-lg">
                    <p className="text-sm text-muted-foreground mb-1">Supplement Your Income</p>
                    <p className="text-2xl font-bold text-foreground">With 4 hrs/week more</p>
                    <p className="text-xl font-semibold text-primary mt-1">
                      Add ${(4 * 4 * 25).toLocaleString()}/month
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                      At $25/hr • Available funds: ${userData.fundingRemaining.toLocaleString()}
                    </p>
                  </div>
                </div>
                {userData.fundingRemaining / userData.monthlyBurn < 6 && (
                  <div className="mt-4 p-4 bg-warning/10 border border-warning/30 rounded-lg">
                    <div className="flex items-start gap-3">
                      <AlertCircle className="w-5 h-5 text-warning mt-0.5" />
                      <div className="flex-1">
                        <p className="text-sm font-semibold text-warning mb-1">Funding Alert</p>
                        <p className="text-sm text-muted-foreground mb-3">
                          Your funds are running low. Consider short-term income opportunities:
                        </p>
                        <div className="space-y-2">
                          <Button 
                            variant="outline" 
                            size="sm"
                            onClick={() => toast.error("Database disconnected temporarily")}
                            className="w-full justify-start border-warning/50 text-warning hover:bg-warning/10"
                          >
                            Proofreading & Editing Gigs ($25-50/hr)
                          </Button>
                          <Button 
                            variant="outline" 
                            size="sm"
                            onClick={() => toast.error("Database disconnected temporarily")}
                            className="w-full justify-start border-warning/50 text-warning hover:bg-warning/10"
                          >
                            Data Analysis Projects ($30-60/hr)
                          </Button>
                          <Button 
                            variant="outline" 
                            size="sm"
                            onClick={() => toast.error("Database disconnected temporarily")}
                            className="w-full justify-start border-warning/50 text-warning hover:bg-warning/10"
                          >
                            Teaching Assistant Positions
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* SECTION 5: UPCOMING GRANTS */}
            <Card className="bg-card border-border/50">
              <CardContent className="p-6">
                <h2 className="text-2xl font-bold text-foreground mb-4">Upcoming Grant Opportunities</h2>
                {userData.upcomingGrants.length > 0 ? (
                  <div className="space-y-3">
                    {userData.upcomingGrants.map((grant, idx) => (
                      <div key={idx} className="p-4 bg-background/50 rounded-lg border border-border/50 hover:border-primary/50 transition-colors">
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex-1">
                            <h3 className="font-semibold text-foreground mb-1">{grant.name}</h3>
                            <p className="text-sm text-muted-foreground">Deadline: {grant.deadline}</p>
                          </div>
                          <div className="text-right">
                            <Badge variant="outline" className="border-success/50 text-success">
                              {grant.match}% match
                            </Badge>
                          </div>
                        </div>
                        <Button 
                          size="sm"
                          onClick={() => toast.error("Database disconnected temporarily")}
                          className="w-full mt-3 bg-gradient-to-r from-[#FF7A18] to-[#FFB800] hover:opacity-90 text-white"
                        >
                          Start Application
                        </Button>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-muted-foreground">No upcoming grants at this time.</p>
                )}
              </CardContent>
            </Card>

            {/* SECTION 6: CONFERENCES & PAPERS */}
            <Card className="bg-card border-border/50">
              <CardContent className="p-6">
                <h2 className="text-2xl font-bold text-foreground mb-4">Conferences & Paper Deadlines</h2>
                {userData.upcomingConferences.length > 0 ? (
                  <div className="space-y-3">
                    {userData.upcomingConferences.map((conf, idx) => (
                      <div key={idx} className="p-4 bg-background/50 rounded-lg border border-border/50">
                        <div className="flex items-center justify-between">
                          <div>
                            <h3 className="font-semibold text-foreground">{conf.name}</h3>
                            <p className="text-sm text-muted-foreground">Deadline: {conf.deadline}</p>
                          </div>
                          <Badge variant="outline" className="border-info/50 text-info">
                            {conf.type}
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-muted-foreground">No upcoming paper deadlines.</p>
                )}
              </CardContent>
            </Card>

            {/* SECTION 7: BURNOUT & CO-AUTHOR RECOMMENDATIONS */}
            {userData.isBurnedOut && (
              <Card className="bg-card border-border/50">
                <CardContent className="p-6">
                  <h2 className="text-2xl font-bold text-foreground mb-4">Collaboration Recommendation</h2>
                  <div className="p-4 bg-warning/10 border border-warning/30 rounded-lg">
                    <div className="flex items-start gap-3">
                      <AlertCircle className="w-5 h-5 text-warning mt-0.5" />
                      <div className="flex-1">
                        <p className="text-sm font-semibold text-warning mb-2">You may be experiencing burnout</p>
                        <p className="text-sm text-muted-foreground mb-3">
                          Consider finding a co-author to share the workload. Recommended skills:
                        </p>
                        <div className="flex flex-wrap gap-2 mb-3">
                          {userData.recommendedSkills.map((skill, idx) => (
                            <Badge key={idx} variant="outline" className="border-warning/50 text-warning">
                              {skill}
                            </Badge>
                          ))}
                        </div>
                        <Button 
                          size="sm"
                          onClick={() => toast.error("Database disconnected temporarily")}
                          className="w-full bg-gradient-to-r from-[#FF7A18] to-[#FFB800] hover:opacity-90 text-white"
                        >
                          Find Co-Authors with These Skills
                        </Button>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* SECTION 8: QUICK STATS CARDS */}
            <div>
              <h2 className="text-2xl font-bold text-foreground mb-4">Quick Stats</h2>
              <QuickStatsGrid />
            </div>

            {/* SECTION 9: GOALS MODULE */}
            <div>
              <h2 className="text-2xl font-bold text-foreground mb-4">Weekly Goals</h2>
              <GoalsModule />
            </div>

            {/* OPTIONAL MODULE: UNIVERSITY POLICY INSIGHTS */}
            <UniversityPolicyModule />
          </div>

          {/* Right Column - AI Nudges Panel */}
          <div className="lg:col-span-1">
            <div className="sticky top-24">
              <AINudgePanel />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfileStrength;
