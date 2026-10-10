import { useState } from "react";
import { useProjects } from "@/hooks/useProjects";
import { useProjectTasks } from "@/hooks/useTasks";
import { TaskBoard } from "@/components/tasks/TaskBoard";
import { EmptyState } from "@/components/ui/EmptyState";
import { cn } from "@/lib/utils";

export default function Tasks() {
  const { data: projects } = useProjects();
  const [selected, setSelected] = useState<number | undefined>(undefined);
  const activeId = selected ?? projects?.[0]?.id;
  const { data: tasks } = useProjectTasks(activeId);

  if (!projects || projects.length === 0) {
    return <EmptyState title="No projects yet" description="Create a project first to see its task board here." />;
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        {projects.map((p) => (
          <button
            key={p.id}
            onClick={() => setSelected(p.id)}
            className={cn(
              "rounded-md border px-3 py-1.5 text-sm",
              (activeId === p.id) ? "border-accent bg-accent/10 text-accent" : "border-border text-muted-foreground hover:bg-muted"
            )}
          >
            {p.name}
          </button>
        ))}
      </div>
      <TaskBoard tasks={tasks ?? []} />
    </div>
  );
}
