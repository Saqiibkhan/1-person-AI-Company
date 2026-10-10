import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { EmptyState } from "@/components/ui/EmptyState";
import { formatTime } from "@/lib/utils";
import type { TaskHistory } from "@/types/task";

/**
 * Section 16/26: shows every version of a task's output alongside
 * its review result, so the human can see exactly how the
 * deliverable improved across the revision loop.
 */
export function RevisionHistory({ history }: { history: TaskHistory | undefined }) {
  if (!history || history.runs.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Revision History</CardTitle>
        </CardHeader>
        <CardContent>
          <EmptyState title="No versions yet" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Revision History</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {history.runs.map((run, i) => {
          const review = history.reviews[i];
          return (
            <div key={run.id} className="rounded-md border border-border p-3">
              <div className="mb-2 flex items-center justify-between">
                <span className="text-sm font-medium">Version {i + 1}</span>
                <span className="text-xs text-muted-foreground">{formatTime(run.started_at)}</span>
              </div>
              {review && (
                <Badge variant={review.status === "approved" ? "success" : "warning"}>
                  {review.status === "approved" ? "Approved" : "Revision Required"} &middot; {review.score}/100
                </Badge>
              )}
              {run.error && <p className="mt-2 text-sm text-danger">Error: {run.error}</p>}
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
}
