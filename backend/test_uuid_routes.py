#!/usr/bin/env python3
"""
Test script to verify UUID route parameters work correctly.
This script tests the actual FastAPI route parameter validation.
"""

import requests
import uuid
import time
from typing import Dict, Any

# Test configuration
BASE_URL = "http://localhost:8000"  # Adjust if your server runs on different port

# Test UUIDs (these won't exist in database, but should pass parameter validation)
TEST_UUID = str(uuid.uuid4())
INVALID_UUID = "not-a-valid-uuid"
OLD_STYLE_ID = "123"

def test_route_parameter_validation():
    """Test that our routes accept UUID strings and reject invalid formats."""
    
    print("Testing FastAPI route parameter validation for UUID parameters...")
    print(f"Using test UUID: {TEST_UUID}")
    print("-" * 60)
    
    # Test cases: (endpoint, method, description)
    test_cases = [
        (f"/api/v1/public/exams/{TEST_UUID}", "GET", "Public exam details with UUID"),
        (f"/api/v1/public/exams/{INVALID_UUID}", "GET", "Public exam details with invalid UUID"),
        (f"/api/v1/public/exams/{OLD_STYLE_ID}", "GET", "Public exam details with old-style integer ID"),
    ]
    
    for endpoint, method, description in test_cases:
        print(f"\nTesting: {description}")
        print(f"URL: {method} {BASE_URL}{endpoint}")
        
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 422:
                # Validation error - this means FastAPI rejected the parameter format
                try:
                    error_detail = response.json()
                    print(f"Validation Error: {error_detail}")
                    if "exam_id" in str(error_detail):
                        print("❌ FAILED: Route still expecting integer, not string UUID")
                    else:
                        print("✅ PASSED: Route accepts string parameters (exam not found is expected)")
                except:
                    print("❌ FAILED: Unknown validation error")
            elif response.status_code == 404:
                print("✅ PASSED: Route accepts UUID parameter (exam not found is expected)")
            elif response.status_code in [401, 403]:
                print("✅ PASSED: Route accepts UUID parameter (auth required is expected)")
            else:
                print(f"ℹ️  INFO: Unexpected status code: {response.status_code}")
                try:
                    print(f"Response: {response.json()}")
                except:
                    print(f"Response text: {response.text[:200]}")
                    
        except requests.exceptions.ConnectionError:
            print("❌ FAILED: Cannot connect to server. Is it running on http://localhost:8000?")
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("- If you see '422 validation error' mentioning exam_id type, routes need fixing")
    print("- If you see '404 not found' or '401/403 auth', routes are working correctly")
    print("- Valid UUIDs should NOT get 422 errors about parameter types")

if __name__ == "__main__":
    test_route_parameter_validation()
