import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { UniversityPasswordModal } from "@/components/auth/UniversityPasswordModal";
import { InstitutionalAccessModal } from "@/components/auth/InstitutionalAccessModal";

export const Header = () => {
  const location = useLocation();
  const [universityPasswordOpen, setUniversityPasswordOpen] = useState(false);
  const [institutionalAccessOpen, setInstitutionalAccessOpen] = useState(false);

  const isActive = (path: string) => location.pathname === path;

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-background backdrop-blur-sm border-b border-border">
      <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
        {/* Brand */}
        <Link to="/home" className="flex items-center gap-3">
          <img 
            src="/favicon.png" 
            alt="Frensei Penguin" 
            className="w-12 h-12 object-contain"
          />
          <span className="text-2xl font-bold text-white drop-shadow-lg">Frensei</span>
        </Link>

        {/* Center Navigation */}
        <nav className="hidden lg:flex items-center gap-4">
          <Link
            to="/home"
            className={`text-white hover:text-primary transition-colors pb-1 text-sm ${
              isActive("/home") ? "nav-link-active" : ""
            }`}
          >
            Home
          </Link>
          <Link
            to="/profile-strength"
            className={`text-white hover:text-primary transition-colors pb-1 text-sm ${
              isActive("/profile-strength") ? "nav-link-active" : ""
            }`}
          >
            PhD Dashboard
          </Link>
          <Link
            to="/timeline"
            className={`text-white hover:text-primary transition-colors pb-1 text-sm ${
              isActive("/timeline") ? "nav-link-active" : ""
            }`}
          >
            Timeline
          </Link>
          <Link
            to="/collaboration-ledger"
            className={`text-white hover:text-primary transition-colors pb-1 text-sm ${
              isActive("/collaboration-ledger") ? "nav-link-active" : ""
            }`}
          >
            Collaboration Tracker
          </Link>
          <Link
            to="/wellbeing"
            className={`text-white hover:text-primary transition-colors pb-1 text-sm ${
              isActive("/wellbeing") ? "nav-link-active" : ""
            }`}
          >
            PhD Doctor
          </Link>
          <Link
            to="/network"
            className={`text-white hover:text-primary transition-colors pb-1 text-sm ${
              isActive("/network") ? "nav-link-active" : ""
            }`}
          >
            Network
          </Link>
          <button
            onClick={() => setUniversityPasswordOpen(true)}
            className="text-white hover:text-primary transition-colors pb-1 text-sm"
          >
            University
          </button>
        </nav>

        {/* Right Side Button */}
        <Button 
          className="bg-gradient-to-r from-[#DB5614] to-[#E69219] hover:opacity-90 text-white transition-all duration-300 shadow-lg hover:shadow-[0_0_20px_rgba(230,146,25,0.55)]"
          onClick={() => setInstitutionalAccessOpen(true)}
        >
          Request Institutional Access
        </Button>
      </div>
      
      {/* University Password Modal */}
      <UniversityPasswordModal open={universityPasswordOpen} onOpenChange={setUniversityPasswordOpen} />
      
      {/* Institutional Access Modal */}
      <InstitutionalAccessModal open={institutionalAccessOpen} onOpenChange={setInstitutionalAccessOpen} />
    </header>
  );
};
