#!/usr/bin/env python3
"""
Test script for Finance App API endpoints
Tests all functionality including the new Project Balance View
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000/api"

class FinanceAppTester:
    def __init__(self):
        self.access_token = None
        self.user_id = None
        self.project_id = None
        
    def test_user_signup(self):
        """Test user registration"""
        print("🔐 Testing user signup...")
        data = {
            "username": "testuser_demo",
            "email": "demo@example.com", 
            "password": "securepass123"
        }
        
        response = requests.post(f"{BASE_URL}/signup/", json=data)
        if response.status_code == 201:
            self.user_id = response.json()["id"]
            print(f"✅ User created successfully! ID: {self.user_id}")
            return True
        elif response.status_code == 400 and "already" in response.text:
            print("ℹ️  User already exists, continuing with login...")
            return True
        else:
            print(f"❌ Signup failed: {response.status_code} - {response.text}")
            return False
    
    def test_user_login(self):
        """Test user login and get JWT token"""
        print("🔑 Testing user login...")
        data = {
            "username": "testuser_demo",
            "password": "securepass123"
        }
        
        response = requests.post(f"{BASE_URL}/login/", json=data)
        if response.status_code == 200:
            tokens = response.json()
            self.access_token = tokens["access"]
            print("✅ Login successful! Token obtained.")
            return True
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return False
    
    def get_headers(self):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.access_token}"}
    
    def test_add_funds(self):
        """Test adding funds to main account"""
        print("💰 Testing add funds to main account...")
        data = {"amount": "1000.00"}
        
        response = requests.post(f"{BASE_URL}/add-funds/", 
                               json=data, headers=self.get_headers())
        if response.status_code == 200:
            balance = response.json()["balance"]
            print(f"✅ Funds added successfully! New balance: ${balance}")
            return True
        else:
            print(f"❌ Add funds failed: {response.status_code} - {response.text}")
            return False
    
    def test_check_main_account(self):
        """Test checking main account balance"""
        print("🏦 Testing main account balance check...")
        
        response = requests.get(f"{BASE_URL}/my-main-account/", 
                              headers=self.get_headers())
        if response.status_code == 200:
            account = response.json()
            print(f"✅ Main account balance: ${account['balance']}")
            return True
        else:
            print(f"❌ Main account check failed: {response.status_code} - {response.text}")
            return False
    
    def test_create_project(self):
        """Test creating a project"""
        print("📋 Testing project creation...")
        data = {
            "name": "Home Renovation",
            "budget": "0.00",
            "user": self.user_id
        }
        
        response = requests.post(f"{BASE_URL}/projects/", 
                               json=data, headers=self.get_headers())
        if response.status_code == 201:
            self.project_id = response.json()["id"]
            print(f"✅ Project created successfully! ID: {self.project_id}")
            return True
        else:
            print(f"❌ Project creation failed: {response.status_code} - {response.text}")
            return False
    
    def test_allocate_funds(self):
        """Test allocating funds from main account to project"""
        print("🔄 Testing fund allocation...")
        data = {
            "project_id": self.project_id,
            "amount": "500.00"
        }
        
        response = requests.post(f"{BASE_URL}/allocate-funds/", 
                               json=data, headers=self.get_headers())
        if response.status_code == 200:
            print("✅ Funds allocated successfully!")
            return True
        else:
            print(f"❌ Fund allocation failed: {response.status_code} - {response.text}")
            return False
    
    def test_add_expense(self):
        """Test adding expense to project"""
        print("💸 Testing expense addition...")
        data = {
            "project": self.project_id,
            "amount": "150.00", 
            "description": "Paint and brushes"
        }
        
        response = requests.post(f"{BASE_URL}/add-expense/", 
                               json=data, headers=self.get_headers())
        if response.status_code == 201:
            print("✅ Expense added successfully!")
            return True
        else:
            print(f"❌ Expense addition failed: {response.status_code} - {response.text}")
            return False
    
    def test_project_balances(self):
        """🆕 Test the new Project Balance View feature"""
        print("📊 Testing NEW Project Balance View...")
        
        response = requests.get(f"{BASE_URL}/project-balances/", 
                              headers=self.get_headers())
        if response.status_code == 200:
            data = response.json()
            print("✅ Project balances retrieved successfully!")
            print("\n📈 PROJECT BALANCE SUMMARY:")
            print("=" * 50)
            
            # Print summary
            summary = data.get("summary", {})
            print(f"Total Projects: {summary.get('total_projects', 0)}")
            print(f"Total Original Budget: ${summary.get('total_original_budget', 0)}")
            print(f"Total Spent: ${summary.get('total_spent', 0)}")
            print(f"Total Remaining: ${summary.get('total_remaining', 0)}")
            
            # Print individual projects
            print("\n📋 INDIVIDUAL PROJECTS:")
            for project in data.get("projects", []):
                print(f"\n🏷️  {project['name']}")
                print(f"   💰 Current Budget: ${project['budget']}")
                print(f"   💸 Total Expenses: ${project['total_expenses']}")
                print(f"   📊 Expense Count: {project['expense_count']}")
                
                if project['latest_expenses']:
                    print("   🕒 Latest Expenses:")
                    for expense in project['latest_expenses']:
                        print(f"      - ${expense['amount']}: {expense['description']}")
            
            return True
        else:
            print(f"❌ Project balances failed: {response.status_code} - {response.text}")
            return False
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting Finance App API Tests...")
        print("=" * 60)
        
        tests = [
            self.test_user_signup,
            self.test_user_login,
            self.test_add_funds,
            self.test_check_main_account,
            self.test_create_project,
            self.test_allocate_funds,
            self.test_add_expense,
            self.test_project_balances  # 🆕 NEW FEATURE TEST
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
                print()  # Add spacing between tests
            except Exception as e:
                print(f"❌ Test failed with exception: {e}")
                print()
        
        print("=" * 60)
        print(f"🎯 RESULTS: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! Your Finance App is working perfectly!")
            print("🆕 The new Project Balance View feature is working great!")
        else:
            print("⚠️  Some tests failed. Check the output above.")
        
        return passed == total

if __name__ == "__main__":
    tester = FinanceAppTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1) 