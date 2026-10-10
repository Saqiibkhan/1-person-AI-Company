import { useState } from "react";
import { FileText, Folder, Download } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { cn } from "@/lib/utils";
import { taskDownloadUrl } from "@/services/api";
import type { TaskFile } from "@/types/task";

/**
 * Shows the agent's deliverable as real files (and folders, when the
 * agent produced a path like "src/main.py"), not one undifferentiated
 * text blob -- with a "Download all" button that gets a real .zip from
 * the backend, plus a per-file download for anyone who just wants one
 * file out of a multi-file deliverable.
 */
export function TaskFilesViewer({ taskId, files }: { taskId: number; files: TaskFile[] }) {
  const [selectedPath, setSelectedPath] = useState<string | null>(files[0]?.path ?? null);

  if (files.length === 0) {
    return <EmptyState title="No output yet" description="This task hasn't produced a deliverable yet." />;
  }

  const selected = files.find((f) => f.path === selectedPath) ?? files[0];
  const isSingleFile = files.length === 1;

  const downloadSingleFile = (file: TaskFile) => {
    const blob = new Blob([file.content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = file.path.split("/").pop() || "file.txt";
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <p className="text-xs text-muted-foreground">
          {files.length} file{files.length > 1 ? "s" : ""}
        </p>
        {!isSingleFile && (
          <a href={taskDownloadUrl(taskId)}>
            <Button size="sm" variant="outline">
              <Download className="h-3.5 w-3.5" /> Download all (.zip)
            </Button>
          </a>
        )}
      </div>

      <div className={cn("grid gap-3", !isSingleFile && "sm:grid-cols-[200px_1fr]")}>
        {!isSingleFile && (
          <div className="space-y-0.5 rounded-md border border-border p-1">
            {files.map((file) => (
              <button
                key={file.path}
                onClick={() => setSelectedPath(file.path)}
                className={cn(
                  "flex w-full items-center gap-1.5 rounded px-2 py-1.5 text-left text-xs",
                  file.path === selected.path ? "bg-accent/15 text-accent" : "hover:bg-muted"
                )}
              >
                {file.path.includes("/") ? (
                  <Folder className="h-3.5 w-3.5 shrink-0" />
                ) : (
                  <FileText className="h-3.5 w-3.5 shrink-0" />
                )}
                <span className="truncate">{file.path}</span>
              </button>
            ))}
          </div>
        )}

        <div className="min-w-0 space-y-2">
          {isSingleFile ? (
            <div className="flex items-center justify-end">
              <Button size="sm" variant="outline" onClick={() => downloadSingleFile(selected)}>
                <Download className="h-3.5 w-3.5" /> Download
              </Button>
            </div>
          ) : (
            <div className="flex items-center justify-between">
              <p className="truncate text-xs font-medium text-muted-foreground">{selected.path}</p>
              <Button size="sm" variant="ghost" onClick={() => downloadSingleFile(selected)}>
                <Download className="h-3.5 w-3.5" />
              </Button>
            </div>
          )}
          <pre className="max-h-96 overflow-auto whitespace-pre-wrap rounded-md bg-muted p-3 text-sm">
            {selected.content || "(empty file)"}
          </pre>
        </div>
      </div>
    </div>
  );
}
