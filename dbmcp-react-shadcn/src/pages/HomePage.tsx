import { useState } from 'react';
import HomeModule from '@/modules/home';

export default function HomePage() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const handleToggleSidebar = () => {
    setSidebarCollapsed(!sidebarCollapsed);
  };

  return (
    <HomeModule 
      onModuleChange={() => {}} 
      sidebarCollapsed={sidebarCollapsed} 
      onToggleSidebar={handleToggleSidebar} 
    />
  );
}
