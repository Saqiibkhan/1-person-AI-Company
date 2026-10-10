import { useEffect, useRef, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import * as api from "@/services/api";
import { WS_BASE_URL } from "@/services/api";
import type { CompanyEvent } from "@/types/event";

/**
 * Section 23: real-time updates. Loads existing history via REST, then
 * subscribes over WebSocket for anything new. Every event that arrives
 * is a real backend event -- nothing here is simulated.
 */
export function useProjectEvents(projectId: number | undefined) {
  const queryClient = useQueryClient();
  const [liveEvents, setLiveEvents] = useState<CompanyEvent[]>([]);
  const wsRef = useRef<WebSocket | null>(null);

  const historyQuery = useQuery({
    queryKey: ["projects", projectId, "events"],
    queryFn: () => api.getProjectEvents(projectId as number),
    enabled: projectId !== undefined,
  });

  useEffect(() => {
    if (projectId === undefined) return;
    setLiveEvents([]);

    const ws = new WebSocket(`${WS_BASE_URL}/ws/projects/${projectId}`);
    wsRef.current = ws;

    ws.onmessage = (event) => {
      const payload: CompanyEvent = JSON.parse(event.data);
      setLiveEvents((prev) => [...prev, payload]);
      // A new event usually means task/project state changed -- refresh those.
      queryClient.invalidateQueries({ queryKey: ["projects", projectId, "tasks"] });
      queryClient.invalidateQueries({ queryKey: ["projects", projectId] });
    };

    return () => ws.close();
  }, [projectId, queryClient]);

  const allEvents = [...(historyQuery.data ?? []), ...liveEvents];
  return { events: allEvents, isLoading: historyQuery.isLoading };
}
