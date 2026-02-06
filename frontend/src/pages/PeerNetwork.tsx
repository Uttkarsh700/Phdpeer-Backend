import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Progress } from "@/components/ui/progress";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { toast } from "sonner";
import { Building2, Users, Rocket, Briefcase, Zap, Check, DollarSign } from "lucide-react";
import confetti from "canvas-confetti";

const industryProjects = [
  { company: "Intel", project: "AI Edge Device Optimization", funding: "€45,000", location: "Dublin, Ireland", matchScore: "88%" },
  { company: "Pfizer", project: "Clinical Data Predictive Modeling", funding: "€60,000", location: "Cambridge, UK", matchScore: "82%" },
  { company: "Cisco", project: "Adaptive Network Security for IoT", funding: "€40,000", location: "San Jose, USA", matchScore: "90%" },
  { company: "Medtronic", project: "Digital Twin Modeling for Cardiac Devices", funding: "€35,000", location: "Galway, Ireland", matchScore: "76%" },
  { company: "IBM Research", project: "Quantum Simulation for Drug Discovery", funding: "€55,000", location: "Zurich, Switzerland", matchScore: "84%" }
];

const entrepreneurshipOpps = [
  { title: "Horizon Europe MSCA Innovation Fund", deadline: "Apply by Jan 2026", funding: "Up to €150,000" },
  { title: "Enterprise Ireland Commercialisation Support", deadline: "Rolling", funding: "€50,000 - €100,000" },
  { title: "MIT Solve Global Challenges", deadline: "Apply Now", funding: "$10,000 - $100,000" }
];

const gigListings = [
  { service: "Proofreading", client: "Nature Partner Journals", rate: "€45/hr", location: "Remote" },
  { service: "Statistical Review", client: "Wiley Research", rate: "€60/hr", location: "Hybrid" },
  { service: "Grant Proposal Drafting", client: "Elsevier Connect", rate: "€70/hr", location: "Remote" }
];

const peerMatches = [
  { name: "Dr. Lucas Moretti", university: "University of Milan", focus: "Adaptive Tutoring Systems", match: "91%", availability: "Tue 15:00 GMT" },
  { name: "Dr. Sara Nguyen", university: "University of Toronto", focus: "AI Assessment Tools", match: "86%", availability: "Wed 11:00 GMT" },
  { name: "Dr. Ravi Menon", university: "IIT Madras", focus: "Predictive Learning Analytics", match: "84%", availability: "Thu 09:30 GMT" }
];

const pendingInvitations = [
  { name: "Dr. Isabella Cruz", university: "Oxford University", topic: "AI Ethics in Education", time: "Oct 14 @ 10:00 GMT" },
  { name: "Dr. Jun Park", university: "KAIST", topic: "LLMs for STEM Assessment", note: "Requested collaboration on RCI dataset" }
];

const aiUpdates = [
  { time: "12:21", text: "🔍 Matched 3 new peers in Data Science." },
  { time: "12:23", text: "💼 Pfizer posted a new Data Modeling project." },
  { time: "12:24", text: "📅 You received 2 new meeting requests." },
  { time: "12:26", text: "🔍 New match: Climate Science researcher in Berlin." },
  { time: "12:28", text: "💼 Cisco posted a new AI Security Project." },
  { time: "12:30", text: "🚀 Enterprise Ireland grant opens next week." }
];

const grantOpportunities = [
  { 
    title: "EU Horizon Europe MSCA Fellowship", 
    funding: "€150,000 - €200,000", 
    deadline: "Sep 2025",
    contact: "Prof. Michael O'Sullivan",
    institution: "Trinity College Dublin",
    match: "94%"
  },
  { 
    title: "Irish Research Council Government of Ireland Postdoctoral Fellowship", 
    funding: "€40,000/year", 
    deadline: "Nov 2025",
    contact: "Dr. Sarah Bennett",
    institution: "University College Cork",
    match: "89%"
  },
  { 
    title: "Science Foundation Ireland Starting Investigator Research Grant", 
    funding: "€500,000 - €1M", 
    deadline: "Jan 2026",
    contact: "Prof. James McCarthy",
    institution: "University of Galway",
    match: "91%"
  },
  { 
    title: "ERC Starting Grant", 
    funding: "€1.5M", 
    deadline: "Oct 2025",
    contact: "Prof. Elena Rossi",
    institution: "European Research Council",
    match: "87%"
  }
];

