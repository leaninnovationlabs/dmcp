import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

interface ToolParameter {
  name: string;
  type: string;
  description?: string;
  required: boolean;
  default?: string;
}

interface ParameterDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSave: () => void;
  onCancel: () => void;
  isEditing: boolean;
  formData: {
    name: string;
    type: string;
    description: string;
    default: string;
    required: boolean;
  };
  onFormChange: (field: string, value: string | boolean) => void;
}

const ParameterDialog = ({
  open,
  onOpenChange,
  onSave,
  onCancel,
  isEditing,
  formData,
  onFormChange,
}: ParameterDialogProps) => {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>
            {isEditing ? "Edit Parameter" : "Add New Parameter"}
          </DialogTitle>
          <DialogDescription>
            Define the parameter details for this tool.
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-4 py-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Name <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => onFormChange("name", e.target.value)}
                placeholder="e.g., start_date"
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-black"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Type <span className="text-red-500">*</span>
              </label>
              <select
                value={formData.type}
                onChange={(e) => onFormChange("type", e.target.value)}
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
                value={formData.description}
                onChange={(e) => onFormChange("description", e.target.value)}
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
                  value={formData.default}
                  onChange={(e) => onFormChange("default", e.target.value)}
                  placeholder="Optional default value"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-black"
                />
              </div>
              <div className="flex items-end pb-2">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.required}
                    onChange={(e) => onFormChange("required", e.target.checked)}
                    className="mr-2"
                  />
                  <span className="text-sm font-medium text-gray-700">
                    Required
                  </span>
                </label>
              </div>
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button
            type="button"
            variant="secondary"
            onClick={onCancel}
          >
            Cancel
          </Button>
          <Button
            type="button"
            onClick={onSave}
            className="bg-primary hover:bg-primary/90 text-primary-foreground"
          >
            {isEditing ? "Update Parameter" : "Save Parameter"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default ParameterDialog;
