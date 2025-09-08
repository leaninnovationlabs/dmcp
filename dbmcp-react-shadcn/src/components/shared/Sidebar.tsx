import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import {
  Home,
  Database,
  Wrench,
  ChevronLeft,
} from 'lucide-react';

type NavigationItem = 'home' | 'data-sources' | 'tools';

interface SidebarProps {
  collapsed?: boolean;
  onToggle?: () => void;
}

const Sidebar = ({ collapsed = false, onToggle }: SidebarProps) => {
  const navigate = useNavigate();
  const location = useLocation();

  const navigationItems = [
    { id: 'home', label: 'Home', icon: Home, path: '/app' },
    { id: 'data-sources', label: 'Data Sources', icon: Database, path: '/data-sources' },
    { id: 'tools', label: 'Tools', icon: Wrench, path: '/tools' },
  ];

  const isActive = (path: string) => {
    return location.pathname === path || location.pathname.startsWith(path + '/');
  };

  const handleNavigation = (path: string) => {
    navigate(path);
  };

  return (
    <aside className={`${collapsed ? 'w-16' : 'w-64'} bg-white border-r border-gray-200 flex flex-col transition-[width] duration-200 ease-in-out shadow-lg`}>
      {/* Main Navigation */}
      <div className={`transition-[padding] duration-200 ease-in-out ${collapsed ? 'p-2' : 'p-4'}`}>
        <nav className="space-y-2">
          {navigationItems.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.path);
            
            return (
              <Button
                key={item.id}
                variant="ghost"
                onClick={() => handleNavigation(item.path)}
                className={`w-full h-auto transition-all duration-200 ease-in-out ${collapsed ? 'justify-center p-2' : 'justify-start p-3'} ${
                  active
                    ? 'bg-[#FEBF23]/20 text-gray-700 border-2 border-[#FEBF23]/50 hover:bg-[#FEBF23]/20'
                    : 'text-gray-700 hover:bg-[#FEBF23]/10'
                }`}
              >
                <Icon className={`w-5 h-5 transition-all duration-200 ease-in-out ${!collapsed ? 'mr-3' : 'mr-0'} ${active ? 'text-gray-600' : 'text-gray-500'}`} />
                <span className={`font-medium transition-all duration-200 ease-in-out ${collapsed ? 'opacity-0 w-0 overflow-hidden' : 'opacity-100'}`}>
                  {item.label}
                </span>
              </Button>
            );
          })}
        </nav>
      </div>

      {/* Collapse Button */}
      <div className="p-2 border-t border-gray-200">
        <Button
          variant="ghost"
          onClick={onToggle}
          className="w-full justify-center p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-50 transition-all duration-200 ease-in-out"
        >
          <ChevronLeft className={`w-4 h-4 transition-transform duration-200 ease-in-out ${collapsed ? 'rotate-180' : ''}`} />
          <span className={`transition-all duration-200 ease-in-out ${collapsed ? 'opacity-0 w-0 overflow-hidden' : 'opacity-100 ml-2'}`}>
            Collapse
          </span>
        </Button>
      </div>
    </aside>
  );
};

export default Sidebar;
