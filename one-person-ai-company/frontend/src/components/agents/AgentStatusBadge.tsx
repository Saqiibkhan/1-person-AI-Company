import { Badge } from "@/components/ui/Badge";
import { humanizeStatus } from "@/lib/utils";
import type { AgentStatus } from "@/types/agent";

const STATUS_VARIANT: Record<AgentStatus, "default" | "success" | "warning" | "danger" | "accent"> = {
  IDLE: "default",
  WORKING: "accent",
  REVIEWING: "warning",
  REVISING: "warning",
  WAITING: "warning",
  COMPLETED: "success",
  FAILED: "danger",
};

export function AgentStatusBadge({ status }: { status: AgentStatus }) {
  return <Badge variant={STATUS_VARIANT[status]}>{humanizeStatus(status)}</Badge>;
}
