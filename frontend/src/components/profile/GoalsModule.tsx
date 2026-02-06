import { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Plus, Trash2 } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

type Goal = {
  id: string;
  user_id: string;
  title: string;
  description?: string | null;
  priority: string;
  completed: boolean;
  due_date?: string | null;
  created_at: string;
  updated_at: string;
};

export const GoalsModule = () => {
  const [goals, setGoals] = useState<Goal[]>([]);
  const [isAddingGoal, setIsAddingGoal] = useState(false);
  const [newGoalTitle, setNewGoalTitle] = useState("");
  const [newGoalPriority, setNewGoalPriority] = useState<"low" | "medium" | "high">("medium");
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    fetchGoals();
  }, []);

  const fetchGoals = async () => {
    try {
      // TODO: Replace with your backend API call
      const storedGoals = localStorage.getItem("goals");
      const goals = storedGoals ? JSON.parse(storedGoals) : [];
      setGoals(goals);
    } catch (error) {
      console.error("Error fetching goals:", error);
      toast({
        title: "Error",
        description: "Failed to load goals",
        variant: "destructive",
      });
    }
  };

  const addGoal = async () => {
    if (!newGoalTitle.trim()) return;

    setIsLoading(true);
    try {
      const userId = sessionStorage.getItem("userId");
      if (!userId) throw new Error("Not authenticated");

      const newGoal: Goal = {
        id: `goal_${Date.now()}`,
        user_id: userId,
        title: newGoalTitle,
        priority: newGoalPriority,
        completed: false,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };

      // Store in localStorage (replace with backend API)
      const storedGoals = localStorage.getItem("goals");
      const goals = storedGoals ? JSON.parse(storedGoals) : [];
      goals.push(newGoal);
      localStorage.setItem("goals", JSON.stringify(goals));

      toast({
        title: "Success",
        description: "Goal added successfully",
      });

      setNewGoalTitle("");
      setNewGoalPriority("medium");
      setIsAddingGoal(false);
      fetchGoals();
    } catch (error) {
      console.error("Error adding goal:", error);
      toast({
        title: "Error",
        description: "Failed to add goal",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const toggleGoalCompletion = async (goalId: string, currentStatus: boolean) => {
    try {
      // TODO: Replace with your backend API call
      const storedGoals = localStorage.getItem("goals");
      const goals = storedGoals ? JSON.parse(storedGoals) : [];
      const goalIndex = goals.findIndex((g: Goal) => g.id === goalId);
      
      if (goalIndex !== -1) {
        goals[goalIndex].completed = !currentStatus;
        goals[goalIndex].updated_at = new Date().toISOString();
        localStorage.setItem("goals", JSON.stringify(goals));
        fetchGoals();
      }
    } catch (error) {
      console.error("Error updating goal:", error);
      toast({
        title: "Error",
        description: "Failed to update goal",
        variant: "destructive",
      });
    }
  };

  const deleteGoal = async (goalId: string) => {
    try {
      // TODO: Replace with your backend API call
      const storedGoals = localStorage.getItem("goals");
      const goals = storedGoals ? JSON.parse(storedGoals) : [];
      const filteredGoals = goals.filter((g: Goal) => g.id !== goalId);
      localStorage.setItem("goals", JSON.stringify(filteredGoals));

      toast({
        title: "Success",
        description: "Goal deleted successfully",
      });
      fetchGoals();
    } catch (error) {
      console.error("Error deleting goal:", error);
      toast({
        title: "Error",
        description: "Failed to delete goal",
        variant: "destructive",
      });
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "high": return "border-destructive/50 text-destructive";
      case "medium": return "border-warning/50 text-warning";
      case "low": return "border-success/50 text-success";
      default: return "border-muted/50 text-muted-foreground";
    }
  };

  return (
    <Card className="bg-card/50 border-border/50">
      <CardContent className="p-6">
        {goals.length === 0 ? (
          <p className="text-center text-muted-foreground py-8">
            No goals yet. Add your first goal to get started!
          </p>
        ) : (
          <div className="space-y-3">
            {goals.map((goal) => (
              <div 
                key={goal.id} 
                className="flex items-center gap-3 p-3 bg-background/50 rounded-lg border border-border/50"
              >
                <Checkbox 
                  checked={goal.completed}
                  onCheckedChange={() => toggleGoalCompletion(goal.id, goal.completed)}
                  className="border-border"
                />
                <span className={`flex-1 text-sm ${goal.completed ? 'line-through text-muted-foreground' : 'text-foreground'}`}>
                  {goal.title}
                </span>
                <Badge 
                  variant="outline" 
                  className={getPriorityColor(goal.priority)}
                >
                  {goal.priority}
                </Badge>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-8 w-8 p-0 text-muted-foreground hover:text-destructive"
                  onClick={() => deleteGoal(goal.id)}
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            ))}
          </div>
        )}

        <Dialog open={isAddingGoal} onOpenChange={setIsAddingGoal}>
          <DialogTrigger asChild>
            <Button 
              className="w-full mt-4 border-primary/50 text-primary hover:bg-primary/10"
              variant="outline"
            >
              <Plus className="w-4 h-4 mr-2" />
              Add New Goal
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-card border-border">
            <DialogHeader>
              <DialogTitle className="text-foreground">Add New Goal</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 pt-4">
              <div>
                <label className="text-sm font-medium text-foreground mb-2 block">Goal Title</label>
                <Input
                  value={newGoalTitle}
                  onChange={(e) => setNewGoalTitle(e.target.value)}
                  placeholder="e.g., Write 400 words today"
                  className="bg-background border-border text-foreground"
                />
              </div>
              <div>
                <label className="text-sm font-medium text-foreground mb-2 block">Priority</label>
                <Select value={newGoalPriority} onValueChange={(v) => setNewGoalPriority(v as "low" | "medium" | "high")}>
                  <SelectTrigger className="bg-background border-border text-foreground">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">Low</SelectItem>
                    <SelectItem value="medium">Medium</SelectItem>
                    <SelectItem value="high">High</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Button
                onClick={addGoal}
                disabled={isLoading || !newGoalTitle.trim()}
                className="w-full bg-primary hover:bg-primary/90 text-primary-foreground"
              >
                {isLoading ? "Adding..." : "Add Goal"}
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </CardContent>
    </Card>
  );
};
