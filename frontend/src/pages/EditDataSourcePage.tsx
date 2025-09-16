import { useNavigate, useParams } from "react-router-dom";
import { useState, useEffect } from "react";
import { toast } from "sonner";
import CreateDataSourceForm from "@/modules/data-sources/CreateDataSourceForm";
import { apiService, DataSource } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";

export default function EditDataSourcePage() {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const { token } = useAuth();
  const [dataSource, setDataSource] = useState<DataSource | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDataSource = async () => {
      if (!token || !id) return;

      try {
        const response = await apiService.getDataSource(token, parseInt(id));
        if (response.success && response.data) {
          setDataSource(response.data);
        }
      } catch (error) {
        console.error("Error fetching datasource:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchDataSource();
  }, [token, id]);

  const handleSave = async (dataSourceData: any) => {
    try {
      console.log("DataSource updated:", dataSourceData);
      // Show success toast
      toast.success("Datasource updated successfully!");
      // Navigate back to datasources list after successful update
      navigate("/data-sources");
    } catch (error) {
      console.error("Error updating datasource:", error);
      toast.error("Failed to update datasource");
    }
  };

  const handleCancel = () => {
    navigate("/data-sources");
  };

  const handleDelete = () => {
    navigate("/data-sources");
  };

  if (loading) {
    return (
      <div className="p-4 pt-2">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
        </div>
      </div>
    );
  }

  if (!dataSource) {
    return (
      <div className="p-4 pt-2">
        <div className="text-center text-gray-500">DataSource not found</div>
      </div>
    );
  }

  return (
    <div className="p-4 pt-2">
      <CreateDataSourceForm
        dataSource={dataSource}
        onSave={handleSave}
        onCancel={handleCancel}
        onDelete={handleDelete}
      />
    </div>
  );
}
