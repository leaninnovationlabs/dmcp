'use client';

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { apiService, DataSource, ApiError } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import {
  Plus,
  Eye,
  Edit,
  Trash2,
  RefreshCw,
  Database
} from 'lucide-react';

interface DataSourcesProps {}

const DataSources = ({}: DataSourcesProps) => {
  const navigate = useNavigate();
  const { token } = useAuth();
  const [dataSources, setDataSources] = useState<DataSource[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);


  // Fetch datasources on component mount
  useEffect(() => {
    const fetchDataSources = async () => {
      console.log('Fetching datasources, token:', token ? 'exists' : 'missing');
      
      if (!token) {
        console.log('No token available, skipping fetch');
        setLoading(false);
        return;
      }
      
      try {
        setLoading(true);
        setError(null);
        console.log('Making API call to fetch datasources...');
        const response = await apiService.getDataSources(token);
        console.log('API response:', response);
        
        if (response.success && response.data) {
          setDataSources(response.data);
          console.log('Datasources loaded:', response.data.length);
        } else {
          setError('Failed to fetch datasources');
          console.error('Failed response:', response);
        }
      } catch (err) {
        console.error('Error fetching datasources:', err);
        if (err instanceof ApiError) {
          setError(err.message);
        } else {
          setError('An unexpected error occurred');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchDataSources();
  }, [token]);


  const handleAddDataSource = () => {
    navigate('/data-sources/create');
  };

  const handleEditDataSource = (dataSource: DataSource) => {
    navigate(`/data-sources/edit/${dataSource.id}`);
  };


  const handleDeleteDataSource = async (id: number) => {
    if (!token) return;
    
    try {
      setError(null);
      const response = await apiService.deleteDataSource(token, id);
      if (response.success) {
        setDataSources(prev => prev.filter(ds => ds.id !== id));
      } else {
        setError('Failed to delete datasource');
      }
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('An unexpected error occurred');
      }
    }
  };




  return (
    <div className="p-4 pt-8">
          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
              <div className="flex items-center">
                <div className="text-red-600 text-sm">{error}</div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setError(null)}
                  className="ml-auto text-red-600 hover:text-red-700"
                >
                  ×
                </Button>
              </div>
            </div>
          )}

          {/* Action Buttons Row */}
          <div className="flex items-center space-x-4 mb-6">
            <Button onClick={handleAddDataSource} className="flex flex-col items-center space-y-2 bg-[#FEBF23] hover:bg-[#FEBF23]/90 text-black border border-[#FEBF23] px-6 py-4 h-auto">
              <Plus className="w-5 h-5" />
              <span className="text-sm">Add New Data Source</span>
            </Button>
          </div>

          {/* Data Sources Overview */}
          <div className="bg-white rounded-lg border border-gray-200 p-4 mb-6">
            <div className="flex items-center space-x-2 mb-2">
              <Eye className="w-5 h-5 text-[#FEBF23]" />
              <h3 className="text-lg font-semibold text-gray-900">Data Sources Overview</h3>
            </div>
            <p className="text-gray-600 mb-3">
              Manage your connected data sources and monitor their status.
              <a href="#" className="text-[#FEBF23] hover:text-[#FEBF23]/80 ml-1 underline font-medium">
                View documentation
              </a>
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-[#FEBF23]/10 rounded-lg p-3 border border-[#FEBF23]/20">
                <div className="flex items-center space-x-2">
                  <Database className="w-4 h-4 text-[#FEBF23]" />
                  <span className="text-sm font-medium text-gray-700">Total Sources</span>
                </div>
                <p className="text-2xl font-bold text-gray-900 mt-1">{loading ? '...' : dataSources.length}</p>
              </div>
              <div className="bg-[#FEBF23]/10 rounded-lg p-3 border border-[#FEBF23]/20">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="text-sm font-medium text-gray-700">Connected</span>
                </div>
                <p className="text-2xl font-bold text-gray-900 mt-1">{loading ? '...' : dataSources.length}</p>
              </div>
              <div className="bg-[#FEBF23]/10 rounded-lg p-3 border border-[#FEBF23]/20">
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
              {loading ? (
                <div className="flex items-center justify-center py-8">
                  <RefreshCw className="w-6 h-6 animate-spin text-gray-500" />
                  <span className="ml-2 text-gray-500">Loading datasources...</span>
                </div>
              ) : dataSources.length === 0 ? (
                <div className="text-center py-8">
                  <Database className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No datasources found</h3>
                  <p className="text-gray-500 mb-4">Get started by adding your first datasource.</p>
                  <Button onClick={handleAddDataSource} className="bg-[#FEBF23] hover:bg-[#FEBF23]/90 text-black">
                    <Plus className="w-4 h-4 mr-2" />
                    Add Datasource
                  </Button>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {dataSources.map((dataSource) => (
                    <div key={dataSource.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center space-x-2">
                          <div className="w-8 h-8 bg-[#FEBF23]/20 rounded flex items-center justify-center">
                            <Database className="w-4 h-4 text-[#FEBF23]" />
                          </div>
                          <div>
                            <h4 className="font-medium text-gray-900">{dataSource.name}</h4>
                            <p className="text-sm text-gray-500 capitalize">{dataSource.database_type}</p>
                          </div>
                        </div>
                        <div className="flex space-x-1">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleEditDataSource(dataSource)}
                            className="text-gray-500 hover:text-gray-700"
                          >
                            <Edit className="w-4 h-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDeleteDataSource(dataSource.id)}
                            className="text-gray-500 hover:text-red-600"
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                      <div className="space-y-2 text-sm text-gray-600">
                        <div className="flex justify-between">
                          <span>Host:</span>
                          <span className="font-mono">{dataSource.host}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Port:</span>
                          <span className="font-mono">{dataSource.port}</span>
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
              )}
            </div>
          </div>
        </div>
  );
};

export default DataSources;
