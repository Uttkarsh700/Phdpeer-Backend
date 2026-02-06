import { useState, useEffect } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { Plus, X } from "lucide-react";

interface AddEventModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onEventAdded: () => void;
  currentUserId: string | null;
}

const EVENT_TYPES = [
  { value: "meeting", label: "Meeting" },
  { value: "feedback_given", label: "Feedback Given" },
  { value: "draft_submitted", label: "Draft Submitted" },
  { value: "revision_request", label: "Revision Request" },
  { value: "delay_explained", label: "Delay Explained" },
  { value: "coauthor_discussion", label: "Co-author Discussion" },
  { value: "dataset_shared", label: "Dataset Shared" },
  { value: "decision_made", label: "Decision Made" },
  { value: "general_note", label: "General Note" }
];

export const AddEventModal = ({ open, onOpenChange, onEventAdded, currentUserId }: AddEventModalProps) => {
  const [eventType, setEventType] = useState("");
  const [summary, setSummary] = useState("");
  const [eventDate, setEventDate] = useState(new Date().toISOString().split('T')[0]);
  const [selectedParticipants, setSelectedParticipants] = useState<string[]>([]);
  const [members, setMembers] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    if (open) {
      // Ensure current user is pre-selected as a participant
      if (currentUserId) {
        setSelectedParticipants((prev) => {
          if (prev.includes(currentUserId)) return prev;
          return [currentUserId, ...prev];
        });
      }
      fetchMembers();
    }
  }, [open]);

  const fetchMembers = async () => {
    try {
      // TODO: Replace with your backend API call
      const storedMembers = localStorage.getItem("project_members");
      const members = storedMembers ? JSON.parse(storedMembers) : [];
      
      if (members.length > 0) {
        setMembers(members);
      } else {
        // Initialize with current user if no members exist
        if (currentUserId) {
          const newMember = {
            user_id: currentUserId,
            display_name: 'You',
            role: 'collaborator',
            id: `member_${Date.now()}`
          };
          members.push(newMember);
          localStorage.setItem("project_members", JSON.stringify(members));
          setMembers(members);
        }
      }
    } catch (error) {
      console.error("Error fetching members:", error);
    }
  };

  const handleSubmit = async () => {
    if (!eventType || !summary || selectedParticipants.length === 0) {
      toast({
        title: "Missing Information",
        description: "Please fill in all required fields",
        variant: "destructive"
      });
      return;
    }

    if (!currentUserId) {
      toast({
        title: "Error",
        description: "Please sign in to create events",
        variant: "destructive"
      });
      return;
    }

    setLoading(true);
    try {
      // TODO: Replace with your backend API call
      const newEvent = {
        id: `event_${Date.now()}`,
        created_by: currentUserId,
        event_type: eventType,
        summary,
        event_date: eventDate,
        status: 'pending',
        created_at: new Date().toISOString(),
        participants: selectedParticipants.map(userId => ({
          user_id: userId,
          role: members.find(m => m.user_id === userId)?.role || 'collaborator',
        })),
        verifications: []
      };

      // Store in localStorage (replace with backend API)
      const storedEvents = localStorage.getItem("collaboration_events");
      const events = storedEvents ? JSON.parse(storedEvents) : [];
      events.push(newEvent);
      localStorage.setItem("collaboration_events", JSON.stringify(events));

      toast({
        title: "Success",
        description: "Event created successfully"
      });

      // Reset form
      setEventType("");
      setSummary("");
      setEventDate(new Date().toISOString().split('T')[0]);
      setSelectedParticipants([]);
      onEventAdded();
      onOpenChange(false);
    } catch (error) {
      console.error('Error creating event:', error);
      toast({
        title: "Error",
        description: "Failed to create event",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const toggleParticipant = (userId: string) => {
    setSelectedParticipants(prev =>
      prev.includes(userId)
        ? prev.filter(id => id !== userId)
        : [...prev, userId]
    );
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold">Add Research Event</DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* Event Type */}
          <div>
            <Label htmlFor="eventType">Event Type</Label>
            <Select value={eventType} onValueChange={setEventType}>
              <SelectTrigger id="eventType">
                <SelectValue placeholder="Select event type" />
              </SelectTrigger>
              <SelectContent>
                {EVENT_TYPES.map(type => (
                  <SelectItem key={type.value} value={type.value}>
                    {type.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Summary */}
          <div>
            <Label htmlFor="summary">Event Summary</Label>
            <Textarea
              id="summary"
              value={summary}
              onChange={(e) => setSummary(e.target.value)}
              placeholder="Describe what happened..."
              rows={4}
            />
          </div>

          {/* Date */}
          <div>
            <Label htmlFor="date">Date</Label>
            <Input
              id="date"
              type="date"
              value={eventDate}
              onChange={(e) => setEventDate(e.target.value)}
            />
          </div>

          {/* Participants */}
          <div>
            <Label>Participants</Label>
            <div className="mt-2 space-y-2 max-h-48 overflow-y-auto border rounded-md p-3">
              {members.map(member => (
                <div
                  key={member.user_id}
                  className="flex items-center justify-between p-2 hover:bg-muted rounded cursor-pointer"
                  onClick={() => toggleParticipant(member.user_id)}
                >
                  <div className="flex items-center gap-3">
                    <input
                      type="checkbox"
                      checked={selectedParticipants.includes(member.user_id)}
                      onChange={() => {}}
                      className="h-4 w-4"
                    />
                    <div>
                      <p className="font-medium">{member.display_name || 'Unnamed'}</p>
                      <p className="text-sm text-muted-foreground capitalize">{member.role}</p>
                    </div>
                  </div>
                </div>
              ))}
              {members.length === 0 && (
                <p className="text-sm text-muted-foreground text-center py-4">
                  No team members yet. Add them in Role Management.
                </p>
              )}
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-3 justify-end">
            <Button variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleSubmit}
              disabled={loading}
              className="bg-gradient-to-r from-[#DB5614] to-[#E69219]"
            >
              {loading ? "Submitting..." : "Submit"}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};
