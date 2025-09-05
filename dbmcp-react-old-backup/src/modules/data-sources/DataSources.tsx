import React, { useState, useEffect } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faPlus, 
  faExclamationTriangle, 
  faRedo, 
  faDatabase,
  faPlug,
  faServer,
  faUser,
  faSpinner
} from '@fortawesome/free-solid-svg-icons';
// import { apiService, Datasource } from '../../services/api';

interface Datasource {
  id: string;
  name: string;
  database_type: string;
  host?: string;
  port?: string;
  database: string;
  username?: string;
  created_at: string;
}

interface Notification {
  id: string;
  message: string;
  type: 'success' | 'error' | 'info' | 'warning';
}

interface DataSourcesProps {
  onAddDatasource?: () => void;
  onEditDatasource?: (id: string) => void;
}

const DataSources: React.FC<DataSourcesProps> = ({ onAddDatasource, onEditDatasource }) => {
  const [datasources, setDatasources] = useState<Datasource[]>([
    {
      id: '1',
      name: 'Production PostgreSQL',
      database_type: 'postgresql',
      host: 'localhost',
      port: '5432',
      database: 'production_db',
      username: 'admin',
      created_at: '2024-01-15T10:30:00Z'
    },
    {
      id: '2',
      name: 'Development MySQL',
      database_type: 'mysql',
      host: 'dev-server',
      port: '3306',
      database: 'dev_db',
      username: 'developer',
      created_at: '2024-01-10T14:20:00Z'
    }
  ]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [testingConnection, setTestingConnection] = useState<string | null>(null);

  // const loadDatasources = async () => {
  //   setLoading(true);
  //   setError(null);

  //   try {
  //     if (!apiService.isAuthenticated()) {
  //       throw new Error('Authentication required');
  //     }

  //     const data = await apiService.getDatasources();
  //     setDatasources(data);
  //   } catch (err) {
  //     const errorMessage = err instanceof Error ? err.message : 'Failed to connect to server';
  //     setError(errorMessage);
  //   } finally {
  //       setLoading(false);
  //   }
  // };

  useEffect(() => {
    //loadDatasources();
  }, []);

  const handleAddDatasource = () => {
    if (onAddDatasource) {
      onAddDatasource();
    } else {
      console.log('Navigate to datasource edit page');
    }
  };

  const handleDatasourceClick = (datasourceId: string) => {
    if (onEditDatasource) {
      onEditDatasource(datasourceId);
    } else {
      console.log('Navigate to datasource edit page with ID:', datasourceId);
    }
  };

  const handleTestConnection = async (datasourceId: string) => {
    setTestingConnection(datasourceId);

    // Simulate API call delay
    setTimeout(() => {
      showNotification('Connection test successful', 'success');
      setTestingConnection(null);
    }, 1000);

    // try {
    //   const success = await apiService.testDatasourceConnection(datasourceId);
    //   if (success) {
    //     showNotification('Connection test successful', 'success');
    //   } else {
    //     showNotification('Connection test failed', 'error');
    //   }
    // } catch (err) {
    //   const errorMessage = err instanceof Error ? err.message : 'Connection test failed';
    //   showNotification(errorMessage, 'error');
    // } finally {
    //   setTestingConnection(null);
    // }
  };

  const showNotification = (message: string, type: 'success' | 'error' | 'info' | 'warning' = 'info') => {
    const id = Date.now().toString();
    const notification: Notification = { id, message, type };
    
    setNotifications(prev => [...prev, notification]);
    
    // Remove notification after 5 seconds
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== id));
    }, 5000);
  };

  const getDatabaseIcon = (databaseType: string) => {
    const colors: { [key: string]: string } = {
      'postgresql': 'text-blue-600',
      'mysql': 'text-orange-500',
      'sqlite': 'text-gray-600',
      'databricks': 'text-orange-400'
    };
    
    const color = colors[databaseType.toLowerCase()] || 'text-blue-500';
    
    return <FontAwesomeIcon icon={faDatabase} className={`text-2xl ${color}`} />;
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

  const renderDatasourceCard = (datasource: Datasource) => {
    const isTesting = testingConnection === datasource.id;
    
    return (
      <div 
        key={datasource.id}
        className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow cursor-pointer datasource-card"
        onClick={() => handleDatasourceClick(datasource.id)}
      >
        <div className="p-8">
          {/* Header */}
          <div className="flex items-start justify-between mb-6">
            <div className="flex items-center space-x-4">
              <div className="flex-shrink-0">{getDatabaseIcon(datasource.database_type)}</div>
              <div className="min-w-0 flex-1">
                <h3 className="text-xl font-semibold text-gray-900 truncate mb-2">
                  {escapeHtml(datasource.name)}
                </h3>
                <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                  {datasource.database_type.toUpperCase()}
                </span>
              </div>
            </div>
            <div className="flex items-center space-x-2 flex-shrink-0">
              <button 
                className="text-gray-400 hover:text-gray-600 transition-colors p-2 rounded-lg hover:bg-gray-100"
                title="Test Connection"
                onClick={(e) => {
                  e.stopPropagation();
                  handleTestConnection(datasource.id);
                }}
                disabled={isTesting}
              >
                {isTesting ? (
                  <FontAwesomeIcon icon={faSpinner} className="text-lg animate-spin" />
                ) : (
                  <FontAwesomeIcon icon={faPlug} className="text-lg" />
                )}
              </button>
            </div>
          </div>

          {/* Connection Info */}
          <div className="space-y-3 text-sm text-gray-600 mb-6">
            {datasource.host && (
              <div className="flex items-center space-x-3">
                <FontAwesomeIcon icon={faServer} className="text-gray-400 w-4" />
                <span className="font-medium">Host:</span>
                <span className="text-gray-700">
                  {escapeHtml(datasource.host)}
                  {datasource.port && `:${datasource.port}`}
                </span>
              </div>
            )}
            <div className="flex items-center space-x-3">
              <FontAwesomeIcon icon={faDatabase} className="text-gray-400 w-4" />
              <span className="font-medium">Database:</span>
              <span className="text-gray-700">{escapeHtml(datasource.database)}</span>
            </div>
            {datasource.username && (
              <div className="flex items-center space-x-3">
                <FontAwesomeIcon icon={faUser} className="text-gray-400 w-4" />
                <span className="font-medium">Username:</span>
                <span className="text-gray-700">{escapeHtml(datasource.username)}</span>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="pt-4 border-t border-gray-200 flex justify-between items-center">
            <span className="text-sm text-gray-500">Created: {formatDate(datasource.created_at)}</span>
            <span className="text-blue-600 font-medium text-sm">Click to edit</span>
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
              <h1 className="text-3xl font-bold text-black">Data Sources</h1>
              <p className="text-gray-600 mt-2">Manage your database connections</p>
            </div>
            <div className="flex items-center">
              <button 
                onClick={handleAddDatasource}
                className="bg-black text-white rounded-lg px-6 py-3 font-medium transition-all duration-200 hover:bg-gray-800 hover:-translate-y-0.5 inline-flex items-center gap-2"
              >
                <FontAwesomeIcon icon={faPlus} />
                Add New Datasource
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
            <p className="mt-4 text-gray-600">Loading datasources...</p>
          </div>
        )}

        {/* Error State */}
        {error && !loading && (
          <div className="text-center py-12">
            <div className="text-red-500 text-4xl mb-4">
              <FontAwesomeIcon icon={faExclamationTriangle} />
            </div>
            <p className="text-red-600 font-semibold text-lg">Error loading datasources</p>
            <p className="text-gray-600 mt-2">{error}</p>
            <button 
              onClick={() => console.log('Retry clicked')}
              className="mt-6 bg-black text-white rounded-lg px-6 py-3 font-medium transition-all duration-200 hover:bg-gray-800 hover:-translate-y-0.5 inline-flex items-center gap-2"
            >
              <FontAwesomeIcon icon={faRedo} />
              Retry
            </button>
          </div>
        )}

        {/* Empty State */}
        {!loading && !error && datasources.length === 0 && (
          <div className="text-center py-16">
            <div className="text-gray-400 text-6xl mb-6">
              <FontAwesomeIcon icon={faDatabase} />
            </div>
            <h3 className="text-2xl font-semibold text-black mb-3">No Datasources Found</h3>
            <p className="text-gray-600 mb-8 max-w-md mx-auto">
              Get started by creating your first datasource to connect to your database
            </p>
            <button 
              onClick={handleAddDatasource}
              className="bg-black text-white rounded-lg px-6 py-3 font-medium transition-all duration-200 hover:bg-gray-800 hover:-translate-y-0.5 inline-flex items-center gap-2"
            >
              <FontAwesomeIcon icon={faPlus} />
              Create Your First Datasource
            </button>
          </div>
        )}

        {/* Datasources Grid */}
        {!loading && !error && datasources.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 pb-12">
            {datasources.map(renderDatasourceCard)}
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

export default DataSources;