export default function PeerNetwork() {
  const [showModal, setShowModal] = useState(false);
  const [modalContent, setModalContent] = useState("");
  const [findingPeer, setFindingPeer] = useState(false);
  const [peerFound, setPeerFound] = useState(false);
  const [currentUpdate, setCurrentUpdate] = useState(0);
  const [showCalendarModal, setShowCalendarModal] = useState(false);
  const [selectedPeer, setSelectedPeer] = useState<string>("");
  const [scanningStage, setScanningStage] = useState(0);
  const [feedUpdates, setFeedUpdates] = useState(aiUpdates);
  const [appliedGigs, setAppliedGigs] = useState<number[]>([]);
  const [inviteSentPeers, setInviteSentPeers] = useState<number[]>([]);
  const [applyingToProject, setApplyingToProject] = useState<number | null>(null);
  const [acceptedInvitations, setAcceptedInvitations] = useState<number[]>([]);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentUpdate((prev) => (prev + 1) % feedUpdates.length);
    }, 3000);
    return () => clearInterval(interval);
  }, [feedUpdates]);

  const addFeedUpdate = (text: string) => {
    const now = new Date();
    const time = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
    const newUpdate = { time, text };
    setFeedUpdates(prev => [...prev, newUpdate]);
  };

  const handleApply = (company: string, idx: number) => {
    setApplyingToProject(idx);
    
    setTimeout(() => {
      toast.success(`Application submitted to ${company}. You'll be notified once they respond.`, {
        duration: 2000,
        className: "bg-[#0E0E10] border-[#E69219] text-white"
      });
      addFeedUpdate(`💼 Application submitted to ${company}.`);
      setApplyingToProject(null);
    }, 800);
  };

  const handleViewDetails = () => {
    toast.success("📬 Link opened, details loaded.", {
      duration: 2000,
      className: "bg-[#0E0E10] border-[#E69219] text-white"
    });
  };

  const handleApplyGig = (gigIdx: number, service: string) => {
    setAppliedGigs(prev => [...prev, gigIdx]);
    toast.success("You've applied for this role successfully.", {
      duration: 2000,
      className: "bg-[#0E0E10] border-[#E69219] text-white"
    });
    addFeedUpdate(`📈 Applied for ${service} gig.`);
  };

  const handleFindPeer = () => {
    setFindingPeer(true);
    setPeerFound(false);
    setScanningStage(0);
    
    setTimeout(() => setScanningStage(1), 800);
    setTimeout(() => setScanningStage(2), 1600);
    setTimeout(() => {
      setFindingPeer(false);
      setPeerFound(true);
    }, 2500);
  };

  const handleInviteToMeet = (peerName: string, idx: number) => {
    setSelectedPeer(peerName);
    setInviteSentPeers(prev => [...prev, idx]);
    
    confetti({
      particleCount: 50,
      spread: 60,
      origin: { y: 0.6 },
      colors: ['#E69219', '#DB5614', '#FFFFFF']
    });

    toast.success("Invite sent, awaiting response.", {
      duration: 2000,
      className: "bg-[#0E0E10] border-[#E69219] text-white"
    });

    setTimeout(() => {
      setInviteSentPeers(prev => prev.filter(i => i !== idx));
    }, 3000);
  };

  const handleScheduleMeeting = (time: string) => {
    confetti({
      particleCount: 100,
      spread: 70,
      origin: { y: 0.6 },
      colors: ['#E69219', '#DB5614', '#FFFFFF']
    });
    
    toast.success(`Invite sent to ${selectedPeer}, awaiting acceptance.`, {
      duration: 2000,
      className: "bg-[#0E0E10] border-[#E69219] text-white"
    });
    addFeedUpdate(`🗓️ Meeting invite sent to ${selectedPeer.split(' ')[1]}.`);
    setShowCalendarModal(false);
  };

  const handleAcceptInvitation = (idx: number, name: string) => {
    setAcceptedInvitations(prev => [...prev, idx]);
    toast.success("Meeting confirmed, calendar invite created.", {
      duration: 2000,
      className: "bg-[#0E0E10] border-[#E69219] text-white"
    });
    addFeedUpdate(`🗓️ Meeting confirmed with ${name.split(' ')[1]}.`);
  };

  const handleDeclineInvitation = (idx: number) => {
    toast.info("Invitation declined.", {
      duration: 2000,
      className: "bg-[#0E0E10] border-[#797979] text-white"
    });
  };

  const handleTryAnotherMatch = () => {
    setPeerFound(false);
    handleFindPeer();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-[#1a0a00] to-[#2d1505] text-white">
      {/* Header */}
      <section className="pt-24 pb-12 px-4 max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-white to-[#E69219] bg-clip-text text-transparent">
            Connect. Collaborate. Grow.
          </h1>
          <p className="text-lg text-[#C8C8C8] max-w-3xl">
            Find peers, industry projects, entrepreneurial opportunities, and gigs, all intelligently matched to your research profile.
          </p>
        </div>

        {/* Three Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Column 1 - Industry & Corporate Projects */}
          <Card className="bg-[#0E0E10] border-[#797979]/30 rounded-xl shadow-lg">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Building2 className="h-5 w-5 text-[#E69219]" />
                Industry & Corporate Projects
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[600px] pr-4">
                <div className="space-y-4">
                   {industryProjects.map((project, idx) => (
                     <Card key={idx} className="bg-black/40 border-[#797979]/20 hover:border-[#E69219]/50 transition-all duration-300 hover:shadow-[0_0_20px_rgba(230,146,25,0.3)] rounded-xl">
                       <CardContent className="p-4">
                         <div className="flex items-start justify-between mb-2">
                           <div className="w-12 h-12 rounded-full bg-gradient-to-br from-[#E69219] to-[#DB5614] flex items-center justify-center text-white font-bold">
                             {project.company.charAt(0)}
                           </div>
                           <Badge className="bg-[#E69219]/20 text-[#E69219] border-[#E69219]/30">
                             {project.matchScore}
                           </Badge>
                         </div>
                         <h3 className="text-white font-semibold mb-1">{project.project}</h3>
                         <p className="text-[#C8C8C8] text-sm mb-1">{project.company}</p>
                         <p className="text-[#C8C8C8] text-xs mb-1">{project.location}</p>
                         <p className="text-[#E69219] text-sm font-semibold mb-3">Funding: {project.funding}</p>
                         <Button 
                           onClick={() => handleApply(project.company, idx)}
                           disabled={applyingToProject === idx}
                           className={`w-full bg-gradient-to-r from-[#DB5614] to-[#E69219] text-white hover:from-[#DB5614] hover:to-[#DB5614] rounded-lg transition-all duration-400 ${
                             applyingToProject === idx ? 'animate-pulse shadow-[0_0_20px_rgba(230,146,25,0.5)]' : ''
                           }`}
                         >
                           {applyingToProject === idx ? 'Submitting...' : 'Apply / Connect'}
                         </Button>
                       </CardContent>
                     </Card>
                   ))}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>

          {/* Column 2 - Researcher Profile & Peer Matching */}
          <Card className="bg-[#0E0E10] border-[#797979]/30 rounded-xl shadow-lg">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Users className="h-5 w-5 text-[#E69219]" />
                Your Research Profile
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
               <div className="flex items-center gap-4">
                 <Avatar className="h-20 w-20 border-2 border-[#E69219]">
                   <AvatarFallback className="bg-gradient-to-br from-[#DB5614] to-[#E69219] text-white text-2xl font-bold">
                     AK
                   </AvatarFallback>
                 </Avatar>
                 <div>
                   <h3 className="text-white font-bold text-lg">Dr. Amara Khan</h3>
                   <p className="text-[#C8C8C8] text-sm">Year 2 PhD Candidate</p>
                   <p className="text-[#C8C8C8] text-xs">Trinity College Dublin</p>
                 </div>
               </div>

               <div className="space-y-3">
                 <div>
                   <p className="text-[#C8C8C8] text-sm mb-1">Research Focus</p>
                   <p className="text-white font-semibold">AI in Education & Adaptive Learning</p>
                 </div>
                 <div>
                   <p className="text-[#C8C8C8] text-sm mb-1">Keywords</p>
                   <div className="flex flex-wrap gap-2">
                     <Badge className="bg-[#E69219]/20 text-[#E69219] border-[#E69219]/30">Learning Analytics</Badge>
                     <Badge className="bg-[#E69219]/20 text-[#E69219] border-[#E69219]/30">Student Retention</Badge>
                     <Badge className="bg-[#E69219]/20 text-[#E69219] border-[#E69219]/30">Natural Language Processing</Badge>
                   </div>
                 </div>
                 <div>
                   <p className="text-[#C8C8C8] text-sm mb-1">Past Projects</p>
                   <p className="text-white text-xs">"Predictive Models for MOOC Dropout (2024)"</p>
                   <p className="text-white text-xs">"AI-Driven Feedback Loops for STEM Learning (2023)"</p>
                 </div>
                 <div>
                   <p className="text-[#C8C8C8] text-sm mb-1">Conferences</p>
                   <p className="text-white text-xs">EDUCAUSE 2024, IEEE AIED 2023</p>
                 </div>
                 <div>
                   <p className="text-[#C8C8C8] text-sm mb-1">Publications</p>
                   <p className="text-white text-xs">2 peer-reviewed papers accepted (IEEE, Springer)</p>
                 </div>
               </div>

              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <p className="text-[#C8C8C8] text-sm">Frensei Match Index</p>
                  <p className="text-[#E69219] font-bold text-xl">87%</p>
                </div>
                <div className="relative">
                  <Progress value={87} className="h-3 bg-[#292D32]" />
                  <div className="absolute inset-0 h-3 bg-gradient-to-r from-[#DB5614] to-[#E69219] rounded-full" style={{ width: '87%' }} />
                </div>
              </div>

              <Button 
                onClick={handleFindPeer}
                disabled={findingPeer}
                className="w-full bg-gradient-to-r from-[#DB5614] to-[#E69219] text-white hover:from-[#DB5614] hover:to-[#DB5614] rounded-xl py-6 text-lg font-semibold"
              >
                {findingPeer ? "Finding Your Peer..." : "Find Peer Now"}
              </Button>

              {findingPeer && (
                <div className="text-center p-4 bg-black/40 rounded-xl border border-[#E69219]/30 animate-pulse">
                  <p className="text-[#E69219] text-sm">
                    {scanningStage === 0 && "Scanning 2,000 researchers in your domain…"}
                    {scanningStage === 1 && "Filtering based on affinity and availability…"}
                    {scanningStage === 2 && "Matching optimal peer connections…"}
                  </p>
                </div>
              )}

              {peerFound && (
                <div className="space-y-4">
                  <ScrollArea className="h-64">
                    <div className="space-y-3">
                      {peerMatches.map((peer, idx) => (
                        <Card key={idx} className="bg-gradient-to-br from-[#E69219]/10 to-[#DB5614]/10 border-[#E69219] rounded-xl animate-scale-in relative">
                          <CardContent className="p-4">
                            {inviteSentPeers.includes(idx) && (
                              <div className="absolute inset-0 bg-[#E69219]/20 rounded-xl flex items-center justify-center backdrop-blur-sm z-10 animate-fade-in">
                                <div className="text-center">
                                  <Check className="h-8 w-8 text-white mx-auto mb-2" />
                                  <p className="text-white font-semibold">Invite sent, awaiting response.</p>
                                </div>
                              </div>
                            )}
                            <div className="flex items-start justify-between mb-2">
                              <div className="flex items-center gap-3">
                                <Avatar className="h-12 w-12 border-2 border-[#E69219]">
                                  <AvatarFallback className="bg-gradient-to-br from-[#DB5614] to-[#E69219] text-white font-bold">
                                    {peer.name.split(' ')[1].charAt(0)}
                                  </AvatarFallback>
                                </Avatar>
                                <div>
                                  <p className="text-white font-semibold">{peer.name}</p>
                                  <p className="text-[#C8C8C8] text-xs">{peer.university}</p>
                                </div>
                              </div>
                              <Badge className="bg-[#E69219]/20 text-[#E69219] border-[#E69219]/30">
                                {peer.match}
                              </Badge>
                            </div>
                            <p className="text-[#C8C8C8] text-sm mb-2">Focus: {peer.focus}</p>
                            <p className="text-white text-xs mb-3">Next available: {peer.availability}</p>
                            <Button 
                              onClick={() => handleInviteToMeet(peer.name, idx)}
                              disabled={inviteSentPeers.includes(idx)}
                              className="w-full bg-gradient-to-r from-[#DB5614] to-[#E69219] text-white hover:from-[#DB5614] hover:to-[#DB5614] rounded-lg transition-all duration-400 disabled:opacity-50"
                            >
                              {inviteSentPeers.includes(idx) ? 'Invite Sent...' : 'Invite to Meet'}
                            </Button>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </ScrollArea>
                  <Button 
                    onClick={handleTryAnotherMatch}
                    variant="outline" 
                    className="w-full border-white text-white hover:bg-white/10 rounded-lg"
                  >
                    Find More Matches
                  </Button>
                </div>
              )}

              {/* Pending Invitations */}
              <Card className="bg-black/40 border-[#797979]/20 rounded-xl mt-4">
                <CardHeader>
                  <CardTitle className="text-white text-sm">Pending Invitations & Requests</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {pendingInvitations.map((invite, idx) => (
                    <div 
                      key={idx} 
                      className={`p-3 bg-[#0E0E10] rounded-lg border transition-all duration-400 ${
                        acceptedInvitations.includes(idx) 
                          ? 'border-green-500 bg-green-500/10' 
                          : 'border-[#797979]/20'
                      }`}
                    >
                      {acceptedInvitations.includes(idx) ? (
                        <div className="text-center py-4 animate-fade-in">
                          <Check className="h-8 w-8 text-green-400 mx-auto mb-2" />
                          <p className="text-green-400 font-semibold">Meeting confirmed, calendar invite created.</p>
                        </div>
                      ) : (
                        <>
                          <div className="flex items-start justify-between mb-2">
                            <div>
                              <p className="text-white font-semibold text-sm">{invite.name}</p>
                              <p className="text-[#C8C8C8] text-xs">{invite.university}</p>
                            </div>
                          </div>
                          <p className="text-[#C8C8C8] text-xs mb-2">Topic: {invite.topic}</p>
                          {invite.time && <p className="text-white text-xs mb-2">{invite.time}</p>}
                          {invite.note && <p className="text-white text-xs mb-2">{invite.note}</p>}
                          <div className="flex gap-2">
                            {invite.time ? (
                              <>
                                <Button 
                                  onClick={() => handleAcceptInvitation(idx, invite.name)}
                                  className="flex-1 bg-gradient-to-r from-[#DB5614] to-[#E69219] text-white hover:from-[#DB5614] hover:to-[#DB5614] rounded-lg text-xs transition-all duration-400"
                                >
                                  Accept
                                </Button>
                                <Button 
                                  onClick={() => handleDeclineInvitation(idx)}
                                  variant="outline"
                                  className="flex-1 border-[#797979] text-white hover:bg-white/10 rounded-lg text-xs transition-all duration-400"
                                >
                                  Decline
                                </Button>
                              </>
                            ) : (
                              <Button 
                                onClick={handleViewDetails}
                                variant="outline"
                                className="w-full border-[#E69219] text-[#E69219] hover:bg-[#E69219]/10 rounded-lg text-xs transition-all duration-400"
                              >
                                View Details
                              </Button>
                            )}
                          </div>
                        </>
                      )}
                    </div>
                  ))}
                </CardContent>
              </Card>
            </CardContent>
          </Card>

          {/* Column 3 - Entrepreneurship & Gig Marketplace */}
          <div className="space-y-6">
            {/* Entrepreneurship Opportunities */}
            <Card className="bg-[#0E0E10] border-[#797979]/30 rounded-xl shadow-lg">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Rocket className="h-5 w-5 text-[#E69219]" />
                  Entrepreneurship Opportunities
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                 {entrepreneurshipOpps.map((opp, idx) => (
                   <Card key={idx} className="bg-black/40 border-[#797979]/20 hover:border-[#E69219]/50 transition-all duration-300 rounded-lg">
                     <CardContent className="p-4">
                       <h4 className="text-white font-semibold text-sm mb-1">{opp.title}</h4>
                       <p className="text-[#E69219] text-xs mb-1">Funding: {opp.funding}</p>
                       <p className="text-[#C8C8C8] text-xs mb-3">{opp.deadline}</p>
                       <Button 
                         onClick={handleViewDetails}
                         variant="outline" 
                         className="w-full border-[#E69219] text-[#E69219] hover:bg-[#E69219]/10 rounded-lg text-sm transition-all duration-400"
                       >
                         View Details
                       </Button>
                     </CardContent>
                   </Card>
                 ))}
              </CardContent>
            </Card>

            {/* Offer Your Skills - Services Marketplace */}
            <Card className="bg-[#0E0E10] border-[#797979]/30 rounded-xl shadow-lg">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Briefcase className="h-5 w-5 text-[#E69219]" />
                  Offer Your Skills
                </CardTitle>
                <CardDescription className="text-[#C8C8C8]">
                  Services Marketplace
                </CardDescription>
              </CardHeader>
               <CardContent className="space-y-3">
                 {gigListings.map((gig, idx) => (
                   <Card key={idx} className="bg-black/40 border-[#797979]/20 hover:border-[#E69219]/50 transition-all duration-300 rounded-lg relative">
                     <CardContent className="p-4">
                       {appliedGigs.includes(idx) && (
                         <div className="absolute inset-0 bg-black/80 rounded-lg flex items-center justify-center backdrop-blur-sm z-10 animate-fade-in">
                           <div className="text-center">
                             <Check className="h-10 w-10 text-white mx-auto mb-2" />
                             <p className="text-white font-semibold">You've applied for this role successfully.</p>
                           </div>
                         </div>
                       )}
                       <div className="flex items-start justify-between mb-2">
                         <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-[#E69219] to-[#DB5614] flex items-center justify-center text-white font-bold text-xs">
                           {gig.client.split(' ')[0].charAt(0)}
                         </div>
                         <Badge className="bg-green-500/20 text-green-400 border-green-500/30">
                           {gig.rate}
                         </Badge>
                       </div>
                       <h4 className="text-white font-semibold text-sm mb-1">{gig.service}</h4>
                       <p className="text-[#C8C8C8] text-xs mb-1">{gig.client}</p>
                       <p className="text-white text-xs mb-3">{gig.location}</p>
                       <Button 
                         onClick={() => handleApplyGig(idx, gig.service)}
                         disabled={appliedGigs.includes(idx)}
                         className="w-full bg-gradient-to-r from-[#DB5614] to-[#E69219] text-white hover:from-[#DB5614] hover:to-[#DB5614] rounded-lg text-sm transition-all duration-400 disabled:opacity-50"
                       >
                         {appliedGigs.includes(idx) ? 'Applied' : 'Apply'}
                       </Button>
                     </CardContent>
                   </Card>
                 ))}
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Grant Recommendations Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Grant Opportunities Card */}
          <Card className="bg-[#0E0E10] border-[#797979]/30 rounded-xl shadow-lg">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <DollarSign className="h-5 w-5 text-[#E69219]" />
                Recommended Grant Opportunities
              </CardTitle>
              <CardDescription className="text-[#C8C8C8]">
                Connect with funding bodies and potential collaborators
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[500px] pr-4">
                <div className="space-y-4">
                  {grantOpportunities.map((grant, idx) => (
                    <Card 
                      key={idx} 
                      onClick={() => toast.info("Database detached temporarily", {
                        duration: 2000,
                        className: "bg-[#0E0E10] border-[#797979] text-white"
                      })}
                      className="bg-black/40 border-[#797979]/20 hover:border-[#E69219]/50 transition-all duration-300 hover:shadow-[0_0_20px_rgba(230,146,25,0.3)] rounded-xl cursor-pointer"
                    >
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between mb-3">
                          <Badge className="bg-[#E69219]/20 text-[#E69219] border-[#E69219]/30">
                            Match: {grant.match}
                          </Badge>
                          <Badge className="bg-green-500/20 text-green-400 border-green-500/30">
                            {grant.funding}
                          </Badge>
                        </div>
                        <h3 className="text-white font-semibold mb-2 text-sm leading-tight">{grant.title}</h3>
                        <div className="space-y-2 mb-3">
                          <div className="flex items-center gap-2">
                            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#E69219] to-[#DB5614] flex items-center justify-center text-white font-bold text-xs">
                              {grant.contact.split(' ')[1]?.charAt(0) || grant.contact.charAt(0)}
                            </div>
                            <div>
                              <p className="text-white text-xs font-semibold">{grant.contact}</p>
                              <p className="text-[#C8C8C8] text-xs">{grant.institution}</p>
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-[#C8C8C8]">Deadline: {grant.deadline}</span>
                          <Button 
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation();
                              toast.info("Database detached temporarily", {
                                duration: 2000,
                                className: "bg-[#0E0E10] border-[#797979] text-white"
                              });
                            }}
                            className="bg-gradient-to-r from-[#DB5614] to-[#E69219] text-white hover:from-[#DB5614] hover:to-[#DB5614] rounded-lg h-7 text-xs"
                          >
                            Connect
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>

          {/* Frensei Penguin AI Feed */}
          <Card className="bg-[#0E0E10] border-[#E69219]/30 rounded-xl shadow-lg">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Zap className="h-5 w-5 text-[#E69219]" />
              Frensei Penguin AI, Live Matching Updates
              <span className="text-xs text-[#C8C8C8] font-normal ml-2">
                (Continuously monitoring project APIs and research networks)
              </span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="bg-black/40 rounded-lg p-4 border border-[#797979]/20">
              <div className="flex items-center gap-3 animate-fade-in">
                <span className="text-[#E69219] text-xs font-mono">[{feedUpdates[currentUpdate].time}]</span>
                <p className="text-white text-sm">{feedUpdates[currentUpdate].text}</p>
              </div>
            </div>
          </CardContent>
          </Card>
        </div>

        {/* Footer */}
        <div className="mt-12 pt-8 border-t border-[#797979]/30 text-center">
          <p className="text-[#C8C8C8] text-sm">
            All matches and interactions are managed via Frensei's <span className="text-[#E69219] font-semibold">DTSP™ (Dynamic Talent Sync Protocol)</span>, part of our patent-pending Research Continuity Ecosystem.
          </p>
        </div>
      </section>

      {/* Modal */}
      <Dialog open={showModal} onOpenChange={setShowModal}>
        <DialogContent className="bg-[#0E0E10] border-[#797979]/30 text-white rounded-xl">
          <DialogHeader>
            <DialogTitle className="text-white">Connection Sent!</DialogTitle>
            <DialogDescription className="text-[#C8C8C8]">
              {modalContent}
            </DialogDescription>
          </DialogHeader>
          <Button 
            onClick={() => setShowModal(false)}
            className="bg-gradient-to-r from-[#DB5614] to-[#E69219] text-white hover:from-[#DB5614] hover:to-[#DB5614] rounded-lg"
          >
            Close
          </Button>
        </DialogContent>
      </Dialog>

      {/* Calendar Modal */}
      <Dialog open={showCalendarModal} onOpenChange={setShowCalendarModal}>
        <DialogContent className="bg-[#0E0E10] border-[#797979]/30 text-white rounded-xl">
          <DialogHeader>
            <DialogTitle className="text-white">Select 30-minute slot with {selectedPeer}</DialogTitle>
            <DialogDescription className="text-[#C8C8C8]">
              Choose an available time slot for your meeting
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-3 py-4">
            {peerMatches.map((peer, idx) => (
              peer.name === selectedPeer && (
                <div key={idx} className="space-y-2">
                  <Button 
                    onClick={() => handleScheduleMeeting(peer.availability)}
                    className="w-full bg-gradient-to-r from-[#DB5614] to-[#E69219] text-white hover:from-[#DB5614] hover:to-[#DB5614] rounded-lg"
                  >
                    {peer.availability}
                  </Button>
                </div>
              )
            ))}
            <Button 
              onClick={() => handleScheduleMeeting("Wed 11:00 GMT")}
              className="w-full bg-gradient-to-r from-[#DB5614] to-[#E69219] text-white hover:from-[#DB5614] hover:to-[#DB5614] rounded-lg"
            >
              Wed 11:00 GMT
            </Button>
            <Button 
              onClick={() => handleScheduleMeeting("Thu 09:30 GMT")}
              className="w-full bg-gradient-to-r from-[#DB5614] to-[#E69219] text-white hover:from-[#DB5614] hover:to-[#DB5614] rounded-lg"
            >
              Thu 09:30 GMT
            </Button>
          </div>
          <Button 
            onClick={() => setShowCalendarModal(false)}
            variant="outline"
            className="w-full border-white text-white hover:bg-white/10 rounded-lg"
          >
            Cancel
          </Button>
        </DialogContent>
      </Dialog>
    </div>
  );
}
