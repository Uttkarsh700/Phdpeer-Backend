import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/hooks/use-toast";
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from "@/components/ui/alert-dialog";

interface ReconstructJourneyModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onEventsCreated: () => void;
  currentUserId: string | null;
}

export const ReconstructJourneyModal = ({ open, onOpenChange, onEventsCreated, currentUserId }: ReconstructJourneyModalProps) => {
  const [journeyText, setJourneyText] = useState("");
  const [loading, setLoading] = useState(false);
  const [extractedEvents, setExtractedEvents] = useState<any[]>([]);
  const [showDuplicateDialog, setShowDuplicateDialog] = useState(false);
  const { toast } = useToast();

  const handleReconstruct = async () => {
    if (!journeyText.trim()) {
      toast({
        title: "Empty Input",
        description: "Please describe your research journey",
        variant: "destructive"
      });
      return;
    }

    if (journeyText.trim().length < 50) {
      toast({
        title: "Too Brief",
        description: "Please provide a more detailed description of your research journey (at least 50 characters)",
        variant: "destructive"
      });
      return;
    }

    setLoading(true);
    
    try {
      // TODO: Replace with your backend API call
      // For now, simulate parsing with a simple extraction
      const data = {
        events: [
          {
            event_type: 'general_note',
            summary: 'Journey event extracted from text',
            event_date: new Date().toISOString().split('T')[0]
          }
        ]
      };

      if (!data.events || data.events.length === 0) {
        toast({
          title: "No Events Found",
          description: "Could not extract events from your description. Please provide more specific details with dates and activities.",
          variant: "destructive"
        });
        setLoading(false);
        return;
      }

      // Check for duplicates
      const existingEvents = JSON.parse(localStorage.getItem('collaboration_events') || '[]');
      const hasDuplicates = data.events.some((newEvent: any) => 
        existingEvents.some((existing: any) => 
          existing.summary.toLowerCase().includes(newEvent.summary.toLowerCase().substring(0, 30)) ||
          newEvent.summary.toLowerCase().includes(existing.summary.toLowerCase().substring(0, 30))
        )
      );

      setExtractedEvents(data.events);

      if (hasDuplicates) {
        setShowDuplicateDialog(true);
      } else {
        saveEvents(data.events);
      }

    } catch (error) {
      console.error('Error parsing journey:', error);
      toast({
        title: "Error",
        description: "Failed to process your journey. Please try again.",
        variant: "destructive"
      });
    }
    
    setLoading(false);
  };

  const saveEvents = (events: any[], overwrite: boolean = false) => {
    const existingEvents = JSON.parse(localStorage.getItem('collaboration_events') || '[]');
    
    let finalEvents = existingEvents;
    
    if (overwrite) {
      // Remove similar events
      const summariesToRemove = events.map(e => e.summary.toLowerCase().substring(0, 30));
      finalEvents = existingEvents.filter((existing: any) => 
        !summariesToRemove.some(summary => 
          existing.summary.toLowerCase().includes(summary) || 
          summary.includes(existing.summary.toLowerCase().substring(0, 30))
        )
      );
    }

    // Add new events
    const newEvents = events.map(event => ({
      id: `event_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      event_type: event.event_type,
      summary: event.summary,
      event_date: event.event_date,
      status: 'pending',
      created_at: new Date().toISOString(),
      created_by: currentUserId,
      participants: [],
      verifications: []
    }));

    finalEvents = [...finalEvents, ...newEvents];
    localStorage.setItem('collaboration_events', JSON.stringify(finalEvents));

    toast({
      title: "Journey Captured",
      description: `${newEvents.length} event${newEvents.length > 1 ? 's' : ''} created successfully.`,
    });

    setJourneyText("");
    setExtractedEvents([]);
    setShowDuplicateDialog(false);
    onOpenChange(false);
    onEventsCreated();
  };

  return (
    <>
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="max-w-3xl">
          <DialogHeader>
            <DialogTitle className="text-2xl font-bold">AI Minutes-to-Timeline™</DialogTitle>
            <DialogDescription>
              Describe your research journey in your own words. Include dates, milestones, meetings, 
              feedback sessions, delays, submissions, or any significant events. Our AI will help 
              organize this into structured events.
            </DialogDescription>
          </DialogHeader>

        <div className="space-y-4">
          <Textarea
            value={journeyText}
            onChange={(e) => setJourneyText(e.target.value)}
            placeholder="Example: In September 2023, I submitted my initial proposal to Dr. Smith. After our meeting in October, she suggested focusing on climate data analysis instead of policy. I spent November collecting datasets, and in December we had a breakthrough discussion about the methodology..."
            rows={12}
            className="text-base"
          />

          <div className="bg-muted p-4 rounded-lg">
            <h4 className="font-medium mb-2">💡 Tips for better results:</h4>
            <ul className="text-sm text-muted-foreground space-y-1">
              <li>• Include dates and timeframes</li>
              <li>• Mention people involved in each event</li>
              <li>• Describe key decisions and milestones</li>
              <li>• Note any delays or challenges</li>
              <li>• Include feedback sessions and revisions</li>
            </ul>
          </div>

          <div className="flex gap-3 justify-end">
            <Button variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleReconstruct}
              disabled={loading}
              className="bg-gradient-to-r from-[#DB5614] to-[#E69219]"
            >
              {loading ? "Processing..." : "Generate Events"}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>

    <AlertDialog open={showDuplicateDialog} onOpenChange={setShowDuplicateDialog}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Duplicate Events Detected</AlertDialogTitle>
          <AlertDialogDescription>
            Some events appear similar to existing ones. Would you like to:
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel onClick={() => setShowDuplicateDialog(false)}>
            Cancel
          </AlertDialogCancel>
          <Button
            variant="outline"
            onClick={() => saveEvents(extractedEvents, false)}
          >
            Keep Both
          </Button>
          <AlertDialogAction onClick={() => saveEvents(extractedEvents, true)}>
            Replace Similar Events
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
    </>
  );
};
