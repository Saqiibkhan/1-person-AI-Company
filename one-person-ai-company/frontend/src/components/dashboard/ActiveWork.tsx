import { Link } from "react-router-dom";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import { TaskStatusBadge } from "@/components/tasks/TaskStatus";
import { EmptyState } from "@/components/ui/EmptyState";
import type { Project } from "@/types/project";
import type { Task } from "@/types/task";

/**
 * Section 7: shows what each agent is actually doing right now, for
 * the single most-recently-active project. Derived entirely from
 * real task rows -- an agent only appears "WORKING" because a task
 * assigned to it genuinely has status RUNNING.
 */
export function ActiveWork({ project, tasks }: { project?: Project; tasks?: Task[] }) {
  if (!project) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Current Work</CardTitle>
        </CardHeader>
        <CardContent>
          <EmptyState
            title="No active project"
            description="Create a project and let your AI workforce start working."
          />
        </CardContent>
      </Card>
    );
  }

  const byAgent = new Map<string, Task[]>();
  for (const task of tasks ?? []) {
    const list = byAgent.get(task.assigned_agent) ?? [];
    list.push(task);
    byAgent.set(task.assigned_agent, list);
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>{project.name}</CardTitle>
        <Link to={`/projects/${project.id}`} className="text-xs text-accent hover:underline">
          View project
        </Link>
      </CardHeader>
      <CardContent className="space-y-3">
        {Array.from(byAgent.entries()).map(([agent, agentTasks]) => {
          const active = agentTasks.find((t) => ["RUNNING", "REVIEWING", "REVISION_REQUIRED"].includes(t.status));
          const current = active ?? agentTasks[0];
          return (
            <div key={agent} className="flex items-center justify-between rounded-md border border-border p-3">
              <div>
                <p className="text-sm font-medium capitalize">{agent} Agent</p>
                <p className="text-xs text-muted-foreground">{current.title}</p>
              </div>
              <TaskStatusBadge status={current.status} />
            </div>
          );
        })}
        {byAgent.size === 0 && <p className="text-sm text-muted-foreground">No tasks planned yet.</p>}
      </CardContent>
    </Card>
  );
}
