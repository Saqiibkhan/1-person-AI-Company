import { FolderKanban, ListTodo, ClipboardCheck, Package } from "lucide-react";
import { Card, CardContent } from "@/components/ui/Card";
import { Skeleton } from "@/components/ui/Skeleton";
import type { Project } from "@/types/project";
import type { Task } from "@/types/task";

interface Props {
  projects?: Project[];
  allTasks?: Task[];
  isLoading: boolean;
}

export function OverviewCards({ projects, allTasks, isLoading }: Props) {
  const activeProjects = projects?.filter((p) => p.status === "RUNNING" || p.status === "PLANNING").length ?? 0;
  const tasksInProgress = allTasks?.filter((t) => t.status === "RUNNING").length ?? 0;
  const tasksAwaitingReview = allTasks?.filter((t) => t.status === "REVIEWING" || t.status === "WAITING_FOR_HUMAN").length ?? 0;
  const completedDeliverables = projects?.filter((p) => p.status === "COMPLETED").length ?? 0;

  const cards = [
    { label: "Active Projects", value: activeProjects, icon: FolderKanban },
    { label: "Tasks In Progress", value: tasksInProgress, icon: ListTodo },
    { label: "Awaiting Review", value: tasksAwaitingReview, icon: ClipboardCheck },
    { label: "Completed Deliverables", value: completedDeliverables, icon: Package },
  ];

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {cards.map(({ label, value, icon: Icon }) => (
        <Card key={label}>
          <CardContent className="flex items-center justify-between">
            <div>
              <p className="text-xs text-muted-foreground">{label}</p>
              {isLoading ? (
                <Skeleton className="mt-2 h-7 w-10" />
              ) : (
                <p className="mt-1 text-2xl font-semibold">{value}</p>
              )}
            </div>
            <div className="flex h-9 w-9 items-center justify-center rounded-md bg-muted">
              <Icon className="h-4 w-4 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
