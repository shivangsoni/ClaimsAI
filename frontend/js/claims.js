// Claims AI Frontend JavaScript
// API Base URL - change this to match your Python backend
const API_BASE_URL = 'http://localhost:5000/api';

// Global variables to store current data
let currentClaimData = {};
let currentValidationResult = {};
let currentEligibilityResult = {};

// Utility function to show alerts
function showAlert(message, type = 'info') {
    const alertArea = document.getElementById('alertArea');
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    alertArea.innerHTML = alertHtml;
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const alert = alertArea.querySelector('.alert');
        if (alert) {
            alert.remove();
        }
    }, 5000);
}

// Utility function to make API calls
async function apiCall(endpoint, method = 'GET', data = null) {
    try {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
        };
        
        if (data) {
            options.body = JSON.stringify(data);
        }
        
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'API call failed');
        }
        
        return result;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// ITERATION 1: Claims Validation Functions
function getFormData(formId) {
    const form = document.getElementById(formId);
    const formData = new FormData(form);
    const data = {};
    
    for (let [key, value] of formData.entries()) {
        data[key] = value;
    }
    
    return data;
}

async function validateClaim() {
    try {
        const claimData = getFormData('claimForm');
        currentClaimData = claimData;
        
        showAlert('Validating claim...', 'info');
        
        const result = await apiCall('/claims/validate', 'POST', claimData);
        currentValidationResult = result;
        
        displayValidationResults(result);
        showAlert('Claim validation completed', 'success');
        
    } catch (error) {
        showAlert(`Validation failed: ${error.message}`, 'danger');
    }
}

function displayValidationResults(result) {
    const resultsDiv = document.getElementById('validationResults');
    const contentDiv = document.getElementById('validationContent');
    
    let html = `
        <div class="mb-3">
            <h6>Validation Status: <span class="badge bg-${result.is_valid ? 'success' : 'danger'}">
                ${result.is_valid ? 'VALID' : 'INVALID'}
            </span></h6>
        </div>
    `;
    
    if (result.recommendation) {
        const badgeClass = getBadgeClass(result.recommendation);
        html += `
            <div class="mb-3">
                <h6>Recommendation:</h6>
                <span class="badge bg-${badgeClass}">${result.recommendation}</span>
            </div>
        `;
    }
    
    if (result.issues && result.issues.length > 0) {
        html += '<h6>Issues Found:</h6><ul class="list-group">';
        result.issues.forEach(issue => {
            const severityClass = getSeverityClass(issue.severity);
            html += `
                <li class="list-group-item d-flex justify-content-between align-items-start">
                    <div class="ms-2 me-auto">
                        <div class="fw-bold">${issue.type || 'Issue'}</div>
                        ${issue.message}
                        ${issue.field ? `<br><small class="text-muted">Field: ${issue.field}</small>` : ''}
                    </div>
                    <span class="badge bg-${severityClass} rounded-pill">${issue.severity}</span>
                </li>
            `;
        });
        html += '</ul>';
    } else {
        html += '<div class="alert alert-success">No issues found!</div>';
    }
    
    contentDiv.innerHTML = html;
    resultsDiv.style.display = 'block';
}

async function submitClaim() {
    try {
        const claimData = getFormData('claimForm');
        
        showAlert('Submitting claim...', 'info');
        
        const result = await apiCall('/claims/submit', 'POST', claimData);
        
        showAlert(`Claim submitted successfully! Claim ID: ${result.claim_id}`, 'success');
        
        // Reset form
        document.getElementById('claimForm').reset();
        document.getElementById('validationResults').style.display = 'none';
        
    } catch (error) {
        showAlert(`Submission failed: ${error.message}`, 'danger');
    }
}

// ITERATION 2: Eligibility Functions
async function checkEligibility() {
    try {
        const eligibilityData = getFormData('eligibilityForm');
        
        showAlert('Checking eligibility...', 'info');
        
        const result = await apiCall('/eligibility/check', 'POST', eligibilityData);
        currentEligibilityResult = result;
        
        displayEligibilityResults(result);
        showAlert('Eligibility check completed', 'success');
        
    } catch (error) {
        showAlert(`Eligibility check failed: ${error.message}`, 'danger');
    }
}

function displayEligibilityResults(result) {
    const resultsDiv = document.getElementById('eligibilityResults');
    const contentDiv = document.getElementById('eligibilityContent');
    
    let html = `
        <div class="mb-3">
            <h6>Eligibility Status: <span class="badge bg-${result.eligible ? 'success' : 'danger'}">
                ${result.eligible ? 'ELIGIBLE' : 'NOT ELIGIBLE'}
            </span></h6>
        </div>
    `;
    
    if (result.coverage_calculation) {
        const calc = result.coverage_calculation;
        html += `
            <div class="mb-3">
                <h6>Coverage Breakdown:</h6>
                <table class="table table-sm">
                    <tr><td>Approved Amount:</td><td>$${calc.approved_amount?.toFixed(2) || '0.00'}</td></tr>
                    <tr><td>Insurance Payment:</td><td>$${calc.insurance_payment?.toFixed(2) || '0.00'}</td></tr>
                    <tr><td>Patient Responsibility:</td><td>$${calc.patient_responsibility?.toFixed(2) || '0.00'}</td></tr>
                    <tr><td>Coverage Percentage:</td><td>${calc.coverage_percentage || 0}%</td></tr>
                </table>
            </div>
        `;
    }
    
    if (result.checks && result.checks.length > 0) {
        html += '<h6>Eligibility Checks:</h6><ul class="list-group">';
        result.checks.forEach(check => {
            const statusClass = check.passed ? 'success' : 'danger';
            html += `
                <li class="list-group-item d-flex justify-content-between align-items-start">
                    <div class="ms-2 me-auto">
                        <div class="fw-bold">${check.check_type}</div>
                        ${check.message}
                    </div>
                    <span class="badge bg-${statusClass} rounded-pill">
                        ${check.passed ? 'PASS' : 'FAIL'}
                    </span>
                </li>
            `;
        });
        html += '</ul>';
    }
    
    contentDiv.innerHTML = html;
    resultsDiv.style.display = 'block';
}

