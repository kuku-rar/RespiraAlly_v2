#!/usr/bin/env python3
"""Patient API Test - Fixed"""
import json
import requests
import base64
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"
RESULTS = []

def get_token():
    response = requests.post(f"{BASE_URL}/auth/therapist/login",
                            json={"email": "test@therapist.com", "password": "SecurePass123!"})
    return response.json()["access_token"]

def log_test(name, endpoint, method, success, code, notes=""):
    RESULTS.append({"name": name, "success": success, "code": code, "notes": notes})
    print(f"{'✅' if success else '❌'} {name} ({code}) - {notes}")

token = get_token()
headers = {"Authorization": f"Bearer {token}"}

# Get therapist ID from token
payload = token.split('.')[1] + '=' * (4 - len(token.split('.')[1]) % 4)
therapist_id = json.loads(base64.b64decode(payload))['sub']

print(f"\n🔑 Therapist ID: {therapist_id}\n")

# Test 1: List patients
r = requests.get(f"{BASE_URL}/patients/", headers=headers, params={"page_size": 5})
log_test("List Patients", "/patients/", "GET", r.status_code == 200, r.status_code,
         f"Total: {r.json().get('total', 0)}")
patient_id = None

# Test 2: Create patient (FIXED - use 'name' not 'full_name')
patient_data = {
    "therapist_id": therapist_id,
    "name": f"測試病患 {int(datetime.now().timestamp())}",
    "birth_date": "1960-01-01",
    "gender": "MALE",
    "phone": "0912345678",
    "height_cm": 170,
    "weight_kg": 70.5
}
r = requests.post(f"{BASE_URL}/patients/", headers=headers, json=patient_data)
success = r.status_code == 201
if success:
    patient_id = r.json()["user_id"]
log_test("Create Patient", "/patients/", "POST", success, r.status_code,
         f"Created patient: {r.json().get('name', 'Error')}" if success else r.json().get('error', {}).get('message', 'Error'))

# Test 3: Get patient details
if patient_id:
    r = requests.get(f"{BASE_URL}/patients/{patient_id}", headers=headers)
    log_test("Get Patient Details", f"/patients/{patient_id}", "GET",
             r.status_code == 200, r.status_code,
             f"Name: {r.json().get('name', 'N/A')}")

# Test 4: Update patient
if patient_id:
    r = requests.patch(f"{BASE_URL}/patients/{patient_id}", headers=headers,
                      json={"phone": "0987654321"})
    log_test("Update Patient", f"/patients/{patient_id}", "PATCH",
             r.status_code == 200 and r.json().get("phone") == "0987654321",
             r.status_code, "Updated phone number")

# Test 5: List patients with filter
r = requests.get(f"{BASE_URL}/patients/", headers=headers,
                params={"search": "測試", "page_size": 10})
log_test("List with Search Filter", "/patients/?search=測試", "GET",
         r.status_code == 200, r.status_code,
         f"Found {len(r.json().get('items', []))} patients")

# Test 6: Pagination
r = requests.get(f"{BASE_URL}/patients/", headers=headers,
                params={"page": 0, "page_size": 2})
success = r.status_code == 200 and "items" in r.json()
log_test("Pagination", "/patients/?page=0&page_size=2", "GET", success,
         r.status_code, f"Total: {r.json().get('total', 0)}")

# Test 7: Unauthorized access
if patient_id:
    r = requests.get(f"{BASE_URL}/patients/{patient_id}")
    log_test("Unauthorized Access", f"/patients/{patient_id}", "GET",
             r.status_code == 401, r.status_code, "No token provided")

# Test 8: Non-existent patient
fake_id = "00000000-0000-0000-0000-000000000000"
r = requests.get(f"{BASE_URL}/patients/{fake_id}", headers=headers)
log_test("Non-existent Patient", f"/patients/{fake_id}", "GET",
         r.status_code == 404, r.status_code, "Should return 404")

# Summary
passed = sum(1 for r in RESULTS if r["success"])
total = len(RESULTS)
print(f"\n{'='*60}")
print(f"✅ Passed: {passed}/{total} ({passed/total*100:.1f}%)")
print(f"❌ Failed: {total-passed}")
with open("/tmp/patient_api_results_fixed.json", "w") as f:
    json.dump(RESULTS, f, indent=2)
