import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";

const Dashboard = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4">
      <div className="max-w-4xl w-full text-center space-y-8">
        <div className="space-y-4">
          <h1 className="text-4xl md:text-5xl font-bold text-white">
            Welcome, Frensei Member
          </h1>
          <p className="text-xl md:text-2xl text-muted-foreground">
            Your Research Climate Awaits.
          </p>
        </div>

        <div className="card-frensei p-8 space-y-6">
          <p className="text-white text-lg">
            You have successfully logged in to your Frensei dashboard.
          </p>
          <p className="text-muted-foreground">
            This is a placeholder dashboard. More features coming soon!
          </p>
          
          <div className="flex gap-4 justify-center pt-4">
            <Button
              onClick={() => navigate("/wellbeing")}
              variant="outline"
              className="border-primary text-primary hover:bg-primary hover:text-white"
            >
              Go to Check-in
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
