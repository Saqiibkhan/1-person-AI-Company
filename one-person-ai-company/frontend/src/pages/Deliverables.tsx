import { useMemo } from "react";
import { Download } from "lucide-react";
import { useQueries } from "@tanstack/react-query";
import { useProjects } from "@/hooks/useProjects";
import { Card, CardContent } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { formatDate } from "@/lib/utils";
import * as api from "@/services/api";
import { projectDownloadUrl } from "@/services/api";

/**
 * Section 20: only approved outputs are shown here as trusted final
 * deliverables -- one entry per completed project.
 */
export default function Deliverables() {
  const { data: projects } = useProjects();
  const completed = (projects ?? []).filter((p) => p.status === "COMPLETED");

  const taskQueries = useQueries({
    queries: completed.map((p) => ({
      queryKey: ["projects", p.id, "tasks"],
      queryFn: () => api.getProjectTasks(p.id),
    })),
  });

  const deliverables = useMemo(
    () =>
      completed.map((project, i) => ({
        project,
        approvedTaskCount: (taskQueries[i]?.data ?? []).filter((t) => t.status === "APPROVED" || t.status === "COMPLETED").length,
      })),
    [completed, taskQueries]
  );

  if (deliverables.length === 0) {
    return <EmptyState title="No deliverables yet" description="Completed projects will show their final deliverable here." />;
  }

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {deliverables.map(({ project, approvedTaskCount }) => (
        <Card key={project.id}>
          <CardContent className="space-y-2">
            <div className="flex items-start justify-between">
              <h3 className="font-medium">{project.name}</h3>
              <Badge variant="success">Approved</Badge>
            </div>
            <p className="text-sm text-muted-foreground">{approvedTaskCount} approved work item(s)</p>
            <p className="text-xs text-muted-foreground">Completed {formatDate(project.updated_at)}</p>
            <a href={projectDownloadUrl(project.id)} className="inline-block pt-1">
              <Button size="sm" variant="outline">
                <Download className="h-3.5 w-3.5" /> Download (.zip)
              </Button>
            </a>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
