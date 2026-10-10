import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";

export default function Settings() {
  const apiBase = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

  return (
    <div className="max-w-xl space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Connection</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-muted-foreground">Backend URL</span>
            <span>{apiBase}</span>
          </div>
          <p className="text-xs text-muted-foreground">
            Set via VITE_API_BASE_URL in the frontend's .env file.
          </p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>About</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground">
          ONEPERSON AI -- your AI company, one human in control. A Manager
          agent coordinates specialized AI workers, and an independent QA/Auditor
          agent reviews their work before it reaches you.
        </CardContent>
      </Card>
    </div>
  );
}
