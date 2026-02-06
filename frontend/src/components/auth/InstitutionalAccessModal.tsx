import { useState, FormEvent } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/hooks/use-toast";

interface InstitutionalAccessModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export const InstitutionalAccessModal = ({
  open,
  onOpenChange,
}: InstitutionalAccessModalProps) => {
  const { toast } = useToast();
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    institution: "",
    role: "",
    message: "",
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    // Simulate form submission
    setTimeout(() => {
      toast({
        title: "Request Submitted",
        description: "Thank you for your interest. We'll contact you within 2 business days.",
      });
      setIsSubmitting(false);
      onOpenChange(false);
      setFormData({
        name: "",
        email: "",
        institution: "",
        role: "",
        message: "",
      });
    }, 1000);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="bg-[#1A1A1A] border-2 border-primary/40 text-white max-w-md">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold bg-gradient-to-r from-[#DB5614] to-[#E69219] bg-clip-text text-transparent">
            Request Institutional Access
          </DialogTitle>
          <DialogDescription className="text-white/70">
            Fill out the form below and our team will reach out to discuss Frensei for your institution.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4 mt-4">
          <div className="space-y-2">
            <Label htmlFor="name" className="text-white">
              Full Name *
            </Label>
            <Input
              id="name"
              type="text"
              required
              value={formData.name}
              onChange={(e) =>
                setFormData({ ...formData, name: e.target.value })
              }
              className="bg-[#0E0E0E] border-primary/30 text-white focus:border-primary"
              placeholder="Dr. Jane Smith"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="email" className="text-white">
              Email Address *
            </Label>
            <Input
              id="email"
              type="email"
              required
              value={formData.email}
              onChange={(e) =>
                setFormData({ ...formData, email: e.target.value })
              }
              className="bg-[#0E0E0E] border-primary/30 text-white focus:border-primary"
              placeholder="jane.smith@university.edu"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="institution" className="text-white">
              Institution Name *
            </Label>
            <Input
              id="institution"
              type="text"
              required
              value={formData.institution}
              onChange={(e) =>
                setFormData({ ...formData, institution: e.target.value })
              }
              className="bg-[#0E0E0E] border-primary/30 text-white focus:border-primary"
              placeholder="University of Example"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="role" className="text-white">
              Your Role *
            </Label>
            <Input
              id="role"
              type="text"
              required
              value={formData.role}
              onChange={(e) =>
                setFormData({ ...formData, role: e.target.value })
              }
              className="bg-[#0E0E0E] border-primary/30 text-white focus:border-primary"
              placeholder="Dean of Graduate Studies"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="message" className="text-white">
              Additional Information
            </Label>
            <Textarea
              id="message"
              value={formData.message}
              onChange={(e) =>
                setFormData({ ...formData, message: e.target.value })
              }
              className="bg-[#0E0E0E] border-primary/30 text-white focus:border-primary min-h-[100px]"
              placeholder="Tell us about your institution's needs..."
            />
          </div>

          <Button
            type="submit"
            disabled={isSubmitting}
            className="w-full bg-gradient-to-r from-[#DB5614] to-[#E69219] hover:opacity-90 text-white transition-all duration-300 shadow-lg hover:shadow-[0_0_20px_rgba(230,146,25,0.55)]"
          >
            {isSubmitting ? "Submitting..." : "Submit Request"}
          </Button>
        </form>
      </DialogContent>
    </Dialog>
  );
};
