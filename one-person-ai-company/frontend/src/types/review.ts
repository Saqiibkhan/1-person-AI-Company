export type ReviewStatus = "approved" | "revision_required" | "failed";

export interface Review {
  id: number;
  task_id: number;
  agent_run_id: number;
  status: ReviewStatus;
  score: number;
  issues: string[];
  required_changes: string[];
  summary: string;
  created_at: string;
}
