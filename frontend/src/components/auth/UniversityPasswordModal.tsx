import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";

interface UniversityPasswordModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export const UniversityPasswordModal = ({ open, onOpenChange }: UniversityPasswordModalProps) => {
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (password === "1111") {
      onOpenChange(false);
      setPassword("");
      setError("");
      navigate("/university-dashboard");
    } else {
      setError("Invalid code. Try again.");
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md bg-[#1E1E1E] border-2 border-primary">
        <DialogHeader>
          <DialogTitle className="text-white text-center text-xl">Enter Access Code</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4 mt-4">
          <div>
            <Label htmlFor="password" className="text-white">Access Code</Label>
            <Input
              id="password"
              type="password"
              value={password}
              onChange={(e) => {
                setPassword(e.target.value);
                setError("");
              }}
              className="bg-black border-primary/30 text-white mt-2"
              placeholder="Enter code"
            />
            {error && <p className="text-red-500 text-sm mt-2">{error}</p>}
          </div>
          <Button type="submit" className="w-full bg-primary hover:bg-secondary text-white">
            Enter
          </Button>
        </form>
      </DialogContent>
    </Dialog>
  );
};
