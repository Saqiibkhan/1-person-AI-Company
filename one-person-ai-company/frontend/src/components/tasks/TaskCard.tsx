import { Link } from "react-router-dom";
import { Card, CardContent } from "@/components/ui/Card";
import { TaskStatusBadge } from "./TaskStatus";
import type { Task } from "@/types/task";

export function TaskCard({ task }: { task: Task }) {
  return (
    <Link to={`/tasks/${task.id}`}>
      <Card className="transition-colors hover:border-accent/50">
        <CardContent className="space-y-2 p-3">
          <div className="flex items-start justify-between gap-2">
            <p className="text-sm font-medium">{task.title}</p>
          </div>
          <p className="text-xs capitalize text-muted-foreground">{task.assigned_agent} Agent</p>
          <div className="flex items-center justify-between">
            <TaskStatusBadge status={task.status} />
            {task.revision_count > 0 && (
              <span className="text-xs text-muted-foreground">Rev {task.revision_count}</span>
            )}
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
