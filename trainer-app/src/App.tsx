import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { DashboardPage } from './pages/DashboardPage';
import ClientsManagementPage from './pages/ClientsManagementPage';
import { BookingsPage } from './pages/BookingsPage';
import { PackagesPage } from './pages/PackagesPage';
import { SettingsPage } from './pages/SettingsPage';
import PricingPage from './pages/PricingPage';
import BillingPage from './pages/BillingPage';
import WhiteLabelPage from './pages/WhiteLabelPage';
import PagesListPage from './pages/PagesListPage';
import PageBuilderPage from './pages/PageBuilderPage';
import TemplateSelectionPage from './pages/TemplateSelectionPage';
import PublicPageView from './pages/PublicPageView';
import ReportsPage from './pages/ReportsPage';
import PaymentLinksSettings from './pages/PaymentLinksSettings';
import { DashboardLayout } from './layouts/DashboardLayout';
import { useAuthStore } from './store/authStore';

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore();
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
}

function App() {
  return (
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
        </Route>

        {/* Catch all */}
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </Router>
  );
}

export default App;
