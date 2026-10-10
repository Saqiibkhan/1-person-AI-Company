import { Link } from "react-router-dom";
import { Card, CardContent } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { humanizeStatus, formatDate } from "@/lib/utils";
import type { Project } from "@/types/project";

const STATUS_VARIANT: Record<Project["status"], "default" | "success" | "warning" | "danger" | "accent"> = {
  CREATED: "default",
  PLANNING: "accent",
  RUNNING: "accent",
  WAITING_FOR_HUMAN: "warning",
  COMPLETED: "success",
  FAILED: "danger",
  CANCELLED: "default",
};

export function ProjectCard({ project }: { project: Project }) {
  return (
    <Link to={`/projects/${project.id}`}>
      <Card className="h-full transition-colors hover:border-accent/50">
        <CardContent className="space-y-3">
          <div className="flex items-start justify-between gap-2">
            <h3 className="font-medium">{project.name}</h3>
            <Badge variant={STATUS_VARIANT[project.status]}>{humanizeStatus(project.status)}</Badge>
          </div>
          <p className="line-clamp-2 text-sm text-muted-foreground">{project.goal}</p>
          <p className="text-xs text-muted-foreground">Created {formatDate(project.created_at)}</p>
        </CardContent>
      </Card>
    </Link>
  );
}
