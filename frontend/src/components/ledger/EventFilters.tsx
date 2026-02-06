import { useState, useEffect } from "react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Card } from "@/components/ui/card";

interface EventFiltersProps {
  events: any[];
  onFilter: (filtered: any[]) => void;
}

export const EventFilters = ({ events, onFilter }: EventFiltersProps) => {
  const [typeFilter, setTypeFilter] = useState<string>("all");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [participantFilter, setParticipantFilter] = useState<string>("all");

  useEffect(() => {
    applyFilters();
  }, [typeFilter, statusFilter, participantFilter, events]);

  const applyFilters = () => {
    let filtered = [...events];

    if (typeFilter !== "all") {
      filtered = filtered.filter(e => e.event_type === typeFilter);
    }

    if (statusFilter !== "all") {
      filtered = filtered.filter(e => e.status === statusFilter);
    }

    if (participantFilter !== "all") {
      filtered = filtered.filter(e =>
        e.participants?.some((p: any) => p.user_id === participantFilter)
      );
    }

    onFilter(filtered);
  };

  const uniqueParticipants = Array.from(
    new Set(
      events.flatMap(e =>
        e.participants?.map((p: any) => ({
          id: p.user_id,
          name: p.project_members?.display_name || 'Unknown'
        })) || []
      )
    )
  );

  return (
    <Card className="p-6 mb-8 card-frensei">
      <h3 className="font-semibold mb-4">Filters</h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <Label>Event Type</Label>
          <Select value={typeFilter} onValueChange={setTypeFilter}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Types</SelectItem>
              <SelectItem value="meeting">Meeting</SelectItem>
              <SelectItem value="feedback_given">Feedback Given</SelectItem>
              <SelectItem value="draft_submitted">Draft Submitted</SelectItem>
              <SelectItem value="revision_request">Revision Request</SelectItem>
              <SelectItem value="delay_explained">Delay Explained</SelectItem>
              <SelectItem value="coauthor_discussion">Co-author Discussion</SelectItem>
              <SelectItem value="dataset_shared">Dataset Shared</SelectItem>
              <SelectItem value="decision_made">Decision Made</SelectItem>
              <SelectItem value="general_note">General Note</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div>
          <Label>Status</Label>
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Statuses</SelectItem>
              <SelectItem value="pending">Pending</SelectItem>
              <SelectItem value="verified">Verified</SelectItem>
              <SelectItem value="rejected">Rejected</SelectItem>
              <SelectItem value="observer_acknowledged">Observer Acknowledged</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div>
          <Label>Participant</Label>
          <Select value={participantFilter} onValueChange={setParticipantFilter}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Participants</SelectItem>
              {uniqueParticipants.map((p: any) => (
                <SelectItem key={p.id} value={p.id}>
                  {p.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>
    </Card>
  );
};
