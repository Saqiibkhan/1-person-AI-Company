import { Link } from "react-router-dom";
import { Card, CardContent } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import type { AgentInfo } from "@/types/agent";
import type { Task } from "@/types/task";

export function AgentCard({ agent, tasks }: { agent: AgentInfo; tasks: Task[] }) {
  const agentTasks = tasks.filter((t) => t.assigned_agent === agent.name);
  const current = agentTasks.find((t) => ["RUNNING", "REVIEWING", "REVISION_REQUIRED"].includes(t.status));
  const completed = agentTasks.filter((t) => t.status === "APPROVED" || t.status === "COMPLETED").length;

  return (
    <Link to={`/workforce/${agent.name}`}>
      <Card className="h-full transition-colors hover:border-accent/50">
        <CardContent className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="font-medium capitalize">{agent.name} Agent</h3>
            <Badge variant={current ? "accent" : "default"}>{current ? "Working" : "Idle"}</Badge>
          </div>
          <p className="text-sm text-muted-foreground">{agent.role}</p>
          <div className="flex flex-wrap gap-1.5">
            {agent.capabilities.slice(0, 3).map((c) => (
              <Badge key={c} variant="default">{c}</Badge>
            ))}
          </div>
          <p className="text-xs text-muted-foreground">
            {current ? `Currently: ${current.title}` : `${completed} task(s) completed`}
          </p>
        </CardContent>
      </Card>
    </Link>
  );
}
