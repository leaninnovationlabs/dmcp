'use client';

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import {
  Home,
  Database,
  Wrench,
  Plus,
  Eye,
  ChevronLeft,
  Upload,
  FileText,
  Zap,
  Palette,
  Search,
  Play,
  Calendar,
  Edit,
  Server,
  Cog
} from 'lucide-react';

type NavigationItem = 'home' | 'data-sources' | 'tools';

interface ToolItem {
  id: string;
  name: string;
  description: string;
  type: string;
  datasource_id: string;
  sql: string;
  parameters?: ToolParameter[];
  created_at: string;
}

interface ToolParameter {
  name: string;
  type: string;
  description?: string;
  required: boolean;
  default?: string;
}

interface Datasource {
  id: string;
  name: string;
  database_type: string;
}

interface ToolsModuleProps {
  onModuleChange: (module: NavigationItem) => void;
  sidebarCollapsed?: boolean;
  onToggleSidebar?: () => void;
}

const ToolsModule = ({ onModuleChange, sidebarCollapsed = false, onToggleSidebar }: ToolsModuleProps) => {
  const navigate = useNavigate();
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingTool, setEditingTool] = useState<ToolItem | null>(null);

  const tools: ToolItem[] = [
    {
      id: '1',
      name: 'User Analytics Query',
      description: 'Get user analytics data with filtering options',
      type: 'query',
      datasource_id: '1',
      sql: 'SELECT user_id, action, created_at FROM user_actions WHERE created_at >= {{ start_date }} AND created_at <= {{ end_date }}',
      parameters: [
        { name: 'start_date', type: 'date', required: true, description: 'Start date for the query' },
        { name: 'end_date', type: 'date', required: true, description: 'End date for the query' }
      ],
      created_at: '2024-01-15T10:30:00Z'
    },
    {
      id: '2',
      name: 'Revenue Report',
      description: 'Generate revenue reports by period',
      type: 'query',
      datasource_id: '2',
      sql: 'SELECT SUM(amount) as total_revenue, DATE(created_at) as date FROM transactions WHERE created_at >= {{ start_date }} GROUP BY DATE(created_at)',
      parameters: [
        { name: 'start_date', type: 'date', required: true, description: 'Start date for revenue calculation' }
      ],
      created_at: '2024-01-10T14:20:00Z'
    },
  ];

  const datasources: Datasource[] = [
    { id: '1', name: 'Production PostgreSQL', database_type: 'postgresql' },
    { id: '2', name: 'Development MySQL', database_type: 'mysql' }
  ];

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

  const getToolTypeIcon = (toolType: string) => {
    switch (toolType) {
      case 'query':
        return <Search className="w-8 h-8 text-gray-600" />;
      case 'http':
        return <Zap className="w-8 h-8 text-gray-600" />;
      case 'code':
        return <FileText className="w-8 h-8 text-gray-600" />;
      default:
        return <Wrench className="w-8 h-8 text-gray-600" />;
    }
  };

  const getToolTypeColor = (toolType: string) => {
    switch (toolType) {
      case 'query':
        return 'bg-gray-100 text-gray-800';
      case 'http':
        return 'bg-gray-100 text-gray-800';
      case 'code':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getDatasourceName = (datasourceId: string) => {
    const datasource = datasources.find(ds => ds.id === datasourceId);
    return datasource ? datasource.name : `Datasource #${datasourceId}`;
  };

  const handleAddTool = () => {
    setShowCreateForm(true);
    setEditingTool(null);
  };

  const handleEditTool = (tool: ToolItem) => {
    setEditingTool(tool);
    setShowCreateForm(true);
  };

  const handleCancelForm = () => {
    setShowCreateForm(false);
    setEditingTool(null);
  };

  const handleSaveTool = (tool: ToolItem) => {
    // Here you would typically save to an API
    console.log('Saving tool:', tool);
    setShowCreateForm(false);
    setEditingTool(null);
  };

  const handleExecuteTool = async (toolId: string) => {
    // Simulate tool execution
    console.log('Executing tool:', toolId);
  };

  if (showCreateForm) {
    return (
      <CreateToolForm
        tool={editingTool}
        datasources={datasources}
        onSave={handleSaveTool}
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
                <Wrench className="w-5 h-5 text-white" />
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
              const isActive = item.id === 'tools';
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

        {/* Tool Categories */}
        {!sidebarCollapsed && (
          <div className="p-4 flex-1">
            <h3 className="text-sm font-semibold text-gray-900 mb-3">Tool Categories</h3>
            <div className="space-y-1">
              <button className="w-full flex items-center space-x-2 px-3 py-2 rounded-lg bg-gray-50 text-gray-700 border border-gray-200">
                <Search className="w-4 h-4 text-gray-600" />
                <span className="text-sm font-medium">Analytics (2)</span>
              </button>
              <button className="w-full flex items-center space-x-2 px-3 py-2 rounded-lg text-gray-700 hover:bg-gray-50">
                <Zap className="w-4 h-4 text-gray-500" />
                <span className="text-sm font-medium">Automation (1)</span>
              </button>
              <button className="w-full flex items-center space-x-2 px-3 py-2 rounded-lg text-gray-700 hover:bg-gray-50">
                <Palette className="w-4 h-4 text-gray-500" />
                <span className="text-sm font-medium">Design (1)</span>
              </button>
              <button className="w-full flex items-center space-x-2 px-3 py-2 rounded-lg text-gray-700 hover:bg-gray-50">
                <FileText className="w-4 h-4 text-gray-500" />
                <span className="text-sm font-medium">Development (1)</span>
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
            <Button 
              onClick={handleAddTool}
              className="flex flex-col items-center space-y-2 bg-[#FEBF23] hover:bg-[#FEBF23]/90 text-black border border-[#FEBF23] px-6 py-4 h-auto"
            >
              <Plus className="w-5 h-5" />
              <span className="text-sm">Add New Tool</span>
            </Button>
            <Button className="flex flex-col items-center space-y-2 bg-white hover:bg-gray-50 text-gray-900 border border-gray-200 px-6 py-4 h-auto">
              <Upload className="w-5 h-5" />
              <span className="text-sm">Import Tool</span>
            </Button>
          </div>

          {/* Tools Overview */}
          <div className="bg-white rounded-lg border border-gray-200 p-4 mb-6">
            <div className="flex items-center space-x-2 mb-2">
              <Eye className="w-5 h-5 text-gray-600" />
              <h3 className="text-lg font-semibold text-gray-900">Tools Overview</h3>
            </div>
            <p className="text-gray-600 mb-3">
              Manage your development and productivity tools.
              <a href="#" className="text-gray-600 hover:text-gray-700 ml-1 underline">
                View documentation
              </a>
            </p>
          </div>

          {/* Breadcrumbs */}
          <div className="flex items-center space-x-2 mb-4">
            <span className="text-sm text-gray-500">Tools / Demo</span>
          </div>

          {/* Tools List */}
          <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Manage and execute your database tools</h2>
            
            {/* Tools Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {tools.map((tool) => (
                <div
                  key={tool.id}
                  className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow cursor-pointer border border-gray-200"
                  onClick={() => handleEditTool(tool)}
                >
                  <div className="p-8">
                    {/* Header */}
                    <div className="flex items-start justify-between mb-6">
                      <div className="flex items-center space-x-4">
                        <div className="flex-shrink-0">
                          {getToolTypeIcon(tool.type)}
                        </div>
                        <div className="min-w-0 flex-1">
                          <h3 className="text-xl font-semibold text-gray-900 truncate mb-2">
                            {tool.name}
                          </h3>
                          <Badge className={getToolTypeColor(tool.type)}>
                            {tool.type.toUpperCase()}
                          </Badge>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2 flex-shrink-0">
                        <button 
                          className="text-gray-400 hover:text-gray-600 transition-colors p-2 rounded-lg hover:bg-gray-100"
                          title="Execute Tool"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleExecuteTool(tool.id);
                          }}
                        >
                          <Play className="w-5 h-5" />
                        </button>
                      </div>
                    </div>

                    {/* Description */}
                    <p className="text-sm text-gray-600 mb-6 line-clamp-2">
                      {tool.description}
                    </p>

                    {/* Tool Info */}
                    <div className="space-y-3 text-sm text-gray-600 mb-6">
                      <div className="flex items-center space-x-3">
                        <Server className="text-gray-400 w-4 h-4" />
                        <span className="font-medium">Datasource:</span>
                        <span className="text-gray-700">{getDatasourceName(tool.datasource_id)}</span>
                      </div>
                      <div className="flex items-center space-x-3">
                        <Cog className="text-gray-400 w-4 h-4" />
                        <span className="font-medium">Parameters:</span>
                        <span className="text-gray-700">{tool.parameters?.length || 0} parameter{(tool.parameters?.length || 0) !== 1 ? 's' : ''}</span>
                      </div>
                    </div>

                    {/* SQL Preview */}
                    {tool.sql && (
                      <div className="mb-6 p-4 bg-gray-50 rounded-md">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">SQL Preview</span>
                        </div>
                        <code className="text-xs text-gray-700 block truncate">
                          {tool.sql.substring(0, 100)}
                          {tool.sql.length > 100 ? '...' : ''}
                        </code>
                      </div>
                    )}

                    {/* Footer */}
                    <div className="pt-4 border-t border-gray-200 flex justify-between items-center">
                      <span className="text-sm text-gray-500 flex items-center gap-1">
                        <Calendar className="w-4 h-4" />
                        Created: {formatDate(tool.created_at)}
                      </span>
                      <span className="text-gray-600 font-medium text-sm flex items-center gap-1">
                        <Edit className="w-4 h-4" />
                        Click to edit
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>
    </>
  );
};

// Create Tool Form Component
interface CreateToolFormProps {
  tool?: ToolItem | null;
  datasources: Datasource[];
  onSave: (tool: ToolItem) => void;
  onCancel: () => void;
  sidebarCollapsed?: boolean;
  onToggleSidebar?: () => void;
}

const CreateToolForm = ({ tool, datasources, onSave, onCancel, sidebarCollapsed = false, onToggleSidebar }: CreateToolFormProps) => {
  const [formData, setFormData] = useState({
    name: tool?.name || '',
    description: tool?.description || '',
    type: tool?.type || '',
    datasource_id: tool?.datasource_id || '',
    sql: tool?.sql || '',
    parameters: tool?.parameters || []
  });

  const isEditMode = !!tool;

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const newTool: ToolItem = {
      id: tool?.id || Date.now().toString(),
      name: formData.name,
      description: formData.description,
      type: formData.type,
      datasource_id: formData.datasource_id,
      sql: formData.sql,
      parameters: formData.parameters,
      created_at: tool?.created_at || new Date().toISOString()
    };
    onSave(newTool);
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
                <Wrench className="w-5 h-5 text-white" />
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
              const isActive = item.id === 'tools';
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
              {isEditMode ? 'Edit Tool' : 'Create New Tool'}
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
                  {isEditMode ? 'Update Tool' : 'Create Tool'}
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
                      placeholder="e.g., User Analytics Query"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Tool Type <span className="text-red-500">*</span>
                    </label>
                    <select
                      value={formData.type}
                      onChange={(e) => handleInputChange('type', e.target.value)}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-black"
                    >
                      <option value="">Select tool type</option>
                      <option value="query">Query</option>
                      <option value="http" disabled>HTTP (Coming Soon)</option>
                      <option value="code" disabled>Code (Coming Soon)</option>
                    </select>
                  </div>
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                    <textarea
                      value={formData.description}
                      onChange={(e) => handleInputChange('description', e.target.value)}
                      rows={2}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-black"
                      placeholder="Brief description of what this tool does"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Datasource <span className="text-red-500">*</span>
                    </label>
                    <select
                      value={formData.datasource_id}
                      onChange={(e) => handleInputChange('datasource_id', e.target.value)}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-black"
                    >
                      <option value="">Select datasource</option>
                      {datasources.map(ds => (
                        <option key={ds.id} value={ds.id}>
                          {ds.name} ({ds.database_type})
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              {/* SQL Query */}
              <div className="mb-8">
                <h2 className="text-xl font-semibold text-black mb-4 border-b border-gray-200 pb-2">SQL Query</h2>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    SQL Query <span className="text-red-500">*</span>
                  </label>
                  <textarea
                    value={formData.sql}
                    onChange={(e) => handleInputChange('sql', e.target.value)}
                    rows={8}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-black font-mono text-sm"
                    placeholder="SELECT * FROM table_name WHERE column = {{ parameter_name }}"
                  />
                  <p className="text-sm text-gray-500 mt-2">
                    Use <code className="bg-gray-100 px-1 rounded">{`{{ parameter_name }}`}</code> for parameter placeholders in your SQL query.
                  </p>
                </div>
              </div>

              {/* Parameters */}
              <div className="mb-8">
                <h2 className="text-xl font-semibold text-black mb-4 border-b border-gray-200 pb-2">Parameters</h2>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <p className="text-sm text-gray-600">Define parameters that users can pass to this tool</p>
                    <Button
                      type="button"
                      className="bg-[#FEBF23] hover:bg-[#FEBF23]/90 text-black border border-[#FEBF23] rounded-lg px-3 py-1 text-sm font-medium"
                    >
                      <Plus className="w-4 h-4 mr-1" />
                      Add Parameter
                    </Button>
                  </div>
                  
                  <div className="text-center py-4 text-gray-500 bg-gray-50 rounded-md">
                    No parameters defined. Click "Add Parameter" to add one.
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

export default ToolsModule;
