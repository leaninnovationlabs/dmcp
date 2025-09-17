import React, { useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { PasswordStrengthIndicator } from "@/components/ui/password-strength";
import { apiService, ApiError } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import {
  Eye,
  EyeOff,
  Key,
  Undo2,
  CheckCircle,
  AlertCircle,
  ArrowLeft,
} from "lucide-react";
import { toast } from "sonner";

interface ChangePasswordModuleProps {
  onSuccess?: () => void;
  onCancel?: () => void;
}

export default function ChangePasswordModule({
  onSuccess,
  onCancel,
}: ChangePasswordModuleProps) {
  const { user } = useAuth();
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const validateForm = () => {
    // Check if all fields are filled
    if (!currentPassword || !newPassword || !confirmPassword) {
      setError("Please fill in all password fields.");
      return false;
    }

    // Check if new password is different from current password
    if (currentPassword === newPassword) {
      setError("New password must be different from your current password.");
      return false;
    }

    // Check password strength
    const strength = getPasswordStrength(newPassword);
    if (strength === "weak") {
      setError("Password is too weak. Please choose a stronger password.");
      return false;
    }

    // Check password match
    if (newPassword !== confirmPassword) {
      setError("New password and confirmation password do not match.");
      return false;
    }

    return true;
  };

  const getPasswordStrength = (
    password: string
  ): "weak" | "fair" | "good" | "strong" => {
    if (password.length < 6) return "weak";

    let score = 0;

    // Length contribution
    if (password.length >= 8) score += 1;
    if (password.length >= 12) score += 1;

    // Character variety contribution
    if (/[a-z]/.test(password)) score += 1;
    if (/[A-Z]/.test(password)) score += 1;
    if (/[0-9]/.test(password)) score += 1;
    if (/[^A-Za-z0-9]/.test(password)) score += 1;

    // Determine strength level
    if (score <= 2) return "weak";
    if (score <= 3) return "fair";
    if (score <= 4) return "good";
    return "strong";
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    setIsLoading(true);

    if (!validateForm()) {
      setIsLoading(false);
      return;
    }

    if (!user?.token) {
      setError("Authentication required. Please log in again.");
      setIsLoading(false);
      return;
    }

    try {
      const response = await apiService.changePassword(user.token, {
        current_password: currentPassword,
        new_password: newPassword,
      });

      if (response.success) {
        setSuccess("Password changed successfully!");
        toast.success(
          response.data?.message || "Password changed successfully!"
        );
        resetForm();
        setTimeout(() => {
          onSuccess?.();
        }, 2000);
      } else {
        const errorMessage =
          response.errors?.[0]?.msg ||
          "Failed to change password. Please try again.";
        setError(errorMessage);
        toast.error(errorMessage);
      }
    } catch (err) {
      if (err instanceof ApiError) {
        if (err.status === 400) {
          const errorMessage =
            "Invalid current password. Please check your current password and try again.";
          setError(errorMessage);
          toast.error(errorMessage);
        } else if (err.status === 401) {
          const errorMessage = "Authentication failed. Please log in again.";
          setError(errorMessage);
          toast.error(errorMessage);
          setTimeout(() => {
            window.location.href = "/";
          }, 2000);
        } else {
          const errorMessage =
            "An error occurred while changing your password. Please try again.";
          setError(errorMessage);
          toast.error(errorMessage);
        }
      } else {
        const errorMessage =
          "An error occurred while changing your password. Please try again.";
        setError(errorMessage);
        toast.error(errorMessage);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const resetForm = () => {
    setCurrentPassword("");
    setNewPassword("");
    setConfirmPassword("");
    setShowCurrentPassword(false);
    setShowNewPassword(false);
    setShowConfirmPassword(false);
    setError("");
    setSuccess("");
  };

  const togglePasswordVisibility = (field: "current" | "new" | "confirm") => {
    switch (field) {
      case "current":
        setShowCurrentPassword(!showCurrentPassword);
        break;
      case "new":
        setShowNewPassword(!showNewPassword);
        break;
      case "confirm":
        setShowConfirmPassword(!showConfirmPassword);
        break;
    }
  };

  return (
    <div className="h-full w-full flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-lg w-full space-y-8">
        <div className="text-center">
          <div className="mx-auto h-12 w-12 bg-primary rounded-lg flex items-center justify-center">
            <Key className="h-6 w-6 text-primary-foreground" />
          </div>
          <h2 className="mt-6 text-3xl font-bold text-gray-900">
            Change Password
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Update your account password
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Password Change Form</CardTitle>
            <CardDescription>
              Please enter your current password and choose a new secure
              password.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Current Password */}
              <div className="space-y-2">
                <Label htmlFor="currentPassword">Current Password</Label>
                <div className="relative">
                  <Input
                    id="currentPassword"
                    type={showCurrentPassword ? "text" : "password"}
                    value={currentPassword}
                    onChange={(e) => setCurrentPassword(e.target.value)}
                    placeholder="Enter your current password"
                    required
                    className="pr-10"
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                    onClick={() => togglePasswordVisibility("current")}
                  >
                    {showCurrentPassword ? (
                      <EyeOff className="h-4 w-4 text-gray-400" />
                    ) : (
                      <Eye className="h-4 w-4 text-gray-400" />
                    )}
                  </Button>
                </div>
              </div>

              {/* New Password */}
              <div className="space-y-2">
                <Label htmlFor="newPassword">New Password</Label>
                <div className="relative">
                  <Input
                    id="newPassword"
                    type={showNewPassword ? "text" : "password"}
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    placeholder="Enter your new password"
                    required
                    className="pr-10"
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                    onClick={() => togglePasswordVisibility("new")}
                  >
                    {showNewPassword ? (
                      <EyeOff className="h-4 w-4 text-gray-400" />
                    ) : (
                      <Eye className="h-4 w-4 text-gray-400" />
                    )}
                  </Button>
                </div>
                <PasswordStrengthIndicator password={newPassword} />
              </div>

              {/* Confirm New Password */}
              <div className="space-y-2">
                <Label htmlFor="confirmPassword">Confirm New Password</Label>
                <div className="relative">
                  <Input
                    id="confirmPassword"
                    type={showConfirmPassword ? "text" : "password"}
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Confirm your new password"
                    required
                    className="pr-10"
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                    onClick={() => togglePasswordVisibility("confirm")}
                  >
                    {showConfirmPassword ? (
                      <EyeOff className="h-4 w-4 text-gray-400" />
                    ) : (
                      <Eye className="h-4 w-4 text-gray-400" />
                    )}
                  </Button>
                </div>
                {confirmPassword && newPassword !== confirmPassword && (
                  <p className="text-xs text-red-600">Passwords do not match</p>
                )}
              </div>

              {/* Error Message */}
              {error && (
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              {/* Success Message */}
              {success && (
                <Alert className="border-green-200 bg-green-50">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <AlertDescription className="text-green-800">
                    {success}
                  </AlertDescription>
                </Alert>
              )}

              {/* Form Actions */}
              <div className="flex items-center justify-end space-x-4">
                <Button
                  type="button"
                  variant="secondary"
                  onClick={resetForm}
                  disabled={isLoading}
                >
                  <Undo2 className="h-4 w-4 mr-2" />
                  Reset
                </Button>
                <Button
                  type="submit"
                  disabled={isLoading}
                  className="bg-primary hover:bg-primary/90 text-primary-foreground border border-primary"
                >
                  <Key className="h-4 w-4 mr-2" />
                  {isLoading ? "Changing Password..." : "Change Password"}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>

        {/* Back Button */}
        <div className="flex items-center justify-center">
          <Button
            variant="ghost"
            onClick={onCancel}
            className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 cursor-pointer"
          >
            <ArrowLeft className="h-4 w-4" />
            <span>Back to Home</span>
          </Button>
        </div>
      </div>
    </div>
  );
}
