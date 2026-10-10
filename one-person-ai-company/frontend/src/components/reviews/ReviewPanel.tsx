import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { ReviewScore } from "./ReviewScore";
import { EmptyState } from "@/components/ui/EmptyState";
import type { Review } from "@/types/review";

/**
 * Section 15: the QA/Auditor review panel. Never treats the score as
 * the only decision mechanism -- status, issues, and required changes
 * are all shown with equal weight.
 */
const STATUS_META: Record<Review["status"], { label: string; variant: "success" | "warning" | "danger" }> = {
  approved: { label: "Approved", variant: "success" },
  revision_required: { label: "Revision Required", variant: "warning" },
  failed: { label: "Failed", variant: "danger" },
};

export function ReviewPanel({ review }: { review: Review | null | undefined }) {
  if (!review) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>QA Review</CardTitle>
        </CardHeader>
        <CardContent>
          <EmptyState title="No review yet" description="This task hasn't been reviewed by QA/Auditor yet." />
        </CardContent>
      </Card>
    );
  }

  const meta = STATUS_META[review.status];

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>QA Review</CardTitle>
        <Badge variant={meta.variant}>{meta.label}</Badge>
      </CardHeader>
      <CardContent className="space-y-4">
        <ReviewScore score={review.score} />

        {review.issues.length > 0 && (
          <div>
            <p className="mb-1 text-xs font-semibold uppercase text-muted-foreground">Issues</p>
            <ul className="list-inside list-disc space-y-1 text-sm">
              {review.issues.map((issue, i) => (
                <li key={i}>{issue}</li>
              ))}
            </ul>
          </div>
        )}

        {review.required_changes.length > 0 && (
          <div>
            <p className="mb-1 text-xs font-semibold uppercase text-muted-foreground">Required Changes</p>
            <ul className="list-inside list-disc space-y-1 text-sm">
              {review.required_changes.map((change, i) => (
                <li key={i}>{change}</li>
              ))}
            </ul>
          </div>
        )}

        <div>
          <p className="mb-1 text-xs font-semibold uppercase text-muted-foreground">Summary</p>
          <p className="text-sm text-muted-foreground">{review.summary}</p>
        </div>
      </CardContent>
    </Card>
  );
}
