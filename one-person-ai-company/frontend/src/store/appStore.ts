import { create } from "zustand";

/**
 * Genuinely global CLIENT state only (Section 31) -- sidebar
 * collapse state and the currently selected project id. Server data
 * (projects, tasks, agents) lives in TanStack Query, never here.
 */
interface AppState {
  sidebarCollapsed: boolean;
  toggleSidebar: () => void;
  selectedProjectId: number | null;
  setSelectedProjectId: (id: number | null) => void;
}

export const useAppStore = create<AppState>((set) => ({
  sidebarCollapsed: false,
  toggleSidebar: () => set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),
  selectedProjectId: null,
  setSelectedProjectId: (id) => set({ selectedProjectId: id }),
}));
