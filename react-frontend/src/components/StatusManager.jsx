import React, { useState } from 'react';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { Textarea } from './ui/textarea';
import { 
  ChevronRight, 
  Brain, 
  User, 
  Clock, 
  CheckCircle2, 
  XCircle, 
  AlertTriangle, 
  FileSearch,
  Shield
} from 'lucide-react';
import { claimsAPI } from '../services/api';
import { useToast } from '../hooks/use-toast';

const STATUS_CONFIG = {
  open: {
    label: 'Open',
    color: 'bg-blue-500',
    icon: <FileSearch className="h-4 w-4" />,
    description: 'Claim received, awaiting initial review',
    canMoveTo: ['validation_complete', 'need_more_info'],
    aiCanSuggest: true
  },
  validation_complete: {
    label: 'Validation Complete',
    color: 'bg-orange-500',
    icon: <Brain className="h-4 w-4" />,
    description: 'AI analysis completed, human review required',
    canMoveTo: ['verified', 'need_more_info', 'open'],
    aiCanSuggest: false
  },
  verified: {
    label: 'Verified',
    color: 'bg-purple-500',
    icon: <Shield className="h-4 w-4" />,
    description: 'Human verified, ready for final decision',
    canMoveTo: ['approved', 'denied', 'need_more_info', 'validation_complete'],
    aiCanSuggest: false
  },
  approved: {
    label: 'Approved',
    color: 'bg-green-500',
    icon: <CheckCircle2 className="h-4 w-4" />,
    description: 'Claim approved for payment',
    canMoveTo: ['verified'], // Allow reverting to verified if needed
    aiCanSuggest: false
  },
  denied: {
    label: 'Denied',
    color: 'bg-red-500',
    icon: <XCircle className="h-4 w-4" />,
    description: 'Claim denied',
    canMoveTo: ['verified'], // Allow reverting to verified if needed
    aiCanSuggest: false
  },
  need_more_info: {
    label: 'Need More Info',
    color: 'bg-yellow-500',
    icon: <AlertTriangle className="h-4 w-4" />,
    description: 'Additional information required',
    canMoveTo: ['open', 'validation_complete', 'verified'],
    aiCanSuggest: false
  }
};

