import { cn } from "@/lib/utils";

export function ReviewScore({ score }: { score: number }) {
  const color = score >= 75 ? "text-success" : score >= 50 ? "text-warning" : "text-danger";
  return (
    <div className="flex items-baseline gap-1">
      <span className={cn("text-2xl font-semibold", color)}>{score}</span>
      <span className="text-xs text-muted-foreground">/100</span>
    </div>
  );
}
