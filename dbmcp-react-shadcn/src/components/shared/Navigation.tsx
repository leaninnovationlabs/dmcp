'use client';

import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import {
  Home,
  Database,
  Wrench,
  HelpCircle,
  Bell,
  Folder
} from 'lucide-react';

type NavigationItem = 'home' | 'data-sources' | 'tools';

interface NavigationProps {
  activeModule: NavigationItem;
  onModuleChange: (module: NavigationItem) => void;
  notificationCount?: number;
}

const Navigation = ({ activeModule, onModuleChange, notificationCount = 0 }: NavigationProps) => {
  const navigationItems = [
    { id: 'home', label: 'Home', icon: Home, color: 'blue' },
    { id: 'data-sources', label: 'Data Sources', icon: Database, color: 'green' },
    { id: 'tools', label: 'Tools', icon: Wrench, color: 'purple' },
  ];

  const getHeaderColor = (module: NavigationItem) => {
    switch (module) {
      case 'home':
        return 'bg-blue-600';
      case 'data-sources':
        return 'bg-green-600';
      case 'tools':
        return 'bg-purple-600';
      default:
        return 'bg-blue-600';
    }
  };

  const getAvatarColor = (module: NavigationItem) => {
    switch (module) {
      case 'home':
        return 'bg-blue-100 text-blue-600';
      case 'data-sources':
        return 'bg-green-100 text-green-600';
      case 'tools':
        return 'bg-purple-100 text-purple-600';
      default:
        return 'bg-blue-100 text-blue-600';
    }
  };

  const activeItem = navigationItems.find(item => item.id === activeModule);

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
      <div className="flex items-center space-x-3">
        <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${getHeaderColor(activeModule)}`}>
          <Folder className="w-5 h-5 text-white" />
        </div>
        <span className="text-lg font-semibold text-gray-900">{activeItem?.label}</span>
      </div>
      
      <div className="flex items-center space-x-4">
        <Button variant="ghost" size="sm" className="relative">
          <HelpCircle className="w-5 h-5 text-gray-600" />
        </Button>
        <Button variant="ghost" size="sm" className="relative">
          <Bell className="w-5 h-5 text-gray-600" />
          {notificationCount > 0 && (
            <Badge className="absolute -top-1 -right-1 h-5 w-5 rounded-full p-0 flex items-center justify-center text-xs">
              {notificationCount}
            </Badge>
          )}
        </Button>
        <Separator orientation="vertical" className="h-6" />
        <div className="flex items-center space-x-2">
          <Avatar className="h-8 w-8">
            <AvatarFallback className={`text-sm font-medium ${getAvatarColor(activeModule)}`}>
              IL
            </AvatarFallback>
          </Avatar>
          <span className="text-sm font-medium text-gray-700">Innovation Labs</span>
        </div>
      </div>
    </header>
  );
};

export default Navigation;
