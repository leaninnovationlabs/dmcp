import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from '@/contexts/AuthContext';
import { SessionProvider, useSession } from '@/contexts/SessionContext';
import { Toaster } from '@/components/ui/sonner';
import SessionExpiredDialog from '@/components/SessionExpiredDialog';
import CloudStorageLayout from '@/components/CloudStorageLayout';
import HomePage from '@/pages/HomePage';
import DataSourcesPage from '@/pages/DataSourcesPage';
import ToolsPage from '@/pages/ToolsPage';
import LoginPage from '@/pages/LoginPage';
import GenerateTokenPage from '@/pages/GenerateTokenPage';
import ChangePasswordPage from '@/pages/ChangePasswordPage';
import ProfilePage from '@/pages/ProfilePage';
import CreateDataSourcePage from '@/pages/CreateDataSourcePage';
import EditDataSourcePage from '@/pages/EditDataSourcePage';

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

function PublicRoute({ children }: { children: React.ReactNode }) {
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

  if (isAuthenticated) {
    return <Navigate to="/app" replace />;
  }

  return <>{children}</>;
}

function NotFoundPage() {
  return (
    <div className="h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-gray-900 mb-4">404</h1>
        <p className="text-xl text-gray-600 mb-8">Page not found</p>
        <button 
          onClick={() => window.history.back()}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Go Back
        </button>
      </div>
    </div>
  );
}

function AppRoutes() {
  return (
    <Routes>
      <Route 
        path="/login" 
        element={
          <PublicRoute>
            <LoginPage />
          </PublicRoute>
        } 
      />
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
      <Route
        path="/profile"
        element={
          <ProtectedRoute>
            <CloudStorageLayout>
              <ProfilePage />
            </CloudStorageLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/data-sources/create"
        element={
          <ProtectedRoute>
            <CloudStorageLayout>
              <CreateDataSourcePage />
            </CloudStorageLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/data-sources/edit/:id"
        element={
          <ProtectedRoute>
            <CloudStorageLayout>
              <EditDataSourcePage />
            </CloudStorageLayout>
          </ProtectedRoute>
        }
      />
      {/* Catch-all route for 404s */}
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}

function SessionHandler() {
  const { isAuthenticated, logout } = useAuth();
  const { isSessionExpired, showSessionExpired, hideSessionExpired } = useSession();


  // Listen for session expired events
  React.useEffect(() => {
    const handleSessionExpired = () => {
      if (isAuthenticated) {
        showSessionExpired();
      }
    };

    window.addEventListener('session-expired', handleSessionExpired);
    return () => {
      window.removeEventListener('session-expired', handleSessionExpired);
    };
  }, [isAuthenticated, showSessionExpired]);

  const handleLogout = () => {
    hideSessionExpired();
    logout();
  };

  return (
    <>
      <AppRoutes />
      <Toaster />
      {isAuthenticated && (
        <SessionExpiredDialog
          isOpen={isSessionExpired}
          onClose={hideSessionExpired}
          onLogout={handleLogout}
        />
      )}
    </>
  );
}

function App() {
  return (
    <AuthProvider>
      <SessionProvider>
        <Router basename="/ui">
          <SessionHandler />
        </Router>
      </SessionProvider>
    </AuthProvider>
  );
}

export default App
