import { useState } from 'react';
import DataSources from '@/modules/data-sources';

export default function DataSourcesPage() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const handleToggleSidebar = () => {
    setSidebarCollapsed(!sidebarCollapsed);
  };

  return (
    <DataSources 
      onModuleChange={() => {}} 
      sidebarCollapsed={sidebarCollapsed} 
      onToggleSidebar={handleToggleSidebar} 
    />
  );
}
