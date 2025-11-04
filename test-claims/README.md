# Test Claims Examples

This folder contains example insurance claims for testing the ClaimsAI system:

## Files Included:

### 1. Valid Claim Examples
**Files:** `valid_claim_example.txt` | `valid_claim_example.pdf`
- Complete policyholder information
- Clear incident description with specific details
- Proper documentation references
- Realistic damage assessment
- Filed within policy period
- All required fields completed
- **Expected Result: APPROVED**

### 2. Invalid Claim Examples
**Files:** `invalid_claim_example.txt` | `invalid_claim_example.pdf`
- Expired policy (2019 policy, 2024 incident)
- Late filing (8 months after incident)
- Missing critical information
- Vague incident description
- No supporting documentation
- Suspicious damage claims
- **Expected Result: DENIED**

## Testing Instructions:

1. **Upload Test Claims:**
   - **PDF Files**: Upload `valid_claim_example.pdf` or `invalid_claim_example.pdf` through the React frontend
   - **Text Files**: Upload `.txt` versions or copy/paste content into manual text input
   - **Format Testing**: Test both PDF and text processing capabilities

2. **Expected GPT-4 Analysis:**
   - Valid claim should be flagged as legitimate with approval recommendation
   - Invalid claim should be flagged with specific issues and denial recommendation

3. **Key Validation Points:**
   - Policy number validation
   - Filing deadline compliance
   - Required documentation completeness
   - Incident description clarity
   - Damage assessment reasonableness

## Usage:
These examples help test the AI's ability to:
- Identify complete vs incomplete claims
- Detect policy compliance issues
- Flag suspicious circumstances
- Validate required documentation
- Assess claim legitimacy

Perfect for demonstrating the ClaimsAI system's analytical capabilities!