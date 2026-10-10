import { useParams } from "react-router-dom";
import { CheckCircle2, XCircle, RotateCcw } from "lucide-react";
import { useTask, useTaskReview, useTaskHistory, useTaskFiles, useApproveTask, useRejectTask, useRetryTask } from "@/hooks/useTasks";
import { TaskFilesViewer } from "@/components/tasks/TaskFilesViewer";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { TaskStatusBadge } from "@/components/tasks/TaskStatus";
import { ReviewPanel } from "@/components/reviews/ReviewPanel";
import { RevisionHistory } from "@/components/reviews/RevisionHistory";
import { ErrorState } from "@/components/ui/ErrorState";
import { Skeleton } from "@/components/ui/Skeleton";
import { formatTime } from "@/lib/utils";

export default function TaskDetails() {
  const { taskId } = useParams();
  const id = Number(taskId);

  const { data: task, isLoading, isError, refetch } = useTask(id);
  const { data: review } = useTaskReview(id);
  const { data: history } = useTaskHistory(id);
  const { data: filesData } = useTaskFiles(id);
  const approve = useApproveTask(task?.project_id);
  const reject = useRejectTask(task?.project_id);
  const retry = useRetryTask(task?.project_id);

  if (isLoading) return <Skeleton className="h-64" />;
  if (isError || !task) return <ErrorState title="Unable to load task" onRetry={() => refetch()} />;

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold">{task.title}</h2>
          <p className="mt-1 text-sm capitalize text-muted-foreground">{task.assigned_agent} Agent</p>
        </div>
        <TaskStatusBadge status={task.status} />
      </div>

      {task.status === "WAITING_FOR_HUMAN" && (
        <Card className="border-danger/40 bg-danger/5">
          <CardHeader>
            <CardTitle>Human Approval Required</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <p className="text-sm text-muted-foreground">
              This task failed QA review after the maximum number of automatic revisions. Review the output
              below and decide how to proceed.
            </p>
            <div className="flex gap-2">
              <Button size="sm" onClick={() => approve.mutate(task.id)} loading={approve.isPending}>
                <CheckCircle2 className="h-3.5 w-3.5" /> Approve
              </Button>
              <Button size="sm" variant="outline" onClick={() => retry.mutate(task.id)} loading={retry.isPending}>
                <RotateCcw className="h-3.5 w-3.5" /> Retry
              </Button>
              <Button size="sm" variant="danger" onClick={() => reject.mutate(task.id)} loading={reject.isPending}>
                <XCircle className="h-3.5 w-3.5" /> Reject
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Task Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <p className="text-muted-foreground">{task.description}</p>
              {task.requirements.length > 0 && (
                <div>
                  <p className="mb-1 text-xs font-semibold uppercase text-muted-foreground">Requirements</p>
                  <ul className="list-inside list-disc space-y-1">
                    {task.requirements.map((r, i) => (
                      <li key={i}>{r}</li>
                    ))}
                  </ul>
                </div>
              )}
              <div className="grid grid-cols-2 gap-2 pt-2 text-xs text-muted-foreground">
                <span>Created: {formatTime(task.created_at)}</span>
                {task.started_at && <span>Started: {formatTime(task.started_at)}</span>}
                {task.completed_at && <span>Completed: {formatTime(task.completed_at)}</span>}
                <span>Revisions: {task.revision_count}</span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Deliverable</CardTitle>
            </CardHeader>
            <CardContent>
              {task.status === "PENDING" || task.status === "WAITING_FOR_DEPENDENCY" ? (
                <p className="text-sm text-muted-foreground">No output yet -- this task hasn't run.</p>
              ) : filesData ? (
                <TaskFilesViewer taskId={task.id} files={filesData.files} />
              ) : (
                <p className="text-sm text-muted-foreground">Waiting for output...</p>
              )}
            </CardContent>
          </Card>

          <RevisionHistory history={history} />
        </div>

        <div className="space-y-6">
          <ReviewPanel review={review} />
        </div>
      </div>
    </div>
  );
}
