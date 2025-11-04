import React, { useState, useEffect } from 'react';
import { Container, Nav, Navbar, Alert } from 'react-bootstrap';
import DocumentUpload from './components/DocumentUpload';
import { claimsAPI } from './services/api';
import 'bootstrap/dist/css/bootstrap.min.css';
import '@fortawesome/fontawesome-free/css/all.min.css';

function App() {
  const [apiStatus, setApiStatus] = useState('checking');
  const [currentClaimData, setCurrentClaimData] = useState({});
  const [currentValidationResult, setCurrentValidationResult] = useState({});

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
    setCurrentClaimData(data);
  };

  const handleValidationUpdate = (result) => {
    setCurrentValidationResult(result);
  };

  return (
    <div className="App">
      <Navbar bg="primary" variant="dark" expand="lg">
        <Container>
          <Navbar.Brand href="#home">
            <i className="fas fa-brain me-2"></i>
            Claims AI - Document Processing
          </Navbar.Brand>
          <Navbar.Toggle aria-label="Toggle navigation" />
          <Navbar.Collapse>
            <Nav className="me-auto">
              <Nav.Link active>
                <i className="fas fa-upload me-2"></i>
                Document Analysis
              </Nav.Link>
            </Nav>
            <Navbar.Text>
              <span className={`badge ${apiStatus === 'connected' ? 'bg-success' : 'bg-danger'}`}>
                API: {apiStatus === 'connected' ? 'Connected' : 'Disconnected'}
              </span>
            </Navbar.Text>
          </Navbar.Collapse>
        </Container>
      </Navbar>

      <Container className="mt-4">
        {apiStatus === 'disconnected' && (
          <Alert variant="warning">
            <i className="fas fa-exclamation-triangle me-2"></i>
            Backend API is not responding. Please ensure the Python backend is running on http://localhost:5000
          </Alert>
        )}

        <div className="tab-content">
          <DocumentUpload 
            onClaimDataUpdate={handleClaimDataUpdate}
            onValidationUpdate={handleValidationUpdate}
          />
        </div>
      </Container>

      <footer className="bg-light text-center text-lg-start mt-5">
        <div className="text-center p-3">
          © 2025 Claims AI System - AI-Powered Document Processing with GPT-4 Mini
        </div>
      </footer>
    </div>
  );
}

export default App;