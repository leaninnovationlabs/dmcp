'use client';

import { useState } from 'react';
import Navigation from './shared/Navigation';
import HomeModule from '@/modules/home';
import DataSources from '@/modules/data-sources';
import ToolsModule from '@/modules/tools';

type NavigationItem = 'home' | 'data-sources' | 'tools';

const CloudStorageLayout = () => {
  const [activeModule, setActiveModule] = useState<NavigationItem>('home');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const handleModuleChange = (module: NavigationItem) => {
    setActiveModule(module);
  };

  const toggleSidebar = () => {
    setSidebarCollapsed(!sidebarCollapsed);
  };

  const renderActiveModule = () => {
    switch (activeModule) {
      case 'home':
        return <HomeModule onModuleChange={handleModuleChange} sidebarCollapsed={sidebarCollapsed} onToggleSidebar={toggleSidebar} />;
      case 'data-sources':
        return <DataSources onModuleChange={handleModuleChange} sidebarCollapsed={sidebarCollapsed} onToggleSidebar={toggleSidebar} />;
      case 'tools':
        return <ToolsModule onModuleChange={handleModuleChange} sidebarCollapsed={sidebarCollapsed} onToggleSidebar={toggleSidebar} />;
      default:
        return <HomeModule onModuleChange={handleModuleChange} sidebarCollapsed={sidebarCollapsed} onToggleSidebar={toggleSidebar} />;
    }
  };

  return (
    <div className="h-screen bg-gray-50 flex flex-col">
      {/* Top Header Bar */}
      <Navigation 
        activeModule={activeModule} 
        onModuleChange={handleModuleChange}
        notificationCount={17}
      />
      
      {/* Main Content Area */}
      <div className="flex flex-1 overflow-hidden">
        {renderActiveModule()}
      </div>
    </div>
  );
};

export default CloudStorageLayout;
