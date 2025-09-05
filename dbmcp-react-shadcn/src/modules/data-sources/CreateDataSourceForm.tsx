'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import {
  Home,
  Database,
  Wrench,
  ChevronLeft,
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

interface CreateDataSourceFormProps {
  dataSource?: DataSourceItem | null;
  onSave: (dataSource: DataSourceItem) => void;
  onCancel: () => void;
  sidebarCollapsed?: boolean;
  onToggleSidebar?: () => void;
}

const CreateDataSourceForm = ({ dataSource, onSave, onCancel, sidebarCollapsed = false, onToggleSidebar }: CreateDataSourceFormProps) => {
  const [formData, setFormData] = useState({
    name: dataSource?.name || '',
    database_type: dataSource?.database_type || '',
    host: dataSource?.host || '',
    port: dataSource?.port || '',
    database: dataSource?.database || '',
    username: dataSource?.username || '',
    password: '',
    connection_string: '',
    additional_params: ''
  });

  const isEditMode = !!dataSource;

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const newDataSource: DataSourceItem = {
      id: dataSource?.id || Date.now().toString(),
      name: formData.name,
      database_type: formData.database_type,
      host: formData.host,
      port: formData.port,
      database: formData.database,
      username: formData.username,
      created_at: dataSource?.created_at || new Date().toISOString()
    };
    onSave(newDataSource);
  };

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
            {[
              { id: 'home', label: 'Home', icon: Home },
              { id: 'data-sources', label: 'Data Sources', icon: Database },
              { id: 'tools', label: 'Tools', icon: Wrench },
            ].map((item) => {
              const Icon = item.icon;
              const isActive = item.id === 'data-sources';
              return (
                <Button
                  key={item.id}
                  variant="ghost"
                  className={`w-full justify-start h-auto ${sidebarCollapsed ? 'p-2' : 'p-3'} ${
                    isActive
                      ? 'bg-gray-50 text-gray-700 border border-gray-200'
                      : 'text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  <Icon className={`${sidebarCollapsed ? 'w-5 h-5' : 'w-5 h-5 mr-3'} ${isActive ? 'text-gray-600' : 'text-gray-500'}`} />
                  {!sidebarCollapsed && <span className="font-medium">{item.label}</span>}
                </Button>
              );
            })}
          </nav>
        </div>

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
        <div className="p-4 pt-2">
          {/* Page Header */}
          <div className="mb-6 max-w-4xl mx-auto">
            <h2 className="text-2xl font-bold text-black">
              {isEditMode ? 'Edit Datasource' : 'Create New Datasource'}
            </h2>
          </div>

          {/* Form */}
          <div className="bg-white border border-gray-200 rounded-lg shadow-sm p-8 max-w-4xl mx-auto">
            <form onSubmit={handleSubmit}>
              {/* Form Actions */}
              <div className="flex justify-end space-x-4 pt-6 border-b border-gray-200 mb-6 pb-6">
                <Button
                  type="button"
                  variant="outline"
                  onClick={onCancel}
                  className="text-gray-700 bg-gray-100 hover:bg-gray-200"
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  className="bg-[#FEBF23] hover:bg-[#FEBF23]/90 text-black border border-[#FEBF23]"
                >
                  {isEditMode ? 'Update Datasource' : 'Create Datasource'}
                </Button>
              </div>

              {/* Basic Information */}
              <div className="mb-8">
                <h2 className="text-xl font-semibold text-black mb-4 border-b border-gray-200 pb-2">
                  Basic Information
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Name <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => handleInputChange('name', e.target.value)}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-black"
                      placeholder="My Database"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Database Type <span className="text-red-500">*</span>
                    </label>
                    <select
                      value={formData.database_type}
                      onChange={(e) => handleInputChange('database_type', e.target.value)}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-black"
                    >
                      <option value="">Select database type</option>
                      <option value="postgresql">PostgreSQL</option>
                      <option value="mysql">MySQL</option>
                      <option value="sqlite">SQLite</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Connection Details */}
              <div className="mb-8">
                <h2 className="text-xl font-semibold text-black mb-4 border-b border-gray-200 pb-2">
                  Connection Details
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Host <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      value={formData.host}
                      onChange={(e) => handleInputChange('host', e.target.value)}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-black"
                      placeholder="localhost"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Port <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      value={formData.port}
                      onChange={(e) => handleInputChange('port', e.target.value)}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-black"
                      placeholder="5432"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Database Name <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      value={formData.database}
                      onChange={(e) => handleInputChange('database', e.target.value)}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-black"
                      placeholder="mydatabase"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Username <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      value={formData.username}
                      onChange={(e) => handleInputChange('username', e.target.value)}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-black"
                      placeholder="username"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Password <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="password"
                      value={formData.password}
                      onChange={(e) => handleInputChange('password', e.target.value)}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-black"
                      placeholder="••••••••"
                    />
                  </div>
                </div>
              </div>

              {/* Advanced Options */}
              <div className="mb-8">
                <h2 className="text-xl font-semibold text-black mb-4 border-b border-gray-200 pb-2">
                  Advanced Options
                </h2>
                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Connection String (Optional)
                    </label>
                    <input
                      type="text"
                      value={formData.connection_string}
                      onChange={(e) => handleInputChange('connection_string', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-black"
                      placeholder="postgresql://user:pass@host:port/db"
                    />
                    <p className="text-sm text-gray-500 mt-1">
                      If provided, this will override the individual connection parameters above.
                    </p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Additional Parameters (JSON)
                    </label>
                    <textarea
                      value={formData.additional_params}
                      onChange={(e) => handleInputChange('additional_params', e.target.value)}
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-black font-mono text-sm"
                      placeholder='{"key": "value"}'
                    />
                  </div>
                </div>
              </div>
            </form>
          </div>
        </div>
      </main>
    </>
  );
};

export default CreateDataSourceForm;
