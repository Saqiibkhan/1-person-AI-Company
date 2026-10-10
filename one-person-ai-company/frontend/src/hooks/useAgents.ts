import { useQuery } from "@tanstack/react-query";
import * as api from "@/services/api";

export function useAgents() {
  return useQuery({ queryKey: ["agents"], queryFn: api.getAgents });
}

export function useAgentStats(name: string | undefined) {
  return useQuery({
    queryKey: ["agents", name, "stats"],
    queryFn: () => api.getAgentStats(name as string),
    enabled: name !== undefined,
  });
}
