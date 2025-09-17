import { useState, useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { LogOut, Clock } from "lucide-react";

interface SessionExpiredDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onLogout: () => void;
}

export default function SessionExpiredDialog({
  isOpen,
  onClose,
  onLogout,
}: SessionExpiredDialogProps) {
  const [countdown, setCountdown] = useState(3);

  useEffect(() => {
    if (!isOpen) return;

    setCountdown(3);
    const timer = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          onLogout();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [isOpen, onLogout]);

  const handleLogoutNow = () => {
    onLogout();
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <div className="flex items-center space-x-2">
            <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
              <LogOut className="w-5 h-5 text-red-600" />
            </div>
            <div>
              <DialogTitle className="text-lg font-semibold text-gray-900">
                Session Expired
              </DialogTitle>
              <DialogDescription className="text-gray-600">
                Your session has expired for security reasons.
              </DialogDescription>
            </div>
          </div>
        </DialogHeader>

        <div className="py-4">
          <div className="flex items-center justify-center space-x-2 text-gray-700">
            <Clock className="w-4 h-4" />
            <span>Logging you out in</span>
            <span className="font-bold text-lg text-red-600">{countdown}</span>
            <span>second{countdown !== 1 ? "s" : ""}</span>
          </div>
        </div>

        <div className="flex justify-end space-x-3">
          <Button variant="secondary" onClick={handleLogoutNow}>
            Logout Now
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
