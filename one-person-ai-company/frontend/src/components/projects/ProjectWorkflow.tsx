import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import { cn } from "@/lib/utils";
import type { Task } from "@/types/task";

/**
 * Section 11: a visual representation of the company's workflow,
 * reflecting real task statuses -- not a static decoration.
 */
export function ProjectWorkflow({ tasks }: { tasks: Task[] }) {
  const stageStatus = (agentName: string) => {
    const agentTasks = tasks.filter((t) => t.assigned_agent === agentName);
    if (agentTasks.length === 0) return "idle";
    if (agentTasks.some((t) => ["RUNNING", "REVIEWING", "REVISION_REQUIRED"].includes(t.status))) return "active";
    if (agentTasks.every((t) => t.status === "APPROVED" || t.status === "COMPLETED")) return "done";
    if (agentTasks.some((t) => t.status === "FAILED" || t.status === "WAITING_FOR_HUMAN")) return "blocked";
    return "pending";
  };

  const stageClass = (stage: string) =>
    cn(
      "rounded-md border px-4 py-2 text-sm font-medium",
      stage === "active" && "border-accent text-accent bg-accent/10",
      stage === "done" && "border-success text-success bg-success/10",
      stage === "blocked" && "border-danger text-danger bg-danger/10",
      (stage === "idle" || stage === "pending") && "border-border text-muted-foreground"
    );

  const workers = ["researcher", "marketing", "builder"].filter((a) => tasks.some((t) => t.assigned_agent === a));

  return (
    <Card>
      <CardHeader>
        <CardTitle>Workflow</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col items-center gap-3">
        <div className={stageClass("done")}>Human Owner</div>
        <div className="h-4 w-px bg-border" />
        <div className={stageClass(tasks.length > 0 ? "done" : "pending")}>Manager Agent</div>
        <div className="h-4 w-px bg-border" />
        <div className="flex flex-wrap justify-center gap-3">
          {workers.length === 0 && <div className={stageClass("pending")}>(no worker tasks yet)</div>}
          {workers.map((worker) => (
            <div key={worker} className={cn(stageClass(stageStatus(worker)), "capitalize")}>
              {worker}
            </div>
          ))}
        </div>
        <div className="h-4 w-px bg-border" />
        <div className={stageClass(tasks.some((t) => t.status === "REVIEWING") ? "active" : "pending")}>
          QA / Auditor
        </div>
      </CardContent>
    </Card>
  );
}
