import { useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { useQueries } from "@tanstack/react-query";
import { Plus, Circle } from "lucide-react";
import { useProjects } from "@/hooks/useProjects";
import { useProjectTasks } from "@/hooks/useTasks";
import { useProjectEvents } from "@/hooks/useProjectEvents";
import { OverviewCards } from "@/components/dashboard/OverviewCards";
import { ActiveWork } from "@/components/dashboard/ActiveWork";
import { ActivityTimeline } from "@/components/dashboard/ActivityTimeline";
import { Button } from "@/components/ui/Button";
import { ErrorState } from "@/components/ui/ErrorState";
import * as api from "@/services/api";

export default function Dashboard() {
  const { data: projects, isLoading, isError, refetch } = useProjects();
  const navigate = useNavigate();

  // Most-recently-active project drives "Current Work" + the activity feed.
  const mostRecent = projects?.find((p) => p.status === "RUNNING" || p.status === "PLANNING") ?? projects?.[0];

  const { data: currentTasks } = useProjectTasks(mostRecent?.id);
  const { events } = useProjectEvents(mostRecent?.id);

  // Pull tasks for every project so overview counts are accurate, not just the active one.
  const allTaskQueries = useQueries({
    queries: (projects ?? []).map((p) => ({
      queryKey: ["projects", p.id, "tasks"],
      queryFn: () => api.getProjectTasks(p.id),
      enabled: !!projects,
    })),
  });
  const allTasks = useMemo(() => allTaskQueries.flatMap((q) => q.data ?? []), [allTaskQueries]);

  const activeProjectCount = projects?.filter((p) => p.status === "RUNNING" || p.status === "PLANNING").length ?? 0;
  const activeTaskCount = allTasks.filter((t) => t.status === "RUNNING" || t.status === "REVIEWING").length;

  if (isError) {
    return <ErrorState title="Unable to load dashboard" message="The backend could not be reached." onRetry={() => refetch()} />;
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4 rounded-lg border border-border bg-card p-5">
        <div>
          <p className="text-xs font-medium text-subtle-foreground">Your AI workforce at a glance.</p>
          <p className="mt-1 text-sm text-muted-foreground">
            {isLoading
              ? "Loading company status..."
              : activeProjectCount > 0
                ? `Currently working across ${activeProjectCount} project${activeProjectCount === 1 ? "" : "s"} and ${activeTaskCount} active task${activeTaskCount === 1 ? "" : "s"}.`
                : "No active work right now."}
          </p>
          <div className="mt-2 flex items-center gap-1.5 text-xs text-muted-foreground">
            <Circle className="h-2 w-2 fill-success text-success" />
            Operational
          </div>
        </div>
        <Button onClick={() => navigate("/projects")}>
          <Plus className="h-4 w-4" /> New Project
        </Button>
      </div>

      <OverviewCards projects={projects} allTasks={allTasks} isLoading={isLoading} />
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <ActiveWork project={mostRecent} tasks={currentTasks} />
        <ActivityTimeline events={events} isLoading={isLoading} />
      </div>
    </div>
  );
}
