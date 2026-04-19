import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import './styles/theme.css';

// Pages
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';

// Components
import Layout from './components/Layout';

const Placeholder = ({ name }) => (
  <Layout>
    <div className="animate-fade p-8">
      <h1 className="text-4xl font-bold">{name} Page</h1>
      <p className="mt-4 text-dim">This feature is coming soon in the React migration.</p>
    </div>
  </Layout>
);

const PrivateRoute = ({ children }) => {
  const { user, loading } = useAuth();
  if (loading) return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-primary" />
    </div>
  );
  return user ? children : <Navigate to="/login" />;
};

import WaterAnalysisPage from './pages/WaterAnalysisPage';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen">
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route 
              path="/" 
              element={
                <PrivateRoute>
                  <Layout>
                    <DashboardPage />
                  </Layout>
                </PrivateRoute>
              } 
            />
            <Route 
              path="/water" 
              element={
                <PrivateRoute>
                  <Layout>
                    <WaterAnalysisPage />
                  </Layout>
                </PrivateRoute>
              } 
            />
            <Route path="/finance" element={<PrivateRoute><Placeholder name="Financials" /></PrivateRoute>} />
            <Route path="/forum" element={<PrivateRoute><Placeholder name="Forum" /></PrivateRoute>} />
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
