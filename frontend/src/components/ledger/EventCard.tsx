import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { CheckCircle, XCircle, Clock, Eye } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface EventCardProps {
  event: any;
  onUpdate: () => void;
  currentUserId: string | null;
}

const EVENT_TYPE_COLORS: Record<string, string> = {
  meeting: "bg-blue-500",
  feedback_given: "bg-green-500",
  draft_submitted: "bg-purple-500",
  revision_request: "bg-yellow-500",
  delay_explained: "bg-orange-500",
  coauthor_discussion: "bg-pink-500",
  dataset_shared: "bg-cyan-500",
  decision_made: "bg-indigo-500",
  general_note: "bg-gray-500"
};

const ROLE_COLORS: Record<string, string> = {
  collaborator: "hsl(217, 91%, 60%)",
  overseer: "hsl(262, 83%, 58%)",
  viewer: "hsl(220, 9%, 46%)",
};

const STATUS_CONFIG: Record<string, { label: string; color: string; icon: any }> = {
  pending: { label: "Pending Verification", color: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200", icon: Clock },
  verified: { label: "Verified", color: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200", icon: CheckCircle },
  rejected: { label: "Rejected", color: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200", icon: XCircle },
  observer_acknowledged: { label: "Observer Acknowledged", color: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200", icon: Eye }
};

const getParticipantDisplayName = (participant: any) => {
  if (participant.display_name) return participant.display_name;
  return participant.user_id.substring(0, 8);
};

export const EventCard = ({ event, onUpdate, currentUserId }: EventCardProps) => {
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();
  const statusConfig = STATUS_CONFIG[event.status] || STATUS_CONFIG.pending;
  const StatusIcon = statusConfig.icon;

  const handleVerification = async (verified: boolean) => {
    setLoading(true);
    try {
      if (!currentUserId) {
        toast({
          title: "Error",
          description: "User session not found",
          variant: "destructive"
        });
        return;
      }

      // Check if user is a participant
      const isParticipant = event.participants?.some((p: any) => p.user_id === currentUserId);
      if (!isParticipant) {
        toast({
          title: "Not Authorized",
          description: "You must be a participant to verify this event",
          variant: "destructive"
        });
        return;
      }

      // TODO: Replace with your backend API call
      // Update verification in localStorage
      const storedEvents = localStorage.getItem("collaboration_events");
      const events = storedEvents ? JSON.parse(storedEvents) : [];
      const eventIndex = events.findIndex((e: any) => e.id === event.id);
      
      if (eventIndex !== -1) {
        const updatedEvent = { ...events[eventIndex] };
        
        // Update or add verification
        if (!updatedEvent.verifications) {
          updatedEvent.verifications = [];
        }
        
        const verificationIndex = updatedEvent.verifications.findIndex(
          (v: any) => v.user_id === currentUserId
        );
        
        const verification = {
          event_id: event.id,
          user_id: currentUserId,
          verified,
          verified_at: new Date().toISOString()
        };
        
        if (verificationIndex !== -1) {
          updatedEvent.verifications[verificationIndex] = verification;
        } else {
          updatedEvent.verifications.push(verification);
        }

        // Calculate new status based on all verifications
        const allVerifications = updatedEvent.verifications;
        let newStatus = updatedEvent.status;
        
        if (allVerifications && allVerifications.length > 0) {
          const hasRejection = allVerifications.some((v: any) => !v.verified);
          const allVerified = allVerifications.every((v: any) => v.verified);
          
          if (hasRejection) {
            newStatus = "rejected";
          } else if (allVerified && allVerifications.length === updatedEvent.participants?.length) {
            newStatus = "verified";
          }
        }

        updatedEvent.status = newStatus;
        events[eventIndex] = updatedEvent;
        localStorage.setItem("collaboration_events", JSON.stringify(events));
      }

      toast({
        title: "Success",
        description: verified ? "Event verified" : "Event rejected"
      });

      onUpdate();
    } catch (error) {
      console.error('Error verifying event:', error);
      toast({
        title: "Error",
        description: "Failed to update verification",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };


  const userVerification = event.verifications?.find((v: any) => v.user_id === currentUserId);
  const isParticipant = event.participants?.some((p: any) => p.user_id === currentUserId);

  return (
    <Card className="p-6 card-frensei">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <Badge
              className={`${EVENT_TYPE_COLORS[event.event_type] || 'bg-gray-500'} text-white`}
            >
              {event.event_type.replace(/_/g, ' ')}
            </Badge>
            <Badge className={statusConfig.color}>
              <StatusIcon className="h-3 w-3 mr-1" />
              {statusConfig.label}
            </Badge>
          </div>
          <h3 className="text-xl font-semibold text-foreground mb-2">
            {event.summary}
          </h3>
          <p className="text-sm text-muted-foreground">
            {formatDate(event.event_date)}
          </p>
        </div>
      </div>

      {/* Participants Section - Only shows actual event participants */}
      {event.participants && event.participants.length > 0 && (
        <div className="space-y-3 mb-4">
          <div className="text-sm font-medium text-muted-foreground">
            Participants & Verification Status ({event.participants.length})
          </div>
          <div className="flex flex-wrap gap-2">
            {event.participants.map((participant: any, index: number) => {
              const verification = event.verifications?.find(
                (v: any) => v.user_id === participant.user_id
              );
              const roleColor = ROLE_COLORS[participant.role] || ROLE_COLORS.viewer;
              const isVerified = verification?.verified === true;
              const isRejected = verification?.verified === false;
              const isPending = !verification;
              
              return (
                <div
                  key={index}
                  className="flex items-center gap-2 rounded-lg px-3 py-2 border-2"
                  style={{ 
                    borderColor: roleColor,
                    backgroundColor: `${roleColor}10`
                  }}
                >
                  <div className="flex flex-col">
                    <span className="text-sm font-semibold" style={{ color: roleColor }}>
                      {getParticipantDisplayName(participant)}
                    </span>
                    <span className="text-[10px] text-muted-foreground capitalize">
                      {participant.role}
                    </span>
                  </div>
                  <div className="flex items-center gap-1.5 ml-2 px-2 py-1 rounded-md" style={{
                    backgroundColor: isVerified ? 'hsl(142, 71%, 45%, 0.15)' : isRejected ? 'hsl(0, 84%, 60%, 0.15)' : 'hsl(45, 93%, 47%, 0.15)'
                  }}>
                    {isVerified && <CheckCircle className="h-4 w-4 text-green-600" />}
                    {isRejected && <XCircle className="h-4 w-4 text-red-600" />}
                    {isPending && <Clock className="h-4 w-4 text-yellow-600" />}
                    <span className="text-xs font-medium" style={{
                      color: isVerified ? 'hsl(142, 71%, 35%)' : isRejected ? 'hsl(0, 84%, 50%)' : 'hsl(45, 93%, 37%)'
                    }}>
                      {isVerified ? 'Approved' : isRejected ? 'Rejected' : 'Pending'}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Verification Actions - Only show if user is a participant and hasn't verified yet */}
      {isParticipant && event.status === 'pending' && !userVerification && (
        <div className="flex gap-3 mt-4 pt-4 border-t">
          <Button
            onClick={() => handleVerification(true)}
            disabled={loading}
            variant="outline"
            className="border-green-500 text-green-500 hover:bg-green-500 hover:text-white"
          >
            <CheckCircle className="mr-2 h-4 w-4" />
            Approve
          </Button>
          <Button
            onClick={() => handleVerification(false)}
            disabled={loading}
            variant="outline"
            className="border-red-500 text-red-500 hover:bg-red-500 hover:text-white"
          >
            <XCircle className="mr-2 h-4 w-4" />
            Reject
          </Button>
        </div>
      )}

      {/* Show user's verification status */}
      {userVerification && (
        <div className="mt-4 pt-4 border-t text-sm text-muted-foreground">
          You {userVerification.verified ? "approved" : "rejected"} this event
        </div>
      )}
    </Card>
  );
};
