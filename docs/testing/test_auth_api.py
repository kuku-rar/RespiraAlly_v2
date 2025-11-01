#!/usr/bin/env python3
"""
RespiraAlly V2.0 - Authentication API Test Script
Comprehensive testing of all auth endpoints
"""

import json
import requests
from datetime import datetime
from typing import Dict, Any

BASE_URL = "http://localhost:8000/api/v1"
RESULTS = []


def log_test(test_name: str, endpoint: str, method: str, success: bool,
             status_code: int, response: Any, notes: str = ""):
    """Log test result"""
    result = {
        "test_name": test_name,
        "endpoint": endpoint,
        "method": method,
        "success": success,
        "status_code": status_code,
        "response_summary": str(response)[:200],
        "notes": notes,
        "timestamp": datetime.now().isoformat()
    }
    RESULTS.append(result)

    status = "✅ PASS" if success else "❌ FAIL"
    print(f"\n{status} | {test_name}")
    print(f"  Endpoint: {method} {endpoint}")
    print(f"  Status: {status_code}")
    if notes:
        print(f"  Notes: {notes}")


def test_therapist_login_valid():
    """Test 1: Valid therapist login"""
    endpoint = f"{BASE_URL}/auth/therapist/login"
    payload = {
        "email": "test@therapist.com",
        "password": "SecurePass123!"
    }

    try:
        response = requests.post(endpoint, json=payload)
        data = response.json()

        success = (
            response.status_code == 200 and
            "access_token" in data and
            "refresh_token" in data and
            data["user"]["role"] == "THERAPIST"
        )

        log_test(
            "Valid Therapist Login",
            "/auth/therapist/login",
            "POST",
            success,
            response.status_code,
            data,
            "Returns access_token, refresh_token, and user info"
        )

        return data.get("access_token"), data.get("refresh_token")

    except Exception as e:
        log_test("Valid Therapist Login", "/auth/therapist/login", "POST",
                False, 0, str(e), f"Exception: {str(e)}")
        return None, None


def test_therapist_login_invalid_password():
    """Test 2: Invalid password"""
    endpoint = f"{BASE_URL}/auth/therapist/login"
    payload = {
        "email": "test@therapist.com",
        "password": "WrongPassword"
    }

    try:
        response = requests.post(endpoint, json=payload)
        data = response.json()

        success = (
            response.status_code == 401 and
            "error" in data and
            data["error"]["type"] == "UnauthorizedError"
        )

        log_test(
            "Invalid Password",
            "/auth/therapist/login",
            "POST",
            success,
            response.status_code,
            data,
            "Should return 401 UnauthorizedError"
        )

    except Exception as e:
        log_test("Invalid Password", "/auth/therapist/login", "POST",
                False, 0, str(e))


def test_therapist_login_nonexistent_email():
    """Test 3: Non-existent email"""
    endpoint = f"{BASE_URL}/auth/therapist/login"
    payload = {
        "email": "nonexistent@test.com",
        "password": "SecurePass123!"
    }

    try:
        response = requests.post(endpoint, json=payload)
        data = response.json()

        success = (
            response.status_code == 401 and
            "error" in data
        )

        log_test(
            "Non-existent Email",
            "/auth/therapist/login",
            "POST",
            success,
            response.status_code,
            data,
            "Should return 401 for non-existent email"
        )

    except Exception as e:
        log_test("Non-existent Email", "/auth/therapist/login", "POST",
                False, 0, str(e))


def test_invalid_email_format():
    """Test 4: Invalid email format"""
    endpoint = f"{BASE_URL}/auth/therapist/login"
    payload = {
        "email": "invalid-email",
        "password": "SecurePass123!"
    }

    try:
        response = requests.post(endpoint, json=payload)
        data = response.json()

        success = (
            response.status_code == 422 and
            "error" in data and
            data["error"]["type"] == "RequestValidationError"
        )

        log_test(
            "Invalid Email Format",
            "/auth/therapist/login",
            "POST",
            success,
            response.status_code,
            data,
            "Should return 422 validation error"
        )

    except Exception as e:
        log_test("Invalid Email Format", "/auth/therapist/login", "POST",
                False, 0, str(e))


def test_empty_password():
    """Test 5: Empty password"""
    endpoint = f"{BASE_URL}/auth/therapist/login"
    payload = {
        "email": "test@therapist.com",
        "password": ""
    }

    try:
        response = requests.post(endpoint, json=payload)
        data = response.json()

        success = (
            response.status_code == 422 and
            "error" in data
        )

        log_test(
            "Empty Password",
            "/auth/therapist/login",
            "POST",
            success,
            response.status_code,
            data,
            "Should return 422 for empty password (min 8 chars)"
        )

    except Exception as e:
        log_test("Empty Password", "/auth/therapist/login", "POST",
                False, 0, str(e))


def test_protected_endpoint_with_token(token: str):
    """Test 6: Access protected endpoint with valid token"""
    endpoint = f"{BASE_URL}/patients/"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(endpoint, headers=headers, params={"limit": 3})
        data = response.json()

        success = response.status_code == 200

        log_test(
            "Protected Endpoint with Valid Token",
            "/patients/",
            "GET",
            success,
            response.status_code,
            data,
            f"Token works, returned {len(data.get('items', []))} patients"
        )

    except Exception as e:
        log_test("Protected Endpoint with Valid Token", "/patients/", "GET",
                False, 0, str(e))


