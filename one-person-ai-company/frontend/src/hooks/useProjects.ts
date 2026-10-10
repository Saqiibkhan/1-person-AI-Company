import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import * as api from "@/services/api";
import type { ProjectCreateInput } from "@/types/project";

export function useProjects() {
  return useQuery({ queryKey: ["projects"], queryFn: api.getProjects });
}

export function useProject(id: number | undefined) {
  return useQuery({
    queryKey: ["projects", id],
    queryFn: () => api.getProject(id as number),
    enabled: id !== undefined,
    refetchInterval: (query) =>
      query.state.data?.status === "RUNNING" || query.state.data?.status === "PLANNING" ? 3000 : false,
  });
}

export function useCreateProject() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (input: ProjectCreateInput) => api.createProject(input),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["projects"] }),
  });
}

export function useRunProject() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => api.runProject(id),
    onSuccess: (_, id) => {
      qc.invalidateQueries({ queryKey: ["projects", id] });
      qc.invalidateQueries({ queryKey: ["projects", id, "tasks"] });
    },
  });
}

export function useStopProject() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => api.stopProject(id),
    onSuccess: (_, id) => qc.invalidateQueries({ queryKey: ["projects", id] }),
  });
}
