import { TaskCard } from "./TaskCard";
import { EmptyState } from "@/components/ui/EmptyState";
import { humanizeStatus } from "@/lib/utils";
import type { Task, TaskStatus } from "@/types/task";

const COLUMNS: TaskStatus[] = [
  "PENDING",
  "RUNNING",
  "REVIEWING",
  "REVISION_REQUIRED",
  "APPROVED",
  "WAITING_FOR_HUMAN",
  "COMPLETED",
  "FAILED",
];

export function TaskBoard({ tasks }: { tasks: Task[] }) {
  if (tasks.length === 0) {
    return <EmptyState title="No tasks yet" description="Run the project to let the Manager create a task plan." />;
  }

  return (
    <div className="flex gap-4 overflow-x-auto pb-2">
      {COLUMNS.map((status) => {
        const columnTasks = tasks.filter((t) => t.status === status);
        if (columnTasks.length === 0) return null;
        return (
          <div key={status} className="w-64 shrink-0">
            <div className="mb-2 flex items-center justify-between px-1">
              <h4 className="text-xs font-semibold uppercase text-muted-foreground">{humanizeStatus(status)}</h4>
              <span className="text-xs text-muted-foreground">{columnTasks.length}</span>
            </div>
            <div className="space-y-2">
              {columnTasks.map((task) => (
                <TaskCard key={task.id} task={task} />
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}
