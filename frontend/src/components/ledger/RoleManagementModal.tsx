import { useState, useEffect } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";
import { UserPlus, Trash2 } from "lucide-react";

interface RoleManagementModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export const RoleManagementModal = ({ open, onOpenChange }: RoleManagementModalProps) => {
  const [members, setMembers] = useState<any[]>([]);
  const [displayName, setDisplayName] = useState("");
  const [role, setRole] = useState<string>("collaborator");
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    if (open) {
      fetchMembers();
    }
  }, [open]);

  const fetchMembers = async () => {
    const storedMembers = localStorage.getItem('project_members');
    setMembers(storedMembers ? JSON.parse(storedMembers) : []);
  };

  const handleRemoveMember = async (memberId: string) => {
    try {
      const storedMembers = localStorage.getItem('project_members');
      const members = storedMembers ? JSON.parse(storedMembers) : [];
      const updated = members.filter((m: any) => m.id !== memberId);
      localStorage.setItem('project_members', JSON.stringify(updated));

      toast({
        title: "Success",
        description: "Team member removed"
      });

      fetchMembers();
    } catch (error) {
      console.error('Error removing member:', error);
      toast({
        title: "Error",
        description: "Failed to remove team member",
        variant: "destructive"
      });
    }
  };

  const handleAddMember = async () => {
    if (!displayName.trim()) {
      toast({
        title: "Missing Name",
        description: "Please enter a display name",
        variant: "destructive"
      });
      return;
    }

    setLoading(true);
    try {
      const storedMembers = localStorage.getItem('project_members');
      const members = storedMembers ? JSON.parse(storedMembers) : [];

      const newMember = {
        id: `member_${Date.now()}`,
        user_id: `user_${Date.now()}`,
        display_name: displayName,
        role: role
      };

      members.push(newMember);
      localStorage.setItem('project_members', JSON.stringify(members));

      toast({
        title: "Success",
        description: "Team member added"
      });

      setDisplayName("");
      setRole("collaborator");
      fetchMembers();
    } catch (error) {
      console.error('Error adding member:', error);
      toast({
        title: "Error",
        description: "Failed to add team member",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const getRoleBadgeColor = (role: string) => {
    switch (role) {
      case 'collaborator':
        return 'bg-blue-500';
      case 'overseer':
        return 'bg-purple-500';
      case 'viewer':
        return 'bg-gray-500';
      default:
        return 'bg-gray-500';
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold">Role Management</DialogTitle>
          <DialogDescription>
            Manage your research team members and their roles
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Role Descriptions */}
          <div className="grid gap-4 p-4 bg-muted rounded-lg">
            <div>
              <Badge className="bg-blue-500 text-white mb-1">Collaborator</Badge>
              <p className="text-sm text-muted-foreground">
                Active participants who can add, verify, and reject events
              </p>
            </div>
            <div>
              <Badge className="bg-purple-500 text-white mb-1">Overseer</Badge>
              <p className="text-sm text-muted-foreground">
                Can view everything and optionally acknowledge events (no verification required)
              </p>
            </div>
            <div>
              <Badge className="bg-gray-500 text-white mb-1">Viewer</Badge>
              <p className="text-sm text-muted-foreground">
                Read-only access to all event logs
              </p>
            </div>
          </div>

          {/* Add Member Form */}
          <div className="border rounded-lg p-4 space-y-4">
            <h3 className="font-medium">Add Team Member</h3>
            <div className="grid gap-4">
              <div>
                <Label htmlFor="displayName">Display Name</Label>
                <Input
                  id="displayName"
                  value={displayName}
                  onChange={(e) => setDisplayName(e.target.value)}
                  placeholder="e.g., Dr. Sarah Smith"
                />
              </div>
              <div>
                <Label htmlFor="role">Role</Label>
                <Select value={role} onValueChange={setRole}>
                  <SelectTrigger id="role">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="collaborator">Collaborator</SelectItem>
                    <SelectItem value="overseer">Overseer</SelectItem>
                    <SelectItem value="viewer">Viewer</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Button
                onClick={handleAddMember}
                disabled={loading}
                className="bg-gradient-to-r from-[#DB5614] to-[#E69219]"
              >
                <UserPlus className="mr-2 h-4 w-4" />
                Add Member
              </Button>
            </div>
          </div>

          {/* Current Members */}
          <div>
            <h3 className="font-medium mb-4">Current Team Members</h3>
            <div className="space-y-3">
              {members.map(member => (
                <div
                  key={member.id}
                  className="flex items-center justify-between p-3 border rounded-lg"
                >
                  <div>
                    <p className="font-medium">{member.display_name}</p>
                    <Badge className={`${getRoleBadgeColor(member.role)} text-white mt-1 capitalize`}>
                      {member.role}
                    </Badge>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleRemoveMember(member.id)}
                  >
                    <Trash2 className="h-4 w-4 text-destructive" />
                  </Button>
                </div>
              ))}
              {members.length === 0 && (
                <p className="text-center text-muted-foreground py-8">
                  No team members yet. Add your first member above.
                </p>
              )}
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};
