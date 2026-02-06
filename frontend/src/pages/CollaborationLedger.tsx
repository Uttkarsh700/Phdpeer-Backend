import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Plus, Users, Filter, Calendar, Bot } from "lucide-react";
import { AddEventModal } from "@/components/ledger/AddEventModal";
import { EventCard } from "@/components/ledger/EventCard";
import { ReconstructJourneyModal } from "@/components/ledger/ReconstructJourneyModal";
import { RoleManagementModal } from "@/components/ledger/RoleManagementModal";
import { EventFilters } from "@/components/ledger/EventFilters";
import { TimelineIntegrationModal } from "@/components/ledger/TimelineIntegrationModal";
import { TimelineView } from "@/components/ledger/TimelineView";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useToast } from "@/hooks/use-toast";

interface CollaborationEvent {
  id: string;
  event_type: string;
  summary: string;
  event_date: string;
  status: string;
  created_at: string;
  participants?: any[];
  verifications?: any[];
}

const CollaborationLedger = () => {
  const [events, setEvents] = useState<CollaborationEvent[]>([]);
  const [filteredEvents, setFilteredEvents] = useState<CollaborationEvent[]>([]);
  const [addEventOpen, setAddEventOpen] = useState(false);
  const [reconstructOpen, setReconstructOpen] = useState(false);
  const [roleManagementOpen, setRoleManagementOpen] = useState(false);
  const [timelineIntegrationOpen, setTimelineIntegrationOpen] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [currentUserId, setCurrentUserId] = useState<string | null>(null);
  const { toast } = useToast();

  useEffect(() => {
    document.title = "Collaboration Tracker | Frensei";
    initializeUser();
  }, []);

  const initializeUser = async () => {
    // TODO: Replace with your backend authentication
    const userId = sessionStorage.getItem("userId");
    if (userId) {
      setCurrentUserId(userId);
      fetchEvents();
    }
  };

  const fetchEvents = async () => {
    try {
      // TODO: Replace with your backend API call
      // For now, load from localStorage or set empty array
      const storedEvents = localStorage.getItem("collaboration_events");
      const eventsData = storedEvents ? JSON.parse(storedEvents) : [];
      
      setEvents(eventsData);
      setFilteredEvents(eventsData);
    } catch (error: any) {
      console.error("Error fetching events:", error);
      toast({
        title: "Error",
        description: "Failed to load events",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="min-h-screen bg-background pt-8 pb-16">
      <div className="max-w-6xl mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-3">
            Collaboration Tracker
          </h1>
          <p className="text-xl text-muted-foreground">
            Capture your research journey collaboratively
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap gap-4 mb-8">
          <Button
            onClick={() => setAddEventOpen(true)}
            className="bg-gradient-to-r from-[#DB5614] to-[#E69219] hover:opacity-90"
          >
            <Plus className="mr-2 h-4 w-4" />
            Add Event
          </Button>
          
          <Button
            onClick={() => setTimelineIntegrationOpen(true)}
            variant="outline"
            className="border-primary text-primary hover:bg-primary hover:text-white"
          >
            <Calendar className="mr-2 h-4 w-4" />
            Import From Timeline
          </Button>

          <Button
            onClick={() => setReconstructOpen(true)}
            variant="outline"
            className="border-primary text-primary hover:bg-primary hover:text-white"
          >
            <Bot className="mr-2 h-4 w-4" />
            AI Minutes-to-Timeline™
          </Button>

          <Button
            onClick={() => setRoleManagementOpen(true)}
            variant="outline"
          >
            <Users className="mr-2 h-4 w-4" />
            Manage Roles
          </Button>

          <Button
            onClick={() => setShowFilters(!showFilters)}
            variant="outline"
          >
            <Filter className="mr-2 h-4 w-4" />
            Filters
          </Button>
        </div>

        {/* Filters */}
        {showFilters && (
          <EventFilters
            events={events}
            onFilter={setFilteredEvents}
          />
        )}

        {/* Events List with Tabs */}
        <Tabs defaultValue="list" className="w-full">
          <TabsList className="mb-6">
            <TabsTrigger value="list">List View</TabsTrigger>
            <TabsTrigger value="timeline">Timeline View</TabsTrigger>
          </TabsList>

          <TabsContent value="list">
            <div className="space-y-6">
              {filteredEvents.length === 0 ? (
                <div className="text-center py-16 card-frensei">
                  <p className="text-xl text-muted-foreground mb-4">
                    No events yet. Start by adding your first event.
                  </p>
                  <Button
                    onClick={() => setAddEventOpen(true)}
                    variant="outline"
                    className="border-primary text-primary"
                  >
                    <Plus className="mr-2 h-4 w-4" />
                    Add Your First Event
                  </Button>
                </div>
              ) : (
                filteredEvents.map((event) => (
                  <EventCard
                    key={event.id}
                    event={event}
                    onUpdate={fetchEvents}
                    currentUserId={currentUserId}
                  />
                ))
              )}
            </div>
          </TabsContent>

          <TabsContent value="timeline">
            {filteredEvents.length === 0 ? (
              <div className="text-center py-16 card-frensei">
                <p className="text-xl text-muted-foreground mb-4">
                  No events yet. Start by adding your first event.
                </p>
                <Button
                  onClick={() => setAddEventOpen(true)}
                  variant="outline"
                  className="border-primary text-primary"
                >
                  <Plus className="mr-2 h-4 w-4" />
                  Add Your First Event
                </Button>
              </div>
            ) : (
              <TimelineView events={filteredEvents} />
            )}
          </TabsContent>
        </Tabs>
      </div>

      {/* Modals */}
      <AddEventModal
        open={addEventOpen}
        onOpenChange={setAddEventOpen}
        onEventAdded={fetchEvents}
        currentUserId={currentUserId}
      />

      <TimelineIntegrationModal
        open={timelineIntegrationOpen}
        onOpenChange={setTimelineIntegrationOpen}
        onEventsImported={fetchEvents}
        currentUserId={currentUserId}
      />

      <ReconstructJourneyModal
        open={reconstructOpen}
        onOpenChange={setReconstructOpen}
        onEventsCreated={fetchEvents}
        currentUserId={currentUserId}
      />

      <RoleManagementModal
        open={roleManagementOpen}
        onOpenChange={setRoleManagementOpen}
      />
    </div>
  );
};

export default CollaborationLedger;
