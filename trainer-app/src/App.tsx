import { lazy, Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { DashboardLayout } from './layouts/DashboardLayout';
import { useAuthStore } from './store/authStore';
import { LoadingSpinner } from './components/ui/spinner';

// Lazy load all pages for better performance
const LoginPage = lazy(() => import('./pages/LoginPage'));
const RegisterPage = lazy(() => import('./pages/RegisterPage'));
const DashboardPage = lazy(() => import('./pages/DashboardPage'));
const ClientsManagementPage = lazy(() => import('./pages/ClientsManagementPage'));
const BookingsPage = lazy(() => import('./pages/BookingsPage'));
const PackagesPage = lazy(() => import('./pages/PackagesPage'));
const SettingsPage = lazy(() => import('./pages/SettingsPage'));
const PricingPage = lazy(() => import('./pages/PricingPage'));
const BillingPage = lazy(() => import('./pages/BillingPage'));
const WhiteLabelPage = lazy(() => import('./pages/WhiteLabelPage'));
const PagesListPage = lazy(() => import('./pages/PagesListPage'));
const PageBuilderPage = lazy(() => import('./pages/PageBuilderPage'));
const TemplateSelectionPage = lazy(() => import('./pages/TemplateSelectionPage'));
const PublicPageView = lazy(() => import('./pages/PublicPageView'));
const ReportsPage = lazy(() => import('./pages/ReportsPage'));
const PaymentLinksSettings = lazy(() => import('./pages/PaymentLinksSettings'));
const WorkflowListPage = lazy(() => import('./pages/WorkflowListPage'));
const WorkflowBuilderPage = lazy(() => import('./pages/WorkflowBuilderPage'));
const WorkflowTemplatesPage = lazy(() => import('./pages/WorkflowTemplatesPage'));
const EmailTemplatesPage = lazy(() => import('./pages/EmailTemplatesPage'));
const SMSTemplatesPage = lazy(() => import('./pages/SMSTemplatesPage'));

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore();
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
}

function App() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner />
      </div>
    }>
      <Router>
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/p/:trainerSlug/:pageSlug" element={<PublicPageView />} />

          {/* Protected Routes */}
          <Route
            path="/"
            element={
              <PrivateRoute>
                <DashboardLayout />
              </PrivateRoute>
            }
          >
            <Route index element={<DashboardPage />} />
            <Route path="clients" element={<ClientsManagementPage />} />
            <Route path="bookings" element={<BookingsPage />} />
            <Route path="packages" element={<PackagesPage />} />
            <Route path="settings" element={<SettingsPage />} />
            <Route path="settings/billing" element={<BillingPage />} />
            <Route path="settings/whitelabel" element={<WhiteLabelPage />} />
            <Route path="pricing" element={<PricingPage />} />
            <Route path="pages" element={<PagesListPage />} />
            <Route path="pages/templates" element={<TemplateSelectionPage />} />
            <Route path="pages/new" element={<PageBuilderPage />} />
            <Route path="pages/:id/edit" element={<PageBuilderPage />} />
            <Route path="reports" element={<ReportsPage />} />
            <Route path="payment-links" element={<PaymentLinksSettings />} />
            <Route path="workflows" element={<WorkflowListPage />} />
            <Route path="workflows/templates" element={<WorkflowTemplatesPage />} />
            <Route path="workflows/new" element={<WorkflowBuilderPage />} />
            <Route path="workflows/:id/edit" element={<WorkflowBuilderPage />} />
            <Route path="email-templates" element={<EmailTemplatesPage />} />
            <Route path="sms-templates" element={<SMSTemplatesPage />} />
          </Route>

          {/* Catch all */}
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </Router>
    </Suspense>
  );
}

export default App;
