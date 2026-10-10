import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Plus, FolderKanban } from "lucide-react";
import { useProjects, useCreateProject, useRunProject } from "@/hooks/useProjects";
import { ProjectCard } from "@/components/projects/ProjectCard";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Textarea } from "@/components/ui/Textarea";
import { Card, CardContent } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { Skeleton } from "@/components/ui/Skeleton";

export default function Projects() {
  const { data: projects, isLoading, isError, refetch } = useProjects();
  const createProject = useCreateProject();
  const runProject = useRunProject();
  const navigate = useNavigate();

  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState("");
  const [goal, setGoal] = useState("");
  const [description, setDescription] = useState("");

  const resetForm = () => {
    setName("");
    setGoal("");
    setDescription("");
    setShowForm(false);
  };

  const handleCreate = async (andRun: boolean) => {
    const project = await createProject.mutateAsync({ name, goal, description: description || undefined });
    resetForm();
    if (andRun) {
      await runProject.mutateAsync(project.id);
    }
    navigate(`/projects/${project.id}`);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">Give your AI workforce a high-level objective.</p>
        <Button onClick={() => setShowForm((v) => !v)}>
          <Plus className="h-4 w-4" /> Create Project
        </Button>
      </div>

      {showForm && (
        <Card>
          <CardContent className="space-y-4">
            <div>
              <label className="mb-1 block text-xs font-medium text-muted-foreground">Project Name</label>
              <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="Launch an AI-powered restaurant platform" />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-muted-foreground">Objective</label>
              <Textarea
                rows={4}
                value={goal}
                onChange={(e) => setGoal(e.target.value)}
                placeholder="Research the market, define the product strategy, create the technical plan, and prepare a launch strategy."
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-muted-foreground">Optional Requirements</label>
              <Textarea rows={2} value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Any extra constraints or context..." />
            </div>
            <div className="flex gap-2">
              <Button disabled={!name || !goal} loading={createProject.isPending && !runProject.isPending} onClick={() => handleCreate(false)}>
                Create Project
              </Button>
              <Button
                variant="outline"
                disabled={!name || !goal}
                loading={createProject.isPending && runProject.isPending}
                onClick={() => handleCreate(true)}
              >
                Create &amp; Run
              </Button>
              <Button variant="ghost" onClick={resetForm}>
                Cancel
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {isLoading && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[...Array(3)].map((_, i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
      )}

      {isError && <ErrorState title="Unable to load projects" message="The backend could not be reached." onRetry={() => refetch()} />}

      {!isLoading && !isError && projects?.length === 0 && (
        <EmptyState
          icon={<FolderKanban className="h-8 w-8" />}
          title="No projects yet"
          description="Create your first project and let your AI workforce start working."
          action={
            <Button onClick={() => setShowForm(true)}>
              <Plus className="h-4 w-4" /> Create Project
            </Button>
          }
        />
      )}

      {projects && projects.length > 0 && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {projects.map((p) => (
            <ProjectCard key={p.id} project={p} />
          ))}
        </div>
      )}
    </div>
  );
}
