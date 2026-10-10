import { useParams } from "react-router-dom";
import { useProject, useRunProject, useStopProject } from "@/hooks/useProjects";
import { useProjectTasks } from "@/hooks/useTasks";
import { useProjectEvents } from "@/hooks/useProjectEvents";
import { ProjectHeader } from "@/components/projects/ProjectHeader";
import { ProjectOverview } from "@/components/projects/ProjectOverview";
import { ProjectWorkflow } from "@/components/projects/ProjectWorkflow";
import { TaskBoard } from "@/components/tasks/TaskBoard";
import { ActivityTimeline } from "@/components/dashboard/ActivityTimeline";
import { ErrorState } from "@/components/ui/ErrorState";
import { Skeleton } from "@/components/ui/Skeleton";

export default function ProjectDetails() {
  const { projectId } = useParams();
  const id = Number(projectId);

  const { data: project, isLoading, isError, refetch } = useProject(id);
  const { data: tasks } = useProjectTasks(id);
  const { events } = useProjectEvents(id);
  const runProject = useRunProject();
  const stopProject = useStopProject();

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-16" />
        <Skeleton className="h-40" />
      </div>
    );
  }

  if (isError || !project) {
    return <ErrorState title="Unable to load project" message="The backend could not be reached." onRetry={() => refetch()} />;
  }

  return (
    <div className="space-y-6">
      <ProjectHeader
        project={project}
        onRun={() => runProject.mutate(project.id)}
        onStop={() => stopProject.mutate(project.id)}
        isRunning={runProject.isPending}
      />
      <ProjectOverview tasks={tasks ?? []} />
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-6">
          <TaskBoard tasks={tasks ?? []} />
        </div>
        <div className="space-y-6">
          <ProjectWorkflow tasks={tasks ?? []} />
          <ActivityTimeline events={events} isLoading={false} />
        </div>
      </div>
    </div>
  );
}
