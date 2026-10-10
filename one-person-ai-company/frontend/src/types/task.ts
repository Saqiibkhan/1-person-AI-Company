export type TaskStatus =
  | "PENDING"
  | "PLANNING"
  | "WAITING_FOR_DEPENDENCY"
  | "RUNNING"
  | "REVIEWING"
  | "REVISION_REQUIRED"
  | "APPROVED"
  | "FAILED"
  | "WAITING_FOR_HUMAN"
  | "COMPLETED"
  | "CANCELLED";

export type AgentName = "manager" | "researcher" | "marketing" | "builder" | "auditor";

export interface Task {
  id: number;
  project_id: number;
  title: string;
  description: string;
  requirements: string[];
  assigned_agent: AgentName;
  status: TaskStatus;
  priority: string;
  depends_on: number[];
  revision_count: number;
  created_at: string;
  updated_at: string;
  started_at: string | null;
  completed_at: string | null;
}

export interface TaskOutput {
  task_id: number;
  output: string | null;
  revision_count: number;
}

export interface TaskFile {
  path: string;
  content: string;
}

export interface TaskFilesResponse {
  task_id: number;
  files: TaskFile[];
}

export interface AgentRunRecord {
  id: number;
  agent_name: string;
  status: string;
  output: string | null;
  error: string | null;
  started_at: string;
  completed_at: string | null;
}

export interface TaskHistory {
  task_id: number;
  runs: AgentRunRecord[];
  reviews: ReviewRecord[];
}

export interface ReviewRecord {
  id: number;
  status: string;
  score: number;
  issues: string[];
  required_changes: string[];
  summary: string;
  created_at: string;
}
