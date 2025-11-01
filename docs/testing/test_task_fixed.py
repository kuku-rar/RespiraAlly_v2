#!/usr/bin/env python3
"""Task Board API Test - Fixed"""
import json, requests, base64
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api/v1"

def get_token():
    r = requests.post(f"{BASE_URL}/auth/therapist/login",
                     json={"email": "test@therapist.com", "password": "SecurePass123!"})
    return r.json()["access_token"]

def get_id(token):
    payload = token.split('.')[1] + '=' * (4 - len(token.split('.')[1]) % 4)
    return json.loads(base64.b64decode(payload))['sub']

token = get_token()
headers = {"Authorization": f"Bearer {token}"}
therapist_id = get_id(token)

print(f"\n🎯 Task Board API Test (Sprint 5)\n")

# Create test patient
r = requests.post(f"{BASE_URL}/patients/", headers=headers, json={
    "therapist_id": therapist_id,
    "name": f"Task Patient {int(datetime.now().timestamp())}",
    "birth_date": "1965-01-01",
    "gender": "MALE"
})
patient_id = r.json()["user_id"]
print(f"✅ Created patient: {patient_id}\n")

results = []
def log(name, ok, code, notes=""):
    results.append(ok)
    print(f"{'✅' if ok else '❌'} {name} ({code}) {notes}")
    return ok

# Test 1: Create task (FIXED - correct schema)
task_data = {
    "patient_id": patient_id,
    "title": "服用呼吸道藥物",
    "description": "每天早晚各服用一次",
    "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
    "priority": "HIGH",
    "task_type": "MANUAL",
    "assigned_to": therapist_id
}
r = requests.post(f"{BASE_URL}/tasks/", headers=headers, json=task_data)
ok = r.status_code == 201
log("Create Task", ok, r.status_code, f"- {r.json().get('title', 'Error')}" if ok else f"")
task_id = r.json().get("task_id") if ok else None

# Test 2: Get task
if task_id:
    r = requests.get(f"{BASE_URL}/tasks/{task_id}", headers=headers)
    log("Get Task", r.status_code == 200, r.status_code,
        f"- Status: {r.json().get('status')}")

# Test 3: Update task
if task_id:
    r = requests.patch(f"{BASE_URL}/tasks/{task_id}", headers=headers,
                      json={"priority": "MEDIUM"})
    log("Update Task", r.status_code == 200, r.status_code)

# Test 4: Start task
if task_id:
    r = requests.post(f"{BASE_URL}/tasks/{task_id}/start", headers=headers)
    log("Start Task", r.status_code == 200, r.status_code,
        f"- New status: {r.json().get('status')}")

# Test 5: Complete task
if task_id:
    r = requests.post(f"{BASE_URL}/tasks/{task_id}/complete", headers=headers,
                     json={"completion_notes": "任務完成"})
    log("Complete Task", r.status_code == 200, r.status_code)

# Test 6: Create & Cancel task
task_data2 = {
    "patient_id": patient_id,
    "title": "回診檢查",
    "priority": "LOW",
    "task_type": "SCHEDULED",
    "due_date": (datetime.now() + timedelta(days=14)).isoformat()
}
r = requests.post(f"{BASE_URL}/tasks/", headers=headers, json=task_data2)
task_id2 = r.json().get("task_id") if r.status_code == 201 else None

if task_id2:
    r = requests.post(f"{BASE_URL}/tasks/{task_id2}/cancel", headers=headers,
                     json={"reason": "行程變更"})
    log("Cancel Task", r.status_code == 200, r.status_code)

# Test 7: List patient tasks
r = requests.get(f"{BASE_URL}/tasks/patients/{patient_id}/", headers=headers)
log("List Patient Tasks", r.status_code == 200, r.status_code,
    f"- {len(r.json().get('items', []))} tasks")

# Test 8: List therapist tasks
r = requests.get(f"{BASE_URL}/tasks/therapists/{therapist_id}/", headers=headers)
log("List Therapist Tasks", r.status_code == 200, r.status_code,
    f"- {len(r.json().get('items', []))} tasks")

# Test 9: Patient task stats
r = requests.get(f"{BASE_URL}/tasks/patients/{patient_id}/stats", headers=headers)
if r.status_code == 200:
    s = r.json()
    log("Patient Task Stats", True, 200,
        f"- Total: {s.get('total_tasks')}, Done: {s.get('done_count')}")
else:
    log("Patient Task Stats", False, r.status_code)

# Test 10: Therapist task stats
r = requests.get(f"{BASE_URL}/tasks/therapists/{therapist_id}/stats", headers=headers)
if r.status_code == 200:
    s = r.json()
    log("Therapist Task Stats", True, 200,
        f"- Total: {s.get('total_tasks')}, Todo: {s.get('todo_count')}")
else:
    log("Therapist Task Stats", False, r.status_code)

# Test 11: Overdue tasks
r = requests.get(f"{BASE_URL}/tasks/overdue/", headers=headers)
log("List Overdue Tasks", r.status_code == 200, r.status_code)

# Test 12: Delete task
if task_id2:
    r = requests.delete(f"{BASE_URL}/tasks/{task_id2}", headers=headers)
    log("Delete Task", r.status_code == 204, r.status_code)

# Test 13: Unauthorized
if task_id:
    r = requests.get(f"{BASE_URL}/tasks/{task_id}")
    log("Unauthorized Access", r.status_code == 401, r.status_code)

passed = sum(results)
total = len(results)
print(f"\n{'='*60}")
print(f"✅ Passed: {passed}/{total} ({passed/total*100:.1f}%)")
print(f"❌ Failed: {total-passed}")
