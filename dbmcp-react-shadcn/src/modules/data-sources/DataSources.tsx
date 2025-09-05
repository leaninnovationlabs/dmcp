'use client';

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import CreateDataSourceForm from './CreateDataSourceForm';
import {
  Home,
  Database,
  Wrench,
  Plus,
  Eye,
  ChevronLeft,
  Upload,
  Edit
} from 'lucide-react';

type NavigationItem = 'home' | 'data-sources' | 'tools';

interface DataSourceItem {
  id: string;
  name: string;
  database_type: string;
  host: string;
  port: string;
  database: string;
  username: string;
  created_at: string;
}

interface DataSourcesProps {
  onModuleChange: (module: NavigationItem) => void;
  sidebarCollapsed?: boolean;
  onToggleSidebar?: () => void;
}

const DataSources = ({ onModuleChange, sidebarCollapsed = false, onToggleSidebar }: DataSourcesProps) => {
  const navigate = useNavigate();
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingDataSource, setEditingDataSource] = useState<DataSourceItem | null>(null);
  const [dataSources, setDataSources] = useState<DataSourceItem[]>([
    {
      id: '1',
      name: 'Production PostgreSQL',
      database_type: 'postgresql',
      host: 'prod-db.company.com',
      port: '5432',
      database: 'production',
      username: 'app_user',
      created_at: '2024-01-15T10:30:00Z'
    },
    {
      id: '2',
      name: 'Analytics MySQL',
      database_type: 'mysql',
      host: 'analytics.company.com',
      port: '3306',
      database: 'analytics',
      username: 'analytics_user',
      created_at: '2024-01-20T14:45:00Z'
    },
    {
      id: '3',
      name: 'Local SQLite',
      database_type: 'sqlite',
      host: 'localhost',
      port: '',
      database: 'local.db',
      username: '',
      created_at: '2024-02-01T09:15:00Z'
    }
  ]);

  const navigationItems = [
    { id: 'home', label: 'Home', icon: Home },
    { id: 'data-sources', label: 'Data Sources', icon: Database },
    { id: 'tools', label: 'Tools', icon: Wrench },
  ];

  const getActiveColor = () => {
    return 'bg-gray-50 text-gray-700 border-gray-200';
  };

  const getIconColor = (isActive: boolean) => {
    if (isActive) {
      return 'text-gray-600';
    }
    return 'text-gray-500';
  };

  const handleNavigationClick = (itemId: string) => {
    switch (itemId) {
      case 'home':
        navigate('/app');
        break;
      case 'data-sources':
        navigate('/data-sources');
        break;
      case 'tools':
        navigate('/tools');
        break;
      default:
        break;
    }
  };

  const handleAddDataSource = () => {
    setEditingDataSource(null);
    setShowCreateForm(true);
  };

  const handleEditDataSource = (dataSource: DataSourceItem) => {
    setEditingDataSource(dataSource);
    setShowCreateForm(true);
  };

  const handleSaveDataSource = (dataSource: DataSourceItem) => {
    if (editingDataSource) {
      // Update existing data source
      setDataSources(prev => prev.map(ds => ds.id === dataSource.id ? dataSource : ds));
    } else {
      // Add new data source
      setDataSources(prev => [...prev, dataSource]);
    }
    setShowCreateForm(false);
    setEditingDataSource(null);
  };

  const handleCancelForm = () => {
    setShowCreateForm(false);
    setEditingDataSource(null);
  };

  if (showCreateForm) {
    return (
      <CreateDataSourceForm
        dataSource={editingDataSource}
        onSave={handleSaveDataSource}
        onCancel={handleCancelForm}
        sidebarCollapsed={sidebarCollapsed}
        onToggleSidebar={onToggleSidebar}
      />
    );
  }

  return (
    <>
      {/* Left Sidebar Navigation */}
      <aside className={`${sidebarCollapsed ? 'w-16' : 'w-64'} bg-white border-r border-gray-200 flex flex-col transition-all duration-300 shadow-lg`}>
        {/* Header */}
        <div className={`${sidebarCollapsed ? 'p-2' : 'p-6'} border-b border-gray-200`}>
          {sidebarCollapsed ? (
            <div className="flex justify-center">
              <div className="w-8 h-8 bg-black rounded flex items-center justify-center">
                <Database className="w-5 h-5 text-white" />
              </div>
            </div>
          ) : (
            <>
              <h1 className="text-xl font-bold text-black">Opsloom Data MCP</h1>
              <p className="text-sm text-gray-600 mt-1">Connect AI assistants to your data</p>
            </>
          )}
        </div>

        {/* Main Navigation */}
        <div className={`${sidebarCollapsed ? 'p-2' : 'p-4'}`}>
          <nav className="space-y-2">
            {navigationItems.map((item) => {
              const Icon = item.icon;
              const isActive = item.id === 'data-sources';
              return (
                <Button
                  key={item.id}
                  variant="ghost"
                  onClick={() => handleNavigationClick(item.id)}
                  className={`w-full justify-start h-auto ${sidebarCollapsed ? 'p-2' : 'p-3'} ${
                    isActive
                      ? `${getActiveColor()} border`
                      : 'text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  <Icon className={`${sidebarCollapsed ? 'w-5 h-5' : 'w-5 h-5 mr-3'} ${getIconColor(isActive)}`} />
                  {!sidebarCollapsed && <span className="font-medium">{item.label}</span>}
                </Button>
              );
            })}
          </nav>
        </div>

        {!sidebarCollapsed && <Separator />}

        {/* Data Source Categories */}
        {!sidebarCollapsed && (
          <div className="p-4 flex-1">
            <h3 className="text-sm font-semibold text-gray-900 mb-3">Data Source Types</h3>
            <div className="space-y-1">
              <button className="w-full flex items-center space-x-2 px-3 py-2 rounded-lg bg-gray-50 text-gray-700 border border-gray-200">
                <Database className="w-4 h-4 text-gray-600" />
                <span className="text-sm font-medium">Databases ({dataSources.length})</span>
              </button>
            </div>
          </div>
        )}

        {/* Collapse Button */}
        <div className="p-2 border-t border-gray-200">
          <Button
            variant="ghost"
            onClick={onToggleSidebar}
            className="w-full justify-center h-auto p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-50"
          >
            <ChevronLeft className={`w-4 h-4 transition-transform duration-300 ${sidebarCollapsed ? 'rotate-180' : ''}`} />
            {!sidebarCollapsed && <span className="ml-2 text-sm">Collapse</span>}
          </Button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 overflow-auto bg-gray-50">
        <div className="p-4 pt-8">
          {/* Action Buttons Row */}
          <div className="flex items-center space-x-4 mb-6">
            <Button    onClick={handleAddDataSource} className="flex flex-col items-center space-y-2 bg-[#FEBF23] hover:bg-[#FEBF23]/90 text-black border border-[#FEBF23] px-6 py-4 h-auto">
            <Plus className="w-5 h-5" />
              <span className="text-sm">Add New Data Source</span>
            </Button>
            <Button className="flex flex-col items-center space-y-2 bg-white hover:bg-gray-50 text-gray-900 border border-gray-200 px-6 py-4 h-auto">
              <Upload className="w-5 h-5" />
              <span className="text-sm">Import Configuration</span>
            </Button>
          </div>

          {/* Data Sources Overview */}
          <div className="bg-white rounded-lg border border-gray-200 p-4 mb-6">
            <div className="flex items-center space-x-2 mb-2">
              <Eye className="w-5 h-5 text-gray-600" />
              <h3 className="text-lg font-semibold text-gray-900">Data Sources Overview</h3>
            </div>
            <p className="text-gray-600 mb-3">
              Manage your connected data sources and monitor their status.
              <a href="#" className="text-gray-600 hover:text-gray-700 ml-1 underline">
                View documentation
              </a>
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-gray-50 rounded-lg p-3">
                <div className="flex items-center space-x-2">
                  <Database className="w-4 h-4 text-gray-600" />
                  <span className="text-sm font-medium text-gray-700">Total Sources</span>
                </div>
                <p className="text-2xl font-bold text-gray-900 mt-1">3</p>
              </div>
              <div className="bg-gray-50 rounded-lg p-3">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="text-sm font-medium text-gray-700">Connected</span>
                </div>
                <p className="text-2xl font-bold text-gray-900 mt-1">3</p>
              </div>
              <div className="bg-gray-50 rounded-lg p-3">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                  <span className="text-sm font-medium text-gray-700">Disconnected</span>
                </div>
                <p className="text-2xl font-bold text-gray-900 mt-1">0</p>
              </div>
            </div>
          </div>

          {/* Data Sources List */}
          <div className="bg-white rounded-lg border border-gray-200">
            <div className="p-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">Manage your database connections</h3>
            </div>
            <div className="p-4">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {dataSources.map((dataSource) => (
                  <div key={dataSource.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center space-x-2">
                        <div className="w-8 h-8 bg-gray-100 rounded flex items-center justify-center">
                          <Database className="w-4 h-4 text-gray-600" />
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-900">{dataSource.name}</h4>
                          <p className="text-sm text-gray-500 capitalize">{dataSource.database_type}</p>
                        </div>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleEditDataSource(dataSource)}
                        className="text-gray-500 hover:text-gray-700"
                      >
                        <Edit className="w-4 h-4" />
                      </Button>
                    </div>
                    <div className="space-y-2 text-sm text-gray-600">
                      <div className="flex justify-between">
                        <span>Host:</span>
                        <span className="font-mono">{dataSource.host}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Database:</span>
                        <span className="font-mono">{dataSource.database}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>User:</span>
                        <span className="font-mono">{dataSource.username}</span>
                      </div>
                    </div>
                    <div className="mt-3 pt-3 border-t border-gray-100">
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-gray-500">
                          Created {new Date(dataSource.created_at).toLocaleDateString()}
                        </span>
                        <Badge variant="secondary" className="text-xs">
                          Connected
                        </Badge>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </main>
    </>
  );
};

export default DataSources;
