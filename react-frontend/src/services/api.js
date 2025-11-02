import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds for file uploads
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
    });
    return response.data;
  },

  // Analyze text directly
  analyzeText: async (text, claimType = 'medical_claim') => {
    const response = await api.post('/claims/analyze-text', {
      text,
      claim_type: claimType,
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

  // Health check
  healthCheck: async () => {
    const response = await api.get('/status');
    return response.data;
  },
};

export default api;