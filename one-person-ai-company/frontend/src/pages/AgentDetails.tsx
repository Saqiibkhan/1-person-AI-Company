import { useParams } from "react-router-dom";
import { useAgents, useAgentStats } from "@/hooks/useAgents";
import { useProjects } from "@/hooks/useProjects";
import { useProjectTasks } from "@/hooks/useTasks";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { TaskStatusBadge } from "@/components/tasks/TaskStatus";
import { Skeleton } from "@/components/ui/Skeleton";

export default function AgentDetails() {
  const { agentName } = useParams();
  const { data: agents } = useAgents();
  const { data: stats } = useAgentStats(agentName);
  const { data: projects } = useProjects();
  const mostRecentProjectId = projects?.[0]?.id;
  const { data: tasks } = useProjectTasks(mostRecentProjectId);

  const agent = agents?.find((a) => a.name === agentName);
  const agentTasks = (tasks ?? []).filter((t) => t.assigned_agent === agentName);

  if (!agent) return <Skeleton className="h-64" />;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold capitalize">{agent.name} Agent</h2>
        <p className="text-sm text-muted-foreground">{agent.role}</p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Responsibilities</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="mb-3 text-sm text-muted-foreground">{agent.description}</p>
              <div className="flex flex-wrap gap-1.5">
                {agent.capabilities.map((c) => (
                  <Badge key={c}>{c}</Badge>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Recent Tasks</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {agentTasks.length === 0 && <p className="text-sm text-muted-foreground">No recent tasks.</p>}
              {agentTasks.map((t) => (
                <div key={t.id} className="flex items-center justify-between rounded-md border border-border p-2 text-sm">
                  <span>{t.title}</span>
                  <TaskStatusBadge status={t.status} />
                </div>
              ))}
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Performance</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <div className="flex justify-between"><span className="text-muted-foreground">Total runs</span><span>{stats?.total_runs ?? "-"}</span></div>
            <div className="flex justify-between"><span className="text-muted-foreground">Approved</span><span>{stats?.approved_count ?? "-"}</span></div>
            <div className="flex justify-between"><span className="text-muted-foreground">Revisions requested</span><span>{stats?.revision_count ?? "-"}</span></div>
            <div className="flex justify-between"><span className="text-muted-foreground">Failed</span><span>{stats?.failed_count ?? "-"}</span></div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
