import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";

interface LoginModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export const LoginModal = ({ open, onOpenChange }: LoginModalProps) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(false);
  const navigate = useNavigate();
  const { toast } = useToast();

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Basic validation
    if (!email || !password) {
      toast({
        title: "Error",
        description: "Please fill in all fields",
        variant: "destructive",
      });
      return;
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      toast({
        title: "Error",
        description: "Please enter a valid email address",
        variant: "destructive",
      });
      return;
    }

    // Mock login success
    toast({
      title: "Welcome back!",
      description: "You have successfully logged in.",
    });

    // Store login state
    localStorage.setItem("isAuthenticated", "true");
    if (rememberMe) {
      localStorage.setItem("rememberMe", "true");
    }

    // Close modal and navigate
    onOpenChange(false);
    navigate("/dashboard");
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="bg-card border-border sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold text-white text-center">
            Welcome to Frensei
          </DialogTitle>
        </DialogHeader>
        
        <form onSubmit={handleLogin} className="space-y-5 mt-4">
          {/* Email/Username Input */}
          <div className="space-y-2">
            <Label htmlFor="email" className="text-white">
              Email / Username
            </Label>
            <Input
              id="email"
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="input-frensei"
            />
          </div>

          {/* Password Input */}
          <div className="space-y-2">
            <Label htmlFor="password" className="text-white">
              Password
            </Label>
            <Input
              id="password"
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="input-frensei"
            />
          </div>

          {/* Remember Me & Forgot Password */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Checkbox
                id="remember"
                checked={rememberMe}
                onCheckedChange={(checked) => setRememberMe(checked as boolean)}
              />
              <Label
                htmlFor="remember"
                className="text-sm text-white cursor-pointer"
              >
                Remember Me
              </Label>
            </div>
            <a
              href="#"
              className="text-sm text-primary hover:text-secondary transition-colors"
              onClick={(e) => {
                e.preventDefault();
                toast({
                  title: "Password Reset",
                  description: "Password reset feature coming soon!",
                });
              }}
            >
              Forgot Password?
            </a>
          </div>

          {/* Login Button */}
          <Button
            type="submit"
            className="w-full btn-primary"
          >
            Login
          </Button>

          {/* Request Access */}
          <div className="text-center text-sm text-muted-foreground">
            Not a member?{" "}
            <a
              href="#"
              className="text-primary hover:text-secondary transition-colors font-medium"
              onClick={(e) => {
                e.preventDefault();
                toast({
                  title: "Request Access",
                  description: "Please contact us to request exclusive access to Frensei.",
                });
              }}
            >
              Request exclusive access to Frensei.
            </a>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};
