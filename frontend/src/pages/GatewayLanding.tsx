import { useState, useEffect, FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

const GatewayLanding = () => {
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    document.title = "Frensei Access | Private Demo";
    // Meta description
    let meta = document.querySelector('meta[name="description"]') as HTMLMetaElement | null;
    if (!meta) {
      meta = document.createElement('meta');
      meta.name = 'description';
      document.head.appendChild(meta);
    }
    meta.setAttribute('content', 'Enter your Frensei access code to continue to the private demo.');
    // Canonical
    let link = document.querySelector('link[rel="canonical"]') as HTMLLinkElement | null;
    if (!link) {
      link = document.createElement('link');
      link.rel = 'canonical';
      document.head.appendChild(link);
    }
    link.setAttribute('href', window.location.origin + '/');
  }, []);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    
    if (password === "frensei2026&") {
      sessionStorage.setItem("frensei_access", "granted");
      navigate("/home");
    } else {
      setError("Invalid code. Please try again.");
      setPassword("");
    }
  };

  return (
    <div className="min-h-screen w-full bg-black flex items-center justify-center p-4 animate-fade-in">
      <div className="w-full max-w-6xl space-y-20 text-center px-8">
        {/* Logo */}
        <div className="mb-16">
          <h1 className="text-8xl md:text-9xl font-bold bg-gradient-to-r from-[#DB5614] to-[#E69219] bg-clip-text text-transparent">
            Frensei
          </h1>
        </div>

        {/* Headline */}
        <div className="space-y-6">
          <h2 className="text-5xl md:text-6xl font-bold text-white leading-tight">
            Welcome to Frensei, Authorized Access Only
          </h2>
          <p className="text-xl md:text-2xl text-[#AAAAAA]">
            This product is private. Please enter your access code to continue.
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-10 mt-20">
          <div className="relative">
            <Input
              type="password"
              value={password}
              onChange={(e) => {
                setPassword(e.target.value);
                setError("");
              }}
              placeholder="Enter access code"
              className="w-full bg-[#1A1A1A] border-2 border-transparent bg-gradient-to-r from-[#DB5614] to-[#E69219] bg-origin-border focus:ring-2 focus:ring-[#E69219] text-white placeholder:text-[#666666] h-24 text-center text-2xl"
              style={{
                backgroundClip: "padding-box, border-box",
                backgroundOrigin: "padding-box, border-box",
                backgroundImage: "linear-gradient(#1A1A1A, #1A1A1A), linear-gradient(to right, #DB5614, #E69219)"
              }}
            />
            {error && (
              <p className="text-red-500 text-xl mt-4 animate-fade-in">
                {error}
              </p>
            )}
          </div>

          <Button
            type="submit"
            className="w-full bg-gradient-to-r from-[#DB5614] to-[#E69219] hover:opacity-90 transition-opacity h-24 text-2xl font-semibold"
          >
            Enter Demo
          </Button>
        </form>

        {/* Contact */}
        <p className="text-lg md:text-xl text-[#666666] mt-24">
          For demo access, contact{" "}
          <a 
            href="mailto:team@frensei.com" 
            className="text-[#AAAAAA] hover:text-[#E69219] transition-colors"
          >
            team@frensei.com
          </a>
        </p>
      </div>
    </div>
  );
};

export default GatewayLanding;
