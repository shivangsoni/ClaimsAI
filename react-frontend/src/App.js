import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import ClaimsDashboard from './components/ClaimsDashboard';
import NewClaimForm from './components/NewClaimForm';
import ClaimDetailPage from './components/ClaimDetailPage';
import DocumentUpload from './components/DocumentUpload.jsx';
import { Toaster } from './components/ui/toaster';
import { claimsAPI } from './services/api';

function App() {
  const [apiStatus, setApiStatus] = useState('checking');

  useEffect(() => {
    checkApiHealth();
  }, []);

  const checkApiHealth = async () => {
    try {
      await claimsAPI.healthCheck();
      setApiStatus('connected');
    } catch (error) {
      setApiStatus('disconnected');
    }
  };

  const handleClaimDataUpdate = (data) => {
    // Handle claim data updates
    console.log('Claim data updated:', data);
  };

  const handleValidationUpdate = (result) => {
    // Handle validation result updates
    console.log('Validation result updated:', result);
  };

  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<ClaimsDashboard />} />
          <Route path="/claims/new" element={<NewClaimForm />} />
          <Route path="/claims/:id" element={<ClaimDetailPage />} />
          <Route 
            path="/document-upload" 
            element={
              <DocumentUpload 
                onClaimDataUpdate={handleClaimDataUpdate}
                onValidationUpdate={handleValidationUpdate}
                apiStatus={apiStatus}
              />
            } 
          />
        </Routes>
        <Toaster />
      </div>
    </Router>
  );
}

export default App;