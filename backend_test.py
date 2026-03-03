#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime

class FitnessAPITester:
    def __init__(self, base_url="https://fitpro-quiz.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
        
        result = {
            "name": name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
        if details:
            print(f"    {details}")
        print()

    def test_health_check(self):
        """Test API health endpoint"""
        try:
            response = requests.get(f"{self.api_url}/", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                self.log_test("Health Check", success, f"API Response: {data.get('message', 'No message')}")
            else:
                self.log_test("Health Check", False, f"Status: {response.status_code}, Response: {response.text[:200]}")
            
            return success
        except Exception as e:
            self.log_test("Health Check", False, f"Error: {str(e)}")
            return False

    def test_quiz_submit(self):
        """Test quiz submission endpoint"""
        # Test data matching the QuizAnswers model
        quiz_data = {
            "age": 25,
            "weight": 75.0,
            "height": 175,
            "gender": "male",
            "goal": "gain_muscle",
            "training_days": 5,
            "equipment": "full_gym",
            "dietary_preference": "non_vegetarian",
            "experience_level": "intermediate",
            "sleep_hours": "7_plus",
            "injuries": ""
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/quiz/submit", 
                json=quiz_data,
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            success = response.status_code == 200
            
            if success:
                data = response.json()
                required_fields = ['quiz_id', 'calories', 'protein', 'training_plan']
                
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    self.log_test("Quiz Submit", False, f"Missing fields: {missing_fields}")
                    return False, None
                
                details = f"Quiz ID: {data['quiz_id']}, Calories: {data['calories']}, Protein: {data['protein']}g"
                self.log_test("Quiz Submit", True, details)
                return True, data['quiz_id']
            else:
                self.log_test("Quiz Submit", False, f"Status: {response.status_code}, Response: {response.text[:300]}")
                return False, None
                
        except Exception as e:
            self.log_test("Quiz Submit", False, f"Error: {str(e)}")
            return False, None

    def test_checkout_session(self, quiz_id):
        """Test Stripe checkout session creation"""
        if not quiz_id:
            self.log_test("Checkout Session", False, "No quiz_id provided")
            return False, None
        
        checkout_data = {
            "quiz_id": quiz_id,
            "origin_url": "https://fitpro-quiz.preview.emergentagent.com"
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/checkout/session",
                json=checkout_data,
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            success = response.status_code == 200
            
            if success:
                data = response.json()
                required_fields = ['session_id', 'url']
                
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    self.log_test("Checkout Session", False, f"Missing fields: {missing_fields}")
                    return False, None
                
                details = f"Session ID: {data['session_id'][:20]}..., URL: {data['url'][:50]}..."
                self.log_test("Checkout Session", True, details)
                return True, data['session_id']
            else:
                self.log_test("Checkout Session", False, f"Status: {response.status_code}, Response: {response.text[:300]}")
                return False, None
                
        except Exception as e:
            self.log_test("Checkout Session", False, f"Error: {str(e)}")
            return False, None

    def test_checkout_status(self, session_id):
        """Test checkout status endpoint"""
        if not session_id:
            self.log_test("Checkout Status", False, "No session_id provided")
            return False
        
        try:
            response = requests.get(
                f"{self.api_url}/checkout/status/{session_id}",
                timeout=10
            )
            
            success = response.status_code == 200
            
            if success:
                data = response.json()
                details = f"Payment Status: {data.get('payment_status', 'Unknown')}"
                self.log_test("Checkout Status", True, details)
            else:
                self.log_test("Checkout Status", False, f"Status: {response.status_code}, Response: {response.text[:300]}")
            
            return success
                
        except Exception as e:
            self.log_test("Checkout Status", False, f"Error: {str(e)}")
            return False

    def test_pdf_download_protected(self, quiz_id):
        """Test PDF download endpoint (should be protected)"""
        if not quiz_id:
            self.log_test("PDF Download (Protected)", False, "No quiz_id provided")
            return False
        
        try:
            response = requests.get(f"{self.api_url}/pdf/download/{quiz_id}", timeout=10)
            
            # Should return 403 since we haven't paid
            success = response.status_code == 403
            
            if success:
                self.log_test("PDF Download (Protected)", True, "Correctly blocked access without payment")
            else:
                details = f"Expected 403, got {response.status_code}. Response: {response.text[:200]}"
                self.log_test("PDF Download (Protected)", False, details)
            
            return success
                
        except Exception as e:
            self.log_test("PDF Download (Protected)", False, f"Error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run comprehensive backend API tests"""
        print("🚀 Starting PROTOCOL Fitness API Tests")
        print(f"🔗 Backend URL: {self.api_url}")
        print("=" * 60)
        
        # Test 1: Health Check
        health_ok = self.test_health_check()
        if not health_ok:
            print("❌ Critical: API is not responding. Stopping tests.")
            return self.print_summary()
        
        # Test 2: Quiz Submit
        quiz_success, quiz_id = self.test_quiz_submit()
        
        # Test 3: Checkout Session (requires quiz_id)
        checkout_success, session_id = self.test_checkout_session(quiz_id)
        
        # Test 4: Checkout Status (requires session_id)
        self.test_checkout_status(session_id)
        
        # Test 5: PDF Download Protection
        self.test_pdf_download_protected(quiz_id)
        
        return self.print_summary()

    def print_summary(self):
        """Print test summary and return exit code"""
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print(f"✅ Passed: {self.tests_passed}/{self.tests_run}")
        print(f"❌ Failed: {self.tests_run - self.tests_passed}/{self.tests_run}")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return 0
        else:
            print("⚠️  Some tests failed. Check details above.")
            return 1

def main():
    tester = FitnessAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())