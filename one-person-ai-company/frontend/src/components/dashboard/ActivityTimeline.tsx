import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { formatTime } from "@/lib/utils";
import type { CompanyEvent } from "@/types/event";

export function ActivityTimeline({ events, isLoading }: { events: CompanyEvent[]; isLoading: boolean }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Company Activity</CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <p className="text-sm text-muted-foreground">Loading activity...</p>
        ) : events.length === 0 ? (
          <EmptyState title="No activity yet" description="Events will appear here as your AI workforce gets to work." />
        ) : (
          <ol className="space-y-3">
            {events
              .slice()
              .reverse()
              .slice(0, 12)
              .map((event) => (
                <li key={event.id} className="flex gap-3 text-sm">
                  <span className="w-12 shrink-0 text-xs text-muted-foreground">{formatTime(event.created_at)}</span>
                  <span>{event.message}</span>
                </li>
              ))}
          </ol>
        )}
      </CardContent>
    </Card>
  );
}
