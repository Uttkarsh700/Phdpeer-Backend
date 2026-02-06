import { format, parseISO } from "date-fns";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { CheckCircle2, XCircle, Clock } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";

interface Participant {
  user_id: string;
  role: string;
  display_name?: string;
}

interface Verification {
  user_id: string;
  verified: boolean;
  verified_at: string;
}

interface CollaborationEvent {
  id: string;
  event_type: string;
  summary: string;
  event_date: string;
  status: string;
  created_at: string;
  participants?: Participant[];
  verifications?: Verification[];
}

interface TimelineViewProps {
  events: CollaborationEvent[];
}

const EVENT_TYPE_COLORS: Record<string, string> = {
  meeting: "hsl(217, 91%, 60%)",
  feedback_given: "hsl(142, 71%, 45%)",
  draft_submitted: "hsl(262, 83%, 58%)",
  revision_request: "hsl(45, 93%, 47%)",
  delay_explained: "hsl(25, 95%, 53%)",
  coauthor_discussion: "hsl(330, 81%, 60%)",
  dataset_shared: "hsl(189, 94%, 43%)",
  decision_made: "hsl(239, 84%, 67%)",
  general_note: "hsl(220, 9%, 46%)",
};

const ROLE_COLORS: Record<string, string> = {
  collaborator: "hsl(217, 91%, 60%)",
  overseer: "hsl(262, 83%, 58%)",
  viewer: "hsl(220, 9%, 46%)",
};

const getVerificationIcon = (verified?: boolean) => {
  if (verified === true) return <CheckCircle2 className="h-4 w-4 text-green-500" />;
  if (verified === false) return <XCircle className="h-4 w-4 text-red-500" />;
  return <Clock className="h-4 w-4 text-muted-foreground" />;
};

const getVerificationStatus = (verified?: boolean) => {
  if (verified === true) return "Approved";
  if (verified === false) return "Rejected";
  return "Pending";
};

const getParticipantDisplayName = (participant: Participant) => {
  if (participant.display_name) return participant.display_name;
  
  // Try to get display name from project members
  const storedMembers = localStorage.getItem('project_members');
  if (storedMembers) {
    const members = JSON.parse(storedMembers);
    const member = members.find((m: any) => m.user_id === participant.user_id);
    if (member?.display_name) return member.display_name;
  }
  
  return participant.user_id.substring(0, 8);
};

export const TimelineView = ({ events }: TimelineViewProps) => {
  // Group events by month
  const eventsByMonth = events.reduce((acc, event) => {
    const monthKey = format(parseISO(event.event_date), "MMMM yyyy");
    if (!acc[monthKey]) {
      acc[monthKey] = [];
    }
    acc[monthKey].push(event);
    return acc;
  }, {} as Record<string, CollaborationEvent[]>);

  // Sort months chronologically
  const sortedMonths = Object.keys(eventsByMonth).sort((a, b) => {
    return parseISO(eventsByMonth[b][0].event_date).getTime() - parseISO(eventsByMonth[a][0].event_date).getTime();
  });

  return (
    <ScrollArea className="h-[calc(100vh-300px)]">
      <div className="relative">
        {sortedMonths.map((month, monthIndex) => (
          <div key={month} className="flex gap-8 mb-12">
            {/* Left: Month marker */}
            <div className="w-32 flex-shrink-0 sticky top-0 pt-2">
              <div className="text-lg font-semibold text-foreground">{month}</div>
              {monthIndex < sortedMonths.length - 1 && (
                <div className="absolute left-12 top-12 bottom-0 w-0.5 bg-border" />
              )}
            </div>

            {/* Right: Events for this month */}
            <div className="flex-1 space-y-6">
              {eventsByMonth[month]
                .sort((a, b) => parseISO(b.event_date).getTime() - parseISO(a.event_date).getTime())
                .map((event) => (
                  <Card key={event.id} className="relative border-l-4" style={{ borderLeftColor: EVENT_TYPE_COLORS[event.event_type] || "#6B7280" }}>
                    <CardHeader className="pb-3">
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <Badge variant="secondary" className="capitalize">
                              {event.event_type.replace(/_/g, " ")}
                            </Badge>
                            <span className="text-sm text-muted-foreground">
                              {format(parseISO(event.event_date), "MMM d, yyyy")}
                            </span>
                          </div>
                          <p className="text-sm text-foreground">{event.summary}</p>
                        </div>
                      </div>
                    </CardHeader>

                    <CardContent className="pt-0">
                      {/* Participants - Only shows actual event participants */}
                      {event.participants && event.participants.length > 0 && (
                        <div className="space-y-3">
                          <p className="text-sm font-medium text-muted-foreground">
                            Participants & Verification Status ({event.participants.length})
                          </p>
                          <div className="flex flex-wrap gap-2">
                            {event.participants.map((participant) => {
                              const verification = event.verifications?.find(
                                (v) => v.user_id === participant.user_id
                              );
                              const roleColor = ROLE_COLORS[participant.role] || ROLE_COLORS.viewer;
                              const isVerified = verification?.verified === true;
                              const isRejected = verification?.verified === false;
                              const isPending = !verification;
                              
                              return (
                                <div
                                  key={participant.user_id}
                                  className="flex items-center gap-2 rounded-lg px-3 py-2 border-2"
                                  style={{ 
                                    borderColor: roleColor,
                                    backgroundColor: `${roleColor}10`
                                  }}
                                >
                                  <Avatar className="h-8 w-8" style={{ backgroundColor: roleColor }}>
                                    <AvatarFallback className="text-xs text-white font-semibold">
                                      {getParticipantDisplayName(participant).substring(0, 2).toUpperCase()}
                                    </AvatarFallback>
                                  </Avatar>
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
                                    {isVerified && <CheckCircle2 className="h-4 w-4 text-green-600" />}
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
                    </CardContent>
                  </Card>
                ))}
            </div>
          </div>
        ))}
      </div>
    </ScrollArea>
  );
};
