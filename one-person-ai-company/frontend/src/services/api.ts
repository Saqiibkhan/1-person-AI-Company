/**
 * Single typed API layer (frontend spec Section 24).
 * Nothing outside this file makes a fetch() call directly.
 */
import type { Project, ProjectCreateInput } from "@/types/project";
import type { Task, TaskOutput, TaskHistory, TaskFilesResponse } from "@/types/task";
import type { Review } from "@/types/review";
import type { AgentInfo, AgentStats } from "@/types/agent";
import type { CompanyEvent } from "@/types/event";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {
      /* ignore body parse errors */
    }
    throw new ApiError(res.status, detail);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

// --- Projects ---
export const createProject = (input: ProjectCreateInput) =>
  request<Project>("/projects", { method: "POST", body: JSON.stringify(input) });

export const getProjects = () => request<Project[]>("/projects");

export const getProject = (id: number) => request<Project>(`/projects/${id}`);

export const runProject = (id: number) => request<{ message: string }>(`/projects/${id}/run`, { method: "POST" });

export const stopProject = (id: number) => request<Project>(`/projects/${id}/stop`, { method: "POST" });

export const getProjectTasks = (id: number) => request<Task[]>(`/projects/${id}/tasks`);

export const getProjectEvents = (id: number) => request<CompanyEvent[]>(`/projects/${id}/events`);

// --- Tasks ---
export const getTask = (id: number) => request<Task>(`/tasks/${id}`);

export const getTaskOutput = (id: number) => request<TaskOutput>(`/tasks/${id}/output`);

export const getTaskFiles = (id: number) => request<TaskFilesResponse>(`/tasks/${id}/files`);

/** Direct download links -- the backend sets Content-Disposition: attachment, so a plain <a> triggers the browser's native download. */
export const taskDownloadUrl = (id: number) => `${BASE_URL}/tasks/${id}/download`;
export const projectDownloadUrl = (id: number) => `${BASE_URL}/projects/${id}/download`;

export const getTaskReview = (id: number) => request<Review | null>(`/tasks/${id}/review`);

export const getTaskHistory = (id: number) => request<TaskHistory>(`/tasks/${id}/history`);

export const approveTask = (id: number) => request<Task>(`/tasks/${id}/approve`, { method: "POST" });

export const rejectTask = (id: number) => request<Task>(`/tasks/${id}/reject`, { method: "POST" });

export const retryTask = (id: number) => request<{ message: string }>(`/tasks/${id}/retry`, { method: "POST" });

// --- Agents ---
export const getAgents = () => request<AgentInfo[]>("/agents");

export const getAgentStats = (name: string) => request<AgentStats>(`/agents/${name}/stats`);

export const WS_BASE_URL = BASE_URL.replace(/^http/, "ws");