def test_protected_endpoint_without_token():
    """Test 7: Access protected endpoint without token"""
    endpoint = f"{BASE_URL}/patients/"

    try:
        response = requests.get(endpoint)
        data = response.json()

        success = (
            response.status_code == 401 and
            "error" in data
        )

        log_test(
            "Protected Endpoint Without Token",
            "/patients/",
            "GET",
            success,
            response.status_code,
            data,
            "Should return 401 when no token provided"
        )

    except Exception as e:
        log_test("Protected Endpoint Without Token", "/patients/", "GET",
                False, 0, str(e))


def test_therapist_register():
    """Test 8: Therapist registration"""
    endpoint = f"{BASE_URL}/auth/therapist/register"
    payload = {
        "email": f"therapist_{datetime.now().timestamp()}@test.com",
        "password": "NewSecurePass123!",
        "full_name": "New Test Therapist"
    }

    try:
        response = requests.post(endpoint, json=payload)
        data = response.json()

        success = (
            response.status_code == 201 and
            "access_token" in data and
            data["user"]["role"] == "THERAPIST"
        )

        log_test(
            "Therapist Registration",
            "/auth/therapist/register",
            "POST",
            success,
            response.status_code,
            data,
            "Auto-login after registration"
        )

    except Exception as e:
        log_test("Therapist Registration", "/auth/therapist/register", "POST",
                False, 0, str(e))


def test_duplicate_email_registration():
    """Test 9: Duplicate email registration"""
    endpoint = f"{BASE_URL}/auth/therapist/register"
    payload = {
        "email": "test@therapist.com",  # Already exists
        "password": "NewSecurePass123!",
        "full_name": "Duplicate Test"
    }

    try:
        response = requests.post(endpoint, json=payload)
        data = response.json()

        success = (
            response.status_code == 409 and
            "error" in data and
            data["error"]["type"] == "ConflictError"
        )

        log_test(
            "Duplicate Email Registration",
            "/auth/therapist/register",
            "POST",
            success,
            response.status_code,
            data,
            "Should return 409 ConflictError"
        )

    except Exception as e:
        log_test("Duplicate Email Registration", "/auth/therapist/register", "POST",
                False, 0, str(e))


def test_refresh_token(refresh_token: str):
    """Test 10: Refresh access token"""
    endpoint = f"{BASE_URL}/auth/refresh"
    payload = {"refresh_token": refresh_token}

    try:
        response = requests.post(endpoint, json=payload)
        data = response.json()

        success = (
            response.status_code == 200 and
            "access_token" in data
        )

        log_test(
            "Refresh Access Token",
            "/auth/refresh",
            "POST",
            success,
            response.status_code,
            data,
            "Returns new access_token"
        )

    except Exception as e:
        log_test("Refresh Access Token", "/auth/refresh", "POST",
                False, 0, str(e))


def test_logout(token: str):
    """Test 11: Logout (revoke token)"""
    endpoint = f"{BASE_URL}/auth/logout"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"revoke_all_tokens": False}

    try:
        response = requests.post(endpoint, headers=headers, json=payload)

        success = response.status_code == 204

        log_test(
            "Logout (Revoke Token)",
            "/auth/logout",
            "POST",
            success,
            response.status_code,
            "No content (204)",
            "Token should be blacklisted"
        )

    except Exception as e:
        log_test("Logout (Revoke Token)", "/auth/logout", "POST",
                False, 0, str(e))


def test_use_revoked_token(token: str):
    """Test 12: Try using revoked token"""
    endpoint = f"{BASE_URL}/patients/"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(endpoint, headers=headers, params={"limit": 1})
        data = response.json()

        success = (
            response.status_code == 401 and
            "error" in data
        )

        log_test(
            "Use Revoked Token",
            "/patients/",
            "GET",
            success,
            response.status_code,
            data,
            "Should return 401 for blacklisted token"
        )

    except Exception as e:
        log_test("Use Revoked Token", "/patients/", "GET",
                False, 0, str(e))


def print_summary():
    """Print test summary"""
    print("\n" + "="*80)
    print("🧪 AUTHENTICATION API TEST SUMMARY")
    print("="*80)

    passed = sum(1 for r in RESULTS if r["success"])
    failed = len(RESULTS) - passed

    print(f"\n✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total:  {len(RESULTS)}")
    print(f"📈 Success Rate: {passed/len(RESULTS)*100:.1f}%")

    if failed > 0:
        print("\n❌ Failed Tests:")
        for r in RESULTS:
            if not r["success"]:
                print(f"  - {r['test_name']} ({r['status_code']})")

    # Save detailed results
    with open("/tmp/auth_api_test_results.json", "w") as f:
        json.dump(RESULTS, f, indent=2)

    print(f"\n📄 Detailed results saved to: /tmp/auth_api_test_results.json")


def main():
    """Run all authentication API tests"""
    print("="*80)
    print("🚀 Starting Authentication API Tests")
    print("="*80)

    # Test 1-5: Login validations
    test_therapist_login_invalid_password()
    test_therapist_login_nonexistent_email()
    test_invalid_email_format()
    test_empty_password()

    # Test 1: Valid login (get tokens for subsequent tests)
    access_token, refresh_token = test_therapist_login_valid()

    if not access_token:
        print("\n❌ Failed to get access token, cannot continue protected endpoint tests")
        print_summary()
        return

    # Test 6-7: Protected endpoints
    test_protected_endpoint_with_token(access_token)
    test_protected_endpoint_without_token()

    # Test 8-9: Registration
    test_therapist_register()
    test_duplicate_email_registration()

    # Test 10: Refresh token
    if refresh_token:
        test_refresh_token(refresh_token)

    # Test 11-12: Logout and revoked token
    test_logout(access_token)
    test_use_revoked_token(access_token)

    # Print summary
    print_summary()


if __name__ == "__main__":
    main()
