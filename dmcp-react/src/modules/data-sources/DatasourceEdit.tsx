import React, { useState, useEffect } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faPlug, 
  faTrash, 
  faSave,
  faArrowLeft,
  faSpinner
} from '@fortawesome/free-solid-svg-icons';

interface Datasource {
  id?: string;
  name: string;
  database_type: string;
  host?: string;
  port?: string;
  database: string;
  username?: string;
  password?: string;
  ssl_mode?: string;
  connection_string?: string;
  additional_params?: any;
  created_at?: string;
}

interface FieldConfig {
  name: string;
  required: boolean;
  type: string;
}

interface DatabaseConfig {
  fields: FieldConfig[];
  sections: Array<{ id: string; title: string }>;
}

interface Notification {
  id: string;
  message: string;
  type: 'success' | 'error' | 'info' | 'warning';
}

interface DatasourceEditProps {
  datasourceId?: string;
  onSave?: (datasource: Datasource) => void;
  onCancel?: () => void;
  onDelete?: (id: string) => void;
}

const DatasourceEdit: React.FC<DatasourceEditProps> = ({ 
  datasourceId, 
  onSave, 
  onCancel, 
  onDelete 
}) => {
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [fieldConfigs, setFieldConfigs] = useState<Record<string, DatabaseConfig>>({});
  
  const [formData, setFormData] = useState<Datasource>({
    name: '',
    database_type: '',
    host: '',
    port: '',
    database: '',
    username: '',
    password: '',
    ssl_mode: '',
    connection_string: '',
    additional_params: {}
  });

  const isEditMode = !!datasourceId;

  useEffect(() => {
    loadFieldConfigs();
    if (isEditMode && datasourceId) {
      loadDatasource(datasourceId);
    }
  }, [datasourceId, isEditMode]);

  const loadFieldConfigs = async () => {
    // Mock field configurations for now
    const configs: Record<string, DatabaseConfig> = {
      postgresql: {
        fields: [
          { name: 'host', required: true, type: 'text' },
          { name: 'port', required: true, type: 'number' },
          { name: 'database', required: true, type: 'text' },
          { name: 'username', required: true, type: 'text' },
          { name: 'password', required: true, type: 'password' },
          { name: 'ssl_mode', required: false, type: 'select' }
        ],
        sections: [{ id: 'postgresql-config', title: 'PostgreSQL Configuration' }]
      },
      mysql: {
        fields: [
          { name: 'host', required: true, type: 'text' },
          { name: 'port', required: true, type: 'number' },
          { name: 'database', required: true, type: 'text' },
          { name: 'username', required: true, type: 'text' },
          { name: 'password', required: true, type: 'password' }
        ],
        sections: [{ id: 'postgresql-config', title: 'MySQL Configuration' }]
      },
      sqlite: {
        fields: [
          { name: 'sqlite_database', required: true, type: 'text' }
        ],
        sections: [{ id: 'sqlite-config', title: 'SQLite Configuration' }]
      },
      databricks: {
        fields: [
          { name: 'databricks_host', required: true, type: 'text' },
          { name: 'http_path', required: true, type: 'text' },
          { name: 'databricks_token', required: true, type: 'password' },
          { name: 'catalog', required: false, type: 'text' },
          { name: 'schema', required: false, type: 'text' }
        ],
        sections: [{ id: 'databricks-config', title: 'Databricks Configuration' }]
      }
    };
    setFieldConfigs(configs);
  };

  const loadDatasource = async (id: string) => {
    setLoading(true);
    try {
      // Mock data for now - replace with API call later
      const mockData: Datasource = {
        id: id,
        name: 'Sample Database',
        database_type: 'postgresql',
        host: 'localhost',
        port: '5432',
        database: 'sample_db',
        username: 'admin',
        ssl_mode: 'require'
      };
      setFormData(mockData);
    } catch (error) {
      showNotification('Failed to load datasource', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleDatabaseTypeChange = (value: string) => {
    setFormData(prev => ({
      ...prev,
      database_type: value
    }));
  };

  const handleAdditionalParamsChange = (value: string) => {
    try {
      const parsed = value ? JSON.parse(value) : {};
      setFormData(prev => ({
        ...prev,
        additional_params: parsed
      }));
    } catch (e) {
      // Keep the raw value if it's not valid JSON
      setFormData(prev => ({
        ...prev,
        additional_params: value
      }));
    }
  };

  const validateForm = (): boolean => {
    if (!formData.name.trim()) {
      showNotification('Name is required', 'error');
      return false;
    }
    if (!formData.database_type) {
      showNotification('Database type is required', 'error');
      return false;
    }
    return true;
  };

  const handleSave = async () => {
    if (!validateForm()) return;

    setSaving(true);
    try {
      // Mock save - replace with API call later
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      if (onSave) {
        onSave(formData);
      } else {
        showNotification(
          isEditMode ? 'Datasource updated successfully' : 'Datasource created successfully', 
          'success'
        );
      }
    } catch (error) {
      showNotification('Failed to save datasource', 'error');
    } finally {
      setSaving(false);
    }
  };

  const handleTestConnection = async () => {
    if (!isEditMode) {
      showNotification('Please save the datasource first before testing the connection', 'warning');
      return;
    }

    setTesting(true);
    try {
      // Mock test - replace with API call later
      await new Promise(resolve => setTimeout(resolve, 1000));
      showNotification('Connection test successful! (150ms)', 'success');
    } catch (error) {
      showNotification('Connection test failed', 'error');
    } finally {
      setTesting(false);
    }
  };

  const handleDelete = async () => {
    if (!datasourceId) return;
    
    if (!window.confirm('Are you sure you want to delete this datasource? This action cannot be undone.')) {
      return;
    }

    setDeleting(true);
    try {
      // Mock delete - replace with API call later
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      if (onDelete) {
        onDelete(datasourceId);
      } else {
        showNotification('Datasource deleted successfully', 'success');
      }
    } catch (error) {
      showNotification('Failed to delete datasource', 'error');
    } finally {
      setDeleting(false);
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

  const getConfigSection = () => {
    if (!formData.database_type || !fieldConfigs[formData.database_type]) {
      return null;
    }

    const config = fieldConfigs[formData.database_type];
    const section = config.sections[0];

    switch (formData.database_type) {
      case 'sqlite':
        return (
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-black mb-4 border-b border-gray-200 pb-2">
              {section.title}
            </h2>
            <div className="grid grid-cols-1 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Database File Path <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={formData.database || ''}
                  onChange={(e) => handleInputChange('database', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-black"
                  placeholder="/path/to/database.db"
                />
                <p className="text-sm text-gray-500 mt-1">Path to the SQLite database file</p>
              </div>
            </div>
          </div>
        );

      case 'postgresql':
      case 'mysql':
        return (
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-black mb-4 border-b border-gray-200 pb-2">
              {section.title}
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Host <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={formData.host || ''}
                  onChange={(e) => handleInputChange('host', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-black"
                  placeholder="localhost"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Port <span className="text-red-500">*</span>
                </label>
                <input
                  type="number"
                  value={formData.port || ''}
                  onChange={(e) => handleInputChange('port', e.target.value)}
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
                  value={formData.database || ''}
                  onChange={(e) => handleInputChange('database', e.target.value)}
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
                  value={formData.username || ''}
                  onChange={(e) => handleInputChange('username', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-black"
                  placeholder="myuser"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Password <span className="text-red-500">*</span>
                </label>
                <input
                  type="password"
                  value={formData.password || ''}
                  onChange={(e) => handleInputChange('password', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-black"
                  placeholder="mypassword"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  SSL Mode
                </label>
                <select
                  value={formData.ssl_mode || ''}
                  onChange={(e) => handleInputChange('ssl_mode', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-black"
                >
                  <option value="">None</option>
                  <option value="require">Require</option>
                  <option value="verify-ca">Verify CA</option>
                  <option value="verify-full">Verify Full</option>
                </select>
              </div>
            </div>
          </div>
        );

      case 'databricks':
        return (
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-black mb-4 border-b border-gray-200 pb-2">
              {section.title}
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Workspace URL <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={formData.host || ''}
                  onChange={(e) => handleInputChange('host', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-black"
                  placeholder="https://your-workspace.cloud.databricks.com"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  HTTP Path <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={formData.additional_params?.http_path || ''}
                  onChange={(e) => handleInputChange('http_path', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-black"
                  placeholder="/sql/1.0/warehouses/default"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Access Token <span className="text-red-500">*</span>
                </label>
                <input
                  type="password"
                  value={formData.password || ''}
                  onChange={(e) => handleInputChange('password', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-black"
                  placeholder="dapi..."
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Catalog
                </label>
                <input
                  type="text"
                  value={formData.additional_params?.catalog || ''}
                  onChange={(e) => handleInputChange('catalog', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-black"
                  placeholder="hive_metastore"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Schema
                </label>
                <input
                  type="text"
                  value={formData.additional_params?.schema || ''}
                  onChange={(e) => handleInputChange('schema', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-black"
                  placeholder="default"
                />
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  if (loading) {
    return (
      <div className="bg-white min-h-screen">
        <div className="max-w-4xl mx-auto p-6">
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-black"></div>
            <p className="mt-4 text-gray-600">Loading datasource...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white min-h-screen">
      {/* Page Header */}
      <div className="border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center space-x-4">
            <h2 className="text-2xl font-bold text-black">
              {isEditMode ? 'Edit Datasource' : 'Create New Datasource'}
            </h2>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto p-6">
        <div className="bg-white border border-gray-200 rounded-lg shadow-sm p-8">
          <form onSubmit={(e) => { e.preventDefault(); handleSave(); }}>
            {/* Form Actions */}
            <div className="flex justify-end space-x-4 pt-6 border-b border-gray-200 mb-6 pb-6">
              <button
                type="button"
                onClick={handleTestConnection}
                disabled={testing || !isEditMode}
                className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500 disabled:opacity-50"
              >
                {testing ? (
                  <FontAwesomeIcon icon={faSpinner} className="animate-spin mr-2" />
                ) : (
                  <FontAwesomeIcon icon={faPlug} className="mr-2" />
                )}
                {testing ? 'Testing...' : 'Test Connection'}
              </button>
              
              {isEditMode && (
                <button
                  type="button"
                  onClick={handleDelete}
                  disabled={deleting}
                  className="px-4 py-2 text-red-700 bg-red-100 rounded-md hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-red-500 disabled:opacity-50"
                >
                  {deleting ? (
                    <FontAwesomeIcon icon={faSpinner} className="animate-spin mr-2" />
                  ) : (
                    <FontAwesomeIcon icon={faTrash} className="mr-2" />
                  )}
                  {deleting ? 'Deleting...' : 'Delete Datasource'}
                </button>
              )}
              
              <button
                type="button"
                onClick={onCancel}
                className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500"
              >
                Cancel
              </button>
              
              <button
                type="submit"
                disabled={saving}
                className="px-4 py-2 bg-black text-white rounded-md hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-black disabled:opacity-50"
              >
                {saving ? (
                  <FontAwesomeIcon icon={faSpinner} className="animate-spin mr-2" />
                ) : (
                  <FontAwesomeIcon icon={faSave} className="mr-2" />
                )}
                {saving ? 'Saving...' : (isEditMode ? 'Update Datasource' : 'Create Datasource')}
              </button>
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
                    onChange={(e) => handleDatabaseTypeChange(e.target.value)}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-black"
                  >
                    <option value="">Select database type</option>
                    <option value="postgresql">PostgreSQL</option>
                    <option value="mysql">MySQL</option>
                    <option value="sqlite">SQLite</option>
                    <option value="databricks">Databricks</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Database-specific Configuration */}
            {getConfigSection()}

            {/* Advanced Options */}
            <div className="mb-8">
              <h2 className="text-xl font-semibold text-black mb-4 border-b border-gray-200 pb-2">
                Advanced Options
              </h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Connection String (Optional)
                  </label>
                  <input
                    type="text"
                    value={formData.connection_string || ''}
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
                    value={''
                      // typeof formData.additional_params === 'string' 
                      // ? formData.additional_params 
                      // : JSON.stringify(formData.additional_params || {}, null, 2)
                    }
                    onChange={(e) => handleAdditionalParamsChange(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-black"
                    rows={4}
                    placeholder='{"key": "value"}'
                  />
                  <p className="text-sm text-gray-500 mt-1">
                    Additional connection parameters in JSON format
                  </p>
                </div>
              </div>
            </div>
          </form>
        </div>
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

export default DatasourceEdit;
