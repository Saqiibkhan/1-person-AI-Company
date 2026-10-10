import { Routes, Route } from "react-router-dom";
import { AppLayout } from "@/components/layout/AppLayout";
import Dashboard from "@/pages/Dashboard";
import Projects from "@/pages/Projects";
import ProjectDetails from "@/pages/ProjectDetails";
import Tasks from "@/pages/Tasks";
import TaskDetails from "@/pages/TaskDetails";
import Workforce from "@/pages/Workforce";
import AgentDetails from "@/pages/AgentDetails";
import Activity from "@/pages/Activity";
import Deliverables from "@/pages/Deliverables";
import Settings from "@/pages/Settings";

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/projects" element={<Projects />} />
        <Route path="/projects/:projectId" element={<ProjectDetails />} />
        <Route path="/tasks" element={<Tasks />} />
        <Route path="/tasks/:taskId" element={<TaskDetails />} />
        <Route path="/workforce" element={<Workforce />} />
        <Route path="/workforce/:agentName" element={<AgentDetails />} />
        <Route path="/activity" element={<Activity />} />
        <Route path="/deliverables" element={<Deliverables />} />
        <Route path="/settings" element={<Settings />} />
      </Route>
    </Routes>
  );
}
