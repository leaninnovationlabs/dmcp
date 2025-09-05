import { useLocation } from 'react-router-dom';
import Navigation from './shared/Navigation';

interface CloudStorageLayoutProps {
  children: React.ReactNode;
}

const CloudStorageLayout = ({ children }: CloudStorageLayoutProps) => {
  const location = useLocation();

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

  return (
    <div className="h-screen bg-gray-50 flex flex-col">
      {/* Top Header Bar */}
      <Navigation 
        activeModule={activeModule} 
        notificationCount={17}
      />
      
      {/* Main Content Area */}
      <div className="flex flex-1 overflow-hidden">
        {children}
      </div>
    </div>
  );
};

export default CloudStorageLayout;
