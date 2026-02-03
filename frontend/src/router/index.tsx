/**
 * Application Router
 * 
 * Defines all application routes and navigation structure.
 */

import { createBrowserRouter, Navigate } from 'react-router-dom';
import App from '@/App';

/**
 * Application routes configuration
 */
export const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
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
        path: 'documents',
        children: [
          {
            index: true,
            lazy: () => import('@/pages/DocumentsPage'),
          },
          {
            path: 'upload',
            lazy: () => import('@/pages/DocumentUploadPage'),
          },
          {
            path: ':documentId',
            lazy: () => import('@/pages/DocumentDetailPage'),
          },
        ],
      },
      {
        path: 'baselines',
        children: [
          {
            index: true,
            lazy: () => import('@/pages/BaselinesPage'),
          },
          {
            path: 'create',
            lazy: () => import('@/pages/BaselineCreatePage'),
          },
          {
            path: ':baselineId',
            lazy: () => import('@/pages/BaselineDetailPage'),
          },
        ],
      },
      {
        path: 'timelines',
        children: [
          {
            index: true,
            lazy: () => import('@/pages/TimelinesPage'),
          },
          {
            path: 'generate',
            lazy: () => import('@/pages/DraftTimelinePage'),
          },
          {
            path: 'draft/:draftId',
            lazy: () => import('@/pages/DraftTimelinePage'),
          },
          {
            path: 'committed/:committedId',
            lazy: () => import('@/pages/CommittedTimelinePage'),
          },
        ],
      },
      {
        path: 'progress',
        children: [
          {
            index: true,
            lazy: () => import('@/pages/ProgressPage'),
          },
          {
            path: 'timeline/:timelineId',
            lazy: () => import('@/pages/TimelineProgressPage'),
          },
        ],
      },
      {
        path: 'health',
        children: [
          {
            index: true,
            lazy: () => import('@/pages/HealthDashboardPage'),
          },
          {
            path: 'assessment',
            lazy: () => import('@/pages/AssessmentPage'),
          },
          {
            path: 'history',
            lazy: () => import('@/pages/AssessmentHistoryPage'),
          },
          {
            path: ':assessmentId',
            lazy: () => import('@/pages/AssessmentDetailPage'),
          },
        ],
      },
      {
        path: '*',
        lazy: () => import('@/pages/NotFoundPage'),
      },
    ],
  },
]);

export default router;
