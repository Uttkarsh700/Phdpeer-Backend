import { useNavigate } from "react-router-dom";
import { Card, CardContent } from "@/components/ui/card";
import { FileText, Calendar, Users, DollarSign } from "lucide-react";

const stats = [
  {
    id: "papers",
    title: "Papers in Progress",
    value: "2 drafts, 1 under review",
    icon: FileText,
    route: "/timeline",
    color: "text-info"
  },
  {
    id: "milestone",
    title: "Next Milestone Due",
    value: "Submit methods chapter – Jan 18",
    icon: Calendar,
    route: "/timeline",
    color: "text-warning"
  },
  {
    id: "supervisor",
    title: "Last Supervisor Interaction",
    value: "12 days ago",
    icon: Users,
    route: "/collaboration-ledger",
    color: "text-secondary"
  },
  {
    id: "grants",
    title: "Available Grants",
    value: "3 opportunities based on your field",
    icon: DollarSign,
    route: "/profile-strength",
    color: "text-success"
  }
];

export const QuickStatsGrid = () => {
  const navigate = useNavigate();

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {stats.map((stat) => {
        const IconComponent = stat.icon;
        return (
          <Card
            key={stat.id}
            onClick={() => navigate(stat.route)}
            className="bg-card/50 border-border/50 cursor-pointer transition-all duration-300 hover:scale-[1.02] hover:shadow-[0_0_20px_rgba(230,146,25,0.3)] hover:border-primary/50 group"
          >
            <CardContent className="p-5">
              <div className="flex items-start gap-3">
                <div className={`${stat.color} group-hover:scale-110 transition-transform duration-300`}>
                  <IconComponent className="w-6 h-6" />
                </div>
                <div className="flex-1">
                  <p className="text-sm text-muted-foreground mb-1 group-hover:text-foreground transition-colors">{stat.title}</p>
                  <p className="text-sm font-semibold text-foreground">{stat.value}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
};
