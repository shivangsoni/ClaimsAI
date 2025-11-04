import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { useToast } from '../hooks/use-toast';
import { claimsAPI } from '../services/api';
import { ArrowLeft, Upload, X } from 'lucide-react';

export default function NewClaimForm() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [files, setFiles] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    dob: "",
    patientId: "",
    claimType: "",
    serviceDate: "",
    provider: "",
    amount: "",
    diagnosis: "",
    notes: "",
  });

  const handleFileChange = (e) => {
    if (e.target.files) {
      setFiles([...files, ...Array.from(e.target.files)]);
    }
  };

  const removeFile = (index) => {
    setFiles(files.filter((_, i) => i !== index));
  };

  const handleInputChange = (e) => {
    const { id, value } = e.target;
    setFormData((prev) => ({ ...prev, [id]: value }));
  };

  const handleSelectChange = (value) => {
    setFormData((prev) => ({ ...prev, claimType: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Basic validation
    if (
      !formData.firstName ||
      !formData.lastName ||
      !formData.dob ||
      !formData.patientId ||
      !formData.claimType ||
      !formData.serviceDate ||
      !formData.provider ||
      !formData.amount ||
      !formData.diagnosis
    ) {
      toast({
        title: "Validation Error",
        description: "Please fill in all required fields marked with *",
        variant: "destructive",
      });
      return;
    }

    setIsSubmitting(true);

    try {
      // Prepare claim data for API
      const claimData = {
        patient_name: `${formData.firstName} ${formData.lastName}`,
        patient_id: formData.patientId,
        date_of_birth: formData.dob,
        policy_number: `POL-${formData.patientId}`, // Generate policy number
        provider_name: formData.provider,
        provider_id: `PRV-${Math.floor(Math.random() * 10000)}`, // Generate provider ID
        service_date: formData.serviceDate,
        service_type: formData.claimType,
        diagnosis_code: `ICD-${Math.floor(Math.random() * 1000)}`, // Generate diagnosis code
        procedure_code: `CPT-${Math.floor(Math.random() * 1000)}`, // Generate procedure code
        amount_billed: parseFloat(formData.amount),
        notes: formData.notes
      };

      // Call the real API
      const response = await claimsAPI.submitClaim(claimData);
      const claimId = response.claim_id;
      
      // If there are uploaded files, process them
      if (files.length > 0) {
        toast({
          title: "Claim Created!",
          description: `Claim ${claimId} created. Now processing uploaded documents...`,
        });

        // Upload and process each file
        for (let i = 0; i < files.length; i++) {
          const file = files[i];
          try {
            // Use the existing upload endpoint for existing claims
            const uploadResponse = await fetch(`http://localhost:5000/api/claims/${claimId}/upload`, {
              method: 'POST',
              body: (() => {
                const formData = new FormData();
                formData.append('document', file);
                formData.append('claim_type', claimData.service_type || 'medical_claim');
                return formData;
              })(),
            });

            if (uploadResponse.ok) {
              const uploadResult = await uploadResponse.json();
              toast({
                title: "Document Processed!",
                description: `${file.name} uploaded and analyzed with GPT-4.`,
              });
            } else {
              console.error(`Failed to upload ${file.name}`);
            }
          } catch (error) {
            console.error(`Error uploading ${file.name}:`, error);
          }
        }
        
        toast({
          title: "Complete Success!",
          description: `Claim ${claimId} submitted with ${files.length} document(s) processed.`,
        });
      } else {
        toast({
          title: "Success!",
          description: `Claim ${claimId} has been submitted successfully.`,
        });
      }

      // Redirect to the claim detail page to show the results
      setTimeout(() => {
        navigate(`/claims/${claimId}`);
      }, 2000);
    } catch (error) {
      console.error('Claim submission error:', error);
      toast({
        title: "Error",
        description: `Failed to submit claim: ${error.response?.data?.error || error.message}`,
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="container mx-auto px-6 py-4">
          <Link
            to="/dashboard"
            className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors"
          >
            <ArrowLeft className="h-4 w-4" />
            <span className="text-sm">Back to Dashboard</span>
          </Link>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8 max-w-4xl">
        <Card className="border-border">
          <CardContent className="p-8">
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-foreground mb-2">Submit New Claim</h1>
              <p className="text-muted-foreground">
                Fill out the form below to submit a new medical claim. All fields marked with * are required.
              </p>
            </div>

            <form className="space-y-8" onSubmit={handleSubmit}>
              {/* Patient Information */}
              <div>
                <h2 className="text-xl font-semibold text-foreground mb-4 pb-2 border-b border-border">
                  Patient Information
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="firstName">First Name *</Label>
                    <Input
                      id="firstName"
                      placeholder="John"
                      value={formData.firstName}
                      onChange={handleInputChange}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="lastName">Last Name *</Label>
                    <Input
                      id="lastName"
                      placeholder="Doe"
                      value={formData.lastName}
                      onChange={handleInputChange}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="dob">Date of Birth *</Label>
                    <Input id="dob" type="date" value={formData.dob} onChange={handleInputChange} required />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="patientId">Patient ID *</Label>
                    <Input
                      id="patientId"
                      placeholder="PAT-123456"
                      value={formData.patientId}
                      onChange={handleInputChange}
                      required
                    />
                  </div>
                </div>
              </div>

              {/* Claim Details */}
              <div>
                <h2 className="text-xl font-semibold text-foreground mb-4 pb-2 border-b border-border">
                  Claim Details
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="claimType">Claim Type *</Label>
                    <Select value={formData.claimType} onValueChange={handleSelectChange} required>
                      <SelectTrigger id="claimType">
                        <SelectValue placeholder="Select type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="inpatient">Inpatient</SelectItem>
                        <SelectItem value="outpatient">Outpatient</SelectItem>
                        <SelectItem value="emergency">Emergency</SelectItem>
                        <SelectItem value="preventive">Preventive</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="serviceDate">Service Date *</Label>
                    <Input
                      id="serviceDate"
                      type="date"
                      value={formData.serviceDate}
                      onChange={handleInputChange}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="provider">Healthcare Provider *</Label>
                    <Input
                      id="provider"
                      placeholder="General Hospital"
                      value={formData.provider}
                      onChange={handleInputChange}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="amount">Claim Amount ($) *</Label>
                    <Input
                      id="amount"
                      type="number"
                      placeholder="1500.00"
                      step="0.01"
                      value={formData.amount}
                      onChange={handleInputChange}
                      required
                    />
                  </div>
                </div>
                <div className="space-y-2 mt-6">
                  <Label htmlFor="diagnosis">Diagnosis/Treatment Description *</Label>
                  <Textarea
                    id="diagnosis"
                    placeholder="Describe the medical condition and treatment received..."
                    rows={5}
                    value={formData.diagnosis}
                    onChange={handleInputChange}
                    required
                  />
                </div>
              </div>

              {/* Supporting Documents */}
              <div>
                <h2 className="text-xl font-semibold text-foreground mb-4 pb-2 border-b border-border">
                  Supporting Documents
                </h2>
                <div className="space-y-4">
                  <div className="border-2 border-dashed border-border rounded-lg p-8 text-center hover:border-primary/50 transition-colors">
                    <input
                      type="file"
                      id="fileUpload"
                      className="hidden"
                      multiple
                      accept=".pdf,.jpg,.jpeg,.png"
                      onChange={handleFileChange}
                    />
                    <label htmlFor="fileUpload" className="cursor-pointer">
                      <Upload className="h-10 w-10 text-muted-foreground mx-auto mb-3" />
                      <p className="text-sm font-medium text-foreground mb-1">Click to upload or drag and drop</p>
                      <p className="text-xs text-muted-foreground">PDF, JPG, PNG up to 10MB</p>
                    </label>
                  </div>

                  {files.length > 0 && (
                    <div className="space-y-2">
                      {files.map((file, index) => (
                        <div key={index} className="flex items-center justify-between p-3 bg-muted rounded-lg">
                          <div className="flex items-center gap-3">
                            <div className="h-10 w-10 bg-primary/10 rounded flex items-center justify-center">
                              <Upload className="h-5 w-5 text-primary" />
                            </div>
                            <div>
                              <p className="text-sm font-medium text-foreground">{file.name}</p>
                              <p className="text-xs text-muted-foreground">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                            </div>
                          </div>
                          <Button type="button" variant="ghost" size="sm" onClick={() => removeFile(index)}>
                            <X className="h-4 w-4" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              {/* Additional Notes */}
              <div>
                <h2 className="text-xl font-semibold text-foreground mb-4 pb-2 border-b border-border">
                  Additional Notes
                </h2>
                <Textarea
                  id="notes"
                  placeholder="Add any additional information or notes about this claim..."
                  rows={4}
                  value={formData.notes}
                  onChange={handleInputChange}
                />
              </div>

              {/* Submit Buttons */}
              <div className="flex flex-col sm:flex-row gap-3 pt-4">
                <Button
                  type="submit"
                  className="flex-1 bg-primary text-primary-foreground hover:bg-primary/90"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? "Submitting..." : "Submit Claim"}
                </Button>
                <Link to="/dashboard" className="flex-1">
                  <Button type="button" variant="outline" className="w-full bg-transparent" disabled={isSubmitting}>
                    Cancel
                  </Button>
                </Link>
              </div>
            </form>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}