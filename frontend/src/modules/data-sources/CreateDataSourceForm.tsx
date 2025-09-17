"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Plug, Trash2 } from "lucide-react";
import { toast } from "sonner";

import {
  DataSource,
  apiService,
  ApiError,
  DatasourceFieldConfig,
} from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";

interface CreateDataSourceFormProps {
  dataSource?: DataSource | null;
  onSave: (dataSource: any) => void;
  onCancel: () => void;
  onDelete?: () => void;
}

const CreateDataSourceForm = ({
  dataSource,
  onSave,
  onCancel,
  onDelete,
}: CreateDataSourceFormProps) => {
  const { token } = useAuth();
  const [formData, setFormData] = useState({
    name: dataSource?.name || "",
    database_type: dataSource?.database_type || "",
    host: dataSource?.host || "",
    port: dataSource?.port?.toString() || "",
    database: dataSource?.database || "",
    username: dataSource?.username || "",
    password: "",
    connection_string: dataSource?.connection_string || "",
    ssl_mode: dataSource?.ssl_mode || "",
    additional_params: dataSource?.additional_params
      ? JSON.stringify(dataSource.additional_params, null, 2)
      : "",
    // SQLite fields
    sqlite_database: "",
    // Databricks fields
    databricks_host: "",
    http_path: "",
    databricks_token: "",
    catalog: "",
    schema: "",
  });

  const [loading, setLoading] = useState(false);
  const [testingConnection, setTestingConnection] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [fieldConfigs, setFieldConfigs] = useState<Record<
    string,
    DatasourceFieldConfig
  > | null>(null);
  const [loadingFieldConfigs, setLoadingFieldConfigs] = useState(true);
  const isEditMode = !!dataSource;

  // Load field configurations on component mount
  useEffect(() => {
    const loadFieldConfigs = async () => {
      if (!token) return;

      try {
        const response = await apiService.getDataSourceFieldConfig(token);
        if (response.success && response.data) {
          setFieldConfigs(response.data);
        } else {
          toast.error("Failed to load field configurations");
        }
      } catch (err) {
        if (err instanceof ApiError) {
          toast.error(err.message);
        } else {
          toast.error(
            "An unexpected error occurred while loading field configurations"
          );
        }
      } finally {
        setLoadingFieldConfigs(false);
      }
    };

    loadFieldConfigs();
  }, [token]);

  // Populate form with existing datasource data
  useEffect(() => {
    if (dataSource && fieldConfigs) {
      populateForm(dataSource);
    }
  }, [dataSource, fieldConfigs]);

  const handleInputChange = (field: string, value: string) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  // Populate form with datasource data
  const populateForm = (datasource: DataSource) => {
    setFormData((prev) => ({
      ...prev,
      name: datasource.name,
      database_type: datasource.database_type,
      host: datasource.host || "",
      port: datasource.port?.toString() || "",
      database: datasource.database || "",
      username: datasource.username || "",
      connection_string: datasource.connection_string || "",
      ssl_mode: datasource.ssl_mode || "",
      additional_params: datasource.additional_params
        ? JSON.stringify(datasource.additional_params, null, 2)
        : "",
      // Populate fields based on database type
      sqlite_database:
        datasource.database_type === "sqlite" ? datasource.database : "",
      databricks_host:
        datasource.database_type === "databricks" ? datasource.host : "",
      http_path:
        datasource.database_type === "databricks"
          ? datasource.additional_params?.http_path || ""
          : "",
      catalog:
        datasource.database_type === "databricks"
          ? datasource.additional_params?.catalog || ""
          : "",
      schema:
        datasource.database_type === "databricks"
          ? datasource.additional_params?.schema || ""
          : "",
    }));
  };

  const handleDeleteClick = () => {
    setShowDeleteDialog(true);
  };

  const handleDeleteConfirm = async () => {
    if (!isEditMode || !dataSource || !token) return;

    try {
      const response = await apiService.deleteDataSource(token, dataSource.id);
      if (response.success) {
        toast.success("Datasource deleted successfully");
        setShowDeleteDialog(false);
        if (onDelete) {
          onDelete();
        }
      } else {
        toast.error("Failed to delete datasource");
      }
    } catch (err) {
      if (err instanceof ApiError) {
        toast.error(err.message);
      } else {
        toast.error("An unexpected error occurred");
      }
    }
  };

  const handleDeleteCancel = () => {
    setShowDeleteDialog(false);
  };

  const handleTestConnection = async () => {
    if (!token) {
      toast.error("No authentication token available");
      return;
    }

    // For edit mode, we test the existing datasource, so no validation needed
    if (isEditMode && dataSource) {
      // No validation needed for edit mode - we'll test the existing datasource
    } else {
      // For create mode, validate all required fields including password
      if (
        !formData.database_type ||
        !formData.host ||
        !formData.port ||
        !formData.database ||
        !formData.username ||
        !formData.password
      ) {
        toast.error("Please fill in all required fields to test connection");
        return;
      }
    }

    setTestingConnection(true);

    try {
      // Parse additional params if provided
      let additionalParams = {};
      if (formData.additional_params.trim()) {
        try {
          additionalParams = JSON.parse(formData.additional_params);
        } catch (err) {
          toast.error("Invalid JSON in additional parameters");
          setTestingConnection(false);
          return;
        }
      }

      const testData = {
        name: formData.name || "test",
        database_type: formData.database_type,
        host: formData.host,
        port: parseInt(formData.port),
        database: formData.database,
        username: formData.username,
        password: formData.password,
        connection_string: formData.connection_string || undefined,
        ssl_mode: formData.ssl_mode || undefined,
        additional_params:
          Object.keys(additionalParams).length > 0
            ? additionalParams
            : undefined,
      };

      let response;

      if (isEditMode && dataSource) {
        // For edit mode, test the existing datasource (no password needed)
        response = await apiService.testExistingDataSourceConnection(
          token,
          dataSource.id
        );
      } else {
        // For create mode, test with provided parameters
        response = await apiService.testDataSourceConnection(token, testData);
      }

      if (response.success) {
        let message = "Connection test successful!";
        if (
          isEditMode &&
          "data" in response &&
          response.data &&
          typeof response.data === "object" &&
          "connection_time_ms" in response.data
        ) {
          message = `Connection successful! (${
            (response.data as any).connection_time_ms
          }ms)`;
        }
        toast.success(message);
      } else {
        toast.error(response.errors?.[0]?.msg || "Connection test failed");
      }
    } catch (err) {
      console.error("Test connection error:", err);
      if (err instanceof ApiError) {
        toast.error(err.message);
      } else {
        toast.error("An unexpected error occurred during connection test");
      }
    } finally {
      setTestingConnection(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Validate required fields
      if (!formData.name || !formData.database_type) {
        setError("Please fill in all required fields");
        setLoading(false);
        return;
      }

      // Type-specific validation using field configurations
      if (fieldConfigs && fieldConfigs[formData.database_type]) {
        const config = fieldConfigs[formData.database_type];
        for (const field of config.fields) {
          if (
            field.required &&
            !formData[field.name as keyof typeof formData]
          ) {
            setError(`Please fill in the required field: ${field.label}`);
            setLoading(false);
            return;
          }
        }
      }

      // Parse additional params if provided
      let additionalParams = {};
      if (formData.additional_params.trim()) {
        try {
          additionalParams = JSON.parse(formData.additional_params);
        } catch (err) {
          setError("Invalid JSON in additional parameters");
          setLoading(false);
          return;
        }
      }

      // Build data source data based on database type
      const dataSourceData = getFormDataForDatabaseType(
        formData,
        additionalParams
      );

      if (isEditMode && dataSource) {
        // Update existing datasource
        const response = await apiService.updateDataSource(
          token!,
          dataSource.id,
          dataSourceData
        );
        if (response.success) {
          onSave(response.data);
        } else {
          setError("Failed to update datasource");
        }
      } else {
        // Create new datasource
        const response = await apiService.createDataSource(
          token!,
          dataSourceData
        );
        if (response.success) {
          onSave(response.data);
        } else {
          setError("Failed to create datasource");
        }
      }
    } catch (err) {
      setError("An unexpected error occurred");
    } finally {
      setLoading(false);
    }
  };

  // Get form data based on database type
  const getFormDataForDatabaseType = (
    formData: any,
    additionalParams: any
  ): any => {
    const baseData = {
      name: formData.name,
      database_type: formData.database_type,
      connection_string: formData.connection_string || undefined,
      additional_params:
        Object.keys(additionalParams).length > 0 ? additionalParams : undefined,
    };

    switch (formData.database_type) {
      case "sqlite":
        return {
          ...baseData,
          database: formData.sqlite_database,
          host: "",
          port: 0,
          username: "",
          password: "",
        };
      case "postgresql":
      case "mysql":
        return {
          ...baseData,
          host: formData.host,
          port: parseInt(formData.port),
          database: formData.database,
          username: formData.username,
          password: formData.password,
          ssl_mode: formData.ssl_mode || undefined,
        };
      case "databricks":
        return {
          ...baseData,
          host: formData.databricks_host,
          password: formData.databricks_token,
          database: "databricks",
          port: 0,
          username: "",
          additional_params: {
            ...additionalParams,
            http_path: formData.http_path,
            catalog: formData.catalog,
            schema: formData.schema,
          },
        };
      default:
        return {
          ...baseData,
          host: "",
          port: 0,
          database: "",
          username: "",
          password: "",
        };
    }
  };

  return (
    <div className="h-full flex flex-col">
      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
          <div className="flex items-center">
            <div className="text-red-600 text-sm">{error}</div>
            <button
              onClick={() => setError(null)}
              className="ml-auto text-red-600 hover:text-red-700"
            >
              ×
            </button>
          </div>
        </div>
      )}

      {/* Header Section */}
      <div className="bg-white rounded-lg border border-gray-200 p-4 mb-4 flex-shrink-0">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">
              {isEditMode ? "Edit Datasource" : "Create New Datasource"}
            </h2>
            <p className="text-gray-600 mt-1">
              Configure database connection settings and parameters
            </p>
          </div>
          <div className="flex items-center space-x-3">
            <Button
              type="button"
              onClick={handleTestConnection}
              disabled={testingConnection || loading}
              variant="secondary"
              className="flex items-center space-x-2"
            >
              <Plug className="w-4 h-4" />
              <span>
                {testingConnection ? "Testing..." : "Test Connection"}
              </span>
            </Button>
            {isEditMode && (
              <Button
                type="button"
                variant="secondary"
                onClick={handleDeleteClick}
                disabled={loading}
                className="flex items-center space-x-2"
              >
                <Trash2 className="w-4 h-4" />
                <span>Delete</span>
              </Button>
            )}
            <Button
              type="button"
              variant="secondary"
              onClick={onCancel}
              disabled={loading}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              form="datasource-form"
              disabled={loading}
              className="bg-primary hover:bg-primary/90 text-primary-foreground border border-primary"
            >
              {!isEditMode
                ? loading
                  ? "Saving..."
                  : "Save"
                : loading
                ? "Updating..."
                : "Update"}
            </Button>
          </div>
        </div>
      </div>

      {/* Form Section */}
      <div className="bg-white rounded-lg border border-gray-200 flex-1 flex flex-col">
        <div className="flex-1 overflow-y-auto p-6">
          {loadingFieldConfigs ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-black"></div>
              <span className="ml-3 text-gray-600">
                Loading form configuration...
              </span>
            </div>
          ) : (
            <form id="datasource-form" onSubmit={handleSubmit}>
              {/* Basic Information */}
              <div className="mb-8">
                <h2 className="text-xl font-semibold text-primary-foreground mb-4 border-b border-gray-200 pb-2">
                  Basic Information
                </h2>
                <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
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
                      placeholder="My Database"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Database Type <span className="text-red-500">*</span>
                    </label>
                    <select
                      value={formData.database_type}
                      onChange={(e) =>
                        handleInputChange("database_type", e.target.value)
                      }
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

              {/* Dynamic Configuration Sections */}
              {fieldConfigs &&
                formData.database_type &&
                fieldConfigs[formData.database_type] && (
                  <div className="mb-8">
                    {fieldConfigs[formData.database_type].sections.map(
                      (section) => (
                        <div key={section.id} className="mb-8">
                          <h2 className="text-xl font-semibold text-primary-foreground mb-4 border-b border-gray-200 pb-2">
                            {section.title}
                          </h2>
                          <p className="text-gray-600 mb-4">
                            {section.description}
                          </p>
                          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
                            {fieldConfigs[formData.database_type].fields.map(
                              (field) => {
                                // Hide password field in edit mode
                                if (field.type === "password" && isEditMode) {
                                  return null;
                                }

                                return (
                                  <div key={field.name}>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                      {field.label}{" "}
                                      {field.required && !isEditMode && (
                                        <span className="text-red-500">*</span>
                                      )}
                                    </label>
                                    {field.type === "password" ? (
                                      <input
                                        type="password"
                                        value={
                                          formData[
                                            field.name as keyof typeof formData
                                          ] || ""
                                        }
                                        onChange={(e) =>
                                          handleInputChange(
                                            field.name,
                                            e.target.value
                                          )
                                        }
                                        required={field.required}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-black"
                                        placeholder={field.placeholder || ""}
                                      />
                                    ) : field.type === "text" ? (
                                      <input
                                        type="text"
                                        value={
                                          formData[
                                            field.name as keyof typeof formData
                                          ] || ""
                                        }
                                        onChange={(e) =>
                                          handleInputChange(
                                            field.name,
                                            e.target.value
                                          )
                                        }
                                        required={field.required}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-black"
                                        placeholder={field.placeholder || ""}
                                      />
                                    ) : field.type === "number" ? (
                                      <input
                                        type="number"
                                        value={
                                          formData[
                                            field.name as keyof typeof formData
                                          ] || ""
                                        }
                                        onChange={(e) =>
                                          handleInputChange(
                                            field.name,
                                            e.target.value
                                          )
                                        }
                                        required={field.required}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-black"
                                        placeholder={field.placeholder || ""}
                                      />
                                    ) : (
                                      <input
                                        type="text"
                                        value={
                                          formData[
                                            field.name as keyof typeof formData
                                          ] || ""
                                        }
                                        onChange={(e) =>
                                          handleInputChange(
                                            field.name,
                                            e.target.value
                                          )
                                        }
                                        required={field.required}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-black"
                                        placeholder={field.placeholder || ""}
                                      />
                                    )}
                                    {field.description && (
                                      <p className="text-sm text-gray-500 mt-1">
                                        {field.description}
                                      </p>
                                    )}
                                  </div>
                                );
                              }
                            )}
                          </div>
                        </div>
                      )
                    )}
                  </div>
                )}

              {/* Advanced Options */}
              <div className="mb-8">
                <h2 className="text-xl font-semibold text-primary-foreground mb-4 border-b border-gray-200 pb-2">
                  Advanced Options
                </h2>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Connection String (Optional)
                    </label>
                    <input
                      type="text"
                      value={formData.connection_string}
                      onChange={(e) =>
                        handleInputChange("connection_string", e.target.value)
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-black"
                      placeholder="postgresql://user:pass@host:port/db"
                    />
                    <p className="text-sm text-gray-500 mt-1">
                      If provided, this will override the individual connection
                      parameters above.
                    </p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Additional Parameters (JSON)
                    </label>
                    <textarea
                      value={formData.additional_params}
                      onChange={(e) =>
                        handleInputChange("additional_params", e.target.value)
                      }
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-black font-mono text-sm"
                      placeholder='{"key": "value"}'
                    />
                  </div>
                </div>
              </div>
            </form>
          )}
        </div>
      </div>

      {/* Delete Confirmation Dialog */}
      <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Datasource</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete "{dataSource?.name}"? This action
              cannot be undone and will permanently remove the datasource and
              all associated data.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="secondary"
              onClick={handleDeleteCancel}
              disabled={loading}
            >
              Cancel
            </Button>
            <Button
              onClick={handleDeleteConfirm}
              disabled={loading}
              className="bg-primary hover:bg-primary/90 text-primary-foreground"
            >
              {loading ? "Deleting..." : "Delete"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default CreateDataSourceForm;
