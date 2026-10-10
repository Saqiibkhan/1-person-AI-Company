export type ProjectStatus =
  | "CREATED"
  | "PLANNING"
  | "RUNNING"
  | "WAITING_FOR_HUMAN"
  | "COMPLETED"
  | "FAILED"
  | "CANCELLED";

export interface Project {
  id: number;
  name: string;
  description: string | null;
  goal: string;
  status: ProjectStatus;
  created_at: string;
  updated_at: string;
}

export interface ProjectCreateInput {
  name: string;
  description?: string;
  goal: string;
}
