"use client";

import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { apiService, ApiError } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "sonner";
import {
  Plus,
  Eye,
  Edit,
  Wrench,
  Trash2,
  CheckCircle,
  Download,
  RotateCcw,
  X,
  Minus,
  Play,
} from "lucide-react";

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

interface ExecutionResult {
  success: boolean;
  rows?: any[];
  rowCount?: number;
  executionTime?: number;
  error?: string;
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
}

const ToolsModule = ({
  onModuleChange: _onModuleChange,
  sidebarCollapsed: _sidebarCollapsed,
  onToggleSidebar: _onToggleSidebar,
}: ToolsModuleProps) => {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingTool, setEditingTool] = useState<ToolItem | null>(null);
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

  const getToolTypeColor = (toolType: string) => {
    switch (toolType) {
      case "query":
        return "bg-gray-100 text-gray-800";
      case "http":
        return "bg-gray-100 text-gray-800";
      case "code":
        return "bg-gray-100 text-gray-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getDatasourceName = (datasourceId: string) => {
    const datasource = datasources.find(
      (ds) => ds.id === parseInt(datasourceId)
    );
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

  const handleSaveTool = async (_tool: ToolItem) => {
    // Refresh the data after saving
    if (token) {
      try {
        // Trigger tools refresh from API
        await apiService.refreshTools(token);
      } catch (err) {
        console.error('Error refreshing tools after save:', err);
      }
      await fetchData();
    }
    setShowCreateForm(false);
    setEditingTool(null);
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

  return (
    <div className="h-full flex flex-col bg-gray-50 overflow-hidden">
      <div className="p-4 flex-1 flex flex-col min-h-0">
        {/* Tools Overview */}
        <div className="bg-white rounded-lg border border-gray-200 p-4 mb-4 flex-shrink-0">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <Eye className="w-5 h-5 text-[#FEBF23]" />
              <h3 className="text-lg font-semibold text-gray-900">
                Tools Overview
              </h3>
            </div>
            <Button
              onClick={handleAddTool}
              className="flex items-center space-x-2 bg-[#FEBF23] hover:bg-[#FEBF23]/90 text-black border border-[#FEBF23] px-4 py-2"
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
              className="text-[#FEBF23] hover:text-[#FEBF23]/80 ml-1 underline font-medium"
            >
              View documentation
            </a>
          </p>
        </div>

        {/* Error Message */}
        {error && (
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
        )}

        {/* Tools List */}
        <div className="bg-white rounded-lg border border-gray-200 flex-1 flex flex-col min-h-0">
          <div className="p-6 flex-shrink-0">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
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
                  className="bg-[#FEBF23] hover:bg-[#FEBF23]/90 text-black"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Create Your First Tool
                </Button>
              </div>
            ) : (
              /* Tools Table */
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
                          Datasource
                        </th>
                        <th className="text-left py-3 px-4 font-medium text-gray-900">
                          Actions
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {tools.map((tool) => (
                        <tr
                          key={tool.id}
                          className="border-b border-gray-100 hover:bg-gray-50"
                        >
                          <td className="py-3 px-4">
                            <span className="text-gray-900">{tool.name}</span>
                          </td>
                          <td className="py-3 px-4">
                            <Badge className={getToolTypeColor(tool.type)}>
                              {tool.type.toUpperCase()}
                            </Badge>
                          </td>
                          <td className="py-3 px-4">
                            <span className="text-sm text-gray-600 max-w-xs truncate block">
                              {tool.description || "No description"}
                            </span>
                          </td>
                          <td className="py-3 px-4">
                            <span className="text-sm text-gray-600">
                              {getDatasourceName(tool.datasource_id)}
                            </span>
                          </td>
                          <td className="py-3 px-4">
                            <div className="flex space-x-1">
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleEditTool(tool)}
                                className="text-gray-500 hover:text-black hover:bg-[#FEBF23] p-1"
                                title="Edit Tool"
                              >
                                <Edit className="w-4 h-4" />
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleDeleteClick(tool.id)}
                                className="text-gray-500 hover:text-red-600 hover:bg-[#FEBF23] p-1"
                                title="Delete Tool"
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
            )}
          </div>
        </div>
      </div>

      {/* Delete Confirmation Dialog */}
      <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Tool</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete this tool? This action cannot be
              undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={handleDeleteCancel}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleDeleteConfirm}
              disabled={loading}
            >
              {loading ? "Deleting..." : "Delete"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

// Create Tool Form Component
interface CreateToolFormProps {
  tool?: ToolItem | null;
  datasources: Datasource[];
  onSave: (tool: ToolItem) => void;
  onCancel: () => void;
  onDelete?: (toolId: string) => void;
  navigate: (path: string) => void;
}

const CreateToolForm = ({
  tool,
  datasources,
  onSave,
  onCancel,
  onDelete,
  navigate: _navigate,
}: CreateToolFormProps) => {
  const { token } = useAuth();
  const [formData, setFormData] = useState({
    name: tool?.name || "",
    description: tool?.description || "",
    type: tool?.type || "",
    datasource_id: tool?.datasource_id || "",
    sql: tool?.sql || "",
    parameters: tool?.parameters || [],
  });
  const [loading, setLoading] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [showExecuteDialog, setShowExecuteDialog] = useState(false);
  const [executionResult, setExecutionResult] =
    useState<ExecutionResult | null>(null);
  const [executing, setExecuting] = useState(false);
  const [parameterValues, setParameterValues] = useState<
    Record<string, string>
  >({});
  const [showParameterForm, setShowParameterForm] = useState(false);
  const [editingParameterIndex, setEditingParameterIndex] = useState<
    number | null
  >(null);
  const [parameterFormData, setParameterFormData] = useState({
    name: "",
    type: "string",
    description: "",
    default: "",
    required: false,
  });

  const isEditMode = !!tool;

  const handleInputChange = (field: string, value: string) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleAddParameter = () => {
    setParameterFormData({
      name: "",
      type: "string",
      description: "",
      default: "",
      required: false,
    });
    setEditingParameterIndex(null);
    setShowParameterForm(true);
  };

  const handleEditParameter = (index: number) => {
    const parameter = formData.parameters[index];
    setParameterFormData({
      name: parameter.name,
      type: parameter.type,
      description: parameter.description || "",
      default: parameter.default || "",
      required: parameter.required,
    });
    setEditingParameterIndex(index);
    setShowParameterForm(true);
  };

  const handleParameterFormChange = (
    field: string,
    value: string | boolean
  ) => {
    setParameterFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleSaveParameter = () => {
    if (!parameterFormData.name.trim()) {
      toast.error("Parameter name is required");
      return;
    }

    const updatedParameter: ToolParameter = {
      name: parameterFormData.name.trim(),
      type: parameterFormData.type,
      description: parameterFormData.description.trim() || undefined,
      required: parameterFormData.required,
      default: parameterFormData.default.trim() || undefined,
    };

    setFormData((prev) => {
      if (editingParameterIndex !== null) {
        // Edit existing parameter
        const updatedParameters = [...prev.parameters];
        updatedParameters[editingParameterIndex] = updatedParameter;
        return {
          ...prev,
          parameters: updatedParameters,
        };
      } else {
        // Add new parameter
        return {
          ...prev,
          parameters: [...prev.parameters, updatedParameter],
        };
      }
    });

    setShowParameterForm(false);
    setEditingParameterIndex(null);
    setParameterFormData({
      name: "",
      type: "string",
      description: "",
      default: "",
      required: false,
    });
  };

  const handleCancelParameter = () => {
    setShowParameterForm(false);
    setEditingParameterIndex(null);
    setParameterFormData({
      name: "",
      type: "string",
      description: "",
      default: "",
      required: false,
    });
  };

  const handleRemoveParameter = (index: number) => {
    setFormData((prev) => ({
      ...prev,
      parameters: prev.parameters.filter((_, i) => i !== index),
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;

    // Validation
    if (!formData.name.trim()) {
      toast.error("Tool name is required");
      return;
    }
    if (!formData.sql.trim()) {
      toast.error("SQL query is required");
      return;
    }
    if (!formData.datasource_id) {
      toast.error("Please select a datasource");
      return;
    }

    try {
      setLoading(true);
      const toolData = {
        name: formData.name.trim(),
        description: formData.description.trim() || null,
        type: formData.type || "query",
        datasource_id: parseInt(formData.datasource_id),
        sql: formData.sql.trim(),
        parameters: formData.parameters.map((param) => ({
          name: param.name,
          type: param.type,
          description: param.description || null,
          required: param.required,
          default: param.default || null,
        })),
      };

      console.log("Sending tool data:", toolData);

      if (isEditMode && tool) {
        const response = await apiService.updateTool(
          token,
          parseInt(tool.id),
          toolData
        );
        if (response.success) {
          toast.success("Tool updated successfully");
          onSave(response.data);
        } else {
          toast.error("Failed to update tool");
        }
      } else {
        const response = await apiService.createTool(token, toolData);
        if (response.success) {
          toast.success("Tool created successfully");
          onSave(response.data);
        } else {
          console.error("Tool creation failed:", response);
          const errorMessage = response.errors?.[0]?.msg || "Unknown error";
          toast.error(`Failed to create tool: ${errorMessage}`);
          console.error("Full error response:", response);
        }
      }
    } catch (err) {
      console.error("Error saving tool:", err);
      if (err instanceof ApiError) {
        toast.error(err.message);
      } else {
        toast.error("An unexpected error occurred");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleExecuteTool = () => {
    setShowExecuteDialog(true);
    setExecutionResult(null);

    // Initialize parameter values with defaults
    const initialValues: Record<string, string> = {};
    if (tool?.parameters) {
      tool.parameters.forEach((param) => {
        initialValues[param.name] = param.default || "";
      });
    }
    setParameterValues(initialValues);
  };

  const handleExecuteConfirm = async () => {
    if (!token || !tool) return;

    // Validate required parameters
    if (tool.parameters) {
      const missingRequired = tool.parameters.filter(
        (param) =>
          param.required &&
          (!parameterValues[param.name] ||
            parameterValues[param.name].trim() === "")
      );

      if (missingRequired.length > 0) {
        toast.error(
          `Please fill in required parameters: ${missingRequired
            .map((p) => p.name)
            .join(", ")}`
        );
        return;
      }
    }

    try {
      setExecuting(true);

      // Call the actual API with parameter values
      const response = await apiService.executeTool(
        token,
        parseInt(tool.id),
        parameterValues
      );

      if (response.success && response.data?.success) {
        setExecutionResult({
          success: true,
          rows: response.data.data || [],
          rowCount: response.data.row_count || 0,
          executionTime: response.data.execution_time_ms || 0,
        });
      } else {
        setExecutionResult({
          success: false,
          error:
            response.data?.error ||
            response.errors?.[0]?.msg ||
            "Execution failed",
        });
      }

      toast.success(
        `Tool executed successfully! ${
          response.data?.row_count || 0
        } rows returned`
      );
    } catch (err) {
      console.error("Error executing tool:", err);
      setExecutionResult({
        success: false,
        error: "Failed to execute tool",
      });
      toast.error("Failed to execute tool");
    } finally {
      setExecuting(false);
    }
  };

  const handleRunAgain = () => {
    setExecutionResult(null);
    // Reset parameter values to defaults
    const initialValues: Record<string, string> = {};
    if (tool?.parameters) {
      tool.parameters.forEach((param) => {
        initialValues[param.name] = param.default || "";
      });
    }
    setParameterValues(initialValues);
  };

  const handleCloseExecuteDialog = () => {
    setShowExecuteDialog(false);
    setExecutionResult(null);
  };

  const handleExportCSV = () => {
    if (!executionResult?.rows) return;

    const csvContent = [
      Object.keys(executionResult.rows[0]).join(","),
      ...executionResult.rows.map((row) =>
        Object.values(row)
          .map((value) => `"${value}"`)
          .join(",")
      ),
    ].join("\n");

    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${tool?.name || "tool"}_results.csv`;
    a.click();
    window.URL.revokeObjectURL(url);

    toast.success("CSV exported successfully");
  };

  const handleDeleteClick = () => {
    setShowDeleteDialog(true);
  };

  const handleDeleteConfirm = async () => {
    if (!token || !tool || !onDelete) return;

    try {
      setLoading(true);
      const response = await apiService.deleteTool(token, parseInt(tool.id));
      if (response.success) {
        toast.success("Tool deleted successfully");
        // Update the tools list in parent component
        onDelete(tool.id);
        // Reset the form state to go back to tools list
        onCancel();
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
      setShowDeleteDialog(false);
    }
  };

  const handleDeleteCancel = () => {
    setShowDeleteDialog(false);
  };

  return (
    <div className="h-full flex flex-col bg-gray-50 overflow-hidden">
      <div className="p-4 flex-1 flex flex-col min-h-0">
        {/* Header Section */}
        <div className="bg-white rounded-lg border border-gray-200 p-4 mb-4 flex-shrink-0">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-gray-900">
                {isEditMode ? "Edit Tool" : "Create New Tool"}
              </h2>
              <p className="text-gray-600 mt-1">
                Configure tool settings and SQL queries for data operations
              </p>
            </div>
            <div className="flex items-center space-x-3">
              {isEditMode && (
                <Button
                  type="button"
                  onClick={handleExecuteTool}
                  disabled={loading}
                  className="bg-[#FEBF23] hover:bg-[#FEBF23]/90 text-black flex items-center space-x-2"
                >
                  <Play className="w-4 h-4" />
                  <span>Execute</span>
                </Button>
              )}
              {isEditMode && (
                <Button
                  type="button"
                  onClick={handleDeleteClick}
                  disabled={loading}
                  variant="outline"
                  className="text-gray-700 bg-gray-100 hover:bg-gray-200 flex items-center space-x-2"
                >
                  <Trash2 className="w-4 h-4" />
                  <span>Delete</span>
                </Button>
              )}
              <Button
                type="button"
                variant="outline"
                onClick={onCancel}
                disabled={loading}
                className="text-gray-700 bg-gray-100 hover:bg-gray-200"
              >
                Cancel
              </Button>
              <Button
                type="submit"
                form="tool-form"
                disabled={loading}
                className="bg-[#FEBF23] hover:bg-[#FEBF23]/90 text-black border border-[#FEBF23]"
              >
                {loading ? "Saving..." : "Save"}
              </Button>
            </div>
          </div>
        </div>

        {/* Form Section */}
        <div className="bg-white rounded-lg border border-gray-200 flex-1 flex flex-col min-h-0">
          <div className="flex-1 overflow-y-auto p-6">
            <form id="tool-form" onSubmit={handleSubmit}>
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
                      onChange={(e) =>
                        handleInputChange("name", e.target.value)
                      }
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
                      onChange={(e) =>
                        handleInputChange("type", e.target.value)
                      }
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-black"
                    >
                      <option value="">Select tool type</option>
                      <option value="query">Query</option>
                      <option value="http" disabled>
                        HTTP (Coming Soon)
                      </option>
                      <option value="code" disabled>
                        Code (Coming Soon)
                      </option>
                    </select>
                  </div>
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Description
                    </label>
                    <textarea
                      value={formData.description}
                      onChange={(e) =>
                        handleInputChange("description", e.target.value)
                      }
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
                      onChange={(e) =>
                        handleInputChange("datasource_id", e.target.value)
                      }
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-black"
                    >
                      <option value="">Select datasource</option>
                      {datasources.map((ds) => (
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
                <h2 className="text-xl font-semibold text-black mb-4 border-b border-gray-200 pb-2">
                  SQL Query
                </h2>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    SQL Query <span className="text-red-500">*</span>
                  </label>
                  <textarea
                    value={formData.sql}
                    onChange={(e) => handleInputChange("sql", e.target.value)}
                    rows={8}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-black font-mono text-sm"
                    placeholder="SELECT * FROM table_name WHERE column = {{ parameter_name }}"
                  />
                  <p className="text-sm text-gray-500 mt-2">
                    Use{" "}
                    <code className="bg-gray-100 px-1 rounded">{`{{ parameter_name }}`}</code>{" "}
                    for parameter placeholders in your SQL query.
                  </p>
                </div>
              </div>

              {/* Parameters */}
              <div className="mb-8">
                <h2 className="text-xl font-semibold text-black mb-4 border-b border-gray-200 pb-2">
                  Parameters
                </h2>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <p className="text-sm text-gray-600">
                      Define parameters that users can pass to this tool
                    </p>
                    {!showParameterForm && (
                      <Button
                        type="button"
                        onClick={handleAddParameter}
                        className="bg-[#FEBF23] hover:bg-[#FEBF23]/90 text-black border border-[#FEBF23] rounded-lg px-3 py-1 text-sm font-medium"
                      >
                        <Plus className="w-4 h-4 mr-1" />
                        Add Parameter
                      </Button>
                    )}
                  </div>

                  {formData.parameters.length === 0 && !showParameterForm ? (
                    <div className="text-center py-4 text-gray-500 bg-gray-50 rounded-md">
                      No parameters defined. Click "Add Parameter" to add one.
                    </div>
                  ) : formData.parameters.length > 0 ? (
                    <div className="space-y-2">
                      {formData.parameters.map((parameter, index) => (
                        <div
                          key={index}
                          className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow"
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              {/* Grid Layout for Labels and Values */}
                              <div
                                className="grid gap-4"
                                style={{
                                  gridTemplateColumns:
                                    "1fr 0.7fr 2fr 1fr 0.8fr",
                                }}
                              >
                                {/* Name Column */}
                                <div>
                                  <div className="text-xs text-black mb-2 font-semibold">
                                    Name
                                  </div>
                                  <div className="text-sm text-gray-900">
                                    {parameter.name}
                                  </div>
                                </div>

                                {/* Type Column */}
                                <div>
                                  <div className="text-xs text-black mb-2 font-semibold">
                                    Type
                                  </div>
                                  <div className="text-xs text-gray-700">
                                    {parameter.type}
                                  </div>
                                </div>

                                {/* Description Column */}
                                <div>
                                  <div className="text-xs text-black mb-2 font-semibold">
                                    Description
                                  </div>
                                  <div className="text-xs text-gray-700 break-words">
                                    {parameter.description || "-"}
                                  </div>
                                </div>

                                {/* Default Value Column */}
                                <div>
                                  <div className="text-xs text-black mb-2 font-semibold">
                                    Default Value
                                  </div>
                                  <div className="text-xs text-gray-700">
                                    {parameter.default || "-"}
                                  </div>
                                </div>

                                {/* Required Column */}
                                <div>
                                  <div className="text-xs text-black mb-2 font-semibold">
                                    Required
                                  </div>
                                  <div className="text-xs text-gray-700">
                                    {parameter.required ? "Yes" : "No"}
                                  </div>
                                </div>
                              </div>
                            </div>

                            <div className="flex items-center space-x-2 ml-4">
                              <Button
                                type="button"
                                onClick={() => handleEditParameter(index)}
                                variant="ghost"
                                size="sm"
                                className="text-blue-600 hover:text-blue-700 hover:bg-blue-50 p-1 h-6 w-6"
                              >
                                <svg
                                  className="w-3 h-3"
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
                                type="button"
                                onClick={() => handleRemoveParameter(index)}
                                variant="ghost"
                                size="sm"
                                className="text-red-600 hover:text-red-700 hover:bg-red-50 p-1 h-6 w-6"
                              >
                                <Minus className="w-3 h-3" />
                              </Button>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : null}

                  {/* Section 3: Add Parameter Form (shown when showParameterForm is true) */}
                  {showParameterForm && (
                    <div className="bg-white border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-4">
                        <h4 className="font-medium text-gray-900">
                          {editingParameterIndex !== null
                            ? "Edit Parameter"
                            : "Add New Parameter"}
                        </h4>
                      </div>
                      <div className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              Name <span className="text-red-500">*</span>
                            </label>
                            <input
                              type="text"
                              value={parameterFormData.name}
                              onChange={(e) =>
                                handleParameterFormChange(
                                  "name",
                                  e.target.value
                                )
                              }
                              placeholder="e.g., start_date"
                              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-black"
                            />
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              Type <span className="text-red-500">*</span>
                            </label>
                            <select
                              value={parameterFormData.type}
                              onChange={(e) =>
                                handleParameterFormChange(
                                  "type",
                                  e.target.value
                                )
                              }
                              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-black"
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
                          <div className="md:col-span-2">
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              Description
                            </label>
                            <textarea
                              value={parameterFormData.description}
                              onChange={(e) =>
                                handleParameterFormChange(
                                  "description",
                                  e.target.value
                                )
                              }
                              rows={2}
                              placeholder="Brief description of this parameter"
                              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-black"
                            />
                          </div>
                          <div className="flex gap-4">
                            <div className="flex-1">
                              <label className="block text-sm font-medium text-gray-700 mb-2">
                                Default Value
                              </label>
                              <input
                                type="text"
                                value={parameterFormData.default}
                                onChange={(e) =>
                                  handleParameterFormChange(
                                    "default",
                                    e.target.value
                                  )
                                }
                                placeholder="Optional default value"
                                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-black"
                              />
                            </div>
                            <div className="flex items-end pb-2">
                              <label className="flex items-center">
                                <input
                                  type="checkbox"
                                  checked={parameterFormData.required}
                                  onChange={(e) =>
                                    handleParameterFormChange(
                                      "required",
                                      e.target.checked
                                    )
                                  }
                                  className="mr-2"
                                />
                                <span className="text-sm font-medium text-gray-700">
                                  Required
                                </span>
                              </label>
                            </div>
                          </div>
                        </div>
                        <div className="flex justify-end space-x-3 pt-4">
                          <Button
                            variant="outline"
                            onClick={handleCancelParameter}
                            className="text-gray-700 bg-gray-100 hover:bg-gray-200"
                          >
                            Cancel
                          </Button>
                          <Button
                            onClick={handleSaveParameter}
                            className="bg-[#FEBF23] hover:bg-[#FEBF23]/90 text-black border border-[#FEBF23]"
                          >
                            {editingParameterIndex !== null
                              ? "Update Parameter"
                              : "Save Parameter"}
                          </Button>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </form>
          </div>
        </div>
      </div>

      {/* Delete Confirmation Dialog */}
      <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Tool</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete "{tool?.name}"? This action cannot
              be undone and will permanently remove the tool and all associated
              data.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={handleDeleteCancel}
              disabled={loading}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleDeleteConfirm}
              disabled={loading}
              className="bg-red-600 hover:bg-red-700 text-white"
            >
              {loading ? "Deleting..." : "Delete"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Execute Tool Dialog */}
      <Dialog open={showExecuteDialog} onOpenChange={handleCloseExecuteDialog}>
        <DialogContent
          className="w-[800px] max-w-[90vw] sm:max-w-[800px] max-h-[65vh] flex flex-col"
          style={{ width: "800px", maxWidth: "90vw", maxHeight: "65vh" }}
        >
          <DialogHeader>
            <DialogTitle className="text-lg font-semibold">
              Execute Tool
            </DialogTitle>
          </DialogHeader>

          <div className="space-y-4 py-3 flex-1 overflow-y-auto">
            {/* Tool Information */}
            <div className="bg-gray-50 rounded-lg p-4 space-y-1">
              <h3 className="font-semibold text-lg text-black">{tool?.name}</h3>
              <p className="text-sm text-black">{tool?.description}</p>
            </div>

            {/* Parameters Section - Only show when no execution result */}
            {!executionResult && (
              <div className="bg-gray-50 rounded-lg p-4">
                {tool?.parameters && tool.parameters.length > 0 ? (
                  <div className="space-y-4">
                    <h4 className="font-medium text-gray-900">Parameters</h4>
                    {tool.parameters.map((param, index) => (
                      <div key={index} className="space-y-2">
                        <label className="text-sm font-medium text-gray-700">
                          {param.name}
                          {param.required && (
                            <span className="text-red-500 ml-1">*</span>
                          )}
                        </label>
                        <input
                          type="text"
                          value={parameterValues[param.name] || ""}
                          onChange={(e) =>
                            setParameterValues((prev) => ({
                              ...prev,
                              [param.name]: e.target.value,
                            }))
                          }
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-gray-500 focus:border-gray-500"
                          placeholder={param.default || `Enter ${param.name}`}
                        />
                        {param.description && (
                          <p className="text-xs text-gray-500">
                            {param.description}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="flex flex-col items-center space-y-2">
                    <div className="w-5 h-5 rounded-full bg-gray-600 flex items-center justify-center">
                      <span className="text-white text-xs font-bold">i</span>
                    </div>
                    <span className="text-sm text-gray-600">
                      This tool has no parameters to configure.
                    </span>
                  </div>
                )}
              </div>
            )}

            {/* Execution Status */}
            {executionResult && (
              <div className="space-y-4">
                {executionResult.success ? (
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <div className="flex items-center space-x-2">
                      <CheckCircle className="w-5 h-5 text-green-600" />
                      <span className="font-medium text-green-800">
                        Execution Completed
                      </span>
                    </div>
                    <p className="text-sm text-green-700 mt-1">
                      {executionResult.rowCount} rows returned in{" "}
                      {executionResult.executionTime}ms
                    </p>
                  </div>
                ) : (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <div className="flex items-center space-x-2">
                      <X className="w-5 h-5 text-red-600" />
                      <span className="font-medium text-red-800">
                        Execution Failed
                      </span>
                    </div>
                    <p className="text-sm text-red-700 mt-1">
                      {executionResult.error}
                    </p>
                  </div>
                )}

                {/* Results Section */}
                {executionResult.success && (
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <h4 className="font-medium text-gray-900">Results</h4>
                      {executionResult.rows &&
                        executionResult.rows.length > 0 && (
                          <Button
                            onClick={handleExportCSV}
                            className="bg-blue-600 hover:bg-blue-700 text-white flex items-center space-x-2"
                          >
                            <Download className="w-4 h-4" />
                            <span>Export CSV</span>
                          </Button>
                        )}
                    </div>

                    {executionResult.rows && executionResult.rows.length > 0 ? (
                      <div className="border border-gray-200 rounded-lg overflow-hidden">
                        <div className="overflow-x-auto max-h-[250px] overflow-y-auto">
                          <table className="w-full">
                            <thead className="bg-gray-50 sticky top-0 z-10">
                              <tr>
                                {Object.keys(executionResult.rows[0]).map(
                                  (key) => (
                                    <th
                                      key={key}
                                      className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                                    >
                                      {key}
                                    </th>
                                  )
                                )}
                              </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                              {executionResult.rows.map((row, index) => (
                                <tr key={index}>
                                  {Object.values(row).map(
                                    (value, cellIndex) => (
                                      <td
                                        key={cellIndex}
                                        className="px-4 py-3 text-sm text-gray-900"
                                      >
                                        {String(value)}
                                      </td>
                                    )
                                  )}
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    ) : (
                      <div className="text-center py-8 bg-gray-50 rounded-lg border border-gray-200">
                        <div className="flex flex-col items-center space-y-2">
                          <div className="w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center">
                            <span className="text-gray-600 text-sm font-bold">
                              !
                            </span>
                          </div>
                          <span className="text-gray-600 font-medium">
                            No records found
                          </span>
                          <span className="text-sm text-gray-500">
                            The query executed successfully but returned no
                            results.
                          </span>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Loading State */}
            {executing && (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
                <span className="ml-3 text-gray-600">Executing tool...</span>
              </div>
            )}
          </div>

          <DialogFooter className="flex justify-end space-x-3 pt-4 pb-4 border-t border-gray-200 flex-shrink-0">
            {!executionResult ? (
              <>
                <Button
                  variant="outline"
                  onClick={handleCloseExecuteDialog}
                  disabled={executing}
                  className="text-gray-700 bg-gray-100 hover:bg-gray-200"
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleExecuteConfirm}
                  disabled={executing}
                  className="bg-[#FEBF23] hover:bg-[#FEBF23]/90 text-black flex items-center space-x-2"
                >
                  <Play className="w-4 h-4" />
                  <span>Execute Tool</span>
                </Button>
              </>
            ) : (
              <>
                <Button
                  variant="outline"
                  onClick={handleCloseExecuteDialog}
                  className="text-gray-700 bg-white border border-gray-300 hover:bg-gray-50"
                >
                  Close
                </Button>
                <Button
                  onClick={handleRunAgain}
                  disabled={executing}
                  className="bg-[#FEBF23] hover:bg-[#FEBF23]/90 text-black border border-[#FEBF23] flex items-center space-x-2"
                >
                  <RotateCcw className="w-4 h-4" />
                  <span>Run Again</span>
                </Button>
              </>
            )}
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default ToolsModule;
