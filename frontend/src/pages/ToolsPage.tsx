import { useState } from 'react';
import ToolsModule from '@/modules/tools';

export default function ToolsPage() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const handleToggleSidebar = () => {
    setSidebarCollapsed(!sidebarCollapsed);
  };

  return (
    <ToolsModule 
      onModuleChange={() => {}} 
      sidebarCollapsed={sidebarCollapsed} 
      onToggleSidebar={handleToggleSidebar} 
    />
  );
}
