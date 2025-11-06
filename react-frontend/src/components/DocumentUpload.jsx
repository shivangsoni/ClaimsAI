import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Link } from 'react-router-dom';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Badge } from './ui/badge';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from './ui/collapsible';
import { ArrowLeft, Upload, FileText, CheckCircle2, XCircle, AlertTriangle, ChevronDown, Brain } from 'lucide-react';
import { claimsAPI } from '../services/api';

const DocumentUpload = ({ onClaimDataUpdate, onValidationUpdate, apiStatus }) => {
  const [file, setFile] = useState(null);
  const [claimType, setClaimType] = useState('medical_claim');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [error, setError] = useState('');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [openSections, setOpenSections] = useState({
    extracted: true,
    validation: true,
    recommendations: true
  });

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
      setUploadProgress(0);
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

  const toggleSection = (section) => {
    setOpenSections(prev => ({ ...prev, [section]: !prev[section] }));
  };

  const analyzeDocument = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setIsAnalyzing(true);
    setError('');
    setUploadProgress(0);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('claim_type', claimType);

      // Simulate progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return prev;
          }
          return prev + 10;
        });
      }, 200);

      const result = await claimsAPI.uploadDocument(file, claimType);
      
      clearInterval(progressInterval);
      setUploadProgress(100);
      
      setAnalysisResult(result);
      
      if (onClaimDataUpdate) {
        onClaimDataUpdate(result.extracted_data || {});
      }
      
      if (onValidationUpdate) {
        onValidationUpdate(result.validation_result || {});
      }

    } catch (error) {
      setError(`Analysis failed: ${error.response?.data?.error || error.message}`);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const removeFile = () => {
    setFile(null);
    setAnalysisResult(null);
    setError('');
    setUploadProgress(0);
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'high': return 'destructive';
      case 'medium': return 'warning';
      case 'low': return 'info';
      default: return 'secondary';
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link
              to="/dashboard"
              className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors"
            >
              <ArrowLeft className="h-4 w-4" />
              <span className="text-sm">Back to Dashboard</span>
            </Link>
            <div className="flex items-center gap-2">
              <Brain className="h-6 w-6 text-primary" />
              <h1 className="text-xl font-bold text-foreground">Claims AI - Document Processing</h1>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant={apiStatus === 'connected' ? 'success' : 'destructive'}>
              API: {apiStatus === 'connected' ? 'Connected' : 'Disconnected'}
            </Badge>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        {apiStatus === 'disconnected' && (
          <Card className="border-yellow-200 bg-yellow-50 mb-6">
            <CardContent className="p-4">
              <div className="flex items-center gap-2 text-yellow-800">
                <AlertTriangle className="h-4 w-4" />
                <span className="text-sm">
                  Backend API is not responding. Please ensure the Python backend is running on http://localhost:8000
                </span>
              </div>
            </CardContent>
          </Card>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Upload and Controls */}
          <div className="lg:col-span-1 space-y-6">
            <Card className="border-border">
              <CardContent className="p-6">
                <h2 className="text-xl font-semibold text-foreground mb-4">Document Upload</h2>
                <p className="text-sm text-muted-foreground mb-6">
                  Upload medical documents for AI-powered analysis and validation
                </p>
                
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="claimType" className="text-sm font-medium">Claim Type</Label>
                    <Select value={claimType} onValueChange={setClaimType}>
                      <SelectTrigger className="w-full mt-2">
                        <SelectValue placeholder="Select claim type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="medical_claim">Medical Claim</SelectItem>
                        <SelectItem value="pharmacy_claim">Pharmacy Claim</SelectItem>
                        <SelectItem value="dental_claim">Dental Claim</SelectItem>
                        <SelectItem value="vision_claim">Vision Claim</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div
                    {...getRootProps()}
                    className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                      isDragActive
                        ? 'border-primary bg-primary/5'
                        : 'border-border hover:border-primary/50'
                    }`}
                  >
                    <input {...getInputProps()} />
                    <Upload className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                    {isDragActive ? (
                      <p className="text-sm text-primary">Drop the file here...</p>
                    ) : (
                      <div>
                        <p className="text-sm font-medium text-foreground mb-1">
                          Click to upload or drag and drop
                        </p>
                        <p className="text-xs text-muted-foreground">
                          PDF, PNG, JPG, TIFF, BMP (max 10MB)
                        </p>
                      </div>
                    )}
                  </div>

                  {file && (
                    <Card className="bg-muted/50">
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <FileText className="h-8 w-8 text-primary" />
                            <div>
                              <p className="text-sm font-medium text-foreground">{file.name}</p>
                              <p className="text-xs text-muted-foreground">
                                {(file.size / 1024 / 1024).toFixed(2)} MB
                              </p>
                            </div>
                          </div>
                          <Button variant="ghost" size="sm" onClick={removeFile}>
                            <XCircle className="h-4 w-4" />
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  )}

                  {uploadProgress > 0 && uploadProgress < 100 && (
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Processing...</span>
                        <span className="text-foreground">{uploadProgress}%</span>
                      </div>
                      <div className="w-full bg-muted rounded-full h-2">
                        <div
                          className="bg-primary h-2 rounded-full transition-all duration-300"
                          style={{ width: `${uploadProgress}%` }}
                        />
                      </div>
                    </div>
                  )}

                  {error && (
                    <Card className="border-red-200 bg-red-50">
                      <CardContent className="p-4">
                        <div className="flex items-center gap-2 text-red-800">
                          <XCircle className="h-4 w-4" />
                          <span className="text-sm">{error}</span>
                        </div>
                      </CardContent>
                    </Card>
                  )}

                  <Button
                    onClick={analyzeDocument}
                    disabled={!file || isAnalyzing || apiStatus === 'disconnected'}
                    className="w-full"
                  >
                    {isAnalyzing ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                        Analyzing Document...
                      </>
                    ) : (
                      <>
                        <Brain className="h-4 w-4 mr-2" />
                        Analyze with AI
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right Column - Results */}
          <div className="lg:col-span-2 space-y-6">
            {analysisResult && (
              <>
                {/* Success Message */}
                <Card className="border-green-200 bg-green-50">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2 text-green-800">
                        <CheckCircle2 className="h-5 w-5" />
                        <div>
                          <p className="text-sm font-semibold">Document Analysis Complete!</p>
                          <p className="text-xs">Claim {analysisResult.claim_id} has been created and saved.</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Link to="/dashboard">
                          <Button size="sm" variant="outline" className="text-green-800 border-green-300 hover:bg-green-100">
                            View Dashboard
                          </Button>
                        </Link>
                        {analysisResult.claim_id && (
                          <Link to={`/claims/${analysisResult.claim_id}`}>
                            <Button size="sm" className="bg-green-700 hover:bg-green-800 text-white">
                              View Claim Details
                            </Button>
                          </Link>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
                
                {/* Extracted Data */}
                <Card className="border-border">
                  <CardContent className="p-6">
                    <Collapsible open={openSections.extracted} onOpenChange={() => toggleSection('extracted')}>
                      <CollapsibleTrigger className="flex items-center justify-between w-full hover:opacity-80 transition-opacity">
                        <h3 className="text-lg font-semibold text-foreground">Extracted Data</h3>
                        <ChevronDown className={`h-5 w-5 transition-transform ${openSections.extracted ? 'rotate-180' : ''}`} />
                      </CollapsibleTrigger>
                      <CollapsibleContent className="pt-4">
                        {analysisResult.extracted_data ? (
                          <div className="bg-primary/5 rounded-lg p-4">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                              {Object.entries(analysisResult.extracted_data).map(([key, value]) => (
                                <div key={key}>
                                  <p className="text-xs font-semibold text-foreground mb-1 uppercase">
                                    {key.replace(/_/g, ' ')}:
                                  </p>
                                  <p className="text-sm text-primary font-medium">{value || 'N/A'}</p>
                                </div>
                              ))}
                            </div>
                          </div>
                        ) : (
                          <p className="text-sm text-muted-foreground">No data extracted</p>
                        )}
                      </CollapsibleContent>
                    </Collapsible>
                  </CardContent>
                </Card>

                {/* Validation Results */}
                <Card className="border-border">
                  <CardContent className="p-6">
                    <Collapsible open={openSections.validation} onOpenChange={() => toggleSection('validation')}>
                      <CollapsibleTrigger className="flex items-center justify-between w-full hover:opacity-80 transition-opacity">
                        <div className="flex items-center gap-2">
                          <h3 className="text-lg font-semibold text-foreground">Validation Results</h3>
                          {analysisResult.validation_result && (
                            <Badge variant={analysisResult.validation_result.is_valid ? 'success' : 'destructive'}>
                              {analysisResult.validation_result.is_valid ? 'VALID' : 'INVALID'}
                            </Badge>
                          )}
                        </div>
                        <ChevronDown className={`h-5 w-5 transition-transform ${openSections.validation ? 'rotate-180' : ''}`} />
                      </CollapsibleTrigger>
                      <CollapsibleContent className="pt-4">
                        {analysisResult.validation_result ? (
                          <div className="space-y-4">
                            {analysisResult.validation_result.recommendation && (
                              <div>
                                <p className="text-sm font-medium text-foreground mb-2">Recommendation:</p>
                                <Badge variant="info">{analysisResult.validation_result.recommendation}</Badge>
                              </div>
                            )}
                            
                            {analysisResult.validation_result.issues && analysisResult.validation_result.issues.length > 0 ? (
                              <div>
                                <p className="text-sm font-medium text-foreground mb-3">Issues Found:</p>
                                <div className="space-y-2">
                                  {analysisResult.validation_result.issues.map((issue, idx) => (
                                    <Card key={idx} className={`border-l-4 ${
                                      issue.severity === 'high' ? 'border-l-red-500 bg-red-50' :
                                      issue.severity === 'medium' ? 'border-l-yellow-500 bg-yellow-50' :
                                      'border-l-blue-500 bg-blue-50'
                                    }`}>
                                      <CardContent className="p-3">
                                        <div className="flex items-start justify-between">
                                          <div className="flex-1">
                                            <p className="text-sm font-medium text-foreground">
                                              {issue.type || 'Issue'}
                                            </p>
                                            <p className="text-xs text-muted-foreground mt-1">{issue.message}</p>
                                            {issue.field && (
                                              <p className="text-xs text-muted-foreground mt-1">
                                                Field: {issue.field}
                                              </p>
                                            )}
                                          </div>
                                          <Badge variant={getSeverityColor(issue.severity)} className="ml-2">
                                            {issue.severity || 'Unknown'}
                                          </Badge>
                                        </div>
                                      </CardContent>
                                    </Card>
                                  ))}
                                </div>
                              </div>
                            ) : (
                              <Card className="border-green-200 bg-green-50">
                                <CardContent className="p-3">
                                  <div className="flex items-center gap-2 text-green-800">
                                    <CheckCircle2 className="h-4 w-4" />
                                    <span className="text-sm">No validation issues found!</span>
                                  </div>
                                </CardContent>
                              </Card>
                            )}
                          </div>
                        ) : (
                          <p className="text-sm text-muted-foreground">No validation results available</p>
                        )}
                      </CollapsibleContent>
                    </Collapsible>
                  </CardContent>
                </Card>

                {/* Recommendations */}
                {analysisResult.recommendations && (
                  <Card className="border-border">
                    <CardContent className="p-6">
                      <Collapsible open={openSections.recommendations} onOpenChange={() => toggleSection('recommendations')}>
                        <CollapsibleTrigger className="flex items-center justify-between w-full hover:opacity-80 transition-opacity">
                          <h3 className="text-lg font-semibold text-foreground">AI Recommendations</h3>
                          <ChevronDown className={`h-5 w-5 transition-transform ${openSections.recommendations ? 'rotate-180' : ''}`} />
                        </CollapsibleTrigger>
                        <CollapsibleContent className="pt-4">
                          <div className="space-y-3">
                            {analysisResult.recommendations.map((rec, idx) => (
                              <Card key={idx} className="bg-blue-50 border-blue-200">
                                <CardContent className="p-3">
                                  <p className="text-sm text-blue-900">{rec}</p>
                                </CardContent>
                              </Card>
                            ))}
                          </div>
                        </CollapsibleContent>
                      </Collapsible>
                    </CardContent>
                  </Card>
                )}
              </>
            )}

            {!analysisResult && (
              <Card className="border-border">
                <CardContent className="p-8 text-center">
                  <FileText className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-foreground mb-2">Ready to Analyze</h3>
                  <p className="text-sm text-muted-foreground">
                    Upload a document and click "Analyze with AI" to see the extracted data and validation results.
                  </p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default DocumentUpload;