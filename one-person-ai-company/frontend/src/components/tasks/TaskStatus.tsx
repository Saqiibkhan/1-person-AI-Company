import { Badge } from "@/components/ui/Badge";
import { humanizeStatus } from "@/lib/utils";
import type { TaskStatus as TaskStatusType } from "@/types/task";

const STATUS_VARIANT: Record<TaskStatusType, "default" | "success" | "warning" | "danger" | "accent"> = {
  PENDING: "default",
  PLANNING: "accent",
  WAITING_FOR_DEPENDENCY: "default",
  RUNNING: "accent",
  REVIEWING: "warning",
  REVISION_REQUIRED: "warning",
  APPROVED: "success",
  FAILED: "danger",
  WAITING_FOR_HUMAN: "danger",
  COMPLETED: "success",
  CANCELLED: "default",
};

export function TaskStatusBadge({ status }: { status: TaskStatusType }) {
  return <Badge variant={STATUS_VARIANT[status]}>{humanizeStatus(status)}</Badge>;
}
