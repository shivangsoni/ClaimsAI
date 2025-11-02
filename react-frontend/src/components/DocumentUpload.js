import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { 
  Card, 
  Button, 
  Form, 
  Alert, 
  Spinner, 
  Badge, 
  Row, 
  Col, 
  ListGroup,
  Accordion,
  ProgressBar 
} from 'react-bootstrap';
import { claimsAPI } from '../services/api';

const DocumentUpload = ({ onClaimDataUpdate, onValidationUpdate }) => {
  const [file, setFile] = useState(null);
  const [claimType, setClaimType] = useState('medical_claim');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [error, setError] = useState('');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [manualText, setManualText] = useState('');

  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      const selectedFile = acceptedFiles[0];
      
      // Validate file size (max 10MB)
      if (selectedFile.size > 10 * 1024 * 1024) {
        setError('File size must be less than 10MB');
        return;
      }
      
      setFile(selectedFile);
      setError('');
      setAnalysisResult(null);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/*': ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']
    },
    multiple: false,
    maxSize: 10 * 1024 * 1024 // 10MB
  });

  const handleUploadAndAnalyze = async () => {
    if (!file) {
      setError('Please select a file to upload');
      return;
    }

    setIsAnalyzing(true);
    setError('');
    setUploadProgress(0);

    try {
      // Simulate progress for better UX
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      const result = await claimsAPI.uploadDocument(file, claimType);
      
      clearInterval(progressInterval);
      setUploadProgress(100);
      
      setAnalysisResult(result);
      
      // Update parent components with extracted data
      if (result.document_analysis && result.document_analysis.extracted_data) {
        onClaimDataUpdate(result.document_analysis.extracted_data);
        onValidationUpdate(result.document_analysis);
      }

    } catch (error) {
      setError(`Analysis failed: ${error.response?.data?.error || error.message}`);
    } finally {
      setIsAnalyzing(false);
      setTimeout(() => setUploadProgress(0), 2000);
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'COMPLETE':
        return <Badge bg="success">Complete</Badge>;
      case 'INCOMPLETE':
        return <Badge bg="warning">Incomplete</Badge>;
      case 'INVALID':
        return <Badge bg="danger">Invalid</Badge>;
      case 'OCR_REQUIRED':
        return <Badge bg="info">OCR Required</Badge>;
      default:
        return <Badge bg="secondary">{status}</Badge>;
    }
  };

  const getSeverityBadge = (severity) => {
    switch (severity) {
      case 'HIGH':
        return <Badge bg="danger">{severity}</Badge>;
      case 'MEDIUM':
        return <Badge bg="warning">{severity}</Badge>;
      case 'LOW':
        return <Badge bg="info">{severity}</Badge>;
      default:
        return <Badge bg="secondary">{severity}</Badge>;
    }
  };

  return (
    <div>
      <Row>
        <Col lg={8}>
          <Card>
            <Card.Header>
              <h3><i className="fas fa-upload me-2"></i>Upload Claim Document</h3>
              <p className="text-muted mb-0">
                Upload PDF or image files for AI-powered analysis using GPT-4
              </p>
            </Card.Header>
            <Card.Body>
              <Form.Group className="mb-3">
                <Form.Label>Claim Type</Form.Label>
                <Form.Select 
                  value={claimType} 
                  onChange={(e) => setClaimType(e.target.value)}
                  disabled={isAnalyzing}
                >
                  <option value="medical_claim">Medical Claim</option>
                  <option value="pharmacy_claim">Pharmacy Claim</option>
                </Form.Select>
              </Form.Group>

              <div 
                {...getRootProps()} 
                className={`border-2 border-dashed rounded p-4 text-center mb-3 ${
                  isDragActive ? 'border-primary bg-light' : 'border-secondary'
                } ${isAnalyzing ? 'opacity-50' : ''}`}
                style={{ cursor: isAnalyzing ? 'not-allowed' : 'pointer' }}
              >
                <input {...getInputProps()} disabled={isAnalyzing} />
                
                {file ? (
                  <div>
                    <i className="fas fa-file-alt fa-3x text-success mb-3"></i>
                    <p className="mb-1"><strong>{file.name}</strong></p>
                    <p className="text-muted">
                      Size: {(file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                ) : isDragActive ? (
                  <div>
                    <i className="fas fa-cloud-upload-alt fa-3x text-primary mb-3"></i>
                    <p>Drop the file here...</p>
                  </div>
                ) : (
                  <div>
                    <i className="fas fa-cloud-upload-alt fa-3x text-muted mb-3"></i>
                    <p>Drag & drop a claim document here, or click to select</p>
                    <p className="text-muted small">
                      Supported formats: PDF, PNG, JPG, JPEG, TIFF, BMP (Max 10MB)
                    </p>
                  </div>
                )}
              </div>

              {uploadProgress > 0 && uploadProgress < 100 && (
                <div className="mb-3">
                  <ProgressBar 
                    animated 
                    now={uploadProgress} 
                    label={`${uploadProgress}%`}
                  />
                </div>
              )}

              {error && (
                <Alert variant="danger">
                  <i className="fas fa-exclamation-triangle me-2"></i>
                  {error}
                </Alert>
              )}

              <Button 
                variant="primary" 
                onClick={handleUploadAndAnalyze}
                disabled={!file || isAnalyzing}
                className="me-2"
              >
                {isAnalyzing ? (
                  <>
                    <Spinner as="span" animation="border" size="sm" className="me-2" />
                    Analyzing with GPT-4...
                  </>
                ) : (
                  <>
                    <i className="fas fa-robot me-2"></i>
                    Analyze with AI
                  </>
                )}
              </Button>

              {file && (
                <Button 
                  variant="outline-secondary" 
                  onClick={() => {
                    setFile(null);
                    setAnalysisResult(null);
                    setError('');
                  }}
                  disabled={isAnalyzing}
                >
                  Clear File
                </Button>
              )}
            </Card.Body>
          </Card>

          {/* Manual Text Input Alternative */}
          <Card className="mt-3">
            <Card.Header>
              <h5><i className="fas fa-keyboard me-2"></i>Or Enter Text Manually</h5>
              <p className="text-muted mb-0 small">
                If you can't upload a file or OCR is unavailable, paste or type your claim text here
              </p>
            </Card.Header>
            <Card.Body>
              <Form.Group className="mb-3">
                <Form.Control 
                  as="textarea" 
                  rows={8}
                  placeholder="Paste your claim document text here...&#10;&#10;Example:&#10;Patient Name: John Doe&#10;Policy Number: POL123456&#10;Date of Service: 2024-11-01&#10;Provider: Medical Center&#10;Diagnosis: Annual checkup&#10;Amount: $150.00"
                  value={manualText}
                  onChange={(e) => setManualText(e.target.value)}
                  disabled={isAnalyzing}
                />
              </Form.Group>
              <Button 
                variant="success" 
                onClick={async () => {
                  if (!manualText.trim()) {
                    setError('Please enter some text to analyze');
                    return;
                  }
                  setError('');
                  setIsAnalyzing(true);
                  try {
                    // Call the API to analyze manually entered text
                    const response = await claimsAPI.analyzeText(manualText, claimType);
                    setAnalysisResult(response.data);
                    
                    // Update parent components with extracted data
                    if (response.data.document_analysis && response.data.document_analysis.extracted_data) {
                      onClaimDataUpdate(response.data.document_analysis.extracted_data);
                      onValidationUpdate(response.data.document_analysis);
                    }
                  } catch (error) {
                    setError(`Analysis failed: ${error.message}`);
                  } finally {
                    setIsAnalyzing(false);
                  }
                }}
                disabled={!manualText.trim() || isAnalyzing}
                className="me-2"
              >
                {isAnalyzing ? (
                  <>
                    <Spinner as="span" animation="border" size="sm" className="me-2" />
                    Analyzing Text...
                  </>
                ) : (
                  <>
                    <i className="fas fa-search me-2"></i>
                    Analyze Text
                  </>
                )}
              </Button>
              <Button 
                variant="outline-secondary" 
                onClick={() => setManualText('')}
                disabled={isAnalyzing}
              >
                Clear Text
              </Button>
            </Card.Body>
          </Card>
        </Col>

        {analysisResult && (
          <Col lg={4}>
            <Card>
              <Card.Header>
                <h5>Quick Summary</h5>
              </Card.Header>
              <Card.Body>
                <div className="mb-2">
                  <strong>Status: </strong>
                  {getStatusBadge(analysisResult.document_analysis?.overall_status)}
                </div>
                <div className="mb-2">
                  <strong>Completeness: </strong>
                  <span className="badge bg-info">
                    {analysisResult.document_analysis?.completeness_score || 0}%
                  </span>
                </div>
                <div className="mb-2">
                  <strong>Best Match: </strong>
                  <Badge bg="secondary">
                    {analysisResult.comparison_with_approved?.best_match_type?.replace('_', ' ').toUpperCase()}
                  </Badge>
                </div>
                <div className="mb-2">
                  <strong>Confidence: </strong>
                  <Badge bg="primary">
                    {analysisResult.document_analysis?.confidence_level || 0}%
                  </Badge>
                </div>
              </Card.Body>
            </Card>
          </Col>
        )}
      </Row>

      {analysisResult && (
        <Row className="mt-4">
          <Col>
            {/* Special display for OCR Required scenario */}
            {analysisResult.document_analysis?.overall_status === 'OCR_REQUIRED' && (
              <Alert variant="info" className="mb-4">
                <Alert.Heading><i className="fas fa-image me-2"></i>Image Processing Required</Alert.Heading>
                <p>This appears to be an image file that requires OCR (Optical Character Recognition) to extract text.</p>
                <hr />
                <div className="mb-3">
                  <strong>To enable image text extraction:</strong>
                  <ol className="mt-2">
                    <li>Install Tesseract OCR from: <a href="https://github.com/UB-Mannheim/tesseract/wiki" target="_blank" rel="noopener noreferrer">https://github.com/UB-Mannheim/tesseract/wiki</a></li>
                    <li>Add Tesseract to your system PATH</li>
                    <li>Restart the backend server</li>
                  </ol>
                </div>
                <div>
                  <strong>Alternative options:</strong>
                  <ul className="mt-2">
                    <li>Convert your image to a PDF format</li>
                    <li>Manually type the document content into the Claims Form tab</li>
                    <li>Use an online OCR tool to extract text first</li>
                  </ul>
                </div>
              </Alert>
            )}

            <Accordion>
              <Accordion.Item eventKey="0">
                <Accordion.Header>
                  <i className="fas fa-search me-2"></i>
                  Detailed Analysis Results
                </Accordion.Header>
                <Accordion.Body>
                  <Row>
                    <Col md={6}>
                      <h6>Missing Sections</h6>
                      {analysisResult.document_analysis?.missing_sections?.length > 0 ? (
                        <ListGroup variant="flush">
                          {analysisResult.document_analysis.missing_sections.map((section, idx) => (
                            <ListGroup.Item key={idx} className="d-flex justify-content-between">
                              <span>{section}</span>
                              <Badge bg="warning">Missing</Badge>
                            </ListGroup.Item>
                          ))}
                        </ListGroup>
                      ) : (
                        <Alert variant="success">All required sections found!</Alert>
                      )}
                    </Col>
                    <Col md={6}>
                      <h6>Data Quality Issues</h6>
                      {analysisResult.document_analysis?.data_quality_issues?.length > 0 ? (
                        <ListGroup variant="flush">
                          {analysisResult.document_analysis.data_quality_issues.map((issue, idx) => (
                            <ListGroup.Item key={idx}>
                              <div className="d-flex justify-content-between align-items-start">
                                <div>
                                  <strong>{issue.section}</strong>
                                  <br />
                                  <small>{issue.issue}</small>
                                </div>
                                {getSeverityBadge(issue.severity)}
                              </div>
                            </ListGroup.Item>
                          ))}
                        </ListGroup>
                      ) : (
                        <Alert variant="success">No quality issues detected!</Alert>
                      )}
                    </Col>
                  </Row>
                </Accordion.Body>
              </Accordion.Item>

              <Accordion.Item eventKey="1">
                <Accordion.Header>
                  <i className="fas fa-lightbulb me-2"></i>
                  Improvement Suggestions
                </Accordion.Header>
                <Accordion.Body>
                  <Row>
                    <Col md={6}>
                      <h6 className="text-danger">Priority Fixes</h6>
                      {analysisResult.improvement_suggestions?.priority_fixes?.length > 0 ? (
                        <ListGroup>
                          {analysisResult.improvement_suggestions.priority_fixes.map((fix, idx) => (
                            <ListGroup.Item key={idx}>
                              <strong>{fix.type?.replace('_', ' ').toUpperCase()}</strong>
                              <br />
                              <small>{fix.description}</small>
                            </ListGroup.Item>
                          ))}
                        </ListGroup>
                      ) : (
                        <Alert variant="success">No priority fixes needed!</Alert>
                      )}
                    </Col>
                    <Col md={6}>
                      <h6 className="text-warning">Optional Improvements</h6>
                      {analysisResult.improvement_suggestions?.optional_improvements?.length > 0 ? (
                        <ListGroup>
                          {analysisResult.improvement_suggestions.optional_improvements.map((improvement, idx) => (
                            <ListGroup.Item key={idx}>
                              <strong>{improvement.section}</strong>
                              <br />
                              <small>{improvement.improvement}</small>
                              <br />
                              {getSeverityBadge(improvement.severity)}
                            </ListGroup.Item>
                          ))}
                        </ListGroup>
                      ) : (
                        <Alert variant="info">No optional improvements suggested</Alert>
                      )}
                    </Col>
                  </Row>
                </Accordion.Body>
              </Accordion.Item>

              <Accordion.Item eventKey="2">
                <Accordion.Header>
                  <i className="fas fa-extract me-2"></i>
                  Extracted Data
                </Accordion.Header>
                <Accordion.Body>
                  <Row>
                    {analysisResult.document_analysis?.extracted_data && 
                     Object.entries(analysisResult.document_analysis.extracted_data).map(([key, value]) => (
                      <Col md={6} key={key} className="mb-2">
                        <strong>{key.replace('_', ' ').toUpperCase()}:</strong>
                        <br />
                        <span className={value ? 'text-success' : 'text-muted'}>
                          {value || 'Not found'}
                        </span>
                      </Col>
                    ))}
                  </Row>
                </Accordion.Body>
              </Accordion.Item>

              <Accordion.Item eventKey="3">
                <Accordion.Header>
                  <i className="fas fa-file-alt me-2"></i>
                  Extracted Text Preview
                </Accordion.Header>
                <Accordion.Body>
                  <div style={{ maxHeight: '300px', overflow: 'auto', backgroundColor: '#f8f9fa', padding: '10px', borderRadius: '5px' }}>
                    <pre style={{ fontSize: '0.8rem', margin: 0 }}>
                      {analysisResult.extracted_text_preview}
                    </pre>
                  </div>
                </Accordion.Body>
              </Accordion.Item>
            </Accordion>
          </Col>
        </Row>
      )}
    </div>
  );
};

export default DocumentUpload;