import React, { useState, useEffect } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faPlus, 
  faExclamationTriangle, 
  faRedo, 
  faTools,
  faPlay,
  faSpinner,
  faDatabase,
  faCog
} from '@fortawesome/free-solid-svg-icons';

interface Tool {
  id: string;
  name: string;
  description?: string;
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

interface Notification {
  id: string;
  message: string;
  type: 'success' | 'error' | 'info' | 'warning';
}

interface ToolsProps {
  onAddTool?: () => void;
  onEditTool?: (id: string) => void;
}

const Tools: React.FC<ToolsProps> = ({ onAddTool, onEditTool }) => {
  const [tools, setTools] = useState<Tool[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [executingTool, setExecutingTool] = useState<string | null>(null);
  const [datasourcesMap, setDatasourcesMap] = useState<Record<string, Datasource>>({});

  useEffect(() => {
    loadTools();
    loadDatasources();
  }, []);

  const loadTools = async () => {
    setLoading(true);
    setError(null);

    try {
      // Mock data for now - replace with API call later
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const mockTools: Tool[] = [
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
        }
      ];
      
      setTools(mockTools);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to connect to server';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const loadDatasources = async () => {
    try {
      // Mock datasources for now - replace with API call later
      const mockDatasources: Datasource[] = [
        { id: '1', name: 'Production PostgreSQL', database_type: 'postgresql' },
        { id: '2', name: 'Development MySQL', database_type: 'mysql' }
      ];
      
      const datasourcesMap: Record<string, Datasource> = {};
      mockDatasources.forEach(ds => {
        datasourcesMap[ds.id] = ds;
      });
      
      setDatasourcesMap(datasourcesMap);
    } catch (error) {
      // Silently fail - not critical for display
    }
  };

  const handleAddTool = () => {
    if (onAddTool) {
      onAddTool();
    } else {
      console.log('Navigate to tool edit page');
    }
  };

  const handleToolClick = (toolId: string) => {
    if (onEditTool) {
      onEditTool(toolId);
    } else {
      console.log('Navigate to tool edit page with ID:', toolId);
    }
  };

  const handleExecuteTool = async (toolId: string) => {
    setExecutingTool(toolId);

    try {
      // Mock execution - replace with API call later
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const rowCount = Math.floor(Math.random() * 100) + 10;
      const executionTime = Math.floor(Math.random() * 500) + 50;
      
      showNotification(
        `Tool executed successfully! ${rowCount} rows returned in ${executionTime}ms`, 
        'success'
      );
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Tool execution failed';
      showNotification(errorMessage, 'error');
    } finally {
      setExecutingTool(null);
    }
  };

  const showNotification = (message: string, type: 'success' | 'error' | 'info' | 'warning' = 'info') => {
    const id = Date.now().toString();
    const notification: Notification = { id, message, type };
    
    setNotifications(prev => [...prev, notification]);
    
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== id));
    }, 5000);
  };

  const getToolTypeIcon = (toolType: string) => {
    const icons: { [key: string]: any } = {
      'query': '🔍',
      'http': '🌐',
      'code': '⚙️'
    };
    return icons[toolType] || '🛠️';
  };

  const getToolTypeColor = (toolType: string) => {
    const colors: { [key: string]: string } = {
      'query': 'bg-blue-100 text-blue-800',
      'http': 'bg-gray-100 text-gray-500',
      'code': 'bg-gray-100 text-gray-500'
    };
    return colors[toolType] || 'bg-gray-100 text-gray-800';
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const escapeHtml = (text: string) => {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  };

  const renderToolCard = (tool: Tool) => {
    const isExecuting = executingTool === tool.id;
    const datasource = datasourcesMap[tool.datasource_id];
    const datasourceName = datasource ? datasource.name : `Datasource #${tool.datasource_id}`;
    const paramCount = tool.parameters ? tool.parameters.length : 0;
    
    return (
      <div 
        key={tool.id}
        className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow cursor-pointer"
        onClick={() => handleToolClick(tool.id)}
      >
        <div className="p-8">
          {/* Header */}
          <div className="flex items-start justify-between mb-6">
            <div className="flex items-center space-x-4">
              <div className="flex-shrink-0 text-2xl">{getToolTypeIcon(tool.type)}</div>
              <div className="min-w-0 flex-1">
                <h3 className="text-xl font-semibold text-gray-900 truncate mb-2">
                  {escapeHtml(tool.name)}
                </h3>
                <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getToolTypeColor(tool.type)}`}>
                  {tool.type.toUpperCase()}
                </span>
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
                disabled={isExecuting}
              >
                {isExecuting ? (
                  <FontAwesomeIcon icon={faSpinner} className="text-lg animate-spin" />
                ) : (
                  <FontAwesomeIcon icon={faPlay} className="text-lg" />
                )}
              </button>
            </div>
          </div>

          {/* Description */}
          {tool.description && (
            <p className="text-sm text-gray-600 mb-6 line-clamp-2">
              {escapeHtml(tool.description)}
            </p>
          )}

          {/* Tool Info */}
          <div className="space-y-3 text-sm text-gray-600 mb-6">
            <div className="flex items-center space-x-3">
              <FontAwesomeIcon icon={faDatabase} className="text-gray-400 w-4" />
              <span className="font-medium">Datasource:</span>
              <span className="text-gray-700">{escapeHtml(datasourceName)}</span>
            </div>
            <div className="flex items-center space-x-3">
              <FontAwesomeIcon icon={faCog} className="text-gray-400 w-4" />
              <span className="font-medium">Parameters:</span>
              <span className="text-gray-700">{paramCount} parameter{paramCount !== 1 ? 's' : ''}</span>
            </div>
          </div>

          {/* SQL Preview */}
          {tool.sql && (
            <div className="mb-6 p-4 bg-gray-50 rounded-md">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">SQL Preview</span>
              </div>
              <code className="text-xs text-gray-700 block truncate">
                {escapeHtml(tool.sql.substring(0, 100))}
                {tool.sql.length > 100 ? '...' : ''}
              </code>
            </div>
          )}

          {/* Footer */}
          <div className="pt-4 border-t border-gray-200 flex justify-between items-center">
            <span className="text-sm text-gray-500">Created: {formatDate(tool.created_at)}</span>
            <span className="text-purple-600 font-medium text-sm">Click to edit</span>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="bg-white min-h-screen">
      {/* Page Header */}
      <div className="border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-black">Tools</h1>
              <p className="text-gray-600 mt-2">Manage and execute your database tools</p>
            </div>
            <div className="flex items-center">
              <button 
                onClick={handleAddTool}
                className="bg-black text-white rounded-lg px-6 py-3 font-medium transition-all duration-200 hover:bg-gray-800 hover:-translate-y-0.5 inline-flex items-center gap-2"
              >
                <FontAwesomeIcon icon={faPlus} />
                Add New Tool
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto p-6">
        {/* Loading State */}
        {loading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-black"></div>
            <p className="mt-4 text-gray-600">Loading tools...</p>
          </div>
        )}

        {/* Error State */}
        {error && !loading && (
          <div className="text-center py-12">
            <div className="text-red-500 text-4xl mb-4">
              <FontAwesomeIcon icon={faExclamationTriangle} />
            </div>
            <p className="text-red-600 font-semibold text-lg">Error loading tools</p>
            <p className="text-gray-600 mt-2">{error}</p>
            <button 
              onClick={loadTools}
              className="mt-6 bg-black text-white rounded-lg px-6 py-3 font-medium transition-all duration-200 hover:bg-gray-800 hover:-translate-y-0.5 inline-flex items-center gap-2"
            >
              <FontAwesomeIcon icon={faRedo} />
              Retry
            </button>
          </div>
        )}

        {/* Empty State */}
        {!loading && !error && tools.length === 0 && (
          <div className="text-center py-16">
            <div className="text-gray-400 text-6xl mb-6">
              <FontAwesomeIcon icon={faTools} />
            </div>
            <h3 className="text-2xl font-semibold text-black mb-3">No Tools Found</h3>
            <p className="text-gray-600 mb-8 max-w-md mx-auto">
              Create your first tool to get started with database management
            </p>
            <button 
              onClick={handleAddTool}
              className="bg-black text-white rounded-lg px-6 py-3 font-medium transition-all duration-200 hover:bg-gray-800 hover:-translate-y-0.5 inline-flex items-center gap-2"
            >
              <FontAwesomeIcon icon={faPlus} />
              Create Your First Tool
            </button>
          </div>
        )}

        {/* Tools Grid */}
        {!loading && !error && tools.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 pb-12">
            {tools.map(renderToolCard)}
          </div>
        )}
      </div>

      {/* Notifications */}
      <div className="fixed top-4 right-4 z-50 space-y-2">
        {notifications.map(notification => {
          const colors = {
            success: 'bg-green-500',
            error: 'bg-red-500',
            info: 'bg-blue-500',
            warning: 'bg-yellow-500'
          };

          return (
            <div 
              key={notification.id}
              className={`notification ${colors[notification.type]} text-white px-6 py-3 rounded-lg shadow-lg transform transition-transform duration-300 max-w-sm`}
            >
              <p className="font-medium">{notification.message}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default Tools;
