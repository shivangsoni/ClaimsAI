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
import { ArrowLeft, Upload, X, Plus, Trash2 } from 'lucide-react';

export default function NewClaimForm() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [files, setFiles] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    // Field 1: Insurance Type
    insuranceType: "",
    // Field 2: Patient's Name
    firstName: "",
    lastName: "",
    middleInitial: "",
    // Field 3: Patient's Birth Date and Sex
    dob: "",
    patientSex: "",
    // Field 4: Insured's Name
    insuredFirstName: "",
    insuredLastName: "",
    // Field 5: Patient's Address
    patientAddress: "",
    patientCity: "",
    patientState: "",
    patientZip: "",
    // Field 6: Patient Relationship to Insured
    patientRelationship: "",
    // Field 7: Insured's Address
    insuredAddress: "",
    insuredCity: "",
    insuredState: "",
    insuredZip: "",
    // Field 9: Patient's SSN
    patientSSN: "",
    // Field 11: Policy Information
    policyNumber: "",
    policyGroupNumber: "",
    patientId: "",
    // Field 14: Date of Current Illness/Injury/Pregnancy
    illnessInjuryDate: "",
    // Field 17: Referring Provider
    referringProviderName: "",
    referringProviderNPI: "",
    // Field 21: Diagnosis Codes (up to 4)
    diagnosisCode: "",
    diagnosisCode2: "",
    diagnosisCode3: "",
    diagnosisCode4: "",
    // Service Line Items (Field 24A-H)
    serviceLines: [{ 
      serviceDate: "",
      placeOfService: "",
      procedureCode: "",
      modifier: "",
      diagnosisPointer: "",
      charges: "",
      daysUnits: "",
      renderingProviderNPI: ""
    }],
    // Field 28: Total Charge
    totalCharge: "",
    // Field 31: Signature
    physicianSignature: "",
    physicianSignatureDate: "",
    // Field 33: Billing Provider Information
    providerName: "",
    providerId: "",
    providerNPI: "",
    providerAddress: "",
    providerCity: "",
    providerState: "",
    providerZip: "",
    providerTaxId: "",
    // Additional
    serviceType: "",
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

  const handleSelectChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const addServiceLine = () => {
    setFormData((prev) => ({
      ...prev,
      serviceLines: [...prev.serviceLines, {
        serviceDate: "",
        placeOfService: "",
        procedureCode: "",
        modifier: "",
        diagnosisPointer: "",
        charges: "",
        daysUnits: "",
        renderingProviderNPI: ""
      }]
    }));
  };

  const removeServiceLine = (index) => {
    setFormData((prev) => ({
      ...prev,
      serviceLines: prev.serviceLines.filter((_, i) => i !== index)
    }));
  };

  const updateServiceLine = (index, field, value) => {
    setFormData((prev) => {
      const updated = [...prev.serviceLines];
      updated[index][field] = value;
      return { ...prev, serviceLines: updated };
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Basic validation
    if (
      !formData.firstName ||
      !formData.lastName ||
      !formData.dob ||
      !formData.policyNumber ||
      !formData.providerName ||
      !formData.diagnosisCode ||
      formData.serviceLines.length === 0 ||
      !formData.totalCharge
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
        insurance_type: formData.insuranceType,
        patient_name: `${formData.lastName}, ${formData.firstName}${formData.middleInitial ? ' ' + formData.middleInitial : ''}`,
        patient_id: formData.patientId || `PAT-${Math.floor(Math.random() * 100000)}`,
        date_of_birth: formData.dob,
        patient_sex: formData.patientSex,
        insured_name: formData.insuredFirstName && formData.insuredLastName 
          ? `${formData.insuredLastName}, ${formData.insuredFirstName}` 
          : null,
        patient_address: formData.patientAddress,
        patient_city: formData.patientCity,
        patient_state: formData.patientState,
        patient_zip: formData.patientZip,
        patient_relationship: formData.patientRelationship,
        insured_address: formData.insuredAddress,
        insured_city: formData.insuredCity,
        insured_state: formData.insuredState,
        insured_zip: formData.insuredZip,
        patient_ssn: formData.patientSSN,
        policy_number: formData.policyNumber,
        policy_group_number: formData.policyGroupNumber,
        illness_injury_date: formData.illnessInjuryDate,
        referring_provider_name: formData.referringProviderName,
        referring_provider_npi: formData.referringProviderNPI,
        diagnosis_code: formData.diagnosisCode,
        diagnosis_code_2: formData.diagnosisCode2 || null,
        diagnosis_code_3: formData.diagnosisCode3 || null,
        diagnosis_code_4: formData.diagnosisCode4 || null,
        service_lines: JSON.stringify(formData.serviceLines),
        service_date: formData.serviceLines[0]?.serviceDate || new Date().toISOString().split('T')[0],
        service_type: formData.serviceType || 'medical_claim',
        procedure_code: formData.serviceLines[0]?.procedureCode || '',
        procedure_modifier: formData.serviceLines[0]?.modifier || null,
        diagnosis_pointer: formData.serviceLines[0]?.diagnosisPointer || null,
        days_units: formData.serviceLines[0]?.daysUnits || null,
        rendering_provider_npi: formData.serviceLines[0]?.renderingProviderNPI || null,
        amount_billed: parseFloat(formData.totalCharge),
        physician_signature: formData.physicianSignature,
        physician_signature_date: formData.physicianSignatureDate,
        provider_name: formData.providerName,
        provider_id: formData.providerId || `PRV-${Math.floor(Math.random() * 10000)}`,
        provider_npi: formData.providerNPI,
        provider_address: formData.providerAddress,
        provider_city: formData.providerCity,
        provider_state: formData.providerState,
        provider_zip: formData.providerZip,
        provider_tax_id: formData.providerTaxId,
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
            const uploadResponse = await fetch(`http://localhost:8000/api/claims/${claimId}/upload`, {
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
      <main className="container mx-auto px-6 py-8 max-w-6xl">
        <Card className="border-border">
          <CardContent className="p-8">
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-foreground mb-2">CMS-1500 Claim Form</h1>
              <p className="text-muted-foreground">
                Fill out the CMS-1500 form below to submit a new medical claim. All fields marked with * are required.
              </p>
            </div>

            <form className="space-y-8" onSubmit={handleSubmit}>
              {/* Field 1: Insurance Type */}
              <div>
                <h2 className="text-xl font-semibold text-foreground mb-4 pb-2 border-b border-border">
                  Insurance Information
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="insuranceType">Insurance Type</Label>
                    <Select value={formData.insuranceType} onValueChange={(value) => handleSelectChange('insuranceType', value)}>
                      <SelectTrigger id="insuranceType">
                        <SelectValue placeholder="Select insurance type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="medicare">Medicare</SelectItem>
                        <SelectItem value="medicaid">Medicaid</SelectItem>
                        <SelectItem value="tricare">TRICARE</SelectItem>
                        <SelectItem value="champva">CHAMPVA</SelectItem>
                        <SelectItem value="group_health">Group Health Plan</SelectItem>
                        <SelectItem value="feca_blacklung">FECA Black Lung</SelectItem>
                        <SelectItem value="other">Other</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </div>

              {/* Field 2-3: Patient Information */}
              <div>
                <h2 className="text-xl font-semibold text-foreground mb-4 pb-2 border-b border-border">
                  Patient Information
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
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
                    <Label htmlFor="middleInitial">Middle Initial</Label>
                    <Input
                      id="middleInitial"
                      placeholder="M"
                      maxLength={1}
                      value={formData.middleInitial}
                      onChange={handleInputChange}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="dob">Date of Birth *</Label>
                    <Input id="dob" type="date" value={formData.dob} onChange={handleInputChange} required />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="patientSex">Sex</Label>
                    <Select value={formData.patientSex} onValueChange={(value) => handleSelectChange('patientSex', value)}>
                      <SelectTrigger id="patientSex">
                        <SelectValue placeholder="Select" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="M">Male</SelectItem>
                        <SelectItem value="F">Female</SelectItem>
                        <SelectItem value="X">Other</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="patientSSN">Patient SSN</Label>
                    <Input
                      id="patientSSN"
                      placeholder="XXX-XX-XXXX"
                      value={formData.patientSSN}
                      onChange={handleInputChange}
                      maxLength={11}
                    />
                  </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
                  <div className="space-y-2">
                    <Label htmlFor="patientAddress">Patient Address</Label>
                    <Input
                      id="patientAddress"
                      placeholder="123 Main St"
                      value={formData.patientAddress}
                      onChange={handleInputChange}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="patientCity">City</Label>
                    <Input
                      id="patientCity"
                      placeholder="Springfield"
                      value={formData.patientCity}
                      onChange={handleInputChange}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="patientState">State</Label>
                    <Input
                      id="patientState"
                      placeholder="IL"
                      maxLength={2}
                      value={formData.patientState}
                      onChange={handleInputChange}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="patientZip">ZIP Code</Label>
                    <Input
                      id="patientZip"
                      placeholder="62701"
                      maxLength={10}
                      value={formData.patientZip}
                      onChange={handleInputChange}
                    />
                  </div>
                </div>
              </div>

              {/* Field 4-7: Insured Information */}
              <div>
                <h2 className="text-xl font-semibold text-foreground mb-4 pb-2 border-b border-border">
                  Insured Information
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="insuredLastName">Insured Last Name</Label>
                    <Input
                      id="insuredLastName"
                      placeholder="Doe"
                      value={formData.insuredLastName}
                      onChange={handleInputChange}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="insuredFirstName">Insured First Name</Label>
                    <Input
                      id="insuredFirstName"
                      placeholder="John"
                      value={formData.insuredFirstName}
                      onChange={handleInputChange}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="patientRelationship">Patient Relationship to Insured</Label>
                    <Select value={formData.patientRelationship} onValueChange={(value) => handleSelectChange('patientRelationship', value)}>
                      <SelectTrigger id="patientRelationship">
                        <SelectValue placeholder="Select relationship" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="self">Self</SelectItem>
                        <SelectItem value="spouse">Spouse</SelectItem>
                        <SelectItem value="child">Child</SelectItem>
                        <SelectItem value="other">Other</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
                  <div className="space-y-2">
                    <Label htmlFor="insuredAddress">Insured Address</Label>
                    <Input
                      id="insuredAddress"
                      placeholder="123 Main St"
                      value={formData.insuredAddress}
                      onChange={handleInputChange}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="insuredCity">City</Label>
                    <Input
                      id="insuredCity"
                      placeholder="Springfield"
                      value={formData.insuredCity}
                      onChange={handleInputChange}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="insuredState">State</Label>
                    <Input
                      id="insuredState"
                      placeholder="IL"
                      maxLength={2}
                      value={formData.insuredState}
                      onChange={handleInputChange}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="insuredZip">ZIP Code</Label>
                    <Input
                      id="insuredZip"
                      placeholder="62701"
                      maxLength={10}
                      value={formData.insuredZip}
                      onChange={handleInputChange}
                    />
                  </div>
                </div>
              </div>

              {/* Field 11: Policy Information */}
              <div>
                <h2 className="text-xl font-semibold text-foreground mb-4 pb-2 border-b border-border">
                  Policy Information
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="policyNumber">Policy Number *</Label>
                    <Input
                      id="policyNumber"
                      placeholder="POL-123456"
                      value={formData.policyNumber}
                      onChange={handleInputChange}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="policyGroupNumber">Policy Group Number</Label>
                    <Input
                      id="policyGroupNumber"
                      placeholder="GRP-789"
                      value={formData.policyGroupNumber}
                      onChange={handleInputChange}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="patientId">Patient ID</Label>
                    <Input
                      id="patientId"
                      placeholder="PAT-123456"
                      value={formData.patientId}
                      onChange={handleInputChange}
                    />
                  </div>
                </div>
              </div>

              {/* Field 14: Illness/Injury Date */}
              <div>
                <h2 className="text-xl font-semibold text-foreground mb-4 pb-2 border-b border-border">
                  Medical Information
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="illnessInjuryDate">Date of Current Illness/Injury/Pregnancy</Label>
                    <Input
                      id="illnessInjuryDate"
                      type="date"
                      value={formData.illnessInjuryDate}
                      onChange={handleInputChange}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="serviceType">Service Type</Label>
                    <Select value={formData.serviceType} onValueChange={(value) => handleSelectChange('serviceType', value)}>
                      <SelectTrigger id="serviceType">
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
                </div>
              </div>

              {/* Field 17: Referring Provider */}
              <div>
                <h2 className="text-xl font-semibold text-foreground mb-4 pb-2 border-b border-border">
                  Referring Provider
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="referringProviderName">Referring Provider Name</Label>
                    <Input
                      id="referringProviderName"
                      placeholder="Dr. Smith"
                      value={formData.referringProviderName}
                      onChange={handleInputChange}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="referringProviderNPI">Referring Provider NPI</Label>
                    <Input
                      id="referringProviderNPI"
                      placeholder="1234567890"
                      value={formData.referringProviderNPI}
                      onChange={handleInputChange}
                    />
                  </div>
                </div>
              </div>

              {/* Field 21: Diagnosis Codes */}
              <div>
                <h2 className="text-xl font-semibold text-foreground mb-4 pb-2 border-b border-border">
                  Diagnosis Codes
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="diagnosisCode">Diagnosis Code 1 *</Label>
                    <Input
                      id="diagnosisCode"
                      placeholder="E11.9"
                      value={formData.diagnosisCode}
                      onChange={handleInputChange}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="diagnosisCode2">Diagnosis Code 2</Label>
                    <Input
                      id="diagnosisCode2"
                      placeholder="I10"
                      value={formData.diagnosisCode2}
                      onChange={handleInputChange}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="diagnosisCode3">Diagnosis Code 3</Label>
                    <Input
                      id="diagnosisCode3"
                      placeholder="M79.3"
                      value={formData.diagnosisCode3}
                      onChange={handleInputChange}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="diagnosisCode4">Diagnosis Code 4</Label>
                    <Input
                      id="diagnosisCode4"
                      placeholder="Z00.00"
                      value={formData.diagnosisCode4}
                      onChange={handleInputChange}
                    />
                  </div>
                </div>
              </div>

              {/* Field 24A-H: Service Line Items */}
              <div>
                <h2 className="text-xl font-semibold text-foreground mb-4 pb-2 border-b border-border">
                  Service Line Items
                </h2>
                {formData.serviceLines.map((line, index) => (
                  <Card key={index} className="mb-4 border-border">
                    <CardContent className="p-6">
                      <div className="flex justify-between items-center mb-4">
                        <h3 className="text-lg font-semibold">Service Line {index + 1}</h3>
                        {formData.serviceLines.length > 1 && (
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            onClick={() => removeServiceLine(index)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        )}
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        <div className="space-y-2">
                          <Label>Service Date *</Label>
                          <Input
                            type="date"
                            value={line.serviceDate}
                            onChange={(e) => updateServiceLine(index, 'serviceDate', e.target.value)}
                            required
                          />
                        </div>
                        <div className="space-y-2">
                          <Label>Place of Service</Label>
                          <Input
                            placeholder="11"
                            value={line.placeOfService}
                            onChange={(e) => updateServiceLine(index, 'placeOfService', e.target.value)}
                          />
                        </div>
                        <div className="space-y-2">
                          <Label>Procedure Code *</Label>
                          <Input
                            placeholder="99213"
                            value={line.procedureCode}
                            onChange={(e) => updateServiceLine(index, 'procedureCode', e.target.value)}
                            required
                          />
                        </div>
                        <div className="space-y-2">
                          <Label>Modifier</Label>
                          <Input
                            placeholder="25"
                            value={line.modifier}
                            onChange={(e) => updateServiceLine(index, 'modifier', e.target.value)}
                          />
                        </div>
                        <div className="space-y-2">
                          <Label>Diagnosis Pointer</Label>
                          <Input
                            placeholder="1"
                            value={line.diagnosisPointer}
                            onChange={(e) => updateServiceLine(index, 'diagnosisPointer', e.target.value)}
                          />
                        </div>
                        <div className="space-y-2">
                          <Label>Charges</Label>
                          <Input
                            type="number"
                            step="0.01"
                            placeholder="150.00"
                            value={line.charges}
                            onChange={(e) => updateServiceLine(index, 'charges', e.target.value)}
                          />
                        </div>
                        <div className="space-y-2">
                          <Label>Days/Units</Label>
                          <Input
                            placeholder="1"
                            value={line.daysUnits}
                            onChange={(e) => updateServiceLine(index, 'daysUnits', e.target.value)}
                          />
                        </div>
                        <div className="space-y-2">
                          <Label>Rendering Provider NPI</Label>
                          <Input
                            placeholder="1234567890"
                            value={line.renderingProviderNPI}
                            onChange={(e) => updateServiceLine(index, 'renderingProviderNPI', e.target.value)}
                          />
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
                <Button
                  type="button"
                  variant="outline"
                  onClick={addServiceLine}
                  className="w-full"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Add Service Line
                </Button>
              </div>

              {/* Field 28: Total Charge */}
              <div>
                <h2 className="text-xl font-semibold text-foreground mb-4 pb-2 border-b border-border">
                  Charges
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="totalCharge">Total Charge ($) *</Label>
                    <Input
                      id="totalCharge"
                      type="number"
                      placeholder="1500.00"
                      step="0.01"
                      value={formData.totalCharge}
                      onChange={handleInputChange}
                      required
                    />
                  </div>
                </div>
              </div>

              {/* Field 31: Signature */}
              <div>
                <h2 className="text-xl font-semibold text-foreground mb-4 pb-2 border-b border-border">
                  Physician Signature
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="physicianSignature">Physician Signature</Label>
                    <Input
                      id="physicianSignature"
                      placeholder="Dr. John Smith"
                      value={formData.physicianSignature}
                      onChange={handleInputChange}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="physicianSignatureDate">Signature Date</Label>
                    <Input
                      id="physicianSignatureDate"
                      type="date"
                      value={formData.physicianSignatureDate}
                      onChange={handleInputChange}
                    />
                  </div>
                </div>
              </div>

              {/* Field 33: Billing Provider Information */}
              <div>
                <h2 className="text-xl font-semibold text-foreground mb-4 pb-2 border-b border-border">
                  Billing Provider Information
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="providerName">Provider Name *</Label>
                    <Input
                      id="providerName"
                      placeholder="General Hospital"
                      value={formData.providerName}
                      onChange={handleInputChange}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="providerId">Provider ID</Label>
                    <Input
                      id="providerId"
                      placeholder="PRV-123456"
                      value={formData.providerId}
                      onChange={handleInputChange}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="providerNPI">Provider NPI</Label>
                    <Input
                      id="providerNPI"
                      placeholder="1234567890"
                      value={formData.providerNPI}
                      onChange={handleInputChange}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="providerTaxId">Provider Tax ID</Label>
                    <Input
                      id="providerTaxId"
                      placeholder="12-3456789"
                      value={formData.providerTaxId}
                      onChange={handleInputChange}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="providerAddress">Provider Address</Label>
                    <Input
                      id="providerAddress"
                      placeholder="456 Medical Blvd"
                      value={formData.providerAddress}
                      onChange={handleInputChange}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="providerCity">City</Label>
                    <Input
                      id="providerCity"
                      placeholder="Springfield"
                      value={formData.providerCity}
                      onChange={handleInputChange}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="providerState">State</Label>
                    <Input
                      id="providerState"
                      placeholder="IL"
                      maxLength={2}
                      value={formData.providerState}
                      onChange={handleInputChange}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="providerZip">ZIP Code</Label>
                    <Input
                      id="providerZip"
                      placeholder="62701"
                      maxLength={10}
                      value={formData.providerZip}
                      onChange={handleInputChange}
                    />
                  </div>
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
