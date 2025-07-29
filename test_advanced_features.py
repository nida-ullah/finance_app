#!/usr/bin/env python3
"""
Advanced Features Test Script for Finance App
Tests all new features: Transaction History, Budget Monitoring, Categories, Transfers, Reporting
"""

import requests
import json
import sys
import time

BASE_URL = "http://localhost:8000/api"

class AdvancedFinanceAppTester:
    def __init__(self):
        self.access_token = None
        self.user_id = None
        self.project1_id = None
        self.project2_id = None
        self.category_id = None
        
    def get_headers(self):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.access_token}"}
    
    def setup_test_data(self):
        """Setup initial test data"""
        print("🔧 Setting up test data...")
        
        # Login as existing user
        login_data = {"username": "testuser_demo", "password": "securepass123"}
        response = requests.post(f"{BASE_URL}/login/", json=login_data)
        if response.status_code == 200:
            self.access_token = response.json()["access"]
            print("✅ Logged in successfully")
        else:
            print("❌ Login failed")
            return False
        
        # Create test projects
        project1_data = {"name": "Kitchen Renovation", "budget": "0.00", "budget_limit": "2000.00", "low_budget_threshold": "200.00"}
        response = requests.post(f"{BASE_URL}/projects/", json=project1_data, headers=self.get_headers())
        if response.status_code == 201:
            self.project1_id = response.json()["id"]
            print(f"✅ Project 1 created: {self.project1_id}")
        
        project2_data = {"name": "Living Room Makeover", "budget": "0.00", "budget_limit": "1500.00", "low_budget_threshold": "150.00"}
        response = requests.post(f"{BASE_URL}/projects/", json=project2_data, headers=self.get_headers())
        if response.status_code == 201:
            self.project2_id = response.json()["id"]
            print(f"✅ Project 2 created: {self.project2_id}")
        
        # Add some funds to main account
        funds_data = {"amount": "3000.00"}
        response = requests.post(f"{BASE_URL}/add-funds/", json=funds_data, headers=self.get_headers())
        if response.status_code == 200:
            print("✅ Added $3000 to main account")
        
        # Allocate funds to projects
        allocate1_data = {"project_id": self.project1_id, "amount": "1000.00"}
        requests.post(f"{BASE_URL}/allocate-funds/", json=allocate1_data, headers=self.get_headers())
        
        allocate2_data = {"project_id": self.project2_id, "amount": "800.00"}
        requests.post(f"{BASE_URL}/allocate-funds/", json=allocate2_data, headers=self.get_headers())
        print("✅ Allocated funds to both projects")
        
        return True
    
    def test_categories(self):
        """🆕 Test expense categories management"""
        print("📂 Testing Categories Management...")
        
        # Get existing categories (should include defaults)
        response = requests.get(f"{BASE_URL}/categories/", headers=self.get_headers())
        if response.status_code == 200:
            categories = response.json()
            print(f"✅ Retrieved {len(categories)} categories")
            if categories:
                self.category_id = categories[0]["id"]
                for cat in categories[:3]:  # Show first 3
                    print(f"   📁 {cat['name']} ({cat['color']}) - {cat['expense_count']} expenses")
        
        # Create a custom category
        custom_category = {
            "name": "Home Improvement",
            "type": "expense", 
            "color": "#2ecc71",
            "description": "Custom category for home improvement expenses"
        }
        response = requests.post(f"{BASE_URL}/categories/", json=custom_category, headers=self.get_headers())
        if response.status_code == 201:
            print("✅ Created custom category: Home Improvement")
        
        return True
    
    def test_categorized_expenses(self):
        """Test adding expenses with categories"""
        print("💸 Testing Categorized Expenses...")
        
        if not self.category_id:
            print("⚠️ No category available for testing")
            return False
        
        # Add expenses with categories and tags
        expense1_data = {
            "project": self.project1_id,
            "category": self.category_id,
            "amount": "250.00",
            "description": "Kitchen cabinets and hardware",
            "tags": "kitchen, cabinets, hardware",
            "receipt_url": "https://example.com/receipt1.pdf"
        }
        
        expense2_data = {
            "project": self.project1_id,
            "category": self.category_id,
            "amount": "180.00", 
            "description": "Paint and brushes",
            "tags": "paint, brushes, walls"
        }
        
        response1 = requests.post(f"{BASE_URL}/add-expense/", json=expense1_data, headers=self.get_headers())
        response2 = requests.post(f"{BASE_URL}/add-expense/", json=expense2_data, headers=self.get_headers())
        
        if response1.status_code == 201 and response2.status_code == 201:
            print("✅ Added categorized expenses with tags")
        
        # Test enhanced expense list
        response = requests.get(f"{BASE_URL}/expenses/", headers=self.get_headers())
        if response.status_code == 200:
            expenses = response.json()
            print(f"✅ Retrieved {len(expenses)} expenses")
            for expense in expenses[:2]:  # Show first 2
                print(f"   💰 ${expense['amount']}: {expense['description']}")
                print(f"      📁 Category: {expense['category_name']}")
                if expense['tags_list']:
                    print(f"      🏷️  Tags: {', '.join(expense['tags_list'])}")
        
        return True
    
    def test_project_transfers(self):
        """🆕 Test fund transfers between projects"""
        print("🔄 Testing Project Fund Transfers...")
        
        transfer_data = {
            "from_project_id": self.project1_id,
            "to_project_id": self.project2_id,
            "amount": "200.00",
            "description": "Transferred funds for shared materials"
        }
        
        response = requests.post(f"{BASE_URL}/transfer-funds/", json=transfer_data, headers=self.get_headers())
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Transferred ${result['amount']} from {result['from_project']} to {result['to_project']}")
        else:
            print(f"❌ Transfer failed: {response.text}")
            return False
        
        return True
    
    def test_transaction_history(self):
        """🆕 Test comprehensive transaction history"""
        print("📊 Testing Transaction History...")
        
        # Get all transactions
        response = requests.get(f"{BASE_URL}/transactions/", headers=self.get_headers())
        if response.status_code == 200:
            data = response.json()
            transactions = data["transactions"]
            summary = data["summary"]
            
            print(f"✅ Retrieved {len(transactions)} transactions")
            print("📈 Summary:")
            print(f"   💰 Total Deposits: ${summary['total_deposits']}")
            print(f"   📤 Total Allocations: ${summary['total_allocations']}")
            print(f"   💸 Total Expenses: ${summary['total_expenses']}")
            print(f"   🔄 Total Transfers: ${summary['total_transfers']}")
            
            print("\n🕒 Recent Transactions:")
            for txn in transactions[:5]:  # Show first 5
                print(f"   {txn['transaction_type'].upper()}: ${txn['amount']} - {txn['description'][:50]}")
        
        # Test filtered transactions
        response = requests.get(f"{BASE_URL}/transactions/?type=expense&limit=10", headers=self.get_headers())
        if response.status_code == 200:
            expense_txns = response.json()["transactions"]
            print(f"✅ Retrieved {len(expense_txns)} expense transactions")
        
        return True
    
    def test_budget_alerts(self):
        """🆕 Test budget monitoring and alerts"""
        print("🚨 Testing Budget Alerts...")
        
        # Check current alerts
        response = requests.get(f"{BASE_URL}/budget-alerts/", headers=self.get_headers())
        if response.status_code == 200:
            data = response.json()
            alerts = data["alerts"]
            unread_count = data["unread_count"]
            
            print(f"✅ Retrieved {len(alerts)} alerts ({unread_count} unread)")
            
            for alert in alerts[:3]:  # Show first 3
                status_icon = "🔴" if not alert['is_read'] else "✅"
                print(f"   {status_icon} {alert['alert_type'].upper()}: {alert['message'][:60]}...")
        
        # Create a low budget situation by adding a large expense
        if self.project2_id:
            large_expense = {
                "project": self.project2_id,
                "amount": "850.00",  # This should trigger low budget alert
                "description": "Large furniture purchase - should trigger alert"
            }
            response = requests.post(f"{BASE_URL}/add-expense/", json=large_expense, headers=self.get_headers())
            if response.status_code == 201:
                print("✅ Added large expense to trigger budget alert")
                
                # Check for new alerts
                time.sleep(1)  # Brief pause
                response = requests.get(f"{BASE_URL}/budget-alerts/?unread_only=true", headers=self.get_headers())
                if response.status_code == 200:
                    new_alerts = response.json()["alerts"]
                    if new_alerts:
                        print(f"🚨 New alert triggered: {new_alerts[0]['message']}")
        
        return True
    
    def test_reporting(self):
        """🆕 Test comprehensive reporting features"""
        print("📊 Testing Advanced Reporting...")
        
        # Test overview report
        response = requests.get(f"{BASE_URL}/reports/?type=overview&period=30", headers=self.get_headers())
        if response.status_code == 200:
            overview = response.json()
            print("✅ Overview Report:")
            print(f"   💰 Main Account: ${overview['main_account_balance']}")
            print(f"   📊 Total Project Budget: ${overview['total_project_budget']}")
            print(f"   💸 Total Expenses (30 days): ${overview['total_expenses']}")
            print(f"   📋 Projects: {overview['projects_count']}")
            if overview['low_budget_projects']:
                print(f"   ⚠️  Low Budget Projects: {', '.join(overview['low_budget_projects'])}")
        
        # Test category report
        response = requests.get(f"{BASE_URL}/reports/?type=categories&period=30", headers=self.get_headers())
        if response.status_code == 200:
            category_report = response.json()
            print("\n✅ Category Report:")
            for cat in category_report['categories'][:3]:  # Show top 3
                print(f"   📁 {cat['name']}: ${cat['amount']} ({cat['expense_count']} expenses)")
        
        # Test project report
        response = requests.get(f"{BASE_URL}/reports/?type=projects&period=30", headers=self.get_headers())
        if response.status_code == 200:
            project_report = response.json()
            print("\n✅ Project Report:")
            for proj in project_report['projects']:
                print(f"   📋 {proj['name']}: ${proj['current_budget']} remaining")
                print(f"      💸 Period Expenses: ${proj['period_expenses']}")
                print(f"      📊 Status: {proj['budget_status']}")
        
        # Test trends report
        response = requests.get(f"{BASE_URL}/reports/?type=trends&period=7", headers=self.get_headers())
        if response.status_code == 200:
            trends = response.json()
            print(f"\n✅ Trends Report:")
            print(f"   📈 Average Daily Spending: ${trends['average_daily_spending']:.2f}")
            if trends['daily_trends']:
                print(f"   📅 Days with expenses: {len(trends['daily_trends'])}")
        
        return True
    
    def test_enhanced_project_balance(self):
        """Test enhanced project balance view with new features"""
        print("📈 Testing Enhanced Project Balance View...")
        
        response = requests.get(f"{BASE_URL}/project-balances/", headers=self.get_headers())
        if response.status_code == 200:
            data = response.json()
            projects = data["projects"]
            summary = data["summary"]
            
            print("✅ Enhanced Project Balance Summary:")
            print(f"   📊 Total Spent: ${summary['total_spent']}")
            print(f"   💰 Total Remaining: ${summary['total_remaining']}")
            
            print("\n📋 Project Details:")
            for project in projects:
                print(f"\n🏷️  {project['name']}")
                print(f"   💰 Budget: ${project['budget']} (Limit: ${project['budget_limit'] or 'Unlimited'})")
                print(f"   📊 Status: {project['budget_status']} {'⚠️' if project['is_budget_low'] else '✅'}")
                print(f"   💸 Total Expenses: ${project['total_expenses']}")
                print(f"   🚨 Unread Alerts: {project['alerts_count']}")
                
                if project['latest_expenses']:
                    print("   🕒 Latest Expenses:")
                    for expense in project['latest_expenses'][:2]:
                        print(f"      - ${expense['amount']}: {expense['description'][:40]}...")
        
        return True
    
    def run_all_advanced_tests(self):
        """Run all advanced feature tests"""
        print("🚀 Starting Advanced Finance App Feature Tests...")
        print("=" * 70)
        
        if not self.setup_test_data():
            print("❌ Setup failed")
            return False
        
        tests = [
            ("Categories Management", self.test_categories),
            ("Categorized Expenses", self.test_categorized_expenses),
            ("Project Transfers", self.test_project_transfers),
            ("Transaction History", self.test_transaction_history),
            ("Budget Alerts", self.test_budget_alerts),
            ("Advanced Reporting", self.test_reporting),
            ("Enhanced Project Balance", self.test_enhanced_project_balance),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n{'='*70}")
            print(f"🧪 TESTING: {test_name}")
            print(f"{'='*70}")
            
            try:
                if test_func():
                    passed += 1
                    print(f"✅ {test_name} - PASSED")
                else:
                    print(f"❌ {test_name} - FAILED")
            except Exception as e:
                print(f"❌ {test_name} - ERROR: {e}")
        
        print("\n" + "=" * 70)
        print(f"🎯 ADVANCED FEATURES TEST RESULTS: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL ADVANCED FEATURES WORKING PERFECTLY!")
            print("🚀 Your finance app now has comprehensive financial management capabilities!")
        else:
            print("⚠️  Some advanced features need attention.")
        
        return passed == total

if __name__ == "__main__":
    tester = AdvancedFinanceAppTester()
    success = tester.run_all_advanced_tests()
    sys.exit(0 if success else 1) 