import React, { useState } from 'react';
import { Card, Form, Button, Row, Col, Alert, Table } from 'react-bootstrap';
import { claimsAPI } from '../services/api';

const EligibilityChecker = ({ onEligibilityUpdate }) => {
  const [formData, setFormData] = useState({
    policy_number: '',
    service_type: '',
    service_date: '',
    amount_billed: ''
  });
  
  const [isChecking, setIsChecking] = useState(false);
  const [eligibilityResult, setEligibilityResult] = useState(null);
  const [error, setError] = useState('');

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    setError('');
  };

  const handleCheck = async () => {
    setIsChecking(true);
    setError('');
    
    try {
      const result = await claimsAPI.checkEligibility(formData);
      setEligibilityResult(result);
      onEligibilityUpdate(result);
    } catch (error) {
      setError(`Eligibility check failed: ${error.response?.data?.error || error.message}`);
    } finally {
      setIsChecking(false);
    }
  };

  return (
    <Row>
      <Col lg={6}>
        <Card>
          <Card.Header>
            <h3><i className="fas fa-shield-alt me-2"></i>Check Eligibility</h3>
            <p className="text-muted mb-0">Verify coverage and policy compliance</p>
          </Card.Header>
          <Card.Body>
            <Form>
              <Form.Group className="mb-3">
                <Form.Label>Policy Number *</Form.Label>
                <Form.Control
                  type="text"
                  name="policy_number"
                  value={formData.policy_number}
                  onChange={handleInputChange}
                  placeholder="e.g., POL12345678"
                  required
                />
                <Form.Text className="text-muted">
                  Sample policies: POL12345678, POL87654321, POL11111111
                </Form.Text>
              </Form.Group>
              
              <Form.Group className="mb-3">
                <Form.Label>Service Type *</Form.Label>
                <Form.Select
                  name="service_type"
                  value={formData.service_type}
                  onChange={handleInputChange}
                  required
                >
                  <option value="">Select Service Type</option>
                  <option value="emergency">Emergency</option>
                  <option value="surgery">Surgery</option>
                  <option value="diagnostics">Diagnostics</option>
                  <option value="pharmacy">Pharmacy</option>
                  <option value="general">General</option>
                </Form.Select>
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
              
              {error && (
                <Alert variant="danger">
                  <i className="fas fa-exclamation-triangle me-2"></i>
                  {error}
                </Alert>
              )}
              
              <Button 
                variant="primary" 
                onClick={handleCheck}
                disabled={isChecking || !formData.policy_number || !formData.service_type || !formData.service_date || !formData.amount_billed}
              >
                {isChecking ? (
                  <>
                    <i className="fas fa-spinner fa-spin me-2"></i>
                    Checking...
                  </>
                ) : (
                  <>
                    <i className="fas fa-search me-2"></i>
                    Check Eligibility
                  </>
                )}
              </Button>
            </Form>
          </Card.Body>
        </Card>
      </Col>
      
      {eligibilityResult && (
        <Col lg={6}>
          <Card>
            <Card.Header>
              <h5>Eligibility Results</h5>
            </Card.Header>
            <Card.Body>
              <div className="mb-3">
                <h6>Eligibility Status: 
                  <span className={`badge bg-${eligibilityResult.eligible ? 'success' : 'danger'} ms-2`}>
                    {eligibilityResult.eligible ? 'ELIGIBLE' : 'NOT ELIGIBLE'}
                  </span>
                </h6>
              </div>
              
              {eligibilityResult.coverage_calculation && (
                <div className="mb-3">
                  <h6>Coverage Breakdown:</h6>
                  <Table striped bordered size="sm">
                    <tbody>
                      <tr>
                        <td>Approved Amount</td>
                        <td>${eligibilityResult.coverage_calculation.approved_amount?.toFixed(2) || '0.00'}</td>
                      </tr>
                      <tr>
                        <td>Insurance Payment</td>
                        <td className="text-success">
                          ${eligibilityResult.coverage_calculation.insurance_payment?.toFixed(2) || '0.00'}
                        </td>
                      </tr>
                      <tr>
                        <td>Patient Responsibility</td>
                        <td className="text-warning">
                          ${eligibilityResult.coverage_calculation.patient_responsibility?.toFixed(2) || '0.00'}
                        </td>
                      </tr>
                      <tr>
                        <td>Coverage Percentage</td>
                        <td>
                          <span className="badge bg-info">
                            {eligibilityResult.coverage_calculation.coverage_percentage || 0}%
                          </span>
                        </td>
                      </tr>
                      {eligibilityResult.coverage_calculation.deductible_applied && (
                        <tr>
                          <td>Deductible Applied</td>
                          <td>${eligibilityResult.coverage_calculation.deductible_applied.toFixed(2)}</td>
                        </tr>
                      )}
                      {eligibilityResult.coverage_calculation.copay_applied && (
                        <tr>
                          <td>Copay Applied</td>
                          <td>${eligibilityResult.coverage_calculation.copay_applied.toFixed(2)}</td>
                        </tr>
                      )}
                    </tbody>
                  </Table>
                </div>
              )}
              
              {eligibilityResult.checks && eligibilityResult.checks.length > 0 && (
                <div>
                  <h6>Eligibility Checks:</h6>
                  {eligibilityResult.checks.map((check, idx) => (
                    <Alert 
                      key={idx} 
                      variant={check.passed ? 'success' : 'danger'}
                      className="py-2"
                    >
                      <div className="d-flex justify-content-between align-items-center">
                        <div>
                          <div className="fw-bold">{check.check_type?.replace('_', ' ').toUpperCase()}</div>
                          <small>{check.message}</small>
                        </div>
                        <span className={`badge bg-${check.passed ? 'success' : 'danger'}`}>
                          {check.passed ? 'PASS' : 'FAIL'}
                        </span>
                      </div>
                    </Alert>
                  ))}
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      )}
    </Row>
  );
};

export default EligibilityChecker;