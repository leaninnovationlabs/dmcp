import { useState } from 'react';
import Navigation from './shared/Navigation';
import HomeModule from '@/modules/home';
import DataSources from '@/modules/data-sources';
import ToolsModule from '@/modules/tools';
import { LoginModule, TokenModule } from '@/modules/auth';
import { useAuth } from '@/contexts/AuthContext';

type NavigationItem = 'home' | 'data-sources' | 'tools' | 'auth' | 'token';

const CloudStorageLayout = () => {
  const [activeModule, setActiveModule] = useState<NavigationItem>('home');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const { isAuthenticated, isLoading } = useAuth();

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
      case 'auth':
        return <LoginModule onLoginSuccess={() => setActiveModule('home')} />;
      case 'token':
        return <TokenModule />;
      default:
        return <HomeModule onModuleChange={handleModuleChange} sidebarCollapsed={sidebarCollapsed} onToggleSidebar={toggleSidebar} />;
    }
  };

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-black mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Show login if not authenticated
  if (!isAuthenticated) {
    return <LoginModule onLoginSuccess={() => setActiveModule('home')} />;
  }

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
