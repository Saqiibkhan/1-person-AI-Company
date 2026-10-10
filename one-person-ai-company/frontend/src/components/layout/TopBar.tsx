import { useLocation } from "react-router-dom";
import { Search, Bell } from "lucide-react";
import { Input } from "@/components/ui/Input";

const PAGE_TITLES: Record<string, string> = {
  "/": "Command Center",
  "/projects": "Projects",
  "/tasks": "Tasks",
  "/workforce": "AI Workforce",
  "/activity": "Activity",
  "/deliverables": "Deliverables",
  "/settings": "Settings",
};

export function TopBar() {
  const location = useLocation();
  const title = PAGE_TITLES[location.pathname] ?? "ONEPERSON AI";

  return (
    <header className="flex h-14 items-center justify-between border-b border-border bg-card px-6">
      <h1 className="text-sm font-semibold">{title}</h1>
      <div className="flex items-center gap-3">
        <div className="relative hidden sm:block">
          <Search className="pointer-events-none absolute left-2.5 top-2.5 h-3.5 w-3.5 text-muted-foreground" />
          <Input placeholder="Search..." className="w-56 pl-8" />
        </div>
        <button className="relative rounded-md p-2 text-muted-foreground hover:bg-muted hover:text-foreground">
          <Bell className="h-4 w-4" />
        </button>
      </div>
    </header>
  );
}
