/**
 * Router Integration Example
 * 
 * Shows how to integrate RouteGuard with React Router.
 * 
 * This is an example - update your actual router configuration.
 */

import { createBrowserRouter, Navigate } from 'react-router-dom';
import { RouteGuard } from '@/guards';
import App from '@/App';

/**
 * Example router configuration with RouteGuard
 */
export const routerWithGuards = createBrowserRouter([
  {
    path: '/',
    element: (
      <RouteGuard>
        <App />
      </RouteGuard>
    ),
    children: [
      {
        index: true,
        element: <Navigate to="/dashboard" replace />,
      },
      {
        path: 'dashboard',
        lazy: () => import('@/pages/DashboardPage'),
      },
      {
        path: 'timelines',
        lazy: () => import('@/pages/TimelinesPage'),
      },
      {
        path: 'progress',
        lazy: () => import('@/pages/ProgressPage'),
      },
      {
        path: 'health',
        lazy: () => import('@/pages/HealthDashboardPage'),
      },
      {
        path: 'documents/upload',
        lazy: () => import('@/pages/DocumentUploadPage'),
      },
      // ... other routes
    ],
  },
]);

/**
 * Alternative: Guard specific routes only
 */
export const routerWithSelectiveGuards = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      // Guard only protected routes
      {
        path: 'dashboard',
        element: (
          <RouteGuard>
            <DashboardPage />
          </RouteGuard>
        ),
      },
      {
        path: 'progress',
        element: (
          <RouteGuard>
            <ProgressPage />
          </RouteGuard>
        ),
      },
      {
        path: 'health',
        element: (
          <RouteGuard>
            <HealthDashboardPage />
          </RouteGuard>
        ),
      },
      // Unprotected routes (no guard)
      {
        path: 'documents',
        element: <DocumentsPage />,
      },
    ],
  },
]);