export default function StatusManager({ claim, onStatusUpdate, onAIProcess }) {
  const [isUpdating, setIsUpdating] = useState(false);
  const [isProcessingAI, setIsProcessingAI] = useState(false);
  const [showCommentModal, setShowCommentModal] = useState(false);
  const [comment, setComment] = useState('');
  const [selectedStatus, setSelectedStatus] = useState(null);
  const { toast } = useToast();

  const currentStatus = claim?.status || 'open';
  const statusConfig = STATUS_CONFIG[currentStatus];
  const availableStatuses = statusConfig?.canMoveTo || [];

  const handleStatusChange = async (newStatus, reason = '') => {
    if (!newStatus) return;
    
    setIsUpdating(true);
    try {
      const response = await claimsAPI.updateClaimStatus(claim.claim_id, {
        status: newStatus,
        changed_by: 'human_user',
        reason: reason || `Manual status change from ${currentStatus} to ${newStatus}`,
        notes: comment
      });

      toast({
        title: "Status Updated",
        description: `Claim moved to ${STATUS_CONFIG[newStatus].label}`,
      });

      onStatusUpdate && onStatusUpdate(response);
      setShowCommentModal(false);
      setComment('');
      setSelectedStatus(null);
    } catch (error) {
      console.error('Status update error:', error);
      toast({
        title: "Update Failed",
        description: "Failed to update claim status. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsUpdating(false);
    }
  };

  const handleAIProcess = async () => {
    if (currentStatus !== 'open') {
      toast({
        title: "Cannot Process",
        description: "AI can only process claims in 'Open' status",
        variant: "destructive",
      });
      return;
    }

    setIsProcessingAI(true);
    try {
      const response = await claimsAPI.processClaimWithAI(claim.claim_id);
      
      toast({
        title: "AI Processing Complete",
        description: `Claim moved to Validation Complete. AI suggests: ${response.suggested_status}`,
      });

      onAIProcess && onAIProcess(response);
    } catch (error) {
      console.error('AI processing error:', error);
      toast({
        title: "AI Processing Failed",
        description: "Failed to process claim with AI. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsProcessingAI(false);
    }
  };

  const confirmStatusChange = (newStatus) => {
    setSelectedStatus(newStatus);
    setShowCommentModal(true);
  };

  // Define the workflow order for breadcrumb display
  const workflowSteps = [
    { key: 'open', label: 'Open', icon: <FileSearch className="h-4 w-4" /> },
    { key: 'validation_complete', label: 'Validation Complete', icon: <Brain className="h-4 w-4" /> },
    { key: 'verified', label: 'Verified', icon: <Shield className="h-4 w-4" /> },
    { key: 'approved', label: 'Approved', icon: <CheckCircle2 className="h-4 w-4" /> },
    { key: 'denied', label: 'Denied', icon: <XCircle className="h-4 w-4" /> }
  ];

  const getCurrentStepIndex = () => {
    if (currentStatus === 'need_more_info') {
      // Show as branched from current workflow position
      return workflowSteps.findIndex(step => step.key === 'verified');
    }
    return workflowSteps.findIndex(step => step.key === currentStatus);
  };

  const renderBreadcrumbWorkflow = () => {
    const currentStepIndex = getCurrentStepIndex();
    
    return (
      <div className="mb-6">
        <h4 className="font-semibold text-foreground mb-3 flex items-center gap-2">
          <User className="h-4 w-4" />
          Human Control - Status Transitions
        </h4>
        <p className="text-sm text-muted-foreground mb-4">
          Click on any available step below to transition the claim status. Comments are required for audit trail.
        </p>
        
        <div className="bg-gradient-to-r from-gray-50 to-gray-100 p-4 rounded-lg border">
          <div className="flex items-center space-x-3 overflow-x-auto pb-2">
            {workflowSteps.map((step, index) => {
              const isCompleted = index < currentStepIndex;
              const isCurrent = index === currentStepIndex;
              const canMoveTo = availableStatuses.includes(step.key);
              
              return (
                <React.Fragment key={step.key}>
                  <div
                    className={`flex items-center gap-3 px-4 py-3 rounded-lg border-2 transition-all min-w-fit transform
                      ${isCurrent 
                        ? 'border-blue-500 bg-blue-100 text-blue-800 shadow-lg scale-105' 
                        : isCompleted 
                          ? 'border-green-500 bg-green-100 text-green-800 shadow-md'
                          : canMoveTo
                            ? 'border-gray-300 bg-white text-gray-700 hover:border-blue-400 hover:bg-blue-50 hover:shadow-lg hover:scale-105 cursor-pointer'
                            : 'border-gray-200 bg-gray-100 text-gray-400 cursor-not-allowed'
                      }
                      ${canMoveTo ? 'hover:transform hover:scale-105' : ''}
                    `}
                    onClick={() => canMoveTo && confirmStatusChange(step.key)}
                    title={canMoveTo ? `Click to move to ${step.label}` : `Cannot move to ${step.label} from current status`}
                  >
                    <div className={`rounded-full p-2 transition-colors
                      ${isCurrent 
                        ? 'bg-blue-600 text-white' 
                        : isCompleted 
                          ? 'bg-green-600 text-white'
                          : canMoveTo
                            ? 'bg-gray-300 text-gray-600'
                            : 'bg-gray-200 text-gray-400'
                      }`}>
                      {step.icon}
                    </div>
                    <div className="flex flex-col">
                      <span className="text-sm font-semibold whitespace-nowrap">{step.label}</span>
                      {isCurrent && (
                        <span className="text-xs text-blue-600">Current Status</span>
                      )}
                      {isCompleted && !isCurrent && (
                        <span className="text-xs text-green-600">Completed</span>
                      )}
                      {canMoveTo && !isCurrent && !isCompleted && (
                        <span className="text-xs text-gray-500">Click to proceed</span>
                      )}
                    </div>
                    {claim.ai_suggested_status === step.key && (
                      <div className="text-xs bg-purple-200 text-purple-700 px-2 py-1 rounded-full ml-1 font-medium">
                        🤖 AI Suggests
                      </div>
                    )}
                  </div>
                  
                  {index < workflowSteps.length - 2 && (
                    <ChevronRight className={`h-5 w-5 ${isCompleted ? 'text-green-500' : 'text-gray-300'}`} />
                  )}
                </React.Fragment>
              );
            })}
          </div>
        </div>

        {/* Need More Info Branch */}
        {currentStatus === 'need_more_info' && (
          <div className="mt-4 flex items-center gap-2">
            <div className="w-6 h-0.5 bg-yellow-400"></div>
            <div className="flex items-center gap-2 px-3 py-2 rounded-lg border-2 border-yellow-500 bg-yellow-50 text-yellow-700">
              <div className="rounded-full p-1 bg-yellow-500 text-white">
                <AlertTriangle className="h-4 w-4" />
              </div>
              <span className="text-sm font-medium">Need More Info</span>
            </div>
            <span className="text-xs text-yellow-600">Branched from workflow</span>
          </div>
        )}
      </div>
    );
  };

  return (
    <Card className="border-border">
      <CardContent className="p-6">
        <div className="space-y-6">
          {/* Current Status Display */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <h3 className="text-lg font-semibold text-foreground">Claim Status</h3>
              <Badge className={`${statusConfig?.color} text-white`}>
                <div className="flex items-center gap-1">
                  {statusConfig?.icon}
                  {statusConfig?.label}
                </div>
              </Badge>
            </div>
            
            {/* AI Processing Button */}
            {currentStatus === 'open' && statusConfig?.aiCanSuggest && (
              <Button
                onClick={handleAIProcess}
                disabled={isProcessingAI}
                className="flex items-center gap-2 bg-purple-600 hover:bg-purple-700"
              >
                <Brain className={`h-4 w-4 ${isProcessingAI ? 'animate-pulse' : ''}`} />
                {isProcessingAI ? 'Processing...' : 'Process with AI'}
              </Button>
            )}
          </div>

          <p className="text-sm text-muted-foreground">{statusConfig?.description}</p>

          {/* AI Suggestions Display */}
          {claim.ai_suggested_status && claim.ai_decision_summary && (
            <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <Brain className="h-5 w-5 text-purple-600" />
                <h4 className="font-semibold text-purple-800">AI Recommendation</h4>
              </div>
              
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <span className="text-sm text-purple-700">Suggested Status:</span>
                  <Badge className={`${STATUS_CONFIG[claim.ai_suggested_status]?.color} text-white`}>
                    {STATUS_CONFIG[claim.ai_suggested_status]?.label}
                  </Badge>
                </div>
                
                {claim.ai_summary && (
                  <div>
                    <span className="text-sm font-medium text-purple-700">Summary:</span>
                    <p className="text-sm text-purple-600 mt-1">{claim.ai_summary}</p>
                  </div>
                )}
                
                <div>
                  <span className="text-sm font-medium text-purple-700">Decision Summary:</span>
                  <p className="text-sm text-purple-600 mt-1">{claim.ai_decision_summary}</p>
                </div>
              </div>
            </div>
          )}

          {/* Breadcrumb Workflow - Primary Status Control */}
          {renderBreadcrumbWorkflow()}

          {/* Instructions for Users */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <User className="h-5 w-5 text-blue-600" />
              <h4 className="font-semibold text-blue-800">How to Change Status</h4>
            </div>
            <ul className="text-sm text-blue-700 space-y-1">
              <li>• Click on any available step in the workflow above to move the claim</li>
              <li>• You can move forward or backward in the workflow as needed</li>
              <li>• A comment is required for each status change to maintain audit trail</li>
              <li>• AI suggestions are highlighted with purple "AI Suggests" badges</li>
            </ul>
          </div>

          {/* Comment Modal for Status Change */}
          {showCommentModal && selectedStatus && (
            <div className="border border-border rounded-lg p-4 bg-muted/50">
              <h4 className="font-medium mb-3 flex items-center gap-2">
                <ChevronRight className="h-4 w-4 text-blue-500" />
                Confirm Status Change: {statusConfig?.label} → {STATUS_CONFIG[selectedStatus]?.label}
              </h4>
              
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-foreground mb-2 block">
                    Comment (Required) <span className="text-red-500">*</span>
                  </label>
                  <Textarea
                    value={comment}
                    onChange={(e) => setComment(e.target.value)}
                    placeholder="Please provide a reason for this status change..."
                    className="min-h-[100px]"
                    required
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    Comments help maintain audit trail and provide context for status changes.
                  </p>
                </div>
                
                <div className="flex gap-2">
                  <Button
                    onClick={() => handleStatusChange(selectedStatus, `Status changed to ${STATUS_CONFIG[selectedStatus]?.label}: ${comment}`)}
                    disabled={isUpdating || !comment.trim()}
                    className="flex-1"
                  >
                    {isUpdating ? (
                      <>
                        <Clock className="h-4 w-4 mr-2 animate-spin" />
                        Updating...
                      </>
                    ) : (
                      <>
                        <CheckCircle2 className="h-4 w-4 mr-2" />
                        Confirm Change
                      </>
                    )}
                  </Button>
                  
                  <Button
                    variant="outline"
                    onClick={() => {
                      setShowCommentModal(false);
                      setSelectedStatus(null);
                      setComment('');
                    }}
                    disabled={isUpdating}
                  >
                    <XCircle className="h-4 w-4 mr-2" />
                    Cancel
                  </Button>
                </div>
              </div>
            </div>
          )}

          {/* Human Notes Display */}
          {claim.human_notes && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <User className="h-5 w-5 text-blue-600" />
                <h4 className="font-semibold text-blue-800">Human Notes</h4>
              </div>
              <p className="text-sm text-blue-700">{claim.human_notes}</p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}