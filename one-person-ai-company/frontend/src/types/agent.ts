export type AgentStatus = "IDLE" | "WORKING" | "REVIEWING" | "REVISING" | "WAITING" | "COMPLETED" | "FAILED";

export interface AgentInfo {
  name: string;
  role: string;
  description: string;
  capabilities: string[];
}

export interface AgentStats {
  name: string;
  total_runs: number;
  approved_count: number;
  revision_count: number;
  failed_count: number;
}
