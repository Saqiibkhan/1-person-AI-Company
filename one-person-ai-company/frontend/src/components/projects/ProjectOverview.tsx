import { Card, CardContent } from "@/components/ui/Card";
import { Progress } from "@/components/ui/Progress";
import type { Task } from "@/types/task";

export function ProjectOverview({ tasks }: { tasks: Task[] }) {
  const total = tasks.length;
  const done = tasks.filter((t) => t.status === "APPROVED" || t.status === "COMPLETED").length;
  const progress = total === 0 ? 0 : Math.round((done / total) * 100);

  const activeAgents = new Set(
    tasks.filter((t) => ["RUNNING", "REVIEWING", "REVISION_REQUIRED"].includes(t.status)).map((t) => t.assigned_agent)
  );

  const currentPhase =
    tasks.find((t) => t.status === "RUNNING")?.title ??
    tasks.find((t) => t.status === "REVIEWING")?.title ??
    (progress === 100 && total > 0 ? "Finalizing" : "Planning");

  return (
    <Card>
      <CardContent className="space-y-4">
        <div>
          <div className="mb-1 flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Progress</span>
            <span className="font-medium">{done}/{total} tasks approved</span>
          </div>
          <Progress value={progress} />
        </div>
        <div className="grid grid-cols-2 gap-4 text-sm sm:grid-cols-3">
          <div>
            <p className="text-muted-foreground">Current Phase</p>
            <p className="font-medium">{currentPhase}</p>
          </div>
          <div>
            <p className="text-muted-foreground">Active Agents</p>
            <p className="font-medium">{activeAgents.size > 0 ? Array.from(activeAgents).join(", ") : "None"}</p>
          </div>
          <div>
            <p className="text-muted-foreground">Total Tasks</p>
            <p className="font-medium">{total}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
