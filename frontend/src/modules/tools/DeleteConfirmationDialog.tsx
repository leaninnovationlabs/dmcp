import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

interface DeleteConfirmationDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm: () => void;
  onCancel: () => void;
  loading?: boolean;
  toolName?: string;
}

const DeleteConfirmationDialog = ({
  open,
  onOpenChange,
  onConfirm,
  onCancel,
  loading = false,
  toolName,
}: DeleteConfirmationDialogProps) => {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Delete Tool</DialogTitle>
          <DialogDescription>
            {toolName
              ? `Are you sure you want to delete "${toolName}"? This action cannot be undone and will permanently remove the tool and all associated data.`
              : "Are you sure you want to delete this tool? This action cannot be undone."}
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <Button
            variant="secondary"
            onClick={onCancel}
            disabled={loading}
          >
            {toolName ? "Cancel" : "Back"}
          </Button>
          <Button
            onClick={onConfirm}
            disabled={loading}
            className="bg-primary hover:bg-primary/90 text-primary-foreground"
          >
            {loading ? "Deleting..." : "Delete"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default DeleteConfirmationDialog;
