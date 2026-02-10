import { Outlet } from "react-router-dom";
import { Header } from "./Header";

export const Layout = () => (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="pt-16">
        <Outlet />
      </main>
    </div>
);
