import { useNavigate, useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Home, Database, Wrench, ChevronLeft } from "lucide-react";

interface SidebarProps {
  collapsed?: boolean;
  onToggle?: () => void;
}

const Sidebar = ({ collapsed = false, onToggle }: SidebarProps) => {
  const navigate = useNavigate();
  const location = useLocation();

  const navigationItems = [
    { id: "home", label: "Home", icon: Home, path: "/app" },
    {
      id: "data-sources",
      label: "Data Sources",
      icon: Database,
      path: "/data-sources",
    },
    { id: "tools", label: "Tools", icon: Wrench, path: "/tools" },
  ];

  const isActive = (path: string) => {
    return (
      location.pathname === path || location.pathname.startsWith(path + "/")
    );
  };

  const handleNavigation = (path: string) => {
    navigate(path);
  };

  return (
    <aside
      className={`${
        collapsed ? "w-16" : "w-64"
      } bg-sidebar border-r border-sidebar-border flex flex-col justify-between transition-[width] duration-200 ease-in-out shadow-lg h-full`}
    >
      {/* Main Navigation */}
      <div
        className={`transition-[padding] duration-200 ease-in-out ${
          collapsed ? "p-2" : "p-4"
        }`}
      >
        <nav className="space-y-2">
          {navigationItems.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.path);

            return (
              <Button
                key={item.id}
                variant="ghost"
                onClick={() => handleNavigation(item.path)}
                className={`w-full h-auto transition-all duration-200 ease-in-out ${
                  collapsed ? "justify-center p-2" : "justify-start p-3"
                } ${
                  active
                    ? "bg-sidebar-accent text-sidebar-accent-foreground border-1 border-sidebar-primary hover:bg-sidebar-accent"
                    : "text-sidebar-foreground hover:bg-sidebar-accent/50"
                }`}
              >
                <Icon
                  className={`w-5 h-5 transition-all duration-200 ease-in-out ${
                    !collapsed ? "mr-3" : "mr-0"
                  } ${
                    active
                      ? "text-sidebar-accent-foreground"
                      : "text-sidebar-foreground/70"
                  }`}
                />
                <span
                  className={`font-medium transition-all duration-200 ease-in-out ${
                    collapsed ? "opacity-0 w-0 overflow-hidden" : "opacity-100"
                  }`}
                >
                  {item.label}
                </span>
              </Button>
            );
          })}
        </nav>
      </div>

      {/* Collapse Button - Pushed to bottom */}
      <div className="p-2 border-t ">
        <Button
          variant="ghost"
          onClick={onToggle}
          className="w-full justify-center p-2 text-sidebar-foreground/70 hover:text-sidebar-foreground hover:bg-sidebar-accent/50 transition-all duration-200 ease-in-out"
        >
          <ChevronLeft
            className={`w-4 h-4 transition-transform duration-200 ease-in-out ${
              collapsed ? "rotate-180" : ""
            }`}
          />
          <span
            className={`transition-all duration-200 ease-in-out ${
              collapsed ? "opacity-0 w-0 overflow-hidden" : "opacity-100 ml-2"
            }`}
          >
            Collapse
          </span>
        </Button>
      </div>
    </aside>
  );
};

export default Sidebar;
