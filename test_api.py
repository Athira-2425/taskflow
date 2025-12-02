"""
Test script for Taskflow API
Demonstrates all functionality and role-based access control
"""
import requests
import json
from typing import Dict, Optional


class TaskflowAPITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.pm_token: Optional[str] = None
        self.dev_token: Optional[str] = None
        
    def make_request(self, method: str, endpoint: str, token: Optional[str] = None, data: Dict = None) -> Dict:
        """Make HTTP request with proper headers"""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=data)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    return e.response.json()
                except:
                    return {"error": str(e)}
            return {"error": str(e)}
    
    def login_project_manager(self) -> Dict:
        """Login as Project Manager"""
        print("🔑 Logging in as Project Manager...")
        data = {
            "username": "project_manager",
            "password": "manager123"
        }
        
        result = self.make_request("POST", "/auth/login", data=data)
        
        if "access_token" in result:
            self.pm_token = result["access_token"]
            print("✅ Project Manager login successful!")
            print(f"   Token: {self.pm_token[:50]}...")
        else:
            print(f"❌ Login failed: {result}")
        
        return result
    
    def login_backend_developer(self) -> Dict:
        """Login as Backend Developer"""
        print("🔑 Logging in as Backend Developer...")
        data = {
            "username": "backend_dev",
            "password": "developer123"
        }
        
        result = self.make_request("POST", "/auth/login", data=data)
        
        if "access_token" in result:
            self.dev_token = result["access_token"]
            print("✅ Backend Developer login successful!")
            print(f"   Token: {self.dev_token[:50]}...")
        else:
            print(f"❌ Login failed: {result}")
        
        return result
    
    def get_current_user_info(self, token: str):
        """Get current user information"""
        print("👤 Getting current user info...")
        result = self.make_request("GET", "/auth/me", token=token)
        
        if "username" in result:
            print(f"   User: {result['full_name']} (@{result['username']})")
            print(f"   Role: {result['role']}")
        else:
            print(f"❌ Failed to get user info: {result}")
        
        return result
    
    def project_manager_create_task(self) -> Dict:
        """Project Manager creates a task"""
        print("📋 Project Manager creating task...")
        data = {
            "title": "Implement User Authentication",
            "description": "Build JWT-based authentication system",
            "priority": 3,
            "assigned_to_id": 2  # Backend Developer
        }
        
        result = self.make_request("POST", "/tasks/", token=self.pm_token, data=data)
        
        if "id" in result:
            print(f"✅ Task created successfully!")
            print(f"   Task ID: {result['id']}")
            print(f"   Title: {result['title']}")
            print(f"   Assigned to: {result['assignee_name']}")
            return result
        else:
            print(f"❌ Task creation failed: {result}")
            return result
    
    def project_manager_get_all_tasks(self) -> Dict:
        """Project Manager gets all tasks"""
        print("📊 Project Manager getting all tasks...")
        result = self.make_request("GET", "/tasks/all", token=self.pm_token)
        
        if "tasks" in result:
            print(f"✅ Found {result['total']} tasks total")
            for task in result['tasks']:
                print(f"   - {task['title']} (Status: {task['status']}, Assigned to: {task['assignee_name']})")
        else:
            print(f"❌ Failed to get tasks: {result}")
        
        return result
    
    def backend_developer_get_own_tasks(self) -> Dict:
        """Backend Developer gets their own tasks"""
        print("📋 Backend Developer getting their tasks...")
        result = self.make_request("GET", "/tasks/", token=self.dev_token)
        
        if "tasks" in result:
            print(f"✅ Found {result['total']} tasks assigned to them")
            for task in result['tasks']:
                print(f"   - {task['title']} (Status: {task['status']})")
        else:
            print(f"❌ Failed to get tasks: {result}")
        
        return result
    
    def backend_developer_update_task_status(self, task_id: int) -> Dict:
        """Backend Developer updates task status"""
        print(f"🔄 Backend Developer updating task {task_id} status...")
        data = {
            "status": "in_progress"
        }
        
        result = self.make_request("PUT", f"/tasks/{task_id}/status", token=self.dev_token, data=data)
        
        if "status" in result:
            print(f"✅ Task status updated to: {result['status']}")
        else:
            print(f"❌ Failed to update task: {result}")
        
        return result
    
    def project_manager_update_task(self, task_id: int) -> Dict:
        """Project Manager updates task details"""
        print(f"📝 Project Manager updating task {task_id}...")
        data = {
            "status": "completed",
            "feedback": "Excellent work! Clean code and good documentation.",
            "score": 9
        }
        
        result = self.make_request("PUT", f"/tasks/{task_id}", token=self.pm_token, data=data)
        
        if "id" in result:
            print(f"✅ Task updated successfully!")
            print(f"   Status: {result['status']}")
            print(f"   Feedback: {result['feedback']}")
            print(f"   Score: {result['score']}/10")
        else:
            print(f"❌ Failed to update task: {result}")
        
        return result
    
    def test_access_denied(self) -> Dict:
        """Test that Backend Developer cannot create tasks"""
        print("🚫 Testing access control - Backend Developer trying to create task...")
        data = {
            "title": "Unauthorized Task",
            "description": "This should fail",
            "priority": 1,
            "assigned_to_id": 2
        }
        
        result = self.make_request("POST", "/tasks/", token=self.dev_token, data=data)
        
        if "detail" in result and "Project Manager role required" in result["detail"]:
            print("✅ Access control working correctly - Backend Developer cannot create tasks")
        else:
            print(f"❌ Access control failed - Backend Developer was able to create task: {result}")
        
        return result
    
    def run_all_tests(self):
        """Run all test scenarios"""
        print("🚀 Starting Taskflow API Tests")
        print("=" * 50)
        
        # Test authentication
        self.login_project_manager()
        print()
        
        self.login_backend_developer()
        print()
        
        # Test getting user info
        print("=== USER INFO ===")
        self.get_current_user_info(self.pm_token)
        self.get_current_user_info(self.dev_token)
        print()
        
        # Test task management
        print("=== TASK MANAGEMENT ===")
        created_task = self.project_manager_create_task()
        if created_task.get("id"):
            task_id = created_task["id"]
            
            print()
            print("=== DATA ISOLATION TEST ===")
            self.project_manager_get_all_tasks()
            print()
            self.backend_developer_get_own_tasks()
            print()
            
            print("=== ROLE-BASED UPDATES ===")
            self.backend_developer_update_task_status(task_id)
            print()
            self.project_manager_update_task(task_id)
            print()
            
            print("=== ACCESS CONTROL TEST ===")
            self.test_access_denied()
            print()
        
        print("✅ All tests completed!")
        print("=" * 50)


def main():
    """Main test function"""
    print("Taskflow API Test Suite")
    print("Make sure the API is running on http://localhost:8000")
    print("Press Enter to continue or Ctrl+C to cancel...")
    
    try:
        input()  # Wait for user input
    except KeyboardInterrupt:
        print("\nTest cancelled.")
        return
    
    tester = TaskflowAPITester()
    
    # Check if API is running
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code != 200:
            print("❌ API is not responding correctly")
            return
        print("✅ API is running")
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to API. Make sure it's running on http://localhost:8000")
        print("   Run: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
        return
    
    tester.run_all_tests()


if __name__ == "__main__":
    main()