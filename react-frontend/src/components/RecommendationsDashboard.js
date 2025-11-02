import React, { useState } from 'react';
import { Card, Button, Row, Col, Alert, Form, ListGroup, Badge, ProgressBar } from 'react-bootstrap';
import { claimsAPI } from '../services/api';

const RecommendationsDashboard = ({ claimData, validationResult, eligibilityResult }) => {
  const [recommendation, setRecommendation] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [reviewData, setReviewData] = useState({
    reviewer_decision: 'APPROVE',
    reviewer_notes: '',
    reviewer_id: ''
  });
  const [isSubmittingReview, setIsSubmittingReview] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleGenerateRecommendation = async () => {
    setIsGenerating(true);
    setError('');
    
    try {
      const requestData = {
        claim_data: Object.keys(claimData).length > 0 ? claimData : {
          claim_id: 'SAMPLE_001',
          patient_id: 'PAT_12345',
          policy_number: 'POL12345678',
          amount_billed: 1500.00,
          service_type: 'diagnostics'
        },
        validation_result: validationResult || { is_valid: true, issues: [] },
        eligibility_result: eligibilityResult || { eligible: true }
      };

      const result = await claimsAPI.generateRecommendation(requestData);
      setRecommendation(result);
    } catch (error) {
      setError(`Recommendation generation failed: ${error.response?.data?.error || error.message}`);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleReviewInputChange = (e) => {
    const { name, value } = e.target;
    setReviewData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmitReview = async () => {
    setIsSubmittingReview(true);
    setError('');
    
    try {
      const validationData = {
        ...reviewData,
        claim_id: claimData.claim_id || 'SAMPLE_001'
      };

      await claimsAPI.validateRecommendation(validationData);
      setSuccess('Review submitted successfully');
      
      // Reset form
      setReviewData({
        reviewer_decision: 'APPROVE',
        reviewer_notes: '',
        reviewer_id: ''
      });
    } catch (error) {
      setError(`Review submission failed: ${error.response?.data?.error || error.message}`);
    } finally {
      setIsSubmittingReview(false);
    }
  };

  const getRecommendationBadge = (rec) => {
    const recLower = rec?.toLowerCase() || '';
    if (recLower.includes('auto_approve')) return 'success';
    if (recLower.includes('approve')) return 'success';
    if (recLower.includes('reject')) return 'danger';
    if (recLower.includes('review')) return 'warning';
    if (recLower.includes('return')) return 'info';
    return 'secondary';
  };

  const getPriorityBadge = (priority) => {
    switch (priority?.toLowerCase()) {
      case 'high': return 'danger';
      case 'medium': return 'warning';
      case 'low': return 'info';
      default: return 'secondary';
    }
  };

  return (
    <div>
      <Row>
        <Col lg={8}>
          <Card>
            <Card.Header>
              <h3><i className="fas fa-robot me-2"></i>AI Recommendations Dashboard</h3>
              <p className="text-muted mb-0">Generate AI recommendations for human validation</p>
            </Card.Header>
            <Card.Body>
              <div className="mb-3">
                <Button 
                  variant="info" 
                  onClick={handleGenerateRecommendation}
                  disabled={isGenerating}
                >
                  {isGenerating ? (
                    <>
                      <i className="fas fa-spinner fa-spin me-2"></i>
                      Generating AI Recommendation...
                    </>
                  ) : (
                    <>
                      <i className="fas fa-robot me-2"></i>
                      Generate AI Recommendation
                    </>
                  )}
                </Button>
              </div>

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

              {recommendation && (
                <Card className="mb-3">
                  <Card.Header>
                    <h5>AI Recommendation</h5>
                  </Card.Header>
                  <Card.Body>
                    <Row>
                      <Col md={6}>
                        <h6>Recommendation:</h6>
                        <Badge bg={getRecommendationBadge(recommendation.recommendation)} className="fs-6">
                          {recommendation.recommendation}
                        </Badge>
                      </Col>
                      <Col md={6}>
                        <h6>Confidence Score:</h6>
                        <ProgressBar 
                          now={recommendation.confidence} 
                          label={`${recommendation.confidence}%`}
                          variant={recommendation.confidence >= 80 ? 'success' : recommendation.confidence >= 60 ? 'warning' : 'danger'}
                        />
                      </Col>
                    </Row>
                    
                    <hr />
                    
                    <div className="mb-3">
                      <h6>Reason:</h6>
                      <p>{recommendation.reason}</p>
                    </div>
                    
                    <div className="mb-3">
                      <h6>Priority Level:</h6>
                      <Badge bg={getPriorityBadge(recommendation.priority)}>
                        {recommendation.priority?.toUpperCase()}
                      </Badge>
                    </div>
                    
                    {recommendation.suggested_actions && recommendation.suggested_actions.length > 0 && (
                      <div className="mb-3">
                        <h6>Suggested Actions:</h6>
                        <ListGroup variant="flush">
                          {recommendation.suggested_actions.map((action, idx) => (
                            <ListGroup.Item key={idx}>
                              <i className="fas fa-chevron-right me-2 text-primary"></i>
                              {action}
                            </ListGroup.Item>
                          ))}
                        </ListGroup>
                      </div>
                    )}
                    
                    {recommendation.overall_score !== undefined && (
                      <div className="mt-3">
                        <small className="text-muted">
                          Overall Score: {recommendation.overall_score.toFixed(1)}/100
                        </small>
                      </div>
                    )}
                  </Card.Body>
                </Card>
              )}
            </Card.Body>
          </Card>
        </Col>
        
        {recommendation && (
          <Col lg={4}>
            <Card>
              <Card.Header>
                <h5>Reviewer Actions</h5>
              </Card.Header>
              <Card.Body>
                <Form>
                  <Form.Group className="mb-3">
                    <Form.Label>Your Decision</Form.Label>
                    <Form.Select
                      name="reviewer_decision"
                      value={reviewData.reviewer_decision}
                      onChange={handleReviewInputChange}
                    >
                      <option value="APPROVE">Approve</option>
                      <option value="REJECT">Reject</option>
                      <option value="RETURN_FOR_CORRECTION">Return for Correction</option>
                      <option value="MANUAL_REVIEW">Requires More Review</option>
                    </Form.Select>
                  </Form.Group>
                  
                  <Form.Group className="mb-3">
                    <Form.Label>Notes</Form.Label>
                    <Form.Control
                      as="textarea"
                      rows={3}
                      name="reviewer_notes"
                      value={reviewData.reviewer_notes}
                      onChange={handleReviewInputChange}
                      placeholder="Enter your review notes..."
                    />
                  </Form.Group>
                  
                  <Form.Group className="mb-3">
                    <Form.Label>Reviewer ID</Form.Label>
                    <Form.Control
                      type="text"
                      name="reviewer_id"
                      value={reviewData.reviewer_id}
                      onChange={handleReviewInputChange}
                      placeholder="Enter your ID"
                    />
                  </Form.Group>
                  
                  <Button 
                    variant="success" 
                    onClick={handleSubmitReview}
                    disabled={isSubmittingReview || !reviewData.reviewer_id}
                  >
                    {isSubmittingReview ? (
                      <>
                        <i className="fas fa-spinner fa-spin me-2"></i>
                        Submitting...
                      </>
                    ) : (
                      <>
                        <i className="fas fa-check me-2"></i>
                        Submit Review
                      </>
                    )}
                  </Button>
                </Form>
                
                {recommendation && (
                  <div className="mt-4">
                    <h6>AI vs Human Comparison</h6>
                    <div className="d-flex justify-content-between">
                      <span>AI Recommendation:</span>
                      <Badge bg={getRecommendationBadge(recommendation.recommendation)}>
                        {recommendation.recommendation}
                      </Badge>
                    </div>
                    <div className="d-flex justify-content-between mt-2">
                      <span>Your Decision:</span>
                      <Badge bg="primary">{reviewData.reviewer_decision}</Badge>
                    </div>
                    <div className="mt-2">
                      <small className="text-muted">
                        Agreement: {recommendation.recommendation === reviewData.reviewer_decision ? '✅' : '❌'}
                      </small>
                    </div>
                  </div>
                )}
              </Card.Body>
            </Card>
          </Col>
        )}
      </Row>
    </div>
  );
};

export default RecommendationsDashboard;