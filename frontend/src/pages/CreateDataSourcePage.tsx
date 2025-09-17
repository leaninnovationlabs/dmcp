import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import CreateDataSourceForm from "@/modules/data-sources/CreateDataSourceForm";

export default function CreateDataSourcePage() {
  const navigate = useNavigate();

  const handleSave = async (_dataSource: any) => {
    try {
      // Show success toast
      toast.success("Datasource created successfully!");
      // Keep form open instead of navigating away
      // User can manually close or create another datasource
    } catch (error) {
      console.error("Error saving datasource:", error);
      toast.error("Failed to create datasource");
    }
  };

  const handleCancel = () => {
    navigate("/data-sources");
  };

  return (
    <div className="p-4">
      <CreateDataSourceForm onSave={handleSave} onCancel={handleCancel} />
    </div>
  );
}
