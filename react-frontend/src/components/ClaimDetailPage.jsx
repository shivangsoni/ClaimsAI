import React, { useState, useEffect, useCallback } from 'react';
import { Link, useParams, Navigate } from 'react-router-dom';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from './ui/collapsible';
import StatusManager from './StatusManager';
import {
  ArrowLeft,
  CheckCircle2,
  Clock,
  Download,
  FileText,
  ChevronDown,
  Lightbulb,
  Search,
  TrendingUp,
  RefreshCw,
} from 'lucide-react';
import { claimsAPI } from '../services/api';
import { useToast } from '../hooks/use-toast';

function StatusBadge({ status }) {
  // Map new 5-stage status system to display styles
  const statusStyles = {
    open: "bg-blue-500 text-white",
    validation_complete: "bg-orange-500 text-white", 
    verified: "bg-purple-500 text-white",
    approved: "bg-green-500 text-white",
    denied: "bg-red-500 text-white",
    need_more_info: "bg-yellow-500 text-white",
    // Legacy status mapping
    submitted: "bg-blue-400 text-white",
    pending: "bg-yellow-500 text-white",
    "under-review": "bg-blue-500 text-white",
    rejected: "bg-red-500 text-white",
  };

  const statusLabels = {
    open: "Open",
    validation_complete: "Validation Complete",
    verified: "Verified", 
    approved: "Approved",
    denied: "Denied",
    need_more_info: "Need More Info",
    // Legacy status mapping
    submitted: "Submitted",
    pending: "Pending Review",
    "under-review": "Under Review",
    rejected: "Rejected",
  };

  const statusIcons = {
    approved: <CheckCircle2 className="h-4 w-4" />,
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium ${statusStyles[status] || statusStyles.open}`}
    >
      {status === "approved" && statusIcons.approved}
      {statusLabels[status] || status}
    </span>
  );
}

export default function ClaimDetailPage() {
  const { id } = useParams();
  const [claimData, setClaimData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const { toast } = useToast();

  // Helper function to safely format dates
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    try {
      return new Date(dateString).toLocaleDateString();
    } catch (error) {
      return 'Invalid Date';
    }
  };
  const [openSections, setOpenSections] = useState({
    extracted: true,
    validation: true,
    recommendations: true,
    timeline: true,
  });

  const loadClaimDetails = useCallback(async () => {
    try {
      setLoading(true);
      const response = await claimsAPI.getClaimDetails(id);
      setClaimData(response);
    } catch (error) {
      console.error('Error loading claim details:', error);
      toast({
        title: "Error",
        description: "Failed to load claim details. Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  }, [id, toast]);

  useEffect(() => {
    if (id) {
      loadClaimDetails();
    }
  }, [id, loadClaimDetails]);

  const handleStatusUpdate = async (response) => {
    // Refresh claim data when status is updated
    await loadClaimDetails();
  };

  const handleAIProcess = async (response) => {
    // Refresh claim data when AI processing is complete
    await loadClaimDetails();
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadClaimDetails();
    setRefreshing(false);
  };

  const toggleSection = (section) => {
    setOpenSections((prev) => ({ ...prev, [section]: !prev[section] }));
  };

  const handleDownload = async (documentId, filename) => {
    try {
      const response = await claimsAPI.downloadDocument(documentId);
      
      // Create blob URL and trigger download
      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      toast({
        title: "Success",
        description: `${filename} downloaded successfully`,
      });
    } catch (error) {
      console.error('Download error:', error);
      toast({
        title: "Error",
        description: "Failed to download document. Please try again.",
        variant: "destructive",
      });
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
          <p className="mt-4 text-muted-foreground">Loading claim details...</p>
        </div>
      </div>
    );
  }

  if (!claimData || !claimData.claim) {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <Link
            to="/dashboard"
            className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors"
          >
            <ArrowLeft className="h-4 w-4" />
            <span className="text-sm">Back to Dashboard</span>
          </Link>
          
          <Button
            onClick={handleRefresh}
            disabled={refreshing}
            variant="outline"
            className="flex items-center gap-2"
          >
            <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        {/* Patient Header */}
        <Card className="border-border mb-6">
          <CardContent className="p-6">
            <div className="flex items-center gap-3">
              <h1 className="text-3xl font-bold text-foreground">{claimData.claim.patient_name}</h1>
              <StatusBadge status={claimData.claim.status} />
            </div>
            <p className="text-muted-foreground mt-2">
              Claim ID: {claimData.claim.claim_id} • Patient ID: {claimData.claim.patient_id}
            </p>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
              <div>
                <p className="text-xs text-muted-foreground mb-1">Service Date</p>
                <p className="text-sm font-medium text-foreground">
                  {formatDate(claimData.claim.service_date)}
                </p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground mb-1">Provider</p>
                <p className="text-sm font-medium text-foreground">{claimData.claim.provider_name}</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground mb-1">Amount</p>
                <p className="text-sm font-medium text-primary">${parseFloat(claimData.claim.amount_billed || 0).toFixed(2)}</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground mb-1">Service Type</p>
                <p className="text-sm font-medium text-foreground">{claimData.claim.service_type}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Status Management */}
        <StatusManager
          claim={claimData.claim}
          onStatusUpdate={handleStatusUpdate}
          onAIProcess={handleAIProcess}
        />

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Claim Information */}
          <div className="lg:col-span-2 space-y-6">
            <Card className="border-border">
              <CardContent className="p-6 space-y-4">
                {/* AI Recommendations */}
                {claimData.recommendations && claimData.recommendations.length > 0 && (
                  <Collapsible open={openSections.recommendations} onOpenChange={() => toggleSection("recommendations")}>
                    <CollapsibleTrigger className="flex items-center justify-between w-full hover:opacity-80 transition-opacity">
                      <div className="flex items-center gap-2">
                        <Lightbulb className="h-5 w-5 text-foreground" />
                        <h3 className="text-base font-semibold text-foreground">AI Recommendation</h3>
                      </div>
                      <ChevronDown
                        className={`h-5 w-5 text-muted-foreground transition-transform ${openSections.recommendations ? "rotate-180" : ""}`}
                      />
                    </CollapsibleTrigger>
                    <CollapsibleContent className="pt-4">
                      {claimData.recommendations.map((rec, index) => (
                        <div key={index} className="space-y-4">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                              <div className="flex items-center gap-2">
                                <Badge className={rec.recommendation === 'APPROVED' ? 'bg-green-500' : rec.recommendation === 'DENIED' ? 'bg-red-500' : 'bg-yellow-500'}>
                                  AI SUGGESTS: {rec.recommendation}
                                </Badge>
                                <span className="text-xs text-purple-600 bg-purple-100 px-2 py-1 rounded-full">
                                  Suggestion Only
                                </span>
                              </div>
                              <span className="text-sm text-muted-foreground">Confidence: {rec.confidence}%</span>
                              <span className="text-sm text-muted-foreground">Score: {rec.overall_score}%</span>
                            </div>
                            <span className="text-xs text-muted-foreground">
                              {formatDate(rec.created_at)}
                            </span>
                          </div>
                          
                          {/* Decision Reasoning */}
                          <div className="bg-muted/50 rounded-lg p-4">
                            <h4 className="text-sm font-semibold text-foreground mb-2">Decision Reasoning:</h4>
                            <p className="text-sm text-foreground leading-relaxed">{rec.reason || 'No reasoning provided'}</p>
                          </div>
                          
                          {/* Key Factors */}
                          {rec.suggested_actions && rec.suggested_actions.length > 0 && (
                            <div className="bg-blue-50 rounded-lg p-3">
                              <h4 className="text-sm font-semibold text-blue-800 mb-2">Key Factors:</h4>
                              <ul className="list-disc list-inside space-y-1">
                                {JSON.parse(rec.suggested_actions || '[]').slice(0, 5).map((factor, i) => (
                                  <li key={i} className="text-sm text-blue-700">{factor}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                          {rec.suggested_actions && JSON.parse(rec.suggested_actions).length > 0 && (
                            <div className="mt-2">
                              <p className="text-xs font-medium text-muted-foreground mb-1">Suggested Actions:</p>
                              <ul className="list-disc list-inside text-sm text-foreground space-y-1">
                                {JSON.parse(rec.suggested_actions).map((action, i) => (
                                  <li key={i}>{action}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      ))}
                    </CollapsibleContent>
                  </Collapsible>
                )}

                <div className="border-t border-border" />

                {/* Validation Results */}
                {claimData.validations && claimData.validations.length > 0 && (
                  <Collapsible open={openSections.validation} onOpenChange={() => toggleSection("validation")}>
                    <CollapsibleTrigger className="flex items-center justify-between w-full hover:opacity-80 transition-opacity">
                      <div className="flex items-center gap-2">
                        <Search className="h-5 w-5 text-foreground" />
                        <h3 className="text-base font-semibold text-foreground">Validation Results</h3>
                      </div>
                      <ChevronDown
                        className={`h-5 w-5 text-muted-foreground transition-transform ${openSections.validation ? "rotate-180" : ""}`}
                      />
                    </CollapsibleTrigger>
                    <CollapsibleContent className="pt-4">
                      {claimData.validations.map((validation, index) => (
                        <div key={index} className="space-y-3">
                          <div className="flex items-center gap-2">
                            {validation.is_valid ? (
                              <CheckCircle2 className="h-5 w-5 text-green-500" />
                            ) : (
                              <Clock className="h-5 w-5 text-red-500" />
                            )}
                            <span className={`text-sm font-medium ${validation.is_valid ? 'text-green-600' : 'text-red-600'}`}>
                              {validation.is_valid ? 'Valid Claim' : 'Issues Found'}
                            </span>
                            <span className="text-xs text-muted-foreground">
                              {validation.total_issues} issues
                            </span>
                          </div>
                          {validation.issues && JSON.parse(validation.issues).length > 0 && (
                            <div className="space-y-2">
                              {JSON.parse(validation.issues).map((issue, i) => (
                                <div key={i} className="p-3 rounded-md bg-red-50 border border-red-200">
                                  <p className="text-sm text-red-800">
                                    <span className="font-medium">{issue.field}:</span> {issue.error}
                                  </p>
                                </div>
                              ))}
                            </div>
                          )}
                          {validation.recommendation && (
                            <div className="p-3 rounded-md bg-blue-50 border border-blue-200">
                              <p className="text-sm text-blue-800">{validation.recommendation}</p>
                            </div>
                          )}
                        </div>
                      ))}
                    </CollapsibleContent>
                  </Collapsible>
                )}

                <div className="border-t border-border" />

                {/* Improvement Suggestions */}
                <Collapsible open={openSections.improvements} onOpenChange={() => toggleSection("improvements")}>
                  <CollapsibleTrigger className="flex items-center justify-between w-full hover:opacity-80 transition-opacity">
                    <div className="flex items-center gap-2">
                      <TrendingUp className="h-5 w-5 text-foreground" />
                      <h3 className="text-base font-semibold text-foreground">Improvement Suggestions</h3>
                    </div>
                    <ChevronDown
                      className={`h-5 w-5 text-muted-foreground transition-transform ${openSections.improvements ? "rotate-180" : ""}`}
                    />
                  </CollapsibleTrigger>
                  <CollapsibleContent className="pt-4">
                    <ul className="space-y-2 text-sm text-foreground">
                      <li className="flex items-start gap-2">
                        <span className="text-primary mt-0.5">•</span>
                        <span>Ensure all medical reports include provider signatures and dates</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-primary mt-0.5">•</span>
                        <span>Include itemized billing statements for faster processing</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-primary mt-0.5">•</span>
                        <span>Submit claims within 30 days of service for optimal review time</span>
                      </li>
                    </ul>
                  </CollapsibleContent>
                </Collapsible>

                <div className="border-t border-border" />

                {/* Extracted Data */}
                <Collapsible open={openSections.extracted} onOpenChange={() => toggleSection("extracted")}>
                  <CollapsibleTrigger className="flex items-center justify-between w-full hover:opacity-80 transition-opacity">
                    <div className="flex items-center gap-2">
                      <FileText className="h-5 w-5 text-foreground" />
                      <h3 className="text-base font-semibold text-foreground">Extracted Data</h3>
                    </div>
                    <ChevronDown
                      className={`h-5 w-5 text-muted-foreground transition-transform ${openSections.extracted ? "rotate-180" : ""}`}
                    />
                  </CollapsibleTrigger>
                  <CollapsibleContent className="pt-4">
                    <div className="bg-primary/5 rounded-lg p-4">
                      <div className="grid grid-cols-2 gap-6">
                        <div>
                          <p className="text-xs font-semibold text-foreground mb-1">BILLED AMOUNT:</p>
                          <p className="text-sm text-primary font-medium">
                            ${parseFloat(claimData.claim.amount_billed || 0).toFixed(2)}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs font-semibold text-foreground mb-1">POLICY NUMBER:</p>
                          <p className="text-sm text-primary font-medium">{claimData.claim.policy_number}</p>
                        </div>
                        <div>
                          <p className="text-xs font-semibold text-foreground mb-1">SERVICE DATE:</p>
                          <p className="text-sm text-primary font-medium">
                            {formatDate(claimData.claim.service_date)}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs font-semibold text-foreground mb-1">SERVICE DATE:</p>
                          <p className="text-sm text-primary font-medium">
                            {formatDate(claimData.claim.service_date)}
                          </p>
                        </div>
                      </div>
                    </div>
                  </CollapsibleContent>
                </Collapsible>
              </CardContent>
            </Card>

            {/* Original Claim Information */}
            <Card className="border-border">
              <CardContent className="p-6">
                <h2 className="text-xl font-semibold text-foreground mb-6">Claim Information</h2>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <p className="text-sm text-muted-foreground mb-1">Patient Name</p>
                    <p className="text-base font-medium text-foreground">{claimData.patientName}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground mb-1">Date of Birth</p>
                    <p className="text-base font-medium text-foreground">{claimData.dob}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground mb-1">Claim Type</p>
                    <p className="text-base font-medium text-foreground">{claimData.claim.service_type}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground mb-1">Service Date</p>
                    <p className="text-base font-medium text-foreground">
                      {formatDate(claimData.claim.service_date)}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground mb-1">Healthcare Provider</p>
                    <p className="text-base font-medium text-foreground">{claimData.claim.provider_name}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground mb-1">Claim Amount</p>
                    <p className="text-base font-medium text-primary">
                      ${parseFloat(claimData.claim.amount_billed || 0).toFixed(2)}
                    </p>
                  </div>
                </div>

                <div className="mt-6 pt-6 border-t border-border">
                  <p className="text-sm text-muted-foreground mb-2">Diagnosis/Treatment</p>
                  <p className="text-base font-medium text-foreground">{claimData.diagnosis}</p>
                </div>

                <div className="mt-6 pt-6 border-t border-border">
                  <p className="text-sm text-muted-foreground mb-2">Additional Notes</p>
                  <p className="text-base text-foreground">{claimData.notes}</p>
                </div>
              </CardContent>
            </Card>

            {/* Supporting Documents */}
            <Card className="border-border">
              <CardContent className="p-6">
                <h2 className="text-xl font-semibold text-foreground mb-2">Supporting Documents</h2>
                <p className="text-sm text-muted-foreground mb-6">View and download claim-related documents</p>

                <div className="space-y-3">
                  {claimData.documents && claimData.documents.length > 0 ? (
                    claimData.documents.map((doc, index) => (
                      <div
                        key={index}
                        className="flex items-center justify-between p-4 border border-border rounded-lg hover:bg-muted/50 transition-colors"
                      >
                        <div className="flex items-center gap-4">
                          <div className="h-12 w-12 bg-primary/10 rounded-lg flex items-center justify-center">
                            <FileText className="h-6 w-6 text-primary" />
                          </div>
                          <div>
                            <p className="text-sm font-medium text-foreground">{doc.original_filename}</p>
                            <p className="text-xs text-muted-foreground">
                              {doc.file_size} bytes • Uploaded {new Date(doc.upload_timestamp).toLocaleString()}
                            </p>
                          </div>
                        </div>
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => handleDownload(doc.id, doc.original_filename)}
                        >
                          <Download className="h-4 w-4 mr-2" />
                          Download
                        </Button>
                      </div>
                    ))
                  ) : (
                    <div className="text-center py-8">
                      <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-3" />
                      <p className="text-sm text-muted-foreground">No documents uploaded for this claim</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right Column - Quick Summary & Timeline */}
          <div className="space-y-6">
            <Card className="border-border">
              <CardContent className="p-6">
                <h2 className="text-lg font-semibold text-foreground mb-4">Quick Summary</h2>

                <div className="space-y-4">
                  <div>
                    <p className="text-sm text-muted-foreground mb-2">Current Status:</p>
                    <StatusBadge status={claimData.claim.status} />
                  </div>

                  {/* AI Suggestion Display */}
                  {claimData.claim.ai_suggested_status && (
                    <div>
                      <p className="text-sm text-muted-foreground mb-2">AI Suggestion:</p>
                      <div className="flex items-center gap-2">
                        <StatusBadge status={claimData.claim.ai_suggested_status} />
                        <span className="text-xs text-purple-600 bg-purple-100 px-2 py-1 rounded-full">
                          Suggestion Only
                        </span>
                      </div>
                    </div>
                  )}

                  {/* Recommendation from recommendations table */}
                  {claimData.recommendations && claimData.recommendations.length > 0 && (
                    <div>
                      <p className="text-sm text-muted-foreground mb-2">AI Analysis:</p>
                      <Badge
                        variant={
                          claimData.recommendations[0].recommendation === "APPROVED"
                            ? "success"
                            : claimData.recommendations[0].recommendation === "DENIED"
                              ? "destructive"
                              : "warning"
                        }
                        className="text-xs"
                      >
                        {claimData.recommendations[0].recommendation}
                      </Badge>
                    </div>
                  )}

                  <div>
                    <p className="text-sm text-muted-foreground mb-2">Completeness:</p>
                    <Badge variant="info" className="text-xs">
                      {claimData.recommendations && claimData.recommendations.length > 0 
                        ? claimData.recommendations[0].overall_score 
                        : 'N/A'}%
                    </Badge>
                  </div>

                  <div>
                    <p className="text-sm text-muted-foreground mb-2">Confidence:</p>
                    <Badge variant="default" className="text-xs">
                      {claimData.recommendations && claimData.recommendations.length > 0 
                        ? claimData.recommendations[0].confidence 
                        : 'N/A'}%
                    </Badge>
                  </div>

                  <div className="pt-4 border-t border-border">
                    <div className="flex items-start gap-2 mb-2">
                      <Lightbulb className="h-4 w-4 text-foreground mt-0.5 flex-shrink-0" />
                      <h3 className="text-sm font-semibold text-foreground">Decision Reasoning</h3>
                    </div>
                    <p className="text-xs text-foreground leading-relaxed">
                      {claimData.recommendations && claimData.recommendations.length > 0 
                        ? claimData.recommendations[0].reason 
                        : 'No analysis available'}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Processing Timeline */}
            <Card className="border-border">
              <CardContent className="p-6">
                <h2 className="text-lg font-semibold text-foreground mb-2">Processing Timeline</h2>
                <p className="text-sm text-muted-foreground mb-6">Track your claim's progress</p>

                <div className="space-y-6">
                  {/* Generate timeline based on new 5-stage status system */}
                  {[
                    { 
                      title: 'Claim Submitted', 
                      date: formatDate(claimData.claim.created_at),
                      completed: true // Always completed since claim exists
                    },
                    { 
                      title: 'Validation Complete', 
                      date: ['validation_complete', 'verified', 'approved', 'denied'].includes(claimData.claim.status) ? 'Complete' : 'Pending',
                      completed: ['validation_complete', 'verified', 'approved', 'denied'].includes(claimData.claim.status)
                    },
                    { 
                      title: 'Verified', 
                      date: ['verified', 'approved', 'denied'].includes(claimData.claim.status) ? 'Complete' : 'Pending',
                      completed: ['verified', 'approved', 'denied'].includes(claimData.claim.status)
                    },
                    { 
                      title: 'Final Decision', 
                      date: ['approved', 'denied'].includes(claimData.claim.status) ? 'Complete' : 'Pending',
                      completed: ['approved', 'denied'].includes(claimData.claim.status)
                    }
                  ].map((item, index) => (
                    <div key={index} className="flex gap-4">
                      <div className="flex flex-col items-center">
                        <div
                          className={`h-8 w-8 rounded-full flex items-center justify-center ${
                            item.completed ? "bg-green-500 text-white" : "bg-muted text-muted-foreground"
                          }`}
                        >
                          {item.completed ? <CheckCircle2 className="h-5 w-5" /> : <Clock className="h-5 w-5" />}
                        </div>
                        {index < 3 && (
                          <div className={`w-0.5 h-12 ${item.completed ? "bg-green-500" : "bg-border"}`} />
                        )}
                      </div>
                      <div className="flex-1 pb-6">
                        <p
                          className={`text-sm font-medium ${
                            item.completed ? "text-foreground" : "text-muted-foreground"
                          }`}
                        >
                          {item.title}
                        </p>
                        <p className="text-xs text-muted-foreground mt-1">{item.date}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
}