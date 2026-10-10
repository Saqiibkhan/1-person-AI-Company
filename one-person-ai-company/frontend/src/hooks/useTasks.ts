import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import * as api from "@/services/api";

export function useProjectTasks(projectId: number | undefined) {
  return useQuery({
    queryKey: ["projects", projectId, "tasks"],
    queryFn: () => api.getProjectTasks(projectId as number),
    enabled: projectId !== undefined,
    refetchInterval: 4000,
  });
}

export function useTask(taskId: number | undefined) {
  return useQuery({
    queryKey: ["tasks", taskId],
    queryFn: () => api.getTask(taskId as number),
    enabled: taskId !== undefined,
    refetchInterval: 4000,
  });
}

export function useTaskOutput(taskId: number | undefined) {
  return useQuery({
    queryKey: ["tasks", taskId, "output"],
    queryFn: () => api.getTaskOutput(taskId as number),
    enabled: taskId !== undefined,
  });
}

export function useTaskFiles(taskId: number | undefined) {
  return useQuery({
    queryKey: ["tasks", taskId, "files"],
    queryFn: () => api.getTaskFiles(taskId as number),
    enabled: taskId !== undefined,
  });
}

export function useTaskReview(taskId: number | undefined) {
  return useQuery({
    queryKey: ["tasks", taskId, "review"],
    queryFn: () => api.getTaskReview(taskId as number),
    enabled: taskId !== undefined,
  });
}

export function useTaskHistory(taskId: number | undefined) {
  return useQuery({
    queryKey: ["tasks", taskId, "history"],
    queryFn: () => api.getTaskHistory(taskId as number),
    enabled: taskId !== undefined,
  });
}

export function useApproveTask(projectId?: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (taskId: number) => api.approveTask(taskId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["projects", projectId, "tasks"] }),
  });
}

export function useRejectTask(projectId?: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (taskId: number) => api.rejectTask(taskId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["projects", projectId, "tasks"] }),
  });
}

export function useRetryTask(projectId?: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (taskId: number) => api.retryTask(taskId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["projects", projectId, "tasks"] }),
  });
}
