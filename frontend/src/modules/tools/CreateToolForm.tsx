"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import DeleteConfirmationDialog from "./DeleteConfirmationDialog";
import ParameterDialog from "./ParameterDialog";
import ToolExecutionDialog from "./ToolExecutionDialog";
import { TagSelector } from "@/components/TagSelector";
import { apiService, ApiError } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "sonner";
import {
  Plus,
  Trash2,
  Minus,
  Play,
  ArrowLeftIcon,
} from "lucide-react";

interface ToolItem {
  id: string;
  name: string;
  description: string;
  type: string;
  datasource_id: string;
  sql: string;
  parameters?: ToolParameter[];
  tags?: string[];
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

interface Tag {
  id: number;
  name: string;
  description?: string;
  color?: string;
}

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
  const [toolDetails, setToolDetails] = useState<ToolItem | null>(tool || null);
  const [loadingToolDetails, setLoadingToolDetails] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    type: "",
    datasource_id: "",
    sql: "",
    parameters: [] as ToolParameter[],
    tags: [] as string[],
    endpoint: "",
    method: "GET",
    headers: "{}",
    payload: "",
  });
  const [loading, setLoading] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [availableTags, setAvailableTags] = useState<Tag[]>([]);
  const [loadingTags, setLoadingTags] = useState(false);
  const [showExecuteDialog, setShowExecuteDialog] = useState(false);
  const [executionResult, setExecutionResult] =
    useState<ExecutionResult | null>(null);
  const [executing, setExecuting] = useState(false);
  const [parameterValues, setParameterValues] = useState<
    Record<string, string>
  >({});
  const [showParameterDialog, setShowParameterDialog] = useState(false);
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

  useEffect(() => {
    const fetchTags = async () => {
      if (!token) return;

      try {
        setLoadingTags(true);
        const response = await apiService.getTags(token);
        if (response.success && response.data) {
          setAvailableTags(response.data);
        } else {
          toast.error("Failed to fetch tags");
        }
      } catch (err) {
        console.error("Error fetching tags:", err);
        if (err instanceof ApiError) {
          toast.error(err.message);
        }
      } finally {
        setLoadingTags(false);
      }
    };

    fetchTags();
  }, [token]);

  useEffect(() => {
    const fetchToolDetails = async () => {
      if (!isEditMode || !tool || !token) {
        return;
      }

      try {
        setLoadingToolDetails(true);
        const response = await apiService.getTool(token, parseInt(tool.id));
        
        if (response.success && response.data) {
          setToolDetails(response.data);
          
          // Parse HTTP configuration if it's an HTTP tool
          let httpConfig = {
            endpoint: "",
            method: "GET",
            headers: "{}",
            payload: "",
          };
          
          if (response.data.type?.toLowerCase() === "http") {
            try {
              const config = JSON.parse(response.data.sql);
              httpConfig = {
                endpoint: config.endpoint || "",
                method: config.method || "GET",
                headers: config.headers || "{}",
                payload: config.payload || "",
              };
            } catch (error) {
              console.error("Error parsing HTTP config:", error);
            }
          }
          
          setFormData({
            name: response.data.name || "",
            description: response.data.description || "",
            type: (response.data.type || "").toLowerCase(),
            datasource_id: response.data.datasource_id || "",
            sql: response.data.type?.toLowerCase() === "http" ? "" : (response.data.sql || ""),
            parameters: response.data.parameters || [],
            tags: response.data.tags || [],
            endpoint: httpConfig.endpoint,
            method: httpConfig.method,
            headers: httpConfig.headers,
            payload: httpConfig.payload,
          });
        } else {
          toast.error("Failed to fetch tool details");
        }
      } catch (err) {
        console.error("Error fetching tool details:", err);
        if (err instanceof ApiError) {
          toast.error(err.message);
        } else {
          toast.error("An unexpected error occurred while fetching tool details");
        }
      } finally {
        setLoadingToolDetails(false);
      }
    };

    fetchToolDetails();
  }, [isEditMode, tool, token]);

  const handleInputChange = (field: string, value: string | string[]) => {
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
    setShowParameterDialog(true);
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
    setShowParameterDialog(true);
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

    setShowParameterDialog(false);
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
    setShowParameterDialog(false);
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

  const handleCreateTag = async (name: string) => {
    if (!token) return;

    try {
      const response = await apiService.createTag(token, { name });
      if (response.success && response.data) {
        setAvailableTags((prev) => [...prev, response.data]);
      } else {
        throw new Error("Failed to create tag");
      }
    } catch (err) {
      console.error("Error creating tag:", err);
      throw err;
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;

    // Prevent multiple submissions
    if (loading) {
      toast.warning("Please wait, save operation in progress...");
      return;
    }

    // Validation
    if (!formData.name.trim()) {
      toast.error("Tool name is required");
      return;
    }
    if (!formData.type) {
      toast.error("Please select a tool type");
      return;
    }

    // Type-specific validation
    if (formData.type === "query") {
      if (!formData.sql.trim()) {
        toast.error("SQL query is required");
        return;
      }
    } else if (formData.type === "http") {
      if (!formData.endpoint?.trim()) {
        toast.error("Endpoint URL is required");
        return;
      }
    }

    if (!formData.datasource_id) {
      toast.error("Please select a datasource");
      return;
    }

    try {
      setLoading(true);
      toast.loading(isEditMode ? "Updating tool..." : "Creating tool...", {
        id: "save-tool",
      });
      let toolData: any = {
        name: formData.name.trim(),
        description: formData.description.trim() || null,
        type: formData.type || "query",
        datasource_id: parseInt(formData.datasource_id),
        parameters: formData.parameters.map((param) => ({
          name: param.name,
          type: param.type,
          description: param.description || null,
          required: param.required,
          default: param.default || null,
        })),
        tags: formData.tags,
      };

      // Add type-specific data
      if (formData.type === "http") {
        // For HTTP tools, store configuration in the sql field as JSON
        toolData.sql = JSON.stringify({
          endpoint: formData.endpoint.trim(),
          method: formData.method,
          headers: formData.headers.trim() || "{}",
          payload: formData.payload.trim() || "",
        });
      } else {
        // For query tools, use the sql field directly
        toolData.sql = formData.sql.trim();
      }

      console.log("Sending tool data:", toolData);

      if (isEditMode && tool) {
        const response = await apiService.updateTool(
          token,
          parseInt(tool.id),
          toolData
        );
        if (response.success) {
          toast.dismiss("save-tool");
          onSave(response.data);
        } else {
          toast.dismiss("save-tool");
          toast.error("Failed to update tool");
        }
      } else {
        const response = await apiService.createTool(token, toolData);
        if (response.success) {
          toast.dismiss("save-tool");
          onSave(response.data);
        } else {
          toast.dismiss("save-tool");
          console.error("Tool creation failed:", response);
          const errorMessage = response.errors?.[0]?.msg || "Unknown error";
          toast.error(`Failed to create tool: ${errorMessage}`);
          console.error("Full error response:", response);
        }
      }
    } catch (err) {
      console.error("Error saving tool:", err);
      toast.dismiss("save-tool");
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
    const currentTool = toolDetails || tool;
    if (currentTool?.parameters) {
      currentTool.parameters.forEach((param) => {
        initialValues[param.name] = param.default || "";
      });
    }
    setParameterValues(initialValues);
  };

  const handleExecuteConfirm = async () => {
    if (!token || !tool) return;

    const currentTool = toolDetails || tool;

    // Validate required parameters
    if (currentTool.parameters) {
      const missingRequired = currentTool.parameters.filter(
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

      if (response.success) {
        // HTTP request was successful, check if there's an error in the data
        if (response.data?.error) {
          // Tool execution failed with an error
          setExecutionResult({
            success: false,
            error: response.data.error,
          });
        } else {
          // Tool execution succeeded (even if no rows returned)
          setExecutionResult({
            success: true,
            rows: response.data?.data || [],
            rowCount: response.data?.row_count || 0,
            executionTime: response.data?.execution_time_ms || 0,
          });
        }
      } else {
        // HTTP   request failed
        setExecutionResult({
          success: false,
          error: response.errors?.[0]?.msg || "Execution failed",
        });
      }

      // Only show success toast if execution was successful
      if (response.success && !response.data?.error) {
        toast.success(
          `Tool executed successfully! ${
            response.data?.row_count || 0
          } rows returned`
        );
      }
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
              <Button
                type="button"
                variant="secondary"
                onClick={onCancel}
                disabled={loading}
                className="bg-tertiary hover:bg-tertiary/90 border-1 text-tertiary-foreground flex items-center space-x-2"
              >
                <ArrowLeftIcon className="w-4 h-4" />
                <span>
                  Cancel
                </span>
              </Button>
              {isEditMode && (
                <Button
                  type="button"
                  onClick={handleExecuteTool}
                  disabled={loading}
                  className="bg-tertiary hover:bg-tertiary/90 border-1 text-tertiary-foreground flex items-center space-x-2"
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
                  variant="secondary"
                  className="bg-tertiary hover:bg-tertiary/90 border-1 text-tertiary-foreground flex items-center space-x-2"
                >
                  <Trash2 className="w-4 h-4" />
                  <span>Delete</span>
                </Button>
              )}
              <Button
                type="submit"
                form="tool-form"
                disabled={loading}
                className="bg-primary hover:bg-primary/90 text-primary-foreground border border-primary"
              >
                {loading ? "Saving..." : "Save"}
              </Button>
            </div>
          </div>
        </div>

        {/* Loading State for Tool Details */}
        {loadingToolDetails && (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
            <span className="ml-3 text-gray-600">Loading tool details...</span>
          </div>
        )}

        {/* Form Section */}
        {!loadingToolDetails && (
          <div className="bg-white rounded-lg border border-gray-200 flex-1 flex flex-col min-h-0">
            <div className="flex-1 overflow-y-auto p-6">
              <form id="tool-form" onSubmit={handleSubmit}>
              {/* Basic Information */}
              <div className="mb-8">
                <h2 className="text-xl font-semibold text-primary-foreground mb-4 border-b border-gray-200 pb-2">
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
                      <option value="http">HTTP</option>
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

              <div className="mb-8">
                <h2 className="text-xl font-semibold text-primary-foreground mb-4 border-b border-gray-200 pb-2">
                  Tags
                </h2>
                <p className="text-sm text-gray-600 mb-4">
                  Add tags to categorize and organize your tools
                </p>
                {loadingTags ? (
                  <div className="flex items-center justify-center py-4">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-gray-900"></div>
                    <span className="ml-3 text-gray-600">Loading tags...</span>
                  </div>
                ) : (
                  <TagSelector
                    selectedTags={formData.tags}
                    onTagsChange={(tags) => handleInputChange("tags", tags)}
                    availableTags={availableTags}
                    onCreateTag={handleCreateTag}
                  />
                )}
              </div>

              {/* SQL Query - Only for Query tools */}
              {formData.type === "query" && (
                <div className="mb-8">
                  <h2 className="text-xl font-semibold text-primary-foreground mb-4 border-b border-gray-200 pb-2">
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
              )}

              {/* HTTP Configuration - Only for HTTP tools */}
              {formData.type === "http" && (
                <div className="mb-8">
                  <h2 className="text-xl font-semibold text-primary-foreground mb-4 border-b border-gray-200 pb-2">
                    HTTP Configuration
                  </h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Endpoint URL <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="url"
                        value={formData.endpoint || ""}
                        onChange={(e) =>
                          handleInputChange("endpoint", e.target.value)
                        }
                        required
                        className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-black"
                        placeholder="https://api.example.com/users"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        HTTP Method <span className="text-red-500">*</span>
                      </label>
                      <select
                        value={formData.method || "GET"}
                        onChange={(e) =>
                          handleInputChange("method", e.target.value)
                        }
                        required
                        className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-black"
                      >
                        <option value="GET">GET</option>
                        <option value="POST">POST</option>
                        <option value="PUT">PUT</option>
                        <option value="PATCH">PATCH</option>
                        <option value="DELETE">DELETE</option>
                      </select>
                    </div>
                  </div>
                  <div className="mt-6">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Headers (JSON format)
                    </label>
                    <textarea
                      value={formData.headers || "{}"}
                      onChange={(e) =>
                        handleInputChange("headers", e.target.value)
                      }
                      rows={4}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-black font-mono text-sm"
                      placeholder='{"Authorization": "Bearer {{ token }}", "Content-Type": "application/json"}'
                    />
                    <p className="text-sm text-gray-500 mt-2">
                      Use{" "}
                      <code className="bg-gray-100 px-1 rounded">{`{{ parameter_name }}`}</code>{" "}
                      for parameter placeholders in headers.
                    </p>
                  </div>
                  <div className="mt-6">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Request Body/Payload (JSON format)
                    </label>
                    <textarea
                      value={formData.payload || ""}
                      onChange={(e) =>
                        handleInputChange("payload", e.target.value)
                      }
                      rows={6}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-black font-mono text-sm"
                      placeholder='{"name": "{{ name }}", "email": "{{ email }}"}'
                    />
                    <p className="text-sm text-gray-500 mt-2">
                      Use{" "}
                      <code className="bg-gray-100 px-1 rounded">{`{{ parameter_name }}`}</code>{" "}
                      for parameter placeholders in the payload.
                    </p>
                  </div>
                </div>
              )}

              {/* Parameters */}
              <div className="mb-8">
                <h2 className="text-xl font-semibold text-primary-foreground mb-4 border-b border-gray-200 pb-2">
                  Parameters
                </h2>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <p className="text-sm text-gray-600">
                      Define parameters that users can pass to this tool
                    </p>
                    <Button
                      type="button"
                      onClick={handleAddParameter}
                      className="bg-primary hover:bg-primary/90 text-primary-foreground border border-primary rounded-lg px-3 py-1 text-sm font-medium"
                    >
                      <Plus className="w-4 h-4 mr-1" />
                      Add Parameter
                    </Button>
                  </div>

                  {formData.parameters.length === 0 ? (
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
                                  <div className="text-xs text-primary-foreground mb-2 font-semibold">
                                    Name
                                  </div>
                                  <div className="text-sm text-gray-900">
                                    {parameter.name}
                                  </div>
                                </div>

                                {/* Type Column */}
                                <div>
                                  <div className="text-xs text-primary-foreground mb-2 font-semibold">
                                    Type
                                  </div>
                                  <div className="text-xs text-gray-700">
                                    {parameter.type}
                                  </div>
                                </div>

                                {/* Description Column */}
                                <div>
                                  <div className="text-xs text-primary-foreground mb-2 font-semibold">
                                    Description
                                  </div>
                                  <div className="text-xs text-gray-700 break-words">
                                    {parameter.description || "-"}
                                  </div>
                                </div>

                                {/* Default Value Column */}
                                <div>
                                  <div className="text-xs text-primary-foreground mb-2 font-semibold">
                                    Default Value
                                  </div>
                                  <div className="text-xs text-gray-700">
                                    {parameter.default || "-"}
                                  </div>
                                </div>

                                {/* Required Column */}
                                <div>
                                  <div className="text-xs text-primary-foreground mb-2 font-semibold">
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

                </div>
              </div>
            </form>
          </div>
        </div>
        )}
      </div>

      <DeleteConfirmationDialog
        open={showDeleteDialog}
        onOpenChange={setShowDeleteDialog}
        onConfirm={handleDeleteConfirm}
        onCancel={handleDeleteCancel}
        loading={loading}
        toolName={tool?.name}
      />

      <ParameterDialog
        open={showParameterDialog}
        onOpenChange={setShowParameterDialog}
        onSave={handleSaveParameter}
        onCancel={handleCancelParameter}
        isEditing={editingParameterIndex !== null}
        formData={parameterFormData}
        onFormChange={handleParameterFormChange}
      />

      <ToolExecutionDialog
        open={showExecuteDialog}
        onOpenChange={handleCloseExecuteDialog}
        toolName={tool?.name}
        toolDescription={tool?.description}
        parameters={tool?.parameters}
        parameterValues={parameterValues}
        onParameterChange={(name, value) =>
          setParameterValues((prev) => ({
            ...prev,
            [name]: value,
          }))
        }
        executionResult={executionResult}
        executing={executing}
        onExecute={handleExecuteConfirm}
        onRunAgain={handleRunAgain}
        onClose={handleCloseExecuteDialog}
        onExportCSV={handleExportCSV}
      />
    </div>
  );
};

export default CreateToolForm;
