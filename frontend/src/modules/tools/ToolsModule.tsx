"use client";

import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import DeleteConfirmationDialog from "./DeleteConfirmationDialog";
import CreateToolForm from "./CreateToolForm";
import { apiService, ApiError } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "sonner";
import {
  Plus,
  Wrench,
  Trash2,
} from "lucide-react";

interface ToolItem {
  id: string;
  name: string;
  description: string;
  type: string;
  datasource_id: string;
  sql: string;
  parameters?: ToolParameter[];
}

interface ToolParameter {
  name: string;
  type: string;
  description?: string;
  required: boolean;
  default?: string;
}


interface Datasource {
  id: number;
  name: string;
  database_type: string;
}

interface ToolsModuleProps {
  onModuleChange?: () => void;
  sidebarCollapsed?: boolean;
  onToggleSidebar?: () => void;
  editingTool?: ToolItem | null;
}

const ToolsModule = ({
  onModuleChange: _onModuleChange,
  sidebarCollapsed: _sidebarCollapsed,
  onToggleSidebar: _onToggleSidebar,
  editingTool: propEditingTool,
}: ToolsModuleProps) => {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [showCreateForm, setShowCreateForm] = useState(propEditingTool !== undefined);
  const [editingTool, setEditingTool] = useState<ToolItem | null>(propEditingTool || null);
  const [tools, setTools] = useState<ToolItem[]>([]);
  const [datasources, setDatasources] = useState<Datasource[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [toolToDelete, setToolToDelete] = useState<string | null>(null);

  // Fetch tools and datasources from API
  useEffect(() => {
    const fetchData = async () => {
      if (!token) {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);

        // Fetch tools and datasources in parallel
        const [toolsResponse, datasourcesResponse] = await Promise.all([
          apiService.getTools(token),
          apiService.getDataSources(token),
        ]);

        if (toolsResponse.success && toolsResponse.data) {
          setTools(toolsResponse.data);
        } else {
          setError("Failed to fetch tools");
          toast.error("Failed to fetch tools");
        }

        if (datasourcesResponse.success && datasourcesResponse.data) {
          setDatasources(datasourcesResponse.data);
        } else {
          setError("Failed to fetch datasources");
          toast.error("Failed to fetch datasources");
        }
      } catch (err) {
        console.error("Error fetching data:", err);
        if (err instanceof ApiError) {
          setError(err.message);
          toast.error(err.message);
        } else {
          setError("An unexpected error occurred");
          toast.error("An unexpected error occurred");
        }
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [token]);


  const getDatasourceName = (datasourceId: string) => {
    const datasource = datasources.find(
      (ds) => ds.id === parseInt(datasourceId)
    );
    return datasource ? datasource.name : `Datasource #${datasourceId}`;
  };

  const handleAddTool = () => {
    navigate("/tools/create");
  };

  const handleEditTool = (tool: ToolItem) => {
    navigate(`/tools/${tool.id}`);
  };

  const handleCancelForm = () => {
    // If we're in a dedicated page (create or edit), navigate back to tools list
    if (propEditingTool !== undefined) {
      navigate("/tools");
      return;
    }
    
    setShowCreateForm(false);
    setEditingTool(null);
  };

  const handleSaveTool = async (tool: ToolItem) => {
    // Show success notification
    const isEdit = !!editingTool;
    toast.success(
      isEdit
        ? `Tool "${tool.name}" updated successfully!`
        : `Tool "${tool.name}" created successfully!`
    );

    // If we're in a dedicated page (create or edit), navigate appropriately
    if (propEditingTool !== undefined) {
      if (isEdit) {
        // Editing existing tool - stay on edit page
        navigate(`/tools/${tool.id}`);
      } else {
        // Creating new tool - go to edit page of new tool
        navigate(`/tools/${tool.id}`);
      }
      return;
    }

    // Refresh the data after saving
    if (token) {
      try {
        // Trigger tools refresh from API
        await apiService.refreshTools(token);
      } catch (err) {
        console.error("Error refreshing tools after save:", err);
        // Show warning about refresh failure but don't fail the save
        toast.warning(
          "Tool saved but refresh failed. Please refresh the page to see changes."
        );
      }
      await fetchData();
    }

    // Keep form open instead of closing automatically
    // User can manually close or create another tool
  };

  const handleDeleteClick = (toolId: string) => {
    setToolToDelete(toolId);
    setShowDeleteDialog(true);
  };

  const handleToolDeleted = (toolId: string) => {
    setTools((prev) => prev.filter((tool) => tool.id !== toolId));
  };

  const handleDeleteConfirm = async () => {
    if (!token || !toolToDelete) return;

    try {
      setLoading(true);
      const response = await apiService.deleteTool(
        token,
        parseInt(toolToDelete)
      );

      if (response.success) {
        setTools((prev) => prev.filter((tool) => tool.id !== toolToDelete));
        setShowDeleteDialog(false);
        setToolToDelete(null);
        toast.success("Tool deleted successfully");
      } else {
        toast.error("Failed to delete tool");
      }
    } catch (err) {
      console.error("Error deleting tool:", err);
      if (err instanceof ApiError) {
        toast.error(err.message);
      } else {
        toast.error("An unexpected error occurred");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteCancel = () => {
    setShowDeleteDialog(false);
    setToolToDelete(null);
  };

  const fetchData = async () => {
    if (!token) return;

    try {
      const [toolsResponse, datasourcesResponse] = await Promise.all([
        apiService.getTools(token),
        apiService.getDataSources(token),
      ]);

      if (toolsResponse.success && toolsResponse.data) {
        setTools(toolsResponse.data);
      }

      if (datasourcesResponse.success && datasourcesResponse.data) {
        setDatasources(datasourcesResponse.data);
      }
    } catch (err) {
      console.error("Error fetching data:", err);
    }
  };


  if (showCreateForm) {
    return (
      <CreateToolForm
        tool={editingTool}
        datasources={datasources}
        onSave={handleSaveTool}
        onCancel={handleCancelForm}
        onDelete={handleToolDeleted}
        navigate={navigate}
      />
    );
  }

  // Render Methods
  const renderToolsOverview = () => (
    <div className="bg-white rounded-lg border border-gray-200 p-4 mb-4 flex-shrink-0">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Wrench className="w-5 h-5 text-primary" />
          <h3 className="text-lg font-semibold text-gray-900">
            Tools Overview
          </h3>
        </div>
        <Button
          onClick={handleAddTool}
          className="flex items-center space-x-2 bg-primary hover:bg-primary/90 text-primary-foreground border border-primary px-4 py-2"
        >
          <Plus className="w-4 h-4" />
          <span>Add New Tool</span>
        </Button>
      </div>
      <p className="text-gray-600">
        Manage your development and productivity tools.
        <a
          href="https://dmcp.opsloom.io/create-tools.html"
          target="_blank"
          rel="noopener noreferrer"
          className="text-primary hover:text-primary/80 ml-1 underline font-medium"
        >
          View documentation
        </a>
      </p>
    </div>
  );

  const renderError = () => (
    error && (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4 flex-shrink-0">
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
    )
  );

  const renderToolsTable = () => (
    <div className="flex-1 flex flex-col overflow-hidden">
      <div className="overflow-auto flex-1">
        <table className="w-full">
          <thead className="bg-gray-50 sticky top-0 z-10">
            <tr className="border-b border-gray-200">
              <th className="text-left py-3 px-4 font-medium text-gray-900">
                Name
              </th>
              <th className="text-left py-3 px-4 font-medium text-gray-900">
                Type
              </th>
              <th className="text-left py-3 px-4 font-medium text-gray-900">
                Description
              </th>
              <th className="text-left py-3 px-4 font-medium text-gray-900">
                Data Source
              </th>
              <th className="text-right py-3 px-4 font-medium text-gray-900">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {tools.map((tool) => (
              <tr key={tool.id} className="hover:bg-gray-50">
                <td className="py-4 px-4">
                  <div className="font-medium text-gray-900">{tool.name}</div>
                </td>
                <td className="py-4 px-4">
                  <span
                    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      tool.type === "query"
                        ? "bg-blue-100 text-blue-800"
                        : tool.type === "http"
                        ? "bg-green-100 text-green-800"
                        : "bg-purple-100 text-purple-800"
                    }`}
                  >
                    {tool.type.toUpperCase()}
                  </span>
                </td>
                <td className="py-4 px-4">
                  <div className="text-gray-600 text-sm max-w-xs truncate">
                    {tool.description || "No description"}
                  </div>
                </td>
                <td className="py-4 px-4">
                  <div className="text-gray-600 text-sm">
                    {getDatasourceName(tool.datasource_id)}
                  </div>
                </td>
                <td className="py-4 px-4 text-right">
                  <div className="flex items-center justify-end space-x-2">
                    <Button
                      onClick={() => handleEditTool(tool)}
                      variant="ghost"
                      size="sm"
                      className="text-blue-600 hover:text-blue-700 hover:bg-blue-50"
                    >
                      <svg
                        className="w-4 h-4"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                        />
                      </svg>
                    </Button>
                    <Button
                      onClick={() => handleDeleteClick(tool.id)}
                      variant="ghost"
                      size="sm"
                      className="text-red-600 hover:text-red-700 hover:bg-red-50"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  const renderToolsList = () => (
    <div className="bg-white rounded-lg border border-gray-200 flex-1 flex flex-col min-h-0">
      <div className="p-6 flex-shrink-0">
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          Manage and execute your database tools
        </h2>
      </div>

      <div className="flex-1 flex flex-col px-6 pb-6 min-h-0">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
            <span className="ml-3 text-gray-600">Loading tools...</span>
          </div>
        ) : tools.length === 0 ? (
          <div className="text-center py-12">
            <Wrench className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No Tools Found
            </h3>
            <p className="text-gray-500 mb-4">
              Create your first tool to get started with database management
            </p>
            <Button
              onClick={handleAddTool}
              className="bg-primary hover:bg-primary/90 text-primary-foreground"
            >
              <Plus className="w-4 h-4 mr-2" />
              Create Your First Tool
            </Button>
          </div>
        ) : (
          renderToolsTable()
        )}
      </div>
    </div>
  );

  const renderDeleteDialog = () => (
    <DeleteConfirmationDialog
      open={showDeleteDialog}
      onOpenChange={setShowDeleteDialog}
      onConfirm={handleDeleteConfirm}
      onCancel={handleDeleteCancel}
      loading={loading}
    />
  );

  return (
    <div className="h-full flex flex-col bg-gray-50 overflow-hidden">
      <div className="p-4 flex-1 flex flex-col min-h-0">
        {renderToolsOverview()}
        {renderError()}
        {renderToolsList()}
      </div>
      {renderDeleteDialog()}
    </div>
  );
};


export default ToolsModule;
