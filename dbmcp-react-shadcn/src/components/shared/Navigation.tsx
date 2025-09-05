'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import {
  Home,
  Database,
  Wrench,
  HelpCircle,
  Bell,
  Folder,
  Key,
  Lock
} from 'lucide-react';

type NavigationItem = 'home' | 'data-sources' | 'tools';

interface NavigationProps {
  activeModule: NavigationItem;
  onModuleChange: (module: NavigationItem) => void;
  notificationCount?: number;
}

const Navigation = ({ activeModule, onModuleChange, notificationCount = 0 }: NavigationProps) => {
  const [isPopoverOpen, setIsPopoverOpen] = useState(false);
  const navigationItems = [
    { id: 'home', label: 'Home', icon: Home },
    { id: 'data-sources', label: 'Data Sources', icon: Database },
    { id: 'tools', label: 'Tools', icon: Wrench },
  ];

  const getHeaderColor = () => {
    return 'bg-gray-600';
  };

  const getAvatarColor = () => {
    return 'bg-gray-100 text-gray-600';
  };

  const activeItem = navigationItems.find(item => item.id === activeModule);

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
      <div className="flex items-center space-x-3">
        <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${getHeaderColor()}`}>
          <Folder className="w-5 h-5 text-white" />
        </div>
        <span className="text-lg font-semibold text-gray-900">{activeItem?.label}</span>
      </div>
      
      <div className="flex items-center space-x-4">
        <Separator orientation="vertical" className="h-6" />
        <Popover open={isPopoverOpen} onOpenChange={setIsPopoverOpen}>
          <PopoverTrigger asChild>
            <Button variant="ghost" className="flex items-center space-x-2 p-2 hover:bg-gray-50">
              <Avatar className="h-8 w-8">
                <AvatarFallback className={`text-sm font-medium ${getAvatarColor()}`}>
                  IL
                </AvatarFallback>
              </Avatar>
              <span className="text-sm font-medium text-gray-700">Innovation Labs</span>
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-56 p-2" align="end">
            <div className="space-y-1">
              <Button
                variant="ghost"
                className="w-full justify-start h-auto p-3 text-gray-700 hover:bg-gray-50"
                onClick={() => {
                  console.log('Change Password clicked');
                  setIsPopoverOpen(false);
                }}
              >
                <Lock className="w-4 h-4 mr-3 text-gray-500" />
                <span className="font-medium">Change Password</span>
              </Button>
              <Button
                variant="ghost"
                className="w-full justify-start h-auto p-3 text-gray-700 hover:bg-gray-50"
                onClick={() => {
                  console.log('Access Keys clicked');
                  setIsPopoverOpen(false);
                }}
              >
                <Key className="w-4 h-4 mr-3 text-gray-500" />
                <span className="font-medium">Access Keys</span>
              </Button>
            </div>
          </PopoverContent>
        </Popover>
      </div>
    </header>
  );
};

export default Navigation;
