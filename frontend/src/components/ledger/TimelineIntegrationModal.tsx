import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Calendar, Edit, Trash2, Plus } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface TimelineIntegrationModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onEventsImported: () => void;
  currentUserId: string | null;
}

interface TimelineEvent {
  id: string;
  title: string;
  date: string;
  type: string;
  selected: boolean;
  editable?: boolean;
}

export const TimelineIntegrationModal = ({ open, onOpenChange, onEventsImported, currentUserId }: TimelineIntegrationModalProps) => {
  const [timelineEvents, setTimelineEvents] = useState<TimelineEvent[]>([
    { id: '1', title: 'Literature Review Completion', date: '2024-03-15', type: 'draft_submitted', selected: true },
    { id: '2', title: 'Methodology Review Meeting', date: '2024-04-01', type: 'meeting', selected: true },
    { id: '3', title: 'Data Collection Phase', date: '2024-05-15', type: 'dataset_shared', selected: false },
    { id: '4', title: 'First Draft Submission', date: '2024-07-01', type: 'draft_submitted', selected: true },
    { id: '5', title: 'Revision Feedback Session', date: '2024-08-15', type: 'feedback_given', selected: true },
    { id: '6', title: 'Final Submission', date: '2024-10-01', type: 'draft_submitted', selected: false }
  ]);
  const [loading, setLoading] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [newEvent, setNewEvent] = useState({ title: '', date: '', type: 'meeting' });
  const [showAddNew, setShowAddNew] = useState(false);
  const { toast } = useToast();

  const toggleSelection = (id: string) => {
    setTimelineEvents(prev =>
      prev.map(event =>
        event.id === id ? { ...event, selected: !event.selected } : event
      )
    );
  };

  const updateEvent = (id: string, field: string, value: string) => {
    setTimelineEvents(prev =>
      prev.map(event =>
        event.id === id ? { ...event, [field]: value } : event
      )
    );
  };

  const deleteEvent = (id: string) => {
    setTimelineEvents(prev => prev.filter(event => event.id !== id));
  };

  const addNewEvent = () => {
    if (!newEvent.title || !newEvent.date) {
      toast({
        title: "Missing Information",
        description: "Please fill in title and date",
        variant: "destructive"
      });
      return;
    }

    const event: TimelineEvent = {
      id: Date.now().toString(),
      title: newEvent.title,
      date: newEvent.date,
      type: newEvent.type,
      selected: true,
      editable: true
    };

    setTimelineEvents(prev => [...prev, event]);
    setNewEvent({ title: '', date: '', type: 'meeting' });
    setShowAddNew(false);
  };

  const handleImport = async () => {
    const selectedEvents = timelineEvents.filter(e => e.selected);
    
    if (selectedEvents.length === 0) {
      toast({
        title: "No Events Selected",
        description: "Please select at least one event to import",
        variant: "destructive"
      });
      return;
    }

    setLoading(true);
    try {
      // TODO: Replace with your backend API call
      const userId = sessionStorage.getItem("userId");
      if (!userId) {
        throw new Error("Your session has expired. Please log in again.");
      }

      // Store events in localStorage (replace with backend API)
      const storedEvents = localStorage.getItem("collaboration_events");
      const events = storedEvents ? JSON.parse(storedEvents) : [];

      for (const event of selectedEvents) {
        const newEvent = {
          id: `event_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          created_by: userId,
          event_type: event.type,
          summary: event.title,
          event_date: event.date,
          status: 'pending',
          created_at: new Date().toISOString(),
          participants: [{
            user_id: userId,
            role: 'collaborator'
          }],
          verifications: []
        };
        events.push(newEvent);
      }

      localStorage.setItem("collaboration_events", JSON.stringify(events));

      toast({
        title: "Success",
        description: `Imported ${selectedEvents.length} events from timeline`
      });

      onEventsImported();
      onOpenChange(false);
    } catch (error: any) {
      console.error('Error importing events:', error);
      toast({
        title: "Error",
        description: error.message || "Failed to import events. Please try logging out and back in.",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold">Import From Research Timeline</DialogTitle>
          <DialogDescription>
            Select and edit timeline milestones to import as collaboration events
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Timeline Events List */}
          <div className="space-y-3">
            {timelineEvents.map(event => (
              <div
                key={event.id}
                className="flex items-start gap-4 p-4 border rounded-lg hover:bg-muted/50 transition-colors"
              >
                <Checkbox
                  checked={event.selected}
                  onCheckedChange={() => toggleSelection(event.id)}
                  className="mt-1"
                />
                
                <div className="flex-1 space-y-2">
                  {editingId === event.id ? (
                    <>
                      <Input
                        value={event.title}
                        onChange={(e) => updateEvent(event.id, 'title', e.target.value)}
                        className="font-medium"
                      />
                      <Input
                        type="date"
                        value={event.date}
                        onChange={(e) => updateEvent(event.id, 'date', e.target.value)}
                      />
                    </>
                  ) : (
                    <>
                      <h4 className="font-medium text-foreground">{event.title}</h4>
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Calendar className="h-3 w-3" />
                        {new Date(event.date).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric'
                        })}
                      </div>
                    </>
                  )}
                </div>

                <div className="flex gap-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setEditingId(editingId === event.id ? null : event.id)}
                  >
                    <Edit className="h-4 w-4" />
                  </Button>
                  {event.editable && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => deleteEvent(event.id)}
                    >
                      <Trash2 className="h-4 w-4 text-destructive" />
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Add New Event */}
          {showAddNew ? (
            <div className="p-4 border rounded-lg space-y-3">
              <h4 className="font-medium">Add Custom Event</h4>
              <Input
                placeholder="Event title"
                value={newEvent.title}
                onChange={(e) => setNewEvent({ ...newEvent, title: e.target.value })}
              />
              <Input
                type="date"
                value={newEvent.date}
                onChange={(e) => setNewEvent({ ...newEvent, date: e.target.value })}
              />
              <div className="flex gap-2">
                <Button onClick={addNewEvent} variant="outline">Add</Button>
                <Button onClick={() => setShowAddNew(false)} variant="ghost">Cancel</Button>
              </div>
            </div>
          ) : (
            <Button
              variant="outline"
              className="w-full"
              onClick={() => setShowAddNew(true)}
            >
              <Plus className="mr-2 h-4 w-4" />
              Add Custom Event
            </Button>
          )}

          {/* Actions */}
          <div className="flex gap-3 justify-end pt-4 border-t">
            <Button variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleImport}
              disabled={loading}
              className="bg-gradient-to-r from-[#DB5614] to-[#E69219]"
            >
              {loading ? "Importing..." : `Import ${timelineEvents.filter(e => e.selected).length} Events`}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};
