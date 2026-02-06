import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Layout } from "./components/layout/Layout";
import GatewayLanding from "./pages/GatewayLanding";
import Index from "./pages/Index";
import WellBeingCheckIn from "./pages/WellBeingCheckIn";
import Dashboard from "./pages/Dashboard";
import ResearchTimeline from "./pages/ResearchTimeline";
import PeerNetwork from "./pages/PeerNetwork";
import UniversityDashboard from "./pages/UniversityDashboard";
import CollaborationLedger from "./pages/CollaborationLedger";
import ProfileStrength from "./pages/ProfileStrength";
import Auth from "./pages/Auth";
import NotFound from "./pages/NotFound";
import WritingEvolution from "./pages/WritingEvolution";
import WritingEvolutionBaseline from "./pages/WritingEvolutionBaseline";
import WritingEvolutionCheckpoint from "./pages/WritingEvolutionCheckpoint";
import WritingEvolutionReport from "./pages/WritingEvolutionReport";
import WritingEvolutionCertificate from "./pages/WritingEvolutionCertificate";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<GatewayLanding />} />
          <Route path="/auth" element={<Auth />} />
          <Route element={<Layout />}>
            <Route path="/home" element={<Index />} />
            <Route path="/profile-strength" element={<ProfileStrength />} />
            <Route path="/wellbeing" element={<WellBeingCheckIn />} />
            <Route path="/timeline" element={<ResearchTimeline />} />
            <Route path="/network" element={<PeerNetwork />} />
            <Route path="/university-dashboard" element={<UniversityDashboard />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/collaboration-ledger" element={<CollaborationLedger />} />
            <Route path="/writing-evolution" element={<WritingEvolution />} />
            <Route path="/writing-evolution/baseline" element={<WritingEvolutionBaseline />} />
            <Route path="/writing-evolution/checkpoint" element={<WritingEvolutionCheckpoint />} />
            <Route path="/writing-evolution/report/:id" element={<WritingEvolutionReport />} />
            <Route path="/writing-evolution/certificate" element={<WritingEvolutionCertificate />} />
          </Route>
          {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
