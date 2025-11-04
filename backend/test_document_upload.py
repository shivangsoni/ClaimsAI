#!/usr/bin/env python3

import requests
import os
import json

def test_document_upload():
    """Test document upload with GPT-4 analysis"""
    
    url = 'http://localhost:5000/api/claims/upload'
    test_file_path = '../test-claims/valid_claim_example.pdf'
    
    if not os.path.exists(test_file_path):
        print(f'Test file not found: {test_file_path}')
        return
    
    print('Uploading document for GPT-4 analysis...')
    print(f'File: {test_file_path}')
    
    try:
        with open(test_file_path, 'rb') as f:
            files = {'document': f}
            data = {'claim_type': 'medical_claim'}
            
            response = requests.post(url, files=files, data=data, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                claim_id = result.get('claim_id')
                print(f'✅ Success! Claim ID: {claim_id}')
                
                # Check GPT-4 analysis results
                analysis = result.get('document_analysis', {})
                print(f'\n📋 GPT-4 Analysis Results:')
                print(f'   Decision: {analysis.get("overall_status", "N/A")}')
                print(f'   Confidence: {analysis.get("confidence_level", "N/A")}%')
                print(f'   Completeness: {analysis.get("completeness_score", "N/A")}%')
                
                reasoning = analysis.get('decision_reasoning')
                if reasoning:
                    print(f'\n🤖 Decision Reasoning:')
                    print(f'   {reasoning}')
                else:
                    print('\n⚠️ No GPT-4 decision reasoning found')
                
                key_factors = analysis.get('key_factors', [])
                if key_factors:
                    print(f'\n🔍 Key Factors:')
                    for i, factor in enumerate(key_factors, 1):
                        print(f'   {i}. {factor}')
                
                # Test database integration
                print(f'\n🗄️ Testing database integration...')
                list_response = requests.get(f'http://localhost:5000/api/claims/details/{claim_id}')
                if list_response.status_code == 200:
                    claim_details = list_response.json()
                    recommendations = claim_details.get('recommendations', [])
                    validations = claim_details.get('validations', [])
                    
                    print(f'   Recommendations saved: {len(recommendations)}')
                    print(f'   Validations saved: {len(validations)}')
                    
                    if recommendations:
                        rec = recommendations[0]
                        print(f'   Latest recommendation: {rec.get("recommendation")} ({rec.get("confidence")}% confidence)')
                        print(f'   Reasoning saved: {"Yes" if rec.get("reason") else "No"}')
                else:
                    print(f'   ❌ Failed to retrieve claim details: {list_response.status_code}')
                    
            else:
                print(f'❌ Error: {response.status_code}')
                print(f'Response: {response.text}')
                
    except requests.exceptions.Timeout:
        print('⏰ Request timed out. GPT-4 analysis may take longer for complex documents.')
    except Exception as e:
        print(f'❌ Unexpected error: {str(e)}')

if __name__ == '__main__':
    test_document_upload()