import { Play, Square } from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { humanizeStatus } from "@/lib/utils";
import type { Project } from "@/types/project";

export function ProjectHeader({
  project,
  onRun,
  onStop,
  isRunning,
}: {
  project: Project;
  onRun: () => void;
  onStop: () => void;
  isRunning: boolean;
}) {
  const canRun = ["CREATED", "WAITING_FOR_HUMAN", "FAILED"].includes(project.status);
  const canStop = project.status === "RUNNING" || project.status === "PLANNING";

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-lg font-semibold">{project.name}</h2>
            <Badge variant="accent">{humanizeStatus(project.status)}</Badge>
          </div>
          <p className="mt-1 max-w-2xl text-sm text-muted-foreground">{project.goal}</p>
        </div>
        <div className="flex gap-2">
          {canRun && (
            <Button size="sm" onClick={onRun} loading={isRunning}>
              <Play className="h-3.5 w-3.5" /> Run
            </Button>
          )}
          {canStop && (
            <Button size="sm" variant="outline" onClick={onStop}>
              <Square className="h-3.5 w-3.5" /> Stop
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
