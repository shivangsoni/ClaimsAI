import React, { useState } from 'react';
import { Card, Form, Button, Row, Col, Alert, Spinner } from 'react-bootstrap';
import { claimsAPI } from '../services/api';

const ClaimsForm = ({ onClaimDataUpdate, onValidationUpdate }) => {
  const [formData, setFormData] = useState({
    patient_id: '',
    patient_name: '',
    date_of_birth: '',
    policy_number: '',
    provider_name: '',
    provider_id: '',
    service_date: '',
    service_type: 'emergency',
    diagnosis_code: '',
    procedure_code: '',
    amount_billed: ''
  });
  
  const [isValidating, setIsValidating] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [validationResult, setValidationResult] = useState(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    setError('');
  };

  const handleValidate = async () => {
    setIsValidating(true);
    setError('');
    
    try {
      const result = await claimsAPI.validateClaim(formData);
      setValidationResult(result);
      onValidationUpdate(result);
      onClaimDataUpdate(formData);
    } catch (error) {
      setError(`Validation failed: ${error.response?.data?.error || error.message}`);
    } finally {
      setIsValidating(false);
    }
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    setError('');
    
    try {
      const result = await claimsAPI.submitClaim(formData);
      setSuccess(`Claim submitted successfully! Claim ID: ${result.claim_id}`);
      
      // Reset form
      setFormData({
        patient_id: '',
        patient_name: '',
        date_of_birth: '',
        policy_number: '',
        provider_name: '',
        provider_id: '',
        service_date: '',
        service_type: 'emergency',
        diagnosis_code: '',
        procedure_code: '',
        amount_billed: ''
      });
      setValidationResult(null);
    } catch (error) {
      setError(`Submission failed: ${error.response?.data?.error || error.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const getSeverityBadge = (severity) => {
    switch (severity) {
      case 'high':
        return 'danger';
      case 'medium':
        return 'warning';
      case 'low':
        return 'info';
      default:
        return 'secondary';
    }
  };

  return (
    <Row>
      <Col lg={8}>
        <Card>
          <Card.Header>
            <h3><i className="fas fa-edit me-2"></i>Manual Claim Entry</h3>
            <p className="text-muted mb-0">Enter claim details manually for validation and submission</p>
          </Card.Header>
          <Card.Body>
            <Form>
              <Row>
                <Col md={6}>
                  <h5>Patient Information</h5>
                  <Form.Group className="mb-3">
                    <Form.Label>Patient ID *</Form.Label>
                    <Form.Control
                      type="text"
                      name="patient_id"
                      value={formData.patient_id}
                      onChange={handleInputChange}
                      required
                    />
                  </Form.Group>
                  
                  <Form.Group className="mb-3">
                    <Form.Label>Patient Name *</Form.Label>
                    <Form.Control
                      type="text"
                      name="patient_name"
                      value={formData.patient_name}
                      onChange={handleInputChange}
                      required
                    />
                  </Form.Group>
                  
                  <Form.Group className="mb-3">
                    <Form.Label>Date of Birth *</Form.Label>
                    <Form.Control
                      type="date"
                      name="date_of_birth"
                      value={formData.date_of_birth}
                      onChange={handleInputChange}
                      required
                    />
                  </Form.Group>
                  
                  <Form.Group className="mb-3">
                    <Form.Label>Policy Number *</Form.Label>
                    <Form.Control
                      type="text"
                      name="policy_number"
                      value={formData.policy_number}
                      onChange={handleInputChange}
                      required
                    />
                  </Form.Group>
                </Col>
                
                <Col md={6}>
                  <h5>Service Information</h5>
                  <Form.Group className="mb-3">
                    <Form.Label>Provider Name *</Form.Label>
                    <Form.Control
                      type="text"
                      name="provider_name"
                      value={formData.provider_name}
                      onChange={handleInputChange}
                      required
                    />
                  </Form.Group>
                  
                  <Form.Group className="mb-3">
                    <Form.Label>Provider ID *</Form.Label>
                    <Form.Control
                      type="text"
                      name="provider_id"
                      value={formData.provider_id}
                      onChange={handleInputChange}
                      required
                    />
                  </Form.Group>
                  
                  <Form.Group className="mb-3">
                    <Form.Label>Service Date *</Form.Label>
                    <Form.Control
                      type="date"
                      name="service_date"
                      value={formData.service_date}
                      onChange={handleInputChange}
                      required
                    />
                  </Form.Group>
                  
                  <Form.Group className="mb-3">
                    <Form.Label>Service Type</Form.Label>
                    <Form.Select
                      name="service_type"
                      value={formData.service_type}
                      onChange={handleInputChange}
                    >
                      <option value="emergency">Emergency</option>
                      <option value="surgery">Surgery</option>
                      <option value="diagnostics">Diagnostics</option>
                      <option value="pharmacy">Pharmacy</option>
                      <option value="general">General</option>
                    </Form.Select>
                  </Form.Group>
                </Col>
              </Row>
              
              <Row>
                <Col md={4}>
                  <Form.Group className="mb-3">
                    <Form.Label>Diagnosis Code *</Form.Label>
                    <Form.Control
                      type="text"
                      name="diagnosis_code"
                      value={formData.diagnosis_code}
                      onChange={handleInputChange}
                      placeholder="e.g., A12.3"
                      required
                    />
                  </Form.Group>
                </Col>
                
                <Col md={4}>
                  <Form.Group className="mb-3">
                    <Form.Label>Procedure Code *</Form.Label>
                    <Form.Control
                      type="text"
                      name="procedure_code"
                      value={formData.procedure_code}
                      onChange={handleInputChange}
                      required
                    />
                  </Form.Group>
                </Col>
                
                <Col md={4}>
                  <Form.Group className="mb-3">
                    <Form.Label>Amount Billed *</Form.Label>
                    <Form.Control
                      type="number"
                      name="amount_billed"
                      value={formData.amount_billed}
                      onChange={handleInputChange}
                      step="0.01"
                      min="0"
                      required
                    />
                  </Form.Group>
                </Col>
              </Row>
              
              {error && (
                <Alert variant="danger">
                  <i className="fas fa-exclamation-triangle me-2"></i>
                  {error}
                </Alert>
              )}
              
              {success && (
                <Alert variant="success">
                  <i className="fas fa-check-circle me-2"></i>
                  {success}
                </Alert>
              )}
              
              <div className="d-flex gap-2">
                <Button 
                  variant="primary" 
                  onClick={handleValidate}
                  disabled={isValidating || isSubmitting}
                >
                  {isValidating ? (
                    <>
                      <Spinner as="span" animation="border" size="sm" className="me-2" />
                      Validating...
                    </>
                  ) : (
                    <>
                      <i className="fas fa-check me-2"></i>
                      Validate Claim
                    </>
                  )}
                </Button>
                
                <Button 
                  variant="success" 
                  onClick={handleSubmit}
                  disabled={isValidating || isSubmitting || !validationResult}
                >
                  {isSubmitting ? (
                    <>
                      <Spinner as="span" animation="border" size="sm" className="me-2" />
                      Submitting...
                    </>
                  ) : (
                    <>
                      <i className="fas fa-paper-plane me-2"></i>
                      Submit Claim
                    </>
                  )}
                </Button>
              </div>
            </Form>
          </Card.Body>
        </Card>
      </Col>
      
      {validationResult && (
        <Col lg={4}>
          <Card>
            <Card.Header>
              <h5>Validation Results</h5>
            </Card.Header>
            <Card.Body>
              <div className="mb-3">
                <h6>Status: 
                  <span className={`badge bg-${validationResult.is_valid ? 'success' : 'danger'} ms-2`}>
                    {validationResult.is_valid ? 'VALID' : 'INVALID'}
                  </span>
                </h6>
              </div>
              
              {validationResult.recommendation && (
                <div className="mb-3">
                  <h6>Recommendation:</h6>
                  <span className="badge bg-info">{validationResult.recommendation}</span>
                </div>
              )}
              
              {validationResult.issues && validationResult.issues.length > 0 && (
                <div>
                  <h6>Issues Found:</h6>
                  {validationResult.issues.map((issue, idx) => (
                    <Alert 
                      key={idx} 
                      variant={getSeverityBadge(issue.severity)}
                      className="py-2"
                    >
                      <div className="fw-bold">{issue.type || 'Issue'}</div>
                      <small>{issue.message}</small>
                      {issue.field && (
                        <div>
                          <small className="text-muted">Field: {issue.field}</small>
                        </div>
                      )}
                    </Alert>
                  ))}
                </div>
              )}
              
              {(!validationResult.issues || validationResult.issues.length === 0) && (
                <Alert variant="success">
                  <i className="fas fa-check-circle me-2"></i>
                  No issues found!
                </Alert>
              )}
            </Card.Body>
          </Card>
        </Col>
      )}
    </Row>
  );
};

export default ClaimsForm;