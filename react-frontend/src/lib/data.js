// Mock data for the claims dashboard
export const claimsData = [
  {
    id: "CLM-2024-001",
    patientId: "PAT-123456",
    patientName: "John Smith",
    dob: "1985-03-15",
    status: "approved",
    type: "Inpatient",
    provider: "General Hospital",
    amount: 2500.00,
    submitted: "2024-10-15",
    serviceDate: "2024-10-10",
    diagnosis: "Appendectomy - routine surgical removal of appendix due to acute appendicitis",
    notes: "Patient presented with acute abdominal pain. Surgery performed successfully without complications.",
    extractedData: {
      billedAmount: 2500.00,
      policyNumber: "POL-789123",
      serviceDate: "2024-10-10"
    },
    completeness: 95,
    confidence: 92,
    decisionReasoning: "All required documentation provided. Medical necessity clearly established. Procedure appropriate for diagnosis. No coverage limitations apply.",
    timeline: [
      { status: "Claim Submitted", date: "Oct 15, 2024", completed: true },
      { status: "Initial Review", date: "Oct 16, 2024", completed: true },
      { status: "Medical Review", date: "Oct 18, 2024", completed: true },
      { status: "Approved", date: "Oct 20, 2024", completed: true }
    ],
    documents: [
      { name: "Medical Report.pdf", size: "2.3 MB", uploadDate: "Oct 15, 2024" },
      { name: "Lab Results.pdf", size: "1.8 MB", uploadDate: "Oct 15, 2024" },
      { name: "Invoice.pdf", size: "945 KB", uploadDate: "Oct 15, 2024" }
    ]
  },
  {
    id: "CLM-2024-002",
    patientId: "PAT-789012",
    patientName: "Sarah Johnson",
    dob: "1992-07-22",
    status: "pending",
    type: "Outpatient",
    provider: "City Medical Center",
    amount: 850.00,
    submitted: "2024-10-20",
    serviceDate: "2024-10-18",
    diagnosis: "Physical therapy for post-surgical knee rehabilitation",
    notes: "Continuing physical therapy following knee arthroscopy. Patient showing good progress.",
    extractedData: {
      billedAmount: 850.00,
      policyNumber: "POL-456789",
      serviceDate: "2024-10-18"
    },
    completeness: 88,
    confidence: 85,
    decisionReasoning: "Standard physical therapy claim. Waiting for treatment notes from previous sessions to verify necessity.",
    timeline: [
      { status: "Claim Submitted", date: "Oct 20, 2024", completed: true },
      { status: "Initial Review", date: "Oct 21, 2024", completed: true },
      { status: "Medical Review", date: "Oct 23, 2024", completed: false },
      { status: "Decision Pending", date: "Pending", completed: false }
    ],
    documents: [
      { name: "PT Assessment.pdf", size: "1.2 MB", uploadDate: "Oct 20, 2024" },
      { name: "Treatment Plan.pdf", size: "890 KB", uploadDate: "Oct 20, 2024" }
    ]
  },
  {
    id: "CLM-2024-003",
    patientId: "PAT-345678",
    patientName: "Michael Davis",
    dob: "1978-11-08",
    status: "under-review",
    type: "Emergency",
    provider: "Emergency Medical Center",
    amount: 3200.00,
    submitted: "2024-10-25",
    serviceDate: "2024-10-24",
    diagnosis: "Emergency room visit for chest pain evaluation, including ECG and cardiac enzymes",
    notes: "Patient presented with acute chest pain. All cardiac tests negative. Discharged with follow-up recommendations.",
    extractedData: {
      billedAmount: 3200.00,
      policyNumber: "POL-123987",
      serviceDate: "2024-10-24"
    },
    completeness: 92,
    confidence: 88,
    decisionReasoning: "Emergency claim under review. Verifying medical necessity of all tests performed during ER visit.",
    timeline: [
      { status: "Claim Submitted", date: "Oct 25, 2024", completed: true },
      { status: "Initial Review", date: "Oct 26, 2024", completed: true },
      { status: "Medical Review", date: "In Progress", completed: false },
      { status: "Decision Pending", date: "Pending", completed: false }
    ],
    documents: [
      { name: "ER Report.pdf", size: "3.1 MB", uploadDate: "Oct 25, 2024" },
      { name: "ECG Results.pdf", size: "1.5 MB", uploadDate: "Oct 25, 2024" },
      { name: "Lab Results.pdf", size: "2.2 MB", uploadDate: "Oct 25, 2024" }
    ]
  },
  {
    id: "CLM-2024-004",
    patientId: "PAT-567890",
    patientName: "Emily Wilson",
    dob: "1995-02-14",
    status: "rejected",
    type: "Preventive",
    provider: "Community Health Clinic",
    amount: 450.00,
    submitted: "2024-10-12",
    serviceDate: "2024-10-10",
    diagnosis: "Annual wellness exam and preventive screening",
    notes: "Routine annual physical examination with basic preventive care screenings.",
    extractedData: {
      billedAmount: 450.00,
      policyNumber: "POL-654321",
      serviceDate: "2024-10-10"
    },
    completeness: 75,
    confidence: 70,
    decisionReasoning: "Claim denied due to insufficient documentation. Missing required preventive care codes and screening results.",
    timeline: [
      { status: "Claim Submitted", date: "Oct 12, 2024", completed: true },
      { status: "Initial Review", date: "Oct 13, 2024", completed: true },
      { status: "Medical Review", date: "Oct 15, 2024", completed: true },
      { status: "Rejected", date: "Oct 17, 2024", completed: true }
    ],
    documents: [
      { name: "Wellness Exam.pdf", size: "1.1 MB", uploadDate: "Oct 12, 2024" }
    ]
  }
]

export function getStats() {
  const total = claimsData.length
  const approved = claimsData.filter(claim => claim.status === 'approved').length
  const pending = claimsData.filter(claim => claim.status === 'pending' || claim.status === 'under-review').length
  const rejected = claimsData.filter(claim => claim.status === 'rejected').length
  
  return { total, approved, pending, rejected }
}

export function getClaimById(id) {
  return claimsData.find(claim => claim.id === id)
}