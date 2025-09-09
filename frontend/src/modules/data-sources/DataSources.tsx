'use client';

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { apiService, DataSource, ApiError } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import {
  Plus,
  Eye,
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
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [dataSourceToDelete, setDataSourceToDelete] = useState<DataSource | null>(null);


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



  const handleDeleteClick = (dataSource: DataSource) => {
    setDataSourceToDelete(dataSource);
    setShowDeleteDialog(true);
  };

  const handleDeleteConfirm = async () => {
    if (!token || !dataSourceToDelete) return;
    
    try {
      setError(null);
      const response = await apiService.deleteDataSource(token, dataSourceToDelete.id);
      if (response.success) {
        setDataSources(prev => prev.filter(ds => ds.id !== dataSourceToDelete.id));
        setShowDeleteDialog(false);
        setDataSourceToDelete(null);
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

  const handleDeleteCancel = () => {
    setShowDeleteDialog(false);
    setDataSourceToDelete(null);
  };




  return (
    <div className="p-4">
          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
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

          {/* Data Sources Overview */}
          <div className="bg-white rounded-lg border border-gray-200 p-4 mb-4">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                <Eye className="w-5 h-5 text-[#FEBF23]" />
                <h3 className="text-lg font-semibold text-gray-900">Data Sources Overview</h3>
              </div>
              <Button 
                onClick={handleAddDataSource} 
                className="flex items-center space-x-2 bg-[#FEBF23] hover:bg-[#FEBF23]/90 text-black border border-[#FEBF23] px-4 py-2"
              >
                <Plus className="w-4 h-4" />
                <span>Add New Data Source</span>
              </Button>
            </div>
            <p className="text-gray-600 mb-4">
              Manage your connected data sources and monitor their status.
              <a href="https://dmcp.opsloom.io/configure-datasources.html" target="_blank" rel="noopener noreferrer" className="text-[#FEBF23] hover:text-[#FEBF23]/80 ml-1 underline font-medium">
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
          <div className="bg-white rounded-lg border border-gray-200 mb-4">
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
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                  {dataSources.map((dataSource) => (
                    <div key={dataSource.id} className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center space-x-2">
                          <div className="w-8 h-8 bg-[#FEBF23]/20 rounded flex items-center justify-center">
                            <Database className="w-4 h-4 text-[#FEBF23]" />
                          </div>
                          <div>
                            <h3 className="font-medium text-gray-900 text-sm truncate">{dataSource.name}</h3>
                          </div>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDeleteClick(dataSource)}
                          className="text-gray-400 hover:text-red-600 hover:bg-red-50 p-1 h-6 w-6"
                        >
                          <Trash2 className="w-3 h-3" />
                        </Button>
                      </div>
                      
                      <div className="space-y-2">
                        {dataSource.database && (
                          <div className="text-xs text-gray-600 truncate">
                            Database: {dataSource.database}
                          </div>
                        )}
                        
                        <div className="flex items-center justify-end space-x-2">
                          <Badge variant="secondary" className="text-xs capitalize">
                            {dataSource.database_type}
                          </Badge>
                          <Badge variant="secondary" className="text-xs bg-green-100 text-green-800">
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

          {/* Delete Confirmation Dialog */}
          <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
            <DialogContent className="sm:max-w-md">
              <DialogHeader>
                <DialogTitle>Delete Data Source</DialogTitle>
                <DialogDescription>
                  Are you sure you want to delete "{dataSourceToDelete?.name}"? This action cannot be undone.
                </DialogDescription>
              </DialogHeader>
              <DialogFooter className="flex space-x-2">
                <Button
                  variant="outline"
                  onClick={handleDeleteCancel}
                  className="text-gray-700 bg-gray-100 hover:bg-gray-200"
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleDeleteConfirm}
                  className="bg-red-600 hover:bg-red-700 text-white"
                >
                  Delete
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
  );
};

export default DataSources;
