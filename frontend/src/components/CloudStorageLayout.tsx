import { useState } from 'react';
import { useLocation } from 'react-router-dom';
import Navigation from './shared/Navigation';
import Sidebar from './shared/Sidebar';

interface CloudStorageLayoutProps {
  children: React.ReactNode;
}

const CloudStorageLayout = ({ children }: CloudStorageLayoutProps) => {
  const location = useLocation();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  // Determine active module based on current route
  const getActiveModule = () => {
    const path = location.pathname;
    if (path === '/app') return 'home';
    if (path === '/data-sources') return 'data-sources';
    if (path === '/tools') return 'tools';
    if (path === '/generate-token') return 'token';
    if (path === '/change-password') return 'change-password';
    if (path === '/profile') return 'profile';
    return 'home';
  };

  const activeModule = getActiveModule();

  const handleToggleSidebar = () => {
    setSidebarCollapsed(!sidebarCollapsed);
  };

  // Hide sidebar for profile, generate-token, and change-password pages
  const isProfilePage = location.pathname === '/profile';
  const isGenerateTokenPage = location.pathname === '/generate-token';
  const isChangePasswordPage = location.pathname === '/change-password';
  const hideSidebar = isProfilePage || isGenerateTokenPage || isChangePasswordPage;

  return (
    <div className="h-screen bg-gray-50 flex flex-col">
      {/* Top Header Bar */}
      <Navigation 
        activeModule={activeModule} 
        notificationCount={17}
      />
      
      {/* Main Content Area with Sidebar */}
      <div className="flex flex-1 overflow-hidden">
        {!hideSidebar && (
          <Sidebar 
            collapsed={sidebarCollapsed} 
            onToggle={handleToggleSidebar}
          />
        )}
        <main className="flex-1 overflow-auto bg-gray-50">
          {children}
        </main>
      </div>
    </div>
  );
};

export default CloudStorageLayout;
