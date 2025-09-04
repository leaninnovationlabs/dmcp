import React, { useState } from 'react';
import Sidebar from './Sidebar';
import Dashboard from '../modules/home/Dashboard';
import DataSources from '../modules/data-sources/DataSources';
import DatasourceEdit from '../modules/data-sources/DatasourceEdit';
import Tools from '../modules/tools/Tools';
import ToolEdit from '../modules/tools/ToolEdit';

const Layout = () => {
  console.log('Layout component loaded successfully!');
  const [activePage, setActivePage] = useState('home');
  const [datasourceEditId, setDatasourceEditId] = useState<string | null>(null);
  const [toolEditId, setToolEditId] = useState<string | null>(null);

  const handleNavigation = (page: string) => {
    setActivePage(page);
    setDatasourceEditId(null); // Clear edit mode when navigating
    setToolEditId(null); // Clear tool edit mode when navigating
    console.log(`Navigating to: ${page}`);
  };

  const handleDatasourceEdit = (id?: string) => {
    setActivePage('datasource');
    setDatasourceEditId(id || 'new');
  };

  const handleDatasourceCancel = () => {
    setDatasourceEditId(null);
  };

  const handleDatasourceSave = (datasource: any) => {
    console.log('Datasource saved:', datasource);
    setDatasourceEditId(null);
    // TODO: Update the datasources list
  };

  const handleDatasourceDelete = (id: string) => {
    console.log('Datasource deleted:', id);
    setDatasourceEditId(null);
    // TODO: Update the datasources list
  };

  const handleToolEdit = (id?: string) => {
    setActivePage('tools');
    setToolEditId(id || 'new');
  };

  const handleToolCancel = () => {
    setToolEditId(null);
  };

  const handleToolSave = (tool: any) => {
    console.log('Tool saved:', tool);
    setToolEditId(null);
    // TODO: Update the tools list
  };

  const handleToolDelete = (id: string) => {
    console.log('Tool deleted:', id);
    setToolEditId(null);
    // TODO: Update the tools list
  };

  const handleLogout = () => {
    // TODO: Implement logout logic here
    console.log('Logout clicked');
  };

  const renderPage = () => {
    switch (activePage) {
      case 'home':
        return <Dashboard />;
      case 'datasource':
        if (datasourceEditId) {
          return (
            <DatasourceEdit
              datasourceId={datasourceEditId === 'new' ? undefined : datasourceEditId}
              onSave={handleDatasourceSave}
              onCancel={handleDatasourceCancel}
              onDelete={handleDatasourceDelete}
            />
          );
        }
        return (
          <DataSources 
            onAddDatasource={() => handleDatasourceEdit()}
            onEditDatasource={(id: string) => handleDatasourceEdit(id)}
          />
        );
      case 'tools':
        if (toolEditId) {
          return (
            <ToolEdit
              toolId={toolEditId === 'new' ? undefined : toolEditId}
              onSave={handleToolSave}
              onCancel={handleToolCancel}
              onDelete={handleToolDelete}
            />
          );
        }
        return (
          <Tools
            onAddTool={() => handleToolEdit()}
            onEditTool={(id: string) => handleToolEdit(id)}
          />
        );
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="min-h-screen bg-white">
      <Sidebar 
        activePage={activePage}
        onNavigate={handleNavigation}
        onLogout={handleLogout}
      />
      
      {/* Main Content */}
      <div className="transition-all duration-300 lg:pl-64 pt-16 lg:pt-0">
        {renderPage()}
      </div>
    </div>
  );
};

export default Layout;