// ITERATION 3: Recommendations Functions
async function generateRecommendation() {
    try {
        // Use current claim and eligibility data if available
        const requestData = {
            claim_data: currentClaimData,
            validation_result: currentValidationResult,
            eligibility_result: currentEligibilityResult
        };
        
        // If no data is available, use sample data
        if (Object.keys(currentClaimData).length === 0) {
            requestData.claim_data = {
                claim_id: 'SAMPLE_001',
                patient_id: 'PAT_12345',
                policy_number: 'POL12345678',
                amount_billed: 1500.00,
                service_type: 'diagnostics'
            };
            requestData.validation_result = { is_valid: true, issues: [] };
            requestData.eligibility_result = { eligible: true };
        }
        
        showAlert('Generating AI recommendation...', 'info');
        
        const result = await apiCall('/recommendations/generate', 'POST', requestData);
        
        displayRecommendation(result);
        showAlert('AI recommendation generated', 'success');
        
    } catch (error) {
        showAlert(`Recommendation generation failed: ${error.message}`, 'danger');
    }
}

function displayRecommendation(result) {
    const resultsDiv = document.getElementById('recommendationResults');
    const contentDiv = document.getElementById('recommendationContent');
    const actionsDiv = document.getElementById('reviewerActions');
    
    const badgeClass = getRecommendationBadgeClass(result.recommendation);
    
    let html = `
        <div class="row">
            <div class="col-md-6">
                <h6>AI Recommendation:</h6>
                <span class="badge bg-${badgeClass} fs-6">${result.recommendation}</span>
            </div>
            <div class="col-md-6">
                <h6>Confidence Score:</h6>
                <div class="progress">
                    <div class="progress-bar" style="width: ${result.confidence}%">${result.confidence}%</div>
                </div>
            </div>
        </div>
        <hr>
        <div class="mb-3">
            <h6>Reason:</h6>
            <p>${result.reason}</p>
        </div>
        <div class="mb-3">
            <h6>Priority Level:</h6>
            <span class="badge bg-${getPriorityBadgeClass(result.priority)}">${result.priority?.toUpperCase()}</span>
        </div>
    `;
    
    if (result.suggested_actions && result.suggested_actions.length > 0) {
        html += '<h6>Suggested Actions:</h6><ul>';
        result.suggested_actions.forEach(action => {
            html += `<li>${action}</li>`;
        });
        html += '</ul>';
    }
    
    if (result.overall_score !== undefined) {
        html += `
            <div class="mt-3">
                <small class="text-muted">Overall Score: ${result.overall_score.toFixed(1)}/100</small>
            </div>
        `;
    }
    
    contentDiv.innerHTML = html;
    resultsDiv.style.display = 'block';
    actionsDiv.style.display = 'block';
}

async function submitReview() {
    try {
        const reviewData = getFormData('reviewForm');
        reviewData.claim_id = currentClaimData.claim_id || 'SAMPLE_001';
        
        showAlert('Submitting review...', 'info');
        
        const result = await apiCall('/recommendations/validate', 'POST', reviewData);
        
        showAlert('Review submitted successfully', 'success');
        
        // Reset review form
        document.getElementById('reviewForm').reset();
        
    } catch (error) {
        showAlert(`Review submission failed: ${error.message}`, 'danger');
    }
}

// Utility functions for styling
function getBadgeClass(recommendation) {
    const rec = recommendation.toLowerCase();
    if (rec.includes('approve')) return 'success';
    if (rec.includes('reject')) return 'danger';
    if (rec.includes('flag')) return 'warning';
    return 'secondary';
}

function getSeverityClass(severity) {
    switch (severity) {
        case 'high': return 'danger';
        case 'medium': return 'warning';
        case 'low': return 'info';
        default: return 'secondary';
    }
}

function getRecommendationBadgeClass(recommendation) {
    const rec = recommendation.toLowerCase();
    if (rec.includes('auto_approve')) return 'success';
    if (rec.includes('approve')) return 'success';
    if (rec.includes('reject')) return 'danger';
    if (rec.includes('review')) return 'warning';
    if (rec.includes('return')) return 'info';
    return 'secondary';
}

function getPriorityBadgeClass(priority) {
    switch (priority?.toLowerCase()) {
        case 'high': return 'danger';
        case 'medium': return 'warning';
        case 'low': return 'info';
        default: return 'secondary';
    }
}

// API Health Check
async function checkAPIHealth() {
    try {
        const result = await apiCall('/status');
        showAlert('Backend API is connected and running', 'success');
    } catch (error) {
        showAlert('Backend API is not responding. Please ensure the Python backend is running on http://localhost:5000', 'warning');
    }
}

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    // Check API health on page load
    setTimeout(checkAPIHealth, 1000);
    
    // Set default dates to today
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('service_date').value = today;
    document.getElementById('elig_service_date').value = today;
});