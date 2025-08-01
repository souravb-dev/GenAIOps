import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryProvider } from './providers/QueryProvider';
import { AuthProvider } from './contexts/AuthContext';
import { ErrorBoundary } from './components/ui/ErrorBoundary';
import { AppLayout } from './components/layout/AppLayout';
import { LoginForm } from './components/auth/LoginForm';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { DashboardPage } from './components/pages/DashboardPage';
import { MonitoringPage } from './components/pages/MonitoringPage';
import { AlertsPage } from './components/pages/AlertsPage';
import './App.css';
import { NotificationProvider } from './contexts/NotificationContext';

// Placeholder components for future modules
function CloudResourcesPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Cloud Resources</h1>
      <p className="text-gray-600 dark:text-gray-400">
        Cloud resources module will be implemented in the next tasks.
      </p>
    </div>
  );
}



function KubernetesPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Kubernetes</h1>
      <p className="text-gray-600 dark:text-gray-400">
        Kubernetes module will be implemented in future tasks.
      </p>
    </div>
  );
}

function CostAnalysisPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Cost Analysis</h1>
      <p className="text-gray-600 dark:text-gray-400">
        Cost analysis module will be implemented in future tasks.
      </p>
    </div>
  );
}

function AutomationPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Automation</h1>
      <p className="text-gray-600 dark:text-gray-400">
        Automation module will be implemented in future tasks.
      </p>
    </div>
  );
}

function SettingsPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Settings</h1>
      <p className="text-gray-600 dark:text-gray-400">
        Settings module will be implemented in future tasks.
      </p>
    </div>
  );
}

function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
      <div className="text-center">
        <div className="text-gray-400 text-6xl mb-4">
          <i className="fas fa-exclamation-triangle"></i>
        </div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Page Not Found</h2>
        <p className="text-gray-600 dark:text-gray-400 mb-4">
          The page you're looking for doesn't exist.
        </p>
        <a
          href="/dashboard"
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md transition-colors"
        >
          Go to Dashboard
        </a>
      </div>
    </div>
  );
}

function App() {
  return (
    <QueryProvider>
      <NotificationProvider>
        <AuthProvider>
          <BrowserRouter>
            <Routes>
              {/* Public routes */}
              <Route path="/login" element={<LoginForm />} />
              
              {/* Protected routes with layout */}
              <Route
                path="/dashboard"
                element={
                  <ProtectedRoute requiredPermissions={['can_view_dashboard']}>
                    <AppLayout>
                      <DashboardPage />
                    </AppLayout>
                  </ProtectedRoute>
                }
              />
              
              <Route
                path="/cloud-resources"
                element={
                  <ProtectedRoute requiredPermissions={['can_view_dashboard']}>
                    <AppLayout>
                      <CloudResourcesPage />
                    </AppLayout>
                  </ProtectedRoute>
                }
              />
              
              <Route
                path="/monitoring"
                element={
                  <ProtectedRoute requiredPermissions={['can_view_alerts']}>
                    <AppLayout>
                      <MonitoringPage />
                    </AppLayout>
                  </ProtectedRoute>
                }
              />
              
              <Route
                path="/alerts"
                element={
                  <ProtectedRoute requiredPermissions={['can_view_alerts']}>
                    <AppLayout>
                      <AlertsPage />
                    </AppLayout>
                  </ProtectedRoute>
                }
              />
              
              <Route
                path="/kubernetes"
                element={
                  <ProtectedRoute requiredPermissions={['can_view_pod_analyzer']}>
                    <AppLayout>
                      <KubernetesPage />
                    </AppLayout>
                  </ProtectedRoute>
                }
              />
              
              <Route
                path="/cost-analysis"
                element={
                  <ProtectedRoute requiredPermissions={['can_view_cost_analyzer']}>
                    <AppLayout>
                      <CostAnalysisPage />
                    </AppLayout>
                  </ProtectedRoute>
                }
              />
              
              <Route
                path="/automation"
                element={
                  <ProtectedRoute requiredPermissions={['can_execute_remediation']}>
                    <AppLayout>
                      <AutomationPage />
                    </AppLayout>
                  </ProtectedRoute>
                }
              />
              
              <Route
                path="/settings"
                element={
                  <ProtectedRoute requiredPermissions={['can_manage_users']}>
                    <AppLayout>
                      <SettingsPage />
                    </AppLayout>
                  </ProtectedRoute>
                }
              />
              
              {/* Default redirect */}
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              
              {/* 404 page */}
              <Route path="*" element={<NotFound />} />
            </Routes>
          </BrowserRouter>
        </AuthProvider>
      </NotificationProvider>
    </QueryProvider>
  );
}

export default App; 