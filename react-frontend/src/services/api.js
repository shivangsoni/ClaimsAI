import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 90000, // 90 seconds for file uploads and AI processing
});

export const claimsAPI = {
  // Upload and analyze document
  uploadDocument: async (file, claimType = 'medical_claim') => {
    const formData = new FormData();
    formData.append('document', file);
    formData.append('claim_type', claimType);

    const response = await api.post('/claims/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 120000, // 2 minutes for document upload and AI processing
    });
    return response.data;
  },

  // Analyze text directly
  analyzeText: async (text, claimType = 'medical_claim') => {
    const response = await api.post('/claims/analyze-text', {
      text,
      claim_type: claimType,
    }, {
      timeout: 120000, // 2 minutes for AI text analysis
    });
    return response.data;
  },

  // Submit traditional claim
  submitClaim: async (claimData) => {
    const response = await api.post('/claims/submit', claimData);
    return response.data;
  },

  // Validate claim
  validateClaim: async (claimData) => {
    const response = await api.post('/claims/validate', claimData);
    return response.data;
  },

  // Get claim status
  getClaimStatus: async (claimId) => {
    const response = await api.get(`/claims/status/${claimId}`);
    return response.data;
  },

  // Get all claims with pagination and filtering
  getAllClaims: async (params = {}) => {
    const response = await api.get('/claims/list', { params });
    return response.data;
  },

  // Get detailed claim information
  getClaimDetails: async (claimId) => {
    const response = await api.get(`/claims/details/${claimId}`);
    return response.data;
  },

  // Get dashboard statistics
  getClaimsStats: async () => {
    const response = await api.get('/claims/stats');
    return response.data;
  },

  // Check eligibility
  checkEligibility: async (eligibilityData) => {
    const response = await api.post('/eligibility/check', eligibilityData);
    return response.data;
  },

  // Generate recommendation
  generateRecommendation: async (requestData) => {
    const response = await api.post('/recommendations/generate', requestData);
    return response.data;
  },

  // Validate recommendation
  validateRecommendation: async (validationData) => {
    const response = await api.post('/recommendations/validate', validationData);
    return response.data;
  },

  // Download document
  downloadDocument: async (documentId) => {
    const response = await api.get(`/claims/documents/download/${documentId}`, {
      responseType: 'blob', // Important for file downloads
    });
    return response;
  },

  // Health check
  healthCheck: async () => {
    const response = await api.get('/status');
    return response.data;
  },
};

export default api;