import React, { useState, useEffect } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faPlay, 
  faTrash, 
  faSave, 
  faArrowLeft, 
  faSpinner,
  faPlus,
  faTimes,
  faCheckCircle,
  faDownload
} from '@fortawesome/free-solid-svg-icons';

interface Tool {
  id?: string;
  name: string;
  description?: string;
  type: string;
  datasource_id: string;
  sql: string;
  parameters?: ToolParameter[];
  created_at?: string;
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

interface ExecutionResult {
  success: boolean;
  row_count?: number;
  execution_time_ms?: number;
  data?: any[];
  error?: string;
}

interface ToolEditProps {
  toolId?: string;
  onSave?: (tool: Tool) => void;
  onCancel?: () => void;
  onDelete?: (id: string) => void;
}

const ToolEdit: React.FC<ToolEditProps> = ({ toolId, onSave, onCancel, onDelete }) => {
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [executing, setExecuting] = useState(false);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [datasources, setDatasources] = useState<Datasource[]>([]);
  const [showExecuteModal, setShowExecuteModal] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [executionResults, setExecutionResults] = useState<ExecutionResult | null>(null);
  const [formData, setFormData] = useState<Tool>({
    name: '',
    description: '',
    type: '',
    datasource_id: '',
    sql: '',
    parameters: []
  });

  const isEditMode = !!toolId;

  useEffect(() => {
    loadDatasources();
    if (isEditMode && toolId) {
      loadTool(toolId);
    } else {
      setLoading(false);
    }
  }, [toolId, isEditMode]);

  const loadDatasources = async () => {
    try {
      // Mock datasources for now - replace with API call later
      const mockDatasources: Datasource[] = [
        { id: '1', name: 'Production PostgreSQL', database_type: 'postgresql' },
        { id: '2', name: 'Development MySQL', database_type: 'mysql' },
        { id: '3', name: 'Analytics Warehouse', database_type: 'snowflake' }
      ];
      setDatasources(mockDatasources);
    } catch (error) {
      showNotification('Failed to load datasources', 'warning');
    }
  };

  const loadTool = async (id: string) => {
    setLoading(true);
    try {
      // Mock tool data for now - replace with API call later
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const mockTool: Tool = {
        id: id,
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
      };
      
      setFormData(mockTool);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load tool';
      showNotification(errorMessage, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field: keyof Tool, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleParameterChange = (index: number, field: keyof ToolParameter, value: any) => {
    setFormData(prev => ({
      ...prev,
      parameters: prev.parameters?.map((param, i) => 
        i === index ? { ...param, [field]: value } : param
      ) || []
    }));
  };

  const addParameter = () => {
    const newParameter: ToolParameter = {
      name: '',
      type: 'string',
      description: '',
      required: false,
      default: ''
    };
    
    setFormData(prev => ({
      ...prev,
      parameters: [...(prev.parameters || []), newParameter]
    }));
  };

  const removeParameter = (index: number) => {
    setFormData(prev => ({
      ...prev,
      parameters: prev.parameters?.filter((_, i) => i !== index) || []
    }));
  };

  const validateForm = (): boolean => {
    if (!formData.name.trim()) {
      showNotification('Name is required', 'error');
      return false;
    }
    if (!formData.type) {
      showNotification('Tool type is required', 'error');
      return false;
    }
    if (!formData.sql.trim()) {
      showNotification('SQL query is required', 'error');
      return false;
    }
    if (!formData.datasource_id) {
      showNotification('Datasource is required', 'error');
      return false;
    }

    // Validate parameters
    const parameterNames = new Set<string>();
    for (const param of formData.parameters || []) {
      if (param.name.trim()) {
        if (parameterNames.has(param.name)) {
          showNotification('Duplicate parameter names are not allowed', 'error');
          return false;
        }
        parameterNames.add(param.name);
        
        if (!/^[a-zA-Z_][a-zA-Z0-9_]*$/.test(param.name)) {
          showNotification('Parameter names must start with a letter or underscore and contain only letters, numbers, and underscores', 'error');
          return false;
        }
      }
    }

    return true;
  };

  const handleSave = async () => {
    if (!validateForm()) return;

    setSaving(true);
    try {
      // Mock save - replace with API call later
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const toolToSave = {
        ...formData,
        parameters: formData.parameters?.filter(p => p.name.trim()) || []
      };
      
      if (onSave) {
        onSave(toolToSave);
      } else {
        showNotification(isEditMode ? 'Tool updated successfully' : 'Tool created successfully', 'success');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to save tool';
      showNotification(errorMessage, 'error');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!toolId) return;
    
    if (!window.confirm('Are you sure you want to delete this tool? This action cannot be undone.')) {
      return;
    }

    setDeleting(true);
    try {
      // Mock delete - replace with API call later
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      if (onDelete) {
        onDelete(toolId);
      } else {
        showNotification('Tool deleted successfully', 'success');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to delete tool';
      showNotification(errorMessage, 'error');
    } finally {
      setDeleting(false);
    }
  };

  const handleExecute = async () => {
    if (!isEditMode) {
      showNotification('Please save the tool first before executing it', 'warning');
      return;
    }

    setShowExecuteModal(true);
    setShowResults(false);
  };

  const executeTool = async (parameters: Record<string, any>) => {
    setExecuting(true);
    try {
      // Mock execution - replace with API call later
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const mockResults: ExecutionResult = {
        success: true,
        row_count: Math.floor(Math.random() * 100) + 10,
        execution_time_ms: Math.floor(Math.random() * 500) + 50,
        data: [
          { user_id: 1, action: 'login', created_at: '2024-01-15' },
          { user_id: 2, action: 'purchase', created_at: '2024-01-15' },
          { user_id: 3, action: 'logout', created_at: '2024-01-15' }
        ]
      };
      
      setExecutionResults(mockResults);
      setShowResults(true);
      showNotification(`Tool executed successfully! ${mockResults.row_count} rows returned`, 'success');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Tool execution failed';
      showNotification(errorMessage, 'error');
    } finally {
      setExecuting(false);
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

  const formatCellValue = (value: any) => {
    if (value === null || value === undefined) {
      return <span className="text-gray-400 italic">NULL</span>;
    }
    
    if (typeof value === 'boolean') {
      return value ? 
        <span className="text-green-600 font-semibold">TRUE</span> : 
        <span className="text-red-600 font-semibold">FALSE</span>;
    }
    
    if (typeof value === 'number') {
      return value % 1 === 0 ? value.toString() : value.toFixed(2);
    }
    
    if (typeof value === 'object') {
      return <code className="bg-gray-100 px-1 rounded text-xs">{JSON.stringify(value)}</code>;
    }
    
    const stringValue = String(value);
    if (stringValue.length > 100) {
      return <span title={stringValue}>{stringValue.substring(0, 100)}...</span>;
    }
    
    return stringValue;
  };

  const exportResultsToCSV = () => {
    if (!executionResults?.data) return;
    
    const headers = Object.keys(executionResults.data[0]);
    let csv = headers.map(header => `"${header}"`).join(',') + '\n';
    
    executionResults.data.forEach(row => {
      const values = headers.map(header => {
        const value = row[header];
        if (value === null || value === undefined) return '';
        if (typeof value === 'boolean') return value ? 'true' : 'false';
        return `"${String(value).replace(/"/g, '""')}"`;
      });
      csv += values.join(',') + '\n';
    });
    
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    
    const toolName = formData.name.replace(/[^a-zA-Z0-9]/g, '_');
    const timestamp = new Date().toISOString().slice(0, 19).replace(/[:-]/g, '');
    link.setAttribute('download', `${toolName}_results_${timestamp}.csv`);
    
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    showNotification('Results exported to CSV', 'success');
  };

  if (loading) {
    return (
      <div className="bg-white min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-black"></div>
          <p className="mt-4 text-gray-600">Loading tool...</p>
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
              {isEditMode ? 'Edit Tool' : 'Create New Tool'}
            </h2>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto p-6">
        <div className="bg-white border border-gray-200 rounded-lg p-8 shadow-sm">
          <form onSubmit={(e) => { e.preventDefault(); handleSave(); }}>
            {/* Form Actions */}
            <div className="flex justify-end space-x-4 pt-6 border-b border-gray-200 pb-6 mb-6">
              {isEditMode && (
                <>
                  <button 
                    type="button"
                    onClick={handleExecute}
                    className="bg-black text-white rounded-lg px-4 py-2 font-medium transition-all duration-200 hover:bg-gray-800 inline-flex items-center gap-2"
                  >
                    <FontAwesomeIcon icon={faPlay} />
                    Execute Tool
                  </button>
                  <button 
                    type="button"
                    onClick={handleDelete}
                    disabled={deleting}
                    className="bg-white text-black border border-gray-300 rounded-lg px-4 py-2 font-medium transition-all duration-200 hover:bg-gray-50 inline-flex items-center gap-2"
                  >
                    {deleting ? (
                      <FontAwesomeIcon icon={faSpinner} className="animate-spin" />
                    ) : (
                      <FontAwesomeIcon icon={faTrash} />
                    )}
                    {deleting ? 'Deleting...' : 'Delete Tool'}
                  </button>
                </>
              )}
              <button 
                type="button"
                onClick={onCancel}
                className="bg-white text-black border border-gray-300 rounded-lg px-4 py-2 font-medium transition-all duration-200 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button 
                type="submit"
                disabled={saving}
                className="bg-black text-white rounded-lg px-4 py-2 font-medium transition-all duration-200 hover:bg-gray-800 inline-flex items-center gap-2"
              >
                {saving ? (
                  <FontAwesomeIcon icon={faSpinner} className="animate-spin" />
                ) : (
                  <FontAwesomeIcon icon={faSave} />
                )}
                {saving ? 'Saving...' : (isEditMode ? 'Save Tool' : 'Create Tool')}
              </button>
            </div>

            {/* Basic Information */}
            <div className="mb-8">
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
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent"
                    placeholder="e.g., aws_cost_by_service"
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
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent"
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
                    value={formData.description || ''}
                    onChange={(e) => handleInputChange('description', e.target.value)}
                    rows={2}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent"
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
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent"
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
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent font-mono text-sm"
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
                  <button 
                    type="button"
                    onClick={addParameter}
                    className="bg-black text-white rounded-lg px-3 py-1 text-sm font-medium transition-all duration-200 hover:bg-gray-800 inline-flex items-center gap-2"
                  >
                    <FontAwesomeIcon icon={faPlus} />
                    Add Parameter
                  </button>
                </div>
                
                {formData.parameters && formData.parameters.length > 0 ? (
                  <div className="space-y-4">
                    {formData.parameters.map((param, index) => (
                      <div key={index} className="bg-gray-50 p-4 rounded-lg border">
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">Name</label>
                            <input 
                              type="text"
                              value={param.name}
                              onChange={(e) => handleParameterChange(index, 'name', e.target.value)}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent text-sm"
                              placeholder="param_name"
                            />
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">Type</label>
                            <select 
                              value={param.type}
                              onChange={(e) => handleParameterChange(index, 'type', e.target.value)}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent text-sm"
                            >
                              <option value="string">String</option>
                              <option value="integer">Integer</option>
                              <option value="float">Float</option>
                              <option value="boolean">Boolean</option>
                              <option value="date">Date</option>
                              <option value="datetime">DateTime</option>
                              <option value="array">Array</option>
                              <option value="object">Object</option>
                            </select>
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">Default Value</label>
                            <input 
                              type="text"
                              value={param.default || ''}
                              onChange={(e) => handleParameterChange(index, 'default', e.target.value)}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent text-sm"
                              placeholder="Optional"
                            />
                          </div>
                          <div className="flex items-end space-x-2">
                            <label className="flex items-center text-sm">
                              <input 
                                type="checkbox"
                                checked={param.required}
                                onChange={(e) => handleParameterChange(index, 'required', e.target.checked)}
                                className="mr-1"
                              />
                              Required
                            </label>
                            <button 
                              type="button"
                              onClick={() => removeParameter(index)}
                              className="text-red-500 hover:text-red-700 px-2 py-1 text-sm"
                            >
                              <FontAwesomeIcon icon={faTrash} />
                            </button>
                          </div>
                        </div>
                        <div className="mt-2">
                          <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                          <input 
                            type="text"
                            value={param.description || ''}
                            onChange={(e) => handleParameterChange(index, 'description', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent text-sm"
                            placeholder="Parameter description"
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-4 text-gray-500 bg-gray-50 rounded-md">
                    No parameters defined. Click "Add Parameter" to add one.
                  </div>
                )}
              </div>
            </div>
          </form>
        </div>
      </div>

      {/* Execute Tool Modal */}
      {showExecuteModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-screen overflow-y-auto">
            <div className="p-6">
              {/* Modal Header */}
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-xl font-bold text-black">Execute Tool</h3>
                <button 
                  onClick={() => setShowExecuteModal(false)}
                  className="text-gray-400 hover:text-gray-600 transition-colors"
                >
                  <FontAwesomeIcon icon={faTimes} className="text-xl" />
                </button>
              </div>

              {/* Tool Info */}
              <div className="mb-6 p-4 bg-gray-50 rounded-lg">
                <h4 className="font-semibold text-black">{formData.name}</h4>
                <p className="text-gray-600 text-sm mt-1">{formData.description || 'No description provided'}</p>
              </div>

              {/* Parameters Form */}
              {!showResults ? (
                <div>
                  <form onSubmit={(e) => { e.preventDefault(); executeTool({}); }}>
                    <div className="space-y-4 mb-6">
                      {formData.parameters && formData.parameters.length > 0 ? (
                        formData.parameters.map((param, index) => (
                          <div key={index} className="parameter-input-group">
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              {param.name}
                              {param.required && <span className="text-red-500"> *</span>}
                              {param.description && (
                                <span className="text-gray-500 font-normal"> - {param.description}</span>
                              )}
                            </label>
                            <input 
                              type="text"
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent"
                              placeholder={param.default ? `Default: ${param.default}` : ''}
                              defaultValue={param.default || ''}
                            />
                          </div>
                        ))
                      ) : (
                        <div className="text-center py-8 text-gray-500 bg-gray-50 rounded-lg">
                          <FontAwesomeIcon icon={faCheckCircle} className="text-2xl mb-2" />
                          <p>This tool has no parameters to configure.</p>
                        </div>
                      )}
                    </div>

                    {/* Modal Actions */}
                    <div className="flex justify-end space-x-4 pt-4 border-t border-gray-200">
                      <button 
                        type="button"
                        onClick={() => setShowExecuteModal(false)}
                        className="bg-white text-black border border-gray-300 rounded-lg px-4 py-2 font-medium transition-all duration-200 hover:bg-gray-50"
                      >
                        Cancel
                      </button>
                      <button 
                        type="submit"
                        disabled={executing}
                        className="bg-black text-white rounded-lg px-4 py-2 font-medium transition-all duration-200 hover:bg-gray-800 inline-flex items-center gap-2"
                      >
                        {executing ? (
                          <FontAwesomeIcon icon={faSpinner} className="animate-spin" />
                        ) : (
                          <FontAwesomeIcon icon={faPlay} />
                        )}
                        {executing ? 'Executing...' : 'Execute Tool'}
                      </button>
                    </div>
                  </form>
                </div>
              ) : (
                /* Results Section */
                <div>
                  <div className="border-t border-gray-200 pt-6">
                    {/* Execution Summary */}
                    {executionResults && (
                      <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                        <div className="flex items-center">
                          <FontAwesomeIcon icon={faCheckCircle} className="text-green-500 mr-2" />
                          <span className="font-semibold text-green-700">Execution Completed</span>
                        </div>
                        <div className="text-sm text-green-600 mt-1">
                          {executionResults.row_count} rows returned in {executionResults.execution_time_ms}ms
                        </div>
                      </div>
                    )}

                    {/* Results Table Container */}
                    <div className="mb-6">
                      <div className="flex justify-between items-center mb-3">
                        <h4 className="text-lg font-semibold text-black">Results</h4>
                        <div className="flex space-x-2">
                          <button 
                            onClick={exportResultsToCSV}
                            className="text-sm px-3 py-1 bg-blue-500 hover:bg-blue-600 text-white rounded transition-colors inline-flex items-center gap-1"
                          >
                            <FontAwesomeIcon icon={faDownload} />
                            Export CSV
                          </button>
                        </div>
                      </div>
                      
                      {executionResults?.data && executionResults.data.length > 0 ? (
                        <div className="border border-gray-200 rounded-lg overflow-hidden">
                          <div className="overflow-x-auto max-h-96">
                            <table className="w-full">
                              <thead className="bg-gray-50 sticky top-0">
                                <tr>
                                  {Object.keys(executionResults.data[0]).map(column => (
                                    <th key={column} className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider border-b border-gray-200">
                                      {column}
                                    </th>
                                  ))}
                                </tr>
                              </thead>
                              <tbody className="divide-y divide-gray-200">
                                {executionResults.data.map((row, rowIndex) => (
                                  <tr key={rowIndex} className={rowIndex % 2 === 0 ? 'bg-white' : 'bg-gray-50'} >
                                    {Object.values(row).map((value, colIndex) => (
                                      <td key={colIndex} className="px-4 py-3 text-sm text-gray-900 border-b border-gray-200">
                                        {formatCellValue(value)}
                                      </td>
                                    ))}
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        </div>
                      ) : (
                        <div className="text-center py-8 text-gray-500 bg-gray-50 rounded-lg">
                          <FontAwesomeIcon icon={faCheckCircle} className="text-2xl mb-2" />
                          <p>No data returned from the query.</p>
                        </div>
                      )}
                    </div>

                    {/* Results Actions */}
                    <div className="flex justify-between items-center pt-4 border-t border-gray-200">
                      <button 
                        onClick={() => setShowResults(false)}
                        className="bg-black text-white rounded-lg px-4 py-2 font-medium transition-all duration-200 hover:bg-gray-800 inline-flex items-center gap-2"
                      >
                        <FontAwesomeIcon icon={faPlay} />
                        Run Again
                      </button>
                      <button 
                        onClick={() => setShowExecuteModal(false)}
                        className="bg-white text-black border border-gray-300 rounded-lg px-4 py-2 font-medium transition-all duration-200 hover:bg-gray-50"
                      >
                        Close
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

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

export default ToolEdit;
