import { useEffect, useState } from "react";
import { useNavigate, useLocation, Outlet } from "react-router-dom";
import { Header } from "./Header";

export const Layout = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [loading, setLoading] = useState(false);

  // Handle route protection
  useEffect(() => {
    // Check gateway access
    const hasAccess = sessionStorage.getItem("frensei_access");
    if (!hasAccess && location.pathname !== "/") {
      navigate("/");
      return;
    }

    // TODO: Replace with your backend authentication check
    // For now, check if user is authenticated via sessionStorage
    const isAuthenticated = sessionStorage.getItem("isAuthenticated") === "true";
    
    // Check authentication for protected routes
    const protectedRoutes = [
      "/wellbeing", 
      "/timeline", 
      "/network", 
      "/university-dashboard", 
      "/collaboration-ledger", 
      "/dashboard",
      "/writing-evolution"
    ];
    const isProtectedRoute = protectedRoutes.some(route => location.pathname.startsWith(route));

    if (isProtectedRoute && !isAuthenticated) {
      navigate("/auth", { state: { from: location.pathname } });
    }
  }, [location.pathname, navigate]);

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="pt-16">
        {loading ? (
          <div className="flex items-center justify-center h-screen">
            <div className="text-white">Loading...</div>
          </div>
        ) : (
          <Outlet />
        )}
      </main>
    </div>
  );
};
