export interface CompanyEvent {
  id: number;
  project_id: number;
  task_id: number | null;
  event_type: string;
  message: string;
  metadata?: Record<string, unknown>;
  created_at: string;
}
