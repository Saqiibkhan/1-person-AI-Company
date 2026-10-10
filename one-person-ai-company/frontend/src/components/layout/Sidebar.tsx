import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  FolderKanban,
  ListTodo,
  Users,
  Activity,
  Package,
  Settings,
  ChevronsLeft,
  ChevronsRight,
  Circle,
} from "lucide-react";
import { useAppStore } from "@/store/appStore";
import { cn } from "@/lib/utils";

const NAV_GROUPS = [
  {
    label: "COMMAND CENTER",
    items: [
      { to: "/", label: "Dashboard", icon: LayoutDashboard, end: true },
      { to: "/projects", label: "Projects", icon: FolderKanban },
      { to: "/tasks", label: "Tasks", icon: ListTodo },
      { to: "/workforce", label: "Workforce", icon: Users },
      { to: "/activity", label: "Activity", icon: Activity },
      { to: "/deliverables", label: "Deliverables", icon: Package },
    ],
  },
  {
    label: "COMPANY",
    items: [{ to: "/settings", label: "Settings", icon: Settings }],
  },
];

/**
 * Minimal geometric mark: one solid "owner" node connected to several
 * smaller "employee" nodes. No robot heads, brains, or circuitry --
 * just an abstract company/org-chart shape, per the brand spec.
 */
function Logomark({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 28 28" fill="none" className={className}>
      <circle cx="14" cy="7" r="4" fill="currentColor" />
      <circle cx="5" cy="22" r="3" fill="currentColor" opacity="0.55" />
      <circle cx="14" cy="24" r="3" fill="currentColor" opacity="0.55" />
      <circle cx="23" cy="22" r="3" fill="currentColor" opacity="0.55" />
      <path
        d="M14 11L5 19M14 11L14 21M14 11L23 19"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        opacity="0.55"
      />
    </svg>
  );
}

export function Sidebar() {
  const collapsed = useAppStore((s) => s.sidebarCollapsed);
  const toggle = useAppStore((s) => s.toggleSidebar);

  return (
    <aside
      className={cn(
        "flex h-screen flex-col border-r border-border bg-muted transition-all",
        collapsed ? "w-16" : "w-60"
      )}
    >
      <div className="flex h-16 items-center gap-2.5 border-b border-border px-4">
        <Logomark className="h-6 w-6 shrink-0 text-accent" />
        {!collapsed && (
          <div className="leading-tight">
            <p className="text-sm font-semibold tracking-tight">ONEPERSON AI</p>
            <p className="text-[10px] text-subtle-foreground">One human. AI workforce.</p>
          </div>
        )}
      </div>

      <nav className="flex-1 space-y-4 overflow-y-auto p-3">
        {NAV_GROUPS.map((group) => (
          <div key={group.label}>
            {!collapsed && (
              <p className="mb-1.5 px-3 text-[10px] font-semibold tracking-wider text-subtle-foreground">
                {group.label}
              </p>
            )}
            <div className="space-y-0.5">
              {group.items.map(({ to, label, icon: Icon, end }) => (
                <NavLink
                  key={to}
                  to={to}
                  end={end}
                  title={collapsed ? label : undefined}
                  className={({ isActive }) =>
                    cn(
                      "flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors",
                      isActive
                        ? "bg-accent-light text-accent-hover font-medium"
                        : "text-muted-foreground hover:bg-card hover:text-foreground"
                    )
                  }
                >
                  <Icon className="h-4 w-4 shrink-0" />
                  {!collapsed && <span>{label}</span>}
                </NavLink>
              ))}
            </div>
          </div>
        ))}
      </nav>

      <div className="space-y-2 border-t border-border p-3">
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <Circle className="h-2 w-2 fill-success text-success" />
          {!collapsed && <span>All systems operational</span>}
        </div>
        {!collapsed && (
          <div className="flex items-center gap-2 rounded-md px-1 py-1">
            <div className="flex h-7 w-7 items-center justify-center rounded-full bg-card text-xs font-medium">
              O
            </div>
            <div className="leading-tight">
              <p className="text-sm">Owner</p>
              <p className="text-[10px] text-subtle-foreground">Human in control</p>
            </div>
          </div>
        )}
        <button
          onClick={toggle}
          className="flex w-full items-center justify-center rounded-md py-1.5 text-muted-foreground hover:bg-card hover:text-foreground"
        >
          {collapsed ? <ChevronsRight className="h-4 w-4" /> : <ChevronsLeft className="h-4 w-4" />}
        </button>
      </div>
    </aside>
  );
}
