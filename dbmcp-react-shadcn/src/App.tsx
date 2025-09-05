import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from '@/contexts/AuthContext';
import { Toaster } from '@/components/ui/sonner';
import CloudStorageLayout from '@/components/CloudStorageLayout';
import HomePage from '@/pages/HomePage';
import DataSourcesPage from '@/pages/DataSourcesPage';
import ToolsPage from '@/pages/ToolsPage';
import LoginPage from '@/pages/LoginPage';
import GenerateTokenPage from '@/pages/GenerateTokenPage';
import ChangePasswordPage from '@/pages/ChangePasswordPage';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-black mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/"
        element={<Navigate to="/app" replace />}
      />
      <Route
        path="/app"
        element={
          <ProtectedRoute>
            <CloudStorageLayout>
              <HomePage />
            </CloudStorageLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/data-sources"
        element={
          <ProtectedRoute>
            <CloudStorageLayout>
              <DataSourcesPage />
            </CloudStorageLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/tools"
        element={
          <ProtectedRoute>
            <CloudStorageLayout>
              <ToolsPage />
            </CloudStorageLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/generate-token"
        element={
          <ProtectedRoute>
            <CloudStorageLayout>
              <GenerateTokenPage />
            </CloudStorageLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/change-password"
        element={
          <ProtectedRoute>
            <CloudStorageLayout>
              <ChangePasswordPage />
            </CloudStorageLayout>
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <AppRoutes />
        <Toaster />
      </Router>
    </AuthProvider>
  );
}

export default App
