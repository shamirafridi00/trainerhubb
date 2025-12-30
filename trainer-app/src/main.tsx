import { StrictMode, useEffect } from 'react'
import { createRoot } from 'react-dom/client'
import { HelmetProvider } from 'react-helmet-async'
import './index.css'
import App from './App.tsx'
import { useAuthStore } from './store/authStore'

function Root() {
  const loadUser = useAuthStore((state) => state.loadUser);

  useEffect(() => {
    // Load user on app start if token exists
    loadUser();
  }, [loadUser]);

  return <App />;
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <HelmetProvider>
      <Root />
    </HelmetProvider>
  </StrictMode>,
)
