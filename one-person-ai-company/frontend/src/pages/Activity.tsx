import { useState } from "react";
import { useProjects } from "@/hooks/useProjects";
import { useProjectEvents } from "@/hooks/useProjectEvents";
import { Card, CardContent } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { formatTime, formatDate } from "@/lib/utils";
import { cn } from "@/lib/utils";

export default function Activity() {
  const { data: projects } = useProjects();
  const [selected, setSelected] = useState<number | undefined>(undefined);
  const activeId = selected ?? projects?.[0]?.id;
  const { events, isLoading } = useProjectEvents(activeId);

  if (!projects || projects.length === 0) {
    return <EmptyState title="No activity yet" description="Activity will appear here once a project starts running." />;
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
              activeId === p.id ? "border-accent bg-accent/10 text-accent" : "border-border text-muted-foreground hover:bg-muted"
            )}
          >
            {p.name}
          </button>
        ))}
      </div>

      <Card>
        <CardContent>
          {isLoading ? (
            <p className="text-sm text-muted-foreground">Loading...</p>
          ) : events.length === 0 ? (
            <EmptyState title="No activity yet" description="Events will appear here as this project runs." />
          ) : (
            <ol className="space-y-3">
              {events.map((event) => (
                <li key={event.id} className="flex gap-4 border-b border-border pb-3 text-sm last:border-0 last:pb-0">
                  <span className="w-32 shrink-0 text-xs text-muted-foreground">
                    {formatDate(event.created_at)} {formatTime(event.created_at)}
                  </span>
                  <span>{event.message}</span>
                </li>
              ))}
            </ol>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
