import { useParams, useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { apiService, ApiError } from "@/lib/api";
import { toast } from "sonner";
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { ArrowLeftIcon } from "lucide-react";
import ToolsModule from "@/modules/tools/ToolsModule";

export default function ToolEditPage() {
  const { toolId } = useParams<{ toolId: string }>();
  const navigate = useNavigate();
  const { token } = useAuth();
  
  const [tool, setTool] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const isCreateMode = !toolId || toolId === 'create';

  // Fetch tool details for editing (only if not in create mode)
  useEffect(() => {
    const fetchToolDetails = async () => {
      if (!token || isCreateMode) {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);

        const response = await apiService.getTool(token, parseInt(toolId!));
        
        if (response.success && response.data) {
          setTool(response.data);
        } else {
          setError("Tool not found");
          toast.error("Tool not found");
        }
      } catch (err) {
        console.error("Error fetching tool details:", err);
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

    fetchToolDetails();
  }, [token, toolId, isCreateMode]);

  const handleSave = (updatedTool: any) => {
    if (isCreateMode) {
      toast.success(`Tool "${updatedTool.name}" created successfully!`);
      navigate(`/tools/${updatedTool.id}`);
    } else {
      toast.success(`Tool "${updatedTool.name}" updated successfully!`);
      navigate(`/tools/${toolId}`);
    }
  };

  const handleCancel = () => {
    navigate("/tools");
  };

  const handleDelete = (toolId: string) => {
    navigate("/tools");
  };

  if (loading && !isCreateMode) {
    return (
      <div className="h-full flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-black mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading tool details...</p>
        </div>
      </div>
    );
  }

  if (error || (!isCreateMode && !tool)) {
    return (
      <div className="h-full flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Tool Not Found</h2>
          <p className="text-gray-600 mb-6">{error || "The requested tool could not be found."}</p>
          <Button onClick={() => navigate("/tools")} className="bg-primary hover:bg-primary/90">
            <ArrowLeftIcon className="w-4 h-4 mr-2" />
            Back to Tools
          </Button>
        </div>
      </div>
    );
  }

  return (
    <ToolsModule
      editingTool={tool}
      onModuleChange={() => {}}
      sidebarCollapsed={false}
      onToggleSidebar={() => {}}
    />
  );
}
