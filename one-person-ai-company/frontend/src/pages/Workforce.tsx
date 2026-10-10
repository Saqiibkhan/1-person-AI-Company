import { useAgents } from "@/hooks/useAgents";
import { useProjects } from "@/hooks/useProjects";
import { useQueries } from "@tanstack/react-query";
import { useMemo } from "react";
import { AgentCard } from "@/components/agents/AgentCard";
import { Skeleton } from "@/components/ui/Skeleton";
import { ErrorState } from "@/components/ui/ErrorState";
import * as api from "@/services/api";

export default function Workforce() {
  const { data: agents, isLoading, isError, refetch } = useAgents();
  const { data: projects } = useProjects();

  const taskQueries = useQueries({
    queries: (projects ?? []).map((p) => ({
      queryKey: ["projects", p.id, "tasks"],
      queryFn: () => api.getProjectTasks(p.id),
    })),
  });
  const allTasks = useMemo(() => taskQueries.flatMap((q) => q.data ?? []), [taskQueries]);

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {[...Array(5)].map((_, i) => (
          <Skeleton key={i} className="h-40" />
        ))}
      </div>
    );
  }

  if (isError || !agents) {
    return <ErrorState title="Unable to load workforce" onRetry={() => refetch()} />;
  }

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {agents.map((agent) => (
        <AgentCard key={agent.name} agent={agent} tasks={allTasks} />
      ))}
    </div>
  );
}
