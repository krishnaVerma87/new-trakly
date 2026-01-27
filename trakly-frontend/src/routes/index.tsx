import { createBrowserRouter, Navigate } from 'react-router-dom';
import ProtectedRoute from '@/components/layout/ProtectedRoute';
import MainLayout from '@/components/layout/MainLayout';
import LoginPage from '@/pages/LoginPage';
import { SignupPage } from '@/pages/SignupPage';
import DashboardPage from '@/pages/DashboardPage';
import ProjectsPage from '@/pages/ProjectsPage';
import { IssuesPage } from '@/pages/IssuesPage';
import { CreateIssuePage } from '@/pages/CreateIssuePage';
import { IssueDetailPage } from '@/pages/IssueDetailPage';
import { SprintsPage } from '@/pages/SprintsPage';
import { SprintBoardPage } from '@/pages/SprintBoardPage';
import FeaturesPage from '@/pages/FeaturesPage';
import FeatureDetailPage from '@/pages/FeatureDetailPage';
import ProjectSettingsPage from '@/pages/ProjectSettingsPage';
import SettingsPage from '@/pages/SettingsPage';
import { WikiPage } from '@/pages/WikiPage';
import { NotificationsPage } from '@/pages/NotificationsPage';

export const router = createBrowserRouter([
  {
    path: '/signup',
    element: <SignupPage />,
  },
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/',
    element: (
      <ProtectedRoute>
        <MainLayout />
      </ProtectedRoute>
    ),
    children: [
      {
        index: true,
        element: <Navigate to="/dashboard" replace />,
      },
      {
        path: 'dashboard',
        element: <DashboardPage />,
      },
      {
        path: 'projects',
        element: <ProjectsPage />,
      },
      {
        path: 'projects/:projectId/issues',
        element: <IssuesPage />,
      },
      {
        path: 'projects/:projectId/issues/new',
        element: <CreateIssuePage />,
      },
      {
        path: 'projects/:projectId/issues/:issueKey',
        element: <IssueDetailPage />,
      },
      {
        path: 'projects/:projectId/sprints',
        element: <SprintsPage />,
      },
      {
        path: 'projects/:projectId/sprints/:sprintId/board',
        element: <SprintBoardPage />,
      },
      {
        path: 'projects/:projectId/features',
        element: <FeaturesPage />,
      },
      {
        path: 'projects/:projectId/features/:featureId',
        element: <FeatureDetailPage />,
      },
      {
        path: 'projects/:projectId/wiki',
        element: <WikiPage />,
      },
      {
        path: 'projects/:projectId/wiki/:slug',
        element: <WikiPage />,
      },
      {
        path: 'projects/:projectId/wiki/:slug/:action',
        element: <WikiPage />,
      },
      {
        path: 'projects/:projectId/settings',
        element: <ProjectSettingsPage />,
      },
      {
        path: 'settings',
        element: <SettingsPage />,
      },
      {
        path: 'notifications',
        element: <NotificationsPage />,
      },
    ],
  },
]);
